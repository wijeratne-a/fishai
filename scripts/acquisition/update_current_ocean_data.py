#!/usr/bin/env python3
"""Refresh a small current MUR SST snippet. Not a species nowcast."""

from __future__ import annotations

import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
URL = (
    "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.csv"
    "?analysed_sst[(last)][(24.60):(24.61)][(-81.50):(-81.49)]"
)


def main() -> None:
    day = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    dest = ROOT / "data" / "raw" / "environmental" / "coastwatch" / "jplMURSST41" / day / "latest-snippet.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(URL, headers={"User-Agent": "FishAI-internal-research/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, dest.open("wb") as handle:
        handle.write(response.read())
    print(f"wrote {dest.relative_to(ROOT)} bytes={dest.stat().st_size}")


if __name__ == "__main__":
    main()
