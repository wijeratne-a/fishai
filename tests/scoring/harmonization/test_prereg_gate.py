"""Pre-registration hard gate tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from fishai.evaluation.harmonization_prereg import (
    HarmonizationPreregNotReadyError,
    assert_harmonization_prereg_ready_for_scoring,
    load_harmonization_prereg,
)
from fishai.scoring.harmonization.prereg_gate import collect_prereg_gate_violations

REPO = Path(__file__).resolve().parents[3]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"


def _ready_block() -> dict:
    doc = load_harmonization_prereg(PREREG)
    block = yaml.safe_load(yaml.dump(doc))["harmonization_wcofs_glorys"]
    block["nearshore"]["shoreline_sha256"] = "deadbeef"
    block["nearshore"]["shoreline_simplification_check"] = {
        "max_coastline_displacement_m": 0.0,
        "nearshore_flag_diff_cell_count": 0,
    }
    block["pass_fail_thresholds"]["cutoffs"] = {
        "rmse_ratio_pass": 1.2,
        "rmse_ratio_ci_upper_pass": 1.5,
        "rmse_ratio_degraded_upper": 1.5,
        "bias_abs_pass_c": 0.5,
        "bias_abs_degraded_c": 1.0,
        "pearson_r_margin_below_glorys": 0.10,
        "min_matched_daily_values": 100,
        "min_buoys": 3,
        "input_rmse_pass_fraction_glorys_sd": 0.5,
        "input_rmse_degraded_fraction_glorys_sd": 1.0,
        "bootstrap_seed": 42,
        "glider_rmse_ratio_pass": 1.2,
        "glider_rmse_ratio_ci_upper_pass": 1.5,
        "glider_rmse_ratio_degraded_upper": 1.5,
        "glider_bias_abs_pass_c_T3m_10m": 0.5,
        "glider_bias_abs_pass_c_S3m_10m": 0.1,
        "glider_bias_abs_pass_c_MLD_m": 10.0,
    }
    block["pass_fail_thresholds"]["combination_rule"] = "worst-of"
    if "variable_grading_status" not in block.get("input_check_grading", {}):
        block["input_check_grading"] = {
            "variable_grading_status": {
                "T3m": "graded",
                "S3m": "graded",
                "MLD_m": "graded",
                "sst_grad": "graded",
                "front_distance_km": "graded",
                "upwelling": "shared_forcing",
                "u_surf": "shared_forcing",
                "v_surf": "shared_forcing",
            }
        }
    return block


@pytest.mark.parametrize(
    "field_path,mutator",
    [
        ("temporal_split.fit_end", lambda b: b["temporal_split"].update({"fit_end": ""})),
        ("temporal_split.test_start", lambda b: b["temporal_split"].update({"test_start": None})),
        ("nearshore.shoreline_source", lambda b: b["nearshore"].update({"shoreline_source": "TBD"})),
        ("nearshore.shoreline_sha256", lambda b: b["nearshore"].update({"shoreline_sha256": ""})),
        (
            "nearshore.shoreline_simplification_check",
            lambda b: b["nearshore"].update({"shoreline_simplification_check": "TO_BE_SET_BEFORE_SCORING"}),
        ),
        ("nearshore.cutoff_km", lambda b: b["nearshore"].update({"cutoff_km": None})),
        (
            "pass_fail_thresholds.cutoffs.rmse_ratio_pass",
            lambda b: b["pass_fail_thresholds"]["cutoffs"].update({"rmse_ratio_pass": "TBD"}),
        ),
    ],
)
def test_gate_refuses_on_blank_field(field_path: str, mutator) -> None:
    block = _ready_block()
    mutator(block)
    doc = {"harmonization_wcofs_glorys": block}
    violations = collect_prereg_gate_violations(doc)
    assert any(field_path.split(".")[-1] in v or field_path in v for v in violations)
    with pytest.raises(HarmonizationPreregNotReadyError):
        assert_harmonization_prereg_ready_for_scoring(doc)


def test_gate_refuses_on_pending_combination_rule() -> None:
    block = _ready_block()
    block["pass_fail_thresholds"]["combination_rule"] = "PENDING auditbot1 confirmation"
    doc = {"harmonization_wcofs_glorys": block}
    assert "pass_fail_thresholds.combination_rule" in collect_prereg_gate_violations(doc)
