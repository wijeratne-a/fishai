"""Pass / degraded / fail grading for harmonization holdout."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fishai.evaluation.nowcast_forcing_buoy import (
    BuoyStratumMetrics,
    evaluate_buoy_stratum_verdict,
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

# Worst (highest rank) to best: UNKNOWN > FAIL > DEGRADED > PASS
VERDICT_RANK = {
    VERDICT_PASS: 1,
    VERDICT_DEGRADED: 2,
    VERDICT_FAIL: 3,
    VERDICT_UNKNOWN: 4,
    VERDICT_NOT_GRADABLE: 0,
}


@dataclass(frozen=True)
class BuoyGradeInput:
    n: int
    n_buoys: int
    bias_c: float
    rmse_mapped: float
    rmse_glorys: float
    rmse_ratio_ci_upper: float
    pearson_r_mapped: float
    pearson_r_glorys: float
    independent_source: bool


@dataclass(frozen=True)
class InputCheckGradeInput:
    rmse: float
    glorys_spatial_sd: float


def normalize_combination_rule(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in ("worst_of", "worstof", "worst_verdict_across_checks", "worstverdictacrosschecks"):
        return "worst_of"
    raise ValueError(f"unsupported combination_rule: {value}")


def rmse_ratio_verdict(
    ratio: float,
    ratio_ci_upper: float,
    cutoffs: dict[str, float],
    *,
    prefix: str = "",
) -> str:
    pass_lim = float(cutoffs[f"{prefix}rmse_ratio_pass"])
    deg_upper = float(cutoffs[f"{prefix}rmse_ratio_degraded_upper"])
    ci_pass = float(cutoffs[f"{prefix}rmse_ratio_ci_upper_pass"])
    if ratio <= pass_lim and ratio_ci_upper <= ci_pass:
        return VERDICT_PASS
    if ratio <= deg_upper:
        return VERDICT_DEGRADED
    return VERDICT_FAIL


def grade_buoy_stratum(
    inp: BuoyGradeInput,
    cutoffs: dict[str, float],
    *,
    doc: dict[str, Any],
) -> tuple[str, str | None]:
    """Holdout buoy gate: gradability pre-checks then #9 ``evaluate_buoy_stratum_verdict``."""
    min_n = int(cutoffs["min_matched_daily_values"])
    min_buoys = int(cutoffs["min_buoys"])
    if inp.n < min_n or inp.n_buoys < min_buoys:
        return VERDICT_DEGRADED, BUOY_INSUFFICIENT_OBS_REASON

    if not inp.independent_source:
        return VERDICT_NOT_GRADABLE, "observation_source_assimilated_by_wcofs"

    if not (
        np_finite(inp.rmse_mapped)
        and np_finite(inp.rmse_glorys)
        and inp.rmse_glorys > 0
    ):
        return VERDICT_NOT_GRADABLE, "missing_rmse"

    metrics = BuoyStratumMetrics(
        rmse_ratio=inp.rmse_mapped / inp.rmse_glorys,
        rmse_ratio_bootstrap_upper_95=inp.rmse_ratio_ci_upper,
        absolute_bias_c=inp.bias_c,
        pearson_r=inp.pearson_r_mapped,
        glorys_pearson_r=inp.pearson_r_glorys,
    )
    result = evaluate_buoy_stratum_verdict(metrics, doc=doc)
    return result.verdict, result.reason


def grade_input_check(inp: InputCheckGradeInput, cutoffs: dict[str, float]) -> str:
    if not np_finite(inp.rmse) or not np_finite(inp.glorys_spatial_sd) or inp.glorys_spatial_sd <= 0:
        return VERDICT_NOT_GRADABLE
    rel = inp.rmse / inp.glorys_spatial_sd
    pass_frac = float(cutoffs["input_rmse_pass_fraction_glorys_sd"])
    deg_frac = float(cutoffs["input_rmse_degraded_fraction_glorys_sd"])
    if rel <= pass_frac:
        return VERDICT_PASS
    if rel <= deg_frac:
        return VERDICT_DEGRADED
    return VERDICT_FAIL


def combine_stratum_verdicts(
    buoy_verdict: str,
    input_verdicts: list[str],
    *,
    combination_rule: str,
    glider_verdict: str | None = None,
) -> tuple[str, str | None]:
    """
    Worst-of buoy and input checks.

    Any failed input check forces UNKNOWN with ``nowcast_forcing_failed_holdout``.
    """
    normalize_combination_rule(combination_rule)
    if any(v == VERDICT_FAIL for v in input_verdicts):
        return VERDICT_UNKNOWN, FAIL_EVIDENCE_REASON

    pool = [buoy_verdict]
    if glider_verdict is not None and glider_verdict != VERDICT_NOT_GRADABLE:
        pool.append(glider_verdict)
    pool.extend([v for v in input_verdicts if v != VERDICT_NOT_GRADABLE])
    if not pool:
        return VERDICT_NOT_GRADABLE, None

    worst = worst_of_verdicts(pool)
    reason: str | None = None
    if worst in (VERDICT_FAIL, VERDICT_UNKNOWN):
        reason = FAIL_EVIDENCE_REASON
    return worst, reason


def worst_of_verdicts(verdicts: list[str]) -> str:
    worst = VERDICT_PASS
    worst_rank = -1
    for v in verdicts:
        rank = VERDICT_RANK.get(v, -1)
        if rank > worst_rank:
            worst_rank = rank
            worst = v
    return worst


def np_finite(x: float) -> bool:
    import math

    return math.isfinite(x)


def _cutoffs_from_pass_fail_thresholds_block(
    cutoffs: dict[str, Any],
    block: dict[str, Any],
) -> dict[str, float]:
    buoy = cutoffs.get("buoy_gate") or {}
    pass_req = buoy.get("pass_requires_all") or {}
    deg = buoy.get("degraded") or {}
    strata = cutoffs.get("strata") or {}
    gradability = strata.get("gradability") or {}
    cell = cutoffs.get("graded_inputs_cell_gate") or {}
    rmse_sd = cell.get("rmse_vs_glorys_spatial_sd") or {}
    glider_tests = (
        ((block.get("observations") or {}).get("scripps_spray_gliders") or {}).get("tests") or {}
    )
    abs_lim = glider_tests.get("absolute_bias_limits") or {}
    ratio_max = float(pass_req["rmse_ratio_max"])
    ratio_ci = float(pass_req["rmse_ratio_bootstrap_upper_95_max"])
    ratio_deg = float(deg["rmse_ratio_max_inclusive"])
    return {
        "rmse_ratio_pass": ratio_max,
        "rmse_ratio_ci_upper_pass": ratio_ci,
        "rmse_ratio_degraded_upper": ratio_deg,
        "bias_abs_pass_c": float(pass_req["absolute_bias_C_max"]),
        "bias_abs_degraded_c": float(deg["absolute_bias_C_max_inclusive"]),
        "pearson_r_margin_below_glorys": float(pass_req["pearson_r_max_deficit_vs_glorys_r"]),
        "min_matched_daily_values": float(gradability["min_matched_daily_values"]),
        "min_buoys": float(gradability["min_distinct_buoys"]),
        "input_rmse_pass_fraction_glorys_sd": float(rmse_sd["pass_max_multiple"]),
        "input_rmse_degraded_fraction_glorys_sd": float(rmse_sd["degraded_max_multiple"]),
        "bootstrap_seed": 42.0,
        "glider_rmse_ratio_pass": ratio_max,
        "glider_rmse_ratio_ci_upper_pass": ratio_ci,
        "glider_rmse_ratio_degraded_upper": ratio_deg,
        "glider_bias_abs_pass_c_T3m_10m": float(abs_lim["temperature_10m_C"]),
        "glider_bias_abs_pass_c_S3m_10m": float(abs_lim["salinity_10m"]),
        "glider_bias_abs_pass_c_MLD_m": float(abs_lim["MLD_m"]),
    }


def cutoffs_from_prereg(doc: dict[str, Any]) -> dict[str, float]:
    block = doc["harmonization_wcofs_glorys"]
    pf = block.get("pass_fail_thresholds") or {}
    raw = pf.get("cutoffs")
    if isinstance(raw, dict) and raw and raw != "TO_BE_SET_BEFORE_SCORING":
        if "buoy_gate" in raw:
            return _cutoffs_from_pass_fail_thresholds_block(raw, block)
        try:
            return {k: float(v) for k, v in raw.items() if isinstance(v, (int, float))}
        except (TypeError, ValueError):
            pass

    grading = block.get("nowcast_forcing_grading") or {}
    buoy = grading.get("buoy_gate") or {}
    ratio = buoy.get("rmse_ratio_to_glorys") or {}
    bias = buoy.get("absolute_bias_C") or {}
    pearson = buoy.get("pearson_r") or {}
    ndbc = (block.get("observations") or {}).get("ndbc_hull_temperature") or {}
    gradability = (ndbc.get("forcing_gate") or {}).get("gradability") or {}
    inputs = (grading.get("graded_inputs_gate") or {}).get("rmse_vs_glorys_sd") or {}
    glider_tests = (
        ((block.get("observations") or {}).get("scripps_spray_gliders") or {}).get("tests") or {}
    )
    abs_lim = glider_tests.get("absolute_bias_limits") or {}

    ratio_pass = ratio.get("pass") or {}
    ratio_deg = ratio.get("degraded") or {}
    cutoffs: dict[str, float] = {
        "rmse_ratio_pass": float(ratio_pass["ratio_max"]),
        "rmse_ratio_ci_upper_pass": float(ratio_pass["bootstrap_upper_95_max"]),
        "rmse_ratio_degraded_upper": float(ratio_deg["ratio_max_inclusive"]),
        "bias_abs_pass_c": float(bias["pass_max"]),
        "bias_abs_degraded_c": float(bias["degraded_max_inclusive"]),
        "pearson_r_margin_below_glorys": float(pearson["max_deficit_vs_glorys_r"]),
        "min_matched_daily_values": float(gradability["min_matched_daily_values"]),
        "min_buoys": float(gradability["min_distinct_buoys"]),
        "input_rmse_pass_fraction_glorys_sd": float(inputs["pass_max_multiple"]),
        "input_rmse_degraded_fraction_glorys_sd": float(inputs["degraded_max_multiple"]),
        "bootstrap_seed": 42.0,
        "glider_rmse_ratio_pass": float(ratio_pass["ratio_max"]),
        "glider_rmse_ratio_ci_upper_pass": float(ratio_pass["bootstrap_upper_95_max"]),
        "glider_rmse_ratio_degraded_upper": float(ratio_deg["ratio_max_inclusive"]),
        "glider_bias_abs_pass_c_T3m_10m": float(abs_lim["temperature_10m_C"]),
        "glider_bias_abs_pass_c_S3m_10m": float(abs_lim["salinity_10m"]),
        "glider_bias_abs_pass_c_MLD_m": float(abs_lim["MLD_m"]),
    }
    return cutoffs
