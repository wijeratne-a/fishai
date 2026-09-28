"""Spray glider holdout grading (mapped WCOFS only, no GLORYS ratio)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from fishai.scoring.harmonization.constants import (
    VERDICT_DEGRADED,
    VERDICT_FAIL,
    VERDICT_NOT_GRADABLE,
    VERDICT_PASS,
)
from fishai.scoring.harmonization.grading import worst_of_verdicts
from fishai.scoring.harmonization.metrics import compute_metrics
from fishai.scoring.harmonization.registry import wcofs_independent_observation_source

REQUIRED_GLIDER_CUTOFF_KEYS: tuple[str, ...] = (
    "glider_bias_abs_pass_c",
    "glider_rmse_pass_c",
    "glider_rmse_degraded_c",
    "glider_pearson_r_min",
)

GLIDER_REPORT_LABEL = "not_independent_reported_only"


@dataclass(frozen=True)
class GliderStratumGrade:
    verdict: str
    reason: str | None
    metrics: list[dict[str, Any]]


def collect_glider_cutoff_gate_violations(cutoffs: dict[str, Any]) -> list[str]:
    missing = [k for k in REQUIRED_GLIDER_CUTOFF_KEYS if k not in cutoffs]
    if missing:
        return [f"pass_fail_thresholds.cutoffs.missing_glider_keys:{','.join(missing)}"]
    if "rmse_ratio_pass" in {k for k in cutoffs if str(k).startswith("glider_rmse_ratio")}:
        return ["pass_fail_thresholds.cutoffs.glider_rmse_ratio_not_supported"]
    return []


def _grade_absolute_rmse_bias_r(
    obs: np.ndarray,
    pred: np.ndarray,
    dates: np.ndarray,
    cutoffs: dict[str, float],
    *,
    block_days: int,
    seed: int,
) -> tuple[str, dict[str, Any]]:
    m = compute_metrics(obs, pred, dates, block_days=block_days, seed=seed)
    bias_lim = float(cutoffs["glider_bias_abs_pass_c"])
    rmse_pass = float(cutoffs["glider_rmse_pass_c"])
    rmse_deg = float(cutoffs["glider_rmse_degraded_c"])
    r_min = float(cutoffs["glider_pearson_r_min"])

    bias_v = VERDICT_PASS if abs(m.bias) <= bias_lim else VERDICT_FAIL
    if m.rmse <= rmse_pass:
        rmse_v = VERDICT_PASS
    elif m.rmse <= rmse_deg:
        rmse_v = VERDICT_DEGRADED
    else:
        rmse_v = VERDICT_FAIL
    r_v = VERDICT_PASS if m.pearson_r >= r_min else VERDICT_FAIL
    verdict = worst_of_verdicts([bias_v, rmse_v, r_v])
    return verdict, {
        "n": m.n,
        "bias": m.bias,
        "rmse": m.rmse,
        "pearson_r": m.pearson_r,
        "bias_ci95": m.bias_ci95,
        "rmse_ci95": m.rmse_ci95,
        "pearson_r_ci95": m.pearson_r_ci95,
        "verdict": verdict,
    }


def grade_glider_stratum(
    match_df: pd.DataFrame,
    *,
    stratum: str,
    cutoffs: dict[str, float],
    block_days: int,
    seed: int,
    registry: dict[str, Any],
    min_profiles: int,
    min_missions: int,
) -> GliderStratumGrade:
    sub = match_df.loc[match_df["stratum"] == stratum].copy()
    if not wcofs_independent_observation_source("spray_glider_profiles", registry):
        return GliderStratumGrade(VERDICT_NOT_GRADABLE, "observation_source_not_independent", [])

    mld_sub = sub[(sub["variable"] == "MLD_m") & sub["obs_value"].notna() & sub["mapped_value"].notna()]
    n_profiles = int(mld_sub["profile_id"].nunique()) if "profile_id" in mld_sub.columns else len(mld_sub)
    n_missions = int(mld_sub["mission"].nunique()) if "mission" in mld_sub.columns else 0
    if n_profiles < min_profiles or n_missions < min_missions:
        return GliderStratumGrade(VERDICT_NOT_GRADABLE, "insufficient_glider_coverage", [])

    metrics_out: list[dict[str, Any]] = []
    verdicts: list[str] = []
    dates = pd.to_datetime(sub["date"]).values.astype("datetime64[D]")

    for variable in ("T3m", "S3m", "MLD_m"):
        part = sub[sub["variable"] == variable]
        if part.empty:
            continue
        obs = part["obs_value"].astype(float).values
        mapped = part["mapped_value"].astype(float).values
        d = pd.to_datetime(part["date"]).values.astype("datetime64[D]")
        verdict, metric = _grade_absolute_rmse_bias_r(
            obs, mapped, d, cutoffs, block_days=block_days, seed=seed
        )
        metric["variable"] = variable
        metric["model_row"] = "wcofs_coarsened_mapped"
        metric["stratum"] = stratum
        if variable in ("T3m", "S3m"):
            metric["obs_depth_label"] = "proxy_for_3m"
        if "glorys_value" in part.columns:
            g_obs = part["obs_value"].astype(float).values
            g_pred = part["glorys_value"].astype(float).values
            g_metric = compute_metrics(g_obs, g_pred, d, block_days=block_days, seed=seed)
            metric["glorys_report"] = {
                "label": GLIDER_REPORT_LABEL,
                "n": g_metric.n,
                "bias": g_metric.bias,
                "rmse": g_metric.rmse,
                "pearson_r": g_metric.pearson_r,
            }
        metrics_out.append(metric)
        verdicts.append(verdict)

    if not verdicts:
        return GliderStratumGrade(VERDICT_NOT_GRADABLE, "no_glider_graded_variables", metrics_out)
    return GliderStratumGrade(worst_of_verdicts(verdicts), None, metrics_out)
