"""Graded cell-by-cell input variables (from prereg vs scorer capability)."""

from __future__ import annotations

from typing import Any

# Exactly what the holdout scorer can grade in the cell-by-cell input check.
SCORER_GRADED_INPUT_VARIABLES: tuple[str, ...] = (
    "T3m",
    "S3m",
    "MLD_m",
    "sst_grad",
    "front_distance_km",
    "upwelling",
)

REPORTED_NOT_GRADED_VARIABLES: tuple[str, ...] = ("u_surf", "v_surf")


def graded_input_variables_from_prereg(doc: dict[str, Any]) -> list[str]:
    block = doc.get("harmonization_wcofs_glorys") or {}
    cfg = block.get("input_check_grading") or {}
    raw = cfg.get("graded_variables")
    if not isinstance(raw, list):
        return []
    return [str(v) for v in raw]


def collect_graded_input_config_violations(doc: dict[str, Any]) -> list[str]:
    """Return gate violations for graded input list vs scorer and prereg variables."""
    violations: list[str] = []
    block = doc.get("harmonization_wcofs_glorys")
    if not isinstance(block, dict):
        return violations

    cfg = block.get("input_check_grading")
    if not isinstance(cfg, dict):
        violations.append("input_check_grading")
        return violations

    graded = graded_input_variables_from_prereg(doc)
    if not graded:
        violations.append("input_check_grading.graded_variables")
        return violations

    scorer_set = set(SCORER_GRADED_INPUT_VARIABLES)
    config_set = set(graded)
    if config_set != scorer_set:
        violations.append("input_check_grading.graded_variables_mismatch_with_scorer")

    prereg_vars = block.get("variables")
    if not isinstance(prereg_vars, list):
        violations.append("variables")
        return violations
    var_set = {str(v) for v in prereg_vars}
    missing = config_set - var_set
    if missing:
        violations.append("input_check_grading.graded_variables_not_in_variables_list")

    return violations
