"""Contract tests: bot2 PR #11 (f71dca9) WCOFS Zarr/pull-log vs PR #5 prediction output."""

from __future__ import annotations

import datetime as dt
import math

import pytest

from fishai.ingestion.physics.sources import wcofs as wcofs_src
from fishai.models.wcofs_pr11_a469ebf_contract import (
    PR11_COMMIT,
    PR11_COMMIT_SHORT,
    PR11_UNKNOWN_PULL_REASONS,
    PR11_VALID_OFFSETS_H,
    PR11_ZARR_STEP_COORDS,
    assert_pr11_step_schema,
    assert_pr11_zarr_view,
    assert_pr5_independent_of_run_cycle_qc,
    assert_source_run_time_for_fallback_tier,
    build_pr11_scenario,
    compare_feature_branch_to_pr11,
    load_pr11_fixture,
    pr11_zarr_step_view,
    pr5_predict_engine_args_from_pr11_zarr_step,
    pr5_prediction_from_pr11_unknown_slot,
    pr5_prediction_from_pr11_zarr_step,
)


def test_fixture_documents_pr11_f71dca9_head() -> None:
    doc = load_pr11_fixture()
    assert doc["pr11_commit"] == PR11_COMMIT
    assert doc["pr11_commit_short"] == PR11_COMMIT_SHORT
    assert "f71dca9" in doc["pr11_commit"]
    assert doc["valid_offset_h_timeline"] == list(PR11_VALID_OFFSETS_H)


@pytest.mark.parametrize(
    "scenario_name",
    [
        "normal_primary_cycle",
        "r1_fallback_previous_cycle",
        "r2_fallback_offsets_beyond_24_unknown",
        "download_failed_absent_from_zarr",
        "valid_time_mismatch_absent_from_zarr",
    ],
)
def test_pr11_fixture_matches_live_builder(scenario_name: str) -> None:
    target = dt.date(2026, 9, 28)
    built = build_pr11_scenario(scenario_name, target)
    doc = next(s for s in load_pr11_fixture()["scenarios"] if s["name"] == scenario_name)
    assert doc["expected_pr5_predictions"] == built["expected_pr5_predictions"]


def test_source_run_time_on_normal_r_r24h_r48h() -> None:
    target = dt.date(2026, 9, 28)
    assert_source_run_time_for_fallback_tier(
        "normal_primary_cycle",
        target,
        expected_source=wcofs_src.cycle_run_time(target),
    )
    assert_source_run_time_for_fallback_tier(
        "r1_fallback_previous_cycle",
        target,
        expected_source=wcofs_src.cycle_run_time(target - dt.timedelta(days=1)),
    )
    assert_source_run_time_for_fallback_tier(
        "r2_fallback_offsets_beyond_24_unknown",
        target,
        expected_source=wcofs_src.cycle_run_time(target - dt.timedelta(days=2)),
    )


def test_r2_offsets_through_24_forecast_age_is_offset_plus_48() -> None:
    target = dt.date(2026, 9, 28)
    scenario = build_pr11_scenario("r2_fallback_offsets_beyond_24_unknown", target)
    for off in range(-21, 25, 3):
        step = next(s for s in scenario["zarr_steps"] if s["valid_offset_h"] == off)
        assert float(step["forecast_age_hours"]) == off + 48
        assert step["fallback_used"] is True
        pred = pr5_prediction_from_pr11_zarr_step(step)
        assert pred["evidence_state"] == "FORECAST"
        assert pred["lead_days"] == int(min(3, max(1, math.ceil((off + 48) / 24))))
        engine = pr5_predict_engine_args_from_pr11_zarr_step(step)
        assert engine["source_run_time"] == step["source_run_time"]
        assert engine["fallback_used"] is True
        assert engine["expected_evidence_state"] == pred["evidence_state"]


def test_r2_unknown_offsets_27_through_72() -> None:
    target = dt.date(2026, 9, 28)
    scenario = build_pr11_scenario("r2_fallback_offsets_beyond_24_unknown", target)
    reasons = {int(u["valid_offset_h"]): u["reason"] for u in scenario["pull_log_unknown"]}
    for off in range(27, 73, 3):
        assert off not in {s["valid_offset_h"] for s in scenario["zarr_steps"]}
        assert reasons[off] == "missing_operational_cycle"
        pred = scenario["expected_pr5_predictions"][str(off)]
        assert pred["evidence_state"] == "UNKNOWN"
        assert pred["unknown_reason"] == "missing_operational_cycle"


def test_valid_time_mismatch_maps_to_unknown_without_fill() -> None:
    target = dt.date(2026, 9, 28)
    scenario = build_pr11_scenario("valid_time_mismatch_absent_from_zarr", target)
    assert 3 in scenario["zarr_absent_offsets"]
    row = next(u for u in scenario["pull_log_unknown"] if u["valid_offset_h"] == 3)
    pred = pr5_prediction_from_pr11_unknown_slot(row)
    assert pred["evidence_state"] == "UNKNOWN"
    assert pred["unknown_reason"] == "valid_time_mismatch"
    assert pred["lead_days"] == 0


def test_pr11_step_and_zarr_schemas_require_source_run_time() -> None:
    target = dt.date(2026, 9, 28)
    step = build_pr11_scenario("normal_primary_cycle", target)["zarr_steps"][0]
    assert_pr11_step_schema(step)
    assert_pr11_zarr_view(step)
    bad = {k: v for k, v in step.items() if k != "source_run_time"}
    with pytest.raises(AssertionError, match="source_run_time"):
        assert_pr11_step_schema(bad)


def test_pr5_models_independent_of_run_cycle_qc_nan_fraction() -> None:
    assert_pr5_independent_of_run_cycle_qc()


def test_schema_mismatch_report_is_explicit_not_silent() -> None:
    doc = load_pr11_fixture()
    reported = doc["schema_mismatch_report"]
    live = [m.as_dict() for m in compare_feature_branch_to_pr11()]
    assert reported == live
    areas = {row["area"] for row in reported}
    assert "dtype_lead_days" in areas
    assert "zarr_field_names" in areas


def test_unknown_reasons_match_pr11_f71dca9_audit() -> None:
    assert PR11_UNKNOWN_PULL_REASONS == frozenset(
        {
            "missing_operational_cycle",
            "download_failed",
            "valid_time_mismatch",
        }
    )
    doc = load_pr11_fixture()
    reasons = set()
    for scenario in doc["scenarios"]:
        for row in scenario["pull_log_unknown"]:
            reasons.add(row["reason"])
    assert reasons <= PR11_UNKNOWN_PULL_REASONS
    assert "valid_time_mismatch" in reasons


def test_zarr_coord_set_matches_f71dca9() -> None:
    assert "source_run_time" in PR11_ZARR_STEP_COORDS
    assert PR11_ZARR_STEP_COORDS == frozenset(
        {
            "valid_offset_h",
            "time",
            "valid_time",
            "forecast_age_hours",
            "source_cycle_time",
            "source_run_time",
            "evidence_state_hint",
            "lead_days",
        }
    )
