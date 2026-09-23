# Visual performance architecture — Ocean Life Globe

**Agent:** VISUAL_PERFORMANCE / TECHNOLOGY-EVALUATION (stack)  
**Date:** 2026-09-18  
**Project:** FishAI / Global Saltwater Life Observatory  
**Status:** Design only. No ocean ingest. No production tile CDN. Sibling visual language is owned by the UI agent (`README.md`, `visual_truth_states.md`). This file is **how** pixels get to the screen.

---

## 0. Non-negotiable constraints

| Constraint | Consequence for rendering |
|---|---|
| Small team; commercial v1 is **email/PDF** | Globe is a research/demo surface, not the SKU. Do not staff a Cesium ion + GPU mesh program. |
| Partner-first; write-time privacy | Browser never mounts `PRIVATE` prefixes. Zoom is **LOD**, not a privacy unlock. |
| No global lake | Tiles are **AOI-clipped, sparse, fixture-first**. No planetary voxel cube. |
| Prototype runs **locally** with fixture tiles | Prefer PMTiles / GeoJSON / static JSON over a tile-server process. |
| GPU optional; 2D fallback required | Terrain, globe projection, and any volume path must degrade to Mercator 2D, then to a static image + table. |
| As-of replay; no future leakage | Every painted cell is from a **locked snapshot**, not “live tables.” |
| Claims ≤ evidence | Empty water is **UNKNOWN hatch**, never a smooth interpolated field. |

Inherited: H3 + official polygons (`artifacts/geospatial_data_engineer/canonical_data_model.md`); depth bins (`observatory/global_digital_twin_architecture.md` §4); prediction contract (`artifacts/scientific_red_team/prediction_contract.md`).

---

## 1. Honest rendering model (Cesium is a globe, not a CT scanner)

The product spec asks for a 4D field \(P(\text{present}\mid \text{lon, lat, depth, time, env})\). **No browser globe engine in 2026 treats the ocean as a medical volume.**

| What the user asked for | What WebGL globes actually do well | Honest MVP substitute |
|---|---|---|
| Global 3D Earth | Cesium ellipsoid; MapLibre **globe projection** (sphere-mapped 2D/2.5D) | MapLibre globe *or* Mercator; Cesium later |
| Bathymetry / seafloor | Terrain-RGB / quantized-mesh **surface** | Fixture DEM + hillshade; **not-for-navigation** |
| Semi-transparent ocean interior | Poor. Engines render a **skin**, not water-column voxels | Opacity on surface cells; no fake glass ocean |
| Vertical curtain / depth slice | Not a first-class primitive in MapLibre; Cesium clipping planes are for **terrain/buildings**, not CT slices | **2D plot** (Plotly / Observable Plot) bound to the same `spatial_cell_id` |
| Volumetric probability cloud | Cesium `VoxelPrimitive` is **experimental**; vtk.js is a scientific volume viewer, not a GIS globe | **Later**, AOI-clipped, after a real 3D field exists |
| Time-lapse of “life” | Cheap to animate; easy to lie | Discrete **issued snapshots** only; no tween across UNKNOWN |

**Binding sentence for engineering:** the globe shows **surfaces, cells, and official polygons**. Depth is a **linked scientific plot** in MVP, not a GPU volume. Do not ship a translucent blue blob that looks like a census of animals in the water column.

P0 / W1 Willapa object is **not** \(P(\text{oyster present})\). Farm oysters are planted. The first operational visual is a Category **D** ops-stress indicator on coarsened public geography (`README.md` §4).

---

## 2. Client / server split

```text
L5 PUBLIC/COARSENED parquet  (already privacy-stripped)
        │
        ▼
  tile baker (Python + DuckDB + h3 + GDAL + tippecanoe)
        │  writes only derivatives allowed by privacy_tier
        ▼
  fixture or object-store:
    cells.pmtiles | env.pmtiles | bathy.pmtiles
    snapshots/{forecast_id}.json
    cells/{spatial_cell_id}@{as_of}.json
        │
        ▼
  browser: MapLibre (tiles) + Evidence panel (JSON) + Plotly (depth)
        │
        ✕ never  L0 raw, L1 lat/lon, L4 outcomes, NEVER_PUBLISH
```

**Do not load all raw records into the browser.** The client requests **tiles for the current viewport + zoom** and **one cell payload on click**. Aggregation (parent H3, counts, min confidence, mixed UNKNOWN) happens in the baker, not in `JSON.parse` of a warehouse dump.

Jobs that bake tiles **only mount PUBLIC or COARSENED prefixes**, same IAM split as `security_and_access_model.md` §4. A `PRIVATE` partner session is a **different tile set**, not a query parameter on the public set.

---

## 3. Level-of-detail (what changes with zoom)

Three independent axes. **Do not collapse them.**

| Axis | Who owns it | Rule |
|---|---|---|
| **Cartographic LOD** | MapLibre / Cesium tile pyramid | Coarser geometry at low zoom; same privacy grain. |
| **Analytical grain** | H3 parent/child + official unit | Parent cells at global zoom; children only if the **tile set’s max res** allows. |
| **Privacy grain** | Write-time `privacy_tier` + `SensitiveLocationRule` | **Locked at bake.** Zoom-in must not fetch a finer privacy class. |

At **global** zoom: sparse parent cells (H3 res 3–4), support-tier chips, UNKNOWN hatch, no biological hotspot texture.  
At **regional** zoom: env rasters (as-of), habitat/official polygons, historical occurrence **only if** PUBLIC and harm-reviewed, medium-res probability **only if** a model was actually issued at that grain.  
At **local** zoom: approved observation **summaries**, depth plot, model explanation. Exact GPS remains absent from PUBLIC tiles even at z18.

Progressive refinement: show hatch + “coverage unknown” immediately; then env tiles; then cell attributes. Never refine UNKNOWN into a filled probability by interpolation.

Downsampling **preserves uncertainty**: parent = `DATA_GAP` if all children empty; `UNKNOWN` if mixed empty/present; confidence = **min** of children (pessimistic); never mean-fill empty children.

Details: `tile_and_lod_design.md`.

---

## 4. Layer types (runtime)

| Kind | Format (MVP) | GPU? | Notes |
|---|---|---|---|
| Basemap | Vector PMTiles or raster XYZ | Optional | Attribution required; OSM-derived styles are ODbL. |
| Bathymetry | `raster-dem` Terrarium/Mapbox Terrain-RGB PMTiles | Optional | Fixture DEM for prototype. Hillshade on; exaggeration labeled. |
| H3 / official polygons | MVT/PMTiles or GeoJSON | Optional | Fill + pattern for truth state; **no heatmap blur**. |
| Env raster (SST, etc.) | Raster tiles or COG+titiler (later) | Optional | Legend = physical units, **never** “fish.” As-of in chrome. |
| Time slices | Separate tileset per `issued_at` **or** feature-state by `time_bin` | No extra | Precomputed. Do not interpolate frames. |
| Depth / curtain | JSON → Plotly | CPU | Same cell id as the map pick. |
| 3D Tiles / voxels | — | — | **Not in MVP.** |
| Raw points / tracks | — | — | **Forbidden** on PUBLIC. Partner ACL + coarsen only. |

---

## 5. Performance budgets (prototype + first AOI)

Willapa-scale fixture, laptop, local static server:

| Budget | Target | If exceeded |
|---|---|---|
| First meaningful paint | < 3 s | Drop terrain; Mercator only |
| Features in GPU memory | ≤ ~20k H3 polygons | Raise parent res; never dump parquet |
| Cell click payload | < 50 KB JSON | Summaries only; no feature vectors with private keys |
| Concurrent time slices in RAM | 1 displayed + 1 prefetch | Unload others |
| Mobile (later) | Mercator, no terrain, 2D hatch | Globe projection off |

Global view, **if** ever a sparse catalog ships: store only cells with data or an explicit envelope request (`global_digital_twin_architecture.md` §3.1). A dense H3-5 world mesh is a rejected lake.

---

## 6. GPU optional — fallback ladder

Required. Test each rung.

1. **WebGL2 + terrain + optional globe projection** (MapLibre).  
2. **WebGL2, Mercator, terrain off** (same style, `maxPitch: 0`).  
3. **No WebGL:** Leaflet (or MapLibre fail overlay) with **pre-rendered raster tiles** + HTML evidence table.  
4. **No map:** the commercial path — **email/PDF** already specified. The globe must not be the only way to see a Category D brief.

Animation, 3D Tiles, and volume rendering are **not** on rungs 2–4.

---

## 7. Time, animation, and anti-deception

- Time slider ticks = **issued snapshots** (`forecast_id`), not a continuous clock.  
- Playback rate labeled (`1 snapshot / 0.8 s`); do not speed-up to imply animals racing.  
- Forecast layers use the visual-truth **FORECAST** encoding (dashed/translucent); do not morph FORECAST into DIRECT_OBSERVATION.  
- No client-side interpolation of empty cells between times. If a cell is missing at \(t_2\), it is UNKNOWN at \(t_2\).  
- `as_of` / `source_data_cutoff_utc` is in the chrome on every frame (`api_for_globe.md`).

---

## 8. Accessibility vs GPU candy

Textures (hatch, dots, dashes) encode truth state so color is not the only channel (`accessibility_and_trust.md` when present). High-cost effects (atmosphere, underwater caustics, particle fish) are **out of scope** — they read as live animals.

Low-bandwidth mode: Mercator + one vector tileset + JSON panel; skip DEM.

---

## 9. What not to build (performance edition)

- Public tile CDN of parquet or of PRIVATE H3-8.  
- Kafka/Spark tile pipeline; Cesium ion as a default dependency.  
- Loading OBIS/GBIF/AIS into deck.gl HexagonLayer “to see scale.”  
- Custom WebGPU ocean path-tracer as Year-1 work.  
- Client-side H3 aggregation of raw GPS.  
- Smooth IDW/kriging in the fragment shader over DATA_GAP.

---

## 10. Pointers

| Document | Role |
|---|---|
| `technology_evaluation.md` | Spec **M** matrix |
| `stack_recommendation.md` | Three stacks + licenses/cost |
| `tile_and_lod_design.md` | H3 zoom privacy |
| `api_for_globe.md` | Snapshot-safe cell contract |
| `../artifacts/geospatial_data_engineer/as_of_replay_design.md` | Cutoff joins |
| `../observatory/sensitive_location_policy.md` | Public map is unsafe as v1 biological atlas |
