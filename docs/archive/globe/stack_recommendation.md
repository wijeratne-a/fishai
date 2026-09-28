# Stack recommendation — three visualization stacks

**Agent:** VISUAL_PERFORMANCE / TECHNOLOGY-EVALUATION  
**Date:** 2026-09-18  
**Status:** Recommended, not a purchase order. Commercial SKU remains **email/PDF**. Globe is local/fixture-first.

Evaluation detail: `technology_evaluation.md`. Runtime architecture: `visual_performance_architecture.md`.

---

## 0. Executive pick

| # | Stack | One-line |
|---|---|---|
| **1** | **MVP globe** | **MapLibre GL JS** (Mercator default, optional globe projection) + **PMTiles** (H3 + official polygons + fixture bathymetry DEM) + **Plotly.js** depth panel + **static snapshot JSON**. Leaflet/static image if WebGL dies. |
| **2** | **Analyst / scientist** | **QGIS** + **GDAL/tippecanoe/DuckDB** tile baker + **Jupyter/cartopy** figures. **ParaView** only when a **named, licensed, AOI-clipped** 3D cube exists (not P0 oyster). |
| **3** | **Long-term volume** | **CesiumJS** ellipsoid host + **3D Tiles** for seafloor/habitat **surfaces** + **vtk.js** (then WebGPU) for scientific volume of sparse `(h3, depth_bin, time)` + **deck.gl** for large **pre-aggregated PUBLIC** H3. **MapLibre 2D remains the fallback.** |

**Not chosen:** Kepler.gl, NASA WorldWind, OpenLayers-as-globe, Three.js-as-GIS, Cesium ion / Mapbox / GEE as default, custom ocean path tracer in Year 1.

---

## 1. MVP globe stack (prototype + first honest AOI)

### 1.1 Composition

| Layer | Choice | License | Cost (order) |
|---|---|---|---|
| App shell | Vite + TypeScript (sibling `prototype/`) | MIT | $0 |
| Map | **MapLibre GL JS** v5+ | **BSD-3-Clause** | $0 |
| Tiles | **PMTiles** in `/public` or `~/fishai-data/globe/` | Spec CC0; JS **BSD-3** | $0 local |
| Bathymetry | Fixture `raster-dem` (Terrarium or Mapbox Terrain-RGB), hillshade | Fixture bytes; later GEBCO/EMODnet **after rights** | $0 fixture |
| H3 cells | GeoJSON if &lt; ~5 MB; else MVT inside PMTiles | Apache-2.0 H3 | $0 |
| Official polygons | Same vector source (growing areas **as public GIS**, not leases) | Agency terms — **do not ingest** until rights | Fixture outlines only now |
| Depth curtain / slice / curve | **Plotly.js** (or Observable Plot) | MIT / ISC | $0 |
| Evidence explorer | Fetch static JSON (`api_for_globe.md`) | — | $0 |
| Time | Dropdown / slider over `forecast_id` list | — | $0 |
| Basemap | Sparse local style **or** OpenFreeMap/Protomaps **with attribution** | OSM **ODbL** if used | $0 |
| No-GPU | Mercator, terrain off; then **Leaflet** raster; then PDF | BSD-2 Leaflet | $0 |

**CesiumJS is not the MVP.** Willapa is a bay. Spec A.1 “global 3D Earth” is satisfied later by MapLibre globe **projection** (demo) or Cesium (stack 3). Shipping Cesium+ion for a fixture prototype fails small-team, local, and mobile constraints.

### 1.2 Capabilities vs spec M

| Need | MVP behavior |
|---|---|
| Global 3D globe | Optional `projection: 'globe'`. Default **2D Mercator** for honesty and performance. |
| Bathymetry | Terrain-RGB + hillshade; caption **not for navigation**. |
| Ocean volume | **None.** Do not fake a glass ocean. |
| Time-dynamic | Swap pre-baked tile/JSON per `issued_at`. No tween. |
| Vector/raster | Native. |
| 3D Tiles | **No.** |
| Large observation datasets | **No raw records.** Tiles of aggregates only. |
| Depth slices | **2D Plotly** for the picked cell’s `depth_bin[]`. Horizontal slice = filter cells by `depth_bin_id` on the map (same 2D view). |
| Animation | Snapshot playback, labeled speed; FORECAST encoding distinct. |
| Mobile | Mercator, no terrain, large hit targets. MapLibre Native **not** in v0. |
| Reproducibility | Hash PMTiles + style + `forecast_id`. |
| Export/API | GeoJSON download of **visible PUBLIC cells**; PNG screenshot; table in panel. Full 14-field contract lives on PDF/email. |

### 1.3 Mobile

| Device | Mode |
|---|---|
| Desktop with WebGL2 | Mercator + optional terrain + optional globe |
| Phone | Mercator, terrain **off**, globe **off** |
| No WebGL | Leaflet XYZ + table |
| Crew on a boat | **Not this UI.** Email/PDF/WhatsApp brief |

### 1.4 3D Tiles, depth, animation (MVP honesty)

- **3D Tiles:** out.  
- **Depth:** plot + `depth_bin_id` filter. W1: `INTERTIDAL_AIR` vs `SURFACE_0_5` vs `UNKNOWN` — not 75 CMEMS levels.  
- **Animation:** only if ≥2 fixture snapshots exist; otherwise a static **Issued / Valid / Inputs through** readout (required chrome).

### 1.5 Cost

**$0** while local. Pilot: same R2/S3 bucket as geospatial storage (~$1–5/mo extra for a few GB of PMTiles). No ion, no Mapbox token required (avoid Mapbox styles that need one).

---

## 2. Analyst / scientist stack

For people who must **see the parquet**, bake tiles, and fail a privacy test — not for captains.

| Tool | Use | License | Cost |
|---|---|---|---|
| **QGIS** 3.x | Open PUBLIC GeoParquet; confirm stripped GPS; style official units; print a **coverage** figure | GPL-2 (desktop only) | $0 |
| **DuckDB** + `h3` + **pandas/geopandas** | As-of joins; parent aggregation; tile feature tables | MIT / Apache-2.0 | $0 |
| **GDAL** | Warp DEM, `gdal2tiles` / Terrain-RGB, COG | MIT-style | $0 |
| **tippecanoe** | Vector pyramid | BSD-2 | $0 |
| **pmtiles** CLI | mbtiles → PMTiles | BSD-3 | $0 |
| **Jupyter + matplotlib/cartopy** | Paper figures; **no** interactive GPS explorer in shared notebooks | BSD | $0 |
| **ParaView** | Slice/volume a **licensed** NetCDF/Zarr subset | BSD-3 | $0 |
| **pandera** tests | Baker CI: fail if `latitude` in PUBLIC tile attributes | MIT | $0 |

**Workflow:** warehouse/object store (geospatial engineer) → baker (`tile_and_lod_design.md`) → artifacts consumed by stack 1. Scientists **do not** browse Kepler against PRIVATE logs.

**P0 oyster:** ParaView is **idle**. Two depth bins plus a tide curve do not need VTK.

**Reproducibility:** baker `transform_hash` + input snapshot ids, same as feature snapshots.

**Mobile:** none. This stack is a laptop.

**3D Tiles:** QGIS has limited 3D; not our publisher. If we bake 3D Tiles later, use Cesium tooling in stack 3.

**Depth slices:** ParaView for cubes; QGIS mesh/raster profile for 2D sections of DEM or a single variable.

**Animation:** ParaView time steps for cubes; QGIS temporal controller for 2D. Not partner-facing.

---

## 3. Long-term high-performance volume-rendering stack

**Gate:** a real, rights-approved, **AOI-clipped** 3D field exists (e.g. thermal-band occupancy, HAB tracer, ROMS T/S). Empty registry today (`global_digital_twin_architecture.md` §7: no taxon is T6). Until then this stack is **design only**.

### 3.1 Composition

| Piece | Role |
|---|---|
| **CesiumJS** (Apache-2.0) | True WGS84 globe, underground camera, clipping planes, time clock |
| **3D Tiles 1.1** | Seafloor/habitat **meshes** and point clouds — not biology voxels by default |
| **vtk.js** (BSD-3) | Scientific **volume + slice** in a panel or synced camera; WebGL then WebGPU backend |
| **deck.gl** (MIT) | GPU draw of **pre-aggregated** PUBLIC H3 / trajectories (no HeatmapLayer for life) |
| **Custom WebGPU raymarcher** | Only if vtk.js cannot show our sparse `(cell, z, t)` field |
| **Cesium VoxelPrimitive** | Evaluate; treat as **experimental**; do not base claims on it |
| **Trame / ParaView server** | Scientist-only remote render of cubes too big for the browser |
| **MapLibre** | **Permanent** 2D/mobile/low-GPU fallback consuming the **same** PMTiles |

### 3.2 Spec M at this horizon

| Need | How |
|---|---|
| Ocean volume | vtk.js transfer function on a **sparse** grid; empty = transparent + UNKNOWN legend, **not** zero |
| Depth slices | vtk.js / ParaView **orthogonal slices**; globe shows slice–surface intersection as a line |
| 3D Tiles | Surfaces yes; biological voxels only after a written accuracy test vs discrete `depth_bin_id` |
| Animation | Cesium clock **snapped** to issued times **or** model output times with `published_at ≤ cutoff` |
| Mobile | Still MapLibre 2D; volume is **desktop** |
| Cost | $0 libraries; optional ion if self-hosted terrain fails; GPU laptop for scientists |
| Repro | Version transfer functions, camera, `model_version`, `feature_snapshot_id` |

### 3.3 What this still will not be

A CT scanner of the global ocean. A live animal cloud. A reason to pull 75-level CMEMS globally. A public NARW volume.

---

## 4. Cross-cutting: licenses, cost, mobile, 3D tiles, depth, animation

| | Stack 1 MVP | Stack 2 Analyst | Stack 3 Volume |
|---|---|---|---|
| **Licenses** | BSD-3 + MIT + Apache H3; OSM ODbL if basemap | GPL-2 QGIS isolated; BSD baker | Apache Cesium + BSD vtk.js + MIT deck.gl |
| **Cost** | $0 local | $0 | $0 libs; optional ion/GPU |
| **Mobile** | Mercator MapLibre | No | MapLibre fallback only |
| **3D Tiles** | No | No | Surfaces yes; voxels experimental |
| **Depth slices** | Plotly 2D | ParaView / QGIS profile | vtk.js + globe intersection |
| **Animation** | Snapshot slider | Desktop time | Clock + FORECAST encoding |

**GPL note:** do not statically link QGIS into the web app.

**Attribution:** every terrain/basemap/source string in the MapLibre `attribution` control; GEBCO “not for navigation” if used.

---

## 5. Rejected options (short)

| Reject | Why |
|---|---|
| **Kepler.gl** | GPS-dump heatmap product; no as-of/privacy/truth-state; leak magnet. Analysts: QGIS + DuckDB. |
| **NASA WorldWind** | Project suspended 2019; servers gone; fork too weak vs Cesium. |
| **OpenLayers as the globe** | Excellent 2D GIS; we already have MapLibre (web) + QGIS (analyst). |
| **Three.js as the map** | Would reimplement tiles/CRS. |
| **Cesium as MVP** | True globe, wrong cost/complexity/mobile/local-first for Willapa fixtures. |
| **Cloud GIS (ion/Mapbox/GEE/ArcGIS Online)** | Money, residency, lake gravity. Static R2 of our PMTiles is enough. |
| **deck.gl HeatmapLayer** | Forbidden biological encoding. |
| **Custom WebGPU Year-1** | No data to render; no fallback. |

---

## 6. Suggested build order (after fixture prototype exists)

1. MapLibre Mercator + hatch cells + evidence JSON + Plotly stub (sibling prototype).  
2. Fixture DEM hillshade; globe projection as a **checkbox**.  
3. Baker: DuckDB parent H3 → tippecanoe → PMTiles; pandera GPS-absence test.  
4. QGIS checklist for privacy QA.  
5. **Stop.** Do not start Cesium/vtk.js until a 3D field and a desktop scientist need it.

---

## 7. Alignment with paused commercial wedge

Captains and farm managers **do not** need stack 1 to get value. Stack 1 must be able to **export** a 14-field panel that matches the email/PDF (`prediction_contract.md`). If the globe and the brief disagree, **L3 prediction wins** (`canonical_data_model.md` layer rules).
