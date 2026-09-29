"""Spray glider holdout grading (mapped WCOFS vs obs; RMSE ratio vs GLORYS)."""

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
from fishai.scoring.harmonization.grading import np_finite, rmse_ratio_verdict, worst_of_verdicts
from fishai.scoring.harmonization.metrics import compute_metrics
from fishai.scoring.harmonization.registry import wcofs_independent_observation_source

REQUIRED_GLIDER_CUTOFF_KEYS: tuple[str, ...] = (
    "glider_rmse_ratio_pass",
    "glider_rmse_ratio_ci_upper_pass",
    "glider_rmse_ratio_degraded_upper",
    "glider_bias_abs_pass_c_T3m_10m",
    "glider_bias_abs_pass_c_S3m_10m",
    "glider_bias_abs_pass_c_MLD_m",
)

GLIDER_BIAS_LIMIT_KEY: dict[str, str] = {
    "T3m": "glider_bias_abs_pass_c_T3m_10m",
    "S3m": "glider_bias_abs_pass_c_S3m_10m",
    "MLD_m": "glider_bias_abs_pass_c_MLD_m",
}

GLIDER_REPORT_LABEL = "not_independent_reported_only"
GLIDER_RMSE_RATIO_KNOWN_LIMITATION = (
    "GLORYS may assimilate glider data via CORA; ratio is conservatively biased against WCOFS"
)


@dataclass(frozen=True)
class GliderStratumGrade:
    verdict: str
    reason: str | None
    metrics: list[dict[str, Any]]


def collect_glider_cutoff_gate_violations(cutoffs: dict[str, Any]) -> list[str]:
    missing = [k for k in REQUIRED_GLIDER_CUTOFF_KEYS if k not in cutoffs]
    if missing:
        return [f"pass_fail_thresholds.cutoffs.missing_glider_keys:{','.join(missing)}"]
    return []


def glider_bias_verdict(abs_bias: float, limit: float) -> str:
    """PASS <= limit; DEGRADED in (limit, 2*limit]; FAIL above 2*limit."""
    if abs_bias <= limit:
        return VERDICT_PASS
    if abs_bias <= 2.0 * limit:
        return VERDICT_DEGRADED
    return VERDICT_FAIL


def grade_glider_variable(
    obs: np.ndarray,
    mapped: np.ndarray,
    glorys: np.ndarray,
    dates: np.ndarray,
    cutoffs: dict[str, float],
    *,
    variable: str,
    block_days: int,
    seed: int,
) -> tuple[str, dict[str, Any]]:
    m_mapped = compute_metrics(obs, mapped, dates, block_days=block_days, seed=seed)
    m_glorys = compute_metrics(obs, glorys, dates, block_days=block_days, seed=seed)
    if not (np_finite(m_mapped.rmse) and np_finite(m_glorys.rmse) and m_glorys.rmse > 0):
        return VERDICT_NOT_GRADABLE, {"verdict": VERDICT_NOT_GRADABLE, "reason": "missing_rmse"}

    ratio = m_mapped.rmse / m_glorys.rmse
    ratio_ci_upper = m_mapped.rmse_ci95[1] / m_glorys.rmse if np.isfinite(m_mapped.rmse_ci95[1]) else ratio
    ratio_v = rmse_ratio_verdict(ratio, ratio_ci_upper, cutoffs, prefix="glider_")

    bias_key = GLIDER_BIAS_LIMIT_KEY[variable]
    bias_v = glider_bias_verdict(abs(m_mapped.bias), float(cutoffs[bias_key]))

    margin = float(cutoffs["pearson_r_margin_below_glorys"])
    r_v = (
        VERDICT_PASS
        if m_mapped.pearson_r >= m_glorys.pearson_r - margin
        else VERDICT_FAIL
    )

    verdict = worst_of_verdicts([ratio_v, bias_v, r_v])
    return verdict, {
        "n": m_mapped.n,
        "bias": m_mapped.bias,
        "rmse": m_mapped.rmse,
        "pearson_r": m_mapped.pearson_r,
        "rmse_ratio_mapped_over_glorys": ratio,
        "rmse_ratio_ci95_upper": ratio_ci_upper,
        "bias_ci95": m_mapped.bias_ci95,
        "rmse_ci95": m_mapped.rmse_ci95,
        "pearson_r_ci95": m_mapped.pearson_r_ci95,
        "verdict": verdict,
        "glorys_report": {
            "label": GLIDER_REPORT_LABEL,
            "n": m_glorys.n,
            "bias": m_glorys.bias,
            "rmse": m_glorys.rmse,
            "pearson_r": m_glorys.pearson_r,
        },
    }


def _filter_variable_rows(part: pd.DataFrame, variable: str) -> pd.DataFrame:
    if variable == "MLD_m":
        if "mld_reached" in part.columns:
            return part.loc[part["mld_reached"].astype(bool)]
        if "mld_exclude_reason" in part.columns:
            return part.loc[part["mld_exclude_reason"].isna()]
    return part


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

    countable = sub[
        sub["obs_value"].notna()
        & sub["mapped_value"].notna()
        & sub.get("glorys_value", sub["mapped_value"]).notna()
    ]
    n_profiles = int(countable["profile_id"].nunique()) if "profile_id" in countable.columns else len(countable)
    n_missions = int(countable["mission"].nunique()) if "mission" in countable.columns else 0
    if n_profiles < min_profiles or n_missions < min_missions:
        return GliderStratumGrade(VERDICT_NOT_GRADABLE, "insufficient_glider_coverage", [])

    metrics_out: list[dict[str, Any]] = []
    verdicts: list[str] = []

    for variable in ("T3m", "S3m", "MLD_m"):
        part = _filter_variable_rows(sub[sub["variable"] == variable], variable)
        if part.empty:
            continue
        obs = part["obs_value"].astype(float).values
        mapped = part["mapped_value"].astype(float).values
        glorys = part["glorys_value"].astype(float).values
        d = pd.to_datetime(part["date"]).values.astype("datetime64[D]")
        verdict, metric = grade_glider_variable(
            obs,
            mapped,
            glorys,
            d,
            cutoffs,
            variable=variable,
            block_days=block_days,
            seed=seed,
        )
        metric["variable"] = variable
        metric["model_row"] = "wcofs_coarsened_mapped"
        metric["stratum"] = stratum
        if variable in ("T3m", "S3m"):
            metric["obs_depth_label"] = "proxy_for_3m"
        metrics_out.append(metric)
        verdicts.append(verdict)

    if not verdicts:
        return GliderStratumGrade(VERDICT_NOT_GRADABLE, "no_glider_graded_variables", metrics_out)
    return GliderStratumGrade(worst_of_verdicts(verdicts), None, metrics_out)
