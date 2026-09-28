#!/usr/bin/env python3
"""
Measure fidelity of the vendored pilot shoreline vs full-resolution Natural Earth.

Downloads ``ne_10m_land`` into ``data/raw/shoreline/`` (gitignored). Does not commit
full-resolution geometry under paths scanned by ``security/precommit_sensitive_scan``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
from pyproj import Geod

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from fishai.ingestion.physics.coast_distance import distance_to_shoreline_km
from fishai.ingestion.physics.shoreline_geo import (
    PILOT_CLIP_BBOX,
    clip_rings_to_bbox,
    label_rings,
    read_land_rings,
    rings_to_feature_collection,
    write_geojson,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import glorys_grid_from_config, load_overlap_config

GEOD = Geod(ellps="WGS84")
NE_URL = "https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip"
RAW_DIR = REPO / "data" / "raw" / "shoreline"
VENDORED = REPO / "data" / "reference" / "shoreline" / "ne_10m_land_pilot_clip.json"
REFERENCE_FLAGS = REPO / "tests" / "fixtures" / "shoreline_nearshore_flags_reference.csv"


def download_ne_land(dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / "ne_10m_land.zip"
    if not zip_path.is_file():
        print(f"Downloading {NE_URL} …")
        urllib.request.urlretrieve(NE_URL, zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest_dir)
    shp = dest_dir / "ne_10m_land.shp"
    if not shp.is_file():
        raise FileNotFoundError(f"missing shapefile under {dest_dir}")
    version_file = dest_dir / "ne_10m_land.VERSION.txt"
    version = version_file.read_text(encoding="utf-8").strip() if version_file.is_file() else "unknown"
    print(f"Natural Earth ne_10m_land version: {version}")
    return shp


def subsample_ring(ring: list[tuple[float, float]], max_pts: int) -> list[tuple[float, float]]:
    if len(ring) <= max_pts:
        return ring
    step = max(1, len(ring) // max_pts)
    out = ring[::step]
    if out[0] != out[-1]:
        out = out + [out[0]]
    return out


def densify_ring_geodesic(
    ring: list[tuple[float, float]],
    spacing_km: float,
) -> tuple[np.ndarray, np.ndarray]:
    lats: list[float] = []
    lons: list[float] = []
    for i in range(len(ring) - 1):
        lon1, lat1 = ring[i]
        lon2, lat2 = ring[i + 1]
        lons.append(lon1)
        lats.append(lat1)
        _, _, dist_m = GEOD.inv(lon1, lat1, lon2, lat2)
        steps = max(1, int(np.ceil((dist_m / 1000.0) / spacing_km)))
        az = GEOD.inv(lon1, lat1, lon2, lat2)[0]
        for step in range(1, steps):
            frac = step / steps
            lon_mid, lat_mid, _ = GEOD.fwd(lon1, lat1, az, dist_m * frac)
            lons.append(float(lon_mid))
            lats.append(float(lat_mid))
    return np.asarray(lats, dtype=float), np.asarray(lons, dtype=float)


def directed_hausdorff_km(
    lat_a: np.ndarray,
    lon_a: np.ndarray,
    lat_b: np.ndarray,
    lon_b: np.ndarray,
) -> float:
    if lat_a.size == 0 or lat_b.size == 0:
        return float("nan")
    worst = 0.0
    for la, lo in zip(lat_a, lon_a, strict=True):
        _, _, dist_m = GEOD.inv(
            np.full_like(lon_b, lo),
            np.full_like(lat_b, la),
            lon_b,
            lat_b,
        )
        worst = max(worst, float(np.min(dist_m)) / 1000.0)
    return worst


def symmetric_hausdorff_km(
    lat_a: np.ndarray,
    lon_a: np.ndarray,
    lat_b: np.ndarray,
    lon_b: np.ndarray,
) -> float:
    return max(
        directed_hausdorff_km(lat_a, lon_a, lat_b, lon_b),
        directed_hausdorff_km(lat_b, lon_b, lat_a, lon_a),
    )


def rings_from_geojson(path: Path) -> list[list[tuple[float, float]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rings: list[list[tuple[float, float]]] = []
    for feat in data.get("features", []):
        geom = feat.get("geometry") or {}
        if geom.get("type") == "Polygon":
            for lon, lat in geom["coordinates"][0]:
                pass
            ring = [(float(lon), float(lat)) for lon, lat in geom["coordinates"][0]]
            rings.append(ring)
    return rings


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_reference_flags(
    cfg: dict,
    full_geojson: Path,
    out_csv: Path,
) -> None:
    lat_dst, lon_dst = glorys_grid_from_config(cfg)
    lat2d, lon2d = np.meshgrid(lat_dst, lon_dst, indexing="ij")
    densify = float(cfg["shoreline"]["densify_spacing_km"])
    dist = distance_to_shoreline_km(lat2d, lon2d, geojson_path=full_geojson, densify_km=densify)
    near = (dist <= float(cfg["nearshore_km"])).astype(int)
    lines = ["lat,lon,nearshore"]
    for j in range(lat_dst.size):
        for i in range(lon_dst.size):
            lines.append(f"{lat_dst[j]:.8f},{lon_dst[i]:.8f},{near[j, i]}")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_csv.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-vertices", type=int, default=400, help="Per-polygon vertex cap for vendored export")
    parser.add_argument("--hausdorff-spacing-km", type=float, default=0.25)
    parser.add_argument("--write-vendored", action="store_true")
    parser.add_argument("--write-reference-flags", action="store_true")
    args = parser.parse_args()

    cfg = load_overlap_config()
    shp = download_ne_land(RAW_DIR)
    full_rings = clip_rings_to_bbox(read_land_rings(shp))
    full_fc = rings_to_feature_collection(full_rings)
    full_path = RAW_DIR / "ne_10m_land_pilot_clip_full.json"
    write_geojson(full_fc, full_path)
    print(f"Full-resolution clip: {full_path} ({full_path.stat().st_size} bytes, gitignored tree)")

    simplified_fc = rings_to_feature_collection(full_rings, max_vertices=args.max_vertices)
    simplified_path = RAW_DIR / "ne_10m_land_pilot_clip_simplified.json"
    write_geojson(simplified_fc, simplified_path)

    print("Computing Hausdorff metrics …")
    labeled_full = label_rings(full_rings)
    labeled_simp = label_rings(rings_from_geojson(simplified_path))

    hausdorff_rows: list[str] = []
    for name in sorted(set(labeled_full) | set(labeled_simp)):
        if name not in labeled_full or name not in labeled_simp:
            hausdorff_rows.append(f"{name}: missing in one geometry")
            continue
        ring_f = subsample_ring(labeled_full[name], max_pts=5000)
        ring_s = subsample_ring(labeled_simp[name], max_pts=5000)
        la_f = np.asarray([p[1] for p in ring_f], dtype=float)
        lo_f = np.asarray([p[0] for p in ring_f], dtype=float)
        la_s = np.asarray([p[1] for p in ring_s], dtype=float)
        lo_s = np.asarray([p[0] for p in ring_s], dtype=float)
        d_ab = directed_hausdorff_km(la_f, lo_f, la_s, lo_s)
        d_ba = directed_hausdorff_km(la_s, lo_s, la_f, lo_f)
        sym = symmetric_hausdorff_km(la_f, lo_f, la_s, lo_s)
        hausdorff_rows.append(
            f"{name}: directed_full→simp={d_ab:.4f} km, directed_simp→full={d_ba:.4f} km, symmetric={sym:.4f} km"
        )
        print(hausdorff_rows[-1])

    lat_dst, lon_dst = glorys_grid_from_config(cfg)
    lat2d, lon2d = np.meshgrid(lat_dst, lon_dst, indexing="ij")
    densify = float(cfg["shoreline"]["densify_spacing_km"])
    dist_full = distance_to_shoreline_km(lat2d, lon2d, geojson_path=full_path, densify_km=densify)
    if sha256_file(full_path) == sha256_file(VENDORED):
        dist_vend = dist_full
    else:
        dist_vend = distance_to_shoreline_km(lat2d, lon2d, geojson_path=VENDORED, densify_km=densify)
    dist_simp = distance_to_shoreline_km(lat2d, lon2d, geojson_path=simplified_path, densify_km=densify)
    diff_v = np.abs(dist_full - dist_vend)
    diff_simp = np.abs(dist_full - dist_simp)
    max_diff_v = float(np.nanmax(diff_v))
    max_diff_simp = float(np.nanmax(diff_simp))
    flag_full = dist_full <= float(cfg["nearshore_km"])
    flag_v = dist_vend <= float(cfg["nearshore_km"])
    flag_simp = dist_simp <= float(cfg["nearshore_km"])
    n_flag_diff_v = int(np.sum(flag_full != flag_v))
    n_flag_diff_simp = int(np.sum(flag_full != flag_simp))
    print(f"Vendored max |Δdistance| vs full: {max_diff_v:.4f} km; flag diffs: {n_flag_diff_v}")
    print(
        f"Simplified (max_vertices={args.max_vertices}) max |Δdistance| vs full: "
        f"{max_diff_simp:.4f} km; flag diffs: {n_flag_diff_simp}"
    )

    if args.write_vendored:
        write_geojson(simplified_fc, VENDORED)
        print(f"Wrote vendored {VENDORED} sha256={sha256_file(VENDORED)}")

    if args.write_reference_flags:
        write_reference_flags(cfg, full_path, REFERENCE_FLAGS)
        print(f"Wrote reference flags {REFERENCE_FLAGS}")

    report = {
        "simplification_method": "uniform_index_decimation",
        "max_vertices_per_polygon": args.max_vertices,
        "natural_earth_version": (RAW_DIR / "ne_10m_land.VERSION.txt").read_text(encoding="utf-8").strip(),
        "vendored_max_cell_distance_diff_km": max_diff_v,
        "vendored_nearshore_flag_differences": n_flag_diff_v,
        "simplified_max_cell_distance_diff_km": max_diff_simp,
        "simplified_nearshore_flag_differences": n_flag_diff_simp,
        "hausdorff": hausdorff_rows,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
