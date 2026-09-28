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
    """Refuse holdout scoring until required prereg fields are concrete."""
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
