#!/usr/bin/env python3
"""Fail if tracked files violate data/binary commit policy."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FORBIDDEN_PREFIXES = ("data/raw/", "data/processed/")
FORBIDDEN_DATA_CSV_PREFIX = "data/"
# Blessed WCOFS h grid. sha256 d5c936303f80be39a3f78dcb9257197150d29c7f079358cacc3ac4cf7edf49e9
ALLOWED_ZARR_PREFIX = "data/derived/physics/wcofs_h_glorys_pilot.zarr/"
BINARY_SUFFIXES = (
    ".nc",
    ".parquet",
    ".zarr",
    ".h5",
    ".hdf5",
    ".tif",
    ".tiff",
    ".gpkg",
    ".geojson",
    ".shp",
    ".shx",
    ".dbf",
    ".prj",
    ".cpg",
    ".grib",
    ".grib2",
    ".grb",
    ".grb2",
    ".rds",
    ".rdata",
    ".feather",
    ".pkl",
    ".pickle",
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
        if lower.startswith(ALLOWED_ZARR_PREFIX):
            continue
        if lower.startswith(FORBIDDEN_DATA_CSV_PREFIX) and lower.endswith(".csv"):
            errors.append(f"forbidden_data_csv:{rel}")
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
