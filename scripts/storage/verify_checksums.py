#!/usr/bin/env python3
"""Verify SHA-256 of files listed in acquisition and structured-survey manifests.

Prints ok / missing / mismatch counts only.
"""

from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

MANIFESTS = (
    REPO_ROOT / "data/manifests/acquisition-manifest.csv",
    REPO_ROOT / "data/manifests/structured-survey-manifest.csv",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest(manifest: Path) -> tuple[int, int, int]:
    ok = missing = mismatch = 0
    with manifest.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or "path" not in reader.fieldnames or "sha256" not in reader.fieldnames:
            return ok, missing, mismatch
        for row in reader:
            rel = (row.get("path") or "").strip()
            expected = (row.get("sha256") or "").strip().lower()
            if not rel or not expected:
                continue
            path = REPO_ROOT / rel
            if not path.is_file():
                missing += 1
                continue
            actual = sha256_file(path).lower()
            if actual == expected:
                ok += 1
            else:
                mismatch += 1
    return ok, missing, mismatch


def main() -> int:
    total_ok = total_missing = total_mismatch = 0
    found_any = False
    for manifest in MANIFESTS:
        if not manifest.is_file():
            continue
        found_any = True
        ok, missing, mismatch = verify_manifest(manifest)
        total_ok += ok
        total_missing += missing
        total_mismatch += mismatch

    if not found_any:
        print("ok=0 missing=0 mismatch=0")
        return 0

    print(f"ok={total_ok} missing={total_missing} mismatch={total_mismatch}")
    return 0 if total_missing == 0 and total_mismatch == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
