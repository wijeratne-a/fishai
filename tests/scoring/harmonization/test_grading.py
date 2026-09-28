"""Grading logic unit tests."""

from __future__ import annotations

import copy

from fishai.scoring.harmonization.grading import (
    BuoyGradeInput,
    combine_stratum_verdicts,
    grade_buoy_stratum,
    grade_input_check,
    InputCheckGradeInput,
    normalize_combination_rule,
)
from fishai.scoring.harmonization.constants import (
    BUOY_INSUFFICIENT_OBS_REASON,
    FAIL_EVIDENCE_REASON,
    VERDICT_DEGRADED,
    VERDICT_FAIL,
    VERDICT_NOT_GRADABLE,
    VERDICT_PASS,
    VERDICT_UNKNOWN,
)

CUTOFFS = {
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


def _buoy(**kwargs) -> BuoyGradeInput:
    base = {
        "n": 120,
        "n_buoys": 4,
        "bias_c": 0.1,
        "rmse_mapped": 1.0,
        "rmse_glorys": 1.0,
        "rmse_ratio_ci_upper": 1.1,
        "pearson_r_mapped": 0.9,
        "pearson_r_glorys": 0.85,
        "independent_source": True,
    }
    base.update(kwargs)
    return BuoyGradeInput(**base)


def test_grade_pass_degraded_fail() -> None:
    assert grade_buoy_stratum(_buoy(), CUTOFFS)[0] == VERDICT_PASS
    assert (
        grade_buoy_stratum(_buoy(rmse_mapped=1.3, rmse_ratio_ci_upper=1.4), CUTOFFS)[0]
        == VERDICT_DEGRADED
    )
    assert (
        grade_buoy_stratum(_buoy(rmse_mapped=2.0, rmse_ratio_ci_upper=2.0), CUTOFFS)[0]
        == VERDICT_FAIL
    )


def test_insufficient_observations_caps_degraded_never_pass() -> None:
    verdict, reason = grade_buoy_stratum(_buoy(n=10), CUTOFFS)
    assert verdict == VERDICT_DEGRADED
    assert reason == BUOY_INSUFFICIENT_OBS_REASON
    assert verdict != VERDICT_PASS


def test_assimilated_source_not_gradable() -> None:
    assert grade_buoy_stratum(_buoy(independent_source=False), CUTOFFS)[0] == VERDICT_NOT_GRADABLE


def test_registry_independence_requires_auditor_acceptance() -> None:
    from fishai.scoring.harmonization.registry import wcofs_independent_observation_source

    pending = {
        "sources": {
            "ndbc_buoy_temperature": {
                "wcofs": {
                    "status": "false",
                    "citation": {
                        "title": "t",
                        "url": "https://example.com",
                        "page_section": "p",
                        "quote": "q",
                    },
                    "accepted_by_auditor": False,
                }
            }
        }
    }
    assert wcofs_independent_observation_source("ndbc_buoy_temperature", pending) is False
    accepted = copy.deepcopy(pending)
    accepted["sources"]["ndbc_buoy_temperature"]["wcofs"]["accepted_by_auditor"] = True
    assert wcofs_independent_observation_source("ndbc_buoy_temperature", accepted) is True


def test_input_check_thresholds() -> None:
    assert (
        grade_input_check(InputCheckGradeInput(rmse=0.4, glorys_spatial_sd=1.0), CUTOFFS)
        == VERDICT_PASS
    )
    assert (
        grade_input_check(InputCheckGradeInput(rmse=0.8, glorys_spatial_sd=1.0), CUTOFFS)
        == VERDICT_DEGRADED
    )
    assert (
        grade_input_check(InputCheckGradeInput(rmse=1.5, glorys_spatial_sd=1.0), CUTOFFS)
        == VERDICT_FAIL
    )


def test_worst_of_combination_and_failed_input_unknown() -> None:
    assert normalize_combination_rule("worst-of") == "worst_of"
    verdict, reason = combine_stratum_verdicts(
        VERDICT_PASS,
        [VERDICT_DEGRADED, VERDICT_PASS],
        combination_rule="worst_of",
    )
    assert verdict == VERDICT_DEGRADED
    assert reason is None

    verdict, reason = combine_stratum_verdicts(
        VERDICT_PASS,
        [VERDICT_FAIL],
        combination_rule="worst-of",
    )
    assert verdict == VERDICT_UNKNOWN
    assert reason == FAIL_EVIDENCE_REASON

    assert (
        combine_stratum_verdicts(
            VERDICT_FAIL,
            [VERDICT_PASS],
            combination_rule="worst_of",
        )[0]
        == VERDICT_FAIL
    )
