#!/usr/bin/env python3
"""Download public SWFSC ODP bulk CSVs (GCS mirror of InPort distributions)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ODP_BASE = "https://storage.googleapis.com/nmfs_odp_swfsc/Fisheries%20Resources%20Division"

FILES: tuple[tuple[str, Path], ...] = (
    ("CPS_Trawl_LifeHistory_HaulCatch.csv", REPO_ROOT / "data/raw/swfsc_cps_trawl_haul_catch/CPS_Trawl_LifeHistory_HaulCatch.csv"),
    (
        "CPS_Trawl_LifeHistory_Nearshore_SetCatch.csv",
        REPO_ROOT / "data/raw/swfsc_cps_nearshore_set_catch/CPS_Trawl_LifeHistory_Nearshore_SetCatch.csv",
    ),
    (
        "CPS_Trawl_LifeHistory_Specimen.csv",
        REPO_ROOT / "data/raw/swfsc_cps_trawl_haul_catch/specimens/CPS_Trawl_LifeHistory_Specimen.csv",
    ),
    (
        "CPS_Trawl_LifeHistory_Nearshore_Specimen.csv",
        REPO_ROOT / "data/raw/swfsc_cps_nearshore_set_catch/specimens/CPS_Trawl_LifeHistory_Nearshore_Specimen.csv",
    ),
)


def main() -> int:
    for name, dest in FILES:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_file() and dest.stat().st_size > 0:
            print(f"skip existing {dest.name}")
            continue
        url = f"{ODP_BASE}/{name}"
        print(f"download {name} -> {dest}")
        rc = subprocess.call(["curl", "-fsSL", "-o", str(dest), url])
        if rc != 0:
            return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
