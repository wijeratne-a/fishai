"""Pass / degraded / fail grading for harmonization holdout."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fishai.scoring.harmonization.constants import (
    FAIL_EVIDENCE_REASON,
    VERDICT_DEGRADED,
    VERDICT_FAIL,
    VERDICT_NOT_GRADABLE,
    VERDICT_PASS,
)

VERDICT_RANK = {
    VERDICT_NOT_GRADABLE: 0,
    VERDICT_PASS: 1,
    VERDICT_DEGRADED: 2,
    VERDICT_FAIL: 3,
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


def _ratio_verdict(
    ratio: float,
    ratio_ci_upper: float,
    cutoffs: dict[str, float],
) -> str:
    pass_lim = float(cutoffs["rmse_ratio_pass"])
    deg_upper = float(cutoffs["rmse_ratio_degraded_upper"])
    ci_pass = float(cutoffs["rmse_ratio_ci_upper_pass"])
    if ratio <= pass_lim and ratio_ci_upper <= ci_pass:
        base = VERDICT_PASS
    elif ratio <= deg_upper:
        base = VERDICT_DEGRADED
    else:
        base = VERDICT_FAIL
    return base


def grade_buoy_stratum(inp: BuoyGradeInput, cutoffs: dict[str, float]) -> tuple[str, str | None]:
    if not inp.independent_source:
        return VERDICT_NOT_GRADABLE, "observation_source_assimilated_by_wcofs"
    min_n = int(cutoffs["min_matched_daily_values"])
    min_buoys = int(cutoffs["min_buoys"])
    if inp.n < min_n or inp.n_buoys < min_buoys:
        return VERDICT_NOT_GRADABLE, "insufficient_matched_observations"

    if not (
        np_finite(inp.rmse_mapped)
        and np_finite(inp.rmse_glorys)
        and inp.rmse_glorys > 0
    ):
        return VERDICT_NOT_GRADABLE, "missing_rmse"

    ratio = inp.rmse_mapped / inp.rmse_glorys
    ratio_verdict = _ratio_verdict(ratio, inp.rmse_ratio_ci_upper, cutoffs)

    bias_lim_pass = float(cutoffs["bias_abs_pass_c"])
    bias_lim_deg = float(cutoffs["bias_abs_degraded_c"])
    abs_bias = abs(inp.bias_c)
    if abs_bias <= bias_lim_pass:
        bias_verdict = VERDICT_PASS
    elif abs_bias <= bias_lim_deg:
        bias_verdict = VERDICT_DEGRADED
    else:
        bias_verdict = VERDICT_FAIL

    margin = float(cutoffs["pearson_r_margin_below_glorys"])
    if inp.pearson_r_mapped >= inp.pearson_r_glorys - margin:
        r_verdict = VERDICT_PASS
    else:
        r_verdict = VERDICT_FAIL

    verdict = _worst_of([ratio_verdict, bias_verdict, r_verdict])
    reason = FAIL_EVIDENCE_REASON if verdict == VERDICT_FAIL else None
    return verdict, reason


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
    not_gradable_combination: str,
) -> str:
    if combination_rule != "worst_of":
        raise ValueError(f"unsupported combination_rule: {combination_rule}")

    pool = [buoy_verdict] + list(input_verdicts)
    if not_gradable_combination == "dominates":
        if any(v == VERDICT_NOT_GRADABLE for v in pool):
            return VERDICT_NOT_GRADABLE
        gradable = [v for v in pool if v != VERDICT_NOT_GRADABLE]
        return _worst_of(gradable) if gradable else VERDICT_NOT_GRADABLE
    # ignore: drop not_gradable when combining
    gradable = [v for v in pool if v != VERDICT_NOT_GRADABLE]
    if not gradable:
        return VERDICT_NOT_GRADABLE
    return _worst_of(gradable)


def _worst_of(verdicts: list[str]) -> str:
    best = VERDICT_NOT_GRADABLE
    best_rank = -1
    for v in verdicts:
        rank = VERDICT_RANK.get(v, -1)
        if rank > best_rank:
            best_rank = rank
            best = v
    return best


def np_finite(x: float) -> bool:
    import math

    return math.isfinite(x)


def cutoffs_from_prereg(doc: dict[str, Any]) -> dict[str, float]:
    block = doc["harmonization_wcofs_glorys"]
    raw = block["pass_fail_thresholds"]["cutoffs"]
    return {k: float(raw[k]) for k in raw}
