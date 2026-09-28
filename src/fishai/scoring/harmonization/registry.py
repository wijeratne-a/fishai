"""Assimilated-sources registry for independence gating."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from fishai.ingestion.sources import REPO_ROOT

DEFAULT_REGISTRY_PATH = REPO_ROOT / "config" / "assimilated_sources.yaml"

WCOFS_ASSIMILATED_VALUES = frozenset({"true", "presumed_true"})
WCOFS_INDEPENDENT_VALUE = "false"


def load_assimilated_sources_registry(path: Path | str | None = None) -> dict[str, Any]:
    p = Path(path) if path is not None else DEFAULT_REGISTRY_PATH
    if not p.is_file():
        raise FileNotFoundError(f"assimilated sources registry not found: {p}")
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"assimilated_sources.yaml must be a mapping: {p}")
    return raw


def wcofs_independent_observation_source(source_id: str, registry: dict[str, Any]) -> bool:
    """True when the registry shows WCOFS does not assimilate this source."""
    sources = registry.get("sources") or {}
    entry = sources.get(source_id)
    if not isinstance(entry, dict):
        return False
    status = str(entry.get("wcofs", "unknown")).lower()
    if status in WCOFS_ASSIMILATED_VALUES:
        return False
    if status == WCOFS_INDEPENDENT_VALUE:
        return True
    # unknown (or any other value) is not confirmed independent — not gradable
    return False
