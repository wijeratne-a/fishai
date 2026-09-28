"""Depth function identity and end-to-end runner on synthetic fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from fishai.evaluation.harmonization_prereg import load_harmonization_prereg
from fishai.ingestion.physics.wcofs_glorys_grid import harmonization_temperature_at_buoy_depth
from fishai.scoring.harmonization.constants import VERDICT_PASS
from fishai.scoring.harmonization.input_check_config import SCORER_GRADED_INPUT_VARIABLES
from fishai.scoring.harmonization.registry import load_assimilated_sources_registry, wcofs_independent_observation_source
from fishai.scoring.harmonization.runner import (
    BUOY_DEPTH_FUNCTION,
    prereg_file_commit,
    run_holdout_scoring,
)

REPO = Path(__file__).resolve().parents[3]
PREREG = REPO / "prereg" / "harmonization_wcofs_glorys.yaml"


def test_shared_buoy_depth_function_identity() -> None:
    assert BUOY_DEPTH_FUNCTION is harmonization_temperature_at_buoy_depth
    depth = np.array([0.0, 0.494, 1.0, 5.0])
    temp = np.array([18.0, 17.5, 17.0, 14.0])
    val = BUOY_DEPTH_FUNCTION(depth, temp)
    assert np.isfinite(val)


def test_registry_marks_ndbc_accepted_independent_for_wcofs() -> None:
    reg = load_assimilated_sources_registry()
    assert wcofs_independent_observation_source("ndbc_buoy_temperature", reg) is True


def _small_ready_prereg(tmp_path: Path) -> Path:
    doc = load_harmonization_prereg(PREREG)
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
        "min_matched_daily_values": 10,
        "min_buoys": 3,
        "input_rmse_pass_fraction_glorys_sd": 0.5,
        "input_rmse_degraded_fraction_glorys_sd": 1.0,
        "bootstrap_seed": 7,
        "glider_rmse_ratio_pass": 1.2,
        "glider_rmse_ratio_ci_upper_pass": 1.5,
        "glider_rmse_ratio_degraded_upper": 1.5,
        "glider_bias_abs_pass_c_T3m_10m": 0.5,
        "glider_bias_abs_pass_c_S3m_10m": 0.1,
        "glider_bias_abs_pass_c_MLD_m": 10.0,
    }
    block["pass_fail_thresholds"]["combination_rule"] = "worst-of"
    path = tmp_path / "prereg.yaml"
    path.write_text(yaml.dump({"schema_version": 1, "harmonization_wcofs_glorys": block}), encoding="utf-8")
    return path


def _synthetic_pairing(n: int = 40) -> pd.DataFrame:
    dates = pd.date_range("2025-09-01", periods=n, freq="D")
    rows = []
    for i, d in enumerate(dates):
        buoy = f"b{i % 4}"
        obs = 15.0 + 0.01 * i
        rows.append(
            {
                "date": d.date().isoformat(),
                "variable": "sea_water_temperature",
                "obs_value": obs,
                "nearshore": i % 2 == 0,
                "obs_id": buoy,
                "wcofs_native": obs + 0.05,
                "wcofs_coarsened": obs + 0.04,
                "wcofs_coarsened_mapped": obs + 0.02,
                "glorys": obs + 0.03,
            }
        )
    return pd.DataFrame(rows)


def test_runner_writes_outputs(tmp_path: Path) -> None:
    prereg_path = _small_ready_prereg(tmp_path)
    map_dir = tmp_path / "map"
    map_dir.mkdir()
    prereg_commit = prereg_file_commit(prereg_path)
    (map_dir / "manifest.json").write_text(
        json.dumps(
            {
                "fitting_commit_sha": "f",
                "prereg_commit_sha": prereg_commit,
                "fit_split_parquet_sha256": "deadbeef",
            }
        ),
        encoding="utf-8",
    )
    input_rows = []
    for stratum in ("pooled", "nearshore", "offshore"):
        for var in SCORER_GRADED_INPUT_VARIABLES:
            input_rows.append(
                {
                    "stratum": stratum,
                    "variable": var,
                    "rmse": 0.1,
                    "glorys_spatial_sd": 1.0,
                }
            )
        # shared_forcing: extreme RMSE must not change buoy+graded verdict
        input_rows.append(
            {
                "stratum": stratum,
                "variable": "upwelling",
                "rmse": 99.0,
                "glorys_spatial_sd": 1.0,
            }
        )
    out_dir = tmp_path / "scores"
    summary = run_holdout_scoring(
        prereg_path,
        pairing_table=_synthetic_pairing(),
        input_check_table=pd.DataFrame(input_rows),
        front_detail_native_sst_grad=[1.0, 2.0],
        front_detail_coarsened_sst_grad=[0.8, 1.6],
        output_dir=out_dir,
        map_dir=map_dir,
        verify_map=True,
    )
    assert (out_dir / "holdout_scores.parquet").is_file()
    assert (out_dir / "summary.json").is_file()
    assert summary["insufficient_model_coverage"]["total"] == 0
    assert summary["preflight"]["any_independent_validation_source"] is True
    assert summary["preflight"]["no_independent_validation_messages"] == []
    ns = [m for m in summary["metrics"] if m["model_row"] == "wcofs_coarsened_mapped" and m["stratum"] == "pooled"]
    assert ns and ns[0]["n"] == 40
    assert ns[0]["verdict"] == VERDICT_PASS
    up_rows = [r for r in summary["input_cell_check"] if r["variable"] == "upwelling"]
    assert up_rows and up_rows[0]["reason"] == "shared_forcing"
    assert up_rows[0]["verdict"] is None
    for row in ("wcofs_native", "wcofs_coarsened", "glorys"):
        same_n = [m for m in summary["metrics"] if m["model_row"] == row and m["stratum"] == "pooled"]
        assert same_n[0]["n"] == 40
