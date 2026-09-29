"""Contract tests: bot2 PR #11 (a469ebf) WCOFS Zarr/pull-log vs PR #5 prediction output."""

from __future__ import annotations

import datetime as dt
import math

import pytest

from fishai.models.wcofs_pr11_a469ebf_contract import (
    PR11_COMMIT,
    PR11_FIXTURE_PATH,
    PR11_UNKNOWN_PULL_REASONS,
    PR11_VALID_OFFSETS_H,
    PR11_ZARR_STEP_COORDS,
    assert_pr11_step_schema,
    assert_pr11_zarr_view,
    build_pr11_scenario,
    compare_feature_branch_to_pr11_a469ebf,
    load_pr11_fixture,
    pr11_zarr_step_view,
    pr5_prediction_from_pr11_unknown_slot,
    pr5_prediction_from_pr11_zarr_step,
)


def test_fixture_documents_pr11_commit_and_timeline() -> None:
    doc = load_pr11_fixture()
    assert doc["pr11_commit"] == PR11_COMMIT
    assert doc["valid_offset_h_timeline"] == list(PR11_VALID_OFFSETS_H)
    assert "SYNTHETIC" in doc["note"]


@pytest.mark.parametrize(
    "scenario_name",
    [
        "normal_primary_cycle",
        "r1_fallback_previous_cycle",
        "r2_fallback_offsets_beyond_24_unknown",
        "download_failed_absent_from_zarr",
    ],
)
def test_pr11_fixture_matches_live_builder(scenario_name: str) -> None:
    target = dt.date(2026, 9, 28)
    built = build_pr11_scenario(scenario_name, target)
    doc = next(s for s in load_pr11_fixture()["scenarios"] if s["name"] == scenario_name)
    assert doc["expected_pr5_predictions"] == built["expected_pr5_predictions"]


def test_normal_run_nowcast_and_forecast_lead_days() -> None:
    target = dt.date(2026, 9, 28)
    scenario = build_pr11_scenario("normal_primary_cycle", target)
    by_off = {int(s["valid_offset_h"]): s for s in scenario["zarr_steps"]}
    assert pr5_prediction_from_pr11_zarr_step(by_off[-3]) == {
        "evidence_state": "NOWCAST_UNVALIDATED",
        "lead_days": 0,
        "unknown_reason": None,
    }
    assert pr5_prediction_from_pr11_zarr_step(by_off[0])["lead_days"] == 0
    assert pr5_prediction_from_pr11_zarr_step(by_off[3]) == {
        "evidence_state": "FORECAST",
        "lead_days": 1,
        "unknown_reason": None,
    }
    assert math.isnan(pr11_zarr_step_view(by_off[0])["lead_days"])


def test_r1_fallback_nowcast_offsets_use_prior_f_fields_and_forecast_lead_1() -> None:
    target = dt.date(2026, 9, 28)
    scenario = build_pr11_scenario("r1_fallback_previous_cycle", target)
    by_off = {int(s["valid_offset_h"]): s for s in scenario["zarr_steps"]}
    for off in (-21, -3, 0):
        step = by_off[off]
        assert step["fallback_used"] is True
        assert step["lead_tag"].startswith("f")
        age = float(step["forecast_age_hours"])
        assert 3.0 <= age <= 24.0
        pred = pr5_prediction_from_pr11_zarr_step(step)
        assert pred["evidence_state"] == "FORECAST"
        assert pred["lead_days"] == 1
    step3 = by_off[3]
    assert float(step3["forecast_age_hours"]) == 27.0
    assert pr5_prediction_from_pr11_zarr_step(step3)["lead_days"] == 2
    step24 = by_off[24]
    assert float(step24["forecast_age_hours"]) == 48.0
    assert pr5_prediction_from_pr11_zarr_step(step24)["lead_days"] == 2


def test_r2_fallback_marks_offsets_beyond_24_as_unknown() -> None:
    target = dt.date(2026, 9, 28)
    scenario = build_pr11_scenario("r2_fallback_offsets_beyond_24_unknown", target)
    assert scenario["zarr_absent_offsets"] == [27, 72]
    unknown_offs = {int(u["valid_offset_h"]) for u in scenario["pull_log_unknown"]}
    assert unknown_offs == {27, 72}
    for row in scenario["pull_log_unknown"]:
        assert row["reason"] == "missing_operational_cycle"
        pred = pr5_prediction_from_pr11_unknown_slot(row)
        assert pred["evidence_state"] == "UNKNOWN"
        assert pred["lead_days"] == 0
        assert pred["unknown_reason"] == "missing_operational_cycle"
    step24 = next(s for s in scenario["zarr_steps"] if s["valid_offset_h"] == 24)
    assert pr5_prediction_from_pr11_zarr_step(step24)["lead_days"] == 3


def test_download_failed_absent_from_zarr_is_unknown() -> None:
    target = dt.date(2026, 9, 28)
    scenario = build_pr11_scenario("download_failed_absent_from_zarr", target)
    assert 3 in scenario["zarr_absent_offsets"]
    failed = next(u for u in scenario["pull_log_unknown"] if u["valid_offset_h"] == 3)
    assert failed["reason"] == "download_failed"
    pred = pr5_prediction_from_pr11_unknown_slot(failed)
    assert pred == {
        "evidence_state": "UNKNOWN",
        "lead_days": 0,
        "unknown_reason": "download_failed",
    }


def test_pr11_step_and_zarr_schemas_reject_feature_extras() -> None:
    target = dt.date(2026, 9, 28)
    step = build_pr11_scenario("normal_primary_cycle", target)["zarr_steps"][0]
    assert_pr11_step_schema(step)
    assert_pr11_zarr_view(step)
    with pytest.raises(AssertionError, match="source_run_time"):
        assert_pr11_step_schema({**step, "source_run_time": step["source_cycle_time"]})


def test_schema_mismatch_report_is_explicit_not_silent() -> None:
    doc = load_pr11_fixture()
    reported = doc["schema_mismatch_report"]
    live = [m.as_dict() for m in compare_feature_branch_to_pr11_a469ebf()]
    assert reported == live
    assert len(reported) >= 1
    areas = {row["area"] for row in reported}
    assert "zarr_coords" in areas
    assert "step_provenance" in areas


def test_unknown_reasons_match_pr11_audit() -> None:
    doc = load_pr11_fixture()
    reasons = set()
    for scenario in doc["scenarios"]:
        for row in scenario["pull_log_unknown"]:
            reasons.add(row["reason"])
    assert reasons <= PR11_UNKNOWN_PULL_REASONS
    assert "missing_operational_cycle" in reasons
    assert "download_failed" in reasons


def test_zarr_coord_set_is_frozen_pr11_contract() -> None:
    assert PR11_ZARR_STEP_COORDS == frozenset(
        {
            "valid_offset_h",
            "time",
            "valid_time",
            "forecast_age_hours",
            "source_cycle_time",
            "evidence_state_hint",
            "lead_days",
        }
    )
