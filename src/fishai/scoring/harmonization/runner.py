"""Harmonization holdout scoring orchestration."""

from __future__ import annotations

import datetime as dt
import hashlib
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from fishai.evaluation.harmonization_prereg import DEFAULT_PREREG_PATH, load_harmonization_prereg
from fishai.ingestion.physics.sources.glorys import resolve_glorys_product_id
from fishai.ingestion.physics.vertical import GLORYS_TOP_LEVEL_DEPTH_M, interp_tracer_at_depth_below_surface
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
from fishai.scoring.harmonization.common_support import (
    apply_common_support,
    insufficient_coverage_counts,
)
from fishai.scoring.harmonization.constants import (
    ALL_MODEL_ROWS,
    GRADED_MODEL_ROW,
    MODEL_ROW_GLORYS,
    MODEL_ROW_WCOFS_COARSENED,
    MODEL_ROW_WCOFS_COARSENED_MAPPED,
    MODEL_ROW_WCOFS_NATIVE,
    NO_INDEPENDENT_VALIDATION_REASON,
    VERDICT_UNKNOWN,
)
from fishai.scoring.harmonization.input_cell_check import build_input_cell_check_summary
from fishai.scoring.harmonization.observation_sources import primary_buoy_validation_registry_id
from fishai.scoring.harmonization.grading import (
    BuoyGradeInput,
    combine_stratum_verdicts,
    cutoffs_from_prereg,
    grade_buoy_stratum,
)
from fishai.scoring.harmonization.glider_grading import (
    GLIDER_RMSE_RATIO_KNOWN_LIMITATION,
    grade_glider_stratum,
)
from fishai.scoring.harmonization.preflight import run_registry_preflight
from fishai.scoring.harmonization.io import write_holdout_outputs
from fishai.scoring.harmonization.manifest import verify_mapping_manifest
from fishai.scoring.harmonization.metrics import compute_metrics
from fishai.scoring.harmonization.prereg_gate import assert_prereg_gate
from fishai.scoring.harmonization.registry import (
    load_assimilated_sources_registry,
    wcofs_independent_observation_source,
)
from fishai.scoring.harmonization.seasons import season_label

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[4] / "artifacts" / "harmonization" / "holdout_scores"

def buoy_temperature_at_harmonization_depth(
    depth_levels_m: np.ndarray,
    temperature: np.ndarray,
) -> float:
    """NDBC buoy match depth: GLORYS top level below the moving surface (0.494 m)."""
    return interp_tracer_at_depth_below_surface(
        depth_levels_m,
        temperature,
        GLORYS_TOP_LEVEL_DEPTH_M,
        extrapolate_above_top=True,
    )


# Shared depth path exported for tests (all rows must use this for buoy temperature).
BUOY_DEPTH_FUNCTION = buoy_temperature_at_harmonization_depth

STRATA_POOL = ("pooled", "nearshore", "offshore")
SEASONAL_STRATA = True


def prereg_file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def prereg_file_commit(path: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%H", "--", str(path)],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if out:
            return out
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return "unknown"


def _config_date(value: Any) -> dt.date:
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def _filter_test_split(df: pd.DataFrame, test_start: dt.date, test_end: dt.date) -> pd.DataFrame:
    if "date" not in df.columns:
        raise ValueError("pairing table requires a date column")
    dates = pd.to_datetime(df["date"]).dt.date
    return df.loc[(dates >= test_start) & (dates <= test_end)].copy()


def _stratum_mask(df: pd.DataFrame, stratum: str) -> pd.Series:
    if stratum == "pooled":
        return pd.Series(True, index=df.index)
    if stratum == "nearshore":
        return df["nearshore"].astype(bool)
    if stratum == "offshore":
        return ~df["nearshore"].astype(bool)
    raise ValueError(f"unknown stratum: {stratum}")


def _front_detail_loss(native: np.ndarray, coarsened: np.ndarray) -> float:
    n = np.nanmean(native)
    c = np.nanmean(coarsened)
    if not np.isfinite(n) or n == 0:
        return float("nan")
    return float(c / n)


def run_holdout_scoring(
    prereg_path: Path | str | None = None,
    *,
    pairing_table: pd.DataFrame | None = None,
    input_check_table: pd.DataFrame | None = None,
    front_detail_native_sst_grad: list[float] | None = None,
    front_detail_coarsened_sst_grad: list[float] | None = None,
    indirect_buoy_table: pd.DataFrame | None = None,
    glider_match_table: pd.DataFrame | None = None,
    output_dir: Path | str | None = None,
    map_dir: Path | str | None = None,
    registry_path: Path | str | None = None,
    dry_run: bool = False,
    verify_map: bool = True,
) -> dict[str, Any]:
    """
    Score harmonization holdout on the TEST split.

    The pre-registration gate runs before any model/observation tables are read.
    """
    prereg_file = Path(prereg_path) if prereg_path is not None else DEFAULT_PREREG_PATH
    doc = load_harmonization_prereg(prereg_file)
    assert_prereg_gate(doc)

    registry = load_assimilated_sources_registry(registry_path)
    preflight = run_registry_preflight(registry)

    if dry_run and pairing_table is None:
        return {
            "status": "ready",
            "prereg_sha256": prereg_file_sha256(prereg_file),
            "buoy_depth_function": BUOY_DEPTH_FUNCTION.__name__,
            "preflight": preflight,
        }

    block = doc["harmonization_wcofs_glorys"]
    split = block["temporal_split"]
    test_start = _config_date(split["test_start"])
    test_end = _config_date(split["test_end"])
    block_days = int(block["metrics"]["reporting"]["block_bootstrap_block_days"])
    cutoffs = cutoffs_from_prereg(doc)
    seed = int(cutoffs["bootstrap_seed"])
    prereg_commit = prereg_file_commit(prereg_file)
    prereg_sha = prereg_file_sha256(prereg_file)
    overlap_cfg = load_overlap_config()
    glorys_product_id = resolve_glorys_product_id(test_start, config=overlap_cfg)

    if verify_map:
        verify_mapping_manifest(map_dir, expected_prereg_commit=prereg_commit)

    force_unknown_verdicts = not preflight["any_independent_validation_source"]

    if pairing_table is None:
        raise ValueError("pairing_table is required unless dry_run=True")

    work = _filter_test_split(pairing_table, test_start, test_end)
    kept, dropped = apply_common_support(work)
    coverage_drop = insufficient_coverage_counts(dropped)

    rows_out: list[dict[str, Any]] = []
    summary_metrics: list[dict[str, Any]] = []

    for variable, var_df in kept.groupby("variable"):
        for model_row in ALL_MODEL_ROWS:
            for stratum in STRATA_POOL:
                mask = _stratum_mask(var_df, stratum)
                sub = var_df.loc[mask]
                dates = pd.to_datetime(sub["date"]).values.astype("datetime64[D]")
                obs = sub["obs_value"].astype(float).values
                pred = sub[model_row].astype(float).values
                m = compute_metrics(obs, pred, dates, block_days=block_days, seed=seed)
                entry = {
                    "model_row": model_row,
                    "stratum": stratum,
                    "season": None,
                    "variable": variable,
                    "graded": model_row == GRADED_MODEL_ROW and stratum in STRATA_POOL,
                    "n": m.n,
                    "bias": m.bias,
                    "rmse": m.rmse,
                    "pearson_r": m.pearson_r,
                    "bias_ci95_lo": m.bias_ci95[0],
                    "bias_ci95_hi": m.bias_ci95[1],
                    "rmse_ci95_lo": m.rmse_ci95[0],
                    "rmse_ci95_hi": m.rmse_ci95[1],
                    "pearson_r_ci95_lo": m.pearson_r_ci95[0],
                    "pearson_r_ci95_hi": m.pearson_r_ci95[1],
                    "verdict": None,
                    "reason": None,
                    "indirect": False,
                }
                rows_out.append(entry)
                summary_metrics.append(entry)

            if SEASONAL_STRATA:
                season_key = var_df["date"].map(
                    lambda d: season_label(
                        pd.to_datetime(d).date(), test_start=test_start, test_end=test_end
                    )
                )
                for season, season_df in var_df.groupby(season_key, sort=True):
                    dates = pd.to_datetime(season_df["date"]).values.astype("datetime64[D]")
                    obs = season_df["obs_value"].astype(float).values
                    pred = season_df[model_row].astype(float).values
                    m = compute_metrics(obs, pred, dates, block_days=block_days, seed=seed)
                    entry = {
                        "model_row": model_row,
                        "stratum": "season",
                        "season": season,
                        "variable": variable,
                        "graded": False,
                        "n": m.n,
                        "bias": m.bias,
                        "rmse": m.rmse,
                        "pearson_r": m.pearson_r,
                        "bias_ci95_lo": m.bias_ci95[0],
                        "bias_ci95_hi": m.bias_ci95[1],
                        "rmse_ci95_lo": m.rmse_ci95[0],
                        "rmse_ci95_hi": m.rmse_ci95[1],
                        "pearson_r_ci95_lo": m.pearson_r_ci95[0],
                        "pearson_r_ci95_hi": m.pearson_r_ci95[1],
                        "verdict": None,
                        "reason": None,
                        "indirect": False,
                    }
                    rows_out.append(entry)

    # Grading (mapped row, buoy temperature, graded strata only)
    grading_cfg = block.get("nowcast_forcing_grading") or {}
    if grading_cfg:
        combination_rule = str(
            grading_cfg.get("combination_rules", {}).get("per_stratum", "worst_verdict_across_checks")
        ).replace("_", "-")
    else:
        combination_rule = str(block["pass_fail_thresholds"]["combination_rule"])
    buoy_var = kept[kept["variable"] == "sea_water_temperature"] if "variable" in kept.columns else kept
    input_cell_check_summary: list[dict[str, Any]] = []
    glider_grading_summary: list[dict[str, Any]] = []
    obs_block = block.get("observations") or {}
    spray_cfg = obs_block.get("spray_glider_profiles") or obs_block.get("scripps_spray_gliders") or {}
    gradability = spray_cfg.get("gradability") or spray_cfg
    min_glider_profiles = int(gradability.get("min_matched_profiles", 100))
    min_glider_missions = int(gradability.get("min_distinct_missions", 3))

    for stratum in STRATA_POOL:
        mask = _stratum_mask(buoy_var, stratum)
        sub = buoy_var.loc[mask]
        source_id = primary_buoy_validation_registry_id()
        independent = wcofs_independent_observation_source(source_id, registry)
        n_buoys = int(sub["obs_id"].nunique()) if "obs_id" in sub.columns else 0
        dates = pd.to_datetime(sub["date"]).values.astype("datetime64[D]")
        obs = sub["obs_value"].astype(float).values
        mapped_pred = sub[MODEL_ROW_WCOFS_COARSENED_MAPPED].astype(float).values
        glorys_pred = sub[MODEL_ROW_GLORYS].astype(float).values
        m_mapped = compute_metrics(obs, mapped_pred, dates, block_days=block_days, seed=seed)
        m_glorys = compute_metrics(obs, glorys_pred, dates, block_days=block_days, seed=seed)
        ratio_ci_upper = (
            m_mapped.rmse / m_glorys.rmse * 1.0
            if m_glorys.rmse and np.isfinite(m_glorys.rmse)
            else float("nan")
        )
        if np.isfinite(m_mapped.rmse_ci95[1]) and m_glorys.rmse > 0:
            ratio_ci_upper = m_mapped.rmse_ci95[1] / m_glorys.rmse

        input_verdicts, input_rows = build_input_cell_check_summary(
            doc, input_check_table, stratum, cutoffs
        )
        input_cell_check_summary.extend(input_rows)

        if force_unknown_verdicts:
            combined = VERDICT_UNKNOWN
            combined_reason = NO_INDEPENDENT_VALIDATION_REASON
        else:
            buoy_grade = grade_buoy_stratum(
                BuoyGradeInput(
                    n=m_mapped.n,
                    n_buoys=n_buoys,
                    bias_c=m_mapped.bias,
                    rmse_mapped=m_mapped.rmse,
                    rmse_glorys=m_glorys.rmse,
                    rmse_ratio_ci_upper=ratio_ci_upper,
                    pearson_r_mapped=m_mapped.pearson_r,
                    pearson_r_glorys=m_glorys.pearson_r,
                    independent_source=independent,
                ),
                cutoffs,
            )
            glider_verdict: str | None = None
            if glider_match_table is not None and not glider_match_table.empty:
                glider_grade = grade_glider_stratum(
                    glider_match_table,
                    stratum=stratum,
                    cutoffs=cutoffs,
                    block_days=block_days,
                    seed=seed,
                    registry=registry,
                    min_profiles=min_glider_profiles,
                    min_missions=min_glider_missions,
                )
                glider_verdict = glider_grade.verdict
                for gm in glider_grade.metrics:
                    gm["stratum_combined_reason"] = glider_grade.reason
                    glider_grading_summary.append(gm)
            combined, combined_reason = combine_stratum_verdicts(
                buoy_grade[0],
                input_verdicts,
                combination_rule=combination_rule,
                glider_verdict=glider_verdict,
            )
        for entry in summary_metrics:
            if (
                entry["model_row"] == GRADED_MODEL_ROW
                and entry["stratum"] == stratum
                and entry["variable"] == "sea_water_temperature"
                and entry.get("season") is None
            ):
                entry["verdict"] = combined
                entry["reason"] = combined_reason

    front_loss = _front_detail_loss(
        np.asarray(front_detail_native_sst_grad or [], dtype=float),
        np.asarray(front_detail_coarsened_sst_grad or [], dtype=float),
    )

    indirect_summary: list[dict[str, Any]] = []
    if indirect_buoy_table is not None:
        for _, row in indirect_buoy_table.iterrows():
            indirect_summary.append(
                {
                    "label": "indirect",
                    "season": row.get("season"),
                    "n": int(row.get("n", 0)),
                    "rmse_my": float(row.get("rmse_my", float("nan"))),
                    "rmse_myint": float(row.get("rmse_myint", float("nan"))),
                }
            )

    detail_df = pd.DataFrame(rows_out)
    summary = {
        "prereg_commit": prereg_commit,
        "prereg_sha256": prereg_sha,
        "test_start": split["test_start"],
        "test_end": split["test_end"],
        "model_rows": list(ALL_MODEL_ROWS),
        "preflight": preflight,
        "insufficient_model_coverage": coverage_drop,
        "glorys_reference_product_id": glorys_product_id,
        "front_detail_loss": front_loss,
        "metrics": summary_metrics,
        "input_cell_check": input_cell_check_summary,
        "glider_holdout_grading": glider_grading_summary,
        "glider_holdout_known_limitations": [GLIDER_RMSE_RATIO_KNOWN_LIMITATION],
        "indirect_glorys_product_check": indirect_summary,
        "buoy_depth_function": f"{BUOY_DEPTH_FUNCTION.__module__}.{BUOY_DEPTH_FUNCTION.__name__}",
    }

    out_path = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    write_holdout_outputs(out_path, detail_df, summary)
    return summary


def run_harmonization_scoring(
    prereg_path: Path | str | None = None,
    *,
    dry_run: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Backward-compatible alias used by ``fishai.evaluation.harmonization_prereg``."""
    return run_holdout_scoring(prereg_path, dry_run=dry_run, **kwargs)
