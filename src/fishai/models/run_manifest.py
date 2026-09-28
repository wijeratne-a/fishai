#!/usr/bin/env python3
"""Write a minimum run manifest. Does not authorize publication."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
REQUIRED = (
    "experiment_id",
    "random_seed",
    "train_years",
    "holdout_year",
    "code_version",
    "input_checksums",
    "publish_status",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def build_manifest(
    *,
    experiment_id: str,
    random_seed: int,
    train_years: list[int],
    holdout_year: int,
    input_paths: list[Path] | None = None,
    notes: str = "synthetic",
) -> dict[str, Any]:
    checksums = {}
    for path in input_paths or []:
        if path.is_file():
            checksums[path.name] = sha256_file(path)
    commit = git_commit()
    return {
        "manifest_version": "1.1",
        "experiment_id": experiment_id,
        "random_seed": random_seed,
        "train_years": list(train_years),
        "holdout_year": holdout_year,
        "code_version": commit or "GIT_UNAVAILABLE",
        "git_commit_of_fit": commit,
        "input_checksums": checksums,
        "publish_status": "NOT_PUBLISHED",
        "utc_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": notes,
    }


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED:
        if field not in manifest or manifest[field] in (None, "", []):
            errors.append(f"missing:{field}")
    if manifest.get("publish_status") != "NOT_PUBLISHED":
        errors.append("publish_status_must_be_NOT_PUBLISHED")
    holdout = manifest.get("holdout_year")
    if holdout in (manifest.get("train_years") or []):
        errors.append("holdout_in_train_years")
    return errors


def write_manifest(dest: Path, manifest: dict[str, Any]) -> Path:
    errors = validate_manifest(manifest)
    if errors:
        raise ValueError(f"invalid run manifest: {errors}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return dest


def main() -> int:
    dest = REPO_ROOT / "data" / "processed" / "manifests" / "SYNTHETIC_RUN_MANIFEST.json"
    manifest = build_manifest(
        experiment_id="syn_frozen_protocol_1",
        random_seed=20260926,
        train_years=[2016, 2019, 2021],
        holdout_year=2023,
        notes="Synthetic protocol test. No real-species fit.",
    )
    write_manifest(dest, manifest)
    print(f"wrote={dest.relative_to(REPO_ROOT)}")
    print("publish_status=NOT_PUBLISHED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
