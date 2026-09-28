"""Spray glider holdout grading and gate tests."""

from __future__ import annotations

import numpy as np
import pandas as pd

from fishai.ingestion.sensors.spray_glider import load_spray_glider_profiles
from fishai.scoring.harmonization.constants import (
    VERDICT_DEGRADED,
    VERDICT_FAIL,
    VERDICT_NOT_GRADABLE,
    VERDICT_PASS,
)
from fishai.scoring.harmonization.glider_grading import (
    collect_glider_cutoff_gate_violations,
    glider_bias_verdict,
    grade_glider_stratum,
    grade_glider_variable,
)
from fishai.scoring.harmonization.glider_observations import spray_profile_observation_rows
from fishai.scoring.harmonization.grading import rmse_ratio_verdict
from fishai.scoring.harmonization.registry import load_assimilated_sources_registry

DEFAULT_GLIDER_CUTOFFS = {
    "glider_rmse_ratio_pass": 1.2,
    "glider_rmse_ratio_ci_upper_pass": 1.5,
    "glider_rmse_ratio_degraded_upper": 1.5,
    "glider_bias_abs_pass_c_T3m_10m": 0.5,
    "glider_bias_abs_pass_c_S3m_10m": 0.1,
    "glider_bias_abs_pass_c_MLD_m": 10.0,
    "pearson_r_margin_below_glorys": 0.10,
}


def test_gate_refuses_missing_glider_cutoff_keys() -> None:
    violations = collect_glider_cutoff_gate_violations({"rmse_ratio_pass": 1.2})
    assert violations
    assert "missing_glider_keys" in violations[0]
    assert "glider_rmse_ratio_pass" in violations[0]


def test_glider_rmse_ratio_boundaries() -> None:
    c = DEFAULT_GLIDER_CUTOFFS
    assert rmse_ratio_verdict(1.1, 1.4, c, prefix="glider_") == VERDICT_PASS
    assert rmse_ratio_verdict(1.25, 1.4, c, prefix="glider_") == VERDICT_DEGRADED
    assert rmse_ratio_verdict(1.6, 1.4, c, prefix="glider_") == VERDICT_FAIL
    assert rmse_ratio_verdict(1.1, 1.6, c, prefix="glider_") == VERDICT_DEGRADED


def test_glider_bias_boundaries_t_s_mld() -> None:
    assert glider_bias_verdict(0.5, 0.5) == VERDICT_PASS
    assert glider_bias_verdict(0.75, 0.5) == VERDICT_DEGRADED
    assert glider_bias_verdict(1.1, 0.5) == VERDICT_FAIL

    assert glider_bias_verdict(0.1, 0.1) == VERDICT_PASS
    assert glider_bias_verdict(0.15, 0.1) == VERDICT_DEGRADED
    assert glider_bias_verdict(0.25, 0.1) == VERDICT_FAIL

    assert glider_bias_verdict(10.0, 10.0) == VERDICT_PASS
    assert glider_bias_verdict(15.0, 10.0) == VERDICT_DEGRADED
    assert glider_bias_verdict(25.0, 10.0) == VERDICT_FAIL


def _series(n: int, mapped_delta: float, glorys_delta: float, bias: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    obs = np.linspace(10.0, 12.0, n)
    mapped = obs + bias + mapped_delta
    glorys = obs + glorys_delta
    dates = pd.date_range("2025-10-01", periods=n, freq="D").values.astype("datetime64[D]")
    return obs, mapped, glorys, dates


def test_glider_pearson_r_margin_same_as_buoy() -> None:
    n = 40
    obs, mapped, glorys, dates = _series(n, 0.001, 0.0011, 0.0)
    verdict, _ = grade_glider_variable(
        obs, mapped, glorys, dates, DEFAULT_GLIDER_CUTOFFS, variable="T3m", block_days=7, seed=3
    )
    assert verdict == VERDICT_PASS


def _synthetic_glider_match(n_profiles: int = 120) -> pd.DataFrame:
    rows = []
    for i in range(n_profiles):
        mission = f"m{i % 4}"
        obs_t = 15.0 + 0.01 * i
        for var, obs, mapped, glorys in (
            ("T3m", obs_t, obs_t + 0.001, obs_t + 0.0011),
            ("S3m", 33.0 + 0.001 * i, 33.0 + 0.001 * i + 0.001, 33.0 + 0.001 * i + 0.0011),
            ("MLD_m", 25.0 + 0.01 * i, 25.0 + 0.01 * i + 0.001, 25.0 + 0.01 * i + 0.0011),
        ):
            rows.append(
                {
                    "stratum": "pooled",
                    "profile_id": f"prof_{i}",
                    "mission": mission,
                    "date": "2025-10-01",
                    "variable": var,
                    "obs_value": obs,
                    "mapped_value": mapped,
                    "glorys_value": glorys,
                    "mld_reached": True,
                }
            )
    return pd.DataFrame(rows)


def test_glider_grades_mapped_with_glorys_ratio() -> None:
    reg = load_assimilated_sources_registry()
    grade = grade_glider_stratum(
        _synthetic_glider_match(),
        stratum="pooled",
        cutoffs=DEFAULT_GLIDER_CUTOFFS,
        block_days=7,
        seed=1,
        registry=reg,
        min_profiles=100,
        min_missions=3,
    )
    assert grade.verdict == VERDICT_PASS
    assert grade.metrics[0]["model_row"] == "wcofs_coarsened_mapped"
    assert "rmse_ratio_mapped_over_glorys" in grade.metrics[0]


def test_mld_not_reached_excluded_from_mld_grading() -> None:
    reg = load_assimilated_sources_registry()
    df = _synthetic_glider_match(n_profiles=120)
    df.loc[df["variable"] == "MLD_m", "mld_reached"] = False
    grade = grade_glider_stratum(
        df,
        stratum="pooled",
        cutoffs=DEFAULT_GLIDER_CUTOFFS,
        block_days=7,
        seed=1,
        registry=reg,
        min_profiles=100,
        min_missions=3,
    )
    assert all(m["variable"] != "MLD_m" for m in grade.metrics)


def test_spray_fixture_profile_metrics() -> None:
    profiles = load_spray_glider_profiles()
    obs = spray_profile_observation_rows(profiles)
    assert not obs.empty


def test_insufficient_profiles_not_gradable() -> None:
    reg = load_assimilated_sources_registry()
    grade = grade_glider_stratum(
        _synthetic_glider_match(n_profiles=10),
        stratum="pooled",
        cutoffs=DEFAULT_GLIDER_CUTOFFS,
        block_days=7,
        seed=1,
        registry=reg,
        min_profiles=100,
        min_missions=3,
    )
    assert grade.verdict == VERDICT_NOT_GRADABLE
