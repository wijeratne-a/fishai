"""Operational WCOFS daily job tests (fixtures only, no network)."""

from __future__ import annotations

import datetime as dt
import json
import threading
from pathlib import Path
from typing import Any

import pytest

from fishai.ingestion.physics import http_util
from fishai.ingestion.physics.sources import wcofs as wcofs_src
from fishai.ingestion.physics.wcofs_daily import (
    build_lead_plan,
    fetch_and_log_leads,
    plan_daily,
    run_wcofs_daily,
    wait_for_primary_cycle,
)
from fishai.ingestion.physics.wcofs_pull_log import DEFAULT_PULL_LOG_DIR, resolve_pull_log_dir, sha256_bytes
from fishai.ingestion.physics.wcofs_store import DEFAULT_STORE_ROOT
from fishai.ingestion.sources import REPO_ROOT
from wcofs_fixtures import write_mini_wcofs_bytes


def test_resolve_pull_log_dir_routes_tmp_path_to_local_provenance(tmp_path: Path) -> None:
    assert resolve_pull_log_dir(tmp_path) == tmp_path / "provenance"
    assert resolve_pull_log_dir(DEFAULT_STORE_ROOT) == DEFAULT_PULL_LOG_DIR


def test_fields_s3_key_t03z_nowcast_and_forecast() -> None:
    day = dt.date(2026, 9, 28)
    assert wcofs_src.fields_s3_key(day, "n003").endswith(
        "wcofs/netcdf/2026/09/28/wcofs.t03z.20260928.fields.n003.nc"
    )
    assert wcofs_src.fields_s3_key(day, "f072").endswith(
        "wcofs.t03z.20260928.fields.f072.nc"
    )
    assert wcofs_src.lead_tag_for_hour(3) == "n003"
    assert wcofs_src.lead_tag_for_hour(27) == "f027"


def test_subset_bbox_margin_expands_indices() -> None:
    import xarray as xr

    payload = write_mini_wcofs_bytes(n_eta=6, n_xi=6)
    ds = wcofs_src.open_dataset_from_bytes(payload)
    tight = wcofs_src.subset_bbox(ds, (32.0, 35.0, -121.0, -117.0), margin_cells=0)
    loose = wcofs_src.subset_bbox(ds, (32.0, 35.0, -121.0, -117.0), margin_cells=2)
    assert loose.sizes["eta_rho"] >= tight.sizes["eta_rho"]
    assert loose.sizes["xi_rho"] >= tight.sizes["xi_rho"]


def test_pull_log_sha256() -> None:
    data = b"wcofs-fixture"
    assert sha256_bytes(data) == sha256_bytes(data)
    assert len(sha256_bytes(data)) == 64


def test_build_lead_plan_fallback_previous_cycle() -> None:
    plan = build_lead_plan(dt.date(2026, 9, 28), primary_available=False, max_missed_cycles=2)
    first = plan.leads[0]
    assert first.lead_hour == 3
    assert first.cycle_date == dt.date(2026, 9, 27)
    assert first.lead_tag == "f027"
    assert first.fallback == "previous_cycle"
    assert first.lead_hours_used == 27


def test_unknown_after_forecast_horizon() -> None:
    plan = build_lead_plan(dt.date(2026, 9, 28), primary_available=False, max_missed_cycles=2)
    unknown_hours = {u["lead_hour"] for u in plan.unknown_leads}
    assert 51 in unknown_hours
    assert all(u["reason"] == "missing_operational_cycle" for u in plan.unknown_leads)


def test_dry_run_lists_keys_and_request_count(tmp_path: Path) -> None:
    plan = plan_daily(
        dt.date(2026, 9, 28),
        out_root=tmp_path,
        primary_available=True,
    )
    assert plan.request_count == len(wcofs_src.OPERATIONAL_LEAD_HOURS)
    assert all(k.startswith("wcofs/netcdf/") for k in plan.s3_keys)
    assert plan.zarr_path == tmp_path / "wcofs_20260928.zarr"
    assert plan.pull_log == tmp_path / "provenance" / "wcofs_pull_20260928.jsonl"
    assert plan.qc_report_path == tmp_path / "wcofs_20260928_qc.json"
    assert not plan.pull_log.parent.exists() or not any(plan.pull_log.parent.iterdir())


def test_idempotent_pull_log_skips_duplicate_etag(tmp_path: Path) -> None:
    payload = write_mini_wcofs_bytes()
    plan = build_lead_plan(dt.date(2026, 9, 28), primary_available=True)
    plan.bbox = (32.0, 35.0, -121.0, -117.0)
    plan.target_date = dt.date(2026, 9, 28)
    plan.s3_keys = [wcofs_src.fields_s3_key(plan.target_date, wcofs_src.lead_tag_for_hour(3))]
    plan.leads = plan.leads[:1]
    log_path = tmp_path / "pull.jsonl"
    plan.pull_log = log_path

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        return payload

    def fake_head(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": "abc", "size_bytes": len(payload)}

    fetch_and_log_leads(plan, get_fn=fake_get, head_meta_fn=fake_head, log_path=log_path)
    fetch_and_log_leads(plan, get_fn=fake_get, head_meta_fn=fake_head, log_path=log_path)
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1


def test_partial_cycle_flags_missing_lead(tmp_path: Path) -> None:
    payload = write_mini_wcofs_bytes()
    plan = build_lead_plan(dt.date(2026, 9, 28), primary_available=True)
    plan.leads = plan.leads[:2]
    plan.s3_keys = plan.s3_keys[:2]
    log_path = tmp_path / "pull.jsonl"
    plan.pull_log = log_path
    plan.zarr_path = tmp_path / "wcofs_20260928.zarr"
    plan.qc_report_path = tmp_path / "wcofs_20260928_qc.json"
    calls = {"n": 0}

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        calls["n"] += 1
        if calls["n"] == 2:
            raise IOError("missing lead")
        return payload

    def fake_head(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": f"e{calls['n']}", "size_bytes": len(payload)}

    slices, missing = fetch_and_log_leads(
        plan, get_fn=fake_get, head_meta_fn=fake_head, log_path=log_path, skip_if_etag_matches=False
    )
    assert missing
    assert len(slices) == 1


def test_wait_for_cycle_respects_cutoff() -> None:
    target = dt.date(2026, 9, 28)
    times = [
        dt.datetime(2026, 9, 28, 5, 0, tzinfo=dt.timezone.utc),
        dt.datetime(2026, 9, 28, 6, 0, tzinfo=dt.timezone.utc),
    ]

    def now_fn() -> dt.datetime:
        return times.pop(0)

    ok = wait_for_primary_cycle(
        target,
        head_fn=lambda _u: False,
        cutoff_utc=dt.time(5, 45),
        now_fn=now_fn,
        sleep_fn=lambda _s: None,
    )
    assert ok is False


def test_max_concurrent_per_host_is_two() -> None:
    assert http_util.MAX_CONCURRENT_PER_HOST == 2
    limiter = http_util._HostLimiter(2)
    acquired = []

    def worker() -> None:
        limiter.acquire()
        acquired.append(1)
        limiter.release()

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=2)
    assert len(acquired) == 4


def test_run_wcofs_daily_dry_run(tmp_path: Path) -> None:
    plan = run_wcofs_daily(
        dt.date(2026, 9, 28),
        out_root=tmp_path,
        dry_run=True,
        wait_for_cycle=False,
        head_fn=lambda _u: True,
    )
    assert plan.request_count > 0
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
        [
            "wcofs-daily",
            "--date",
            "2026-09-28",
            "--out",
            str(tmp_path),
            "--dry-run",
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "wcofs.t03z.20260928.fields.n003.nc" in out
    assert "requests=" in out
    assert f"pull_log={tmp_path / 'provenance' / 'wcofs_pull_20260928.jsonl'}" in out
    assert not (tmp_path / "provenance").exists()
    assert _provenance_tree_snapshot() == repo_provenance_snapshot


def test_wcofs_writes_never_touch_repo_provenance(tmp_path: Path, repo_provenance_snapshot) -> None:
    from fishai.ingestion.physics.cli import main

    payload = write_mini_wcofs_bytes()
    plan = build_lead_plan(dt.date(2026, 9, 28), primary_available=True)
    plan.leads = plan.leads[:1]
    plan.s3_keys = plan.s3_keys[:1]
    plan.bbox = (32.0, 35.0, -121.0, -117.0)
    plan.target_date = dt.date(2026, 9, 28)
    plan.pull_log = tmp_path / "provenance" / "wcofs_pull_20260928.jsonl"
    plan.qc_report_path = tmp_path / "wcofs_20260928_qc.json"
    plan.zarr_path = tmp_path / "wcofs_20260928.zarr"

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        return payload

    def fake_head(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": "abc", "size_bytes": len(payload)}

    fetch_and_log_leads(
        plan,
        get_fn=fake_get,
        head_meta_fn=fake_head,
        log_path=plan.pull_log,
        skip_if_etag_matches=False,
    )
    run_wcofs_daily(
        dt.date(2026, 9, 28),
        out_root=tmp_path,
        dry_run=True,
        wait_for_cycle=False,
    )
    main(["wcofs-daily", "--date", "2026-09-28", "--out", str(tmp_path), "--dry-run"])

    assert _provenance_tree_snapshot() == repo_provenance_snapshot
    assert plan.pull_log.is_file()
    assert plan.pull_log.is_relative_to(tmp_path)
