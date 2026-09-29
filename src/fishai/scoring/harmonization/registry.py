"""Assimilated-sources registry for independence gating."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from fishai.ingestion.sources import REPO_ROOT

DEFAULT_REGISTRY_PATH = REPO_ROOT / "config" / "assimilated_sources.yaml"

WCOFS_ASSIMILATED_STATUSES = frozenset({"true", "presumed_true"})
WCOFS_NOT_INDEPENDENT_STATUSES = frozenset({"true", "presumed_true", "unknown"})

from fishai.scoring.harmonization.observation_sources import holdout_validation_registry_ids


def load_assimilated_sources_registry(path: Path | str | None = None) -> dict[str, Any]:
    p = Path(path) if path is not None else DEFAULT_REGISTRY_PATH
    if not p.is_file():
        raise FileNotFoundError(f"assimilated sources registry not found: {p}")
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"assimilated_sources.yaml must be a mapping: {p}")
    return raw


def _model_block(entry: dict[str, Any], model: str) -> dict[str, Any]:
    block = entry.get(model)
    if isinstance(block, dict):
        return block
    # Legacy flat wcofs/glorys string values.
    if model in entry and isinstance(entry.get(model), str):
        return {"status": entry[model]}
    return {}


def _citation_complete(citation: object) -> bool:
    if not isinstance(citation, dict):
        return False
    for key in ("title", "url", "page_section", "quote"):
        val = citation.get(key)
        if not isinstance(val, str) or not val.strip():
            return False
    return True


def wcofs_effective_assimilation_status(entry: dict[str, Any]) -> str:
    """
    Effective WCOFS assimilation status for independence.

    ``false`` counts as independent only with a complete citation and
    ``accepted_by_auditor: true``; otherwise treated as ``unknown``.
    """
    block = _model_block(entry, "wcofs")
    raw = str(block.get("status", "unknown")).lower()
    if raw in WCOFS_ASSIMILATED_STATUSES:
        return raw
    if raw == "false":
        accepted = bool(block.get("accepted_by_auditor", False))
        if accepted and _citation_complete(block.get("citation")):
            return "false"
        return "unknown"
    if raw == "unknown":
        return "unknown"
    return "unknown"


def wcofs_independent_observation_source(source_id: str, registry: dict[str, Any]) -> bool:
    """True when WCOFS is confirmed not to assimilate this source."""
    sources = registry.get("sources") or {}
    entry = sources.get(source_id)
    if not isinstance(entry, dict):
        return False
    return wcofs_effective_assimilation_status(entry) == "false"


def any_holdout_validation_source_independent_of_wcofs(registry: dict[str, Any]) -> bool:
    return any(
        wcofs_independent_observation_source(source_id, registry)
        for source_id in holdout_validation_registry_ids()
    )


def no_independent_validation_messages(registry: dict[str, Any]) -> list[str]:
    """
    Preflight messages when no holdout validation source is WCOFS-independent.

    Each message is named ``NO_INDEPENDENT_VALIDATION`` for operator visibility.
    """
    if any_holdout_validation_source_independent_of_wcofs(registry):
        return []
    messages: list[str] = []
    sources = registry.get("sources") or {}
    for source_id in holdout_validation_registry_ids():
        entry = sources.get(source_id)
        if not isinstance(entry, dict):
            messages.append(
                f"NO_INDEPENDENT_VALIDATION: {source_id} missing from registry; "
                "verdicts will all be UNKNOWN"
            )
            continue
        display = str(entry.get("display_name", source_id))
        status = wcofs_effective_assimilation_status(entry)
        messages.append(
            f"NO_INDEPENDENT_VALIDATION: {display} assimilation status is "
            f"'{status}' for WCOFS; verdicts will all be UNKNOWN"
        )
    return messages
