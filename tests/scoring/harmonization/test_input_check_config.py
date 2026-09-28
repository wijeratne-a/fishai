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
from fishai.scoring.harmonization.constants import VERDICT_PASS
from fishai.scoring.harmonization.grading import combine_stratum_verdicts
from fishai.scoring.harmonization.input_check_config import (
    GRADING_STATUS_SHARED_FORCING,
    SCORER_GRADED_INPUT_VARIABLES,
    collect_graded_input_config_violations,
    variable_grading_status_map,
)

PREREG_PATH = (
    __import__("pathlib").Path(__file__).resolve().parents[3] / "prereg" / "harmonization_wcofs_glorys.yaml"
)


def _ready_doc() -> dict:
    doc = load_harmonization_prereg(PREREG_PATH)
    return yaml.safe_load(yaml.dump(doc))


def test_committed_prereg_five_graded_inputs_match_scorer() -> None:
    doc = load_harmonization_prereg(PREREG_PATH)
    assert collect_graded_input_config_violations(doc) == []
    status = variable_grading_status_map(doc)
    assert set(SCORER_GRADED_INPUT_VARIABLES) == {
        k for k, v in status.items() if v == "graded"
    }
    assert status["upwelling"] == GRADING_STATUS_SHARED_FORCING


def test_gate_refuses_graded_list_mismatch_with_scorer() -> None:
    doc = _ready_doc()
    variables = doc["harmonization_wcofs_glorys"]["variables"]
    doc["harmonization_wcofs_glorys"]["variables"] = [
        v for v in variables if not (isinstance(v, dict) and v.get("name") == "front_distance_km")
    ]
    assert "input_check_grading.graded_variables_mismatch_with_scorer" in collect_graded_input_config_violations(
        doc
    )
    with pytest.raises(HarmonizationPreregNotReadyError, match="graded_variables_mismatch"):
        assert_harmonization_prereg_ready_for_scoring(doc)


def test_gate_refuses_graded_variable_missing_from_variables_list() -> None:
    doc = _ready_doc()
    block = doc["harmonization_wcofs_glorys"]
    block["variables"] = [v for v in block["variables"] if not (isinstance(v, dict) and v.get("name") == "T3m")]
    assert "variables.variable_not_in_variables_list" in collect_graded_input_config_violations(doc)
    with pytest.raises(HarmonizationPreregNotReadyError):
        assert_harmonization_prereg_ready_for_scoring(doc)


def test_shared_forcing_variable_never_affects_stratum_verdict() -> None:
    buoy_pass = VERDICT_PASS
    graded_pass = [VERDICT_PASS] * len(SCORER_GRADED_INPUT_VARIABLES)
    combined, _ = combine_stratum_verdicts(
        buoy_pass,
        graded_pass,
        combination_rule="worst-of",
    )
    assert combined == VERDICT_PASS
    assert "FAIL" not in graded_pass
