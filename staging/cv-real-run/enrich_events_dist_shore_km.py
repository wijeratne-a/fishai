#!/usr/bin/env python3
"""Add dist_shore_km to local cufes_events.parquet (track midpoint to pilot shoreline)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PR28 = Path("/tmp/fishai-pr28")
sys.path.insert(0, str(PR28 / "src"))

from fishai.ingestion.physics.coast_distance import distance_to_shoreline_km, shoreline_path_from_config
def _midpoint_lat_lon(ev: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    lat0 = ev["lat"] if "lat" in ev.columns else ev["start_latitude"]
    lon0 = ev["lon"] if "lon" in ev.columns else ev["start_longitude"]
    lat1 = ev["stop_lat"] if "stop_lat" in ev.columns else ev["stop_latitude"]
    lon1 = ev["stop_lon"] if "stop_lon" in ev.columns else ev["stop_longitude"]
    return (lat0 + lat1) / 2.0, (lon0 + lon1) / 2.0


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    path = root / "data/processed/calcofi_cufes/cufes_events.parquet"
    ev = pd.read_parquet(path)
    if "dist_shore_km" in ev.columns and ev["dist_shore_km"].notna().all():
        print("dist_shore_km already present")
        return 0
    lat, lon = _midpoint_lat_lon(ev)
    shore = root / "data/reference/shoreline/ne_10m_land_pilot_clip.json"
    dist = distance_to_shoreline_km(lat, lon, geojson_path=shore)
    ev["dist_shore_km"] = dist
    ev.to_parquet(path, index=False)
    print(f"wrote dist_shore_km for {len(ev)} events; min={dist.min():.2f} max={dist.max():.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
