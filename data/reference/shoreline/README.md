# Pilot shoreline reference (Natural Earth)

## Source

- **Dataset:** [Natural Earth](https://www.naturalearthdata.com/) `ne_10m_land` (10m physical vectors)
- **Download URL:** https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/
- **Version:** 5.1.1 (from `ne_10m_land.VERSION.txt` in the upstream zip)
- **License:** Public domain ([Natural Earth terms of use](https://www.naturalearthdata.com/about/terms-of-use/))

## Vendored file

| File | Description |
|------|-------------|
| `ne_10m_land_pilot_clip.json` | GeoJSON land polygons intersecting the clip box (`.json` extension for CI policy) |

**Clip box (WGS84):** latitude 31°N–36°N, longitude 122°W–116°W (includes the Southern California Bight pilot and Channel Islands).

**SHA-256 (`ne_10m_land_pilot_clip.json`):** `2f677a16aa6c8470846d813eda6d82f2656dea2d697b1511a4c878542d20996c`

### Simplification (production)

- **Method:** `none_bbox_clip_only` — all Natural Earth vertices are retained after intersecting the clip box; no Douglas–Peucker or decimation.
- **Tolerance / cap:** none (`simplification_max_vertices_per_polygon: null` in `data/config/wcofs_glorys_overlap.yaml`).

Earlier revisions used **uniform index decimation** (`max_vertices_per_polygon=400`), which broke nearshore flags; fidelity work (below) replaced that with the full clip. The coordinate scan reads the full file under `data/reference/shoreline/` (see `security/precommit_sensitive_scan.py`).

Full-resolution clip for reproducibility is written to **`data/raw/shoreline/`** (gitignored) by `scripts/shoreline_fidelity.py`.

## Fidelity report (2026-09-28)

Reproduce:

```bash
python scripts/shoreline_fidelity.py --max-vertices 400
```

Hausdorff distances (km, geodesic, vertex subsample ≤5000 per polygon) between **full** clip and **400-vertex decimated** trial:

| Region | Directed full→simp | Directed simp→full | Symmetric |
|--------|-------------------:|-------------------:|----------:|
| mainland | 358.35 | 39.80 | 358.35 |
| santa_catalina | 0.00 | 0.00 | 0.00 |
| san_clemente | 0.00 | 0.00 | 0.00 |
| san_nicolas | 0.00 | 0.00 | 0.00 |
| san_miguel | 0.00 | 0.00 | 0.00 |
| santa_rosa | 0.00 | 0.00 | 0.00 |
| santa_cruz | 0.00 | 0.00 | 0.00 |
| anacapa | 0.00 | 0.00 | 0.00 |

GLORYS pilot grid (1/12°, 37×49 cells), 20 km nearshore cutoff, 1 km boundary densification (`pyproj.Geod`):

| Geometry | Max \|Δ shore distance\| vs full | Nearshore flag mismatches |
|----------|----------------------------------|---------------------------|
| **Vendored (full clip)** | **0.00 km** | **0** |
| Decimated trial (400 verts) | 44.64 km | 211 |

Reference nearshore flags from full resolution: `tests/fixtures/shoreline_nearshore_flags_reference.csv` (checked in CI).

## Distance method

Production `nearshore` flags use **geodesic** distance on WGS84 (`pyproj.Geod`, ellipsoid WGS84) from each GLORYS cell centre to the nearest point on densified land-polygon boundaries (vertices spaced at ≤ 1 km along each edge). Configured in `data/config/wcofs_glorys_overlap.yaml` under `shoreline.distance_method: pyproj_geod_fwd`.

Unit tests may use the simplified polyline at `tests/fixtures/pilot_coastline_vertices.csv` when a test does not require full shoreline geometry.
