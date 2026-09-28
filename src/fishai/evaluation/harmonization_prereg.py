"""Load harmonization pre-registration and gate holdout scoring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PREREG_PATH = REPO_ROOT / "prereg" / "harmonization_wcofs_glorys.yaml"
PLACEHOLDER_TOKEN = "TO_BE_SET_BEFORE_SCORING"


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


def assert_harmonization_prereg_ready_for_scoring(doc: dict[str, Any]) -> None:
    """Refuse holdout scoring until bot2/auditbot1 placeholders are concrete."""
    block = doc.get("harmonization_wcofs_glorys")
    if not isinstance(block, dict):
        raise HarmonizationPreregNotReadyError("missing harmonization_wcofs_glorys block")
    pending = iter_placeholder_fields(block)
    if pending:
        fields = ", ".join(sorted(pending))
        raise HarmonizationPreregNotReadyError(
            f"harmonization scoring blocked: unset prereg fields ({fields})"
        )


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
