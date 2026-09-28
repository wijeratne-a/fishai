"""Graded cell-by-cell input variables (from prereg vs scorer capability)."""

from __future__ import annotations

from typing import Any

# Exactly five cell-by-cell graded inputs the holdout scorer implements.
SCORER_GRADED_INPUT_VARIABLES: tuple[str, ...] = (
    "T3m",
    "S3m",
    "MLD_m",
    "sst_grad",
    "front_distance_km",
)

GRADING_STATUS_GRADED = "graded"
GRADING_STATUS_SHARED_FORCING = "shared_forcing"
GRADING_STATUS_ASSIMILATED_REPORTED_ONLY = "assimilated_reported_only"

VALID_GRADING_STATUSES: frozenset[str] = frozenset(
    {
        GRADING_STATUS_GRADED,
        GRADING_STATUS_SHARED_FORCING,
        GRADING_STATUS_ASSIMILATED_REPORTED_ONLY,
    }
)


def _role_to_grading_status(entry: dict[str, Any]) -> str | None:
    role = str(entry.get("role", ""))
    grading = str(entry.get("grading", ""))
    if grading == "shared_forcing" or role == "shared_forcing":
        return GRADING_STATUS_SHARED_FORCING
    if role == "graded_input":
        return GRADING_STATUS_GRADED
    if role == "report_only":
        return GRADING_STATUS_ASSIMILATED_REPORTED_ONLY
    return None


def variable_grading_status_map(doc: dict[str, Any]) -> dict[str, str]:
    block = doc.get("harmonization_wcofs_glorys") or {}
    cfg = block.get("input_check_grading") or {}
    raw = cfg.get("variable_grading_status")
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}

    out: dict[str, str] = {}
    for item in block.get("variables") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", ""))
        status = _role_to_grading_status(item)
        if name and status:
            out[name] = status
    return out


def graded_input_variables_from_prereg(doc: dict[str, Any]) -> list[str]:
    status_map = variable_grading_status_map(doc)
    return sorted(
        name
        for name, status in status_map.items()
        if status == GRADING_STATUS_GRADED
    )


def collect_graded_input_config_violations(doc: dict[str, Any]) -> list[str]:
    """Return gate violations for graded input list vs scorer and prereg variables."""
    violations: list[str] = []
    block = doc.get("harmonization_wcofs_glorys")
    if not isinstance(block, dict):
        return violations

    status_map = variable_grading_status_map(doc)
    if not status_map:
        violations.append("variables.variable_grading_roles")
        return violations

    for var, status in status_map.items():
        if status not in VALID_GRADING_STATUSES:
            violations.append(f"input_check_grading.variable_grading_status.{var}")

    prereg_vars = block.get("variables")
    if not isinstance(prereg_vars, list):
        violations.append("variables")
        return violations
    var_set: set[str] = set()
    for v in prereg_vars:
        if isinstance(v, dict):
            var_set.add(str(v.get("name", "")))
        else:
            var_set.add(str(v))
    for name in status_map:
        if name not in var_set:
            violations.append("variables.variable_not_in_variables_list")

    graded = set(graded_input_variables_from_prereg(doc))
    scorer_set = set(SCORER_GRADED_INPUT_VARIABLES)
    if graded != scorer_set:
        violations.append("input_check_grading.graded_variables_mismatch_with_scorer")

    missing_graded_in_vars = graded - var_set
    if missing_graded_in_vars:
        violations.append("input_check_grading.graded_variables_not_in_variables_list")

    for name in scorer_set:
        if status_map.get(name) != GRADING_STATUS_GRADED:
            violations.append("input_check_grading.graded_status_missing_or_wrong")

    return violations
