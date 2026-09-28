"""Operational WCOFS daily job tests (fixtures only, no network)."""

from __future__ import annotations

import datetime as dt
import json
import math
import re
import threading
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import xarray as xr

from fishai.ingestion.physics import http_util
from fishai.ingestion.physics.sources import wcofs as wcofs_src
from fishai.ingestion.physics.wcofs_daily import (
    LeadPlan,
    assemble_merged_dataset,
    build_lead_plan,
    evidence_from_forecast_age,
    expected_valid_time,
    fetch_and_log_leads,
    plan_daily,
    read_ocean_time_utc,
    requested_cycle_time,
    run_wcofs_daily,
    step_provenance_record,
    wait_for_primary_cycle,
)
from fishai.ingestion.physics.wcofs_pull_log import (
    DAY_SUCCESS_RECORD_TYPE,
    DAY_TOMBSTONE_RECORD_TYPE,
    DEFAULT_PULL_LOG_DIR,
    load_day_outcome,
    load_day_tombstone,
    resolve_pull_log_dir,
    sha256_bytes,
)
from fishai.ingestion.physics.wcofs_store import DEFAULT_STORE_ROOT, package_wcofs_cycle, write_wcofs_cycle
from fishai.ingestion.sources import REPO_ROOT
from fishai.physics.store import WcofsDayFailed, latest_wcofs_cycle_date, open_wcofs_cycle
from wcofs_fixtures import write_mini_wcofs_bytes

_FIELDS_URL = re.compile(r"wcofs\.t03z\.(\d{8})\.fields\.(\w+)\.nc")


def _parse_fields_url(url: str) -> tuple[dt.date, str]:
    match = _FIELDS_URL.search(url)
    assert match is not None, url
    ymd = match.group(1)
    day = dt.date(int(ymd[:4]), int(ymd[4:6]), int(ymd[6:8]))
    return day, match.group(2)


def _three_hour_offsets(start_h: int, end_h: int) -> set[int]:
    return set(range(start_h, end_h + 1, 3))


def test_resolve_pull_log_dir_routes_tmp_path_to_local_provenance(tmp_path: Path) -> None:
    assert resolve_pull_log_dir(tmp_path) == tmp_path / "provenance"
    assert resolve_pull_log_dir(DEFAULT_STORE_ROOT) == DEFAULT_PULL_LOG_DIR


def test_all_field_leads_include_nowcast_and_forecast_overlap() -> None:
    assert wcofs_src.lead_tag_for_valid_offset(3) == "f003"
    assert wcofs_src.lead_tag_for_valid_offset(0) == "n024"
    assert wcofs_src.lead_tag_for_valid_offset(-3) == "n021"
    assert len(wcofs_src.operational_lead_tags()) == len(wcofs_src.ALL_FIELD_LEADS)


def test_ocean_time_in_fixture_matches_wcofs_valid_time_pattern() -> None:
    cycle = dt.date(2026, 9, 26)
    r = wcofs_src.cycle_run_time(cycle)
    for tag, offset_h in (("n003", -21), ("n024", 0), ("f003", 3), ("f027", 27)):
        payload = write_mini_wcofs_bytes(cycle_date=cycle, lead_tag=tag)
        ds = wcofs_src.open_dataset_from_bytes(payload)
        valid = read_ocean_time_utc(ds)
        assert valid == r + dt.timedelta(hours=offset_h)


@pytest.mark.parametrize(
    ("age", "fallback", "hint", "lead_days"),
    [
        (-3.0, False, "nowcast", None),
        (-21.0, False, "nowcast", None),
        (0.0, False, "nowcast", None),
        (3.0, False, "forecast", 1),
        (27.0, False, "forecast", 2),
        (0.0, True, "forecast", 1),
    ],
)
def test_evidence_from_forecast_age(age: float, fallback: bool, hint: str, lead_days: int | None) -> None:
    got_hint, got_days = evidence_from_forecast_age(age, fallback_used=fallback)
    assert got_hint == hint
    if lead_days is None:
        assert got_days is None
    else:
        assert got_days == lead_days


def _packaged_single(
    target: dt.date,
    *,
    cycle_date: dt.date,
    lead_tag: str,
    valid_offset_h: int,
    tmp_path: Path,
    fallback: str | None = None,
) -> tuple[Any, dict[str, Any]]:
    plan = DailyPlanStub(target, valid_offset_h, cycle_date, lead_tag, fallback)
    payload = write_mini_wcofs_bytes(cycle_date=cycle_date, lead_tag=lead_tag)
    log_path = tmp_path / "provenance" / "pull.jsonl"
    plan.pull_log = log_path

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        return payload

    def fake_head(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": "abc", "size_bytes": len(payload)}

    slices, _failed = fetch_and_log_leads(
        plan,
        get_fn=fake_get,
        head_meta_fn=fake_head,
        log_path=log_path,
        skip_if_etag_matches=False,
    )
    merged = assemble_merged_dataset(plan, slices)
    packaged = package_wcofs_cycle(merged, target)
    log_line = json.loads(log_path.read_text(encoding="utf-8").strip().splitlines()[0])
    return packaged, log_line


class DailyPlanStub:
    """Minimal plan object for single-step packaging tests."""

    def __init__(
        self,
        target: dt.date,
        valid_offset_h: int,
        cycle_date: dt.date,
        lead_tag: str,
        fallback: str | None,
    ) -> None:
        self.target_date = target
        self.bbox = (32.0, 35.0, -121.0, -117.0)
        self.primary_available = cycle_date == target and fallback is None
        self.leads = [LeadPlan(valid_offset_h, cycle_date, lead_tag, fallback)]
        self.unknown_slots: list[dict[str, Any]] = []
        self.pull_log: Path | None = None


def test_normal_cycle_uses_ocean_time_and_nowcast_age(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)
    packaged, log = _packaged_single(
        target,
        cycle_date=target,
        lead_tag="n024",
        valid_offset_h=0,
        tmp_path=tmp_path,
    )
    r = requested_cycle_time(target)
    assert log["forecast_age_hours"] == 0.0
    assert log["evidence_state_hint"] == "nowcast"
    assert log["source_run_time"] == r.isoformat()
    assert "lead_days" not in log
    assert float(packaged["forecast_age_hours"].sel(valid_offset_h=0).values) == 0.0
    assert str(packaged["source_run_time"].sel(valid_offset_h=0).values)[:19] == r.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )


def test_fallback_uses_prior_source_cycle_and_forecast_age(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)
    prev = target - dt.timedelta(days=1)
    packaged, log = _packaged_single(
        target,
        cycle_date=prev,
        lead_tag="f024",
        valid_offset_h=0,
        tmp_path=tmp_path,
        fallback="previous_cycle",
    )
    src_r = wcofs_src.cycle_run_time(prev)
    assert log["source_cycle_time"] == src_r.isoformat()
    assert log["source_run_time"] == src_r.isoformat()
    assert log["forecast_age_hours"] == 24.0
    assert log["evidence_state_hint"] == "forecast"
    assert log["lead_days"] == 1
    assert float(packaged["forecast_age_hours"].sel(valid_offset_h=0).values) == 24.0
    assert str(packaged["source_run_time"].sel(valid_offset_h=0).values)[:19] == src_r.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )


def test_walkback_skips_missing_runs(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)

    def exists(d: dt.date) -> bool:
        return d == dt.date(2026, 9, 26)

    plan = build_lead_plan(
        target,
        primary_available=False,
        max_missed_cycles=3,
        cycle_exists_fn=exists,
    )
    assert plan.leads
    assert all(lp.cycle_date == dt.date(2026, 9, 26) for lp in plan.leads)


def test_two_missing_operational_days_walkback_or_unknown() -> None:
    target = dt.date(2026, 9, 28)
    source_day = dt.date(2026, 9, 26)
    expected_covered = _three_hour_offsets(-21, 24)
    expected_unknown = _three_hour_offsets(27, 72)

    def exists(d: dt.date) -> bool:
        return d == source_day

    plan = build_lead_plan(
        target,
        primary_available=False,
        max_missed_cycles=2,
        cycle_exists_fn=exists,
    )
    covered_offsets = {lp.valid_offset_h for lp in plan.leads}
    assert covered_offsets == expected_covered
    unknown = [u for u in plan.unknown_slots if u["reason"] == "missing_operational_cycle"]
    assert {u["valid_offset_h"] for u in unknown} == expected_unknown
    for lp in plan.leads:
        assert lp.cycle_date == source_day
        assert lp.fallback == "previous_cycle"
        assert lp.lead_tag.startswith("f")
        age_h = lp.valid_offset_h + 48
        assert age_h == int(lp.lead_tag[1:])
        assert lp.lead_tag == wcofs_src.lead_tag_for_age_from_source(age_h)


def test_two_missed_runs_fallback_source_run_time_in_log_and_zarr(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)
    source_day = dt.date(2026, 9, 26)
    source_r = requested_cycle_time(source_day)

    def exists(d: dt.date) -> bool:
        return d == source_day

    plan = build_lead_plan(
        target,
        primary_available=False,
        max_missed_cycles=2,
        cycle_exists_fn=exists,
    )
    plan.pull_log = tmp_path / "provenance" / "pull.jsonl"
    payloads = {
        (lp.cycle_date, lp.lead_tag): write_mini_wcofs_bytes(
            cycle_date=lp.cycle_date, lead_tag=lp.lead_tag
        )
        for lp in plan.leads
    }

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        for lp in plan.leads:
            key = wcofs_src.fields_s3_key(lp.cycle_date, lp.lead_tag)
            if key in url or lp.lead_tag in url:
                return payloads[(lp.cycle_date, lp.lead_tag)]
        raise KeyError(url)

    def fake_head(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": "e", "size_bytes": 100}

    slices, failed = fetch_and_log_leads(
        plan,
        get_fn=fake_get,
        head_meta_fn=fake_head,
        log_path=plan.pull_log,
        skip_if_etag_matches=False,
    )
    assert not failed
    merged = assemble_merged_dataset(plan, slices)
    packaged = package_wcofs_cycle(merged, target)
    for lp in plan.leads:
        off = lp.valid_offset_h
        assert float(packaged["forecast_age_hours"].sel(valid_offset_h=off).values) == off + 48
        assert packaged["evidence_state_hint"].sel(valid_offset_h=off).values == "forecast"
        run_t = packaged["source_run_time"].sel(valid_offset_h=off).values
        assert str(run_t)[:19] == source_r.strftime("%Y-%m-%dT%H:%M:%S")
    log_lines = [
        json.loads(line) for line in plan.pull_log.read_text(encoding="utf-8").strip().splitlines()
    ]
    for rec in log_lines:
        assert rec["status"] == "ok"
        assert rec["source_run_time"] == source_r.isoformat()
        assert rec["fallback_used"] is True
        assert rec["forecast_age_hours"] == rec["lead_hour"] + 48
        assert rec["evidence_state_hint"] == "forecast"


def test_valid_time_mismatch_skips_zarr_step_and_marks_unknown(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)
    plan = build_lead_plan(target, primary_available=True, cycle_exists_fn=lambda _d: True)
    good = next(lp for lp in plan.leads if lp.valid_offset_h == -21)
    bad = next(lp for lp in plan.leads if lp.valid_offset_h == 3)
    plan.leads = [good, bad]
    plan.s3_keys = [
        wcofs_src.fields_s3_key(lp.cycle_date, lp.lead_tag) for lp in plan.leads
    ]
    log_path = tmp_path / "pull.jsonl"
    plan.pull_log = log_path
    good_bytes = write_mini_wcofs_bytes(cycle_date=target, lead_tag=good.lead_tag)
    bad_bytes = write_mini_wcofs_bytes(
        cycle_date=target, lead_tag=bad.lead_tag, valid_time_shift_h=3
    )

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        if bad.lead_tag in url:
            return bad_bytes
        return good_bytes

    def fake_head(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": "x", "size_bytes": 10}

    slices, failed = fetch_and_log_leads(
        plan,
        get_fn=fake_get,
        head_meta_fn=fake_head,
        log_path=log_path,
        skip_if_etag_matches=False,
    )
    assert len(slices) == 1
    assert slices[0][0].valid_offset_h == -21
    assert len(failed) == 1
    assert failed[0]["valid_offset_h"] == 3
    assert failed[0]["reason"] == "valid_time_mismatch"
    assert failed[0]["state"] == "UNKNOWN"
    assert failed[0]["evidence_state_hint"] == "UNKNOWN"
    expected = expected_valid_time(target, 3)
    assert failed[0]["expected_valid_time"] == expected.isoformat()
    assert "actual_valid_time" in failed[0]
    err_line = json.loads(log_path.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert err_line["status"] == "error"
    assert err_line["reason"] == "valid_time_mismatch"
    assert err_line["expected_valid_time"] == expected.isoformat()
    merged = assemble_merged_dataset(plan, slices)
    packaged = package_wcofs_cycle(merged, target)
    assert -21 in packaged.valid_offset_h.values
    assert 3 not in packaged.valid_offset_h.values


def test_download_failed_marks_unknown(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)
    plan = build_lead_plan(target, primary_available=True, cycle_exists_fn=lambda _d: True)
    plan.leads = plan.leads[:1]
    plan.s3_keys = plan.s3_keys[:1]
    plan.pull_log = tmp_path / "pull.jsonl"
    payload = write_mini_wcofs_bytes(cycle_date=target, lead_tag=plan.leads[0].lead_tag)
    calls = {"n": 0}

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        calls["n"] += 1
        raise IOError("fail")

    def fake_head(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": "x", "size_bytes": len(payload)}

    slices, failed = fetch_and_log_leads(
        plan,
        get_fn=fake_get,
        head_meta_fn=fake_head,
        log_path=plan.pull_log,
        skip_if_etag_matches=False,
    )
    assert not slices
    assert failed[0]["reason"] == "download_failed"
    assert failed[0]["evidence_state_hint"] == "UNKNOWN"


def test_dry_run_lists_keys_and_request_count(tmp_path: Path) -> None:
    plan = plan_daily(
        dt.date(2026, 9, 28),
        out_root=tmp_path,
        primary_available=True,
        cycle_exists_fn=lambda _d: True,
    )
    assert plan.request_count == len(wcofs_src.TARGET_VALID_OFFSETS_H)
    assert plan.pull_log == tmp_path / "provenance" / "wcofs_pull_20260928.jsonl"


def test_idempotent_pull_log_skips_duplicate_etag(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)
    plan = build_lead_plan(target, primary_available=True)
    plan.leads = plan.leads[:1]
    plan.s3_keys = plan.s3_keys[:1]
    lead = plan.leads[0]
    payload = write_mini_wcofs_bytes(cycle_date=target, lead_tag=lead.lead_tag)
    log_path = tmp_path / "pull.jsonl"
    plan.pull_log = log_path

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        return payload

    def fake_head(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": "abc", "size_bytes": len(payload)}

    fetch_and_log_leads(plan, get_fn=fake_get, head_meta_fn=fake_head, log_path=log_path)
    fetch_and_log_leads(plan, get_fn=fake_get, head_meta_fn=fake_head, log_path=log_path)
    assert len(log_path.read_text(encoding="utf-8").strip().splitlines()) == 1


def test_wait_for_cycle_respects_cutoff() -> None:
    target = dt.date(2026, 9, 28)
    times = [
        dt.datetime(2026, 9, 28, 5, 0, tzinfo=dt.timezone.utc),
        dt.datetime(2026, 9, 28, 6, 0, tzinfo=dt.timezone.utc),
    ]

    def now_fn() -> dt.datetime:
        return times.pop(0)

    assert (
        wait_for_primary_cycle(
            target,
            head_fn=lambda _u: False,
            cutoff_utc=dt.time(5, 45),
            now_fn=now_fn,
            sleep_fn=lambda _s: None,
        )
        is False
    )


def test_max_concurrent_per_host_is_two() -> None:
    assert http_util.MAX_CONCURRENT_PER_HOST == 2


def test_plan_daily_defaults_cycle_exists_from_availability_probe(tmp_path: Path) -> None:
    """Walk-back uses cycle availability probes unless cycle_exists_fn is injected."""
    target = dt.date(2026, 9, 28)
    source_day = dt.date(2026, 9, 26)

    def head(url: str) -> bool:
        if "fields.n024.nc" not in url:
            return False
        return source_day.strftime("%Y/%m/%d") in url

    plan = plan_daily(
        target,
        out_root=tmp_path,
        primary_available=False,
        head_fn=head,
    )
    assert {lp.valid_offset_h for lp in plan.leads} == _three_hour_offsets(-21, 24)
    assert all(lp.cycle_date == source_day for lp in plan.leads)
    unknown = [u for u in plan.unknown_slots if u["reason"] == "missing_operational_cycle"]
    assert {u["valid_offset_h"] for u in unknown} == _three_hour_offsets(27, 72)


def test_run_wcofs_daily_walkback_via_mocked_http_only(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)
    source_day = dt.date(2026, 9, 26)
    source_r = requested_cycle_time(source_day)
    head_lock = threading.Lock()
    head_inflight = {"n": 0, "max": 0}

    def head(url: str) -> bool:
        with head_lock:
            head_inflight["n"] += 1
            head_inflight["max"] = max(head_inflight["max"], head_inflight["n"])
        try:
            if "fields.n024.nc" not in url:
                return False
            day, _lead = _parse_fields_url(url)
            return day == source_day
        finally:
            with head_lock:
                head_inflight["n"] -= 1

    payload_cache: dict[tuple[dt.date, str], bytes] = {}

    def get_fn(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        day, lead = _parse_fields_url(url)
        key = (day, lead)
        if key not in payload_cache:
            payload_cache[key] = write_mini_wcofs_bytes(cycle_date=day, lead_tag=lead)
        return payload_cache[key]

    def head_meta(url: str) -> dict[str, Any]:
        with head_lock:
            head_inflight["n"] += 1
            head_inflight["max"] = max(head_inflight["max"], head_inflight["n"])
        try:
            return {"status": 200, "etag": "mock-etag", "size_bytes": 100}
        finally:
            with head_lock:
                head_inflight["n"] -= 1

    plan = run_wcofs_daily(
        target,
        out_root=tmp_path,
        dry_run=False,
        wait_for_cycle=False,
        head_fn=head,
        get_fn=get_fn,
        head_meta_fn=head_meta,
    )
    assert head_inflight["max"] <= http_util.MAX_CONCURRENT_PER_HOST
    assert plan.zarr_path is not None and plan.zarr_path.is_dir()
    assert {lp.valid_offset_h for lp in plan.leads} == _three_hour_offsets(-21, 24)
    assert all(lp.cycle_date == source_day for lp in plan.leads)
    missing = [u for u in plan.unknown_slots if u["reason"] == "missing_operational_cycle"]
    assert {u["valid_offset_h"] for u in missing} == _three_hour_offsets(27, 72)
    assert not any(u.get("reason") == "download_failed" for u in plan.unknown_slots)

    import xarray as xr

    packaged = xr.open_zarr(plan.zarr_path, consolidated=False)
    for off in _three_hour_offsets(-21, 24):
        assert str(packaged["source_run_time"].sel(valid_offset_h=off).values)[:19] == source_r.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        assert packaged["evidence_state_hint"].sel(valid_offset_h=off).values == "forecast"

    log_path = plan.pull_log
    assert log_path is not None
    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").strip().splitlines()]
    pull_records = [r for r in records if r.get("s3_key")]
    assert pull_records
    assert all(r["status"] == "ok" for r in pull_records)
    assert all(r.get("reason") != "download_failed" for r in pull_records)
    assert all(r["source_run_time"] == source_r.isoformat() for r in pull_records)
    assert all(r["fallback_used"] is True for r in pull_records)
    assert all(r["forecast_age_hours"] == r["lead_hour"] + 48 for r in pull_records)


def test_run_wcofs_daily_dry_run(tmp_path: Path) -> None:
    plan = run_wcofs_daily(
        dt.date(2026, 9, 28),
        out_root=tmp_path,
        dry_run=True,
        wait_for_cycle=False,
        head_fn=lambda _u: True,
    )
    assert plan.request_count == len(wcofs_src.TARGET_VALID_OFFSETS_H)
    assert not (tmp_path / "wcofs_20260928.zarr").exists()


def _provenance_tree_snapshot() -> dict[str, tuple[int, int]]:
    root = REPO_ROOT / "data" / "provenance"
    if not root.is_dir():
        return {}
    return {
        str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }


def test_cli_wcofs_daily_dry_run(tmp_path: Path, capsys, repo_provenance_snapshot) -> None:
    from fishai.ingestion.physics.cli import main

    code = main(
        ["wcofs-daily", "--date", "2026-09-28", "--out", str(tmp_path), "--dry-run"]
    )
    assert code == 0
    assert "requests=" in capsys.readouterr().out
    assert _provenance_tree_snapshot() == repo_provenance_snapshot


def test_run_wcofs_daily_total_failure_writes_tombstone_not_zarr(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)
    prev = target - dt.timedelta(days=1)
    write_wcofs_cycle(_synthetic_merged_for_reader(), prev, tmp_path)

    plan = run_wcofs_daily(
        target,
        out_root=tmp_path,
        dry_run=False,
        wait_for_cycle=False,
        head_fn=lambda _u: False,
    )
    assert plan.pull_log is not None
    tombstone = load_day_tombstone(plan.pull_log)
    assert tombstone is not None
    assert tombstone["record_type"] == DAY_TOMBSTONE_RECORD_TYPE
    assert tombstone["status"] == "failed"
    assert tombstone["reason"] == "wcofs_nowcast_missing"
    assert plan.zarr_path is not None and not plan.zarr_path.is_dir()

    with pytest.raises(WcofsDayFailed) as excinfo:
        open_wcofs_cycle(target, store_root=tmp_path)
    assert excinfo.value.reason == "wcofs_nowcast_missing"
    with pytest.raises(WcofsDayFailed):
        latest_wcofs_cycle_date(tmp_path, as_of=target)
    open_wcofs_cycle(prev, store_root=tmp_path)


def test_run_wcofs_daily_partial_failure_still_writes_zarr(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)

    def head(url: str) -> bool:
        return target.strftime("%Y/%m/%d") in url and "fields.n024.nc" in url

    payload_cache: dict[tuple[dt.date, str], bytes] = {}

    def get_fn(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        day, lead = _parse_fields_url(url)
        key = (day, lead)
        if lead == "f003":
            raise IOError("simulated partial outage")
        if key not in payload_cache:
            payload_cache[key] = write_mini_wcofs_bytes(cycle_date=day, lead_tag=lead)
        return payload_cache[key]

    def head_meta(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": "mock", "size_bytes": 100}

    plan = run_wcofs_daily(
        target,
        out_root=tmp_path,
        dry_run=False,
        wait_for_cycle=False,
        head_fn=head,
        get_fn=get_fn,
        head_meta_fn=head_meta,
    )
    assert plan.zarr_path is not None and plan.zarr_path.is_dir()
    assert plan.pull_log is not None and load_day_outcome(plan.pull_log)[0] == "success"
    import xarray as xr

    packaged = xr.open_zarr(plan.zarr_path, consolidated=False)
    assert 0 in packaged.valid_offset_h.values
    assert 3 not in packaged.valid_offset_h.values


def test_utc_today_uses_utc_not_local_date(monkeypatch: pytest.MonkeyPatch) -> None:
    from fishai.ingestion.physics.wcofs_pull_log import utc_today

    # 2026-09-29 02:30 UTC is still 2026-09-28 evening in US Pacific.
    fixed = dt.datetime(2026, 9, 29, 2, 30, tzinfo=dt.timezone.utc)
    monkeypatch.setattr(
        "fishai.ingestion.physics.wcofs_pull_log.datetime",
        type(
            "FakeDatetime",
            (),
            {"now": staticmethod(lambda tz=None: fixed)},
        ),
    )
    assert utc_today() == dt.date(2026, 9, 29)


def test_cli_wcofs_daily_default_date_is_utc(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    import fishai.ingestion.physics.cli as cli_mod

    fixed = dt.datetime(2026, 9, 29, 2, 30, tzinfo=dt.timezone.utc)
    monkeypatch.setattr(
        "fishai.ingestion.physics.wcofs_pull_log.datetime",
        type(
            "FakeDatetime",
            (),
            {"now": staticmethod(lambda tz=None: fixed)},
        ),
    )

    code = cli_mod.main(["wcofs-daily", "--out", str(tmp_path), "--dry-run"])
    assert code == 0
    assert "target_cycle=2026-09-29" in capsys.readouterr().out


def test_run_wcofs_daily_missing_nowcast_slot_tombstones(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)

    def head(url: str) -> bool:
        return target.strftime("%Y/%m/%d") in url and "fields.n024.nc" in url

    payload_cache: dict[tuple[dt.date, str], bytes] = {}

    def get_fn(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        day, lead = _parse_fields_url(url)
        if lead == "n024":
            raise IOError("nowcast lead missing")
        key = (day, lead)
        if key not in payload_cache:
            payload_cache[key] = write_mini_wcofs_bytes(cycle_date=day, lead_tag=lead)
        return payload_cache[key]

    def head_meta(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": "mock", "size_bytes": 100}

    plan = run_wcofs_daily(
        target,
        out_root=tmp_path,
        dry_run=False,
        wait_for_cycle=False,
        head_fn=head,
        get_fn=get_fn,
        head_meta_fn=head_meta,
    )
    assert plan.pull_log is not None
    outcome, tomb = load_day_outcome(plan.pull_log)
    assert outcome == "failed"
    assert tomb is not None and tomb["reason"] == "wcofs_nowcast_missing"
    assert plan.zarr_path is not None and not plan.zarr_path.is_dir()
    with pytest.raises(WcofsDayFailed):
        open_wcofs_cycle(target, store_root=tmp_path)


def _mock_full_day_http(target: dt.date) -> tuple[Any, Any, Any]:
    payload_cache: dict[tuple[dt.date, str], bytes] = {}

    def head(url: str) -> bool:
        return target.strftime("%Y/%m/%d") in url and "fields.n024.nc" in url

    def get_fn(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        day, lead = _parse_fields_url(url)
        key = (day, lead)
        if key not in payload_cache:
            payload_cache[key] = write_mini_wcofs_bytes(cycle_date=day, lead_tag=lead)
        return payload_cache[key]

    def head_meta(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": "mock", "size_bytes": 100}

    return head, get_fn, head_meta


def test_failed_rerun_after_success_keeps_valid_zarr(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)
    head, get_fn, head_meta = _mock_full_day_http(target)
    first = run_wcofs_daily(
        target,
        out_root=tmp_path,
        dry_run=False,
        wait_for_cycle=False,
        head_fn=head,
        get_fn=get_fn,
        head_meta_fn=head_meta,
    )
    assert first.zarr_path is not None and first.zarr_path.is_dir()

    run_wcofs_daily(
        target,
        out_root=tmp_path,
        dry_run=False,
        wait_for_cycle=False,
        head_fn=lambda _u: False,
    )
    assert first.zarr_path.is_dir()
    open_wcofs_cycle(target, store_root=tmp_path)
    assert load_day_outcome(first.pull_log)[0] == "failed"


def test_run_wcofs_daily_rerun_after_tombstone_writes_zarr(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)
    failed = run_wcofs_daily(
        target,
        out_root=tmp_path,
        dry_run=False,
        wait_for_cycle=False,
        head_fn=lambda _u: False,
    )
    assert failed.pull_log is not None
    assert load_day_outcome(failed.pull_log)[0] == "failed"

    head, get_fn, head_meta = _mock_full_day_http(target)
    plan = run_wcofs_daily(
        target,
        out_root=tmp_path,
        dry_run=False,
        wait_for_cycle=False,
        head_fn=head,
        get_fn=get_fn,
        head_meta_fn=head_meta,
    )
    assert plan.zarr_path is not None and plan.zarr_path.is_dir()
    assert plan.pull_log is not None
    outcome, success = load_day_outcome(plan.pull_log)
    assert outcome == "success"
    assert success is not None and success["record_type"] == DAY_SUCCESS_RECORD_TYPE
    open_wcofs_cycle(target, store_root=tmp_path)


def _synthetic_merged_for_reader() -> Any:
    n_s, n_eta, n_xi = 4, 3, 3
    s_rho = (np.arange(1, n_s + 1) - n_s - 0.5) / n_s
    lat = np.linspace(33.0, 33.1, n_eta)
    lon = np.linspace(-120.0, -119.9, n_xi)
    lat2d = np.broadcast_to(lat[:, None], (n_eta, n_xi))
    lon2d = np.broadcast_to(lon[None, :], (n_eta, n_xi))
    h = np.full((n_eta, n_xi), 100.0)
    temp = np.linspace(10, 18, n_s)[:, None, None] * np.ones((n_s, n_eta, n_xi))
    salt = np.full((n_s, n_eta, n_xi), 33.5)
    base = xr.Dataset(
        {
            "temp": (("s_rho", "eta_rho", "xi_rho"), temp),
            "salt": (("s_rho", "eta_rho", "xi_rho"), salt),
            "zeta": (("eta_rho", "xi_rho"), np.zeros((n_eta, n_xi))),
            "h": (("eta_rho", "xi_rho"), h),
            "mask_rho": (("eta_rho", "xi_rho"), np.ones((n_eta, n_xi))),
            "lat_rho": (("eta_rho", "xi_rho"), lat2d),
            "lon_rho": (("eta_rho", "xi_rho"), lon2d),
            "hc": 50.0,
            "s_rho": ("s_rho", s_rho),
            "Cs_r": ("s_rho", np.linspace(-1, 0, n_s)),
        }
    )
    merged = base.expand_dims(lead_hours=[3])
    merged.attrs["attribution"] = "WCOFS"
    merged.attrs["source"] = "wcofs"
    return merged
