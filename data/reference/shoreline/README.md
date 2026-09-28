# Pilot shoreline reference (Natural Earth)

## Source

- **Dataset:** [Natural Earth](https://www.naturalearthdata.com/) `ne_10m_land` (10m physical vectors)
- **Download URL:** https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/
- **Version:** 5.1.1 (from `ne_10m_land.VERSION.txt` in the upstream zip)
- **License:** Public domain ([Natural Earth terms](https://www.naturalearthdata.com/about/terms-of-use/))

## Vendored file

| File | Description |
|------|-------------|
| `ne_10m_land_pilot_clip.json` | GeoJSON land polygons intersecting the clip box (`.json` extension for CI policy) |

**Clip box (WGS84):** latitude 31°N–36°N, longitude 122°W–116°W (includes the Southern California Bight pilot and Channel Islands).

**SHA-256 (`ne_10m_land_pilot_clip.json`):** `2f677a16aa6c8470846d813eda6d82f2656dea2d697b1511a4c878542d20996c`

## Distance method

Production `nearshore` flags use **geodesic** distance on WGS84 (`pyproj.Geod`, ellipsoid WGS84) from each GLORYS cell centre to the nearest point on densified land-polygon boundaries (vertices spaced at ≤ 1 km along each edge). Configured in `data/config/wcofs_glorys_overlap.yaml` under `shoreline.distance_method: pyproj_geod_fwd`.

Unit tests may use the simplified polyline at `tests/fixtures/pilot_coastline_vertices.csv` when a test does not require full shoreline geometry.
