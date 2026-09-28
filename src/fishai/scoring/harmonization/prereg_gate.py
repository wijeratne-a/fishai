"""Validate harmonization pre-registration before any scoring I/O."""

from __future__ import annotations

from typing import Any

from fishai.evaluation.harmonization_prereg import PLACEHOLDER_TOKEN
from fishai.scoring.harmonization.grading import normalize_combination_rule
from fishai.scoring.harmonization.input_check_config import collect_graded_input_config_violations

REQUIRED_CUTOFF_NUMERIC_KEYS: tuple[str, ...] = (
    "rmse_ratio_pass",
    "rmse_ratio_ci_upper_pass",
    "rmse_ratio_degraded_upper",
    "bias_abs_pass_c",
    "bias_abs_degraded_c",
    "pearson_r_margin_below_glorys",
    "min_matched_daily_values",
    "min_buoys",
    "input_rmse_pass_fraction_glorys_sd",
    "input_rmse_degraded_fraction_glorys_sd",
    "bootstrap_seed",
)

INVALID_STRINGS = frozenset({"", "tbd", "to_be_set_before_scoring", "pending"})


def _is_blank_or_pending(value: object) -> bool:
    if value is None:
        return True
    if value == PLACEHOLDER_TOKEN:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return True
        lower = stripped.lower()
        if lower in INVALID_STRINGS:
            return True
        if "pending" in lower:
            return True
    return False


def collect_prereg_gate_violations(doc: dict[str, Any]) -> list[str]:
    """Return dotted field paths that block holdout scoring."""
    violations: list[str] = []
    block = doc.get("harmonization_wcofs_glorys")
    if not isinstance(block, dict):
        return ["harmonization_wcofs_glorys"]

    split = block.get("temporal_split") or {}
    for key in ("fit_end", "test_start"):
        if _is_blank_or_pending(split.get(key)):
            violations.append(f"temporal_split.{key}")

    near = block.get("nearshore") or {}
    if _is_blank_or_pending(near.get("shoreline_source")):
        violations.append("nearshore.shoreline_source")
    if _is_blank_or_pending(near.get("shoreline_sha256")):
        violations.append("nearshore.shoreline_sha256")
    simp = near.get("shoreline_simplification_check")
    if _is_blank_or_pending(simp) or not isinstance(simp, dict):
        violations.append("nearshore.shoreline_simplification_check")
    elif isinstance(simp, dict):
        for sk in ("max_coastline_displacement_m", "nearshore_flag_diff_cell_count"):
            val = simp.get(sk)
            if _is_blank_or_pending(val) or not isinstance(val, (int, float)):
                violations.append(f"nearshore.shoreline_simplification_check.{sk}")
    if _is_blank_or_pending(near.get("cutoff_km")):
        violations.append("nearshore.cutoff_km")

    pf = block.get("pass_fail_thresholds") or {}
    cutoffs = pf.get("cutoffs")
    if _is_blank_or_pending(cutoffs) or not isinstance(cutoffs, dict):
        violations.append("pass_fail_thresholds.cutoffs")
    elif isinstance(cutoffs, dict):
        for key in REQUIRED_CUTOFF_NUMERIC_KEYS:
            val = cutoffs.get(key)
            if _is_blank_or_pending(val) or not isinstance(val, (int, float)):
                violations.append(f"pass_fail_thresholds.cutoffs.{key}")

    combo = pf.get("combination_rule")
    if _is_blank_or_pending(combo):
        violations.append("pass_fail_thresholds.combination_rule")
    elif isinstance(combo, str):
        try:
            normalize_combination_rule(combo)
        except ValueError:
            violations.append("pass_fail_thresholds.combination_rule")

    violations.extend(collect_graded_input_config_violations(doc))

    return sorted(violations)


def assert_prereg_gate(doc: dict[str, Any]) -> None:
    from fishai.evaluation.harmonization_prereg import HarmonizationPreregNotReadyError

    violations = collect_prereg_gate_violations(doc)
    if violations:
        fields = ", ".join(violations)
        raise HarmonizationPreregNotReadyError(
            f"harmonization scoring blocked: invalid or unset prereg fields ({fields})"
        )
