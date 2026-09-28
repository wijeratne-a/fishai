"""Validate harmonization pre-registration before any scoring I/O."""

from __future__ import annotations

from typing import Any

from fishai.evaluation.harmonization_prereg import PLACEHOLDER_TOKEN
from fishai.scoring.harmonization.grading import cutoffs_from_prereg, normalize_combination_rule
from fishai.scoring.harmonization.glider_grading import collect_glider_cutoff_gate_violations
from fishai.scoring.harmonization.input_check_config import collect_graded_input_config_violations
from fishai.scoring.harmonization.shoreline_gate import collect_shoreline_sha256_gate_violations

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
        for sk in (
            "max_coastline_displacement_km",
            "nearshore_flag_mismatches_vs_full_resolution",
        ):
            val = simp.get(sk)
            if _is_blank_or_pending(val) or not isinstance(val, (int, float)):
                violations.append(f"nearshore.shoreline_simplification_check.{sk}")
    if _is_blank_or_pending(near.get("cutoff_km")):
        violations.append("nearshore.cutoff_km")
    violations.extend(collect_shoreline_sha256_gate_violations(doc))

    grading = block.get("nowcast_forcing_grading")
    pf = block.get("pass_fail_thresholds") or {}
    if grading is None and not pf:
        violations.append("nowcast_forcing_grading")
    elif grading is not None:
        combo = (grading.get("combination_rules") or {}).get("per_stratum")
        if combo and not _is_blank_or_pending(combo):
            try:
                normalize_combination_rule(str(combo).replace("_", "-"))
            except ValueError:
                violations.append("nowcast_forcing_grading.combination_rules.per_stratum")
        obs = block.get("observations") or {}
        if "scripps_spray_gliders" in obs or "spray_glider_profiles" in obs:
            try:
                cutoffs = cutoffs_from_prereg(doc)
                violations.extend(collect_glider_cutoff_gate_violations(cutoffs))
            except (KeyError, TypeError, ValueError) as exc:
                violations.append(f"nowcast_forcing_grading.cutoffs_incomplete:{exc}")
    elif isinstance(pf, dict):
        cutoffs = pf.get("cutoffs")
        if _is_blank_or_pending(cutoffs) or not isinstance(cutoffs, dict):
            violations.append("pass_fail_thresholds.cutoffs")
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
