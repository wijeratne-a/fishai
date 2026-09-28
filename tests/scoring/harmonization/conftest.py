"""Shared fixtures for harmonization holdout scoring tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from fishai.evaluation.harmonization_prereg import load_harmonization_prereg

REPO = Path(__file__).resolve().parents[3]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"


@pytest.fixture
def ready_prereg_path(tmp_path: Path) -> Path:
    doc = load_harmonization_prereg(PREREG)
    block = yaml.safe_load(yaml.dump(doc))["harmonization_wcofs_glorys"]
    block["nearshore"]["shoreline_sha256"] = "abc123"
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
    patched = {"schema_version": 1, "harmonization_wcofs_glorys": block}
    path = tmp_path / "prereg.yaml"
    path.write_text(yaml.dump(patched), encoding="utf-8")
    return path
