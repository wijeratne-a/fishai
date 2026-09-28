#!/usr/bin/env python3
"""Fail if tracked files exist under data/raw or data/processed, or if binary extensions are committed."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FORBIDDEN_PREFIXES = ("data/raw/", "data/processed/")
BINARY_SUFFIXES = (
    ".nc",
    ".parquet",
    ".zarr",
    ".h5",
    ".hdf5",
    ".tif",
    ".tiff",
)


def git_ls_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=REPO, text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]


def main() -> int:
    errors: list[str] = []
    for rel in git_ls_files():
        if rel.startswith(FORBIDDEN_PREFIXES):
            errors.append(f"forbidden_path:{rel}")
        lower = rel.lower()
        for suffix in BINARY_SUFFIXES:
            if lower.endswith(suffix) or f"{suffix}/" in lower:
                errors.append(f"forbidden_binary:{rel}")
                break
    if errors:
        for err in sorted(errors):
            print(err, file=sys.stderr)
        print(f"RESULT FAIL count={len(errors)}", file=sys.stderr)
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
