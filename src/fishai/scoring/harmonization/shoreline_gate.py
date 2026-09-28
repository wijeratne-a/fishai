"""Shoreline fingerprint gate via ``frozen_shoreline_reference_sha256()`` (#9)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from fishai.evaluation.harmonization_prereg import (
    frozen_shoreline_reference,
    frozen_shoreline_reference_sha256,
)
from fishai.ingestion.sources import REPO_ROOT


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def shoreline_file_path_from_prereg(doc: dict[str, Any]) -> Path:
    ref = frozen_shoreline_reference(doc)
    rel_path = ref.get("path")
    if not isinstance(rel_path, str) or not rel_path.strip():
        raise ValueError("frozen_shoreline_reference.path missing")
    return REPO_ROOT / rel_path


def collect_shoreline_sha256_gate_violations(doc: dict[str, Any]) -> list[str]:
    """
    Compare vendored shoreline file hash to ``frozen_shoreline_reference_sha256(doc)``.

    Refuses scoring when the prereg hash is missing/invalid or the file does not match.
    """
    try:
        expected = frozen_shoreline_reference_sha256(doc).strip().lower()
    except ValueError:
        return ["frozen_shoreline_reference_sha256_unavailable"]

    try:
        shore_path = shoreline_file_path_from_prereg(doc)
    except ValueError:
        return ["frozen_shoreline_reference.path_missing"]

    if not shore_path.is_file():
        return ["frozen_shoreline_reference.path_not_found"]

    actual = sha256_file(shore_path).lower()
    if actual != expected:
        return ["shoreline_file_sha256_mismatch_frozen_shoreline_reference"]

    near = (doc.get("harmonization_wcofs_glorys") or {}).get("nearshore") or {}
    declared = near.get("shoreline_sha256")
    if isinstance(declared, str) and declared.strip():
        if declared.strip().lower() != expected:
            return ["nearshore.shoreline_sha256_mismatch_frozen_shoreline_reference"]

    return []
