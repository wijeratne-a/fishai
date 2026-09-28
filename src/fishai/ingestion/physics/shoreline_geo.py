"""Natural Earth land clip, simplification, and GeoJSON helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import shapefile

PILOT_CLIP_BBOX = (-122.0, 31.0, -116.0, 36.0)  # min_lon, min_lat, max_lon, max_lat

# Approximate centroids for Channel Islands naming in fidelity reports.
CHANNEL_ISLAND_CENTROIDS: dict[str, tuple[float, float]] = {
    "san_miguel": (34.05, -120.40),
    "santa_rosa": (33.98, -120.10),
    "santa_cruz": (34.00, -119.65),
    "anacapa": (34.01, -119.36),
    "santa_barbara": (33.48, -119.92),
    "san_nicolas": (33.25, -119.50),
    "santa_catalina": (33.40, -118.42),
    "san_clemente": (32.90, -118.50),
}


def bbox_intersects_ring(ring: list[tuple[float, float]], bbox: tuple[float, float, float, float]) -> bool:
    min_lon, min_lat, max_lon, max_lat = bbox
    lons = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    return not (
        max(lons) < min_lon
        or min(lons) > max_lon
        or max(lats) < min_lat
        or min(lats) > max_lat
    )


def read_land_rings(shape_path: Path) -> list[list[tuple[float, float]]]:
    reader = shapefile.Reader(str(shape_path))
    rings: list[list[tuple[float, float]]] = []
    for shp in reader.shapes():
        parts = list(shp.parts) + [len(shp.points)]
        for p0, p1 in zip(parts[:-1], parts[1:], strict=True):
            ring = [(float(x), float(y)) for x, y in shp.points[p0:p1]]
            if len(ring) >= 3:
                rings.append(ring)
    return rings


def clip_rings_to_bbox(
    rings: Iterable[list[tuple[float, float]]],
    bbox: tuple[float, float, float, float] = PILOT_CLIP_BBOX,
) -> list[list[tuple[float, float]]]:
    out: list[list[tuple[float, float]]] = []
    for ring in rings:
        if bbox_intersects_ring(ring, bbox):
            out.append(ring)
    return out


def decimate_ring(
    ring: list[tuple[float, float]],
    *,
    max_vertices: int,
) -> list[tuple[float, float]]:
    """
    Uniform index decimation (every *n*th vertex) preserving ring closure.

    This is the vendored simplification method (not Douglas–Peucker); ``max_vertices``
    is the per-polygon cap applied at export time.
    """
    if len(ring) <= max_vertices:
        coords = [[lon, lat] for lon, lat in ring]
    else:
        step = max(1, len(ring) // max_vertices)
        sampled = ring[::step]
        coords = [[lon, lat] for lon, lat in sampled]
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords


def rings_to_feature_collection(
    rings: list[list[tuple[float, float]]],
    *,
    max_vertices: int | None = None,
) -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    for ring in rings:
        lonlat = ring if max_vertices is None else decimate_ring(ring, max_vertices=max_vertices)
        if isinstance(lonlat[0], tuple):
            lonlat = [[p[0], p[1]] for p in lonlat]
        features.append(
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "Polygon", "coordinates": [lonlat]},
            }
        )
    return {"type": "FeatureCollection", "features": features}


def write_geojson(fc: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fc), encoding="utf-8")


def ring_centroid(ring: list[tuple[float, float]]) -> tuple[float, float]:
    lons = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    return float(sum(lats) / len(lats)), float(sum(lons) / len(lons))


def ring_area_deg2(ring: list[tuple[float, float]]) -> float:
    """Shoelace area in degree² (naming/ordering only)."""
    area = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def name_ring(ring: list[tuple[float, float]]) -> str:
    la, lo = ring_centroid(ring)
    best_name = "mainland"
    best_dist = float("inf")
    for name, (cla, clo) in CHANNEL_ISLAND_CENTROIDS.items():
        dist = (la - cla) ** 2 + (lo - clo) ** 2
        if dist < best_dist:
            best_dist = dist
            best_name = name
    if best_dist > 0.25:  # ~0.5° — not a known island centroid
        return "mainland"
    return best_name


def label_rings(rings: list[list[tuple[float, float]]]) -> dict[str, list[tuple[float, float]]]:
    """Group rings by mainland vs named island (largest ring → mainland if unlabeled)."""
    labeled: dict[str, list[tuple[float, float]]] = {}
    areas = sorted(((ring_area_deg2(r), r) for r in rings), reverse=True)
    for area, ring in areas:
        name = name_ring(ring)
        if name != "mainland":
            key = name
        else:
            key = "mainland" if "mainland" not in labeled else f"mainland_{len(labeled)}"
        labeled[key] = ring
    if "mainland" not in labeled and areas:
        labeled["mainland"] = areas[0][1]
    return labeled
