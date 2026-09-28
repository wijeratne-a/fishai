"""Distance to a simplified pilot coastline (committed fixture vertices)."""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

import numpy as np

from fishai.ingestion.physics.geo_distance import haversine_km
from fishai.ingestion.sources import REPO_ROOT

DEFAULT_COASTLINE_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "pilot_coastline_vertices.csv"


@lru_cache(maxsize=4)
def load_coastline_vertices(path: str) -> tuple[np.ndarray, np.ndarray]:
    fixture = Path(path)
    lats: list[float] = []
    lons: list[float] = []
    with fixture.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            lats.append(float(row["lat"]))
            lons.append(float(row["lon"]))
    return np.asarray(lats, dtype=float), np.asarray(lons, dtype=float)


def distance_to_coast_km(
    lat: np.ndarray,
    lon: np.ndarray,
    *,
    coastline_fixture: Path | str = DEFAULT_COASTLINE_FIXTURE,
) -> np.ndarray:
    """
    Minimum great-circle distance (km) from each point to the coastline polyline.

    Uses vertex-to-vertex segments from ``coastline_fixture`` (same geometry as the
    pilot distance regression fixture family).
    """
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    coast_lat, coast_lon = load_coastline_vertices(str(coastline_fixture))
    if coast_lat.size < 2:
        return np.full(lat.shape, np.nan, dtype=float)

    flat_lat = lat.ravel()
    flat_lon = lon.ravel()
    out = np.empty(flat_lat.size, dtype=float)
    for idx, (la, lo) in enumerate(zip(flat_lat, flat_lon, strict=True)):
        best = float("inf")
        for j in range(len(coast_lat) - 1):
            for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
                cla = coast_lat[j] + frac * (coast_lat[j + 1] - coast_lat[j])
                clo = coast_lon[j] + frac * (coast_lon[j + 1] - coast_lon[j])
                best = min(best, haversine_km(la, lo, cla, clo))
        out[idx] = best
    return out.reshape(lat.shape)
