"""Graded input list gate vs prereg and scorer."""

from __future__ import annotations

import copy

import pytest
import yaml

from fishai.evaluation.harmonization_prereg import (
    HarmonizationPreregNotReadyError,
    assert_harmonization_prereg_ready_for_scoring,
    load_harmonization_prereg,
)
from fishai.scoring.harmonization.input_check_config import collect_graded_input_config_violations
from fishai.scoring.harmonization.prereg_gate import collect_prereg_gate_violations

REPO = __file__.replace("tests/scoring/harmonization/test_input_check_config.py", "")
PREREG_PATH = (
    __import__("pathlib").Path(__file__).resolve().parents[3] / "prereg" / "harmonization_wcofs_glorys.yaml"
)


def _ready_doc() -> dict:
    doc = load_harmonization_prereg(PREREG_PATH)
    block = yaml.safe_load(yaml.dump(doc))["harmonization_wcofs_glorys"]
    block["nearshore"]["shoreline_sha256"] = "abc"
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
    }
    block["pass_fail_thresholds"]["combination_rule"] = "worst-of"
    return {"schema_version": 1, "harmonization_wcofs_glorys": block}


def test_committed_prereg_graded_inputs_match_scorer() -> None:
    doc = load_harmonization_prereg(PREREG_PATH)
    assert collect_graded_input_config_violations(doc) == []


def test_gate_refuses_graded_list_mismatch_with_scorer() -> None:
    doc = _ready_doc()
    doc["harmonization_wcofs_glorys"]["input_check_grading"]["graded_variables"] = [
        "T3m",
        "S3m",
        "MLD_m",
    ]
    assert "input_check_grading.graded_variables_mismatch_with_scorer" in collect_graded_input_config_violations(
        doc
    )
    with pytest.raises(HarmonizationPreregNotReadyError, match="graded_variables_mismatch"):
        assert_harmonization_prereg_ready_for_scoring(doc)


def test_gate_refuses_graded_variable_missing_from_variables_list() -> None:
    doc = _ready_doc()
    block = doc["harmonization_wcofs_glorys"]
    block["variables"] = [v for v in block["variables"] if v != "upwelling"]
    assert "input_check_grading.graded_variables_not_in_variables_list" in collect_graded_input_config_violations(
        doc
    )
    with pytest.raises(HarmonizationPreregNotReadyError, match="not_in_variables_list"):
        assert_harmonization_prereg_ready_for_scoring(doc)
