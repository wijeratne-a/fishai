# Tile and LOD design — H3, privacy, and what the browser is allowed to load

**Agent:** VISUAL_PERFORMANCE / TECHNOLOGY-EVALUATION  
**Date:** 2026-09-18  
**Status:** Design. No production tiles. No bulk DEM ingest. Extends `artifacts/geospatial_data_engineer/` — does **not** reopen H3 vs S2.

---

## 0. Laws

1. **Browser never loads raw records** (no L0, no L1 lat/lon, no L4 outcomes, no AIS, no OBIS dumps).  
2. **Privacy grain is locked at bake time.** Zooming in is cartographic LOD, not a finer ACL.  
3. **Server-side (baker-side) aggregation only.** No client H3 rollup of GPS.  
4. **Sparse tiles.** Only cells with an issued state, an observation summary, or an explicit UNKNOWN-in-AOI request. Do not flood the ocean with interpolated hexes.  
5. **As-of.** Each tileset is keyed by `forecast_id` **or** `source_data_cutoff_utc`. There is no “latest” without a snapshot id.  
6. **Pessimistic downsample.** Empty children do not become a smooth parent probability.

---

## 1. Spatial index (inherited, not re-decided)

From `canonical_data_model.md` §3 and `global_digital_twin_architecture.md` §3.1.

| Use | H3 res | Mean area (documented) | Globe role |
|---|---|---|---|
| Global catalog / basin summaries | **3–4** | res 4 ~1 770 km² | Zoom 0–4 PUBLIC |
| Default **public** fish coarsening | **5** | ~253 km² | Max PUBLIC fish grain |
| Fish encounter **features** (internal) | **6** | ~36 km² | PRIVATE/RESTRICTED tiles only |
| Estuary / farm **internal** | **8** | ~0.74 km² | Never PUBLIC |
| Coastal research nest | **8–9** inside AOI | | Same privacy rules |

Always persist `spatial_cell_id`, `h3_res`, `spatial_cell_id_public`, `spatial_cell_area_km2` (H3 is **not** equal-area).

**Official polygons remain first-class** and often **coarser / more operationally honest** than H3:

| Wedge | Public geography | Not public |
|---|---|---|
| Oyster WA | WA DOH **growing area** (or named water body in fixtures) | Lease corners, rafts, beds, farm KPIs |
| Chinook | PFMC/state **management area** | H3-6 “holes,” drifts, wrecks |
| Lobster | NEFSC **statistical area** / LMA | Trap GPS, strings |

Red-team: public Chinook grain is **management area**, not H3-6 (`prediction_contract.md`; `deployment_blockers.md` B-SIB-04).

---

## 2. Zoom-level privacy rules (binding)

MapLibre/Cesium **web mercator zoom** `z` is only a request for **cartographic** detail. The baker maps `z` → **H3 parent to serve**, then **clamps** to the tile set’s `max_h3_res`.

### 2.1 PUBLIC tile set (anonymous / marketing / demo)

| Web zoom (approx) | Requested H3 parent | **Served** (clamp) | What may appear |
|---|---|---|---|
| 0–3 | res 3 | res **3** | Basin summaries, support tier, UNKNOWN hatch, **no** biological hotspot fill |
| 4–6 | res 4 | res **4** | Same + coarse env context if licensed |
| 7–9 | res 5 | res **5** | Default public fish grain **if** harm-reviewed; else official unit only |
| 10–12 | res 6 | **still res 5** (or official polygon) | Cells look larger; **no new GPS** |
| 13–22 | res 7–9 | **still res 5** / growing-area / PFMC area | Labels, evidence click; **not** H3-8 |

**Oyster PUBLIC:** ignore H3 children entirely. Geometry = **growing area or fixture water-body**. Zoom 22 still shows that polygon, not beds.

**k-anonymity:** do not emit a PUBLIC cell that represents **n &lt; 3** partners (or n = 1 farm). Withhold or roll up.

**DELAYED / embargo:** rows with `published_at + min_delay_hours > snapshot.as_of` are omitted at bake (`security_and_access_model.md` §6).

**NEVER_PUBLISH:** no tile, no tooltip, no vector hole that outlines the site.

### 2.2 COARSENED tile set (authenticated pilot)

Same pyramid, but `max_h3_res` may be **5** (fish) or **7** (farm bay-level) **if** the DUA says so. Still **no** lat/lon attributes. Still no client raw logs.

### 2.3 RESTRICTED / PRIVATE tile sets (ACL)

| Session | `max_h3_res` | Still forbidden in vector properties |
|---|---|---|
| Partner owner | Feature res (6 fish / 8 oyster) **on their footprint only** | Other partners’ geometry; vessel names; neighbor leases |
| Internal model-ops | Feature res inside AOI | Anything `NEVER_PUBLISH`; listed-species dens |

PUBLIC clients **cannot** URI-guess `/tiles/PRIVATE/...`. Separate prefix + key, same as parquet.

### 2.4 The rule in one sentence

> **Increasing zoom never changes `privacy_tier` and never raises H3 resolution above the tileset’s baked `max_h3_res`.**

A “progressive reveal” of fishing holes is a **privacy incident** (`privacy_and_sensitive_location_policy.md` §12).

---

## 3. Tile kinds

### 3.1 Vector tiles (primary biological / ops / coverage)

**Content:** H3 polygons (or official polygons) as MVT layers:

| `source-layer` | Properties (PUBLIC) | Forbidden properties |
|---|---|---|
| `cells` | `spatial_cell_id`, `h3_res`, `cell_area_km2`, `truth_state`, `confidence_category`, `privacy_tier`, `depth_bin_id`, `units`, `model_version`, `forecast_id`, `prediction_contract_category`, `data_support`, `official_unit_id` | `latitude`, `longitude`, `geometry` native GPS, `partner_id`, `lease_id`, `vessel_id`, raw `prediction_value` if contract forbids numbers |
| `unknown` | same ids + `reason_codes[]` | filled probability |
| `official` | `official_unit_id`, `attribution`, `last_verified_at_utc` | model open/closed color |

**Encoding:** MapLibre `fill` + `fill-pattern` (hatch) keyed on `truth_state`. **No heatmap layer. No blur. No extrusion-as-abundance.**

**Prototype:** GeoJSON FeatureCollection is acceptable for one Willapa AOI. Production path: tippecanoe `--no-tile-size-limit` only if needed; prefer dropping attributes over dropping privacy fields.

### 3.2 Raster tiles (physical / habitat context)

| Product | Format | Rule |
|---|---|---|
| Bathymetry hillshade / terrain | Terrain-RGB or Terrarium PMTiles | **Not navigation.** Fixture DEM in prototype — do not download GEBCO globally in this design pass. |
| SST, chl, winds | PNG/WebP XYZ **or** later COG+titiler | Legend in **physical units**. Title must not say oysters/fish. As-of in chrome. |
| Observation density | Raster or vector class | Density of **observations**, never AIS-as-animals |

Raster pyramids **also** clamp: do not serve 100 m biological rasters on PUBLIC. Env rasters may be native **if** not fused with biology (`sensitive_location_policy.md` habitat-only row). **Fusion inherits the biological tier.**

### 3.3 Volumetric tiles (later — not MVP)

**Do not** build a 256³ world texture.

**MVP stand-in:** each vector cell carries `depth_bins: [{ depth_bin_id, value, units, confidence_category, truth_state }]` in the **click JSON** (not necessarily in the MVT, to keep tiles small). Plotly reads that array.

**Later packings** (only after a real field):

| Packing | When |
|---|---|
| Extra MVT properties `z_SURFACE_0_5`, `z_SHELF_25_100`, … | Few bins, regional AOI |
| Quantized 3D Tiles voxels / vtk.js `.vti` per basin | Scientist stack 3 |
| Zarr subset on object store, **not** in the browser | Native cubes |

Empty bins stay **missing**, not 0. Depth-integrated flag `depth_representation: integrated | bin | unknown` is mandatory (`api_for_globe.md`).

### 3.4 3D Tiles

Out of MVP. If used: **bathymetry/habitat meshes**, quantized-mesh terrain, never a secret-spot point cloud.

---

## 4. Server-side aggregation

Baker algorithm for parent cell \(P\) from children \(C_i\) (already in the **same** privacy prefix):

| Child situation | Parent `truth_state` | Parent confidence | Parent value |
|---|---|---|---|
| All `DATA_GAP` / absent | `DATA_GAP` | `none` | **null** (not 0) |
| Mix of gap + values | `UNKNOWN` or keep `DATA_GAP` hatch overlay | **min** child confidence | **Do not** area-weighted mean of present-only children **as if** gaps were zero. Either withhold numeric value or mark `partial_coverage=true` |
| All same truth state | that state | min confidence | For ranks/terciles: recompute from child ranks **only if** comparison set is defined at parent; else **null** + `aggregated: true` |
| Any `RESTRICTED_OR_COARSENED` | `RESTRICTED_OR_COARSENED` | — | Coarser only |
| Any `NEVER_PUBLISH` child | **drop geometry** or roll to official unit | — | Must not outline the secret |

Counts: `n_obs`, `n_partners` computed on **PUBLIC-safe** ids. If `n_partners < 3`, withhold.

**No IDW, kriging, or GPU blur** to fill \(P\).

Area rates use `cell_area_km2` per cell, never the H3 table average.

---

## 5. Time LOD

| User control | Tiles loaded |
|---|---|
| One snapshot | `tiles/{privacy}/{forecast_id}/{z}/{x}/{y}` |
| Playback | Prefetch adjacent `forecast_id`s only |
| Climatology | Separate tileset `climate/{doy}/` baked from **historical PUBLIC** summaries, labeled CLIMATOLOGY |
| Anomaly | Baked difference vs named climatology; not computed in the fragment shader from live data |

Do not stack 365 daily biological rasters in the browser. Cache **one** time slice.

Forecast vs analysis: different `truth_state`; different tileset prefix `forecast/` vs `estimate/`.

---

## 6. Bake pipeline (local, small team)

```text
duckdb  read  normalized/PUBLIC/*.parquet   -- as-of predicate
   → parent H3 / official dissolve
   → geoparquet  bake/{forecast_id}/cells.parquet
tippecanoe  →  mbtiles
pmtiles convert →  cells.pmtiles
gdal  (fixture DEM) → terrain-rgb → pmtiles
pandera / pytest  FAIL if any feature property matches lat|lon|latitude|gps
write  bake_manifest.json  {forecast_id, cutoff, max_h3_res, privacy_tier, hashes}
```

Scheduler: laptop cron, same as ingest. **Not** Airflow. **Not** a public CDN of parquet.

Fixture prototype may **skip** tippecanoe and commit a hand-written GeoJSON under `globe/prototype/` (other agent). The **contract** is still: no real GPS, mixed truth states, Willapa water-body only.

---

## 7. Directory layout (object store / local)

```text
globe-tiles/
  PUBLIC/
    {forecast_id}/
      cells.pmtiles
      env_sst.pmtiles          # optional, labeled physical
      bathy.pmtiles            # fixture or rights-cleared
      manifest.json
  COARSENED/{forecast_id}/...
  PRIVATE/{forecast_id}/...    # IAM deny for brief/globe-public roles
```

Manifest must include `source_data_cutoff_utc`, `model_version`, `privacy_policy_applied`, `max_h3_res`, `aoi_id`.

---

## 8. Performance LOD (non-privacy)

| Viewport | Max features (order) | Action |
|---|---|---|
| World | hundreds of res-3/4 cells | Sparse catalog only |
| EEZ / region | thousands of res-5 | OK |
| Estuary | hundreds of polygons + one DEM | GeoJSON OK |
| Over budget | — | Raise parent; never send points |

Dynamic loading: MapLibre overzooms **the same** coarse MVT rather than fetching a forbidden finer layer (`maxzoom` in source = clamp zoom).

---

## 9. Prototype vs later

| | Prototype (local) | After rights + wedge lock |
|---|---|---|
| Cells | Synthetic Willapa GeoJSON | Baked from PUBLIC parquet |
| DEM | A few fixture terrain tiles **or** flat | AOI-clipped DEM if licence allows |
| Tile server | Vite / Range-request static | R2/S3 PMTiles |
| Volumetric | JSON `depth_bins[]` | Still JSON until a cube exists |

**Do not** fetch OpenWaters/GEBCO/EMODnet as part of implementing this document. Record them as **candidate** terrain sources for the rights agent.

---

## 10. Failure modes (tile-specific)

| Failure | User-visible | Not allowed |
|---|---|---|
| Missing tile | UNKNOWN hatch / “no snapshot” | Repeat last forecast |
| Mixed children | Hatch + `partial_coverage` | Average |
| Zoom past max_h3_res | Same cells, larger | Secret spots |
| Stale closures | `last_verified_at` banner | Green “open” fill |
