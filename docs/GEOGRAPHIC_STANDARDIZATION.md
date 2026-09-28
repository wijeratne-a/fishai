# Geographic standardization

## Exchange CRS

- Horizontal exchange: **WGS84 lon/lat** (OGC:CRS84). Record `crs_epsg=4326` in metadata; do not rely on lat-first axis order.
- Depth: meters, positive downward when known; otherwise set `depth_unknown=true`.

## Analytical vs public geometry

| Tier | Allowed geometry |
|---|---|
| `PRIVATE` / `RESTRICTED` | Native lat/lon or fine cells, offline only |
| `COARSENED` / `PUBLIC` | `spatial_cell_id`, parent H3, or `official_unit_id` only |

**Globe evidence and model outputs must not include raw `latitude` / `longitude`.**

## Spatial support

Prefer the source’s sample unit (`POINT`, `TOW`, `TRANSECT`, `SAMPLE_UNIT`, …). A user query radius (e.g. 50 miles) is a display window, not the likelihood unit unless the survey design says so.

## Official units

When regulators/operators use polygons (growing areas, statistical areas, management zones), store `official_unit_id` / type alongside any H3 index. H3 does not replace official geography.

## Sensitivity

Sensitive taxa, wrecks, nurseries, spawning sites, and telemetry tracks: `NEVER_PUBLISH` native pins; coarsen or withhold.
