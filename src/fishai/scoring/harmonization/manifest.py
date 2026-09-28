"""Frozen WCOFS→GLORYS mapping artifact verification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from fishai.ingestion.sources import REPO_ROOT

DEFAULT_MAP_DIR = REPO_ROOT / "artifacts" / "harmonization" / "wcofs_to_glorys_map" / "v1"


class MappingManifestError(RuntimeError):
    """Raised when the frozen mapping manifest is missing or fails verification."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_mapping_manifest(
    map_dir: Path | str | None = None,
    *,
    expected_prereg_commit: str,
    expected_fit_parquet_sha256: str | None = None,
) -> dict[str, Any]:
    """
    Load ``manifest.json`` and verify recorded SHAs/commits.

    Raises ``MappingManifestError`` on any mismatch or missing file.
    """
    root = Path(map_dir) if map_dir is not None else DEFAULT_MAP_DIR
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        raise MappingManifestError(f"mapping manifest missing: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise MappingManifestError("manifest.json must be a JSON object")

    fit_commit = manifest.get("fitting_commit_sha")
    prereg_commit = manifest.get("prereg_commit_sha")
    parquet_sha = manifest.get("fit_split_parquet_sha256")

    errors: list[str] = []
    if not fit_commit:
        errors.append("fitting_commit_sha missing")
    if not prereg_commit:
        errors.append("prereg_commit_sha missing")
    if not parquet_sha:
        errors.append("fit_split_parquet_sha256 missing")
    if prereg_commit and prereg_commit != expected_prereg_commit:
        errors.append(
            f"prereg_commit_sha mismatch (manifest {prereg_commit}, expected {expected_prereg_commit})"
        )
    if expected_fit_parquet_sha256 and parquet_sha != expected_fit_parquet_sha256:
        errors.append("fit_split_parquet_sha256 mismatch")

    fit_parquet = manifest.get("fit_split_parquet_path")
    if fit_parquet:
        pq = root / fit_parquet if not Path(fit_parquet).is_absolute() else Path(fit_parquet)
        if pq.is_file() and parquet_sha:
            actual = _sha256_file(pq)
            if actual != parquet_sha:
                errors.append("fit split parquet on-disk SHA-256 does not match manifest")

    if errors:
        raise MappingManifestError("; ".join(errors))
    return manifest
