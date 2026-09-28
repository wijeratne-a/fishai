"""Mapping manifest verification tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fishai.scoring.harmonization.manifest import MappingManifestError, verify_mapping_manifest


def test_manifest_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(MappingManifestError, match="manifest missing"):
        verify_mapping_manifest(tmp_path, expected_prereg_commit="abc")


def test_manifest_hash_mismatch(tmp_path: Path) -> None:
    manifest = {
        "fitting_commit_sha": "fit123",
        "prereg_commit_sha": "wrong",
        "fit_split_parquet_sha256": "deadbeef",
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(MappingManifestError, match="prereg_commit_sha mismatch"):
        verify_mapping_manifest(tmp_path, expected_prereg_commit="expected")
