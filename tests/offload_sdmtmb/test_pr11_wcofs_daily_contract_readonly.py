"""Read-only contract tests for PR #11 (f71dca9) WCOFS daily walk-back semantics."""

from __future__ import annotations

import datetime as dt
import importlib
import json
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[2]
PHYSICS_TESTS = REPO / "tests" / "ingestion" / "physics"


def _three_hour_offsets(start_h: int, end_h: int) -> set[int]:
    return set(range(start_h, end_h + 1, 3))


def _load_pr11_wcofs_stack() -> tuple[Any, Any, str | None]:
    try:
        wcofs_daily = importlib.import_module("fishai.ingestion.physics.wcofs_daily")
        wcofs_src = importlib.import_module("fishai.ingestion.physics.sources.wcofs")
    except ImportError as exc:
        return None, None, f"PR #11 wcofs_daily not importable: {exc}"
    if not hasattr(wcofs_src, "TARGET_VALID_OFFSETS_H"):
        return None, None, "wcofs_src missing PR #11 TARGET_VALID_OFFSETS_H API"
    return wcofs_daily, wcofs_src, None


@pytest.fixture(scope="module")
def pr11_stack() -> tuple[Any, Any]:
    wcofs_daily, wcofs_src, reason = _load_pr11_wcofs_stack()
    if wcofs_daily is None:
        pytest.skip(reason or "PR #11 stack unavailable")
    return wcofs_daily, wcofs_src


def test_sdmtmb_core_tree_does_not_reference_run_cycle_qc() -> None:
    roots = (
        REPO / "src" / "models",
        REPO / "python",
        REPO / "tests" / "models",
    )
    hits: list[str] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".R", ".yaml", ".yml", ".md"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if "run_cycle_qc" in text:
                hits.append(str(path.relative_to(REPO)))
    assert hits == []


def test_source_run_time_matches_cycle_run_time(pr11_stack: tuple[Any, Any]) -> None:
    wcofs_daily, wcofs_src = pr11_stack
    target = dt.date(2026, 9, 28)
    r = wcofs_src.cycle_run_time(target)
    assert wcofs_daily.source_run_time_for_cycle(target) == r
    assert wcofs_daily.requested_cycle_time(target) == r
    plan = wcofs_daily.build_lead_plan(
        target, primary_available=True, cycle_exists_fn=lambda _d: True
    )
    for lp in plan.leads:
        assert wcofs_src.cycle_run_time(lp.cycle_date).isoformat() == r.isoformat()


def test_walkback_r_minus_one_missing_offsets_and_unknown_tail(pr11_stack: tuple[Any, Any]) -> None:
    wcofs_daily, wcofs_src = pr11_stack
    target = dt.date(2026, 9, 28)
    source_day = dt.date(2026, 9, 26)

    def exists(d: dt.date) -> bool:
        return d == source_day

    plan = wcofs_daily.build_lead_plan(
        target,
        primary_available=False,
        max_missed_cycles=2,
        cycle_exists_fn=exists,
    )
    covered = {lp.valid_offset_h for lp in plan.leads}
    assert covered == _three_hour_offsets(-21, 24)
    unknown = {
        u["valid_offset_h"]
        for u in plan.unknown_slots
        if u["reason"] == "missing_operational_cycle"
    }
    assert unknown == _three_hour_offsets(27, 72)
    for lp in plan.leads:
        assert lp.cycle_date == source_day
        assert lp.fallback == "previous_cycle"


def test_valid_time_mismatch_unknown_no_fill(tmp_path: Path, pr11_stack: tuple[Any, Any]) -> None:
    wcofs_daily, wcofs_src = pr11_stack
    fixture_path = PHYSICS_TESTS / "wcofs_fixtures.py"
    if not fixture_path.is_file():
        pytest.skip("wcofs_fixtures from PR #11 not present")
    import importlib.util

    spec = importlib.util.spec_from_file_location("wcofs_fixtures_offload", fixture_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    write_mini_wcofs_bytes = mod.write_mini_wcofs_bytes

    target = dt.date(2026, 9, 28)
    plan = wcofs_daily.build_lead_plan(target, primary_available=True, cycle_exists_fn=lambda _d: True)
    good = next(lp for lp in plan.leads if lp.valid_offset_h == -21)
    bad = next(lp for lp in plan.leads if lp.valid_offset_h == 3)
    plan.leads = [good, bad]
    plan.s3_keys = [wcofs_src.fields_s3_key(lp.cycle_date, lp.lead_tag) for lp in plan.leads]
    log_path = tmp_path / "pull.jsonl"
    plan.pull_log = log_path
    good_bytes = write_mini_wcofs_bytes(cycle_date=target, lead_tag=good.lead_tag)
    bad_bytes = write_mini_wcofs_bytes(
        cycle_date=target, lead_tag=bad.lead_tag, valid_time_shift_h=3
    )

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        return bad_bytes if bad.lead_tag in url else good_bytes

    def fake_head(url: str) -> dict[str, Any]:  # noqa: ARG001
        return {"status": 200, "etag": "x", "size_bytes": 10}

    slices, failed = wcofs_daily.fetch_and_log_leads(
        plan,
        get_fn=fake_get,
        head_meta_fn=fake_head,
        log_path=log_path,
        skip_if_etag_matches=False,
    )
    assert len(slices) == 1
    assert len(failed) == 1
    assert failed[0]["reason"] == "valid_time_mismatch"
    assert failed[0]["state"] == "UNKNOWN"
    merged = wcofs_daily.assemble_merged_dataset(plan, slices)
    packaged = importlib.import_module("fishai.ingestion.physics.wcofs_store").package_wcofs_cycle(
        merged, target
    )
    assert -21 in packaged.valid_offset_h.values
    assert 3 not in packaged.valid_offset_h.values
    err_line = json.loads(log_path.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert err_line["status"] == "error"
    assert err_line["reason"] == "valid_time_mismatch"
