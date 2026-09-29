#!/usr/bin/env python3
"""Export WCOFS ROMS h onto the GLORYS pilot grid (bot2 / PR #28 parity)."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--cycle-date",
        default="2025-06-01",
        help="WCOFS fields cycle date (matches evidence manifest example)",
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))

    from fishai.ingestion.physics.sources.wcofs import fetch_cycle
    from fishai.ingestion.physics.wcofs_h_glorys_store import export_wcofs_h_glorys_grid
    from fishai.ingestion.sources import load_sources_manifest

    manifest = load_sources_manifest(root / "data" / "SOURCES.yaml")
    pilot = manifest.get("pilot") or {}
    bbox = pilot.get("bbox") or {}
    lat_min, lat_max = float(bbox["lat_min"]), float(bbox["lat_max"])
    lon_min, lon_max = float(bbox["lon_min"]), float(bbox["lon_max"])
    cycle = dt.date.fromisoformat(args.cycle_date)
    ds = fetch_cycle(cycle, ("n003",), (lat_min, lat_max, lon_min, lon_max))
    s3_key = str(ds.attrs.get("wcofs_s3_key", ""))
    export_wcofs_h_glorys_grid(
        ds,
        source_file=s3_key,
        artifact_path=args.artifact,
        manifest_path=args.manifest,
    )
    print(f"wrote artifact={args.artifact} manifest={args.manifest}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
