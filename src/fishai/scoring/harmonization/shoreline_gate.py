"""Shoreline fingerprint gate (PR #7 overlap config path, not hard-coded hashes)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from fishai.ingestion.physics.coast_distance import shoreline_path_from_config
from fishai.ingestion.physics.wcofs_glorys_overlap import DEFAULT_CONFIG, load_overlap_config
from fishai.ingestion.sources import REPO_ROOT


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def pilot_shoreline_sha256_from_overlap_config(
    config_path: Path | str | None = None,
) -> str:
    """SHA-256 of the vendored pilot shoreline file referenced in overlap config."""
    cfg = load_overlap_config(config_path or DEFAULT_CONFIG)
    shore_path = shoreline_path_from_config(cfg)
    if not shore_path.is_file():
        raise FileNotFoundError(f"pilot shoreline not found: {shore_path}")
    return sha256_file(shore_path)


def collect_shoreline_sha256_gate_violations(
    doc: dict[str, Any],
    *,
    config_path: Path | str | None = None,
) -> list[str]:
    block = doc.get("harmonization_wcofs_glorys") or {}
    near = block.get("nearshore") or {}
    declared = near.get("shoreline_sha256")
    if not isinstance(declared, str) or not declared.strip():
        return []

    try:
        expected = pilot_shoreline_sha256_from_overlap_config(config_path)
    except FileNotFoundError:
        return ["nearshore.shoreline_sha256_overlap_file_missing"]

    if declared.strip().lower() != expected.lower():
        return ["nearshore.shoreline_sha256_mismatch_overlap_config"]

    frozen = block.get("frozen_shoreline_reference") or {}
    frozen_sha = frozen.get("sha256")
    if isinstance(frozen_sha, str) and frozen_sha.strip().lower() != expected.lower():
        return ["frozen_shoreline_reference.sha256_mismatch_overlap_config"]

    return []
