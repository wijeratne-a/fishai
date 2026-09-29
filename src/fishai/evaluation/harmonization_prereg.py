"""Load harmonization pre-registration and gate holdout scoring."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PREREG_PATH = REPO_ROOT / "prereg" / "harmonization_wcofs_glorys.yaml"
PLACEHOLDER_TOKEN = "TO_BE_SET_BEFORE_SCORING"
PENDING_COMBINATION_RULE_PREFIX = "PENDING_AUDITOR_CONFIRMATION"
_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


class HarmonizationPreregNotReadyError(RuntimeError):
    """Raised when scoring is attempted before required prereg fields are set."""


def load_harmonization_prereg(path: Path | str | None = None) -> dict[str, Any]:
    """Parse ``prereg/harmonization_wcofs_glorys.yaml`` (or override path)."""
    p = Path(path) if path is not None else DEFAULT_PREREG_PATH
    if not p.is_file():
        raise FileNotFoundError(f"harmonization prereg not found: {p}")
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"harmonization prereg must be a mapping: {p}")
    block = raw.get("harmonization_wcofs_glorys")
    if not isinstance(block, dict):
        raise ValueError(f"missing harmonization_wcofs_glorys block in {p}")
    return raw


def frozen_shoreline_reference(doc: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the auditor-frozen pilot shoreline block from harmonization prereg."""
    raw = doc if doc is not None else load_harmonization_prereg()
    block = raw["harmonization_wcofs_glorys"]
    ref = block.get("frozen_shoreline_reference")
    if not isinstance(ref, dict):
        raise ValueError("missing frozen_shoreline_reference in harmonization prereg")
    return ref


def frozen_shoreline_reference_sha256(doc: dict[str, Any] | None = None) -> str:
    """SHA-256 of ``frozen_shoreline_reference.path`` (single value for Bot4 scoring)."""
    ref = frozen_shoreline_reference(doc)
    sha = ref.get("sha256")
    if not is_valid_frozen_shoreline_sha256(sha):
        raise ValueError(f"malformed frozen_shoreline_reference.sha256: {sha!r}")
    if ref.get("frozen") is not True:
        raise ValueError("frozen_shoreline_reference is not marked frozen")
    return str(sha)


def is_valid_frozen_shoreline_sha256(value: object) -> bool:
    """True when ``value`` is a 64-char lowercase hex SHA-256 with prereg prefix/suffix."""
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    if not _SHA256_HEX_RE.match(lowered):
        return False
    return True


# Bot4 PR #10 and other scoring code import this constant instead of hard-coding hashes.
FROZEN_PILOT_SHORELINE_REFERENCE_SHA256 = frozen_shoreline_reference_sha256()


def pass_fail_thresholds_cutoffs(doc: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return auditbot1 cutoff block from ``pass_fail_thresholds.cutoffs``."""
    raw = doc if doc is not None else load_harmonization_prereg()
    block = raw["harmonization_wcofs_glorys"].get("pass_fail_thresholds")
    if not isinstance(block, dict):
        raise ValueError("missing pass_fail_thresholds in harmonization prereg")
    cutoffs = block.get("cutoffs")
    if not isinstance(cutoffs, dict):
        raise ValueError("pass_fail_thresholds.cutoffs must be a mapping")
    return cutoffs


def combination_rule_blocks_scoring(cutoffs: dict[str, Any]) -> bool:
    """True while ``combination_rule`` awaits auditor confirmation."""
    rule = cutoffs.get("combination_rule")
    return isinstance(rule, str) and rule.startswith(PENDING_COMBINATION_RULE_PREFIX)


PASS_FAIL_GRADED_INPUT_COUNT = 5

UPWELLING_LAG_TRAILING_MEAN_DAYS = (0, 7, 14, 28)
UPWELLING_LAG_SELECTION_METHOD = "time_forward_cv_mean_out_of_fold_log_likelihood"
UPWELLING_LAG_FIT_SPLIT_END = "2017-12-31"
UPWELLING_LAG_FROZEN_BEFORE = "2018-01-01"
UPWELLING_LAG_HOLDOUT_TEST_END = "2022-04-27"


def upwelling_lags_prereg(doc: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the ``upwelling_lags`` block (CUFES pilot; applies only if upwelling survives)."""
    raw = doc if doc is not None else load_harmonization_prereg()
    block = raw["harmonization_wcofs_glorys"].get("upwelling_lags")
    if not isinstance(block, dict):
        raise ValueError("missing upwelling_lags in harmonization prereg")
    return block


def upwelling_survives_in_pilot_variables(doc: dict[str, Any] | None = None) -> bool:
    """True when ``upwelling`` is declared and not marked for drop when wind product is missing."""
    raw = doc if doc is not None else load_harmonization_prereg()
    vars_by_name = {v["name"]: v for v in raw["harmonization_wcofs_glorys"]["variables"]}
    up = vars_by_name.get("upwelling")
    if not isinstance(up, dict):
        return False
    blank = up.get("blank_when")
    if isinstance(blank, dict) and blank.get("exclude_events") is False:
        return True
    return up.get("role") == "graded_input"


def assert_upwelling_lags_prereg(doc: dict[str, Any] | None = None) -> None:
    """Validate preregistered upwelling lag candidates and frozen selection policy."""
    lags = upwelling_lags_prereg(doc)
    if lags.get("window_end") != "day_before_event":
        raise ValueError("upwelling_lags.window_end must be day_before_event")
    if lags.get("no_other_lags") is not True:
        raise ValueError("upwelling_lags.no_other_lags must be true")
    days = tuple(c["trailing_mean_days"] for c in lags["candidates"])
    if days != UPWELLING_LAG_TRAILING_MEAN_DAYS:
        raise ValueError(
            f"upwelling_lags candidates must be {UPWELLING_LAG_TRAILING_MEAN_DAYS}, got {days!r}"
        )
    sel = lags.get("selection")
    if not isinstance(sel, dict):
        raise ValueError("upwelling_lags.selection must be a mapping")
    if sel.get("method") != UPWELLING_LAG_SELECTION_METHOD:
        raise ValueError("upwelling_lags.selection.method mismatch")
    if sel.get("fit_split_end") != UPWELLING_LAG_FIT_SPLIT_END:
        raise ValueError("upwelling_lags.selection.fit_split_end mismatch")
    if sel.get("frozen_before") != UPWELLING_LAG_FROZEN_BEFORE:
        raise ValueError("upwelling_lags.selection.frozen_before mismatch")
    if sel.get("holdout_test_end") != UPWELLING_LAG_HOLDOUT_TEST_END:
        raise ValueError("upwelling_lags.selection.holdout_test_end mismatch")
    if sel.get("never_reselect_after_freeze") is not True:
        raise ValueError("upwelling_lags.selection.never_reselect_after_freeze must be true")
    note = sel.get("note")
    if not isinstance(note, str) or "re-select" not in note.lower():
        raise ValueError("upwelling_lags.selection.note must forbid post-test re-selection")


def pass_fail_graded_input_names(doc: dict[str, Any] | None = None) -> tuple[str, ...]:
    """Return cell-gate graded input names from ``pass_fail_thresholds.cutoffs``."""
    cutoffs = pass_fail_thresholds_cutoffs(doc)
    names = cutoffs.get("graded_inputs")
    if not isinstance(names, list) or not names:
        raise ValueError("pass_fail_thresholds.cutoffs.graded_inputs must be a non-empty list")
    return tuple(str(n) for n in names)


def _variable_is_never_cell_graded(entry: dict[str, Any]) -> bool:
    if entry.get("grading") == "shared_forcing":
        return True
    return entry.get("role") == "report_only"


def assert_graded_inputs_declared_in_variables(doc: dict[str, Any]) -> None:
    """Every ``graded_inputs`` name must appear in harmonization ``variables``."""
    expected = pass_fail_graded_input_names(doc)
    if len(expected) != PASS_FAIL_GRADED_INPUT_COUNT:
        raise ValueError(
            "pass_fail_thresholds.cutoffs.graded_inputs must list exactly "
            f"{PASS_FAIL_GRADED_INPUT_COUNT} names, got {len(expected)}"
        )
    block = doc["harmonization_wcofs_glorys"]
    vars_by_name = {v["name"]: v for v in block["variables"]}
    missing = [n for n in expected if n not in vars_by_name]
    if missing:
        raise ValueError(f"graded_inputs missing from variables list: {missing}")
    for name in expected:
        entry = vars_by_name[name]
        if _variable_is_never_cell_graded(entry):
            raise ValueError(f"graded_inputs must not include never-graded variable {name!r}")
        if entry.get("role") != "graded_input":
            raise ValueError(f"variables.{name}.role must be graded_input for cell gate")
    for name, entry in vars_by_name.items():
        if not _variable_is_never_cell_graded(entry):
            continue
        if name in expected:
            raise ValueError(f"shared_forcing/report_only variable {name!r} is in graded_inputs")


def assert_pass_fail_thresholds_ready_for_scoring(doc: dict[str, Any]) -> None:
    """Refuse scoring until cutoff combination_rule is auditor-confirmed."""
    cutoffs = pass_fail_thresholds_cutoffs(doc)
    if combination_rule_blocks_scoring(cutoffs):
        raise HarmonizationPreregNotReadyError(
            "harmonization scoring blocked: pass_fail_thresholds.cutoffs.combination_rule "
            "pending auditor confirmation"
        )
    rule = cutoffs.get("combination_rule")
    if rule != "worst_of":
        raise HarmonizationPreregNotReadyError(
            f"harmonization scoring blocked: unsupported combination_rule {rule!r}"
        )
    for key in (
        "verdict_rank_worst_first",
        "graded_inputs",
        "failed_input_stratum_verdict",
        "not_gradable_cap",
        "no_independent_validation",
        "graded_inputs_cell_gate",
    ):
        if key not in cutoffs:
            raise HarmonizationPreregNotReadyError(
                f"harmonization scoring blocked: pass_fail_thresholds.cutoffs missing {key}"
            )
    try:
        assert_graded_inputs_declared_in_variables(doc)
    except ValueError as exc:
        raise HarmonizationPreregNotReadyError(str(exc)) from exc


def iter_placeholder_fields(node: object, prefix: str = "") -> list[str]:
    """Return dotted paths whose value equals ``TO_BE_SET_BEFORE_SCORING``."""
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            found.extend(iter_placeholder_fields(value, path))
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            found.extend(iter_placeholder_fields(item, f"{prefix}[{idx}]"))
    elif node == PLACEHOLDER_TOKEN:
        found.append(prefix or PLACEHOLDER_TOKEN)
    return found


def shoreline_simplification_check(doc: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return bot2 shoreline simplification fidelity block from nearshore prereg."""
    raw = doc if doc is not None else load_harmonization_prereg()
    near = raw["harmonization_wcofs_glorys"]["nearshore"]
    check = near.get("shoreline_simplification_check")
    if check == PLACEHOLDER_TOKEN or not isinstance(check, dict):
        raise ValueError("shoreline_simplification_check is unset or not a mapping")
    return check


def assert_shoreline_simplification_check_valid(doc: dict[str, Any] | None = None) -> None:
    """Refuse scoring when simplification check is placeholder, mismatched, or wrong hash."""
    check = shoreline_simplification_check(doc)
    mismatches = check.get("nearshore_flag_mismatches_vs_full_resolution")
    if mismatches is None or int(mismatches) > 0:
        raise ValueError(
            "shoreline_simplification_check: nearshore_flag_mismatches_vs_full_resolution "
            f"must be 0, got {mismatches!r}"
        )
    file_sha = check.get("file_sha256")
    frozen_sha = frozen_shoreline_reference_sha256(doc)
    if file_sha != frozen_sha:
        raise ValueError(
            "shoreline_simplification_check.file_sha256 must equal "
            "frozen_shoreline_reference.sha256"
        )


def assert_harmonization_prereg_ready_for_scoring(doc: dict[str, Any]) -> None:
    """Refuse holdout scoring until required prereg fields are concrete and consistent."""
    block = doc.get("harmonization_wcofs_glorys")
    if not isinstance(block, dict):
        raise HarmonizationPreregNotReadyError("missing harmonization_wcofs_glorys block")
    pending = iter_placeholder_fields(block)
    if pending:
        fields = ", ".join(sorted(pending))
        raise HarmonizationPreregNotReadyError(
            f"harmonization scoring blocked: unset prereg fields ({fields})"
        )
    try:
        assert_shoreline_simplification_check_valid(doc)
    except ValueError as exc:
        raise HarmonizationPreregNotReadyError(str(exc)) from exc
    from fishai.scoring.harmonization.input_check_config import (
        collect_graded_input_config_violations,
    )

    graded_input_violations = collect_graded_input_config_violations(doc)
    if graded_input_violations:
        fields = ", ".join(sorted(graded_input_violations))
        raise HarmonizationPreregNotReadyError(
            f"harmonization scoring blocked: invalid or unset prereg fields ({fields})"
        )
    try:
        assert_pass_fail_thresholds_ready_for_scoring(doc)
    except HarmonizationPreregNotReadyError:
        raise
    except ValueError as exc:
        raise HarmonizationPreregNotReadyError(str(exc)) from exc
    from fishai.scoring.harmonization.prereg_gate import assert_prereg_gate

    assert_prereg_gate(doc)


def run_harmonization_scoring(
    prereg_path: Path | str | None = None,
    *,
    dry_run: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Holdout scoring entry point (delegates to ``fishai.scoring.harmonization``).

    Raises ``HarmonizationPreregNotReadyError`` while required prereg fields are unset.
    """
    from fishai.scoring.harmonization.runner import run_holdout_scoring

    return run_holdout_scoring(prereg_path, dry_run=dry_run, **kwargs)
