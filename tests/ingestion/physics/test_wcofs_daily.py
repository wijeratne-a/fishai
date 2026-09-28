"""Operational WCOFS daily job tests (fixtures only, no network)."""

from __future__ import annotations

import datetime as dt
import json
import math
import threading
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from fishai.ingestion.physics import http_util
from fishai.ingestion.physics.sources import wcofs as wcofs_src
from fishai.ingestion.physics.wcofs_daily import (
    LeadPlan,
    assemble_merged_dataset,
    build_lead_plan,
    evidence_from_forecast_age,
    fetch_and_log_leads,
    plan_daily,
    read_ocean_time_utc,
    requested_cycle_time,
    run_wcofs_daily,
    step_provenance_record,
    wait_for_primary_cycle,
)
from fishai.ingestion.physics.wcofs_pull_log import DEFAULT_PULL_LOG_DIR, resolve_pull_log_dir, sha256_bytes
from fishai.ingestion.physics.wcofs_store import DEFAULT_STORE_ROOT, package_wcofs_cycle
from fishai.ingestion.sources import REPO_ROOT
from wcofs_fixtures import write_mini_wcofs_bytes


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
    assert log["forecast_age_hours"] == 0.0
    assert log["evidence_state_hint"] == "nowcast"
    assert "lead_days" not in log
    assert float(packaged["forecast_age_hours"].sel(valid_offset_h=0).values) == 0.0


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
    assert log["source_cycle_time"] == wcofs_src.cycle_run_time(prev).isoformat()
    assert log["forecast_age_hours"] == 24.0
    assert log["evidence_state_hint"] == "forecast"
    assert log["lead_days"] == 1
    assert float(packaged["forecast_age_hours"].sel(valid_offset_h=0).values) == 24.0


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

    def exists(d: dt.date) -> bool:
        return d == dt.date(2026, 9, 26)

    plan = build_lead_plan(
        target,
        primary_available=False,
        max_missed_cycles=2,
        cycle_exists_fn=exists,
    )
    assert plan.leads
    unknown = [u for u in plan.unknown_slots if u["reason"] == "missing_operational_cycle"]
    assert unknown
    assert any(u["valid_offset_h"] == 72 for u in unknown)


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
    )
    assert plan.request_count == len(wcofs_src.TARGET_VALID_OFFSETS_H)
    assert plan.pull_log == tmp_path / "provenance" / "wcofs_pull_20260928.jsonl"


def test_idempotent_pull_log_skips_duplicate_etag(tmp_path: Path) -> None:
    target = dt.date(2026, 9, 28)
    payload = write_mini_wcofs_bytes(cycle_date=target, lead_tag="n024")
    plan = build_lead_plan(target, primary_available=True)
    plan.leads = plan.leads[:1]
    plan.s3_keys = plan.s3_keys[:1]
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
