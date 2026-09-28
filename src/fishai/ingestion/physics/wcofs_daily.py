"""Daily operational WCOFS pull for the FishAI pilot (batch-only, idempotent)."""

from __future__ import annotations

import datetime as dt
import json
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
    build_pull_record,
    load_pull_index,
    pull_log_path,
    sha256_bytes,
)
from fishai.ingestion.physics.wcofs_store import cycle_zarr_path, write_wcofs_cycle
from fishai.ingestion.sources import attribution_for, load_sources_manifest, require_approved

DEFAULT_WAIT_CUTOFF_UTC = dt.time(5, 45)
DEFAULT_MAX_MISSED_CYCLES = 2
FORECAST_HORIZON_H = 72
TEMP_MIN_C = -2.0
TEMP_MAX_C = 35.0
SALT_MIN_PSU = 0.0
SALT_MAX_PSU = 42.0


@dataclass(frozen=True)
class LeadPlan:
    lead_hour: int
    cycle_date: dt.date
    lead_tag: str
    fallback: str | None = None
    lead_hours_used: int | None = None


@dataclass
class DailyPlan:
    target_date: dt.date
    bbox: tuple[float, float, float, float]
    primary_available: bool
    leads: list[LeadPlan] = field(default_factory=list)
    unknown_leads: list[dict[str, Any]] = field(default_factory=list)
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


def build_lead_plan(
    target: dt.date,
    *,
    primary_available: bool,
    max_missed_cycles: int = DEFAULT_MAX_MISSED_CYCLES,
) -> DailyPlan:
    bbox = _pilot_bbox()
    plan = DailyPlan(target_date=target, bbox=bbox, primary_available=primary_available)
    for lh in wcofs_src.OPERATIONAL_LEAD_HOURS:
        if primary_available:
            tag = wcofs_src.lead_tag_for_hour(lh)
            lp = LeadPlan(lead_hour=lh, cycle_date=target, lead_tag=tag)
            plan.leads.append(lp)
            plan.s3_keys.append(wcofs_src.fields_s3_key(target, tag))
            continue
        resolved: LeadPlan | None = None
        for missed in range(1, max_missed_cycles + 1):
            prev = target - dt.timedelta(days=missed)
            used = lh + 24 * missed
            if used > FORECAST_HORIZON_H:
                break
            try:
                tag = wcofs_src.lead_tag_for_hour(used)
            except ValueError:
                break
            resolved = LeadPlan(
                lead_hour=lh,
                cycle_date=prev,
                lead_tag=tag,
                fallback="previous_cycle",
                lead_hours_used=used,
            )
            break
        if resolved is None:
            plan.unknown_leads.append(
                {
                    "lead_hour": lh,
                    "state": "UNKNOWN",
                    "reason": "missing_operational_cycle",
                }
            )
        else:
            plan.leads.append(resolved)
            plan.s3_keys.append(wcofs_src.fields_s3_key(resolved.cycle_date, resolved.lead_tag))
    plan.request_count = len(plan.s3_keys)
    return plan


def plan_daily(
    target: dt.date,
    *,
    out_root: Path,
    primary_available: bool | None = None,
    head_fn: Callable[[str], bool] | None = None,
    max_missed_cycles: int = DEFAULT_MAX_MISSED_CYCLES,
) -> DailyPlan:
    if primary_available is None:
        primary_available = wcofs_src.cycle_available(target, head_fn=head_fn)
    plan = build_lead_plan(
        target,
        primary_available=primary_available,
        max_missed_cycles=max_missed_cycles,
    )
    plan.zarr_path = cycle_zarr_path(target, out_root)
    plan.pull_log = pull_log_path(target.strftime("%Y%m%d"))
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
) -> tuple[list[tuple[LeadPlan, xr.Dataset]], list[str]]:
    """Fetch each planned lead, append pull log lines, return datasets and missing tags."""
    log_path = log_path or plan.pull_log
    assert log_path is not None
    index = load_pull_index(log_path) if skip_if_etag_matches else {}
    merged: list[tuple[LeadPlan, xr.Dataset]] = []
    missing: list[str] = []
    bbox = plan.bbox
    for lp in plan.leads:
        s3_key = wcofs_src.fields_s3_key(lp.cycle_date, lp.lead_tag)
        url = wcofs_src._fields_url_s3(lp.cycle_date, lp.lead_tag)
        try:
            data, meta = _fetch_lead_bytes(
                lp.cycle_date, lp.lead_tag, get_fn=get_fn, head_meta_fn=head_meta_fn
            )
            ds = wcofs_src.open_dataset_from_bytes(data)
            sub = wcofs_src.subset_bbox(ds, bbox)
            merged.append((lp, sub))
            prior = index.get(s3_key)
            if skip_if_etag_matches and prior and prior.get("etag") == meta.get("etag"):
                continue
            rec = build_pull_record(
                s3_key=s3_key,
                url=url,
                cycle=cycle_id(lp.cycle_date),
                lead=lp.lead_tag,
                lead_hour=lp.lead_hour,
                status="ok",
                etag=meta.get("etag"),
                size_bytes=meta.get("size_bytes"),
                sha256=meta.get("sha256"),
                extra={
                    "target_cycle": cycle_id(plan.target_date),
                    "fallback": lp.fallback,
                    "lead_hours_used": lp.lead_hours_used,
                },
            )
            append_pull_log(rec, log_path=log_path)
        except Exception as exc:  # noqa: BLE001
            missing.append(lp.lead_tag)
            rec = build_pull_record(
                s3_key=s3_key,
                url=url,
                cycle=cycle_id(lp.cycle_date),
                lead=lp.lead_tag,
                lead_hour=lp.lead_hour,
                status="error",
                extra={"error": str(exc), "target_cycle": cycle_id(plan.target_date)},
            )
            append_pull_log(rec, log_path=log_path)
    return merged, missing


def assemble_merged_dataset(
    plan: DailyPlan,
    lead_slices: Sequence[tuple[LeadPlan, xr.Dataset]],
) -> xr.Dataset:
    datasets: list[xr.Dataset] = []
    ref_raw: xr.Dataset | None = None
    fallback_meta: list[dict[str, Any]] = []
    for lp, sub in sorted(lead_slices, key=lambda x: x[0].lead_hour):
        if ref_raw is None:
            ref_raw = sub
        sub = sub.expand_dims(lead_hours=[lp.lead_hour])
        if lp.fallback:
            sub = sub.assign_attrs(
                fallback=lp.fallback,
                lead_hours_used=int(lp.lead_hours_used or 0),
                source_cycle=cycle_id(lp.cycle_date),
            )
            fallback_meta.append(
                {
                    "lead_hour": lp.lead_hour,
                    "fallback": lp.fallback,
                    "source_cycle": cycle_id(lp.cycle_date),
                    "lead_hours_used": lp.lead_hours_used,
                }
            )
        datasets.append(sub)

    merged = xr.concat(datasets, dim="lead_hours")
    merged.attrs["attribution"] = attribution_for("wcofs")
    merged.attrs["source"] = "wcofs"
    merged.attrs["cycle"] = cycle_id(plan.target_date)
    if plan.unknown_leads:
        merged.attrs["unknown_valid_times"] = json.dumps(plan.unknown_leads)
    if fallback_meta:
        merged.attrs["fallback_leads"] = json.dumps(fallback_meta)

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
    ref = packaged.isel(lead_hours=0)
    wet = ref["MLD_m"].notnull() if "MLD_m" in packaged else ref["temp"].isel(s_rho=0).notnull()
    wet_count = int(wet.sum())
    total = int(wet.size) or 1

    def _nan_frac(da: xr.DataArray) -> float:
        arr = da.values
        mask = wet.values if wet.ndim == arr.ndim[-2:] else np.ones(arr.shape[-2:], dtype=bool)
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
) -> DailyPlan:
    require_approved("wcofs")
    if dry_run:
        return plan_daily(
            target,
            out_root=out_root,
            primary_available=True,
            max_missed_cycles=max_missed_cycles,
        )
    primary_available = wcofs_src.cycle_available(target, head_fn=head_fn)
    if wait_for_cycle and not primary_available and not dry_run:
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
    )

    zpath = plan.zarr_path
    assert zpath is not None
    if zpath.is_dir() and _pull_complete(plan.pull_log, plan.s3_keys):
        return plan

    lead_slices, missing = fetch_and_log_leads(
        plan,
        get_fn=get_fn,
        head_meta_fn=head_meta_fn,
        log_path=plan.pull_log,
    )
    partial = bool(missing)
    merged = assemble_merged_dataset(plan, lead_slices)
    extra_attrs = {
        "partial_cycle": partial,
        "missing_leads": json.dumps(missing),
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
        qc["missing_leads"] = missing
    write_wcofs_cycle(merged, target, out_root, extra_attrs=extra_attrs, packaged=packaged)
    write_qc_report(qc, plan.qc_report_path or out_root / f"wcofs_{target:%Y%m%d}_qc.json")
    return plan
