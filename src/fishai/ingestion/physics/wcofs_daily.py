"""Daily operational WCOFS pull for the FishAI pilot (batch-only, idempotent)."""

from __future__ import annotations

import datetime as dt
import json
import math
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np
import xarray as xr

from fishai.ingestion.physics.http_util import get_bytes, head_metadata
from fishai.ingestion.physics.sources import wcofs as wcofs_src
from fishai.ingestion.physics.wcofs_pull_log import (
    append_pull_log,
    build_day_success_record,
    build_day_tombstone_record,
    build_pull_record,
    load_day_outcome,
    load_pull_index,
    pull_log_path,
    resolve_pull_log_dir,
    sha256_bytes,
)
from fishai.ingestion.physics.wcofs_store import cycle_zarr_path, write_wcofs_cycle
from fishai.ingestion.sources import attribution_for, load_sources_manifest, require_approved

DEFAULT_WAIT_CUTOFF_UTC = dt.time(5, 45)
DEFAULT_MAX_MISSED_CYCLES = 2
NOWCAST_VALID_OFFSET_H = 0
FORECAST_HORIZON_H = 72
TEMP_MIN_C = -2.0
TEMP_MAX_C = 35.0
SALT_MIN_PSU = 0.0
SALT_MAX_PSU = 42.0


@dataclass(frozen=True)
class LeadPlan:
    valid_offset_h: int
    cycle_date: dt.date
    lead_tag: str
    fallback: str | None = None


@dataclass
class DailyPlan:
    target_date: dt.date
    bbox: tuple[float, float, float, float]
    primary_available: bool
    leads: list[LeadPlan] = field(default_factory=list)
    unknown_slots: list[dict[str, Any]] = field(default_factory=list)
    s3_keys: list[str] = field(default_factory=list)
    request_count: int = 0
    zarr_path: Path | None = None
    pull_log: Path | None = None
    qc_report_path: Path | None = None


def _pilot_bbox(manifest: dict | None = None) -> tuple[float, float, float, float]:
    manifest = manifest or load_sources_manifest()
    pilot = manifest.get("pilot") or {}
    bbox = pilot.get("bbox") or {}
    return (
        float(bbox["lat_min"]),
        float(bbox["lat_max"]),
        float(bbox["lon_min"]),
        float(bbox["lon_max"]),
    )


def cycle_id(date: dt.date) -> str:
    return f"{date.strftime('%Y%m%d')}T03Z"


def _cycle_init_utc(day: dt.date) -> dt.datetime:
    return dt.datetime.combine(day, dt.time(3, 0), tzinfo=dt.timezone.utc)


def requested_cycle_time(target: dt.date) -> dt.datetime:
    """Operational 03Z run time R for the target calendar day."""
    return wcofs_src.cycle_run_time(target)


def expected_valid_time(target: dt.date, valid_offset_h: int) -> dt.datetime:
    return requested_cycle_time(target) + dt.timedelta(hours=valid_offset_h)


def source_run_time_for_cycle(cycle_date: dt.date) -> dt.datetime:
    return wcofs_src.cycle_run_time(cycle_date)


def read_ocean_time_utc(ds: xr.Dataset) -> dt.datetime:
    import pandas as pd

    da = ds["ocean_time"]
    scalar = float(da.values.flat[0]) if da.size else float(da.values)
    units = str(da.attrs.get("units", ""))
    if units.startswith("seconds since"):
        ref = units[len("seconds since") :].strip()
        base = pd.Timestamp(ref)
        if base.tzinfo is None:
            base = base.tz_localize("UTC")
        ts = base + pd.Timedelta(seconds=scalar)
        return ts.to_pydatetime().astimezone(dt.timezone.utc)
    ts = pd.Timestamp(scalar)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.to_pydatetime().astimezone(dt.timezone.utc)


def forecast_age_hours(valid: dt.datetime, source_cycle: dt.date) -> float:
    r_src = wcofs_src.cycle_run_time(source_cycle)
    return (valid.astimezone(dt.timezone.utc) - r_src).total_seconds() / 3600.0


def evidence_from_forecast_age(age: float, *, fallback_used: bool) -> tuple[str, int | None]:
    if fallback_used:
        lead_days = max(1, int(math.ceil(age / 24.0)))
        return "forecast", lead_days
    if age <= 0.0:
        return "nowcast", None
    return "forecast", int(math.ceil(age / 24.0))


def step_provenance_record(
    lp: LeadPlan,
    ds: xr.Dataset,
    target: dt.date,
    *,
    primary_available: bool,
) -> dict[str, Any]:
    valid = read_ocean_time_utc(ds)
    source = source_run_time_for_cycle(lp.cycle_date)
    requested = requested_cycle_time(target)
    age = forecast_age_hours(valid, lp.cycle_date)
    fallback_used = lp.cycle_date != target or lp.fallback is not None
    hint, lead_days = evidence_from_forecast_age(age, fallback_used=fallback_used)
    rec: dict[str, Any] = {
        "valid_offset_h": lp.valid_offset_h,
        "requested_cycle_time": requested.isoformat(),
        "source_cycle_time": source.isoformat(),
        "source_run_time": source.isoformat(),
        "valid_time": valid.isoformat(),
        "forecast_age_hours": age,
        "fallback_used": fallback_used,
        "evidence_state_hint": hint,
        "primary_cycle_available": primary_available,
        "lead_tag": lp.lead_tag,
    }
    if lead_days is not None:
        rec["lead_days"] = lead_days
    if lp.fallback:
        rec["fallback"] = lp.fallback
    return rec


def unknown_slot_record(
    target: dt.date,
    valid_offset_h: int,
    *,
    reason: str,
) -> dict[str, Any]:
    valid = requested_cycle_time(target) + dt.timedelta(hours=valid_offset_h)
    return {
        "valid_offset_h": valid_offset_h,
        "requested_cycle_time": requested_cycle_time(target).isoformat(),
        "valid_time": valid.isoformat(),
        "state": "UNKNOWN",
        "reason": reason,
        "evidence_state_hint": "UNKNOWN",
    }


def build_step_provenance_table(
    plan: DailyPlan,
    lead_slices: Sequence[tuple[LeadPlan, xr.Dataset]] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if lead_slices:
        for lp, ds in lead_slices:
            rows.append(
                step_provenance_record(
                    lp, ds, plan.target_date, primary_available=plan.primary_available
                )
            )
    else:
        for lp in plan.leads:
            rows.append(
                {
                    "valid_offset_h": lp.valid_offset_h,
                    "lead_tag": lp.lead_tag,
                    "source_cycle_time": wcofs_src.cycle_run_time(lp.cycle_date).isoformat(),
                    "source_run_time": wcofs_src.cycle_run_time(lp.cycle_date).isoformat(),
                    "requested_cycle_time": requested_cycle_time(plan.target_date).isoformat(),
                    "valid_time": (
                        requested_cycle_time(plan.target_date)
                        + dt.timedelta(hours=lp.valid_offset_h)
                    ).isoformat(),
                    "fallback_used": lp.cycle_date != plan.target_date or lp.fallback is not None,
                }
            )
    for unk in plan.unknown_slots:
        rows.append(unk)
    return rows


def resolve_lead_for_offset(
    target: dt.date,
    valid_offset_h: int,
    *,
    primary_available: bool,
    cycle_exists_fn: Callable[[dt.date], bool],
    max_missed_cycles: int,
) -> LeadPlan | None:
    if primary_available and cycle_exists_fn(target):
        tag = wcofs_src.lead_tag_for_valid_offset(valid_offset_h)
        return LeadPlan(valid_offset_h, target, tag)
    for days_back in range(1, max_missed_cycles + 1):
        prev = target - dt.timedelta(days=days_back)
        if not cycle_exists_fn(prev):
            continue
        age_h = valid_offset_h + 24 * days_back
        if age_h < -21 or age_h > 72:
            continue
        try:
            tag = wcofs_src.lead_tag_for_age_from_source(age_h)
        except ValueError:
            continue
        expected = wcofs_src.valid_time_for_lead_tag(prev, tag)
        wanted = requested_cycle_time(target) + dt.timedelta(hours=valid_offset_h)
        if expected != wanted:
            continue
        return LeadPlan(valid_offset_h, prev, tag, fallback="previous_cycle")
    return None


def build_lead_plan(
    target: dt.date,
    *,
    primary_available: bool,
    max_missed_cycles: int = DEFAULT_MAX_MISSED_CYCLES,
    cycle_exists_fn: Callable[[dt.date], bool] | None = None,
) -> DailyPlan:
    exists = cycle_exists_fn if cycle_exists_fn is not None else (lambda _d: True)
    bbox = _pilot_bbox()
    plan = DailyPlan(target_date=target, bbox=bbox, primary_available=primary_available)
    for offset_h in wcofs_src.TARGET_VALID_OFFSETS_H:
        if primary_available:
            if not exists(target):
                plan.unknown_slots.append(
                    unknown_slot_record(target, offset_h, reason="missing_operational_cycle")
                )
                continue
            tag = wcofs_src.lead_tag_for_valid_offset(offset_h)
            lp = LeadPlan(offset_h, target, tag)
        else:
            lp = resolve_lead_for_offset(
                target,
                offset_h,
                primary_available=False,
                cycle_exists_fn=exists,
                max_missed_cycles=max_missed_cycles,
            )
            if lp is None:
                plan.unknown_slots.append(
                    unknown_slot_record(target, offset_h, reason="missing_operational_cycle")
                )
                continue
        plan.leads.append(lp)
        plan.s3_keys.append(wcofs_src.fields_s3_key(lp.cycle_date, lp.lead_tag))
    plan.request_count = len(plan.s3_keys)
    return plan


def wait_for_primary_cycle(
    target: dt.date,
    *,
    head_fn: Callable[[str], bool] | None = None,
    cutoff_utc: dt.time = DEFAULT_WAIT_CUTOFF_UTC,
    t0: float = 30.0,
    t_max: float = 600.0,
    now_fn: Callable[[], dt.datetime] | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> bool:
    """Retry until the t03z cycle probe succeeds or ``cutoff_utc`` on the target UTC day."""
    check = head_fn or (lambda url: head_metadata(url).get("status") == 200)
    probe_url = wcofs_src._fields_url_s3(target, wcofs_src.CYCLE_PROBE_LEAD)
    now_fn = now_fn or (lambda: dt.datetime.now(dt.timezone.utc))
    attempt = 0
    while True:
        if check(probe_url):
            return True
        now = now_fn()
        if now.date() < target:
            return False
        if now.date() > target or (now.date() == target and now.time() >= cutoff_utc):
            return False
        wait = min(t_max, t0 * (2 ** attempt))
        wait *= 0.5 + random.random()
        sleep_fn(wait)
        attempt += 1


def plan_daily(
    target: dt.date,
    *,
    out_root: Path,
    primary_available: bool | None = None,
    head_fn: Callable[[str], bool] | None = None,
    max_missed_cycles: int = DEFAULT_MAX_MISSED_CYCLES,
    provenance_dir: Path | None = None,
    cycle_exists_fn: Callable[[dt.date], bool] | None = None,
) -> DailyPlan:
    if primary_available is None:
        primary_available = wcofs_src.cycle_available(target, head_fn=head_fn)
    if cycle_exists_fn is None:
        cycle_exists_fn = lambda d: wcofs_src.cycle_available(d, head_fn=head_fn)
    plan = build_lead_plan(
        target,
        primary_available=primary_available,
        max_missed_cycles=max_missed_cycles,
        cycle_exists_fn=cycle_exists_fn,
    )
    plan.zarr_path = cycle_zarr_path(target, out_root)
    log_dir = resolve_pull_log_dir(out_root, provenance_dir)
    plan.pull_log = pull_log_path(target.strftime("%Y%m%d"), log_dir=log_dir)
    plan.qc_report_path = out_root / f"wcofs_{target:%Y%m%d}_qc.json"
    return plan


def _fetch_lead_bytes(
    cycle_date: dt.date,
    lead_tag: str,
    *,
    get_fn: Callable[..., bytes] | None = None,
    head_meta_fn: Callable[[str], dict[str, Any]] | None = None,
) -> tuple[bytes, dict[str, Any]]:
    get_fn = get_fn or get_bytes
    head_meta_fn = head_meta_fn or head_metadata
    url = wcofs_src._fields_url_s3(cycle_date, lead_tag)
    meta = head_meta_fn(url)
    data = get_fn(url, extra_cache_key=f"{cycle_date.isoformat()}_{lead_tag}")
    meta = {**meta, "sha256": sha256_bytes(data), "url": url}
    return data, meta


def fetch_and_log_leads(
    plan: DailyPlan,
    *,
    get_fn: Callable[..., bytes] | None = None,
    head_meta_fn: Callable[[str], dict[str, Any]] | None = None,
    log_path: Path | None = None,
    skip_if_etag_matches: bool = True,
) -> tuple[list[tuple[LeadPlan, xr.Dataset]], list[dict[str, Any]]]:
    """Fetch each planned lead, append pull log lines, return datasets and failed slots."""
    log_path = log_path or plan.pull_log
    assert log_path is not None
    index = load_pull_index(log_path) if skip_if_etag_matches else {}
    merged: list[tuple[LeadPlan, xr.Dataset]] = []
    failed: list[dict[str, Any]] = []
    bbox = plan.bbox
    for lp in list(plan.leads):
        s3_key = wcofs_src.fields_s3_key(lp.cycle_date, lp.lead_tag)
        url = wcofs_src._fields_url_s3(lp.cycle_date, lp.lead_tag)
        try:
            data, meta = _fetch_lead_bytes(
                lp.cycle_date, lp.lead_tag, get_fn=get_fn, head_meta_fn=head_meta_fn
            )
            ds = wcofs_src.open_dataset_from_bytes(data)
            sub = wcofs_src.subset_bbox(ds, bbox)
            expected = expected_valid_time(plan.target_date, lp.valid_offset_h)
            actual = read_ocean_time_utc(sub)
            if actual != expected:
                mismatch = unknown_slot_record(
                    plan.target_date, lp.valid_offset_h, reason="valid_time_mismatch"
                )
                mismatch["expected_valid_time"] = expected.isoformat()
                mismatch["actual_valid_time"] = actual.isoformat()
                failed.append(mismatch)
                prior = index.get(s3_key)
                if skip_if_etag_matches and prior and prior.get("etag") == meta.get("etag"):
                    continue
                rec = build_pull_record(
                    s3_key=s3_key,
                    url=url,
                    cycle=cycle_id(lp.cycle_date),
                    lead=lp.lead_tag,
                    lead_hour=lp.valid_offset_h,
                    status="error",
                    etag=meta.get("etag"),
                    size_bytes=meta.get("size_bytes"),
                    sha256=meta.get("sha256"),
                    extra={
                        "target_cycle": cycle_id(plan.target_date),
                        "reason": "valid_time_mismatch",
                        "expected_valid_time": expected.isoformat(),
                        "actual_valid_time": actual.isoformat(),
                        "evidence_state_hint": "UNKNOWN",
                    },
                )
                append_pull_log(rec, log_path=log_path)
                continue
            prov = step_provenance_record(
                lp, sub, plan.target_date, primary_available=plan.primary_available
            )
            merged.append((lp, sub))
            prior = index.get(s3_key)
            if skip_if_etag_matches and prior and prior.get("etag") == meta.get("etag"):
                continue
            rec = build_pull_record(
                s3_key=s3_key,
                url=url,
                cycle=cycle_id(lp.cycle_date),
                lead=lp.lead_tag,
                lead_hour=lp.valid_offset_h,
                status="ok",
                etag=meta.get("etag"),
                size_bytes=meta.get("size_bytes"),
                sha256=meta.get("sha256"),
                extra={"target_cycle": cycle_id(plan.target_date), "fallback": lp.fallback},
            )
            rec.update(
                {
                    k: prov[k]
                    for k in (
                        "requested_cycle_time",
                        "source_cycle_time",
                        "source_run_time",
                        "valid_time",
                        "forecast_age_hours",
                        "fallback_used",
                        "evidence_state_hint",
                        "lead_days",
                    )
                    if k in prov
                }
            )
            append_pull_log(rec, log_path=log_path)
        except Exception as exc:  # noqa: BLE001
            failed.append(
                unknown_slot_record(plan.target_date, lp.valid_offset_h, reason="download_failed")
            )
            rec = build_pull_record(
                s3_key=s3_key,
                url=url,
                cycle=cycle_id(lp.cycle_date),
                lead=lp.lead_tag,
                lead_hour=lp.valid_offset_h,
                status="error",
                extra={
                    "error": str(exc),
                    "target_cycle": cycle_id(plan.target_date),
                    "reason": "download_failed",
                    "evidence_state_hint": "UNKNOWN",
                },
            )
            append_pull_log(rec, log_path=log_path)
    return merged, failed


def assemble_merged_dataset(
    plan: DailyPlan,
    lead_slices: Sequence[tuple[LeadPlan, xr.Dataset]],
) -> xr.Dataset:
    datasets: list[xr.Dataset] = []
    ref_raw: xr.Dataset | None = None
    for lp, sub in sorted(lead_slices, key=lambda x: x[0].valid_offset_h):
        if ref_raw is None:
            ref_raw = sub
        sub = sub.expand_dims(valid_offset_h=[lp.valid_offset_h])
        if lp.fallback:
            sub = sub.assign_attrs(
                fallback=lp.fallback,
                source_cycle=cycle_id(lp.cycle_date),
            )
        datasets.append(sub)

    merged = xr.concat(datasets, dim="valid_offset_h")
    merged.attrs["attribution"] = attribution_for("wcofs")
    merged.attrs["source"] = "wcofs"
    merged.attrs["cycle"] = cycle_id(plan.target_date)
    table = build_step_provenance_table(plan, lead_slices)
    merged.attrs["step_provenance"] = json.dumps(table)
    merged.attrs["requested_cycle_time"] = requested_cycle_time(plan.target_date).isoformat()
    merged.attrs["fallback_used"] = str(
        any(lp.cycle_date != plan.target_date or lp.fallback for lp, _ in lead_slices)
        or not plan.primary_available
    ).lower()
    source_times = {
        step_provenance_record(lp, sub, plan.target_date, primary_available=plan.primary_available)[
            "source_cycle_time"
        ]
        for lp, sub in lead_slices
    }
    if len(source_times) == 1:
        merged.attrs["source_cycle_time"] = next(iter(source_times))
    else:
        merged.attrs["source_cycle_time"] = json.dumps(sorted(source_times))
    if plan.unknown_slots:
        merged.attrs["unknown_valid_times"] = json.dumps(plan.unknown_slots)

    ref = ref_raw
    assert ref is not None

    def _surface(da: xr.DataArray) -> xr.DataArray:
        return da.isel(ocean_time=0) if "ocean_time" in da.dims else da

    h = ref.h.values
    zeta = _surface(ref.zeta).values
    temp = _surface(ref.temp).values
    salt = _surface(ref.salt).values
    s_rho = ref.s_rho.values
    hc = float(ref.hc.values)
    cs_r = ref.Cs_r.values if "Cs_r" in ref else None
    from fishai.ingestion.physics.vertical import bottom_layer, mld, s_to_z, thermocline_depth

    z = s_to_z(h, zeta, s_rho, hc, cs_r=cs_r)
    wet = ref.mask_rho.values == 1
    feats: dict[str, Any] = bottom_layer(temp, salt)
    feats["mld_m"] = np.where(wet, mld(z, temp), np.nan)
    feats["thermocline_depth_m"] = np.where(wet, thermocline_depth(z, temp), np.nan)
    for name, arr in feats.items():
        merged[name] = (("eta_rho", "xi_rho"), arr)
    return merged


def run_cycle_qc(
    packaged: xr.Dataset,
    *,
    previous: xr.Dataset | None = None,
) -> dict[str, Any]:
    ref = (
        packaged.isel(valid_offset_h=0)
        if "valid_offset_h" in packaged.dims
        else packaged.isel(lead_hours=0)
    )
    wet = ref["MLD_m"].notnull() if "MLD_m" in packaged else ref["temp"].isel(s_rho=0).notnull()
    wet_count = int(wet.sum())
    total = int(wet.size) or 1

    def _nan_frac(da: xr.DataArray) -> float:
        arr = da.values
        mask = (
            wet.values
            if wet.ndim == len(arr.shape[-2:])
            else np.ones(arr.shape[-2:], dtype=bool)
        )
        if arr.ndim == 4:
            flat = arr[:, :, mask]
        elif arr.ndim == 3:
            flat = arr[:, mask]
        else:
            flat = arr
        return float(np.isnan(flat).sum() / max(flat.size, 1))

    report: dict[str, Any] = {
        "cycle_id": packaged.attrs.get("cycle_id"),
        "wet_cells": wet_count,
        "nan_fraction": {
            "temp": _nan_frac(packaged["temp"]),
            "salt": _nan_frac(packaged["salt"]),
        },
        "range_flags": [],
    }
    tmin = float(packaged["temp"].min())
    tmax = float(packaged["temp"].max())
    smin = float(packaged["salt"].min())
    smax = float(packaged["salt"].max())
    if tmin < TEMP_MIN_C or tmax > TEMP_MAX_C:
        report["range_flags"].append(
            {"variable": "temp", "min": tmin, "max": tmax, "expected": [TEMP_MIN_C, TEMP_MAX_C]}
        )
    if smin < SALT_MIN_PSU or smax > SALT_MAX_PSU:
        report["range_flags"].append(
            {"variable": "salt", "min": smin, "max": smax, "expected": [SALT_MIN_PSU, SALT_MAX_PSU]}
        )

    if previous is not None and "lead_hours" in packaged.dims:
        shared = sorted(set(map(int, packaged.lead_hours.values)) & set(map(int, previous.lead_hours.values)))
        diffs: list[float] = []
        for lh in shared[:3]:
            a = packaged["T3m"].sel(lead_hours=lh)
            b = previous["T3m"].sel(lead_hours=lh)
            d = (a - b).values
            diffs.append(float(np.nanmean(np.abs(d))))
        if diffs:
            report["nowcast_vs_previous_cycle"] = {
                "lead_hours_compared": shared[:3],
                "mean_abs_T3m_diff": diffs,
            }
    return report


def write_qc_report(report: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _pull_complete(log_path: Path | None, s3_keys: Sequence[str]) -> bool:
    if log_path is None or not log_path.is_file():
        return False
    index = load_pull_index(log_path)
    return all(key in index for key in s3_keys)


def _successful_valid_offsets(
    lead_slices: Sequence[tuple[LeadPlan, xr.Dataset]],
) -> set[int]:
    return {lp.valid_offset_h for lp, _ in lead_slices}


def _nowcast_slot_satisfied(
    lead_slices: Sequence[tuple[LeadPlan, xr.Dataset]],
) -> bool:
    return NOWCAST_VALID_OFFSET_H in _successful_valid_offsets(lead_slices)


def _tombstone_reason_code(
    plan: DailyPlan,
    lead_slices: Sequence[tuple[LeadPlan, xr.Dataset]],
    failed: Sequence[dict[str, Any]],
    *,
    wait_timed_out: bool,
) -> str | None:
    if not _nowcast_slot_satisfied(lead_slices):
        if not lead_slices:
            if wait_timed_out:
                return "timeout"
            if plan.leads and failed and all(
                slot.get("reason") == "download_failed" for slot in failed
            ):
                return "download_failed"
            if not plan.leads:
                return "wcofs_nowcast_missing"
            return "download_failed"
        return "wcofs_nowcast_missing"
    return None


def _write_failed_day(
    plan: DailyPlan,
    target: dt.date,
    *,
    reason: str,
    out_root: Path,
) -> None:
    assert plan.pull_log is not None
    attempted_cycles = sorted({cycle_id(lp.cycle_date) for lp in plan.leads})
    tombstone = build_day_tombstone_record(
        target,
        reason=reason,
        attempted_s3_keys=plan.s3_keys,
        attempted_cycles=attempted_cycles,
        unknown_slots=plan.unknown_slots,
    )
    append_pull_log(tombstone, log_path=plan.pull_log)
    qc_path = plan.qc_report_path or out_root / f"wcofs_{target:%Y%m%d}_qc.json"
    write_qc_report(
        {
            "cycle_id": cycle_id(target),
            "status": "failed",
            "reason": reason,
            "attempted_s3_keys": list(plan.s3_keys),
            "attempted_cycles": attempted_cycles,
            "unknown_slots": list(plan.unknown_slots),
        },
        qc_path,
    )


def run_wcofs_daily(
    target: dt.date,
    *,
    out_root: Path,
    dry_run: bool = False,
    wait_for_cycle: bool = True,
    cutoff_utc: dt.time = DEFAULT_WAIT_CUTOFF_UTC,
    max_missed_cycles: int = DEFAULT_MAX_MISSED_CYCLES,
    head_fn: Callable[[str], bool] | None = None,
    get_fn: Callable[..., bytes] | None = None,
    head_meta_fn: Callable[[str], dict[str, Any]] | None = None,
    now_fn: Callable[[], dt.datetime] | None = None,
    provenance_dir: Path | None = None,
) -> DailyPlan:
    require_approved("wcofs")
    if dry_run:
        return plan_daily(
            target,
            out_root=out_root,
            primary_available=True,
            max_missed_cycles=max_missed_cycles,
            provenance_dir=provenance_dir,
            cycle_exists_fn=lambda _d: True,
        )
    primary_available = wcofs_src.cycle_available(target, head_fn=head_fn)
    wait_timed_out = False
    if wait_for_cycle and not primary_available and not dry_run:
        wait_timed_out = True
        primary_available = wait_for_primary_cycle(
            target,
            head_fn=head_fn,
            cutoff_utc=cutoff_utc,
            now_fn=now_fn,
        )
    plan = plan_daily(
        target,
        out_root=out_root,
        primary_available=primary_available,
        head_fn=head_fn,
        max_missed_cycles=max_missed_cycles,
        provenance_dir=provenance_dir,
    )

    zpath = plan.zarr_path
    assert zpath is not None
    day_outcome, _ = load_day_outcome(plan.pull_log) if plan.pull_log else (None, None)
    if (
        zpath.is_dir()
        and _pull_complete(plan.pull_log, plan.s3_keys)
        and day_outcome in (None, "success")
        and plan.primary_available
    ):
        return plan

    lead_slices, failed = fetch_and_log_leads(
        plan,
        get_fn=get_fn,
        head_meta_fn=head_meta_fn,
        log_path=plan.pull_log,
    )
    if failed:
        plan.unknown_slots.extend(failed)
    tombstone_reason = _tombstone_reason_code(
        plan, lead_slices, failed, wait_timed_out=wait_timed_out
    )
    if tombstone_reason:
        _write_failed_day(
            plan,
            target,
            reason=tombstone_reason,
            out_root=out_root,
        )
        return plan
    partial = bool(failed)
    merged = assemble_merged_dataset(plan, lead_slices)
    extra_attrs = {
        "partial_cycle": partial,
        "missing_leads": json.dumps([f["valid_offset_h"] for f in failed]),
        "operational_target_cycle": cycle_id(target),
        "primary_cycle_available": plan.primary_available,
    }
    prev_date = target - dt.timedelta(days=1)
    prev_path = cycle_zarr_path(prev_date, out_root)
    previous = None
    if prev_path.is_dir():
        previous = xr.open_zarr(prev_path, consolidated=False)
    from fishai.ingestion.physics.wcofs_store import package_wcofs_cycle as _package

    packaged = _package(merged, target)
    packaged.attrs.update(extra_attrs)
    qc = run_cycle_qc(packaged, previous=previous)
    if partial:
        qc["partial_cycle"] = True
        qc["missing_leads"] = [f["valid_offset_h"] for f in failed]
    write_wcofs_cycle(merged, target, out_root, extra_attrs=extra_attrs, packaged=packaged)
    write_qc_report(qc, plan.qc_report_path or out_root / f"wcofs_{target:%Y%m%d}_qc.json")
    assert plan.pull_log is not None
    append_pull_log(build_day_success_record(target), log_path=plan.pull_log)
    return plan
