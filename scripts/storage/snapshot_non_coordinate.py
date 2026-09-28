#!/usr/bin/env python3
"""Snapshot code and non-coordinate metadata to an off-repo folder.

Does not copy data/raw, data/interim, data/restricted, or survey coordinates.
A backup is not claimed until restore_test.py compares SHA-256 hashes.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SNAPSHOT_ROOT = REPO_ROOT.parent / "fishai-offrepo-snapshots"

# Explicit allow-list. No raw survey tables. No restricted env extracts.
SNAPSHOT_PATHS = (
    "data/metadata/RESTORE_TEST_OBJECT.json",
    "data/metadata/noaa-rvc-erddap-metadata.csv",
    "data/manifests/source-licenses.csv",
    "data/manifests/structured-survey-manifest.csv",
    "data/manifests/acquisition-manifest.csv",
    "models/config/MODEL_EXPERIMENT_SCHEMA.json",
    "models/config/EXPERIMENT_TEMPLATE.yaml",
    "models/config/CONFIGURATION_RULES.md",
    "science/time/TEMPORAL_INTEGRITY_RULES.md",
    "science/measurements/MEASUREMENT_SEMANTICS.md",
    "labels/LABEL_VALIDATION_RULES.yaml",
    "reproducibility/MINIMUM_RUN_MANIFEST.json",
    "docs/BACKUP_AND_RECOVERY.md",
    "scripts/storage/verify_checksums.py",
    "scripts/validation/validate_acquired_file.py",
    "scripts/validation/validate_atlantic_frames.py",
    "tests/measurements/test_units.py",
    "tests/models/config/test_config_rules.py",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_root() -> Path:
    return Path(
        __import__("os").environ.get("FISHAI_SNAPSHOT_ROOT", str(DEFAULT_SNAPSHOT_ROOT))
    )


def run_snapshot() -> dict:
    dest_root = snapshot_root()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = dest_root / stamp
    dest.mkdir(parents=True, exist_ok=True)

    files: list[dict] = []
    missing: list[str] = []
    for rel in SNAPSHOT_PATHS:
        src = REPO_ROOT / rel
        if not src.is_file():
            missing.append(rel)
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        files.append(
            {
                "path": rel,
                "sha256": sha256_file(src),
                "bytes": src.stat().st_size,
            }
        )

    manifest = {
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_repo": str(REPO_ROOT),
        "snapshot_dir": str(dest),
        "contains_survey_coordinates": False,
        "contains_raw_survey_bytes": False,
        "file_count": len(files),
        "missing": missing,
        "files": files,
    }
    (dest / "SNAPSHOT_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    latest = dest_root / "LATEST"
    if latest.exists() or latest.is_symlink():
        latest.unlink()
    latest.symlink_to(dest)
    return manifest


def main() -> int:
    manifest = run_snapshot()
    print(f"snapshot_dir={manifest['snapshot_dir']}")
    print(f"file_count={manifest['file_count']}")
    print(f"missing={len(manifest['missing'])}")
    print("contains_survey_coordinates=False")
    return 0 if manifest["file_count"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
