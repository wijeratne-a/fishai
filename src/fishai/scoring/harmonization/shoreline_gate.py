"""Shoreline fingerprint gate (frozen_shoreline_reference from prereg #9)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from fishai.ingestion.sources import REPO_ROOT


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def frozen_shoreline_reference_block(doc: dict[str, Any]) -> dict[str, Any] | None:
    block = doc.get("harmonization_wcofs_glorys") or {}
    near = block.get("nearshore") or {}
    ref_key = near.get("frozen_shoreline_reference_key") or "frozen_shoreline_reference"
    ref = block.get(ref_key)
    return ref if isinstance(ref, dict) else None


def frozen_shoreline_sha256_from_prereg(doc: dict[str, Any]) -> str | None:
    """Authoritative SHA-256 from prereg ``frozen_shoreline_reference`` (or named key)."""
    ref = frozen_shoreline_reference_block(doc)
    if not ref:
        return None
    sha = ref.get("sha256")
    if not isinstance(sha, str) or len(sha.strip()) != 64:
        return None
    return sha.strip().lower()


def collect_shoreline_sha256_gate_violations(doc: dict[str, Any]) -> list[str]:
    block = doc.get("harmonization_wcofs_glorys") or {}
    near = block.get("nearshore") or {}
    declared = near.get("shoreline_sha256")
    if not isinstance(declared, str) or not declared.strip():
        return []

    expected = frozen_shoreline_sha256_from_prereg(doc)
    if expected is None:
        ref_key = near.get("frozen_shoreline_reference_key") or "frozen_shoreline_reference"
        return [f"{ref_key}.sha256_missing_or_invalid"]

    if declared.strip().lower() != expected:
        return ["nearshore.shoreline_sha256_mismatch_frozen_shoreline_reference"]

    ref = frozen_shoreline_reference_block(doc) or {}
    rel_path = ref.get("path")
    if not isinstance(rel_path, str) or not rel_path.strip():
        return ["frozen_shoreline_reference.path_missing"]
    shore_path = REPO_ROOT / rel_path
    if not shore_path.is_file():
        return ["frozen_shoreline_reference.path_not_found"]
    if sha256_file(shore_path).lower() != expected:
        return ["frozen_shoreline_reference.file_sha256_mismatch"]

    return []
