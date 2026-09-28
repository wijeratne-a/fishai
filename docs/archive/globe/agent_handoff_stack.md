# Agent handoff — globe visual performance / stack

**Agent id:** VISUAL_PERFORMANCE / TECHNOLOGY-EVALUATION  
**Date:** 2026-09-18  
**Write root:** `/Users/wijeratne/dev/fishai/globe/`  
**Did not write:** `artifacts/integration/**`, `project_state.json`, `observatory/**`, commercial product files. Did not ingest ocean data. Did not download GEBCO/CMEMS/OBIS.

UI language is a **sibling** (`README.md` and visual-spec files). This handoff is **how it renders and which libraries**.

---

## 1. Executive finding

**MVP globe = MapLibre GL JS + local PMTiles/GeoJSON + fixture bathymetry DEM + Plotly depth panel + static as-of JSON.** Default **2D Mercator**; optional MapLibre **globe projection**; **Leaflet/static** if WebGL is missing. GPU terrain is optional.

CesiumJS is a **true ellipsoid globe**, not a CT scanner of the water column. Depth curtain/slice in MVP is a **2D plot of the same cell**, not a GPU volume. Kepler.gl and NASA WorldWind are **rejected**.

Commercial v1 remains **email/PDF**. This stack must not become a public animal heatmap or a global tile lake.

---

## 2. Three stacks (spec M)

| # | Name | Stack | 3D Tiles | Depth | Animation | Mobile | Cost |
|---|---|---|---|---|---|---|---|
| **1** | MVP globe | MapLibre BSD-3, PMTiles, Plotly MIT, H3 Apache-2.0 | No | Plotly bins | Snapshot slider | Mercator, no terrain | $0 |
| **2** | Analyst/scientist | QGIS GPL-2 (desktop), GDAL, DuckDB, tippecanoe; **ParaView** if a licensed cube exists | No | ParaView / profile | Desktop only | No | $0 |
| **3** | Long-term volume | CesiumJS Apache-2.0 + 3D Tiles **surfaces** + vtk.js volume + deck.gl **pre-aggregated PUBLIC** H3; MapLibre fallback **forever** | Surfaces yes; voxels experimental | vtk.js slices | Cesium clock snapped to issued times | 2D fallback only | $0 libs; optional ion later |

Build order: **1 → baker in 2 → stop.** Do not start 3 until a real AOI-clipped 3D field exists.

---

## 3. Why not Kepler / WorldWind

**Kepler.gl:** GPS-dump heatmap explorer; no as-of, no `privacy_tier`, no visual-truth contract; leak magnet for catch/AIS/leases. Analysts use QGIS + DuckDB on **already PUBLIC** parquet.

**NASA WorldWind:** project **suspended 2019**; official elevation/imagery servers gone; JS fork too weak. If we need an ellipsoid later, use **CesiumJS**.

---

## 4. Zoom-level privacy rules (for every visual/geo agent)

| Zoom | PUBLIC serves | Never |
|---|---|---|
| Global (z 0–6) | H3 res **3–4** summaries, UNKNOWN hatch | Biological hotspot fill |
| Regional (z 7–9) | H3 res **5** or **official unit** (oyster = growing area) | H3-6/8 “holes” |
| Local (z 10–22) | **Same max grain, larger on screen** | Finer privacy class, GPS, leases, traps |

**Zoom is LOD, not an ACL upgrade.** Bake-time clamp: `max_h3_res`. k-anonymity: no PUBLIC cell with n &lt; 3 partners. `NEVER_PUBLISH` is omitted, not blurred. Details: `tile_and_lod_design.md` §2.

---

## 5. Files written

| File | Role |
|---|---|
| `visual_performance_architecture.md` | Spec L: client/server, LOD axes, GPU fallback ladder, anti-deception animation |
| `technology_evaluation.md` | Spec M matrix + per-tool verdicts |
| `stack_recommendation.md` | Stacks 1–3, licenses, cost, mobile, tiles, depth, animation |
| `tile_and_lod_design.md` | H3 parents, vector/raster/volumetric, baker, zoom privacy |
| `api_for_globe.md` | Snapshot + cell contract: `truth_state`, depth, as-of, `privacy_tier`, units, `model_version` |
| `agent_handoff_stack.md` | This document |

---

## 6. Recipients

| Agent | Ask |
|---|---|
| Prototype implementer | MapLibre + fixtures; no Cesium required; Plotly for depth; mixed truth states; Willapa water-body only |
| UI / evidence | Bind chrome to `api_for_globe.md` snapshot fields; UNKNOWN hatch not a spinner |
| Geospatial engineer | Baker mounts **PUBLIC/COARSENED only**; pandera fail on lat/lon in tiles; snapshot keys = `forecast_id` |
| Rights / sensitive location | Public biological atlas remains **unsafe**; globe P0 = coverage + env + ops-stress, not life census |
| Scientific red team | No interpolated empty cells; no future leakage on time slider; oyster cell stays Category D |
| Product / commercial | Do not replace email/PDF with a globe SKU |
| Cost | $0 local; no ion/Mapbox/GEE line in Year-1 P0 |

---

## 7. Confidence and limitations

| Item | Confidence | Limit |
|---|---|---|
| MapLibre as MVP vs Cesium | High for Willapa/small team | Globe projection ≠ ellipsoid subsurface |
| Volume rendering immaturity | High | Cesium voxels experimental (docs, 2026) |
| License table | High for OSS SPDX; Medium for agency DEM reuse | Rights agent must clear GEBCO/EMODnet/OSM style before non-fixture terrain |
| Tile privacy clamp | High as a design | Unproven in running baker |
| Kepler/WorldWind reject | High | — |

No datasets ingested. No models trained. No tile CDN.

---

## 8. Smallest next experiment

Already in scope for the **prototype** sibling: open a local MapLibre app on fixture Willapa cells with FORECAST vs UNKNOWN vs HABITAT encodings and an evidence JSON panel.

**Do not** as the next stack step: stand up Cesium ion, Martin, titiler, or a WebGPU volume.
