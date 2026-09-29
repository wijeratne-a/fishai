"""Geodesic distance to shoreline polygons (Natural Earth production; fixture in tests)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from pyproj import Geod

from fishai.ingestion.sources import REPO_ROOT

GEOD = Geod(ellps="WGS84")
DEFAULT_DENSIFY_KM = 1.0


@lru_cache(maxsize=4)
def _densified_boundary_vertices(geojson_path: str, densify_km: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Densify polygon exteriors to <= ``densify_km`` spacing using pyproj Geod forward.

    Distance is the minimum geodesic distance from each query point to any densified
    vertex (WGS84 ellipsoid).
    """
    path = Path(geojson_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    lats: list[float] = []
    lons: list[float] = []
    for feature in data.get("features", []):
        geom = feature.get("geometry") or {}
        gtype = geom.get("type")
        coords = geom.get("coordinates") or []
        rings: list[list[list[float]]] = []
        if gtype == "Polygon":
            rings = [coords[0]] if coords else []
        elif gtype == "MultiPolygon":
            rings = [poly[0] for poly in coords if poly]
        for ring in rings:
            if len(ring) < 2:
                continue
            for i in range(len(ring) - 1):
                lon1, lat1 = float(ring[i][0]), float(ring[i][1])
                lon2, lat2 = float(ring[i + 1][0]), float(ring[i + 1][1])
                lons.append(lon1)
                lats.append(lat1)
                _, _, dist_m = GEOD.inv(lon1, lat1, lon2, lat2)
                steps = max(1, int(np.ceil((dist_m / 1000.0) / densify_km)))
                for step in range(1, steps):
                    frac = step / steps
                    lon_mid, lat_mid, _ = GEOD.fwd(lon1, lat1, GEOD.inv(lon1, lat1, lon2, lat2)[0], dist_m * frac)
                    lons.append(float(lon_mid))
                    lats.append(float(lat_mid))
    return np.asarray(lats, dtype=float), np.asarray(lons, dtype=float)


def shoreline_path_from_config(config: dict[str, Any]) -> Path:
    rel = config.get("shoreline", {}).get("path") or "data/reference/shoreline/ne_10m_land_pilot_clip.geojson"
    path = Path(rel)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _min_distance_to_coast_vertices_km(
    lat: np.ndarray,
    lon: np.ndarray,
    coast_lat: np.ndarray,
    coast_lon: np.ndarray,
    *,
    chunk: int = 8000,
    point_batch: int = 512,
) -> np.ndarray:
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    flat_lat = lat.ravel()
    flat_lon = lon.ravel()
    out = np.empty(flat_lat.size, dtype=float)
    if coast_lat.size == 0:
        out.fill(np.nan)
        return out.reshape(lat.shape)
    n_coast = coast_lat.size
    for p0 in range(0, flat_lat.size, point_batch):
        p1 = min(p0 + point_batch, flat_lat.size)
        plat = flat_lat[p0:p1]
        plon = flat_lon[p0:p1]
        best_m = np.full(p1 - p0, np.inf, dtype=float)
        for start in range(0, n_coast, chunk):
            end = min(start + chunk, n_coast)
            clon = coast_lon[start:end]
            clat = coast_lat[start:end]
            nc = end - start
            pp = p1 - p0
            _, _, dist_m = GEOD.inv(
                np.repeat(plon, nc),
                np.repeat(plat, nc),
                np.tile(clon, pp),
                np.tile(clat, pp),
            )
            dist_m = dist_m.reshape(pp, nc)
            best_m = np.minimum(best_m, np.min(dist_m, axis=1))
        out[p0:p1] = best_m / 1000.0
    return out.reshape(lat.shape)


def distance_to_shoreline_km(
    lat: np.ndarray,
    lon: np.ndarray,
    *,
    geojson_path: Path | str,
    densify_km: float = DEFAULT_DENSIFY_KM,
) -> np.ndarray:
    """Minimum geodesic distance (km) from each point to the land boundary."""
    coast_lat, coast_lon = _densified_boundary_vertices(str(geojson_path), float(densify_km))
    return _min_distance_to_coast_vertices_km(lat, lon, coast_lat, coast_lon)


def nearshore_mask(
    lat: np.ndarray,
    lon: np.ndarray,
    *,
    config: dict[str, Any],
) -> np.ndarray:
    shore = shoreline_path_from_config(config)
    densify = float(config.get("shoreline", {}).get("densify_spacing_km", DEFAULT_DENSIFY_KM))
    dist_km = distance_to_shoreline_km(lat, lon, geojson_path=shore, densify_km=densify)
    return dist_km <= float(config["nearshore_km"])
