"""Spray glider holdout grading and gate tests."""

from __future__ import annotations

import pandas as pd
import pytest

from fishai.scoring.harmonization.glider_grading import (
    collect_glider_cutoff_gate_violations,
    grade_glider_stratum,
)
from fishai.scoring.harmonization.glider_observations import spray_profile_observation_rows
from fishai.scoring.harmonization.registry import load_assimilated_sources_registry
from fishai.ingestion.sensors.spray_glider import load_spray_glider_profiles
from fishai.scoring.harmonization.constants import VERDICT_NOT_GRADABLE, VERDICT_PASS


def test_gate_refuses_missing_glider_cutoff_keys() -> None:
    violations = collect_glider_cutoff_gate_violations({"rmse_ratio_pass": 1.2})
    assert violations
    assert "missing_glider_keys" in violations[0]


def _synthetic_glider_match(n_profiles: int = 120) -> pd.DataFrame:
    rows = []
    for i in range(n_profiles):
        mission = f"m{i % 4}"
        obs_t = 15.0 + 0.01 * i
        for var, obs, mapped in (
            ("T3m", obs_t, obs_t + 0.02),
            ("S3m", 33.0 + 0.001 * i, 33.0 + 0.001 * i + 0.01),
            ("MLD_m", 25.0 + 0.01 * i, 25.0 + 0.01 * i + 0.02),
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
                    "glorys_value": obs + 0.05,
                }
            )
    return pd.DataFrame(rows)


def test_glider_grades_mapped_only_not_glorys_ratio() -> None:
    reg = load_assimilated_sources_registry()
    cutoffs = {
        "glider_bias_abs_pass_c": 0.5,
        "glider_rmse_pass_c": 0.6,
        "glider_rmse_degraded_c": 1.0,
        "glider_pearson_r_min": 0.0,
    }
    grade = grade_glider_stratum(
        _synthetic_glider_match(),
        stratum="pooled",
        cutoffs=cutoffs,
        block_days=7,
        seed=1,
        registry=reg,
        min_profiles=100,
        min_missions=3,
    )
    assert grade.verdict == VERDICT_PASS
    assert grade.metrics[0]["model_row"] == "wcofs_coarsened_mapped"
    assert grade.metrics[0]["glorys_report"]["label"] == "not_independent_reported_only"


def test_spray_fixture_profile_metrics_and_mld_exclude() -> None:
    profiles = load_spray_glider_profiles()
    obs = spray_profile_observation_rows(profiles)
    assert not obs.empty
    assert obs["mld_exclude_reason"].notna().sum() >= 0


def test_insufficient_profiles_not_gradable() -> None:
    reg = load_assimilated_sources_registry()
    cutoffs = {
        "glider_bias_abs_pass_c": 0.5,
        "glider_rmse_pass_c": 0.6,
        "glider_rmse_degraded_c": 1.0,
        "glider_pearson_r_min": 0.5,
    }
    grade = grade_glider_stratum(
        _synthetic_glider_match(n_profiles=10),
        stratum="pooled",
        cutoffs=cutoffs,
        block_days=7,
        seed=1,
        registry=reg,
        min_profiles=100,
        min_missions=3,
    )
    assert grade.verdict == VERDICT_NOT_GRADABLE
