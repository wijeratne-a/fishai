#!/usr/bin/env python3
"""Restore one metadata file and one non-coordinate test object; compare SHA-256.

Writes audit/storage/RESTORE_VERIFICATION.md and RESTORE_RESULTS.csv.
Does not copy survey coordinates. Does not claim backup unless checksums match.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from snapshot_non_coordinate import (
    DEFAULT_SNAPSHOT_ROOT,
    snapshot_root,
    run_snapshot,
    sha256_file,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "audit" / "storage"

METADATA_REL = "data/metadata/noaa-rvc-erddap-metadata.csv"
TEST_OBJECT_REL = "data/metadata/RESTORE_TEST_OBJECT.json"


def restore_one(snapshot_dir: Path, rel: str, restore_dir: Path) -> dict:
    src = snapshot_dir / rel
    dest = restore_dir / Path(rel).name
    original = REPO_ROOT / rel
    result = {
        "check_id": "",
        "path": rel,
        "snapshot_present": src.is_file(),
        "original_present": original.is_file(),
        "sha256_original": "",
        "sha256_restored": "",
        "result": "FAIL",
        "detail": "",
    }
    if not src.is_file():
        result["detail"] = "snapshot_file_missing"
        return result
    if not original.is_file():
        result["detail"] = "original_file_missing"
        return result
    restore_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    orig_hash = sha256_file(original)
    rest_hash = sha256_file(dest)
    result["sha256_original"] = orig_hash
    result["sha256_restored"] = rest_hash
    if orig_hash == rest_hash:
        result["result"] = "PASS"
        result["detail"] = "sha256_match"
    else:
        result["detail"] = "sha256_mismatch"
    return result


def write_report(rows: list[dict], snapshot_dir: str, overall: str) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    csv_path = AUDIT_DIR / "RESTORE_RESULTS.csv"
    fields = [
        "check_id",
        "check_name",
        "result",
        "detail",
        "sha256_original",
        "sha256_restored",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "check_id": row["check_id"],
                    "check_name": row["check_name"],
                    "result": row["result"],
                    "detail": row["detail"],
                    "sha256_original": row.get("sha256_original", ""),
                    "sha256_restored": row.get("sha256_restored", ""),
                }
            )

    claim = "BACKUP_VERIFIED" if overall == "PASS" else "BACKUP_NOT_CLAIMED"
    md = AUDIT_DIR / "RESTORE_VERIFICATION.md"
    md.write_text(
        "\n".join(
            [
                "# Restore verification",
                "",
                f"**As of:** {stamp}",
                f"**Status:** `{overall}`",
                f"**Claim:** `{claim}`",
                "",
                "## Findings",
                "",
                "| Item | Value |",
                "|---|---|",
                f"| Separate backup location | `{snapshot_dir}` |",
                f"| Last restore result | `{overall}` |",
                f"| Claim allowed | **{'yes' if overall == 'PASS' else 'no'}** |",
                "| Raw survey copy performed | **no** |",
                "| Coordinates in this report | **no** |",
                "",
                "## Restored objects",
                "",
                "| Object | Result | Detail |",
                "|---|---|---|",
                *[
                    f"| `{row['path']}` | `{row['result']}` | {row['detail']} |"
                    for row in rows
                    if row.get("path")
                ],
                "",
                "## Policy",
                "",
                "Git ignore of `data/raw/` is isolation, not a backup.",
                "A backup is claimed only after an off-repo restore checksum matches.",
                "Survey coordinates were not copied into Git or this report.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    manifest = run_snapshot()
    snapshot_dir = Path(manifest["snapshot_dir"])
    restore_dir = snapshot_dir.parent / "restore-scratch" / snapshot_dir.name
    if restore_dir.exists():
        shutil.rmtree(restore_dir)
    restore_dir.mkdir(parents=True, exist_ok=True)

    meta = restore_one(snapshot_dir, METADATA_REL, restore_dir / "metadata")
    meta["check_id"] = "RV-010"
    meta["check_name"] = "restore_metadata_file_sha256"
    meta["path"] = METADATA_REL

    obj = restore_one(snapshot_dir, TEST_OBJECT_REL, restore_dir / "test-object")
    obj["check_id"] = "RV-011"
    obj["check_name"] = "restore_non_coordinate_test_object_sha256"
    obj["path"] = TEST_OBJECT_REL

    location_ok = snapshot_dir.is_dir() and (
        str(snapshot_dir).startswith(str(DEFAULT_SNAPSHOT_ROOT))
        or str(snapshot_dir).startswith(str(snapshot_root()))
    )
    loc_row = {
        "check_id": "RV-001",
        "check_name": "separate_backup_location_documented",
        "result": "PASS" if location_ok else "FAIL",
        "detail": str(snapshot_dir),
        "path": "",
        "sha256_original": "",
        "sha256_restored": "",
    }
    raw_row = {
        "check_id": "RV-004",
        "check_name": "raw_survey_copy_this_run",
        "result": "NOT_PERFORMED",
        "detail": "Raw survey files were not copied",
        "path": "",
        "sha256_original": "",
        "sha256_restored": "",
    }

    matched = meta["result"] == "PASS" and obj["result"] == "PASS"
    overall = "PASS" if matched and location_ok else "FAIL"
    overall_row = {
        "check_id": "RV-005",
        "check_name": "overall_status",
        "result": overall,
        "detail": "Restore checksum match" if matched else "Restore checksum failed",
        "path": "",
        "sha256_original": "",
        "sha256_restored": "",
    }
    claim_row = {
        "check_id": "RV-003",
        "check_name": "backup_verified_claim",
        "result": "BACKUP_VERIFIED" if overall == "PASS" else "BACKUP_NOT_CLAIMED",
        "detail": "Claimed only after SHA-256 restore match",
        "path": "",
        "sha256_original": "",
        "sha256_restored": "",
    }

    rows = [loc_row, meta, obj, raw_row, claim_row, overall_row]
    write_report(rows, str(snapshot_dir), overall)

    docs = REPO_ROOT / "docs" / "BACKUP_AND_RECOVERY.md"
    docs.write_text(
        "\n".join(
            [
                "# Backup and recovery",
                "",
                "## Policy",
                "",
                "A backup is **not** claimed until a restore test succeeds. Git ignore of `data/raw/` isolates raw bytes from the repository; that isolation is **not** a backup.",
                "",
                "## Current state",
                "",
                "| Item | Value |",
                "|------|-------|",
                f"| Last restore result | `{overall}` |",
                f"| Last successful backup | `{'claimed after restore checksum match' if overall == 'PASS' else 'none claimed'}` |",
                "| Restore test script | `scripts/storage/restore_test.py` |",
                f"| Off-repo snapshot | `{snapshot_dir}` |",
                "",
                "## Procedure",
                "",
                "1. Snapshot non-coordinate files with `scripts/storage/snapshot_non_coordinate.py`.",
                "2. Restore one metadata file and one non-coordinate test object.",
                "3. Compare SHA-256 to the working copies.",
                "4. Record `PASS` or `FAIL` in `audit/storage/`.",
                "",
                "Survey coordinates are not copied into Git or the snapshot allow-list.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"overall={overall}")
    print(f"metadata={meta['result']}")
    print(f"test_object={obj['result']}")
    print(f"snapshot_dir={snapshot_dir}")
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
