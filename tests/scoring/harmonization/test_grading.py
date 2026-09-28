"""Grading logic unit tests."""

from __future__ import annotations

from fishai.scoring.harmonization.grading import (
    BuoyGradeInput,
    combine_stratum_verdicts,
    grade_buoy_stratum,
    grade_input_check,
    InputCheckGradeInput,
)
from fishai.scoring.harmonization.constants import (
    VERDICT_DEGRADED,
    VERDICT_FAIL,
    VERDICT_NOT_GRADABLE,
    VERDICT_PASS,
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


def test_grade_pass_degraded_fail_not_gradable() -> None:
    assert grade_buoy_stratum(_buoy(), CUTOFFS)[0] == VERDICT_PASS
    assert (
        grade_buoy_stratum(_buoy(rmse_mapped=1.3, rmse_ratio_ci_upper=1.4), CUTOFFS)[0]
        == VERDICT_DEGRADED
    )
    assert (
        grade_buoy_stratum(_buoy(rmse_mapped=2.0, rmse_ratio_ci_upper=2.0), CUTOFFS)[0]
        == VERDICT_FAIL
    )
    assert grade_buoy_stratum(_buoy(n=10), CUTOFFS)[0] == VERDICT_NOT_GRADABLE


def test_assimilated_source_not_gradable() -> None:
    assert grade_buoy_stratum(_buoy(independent_source=False), CUTOFFS)[0] == VERDICT_NOT_GRADABLE


def test_registry_independence_controls_gradability() -> None:
    from fishai.scoring.harmonization.registry import wcofs_independent_observation_source

    assimilated = {"sources": {"ndbc_buoy_temperature": {"wcofs": "unknown"}}}
    assert wcofs_independent_observation_source("ndbc_buoy_temperature", assimilated) is False
    independent = {"sources": {"ndbc_buoy_temperature": {"wcofs": "false"}}}
    assert wcofs_independent_observation_source("ndbc_buoy_temperature", independent) is True


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


def test_worst_of_combination() -> None:
    assert (
        combine_stratum_verdicts(
            VERDICT_PASS,
            [VERDICT_DEGRADED, VERDICT_PASS],
            combination_rule="worst_of",
            not_gradable_combination="ignore",
        )
        == VERDICT_DEGRADED
    )
