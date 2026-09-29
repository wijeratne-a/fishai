#!/usr/bin/env python3
"""Add dist_shore_km to local cufes_events.parquet (staging dry-run; subsampled shoreline)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Geod

GEOD = Geod(ellps="WGS84")
VERTEX_STRIDE = 25


def _coast_vertices(geojson_path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = json.loads(geojson_path.read_text(encoding="utf-8"))
    lats: list[float] = []
    lons: list[float] = []
    for feature in data.get("features", []):
        geom = feature.get("geometry") or {}
        rings: list = []
        if geom.get("type") == "Polygon":
            rings = [geom.get("coordinates", [[[]]])[0]]
        elif geom.get("type") == "MultiPolygon":
            rings = [poly[0] for poly in geom.get("coordinates", []) if poly]
        for ring in rings:
            for i in range(0, max(0, len(ring) - 1), VERTEX_STRIDE):
                lon, lat = ring[i][:2]
                lons.append(float(lon))
                lats.append(float(lat))
    return np.asarray(lats, dtype=float), np.asarray(lons, dtype=float)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    path = root / "data/processed/calcofi_cufes/cufes_events.parquet"
    ev = pd.read_parquet(path)
    if "dist_shore_km" in ev.columns and ev["dist_shore_km"].notna().all():
        print("dist_shore_km already present")
        return 0
    shore = root / "data/reference/shoreline/ne_10m_land_pilot_clip.json"
    clat, clon = _coast_vertices(shore)
    plat = (ev["lat"] + ev["stop_lat"]) / 2.0
    plon = (ev["lon"] + ev["stop_lon"]) / 2.0
    out = np.empty(len(ev), dtype=float)
    for i, (la, lo) in enumerate(zip(plat.to_numpy(), plon.to_numpy())):
        _, _, dm = GEOD.inv(np.full(clon.size, lo), np.full(clat.size, la), clon, clat)
        out[i] = float(np.min(dm)) / 1000.0
    ev["dist_shore_km"] = out
    ev.to_parquet(path, index=False)
    print(f"wrote dist_shore_km for {len(ev)} events; min={out.min():.2f} max={out.max():.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
