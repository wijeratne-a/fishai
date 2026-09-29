"""Tests for pass_fail_thresholds stratum verdict combination (worst_of)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from fishai.evaluation.harmonization_prereg import (
    HarmonizationPreregNotReadyError,
    assert_graded_inputs_declared_in_variables,
    assert_harmonization_prereg_ready_for_scoring,
    assert_pass_fail_thresholds_ready_for_scoring,
    combination_rule_blocks_scoring,
    load_harmonization_prereg,
    pass_fail_graded_input_names,
    pass_fail_thresholds_cutoffs,
    run_harmonization_scoring,
)
from fishai.evaluation.nowcast_forcing_stratum import (
    NO_INDEPENDENT_OBS_CHECK,
    NO_INDEPENDENT_VALIDATION,
    StratumCombinationInput,
    combine_stratum_verdict,
    stratum_combination_rules_from_prereg,
)

REPO = Path(__file__).resolve().parents[2]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"


def _all_pass_inputs(rules) -> dict[str, str]:
    return {name: "PASS" for name in rules.graded_inputs}


def test_cutoffs_combination_rule_worst_of_and_five_graded_inputs() -> None:
    doc = load_harmonization_prereg(PREREG)
    cutoffs = pass_fail_thresholds_cutoffs(doc)
    assert cutoffs["combination_rule"] == "worst_of"
    assert not combination_rule_blocks_scoring(cutoffs)
    assert cutoffs["verdict_rank_worst_first"] == ["UNKNOWN", "FAIL", "DEGRADED", "PASS"]
    assert cutoffs["graded_inputs"] == [
        "T3m",
        "S3m",
        "MLD_m",
        "sst_grad",
        "front_distance_km",
    ]
    assert len(cutoffs["graded_inputs"]) == 5
    assert cutoffs["not_gradable_cap"]["verdict"] == "DEGRADED"
    assert cutoffs["not_gradable_cap"]["reason"] == NO_INDEPENDENT_OBS_CHECK
    niv = cutoffs["no_independent_validation"]
    assert niv["all_strata_verdict"] == "UNKNOWN"
    assert niv["reason"] == NO_INDEPENDENT_VALIDATION
    assert niv["unknown_assimilation_status"] == "not_independent"
    assert_pass_fail_thresholds_ready_for_scoring(doc) is None


def test_every_graded_input_appears_in_variables() -> None:
    doc = load_harmonization_prereg(PREREG)
    names = pass_fail_graded_input_names(doc)
    assert len(names) == 5
    assert_graded_inputs_declared_in_variables(doc)
    vars_by_name = {v["name"]: v for v in doc["harmonization_wcofs_glorys"]["variables"]}
    assert "upwelling" not in names
    assert vars_by_name["upwelling"]["grading"] == "shared_forcing"
    assert vars_by_name["upwelling"]["role"] == "report_only"
    assert "same outside wind product" in vars_by_name["upwelling"]["note"]
    assert vars_by_name["u_surf"]["role"] == "report_only"
    assert vars_by_name["v_surf"]["role"] == "report_only"


def test_shared_forcing_and_report_only_variables_never_graded() -> None:
    doc = load_harmonization_prereg(PREREG)
    graded = set(pass_fail_graded_input_names(doc))
    for entry in doc["harmonization_wcofs_glorys"]["variables"]:
        name = entry["name"]
        if entry.get("grading") == "shared_forcing" or entry.get("role") == "report_only":
            assert name not in graded


def test_scoring_entry_point_passes_prereg_gate_on_committed_doc() -> None:
    doc = load_harmonization_prereg(PREREG)
    assert_harmonization_prereg_ready_for_scoring(doc)
    result = run_harmonization_scoring(PREREG, dry_run=True)
    assert result["status"] == "ready"


def test_worst_of_buoy_and_inputs_gradable_all_pass() -> None:
    rules = stratum_combination_rules_from_prereg()
    result = combine_stratum_verdict(
        StratumCombinationInput(
            has_independent_graded_variable=True,
            buoy_gradable=True,
            buoy_verdict="PASS",
            input_verdicts=_all_pass_inputs(rules),
        ),
        rules=rules,
    )
    assert result.verdict == "PASS"
    assert result.reason is None


def test_failed_input_forces_stratum_unknown() -> None:
    rules = stratum_combination_rules_from_prereg()
    inputs = _all_pass_inputs(rules)
    inputs["MLD_m"] = "UNKNOWN"
    result = combine_stratum_verdict(
        StratumCombinationInput(
            has_independent_graded_variable=True,
            buoy_gradable=True,
            buoy_verdict="PASS",
            input_verdicts=inputs,
        ),
        rules=rules,
    )
    assert result.verdict == "UNKNOWN"

    inputs2 = _all_pass_inputs(rules)
    inputs2["sst_grad"] = "FAIL"
    result2 = combine_stratum_verdict(
        StratumCombinationInput(
            has_independent_graded_variable=True,
            buoy_gradable=True,
            buoy_verdict="PASS",
            input_verdicts=inputs2,
        ),
        rules=rules,
    )
    assert result2.verdict == "UNKNOWN"


def test_worst_of_degraded_input_with_gradable_buoy_pass() -> None:
    rules = stratum_combination_rules_from_prereg()
    inputs = _all_pass_inputs(rules)
    inputs["T3m"] = "DEGRADED"
    result = combine_stratum_verdict(
        StratumCombinationInput(
            has_independent_graded_variable=True,
            buoy_gradable=True,
            buoy_verdict="PASS",
            input_verdicts=inputs,
        ),
        rules=rules,
    )
    assert result.verdict == "DEGRADED"


def test_no_independent_validation_all_strata_unknown() -> None:
    rules = stratum_combination_rules_from_prereg()
    result = combine_stratum_verdict(
        StratumCombinationInput(
            has_independent_graded_variable=False,
            buoy_gradable=True,
            buoy_verdict="PASS",
            input_verdicts=_all_pass_inputs(rules),
        ),
        rules=rules,
    )
    assert result.verdict == "UNKNOWN"
    assert result.reason == NO_INDEPENDENT_VALIDATION


def test_not_gradable_buoy_all_inputs_pass_yields_degraded_cap() -> None:
    rules = stratum_combination_rules_from_prereg()
    result = combine_stratum_verdict(
        StratumCombinationInput(
            has_independent_graded_variable=True,
            buoy_gradable=False,
            buoy_verdict=None,
            input_verdicts=_all_pass_inputs(rules),
        ),
        rules=rules,
    )
    assert result.verdict == "DEGRADED"
    assert result.reason == NO_INDEPENDENT_OBS_CHECK


def test_pending_combination_rule_still_blocks_scoring(tmp_path: Path) -> None:
    doc = yaml.safe_load(yaml.dump(load_harmonization_prereg(PREREG)))
    doc["harmonization_wcofs_glorys"]["pass_fail_thresholds"]["cutoffs"][
        "combination_rule"
    ] = "PENDING_AUDITOR_CONFIRMATION: proposed worst_of"
    path = tmp_path / "prereg.yaml"
    path.write_text(yaml.dump(doc), encoding="utf-8")
    loaded = load_harmonization_prereg(path)
    with pytest.raises(HarmonizationPreregNotReadyError, match="combination_rule"):
        assert_pass_fail_thresholds_ready_for_scoring(loaded)
