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
FROZEN_SHORELINE_SHA256_PREFIX = "2f677a16"
FROZEN_SHORELINE_SHA256_SUFFIX = "20996c"
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
    return lowered.startswith(FROZEN_SHORELINE_SHA256_PREFIX) and lowered.endswith(
        FROZEN_SHORELINE_SHA256_SUFFIX
    )


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
        "input_verdict_variables",
        "failed_input_stratum_verdict",
        "not_gradable_cap",
        "no_independent_validation",
    ):
        if key not in cutoffs:
            raise HarmonizationPreregNotReadyError(
                f"harmonization scoring blocked: pass_fail_thresholds.cutoffs missing {key}"
            )


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
    try:
        assert_pass_fail_thresholds_ready_for_scoring(doc)
    except HarmonizationPreregNotReadyError:
        raise
    except ValueError as exc:
        raise HarmonizationPreregNotReadyError(str(exc)) from exc


def run_harmonization_scoring(
    prereg_path: Path | str | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Holdout scoring entry point.

    Raises ``HarmonizationPreregNotReadyError`` while any ``TO_BE_SET_BEFORE_SCORING``
    field remains. Full pairing/scoring is implemented in a later change; this gate
    enforces the prereg lock only.
    """
    doc = load_harmonization_prereg(prereg_path)
    assert_harmonization_prereg_ready_for_scoring(doc)
    if dry_run:
        return {"status": "ready", "scoring": "not_implemented"}
    raise NotImplementedError(
        "harmonization holdout scoring is not implemented; prereg placeholders are set"
    )
