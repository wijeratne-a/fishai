#!/usr/bin/env python3
"""Download SWFSC CPS adult catch/specimen CSVs from the public NOAA GCS mirror (InPort).

Used when ERDDAP tabledap requests time out (HTTP 504). Source URLs are documented on
InPort item 20693; no credentials required.
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

GCS_BASE = "https://storage.googleapis.com/nmfs_odp_swfsc/Fisheries%20Resources%20Division"

ARTIFACTS: dict[str, tuple[str, Path]] = {
    "trawl_catch": (
        "CPS_Trawl_LifeHistory_HaulCatch.csv",
        REPO_ROOT / "data" / "raw" / "swfsc_cps_trawl_haul_catch" / "FRDCPSTrawlLHHaulCatch_2003.csv",
    ),
    "trawl_specimen": (
        "CPS_Trawl_LifeHistory_Specimen.csv",
        REPO_ROOT / "data" / "raw" / "swfsc_cps_trawl_haul_catch" / "specimens" / "FRDCPSTrawlLHSpecimen_gcs.csv",
    ),
    "nearshore_catch": (
        "CPS_Trawl_LifeHistory_Nearshore_SetCatch.csv",
        REPO_ROOT
        / "data"
        / "raw"
        / "swfsc_cps_nearshore_set_catch"
        / "cps_nearshore_set_catch_gcs.csv",
    ),
    "nearshore_specimen": (
        "CPS_Trawl_LifeHistory_Nearshore_Specimen.csv",
        REPO_ROOT
        / "data"
        / "raw"
        / "swfsc_cps_nearshore_set_catch"
        / "specimens"
        / "FRDCPSNearshoreSpecimen_gcs.csv",
    ),
}


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "fishai-adult-cps-gcs/0.1"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        dest.write_bytes(resp.read())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch adult CPS inputs from public NOAA GCS mirror")
    parser.add_argument(
        "--only",
        action="append",
        choices=sorted(ARTIFACTS),
        help="Download subset (default: all four tables)",
    )
    args = parser.parse_args(argv)
    keys = args.only or sorted(ARTIFACTS)
    for key in keys:
        name, dest = ARTIFACTS[key]
        url = f"{GCS_BASE}/{name}"
        print(f"download {name} -> {dest}")
        _download(url, dest)
        print(f"  bytes={dest.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
