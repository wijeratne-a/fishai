# Technology evaluation — Ocean Life Globe (user spec M)

**Agent:** VISUAL_PERFORMANCE / TECHNOLOGY-EVALUATION  
**Date:** 2026-09-18  
**Status:** Evaluation for a small team. Licenses and product pages accessed 2026-09-18 via public docs. **No vendor contract. No ingest.**

Spec **M** requires a recommendation of (1) MVP globe, (2) analyst/scientist, (3) long-term volume stack, after scoring the list below on: global 3D globe, bathymetry, ocean volume, time-dynamic layers, vector/raster, 3D tiles, large observation datasets, depth slices, animation, mobile, open-source licensing, cost, performance, scientific reproducibility, export/API.

Scoring: **H** = fits this program now; **M** = usable with work or later; **L** = poor fit; **—** = not the job of that tool. “Ocean volume” means **water-column scientific volume** (CT-like), not “a pretty blue globe.”

---

## 1. Scorecard (spec M)

| Technology | Globe | Bathy | Ocean volume | Time | Vec/Rast | 3D Tiles | Big obs | Depth slice | Anim | Mobile | License | Cost | Perf | Repro | Export/API |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **CesiumJS** | H | H | L | H | H | H | M | M | H | M | Apache-2.0 | $0 lib; ion $ | M–H | M | H |
| **Cesium 3D Tiles** | — | M | L–M | M | — | H | H (points) | L | M | M | OGC / Apache docs | Bake cost | H | M | H |
| **deck.gl** | M | L | L | H | H | L | **H** | L | H | M | MIT | $0 | H | M | M |
| **MapLibre GL JS** | M | H | L | M | **H** | L | M | L | M | **H** | BSD-3 | $0 | H | H | H |
| **Three.js** | L | L | M | M | L | L | L | M | H | M | MIT | $0 | M | L | L |
| **WebGPU** | — | — | M | — | — | — | — | M | M | L | W3C | $0 | H* | L | L |
| **NASA WorldWind (JS)** | M | M | L | L | M | L | L | L | L | L | Apache-2.0 | $0 | L | L | L |
| **OpenLayers** | L | M | L | M | H | L | M | L | L | M | BSD-2 | $0 | M | H | H |
| **Kepler.gl** | L | L | L | H | H | L | H | L | H | L | MIT | $0 / studio $ | M | L | M |
| **QGIS** | L | H | L | M | H | M | H | M | L | — | **GPL-2** | $0 | H (desktop) | **H** | H |
| **ParaView** | L | M | **H** | H | M | L | H | **H** | H | — | BSD-3 | $0 | H | **H** | H |
| **Custom WebGL/WebGPU volume** | L | L | H | M | L | L | M | H | H | L | n/a | Eng. time | ? | L | L |
| **Tile servers (Martin, titiler, …)** | — | H | L | M | H | M | H | L | — | — | mostly MIT/BSD | Ops $ | H | H | H |
| **Cloud geospatial (ion, Mapbox, ArcGIS, GEE, …)** | M | H | L | H | H | H | H | M | H | H | mixed | **$$** | H | L | H |

\*WebGPU performance is high **where implemented**; Safari/older Android still need WebGL fallback in 2026.

**Read the table as:** MapLibre wins **MVP web** (license, local tiles, mobile, 2D fallback). Cesium wins **true ellipsoid + 3D Tiles**. deck.gl wins **GPU layers of already-aggregated cells**. ParaView/vtk.js win **scientific volume**. Kepler and WorldWind **lose** for this program (see §16–17). Cloud platforms lose on cost, privacy, and “no global lake.”

---

## 2. CesiumJS

**What it is:** Apache-2.0 WebGL globe (WGS84 ellipsoid). Latest public release observed 2026-09-18: **1.142** (2026-06-01) on `CesiumGS/cesium`. 2D/2.5D Columbus views exist. CZML for time-dynamic entities. Quantized-mesh terrain. Imagery WMS/WMTS/TMS/COG-via-providers.

**Fits:** Spec A.1 true globe; seafloor as **terrain**; 3D Tiles for photogrammetry/point clouds; clipping planes; camera underground (still a **surface engine**).

**Does not fit:** Water-column CT. `VoxelPrimitive` is documented as **experimental** (no standard deprecation policy) — a research hook, not a validated ocean-biology renderer. Heavy bundle; ion is the easy path for world terrain (vendor + cost). Mobile works on recent phones, struggles on low-end.

**Reproducibility:** Scene JSON + ion asset ids are **not** a scientific snapshot. Reproducible path = **self-hosted** terrain/imagery + `forecast_id` in our API.

**Cost:** Library $0. Cesium ion: free community tier then paid world terrain / 3D Tiles hosting. Self-host quantized-mesh is real engineering.

**Verdict:** **Long-term globe host**, not the Willapa fixture MVP. Revisit when we need ellipsoid + 3D Tiles, not for email-adjacent P0.

---

## 3. Cesium 3D Tiles (1.0 / 1.1)

**What it is:** OGC community standard for hierarchical 3D content (b3dm, i3dm, pnts, cmpt; 1.1 metadata + implicit tiling). Voxel content exists via `3DTILES_content_voxels` + `Cesium3DTilesVoxelProvider`.

**Fits:** Massive **seafloor meshes**, wrecks, habitat surfaces, lidar. LOD streaming. Not for H3 hexagonal **analytics** (those stay MVT).

**Does not fit:** Discrete depth-bin biology. Baking a global biological voxel tileset would be a **lake**. Experimental voxels ≠ survey-grade slices.

**Verdict:** **Format to keep in the pocket** for habitat meshes. Not an MVP work item. Do not confuse “we support 3D Tiles” with “we render ocean volume.”

---

## 4. deck.gl

**What it is:** MIT GPU layer framework (vis.gl). `H3HexagonLayer`, `TripsLayer`, `HeatmapLayer`, `MVTLayer`. MapLibre overlay via `MapboxOverlay` / `MapLibre` integration. Experimental `GlobeView`.

**Fits:** Tens of thousands of **pre-aggregated** H3 cells; trip animation **of coarsened PUBLIC paths**; binary data.

**Does not fit:** Bathymetry terrain (not its job). Depth slices. Encourages **HeatmapLayer** and GPS dumps — exactly the visual we forbid. HeatmapLayer is **banned** for biological layers.

**Verdict:** **Optional accelerator** on stack 3 for large PUBLIC cell sets. Never pointed at L1 lat/lon. Not a globe.

---

## 5. MapLibre GL JS

**What it is:** BSD-3-Clause vector-tile renderer (Mapbox GL JS community fork). Style spec v8. `raster-dem` terrain (Mapbox or Terrarium encoding). **Globe projection** shipped; **terrain-on-globe** merged (PR #4977 / changelog). Native PMTiles protocol. MapLibre Native exists for iOS/Android later.

**Fits:** Local-first prototype; H3 as fill extrusions or polygons; official polygons; hillshaded bathymetry; same codebase for **Mercator 2D fallback**; mobile; tiny team; $0; fixture PMTiles on disk.

**Does not fit:** True ellipsoid with subsurface camera. Ocean volume. First-class 3D Tiles. Globe mode is a **projected map on a sphere**, not a water-column model.

**Reproducibility:** Style JSON + PMTiles bytes + `forecast_id` is a strong, hashable visual snapshot.

**Verdict:** **MVP globe/map stack (chosen).** Default **Mercator**; optional `projection: globe` as a demo toggle. Terrain on when WebGL and DEM exist; off otherwise.

---

## 6. Three.js

**What it is:** MIT general WebGL/WebGPU scene graph.

**Fits:** Custom meshes; can host a raymarched volume if we write it.

**Does not fit:** Geodesy, tiles, CRS, attribution, accessibility map chrome. Rebuilding Cesium/MapLibre is not a three-person job.

**Verdict:** **Reject as map engine.** May appear **inside** vtk.js/other, not as our GIS.

---

## 7. WebGPU

**What it is:** Browser GPU API, not a product. Three.js, vtk.js, and Babylon expose backends. Coverage in 2026 is still not “every partner phone.”

**Fits:** Future custom volume raymarcher; compute for particle advection **of licensed cubes**.

**Does not fit:** MVP. No 2D fallback of its own.

**Verdict:** **Capability for stack 3**, behind WebGL. Not a line item for P0.

---

## 8. NASA WorldWind (Java / JS)

**What it was:** NASA/ESA virtual globe. Apache-2.0. JS: Web WorldWind.

**Status (public, 2019–2026):** NASA **suspended** the WorldWind project (announcement May 2019). Elevation/imagery servers (`worldwind26.arc.nasa.gov`, `files.worldwind.arc.nasa.gov`) were withdrawn. Community fork **WorldWindJS** (`WorldWindEarth/worldwindjs`) exists; small compared with Cesium. Java WorldWind is a **desktop** NASA SDK, not our web prototype.

**Fits historically:** Teaching globe, WMS.

**Does not fit now:** Maintenance, tile reliability, 3D Tiles, vector-tile ecosystem, mobile web, community answers.

**Verdict:** **Rejected** for all three stacks. See `stack_recommendation.md` §5.

---

## 9. OpenLayers

**What it is:** BSD-2 2D GIS web library. WMS/WMTS/MVT/GeoTIFF. Best-in-class **OGC client** semantics.

**Fits:** Analyst web GIS; print; projections.

**Does not fit:** Globe; bathymetric terrain as MapLibre does; modern style-spec vector design; our prototype’s PMTiles-first path (possible but worse DX than MapLibre).

**Verdict:** **Not MVP.** Optional later if an agency **requires** WMS-only. QGIS already covers analyst OGC.

---

## 10. Kepler.gl

**What it is:** MIT (Foursquare) explorer on deck.gl + Mapbox/MapLibre. Time filters, hexbins, trip layers, large CSV/Parquet.

**Fits:** One-off **internal** exploration of **already PUBLIC** coarsened tables by a data scientist who knows not to plot GPS.

**Does not fit this globe:**

1. Product metaphor is “dump a GPS table and see.” That is how partner catch, AIS, and leases leak.  
2. No bathymetry globe, no evidence-truth encoding, no as-of snapshot contract.  
3. Heatmaps / trip replay are the **forbidden** visual.  
4. Mapbox-era defaults and a heavy Studio/cloud gravity well.  
5. Not mobile; not an evidence explorer; not harm-review-aware.

**Verdict:** **Rejected as a globe or partner-facing UI.** Do not add it to the prototype. Analysts use **QGIS + DuckDB**. See `stack_recommendation.md` §5.

---

## 11. QGIS (analyst/scientist stack)

**What it is:** GPL-2 desktop GIS. GeoParquet, PostGIS, NetCDF, GDAL, print layouts, mesh (limited).

**Fits:** Visual QA that PUBLIC tiles contain **no** lat/lon; official polygon joins; figure export for papers; harm-review screenshots; COG inspection.

**License caution:** GPL-2 on QGIS **does not infect** our BSD/MIT web client. Keep QGIS as a **desktop tool**, not linked into the globe binary.

**Does not fit:** Web globe; mobile; volume rendering of ROMS (use ParaView).

**Verdict:** **Analyst stack core.**

---

## 12. ParaView / scientific volumetric visualization

**What it is:** BSD-3, VTK-based desktop (and Trame/ParaViewWeb for remote). First-class volume, slice, clip, streamlines, time.

**Fits:** A **named**, AOI-clipped NetCDF/Zarr (ROMS/FVCOM/CMEMS subset) for **scientists**. Depth slices that are actually slices. Honest path for spec C.4–C.6 **offline**.

**Does not fit:** Partner email; public globe; P0 oyster (intertidal air × tide — **two bins**, not a 50-level cube). Running ParaView as a public multi-tenant renderer is an ops program we will not start.

**Verdict:** **Scientist volume tool** (stack 2, and input to stack 3). Not the browser MVP.

---

## 13. Custom WebGL/WebGPU volume rendering

**Libraries to steal from, not wrap as a product:** vtk.js (BSD-3, WebGL+WebGPU volume mapper — medical/scientific), Kitware VolView, Cesium experimental voxels.

**Fits:** When we have a **real** 3D field (HAB tracer, thermal-band occupancy volume) inside one basin, and vtk.js in a **panel** is not enough.

**Does not fit:** Year-1. Reproducibility is poor until the shader + transfer function is versioned next to `model_version`.

**Verdict:** **Stack 3, gated.** Prefer vtk.js **in a side panel** over a custom ocean path tracer.

---

## 14. Raster / vector tile servers

| Tool | Role | License (typical) | MVP? |
|---|---|---|---|
| **PMTiles** + static HTTP range | Local and R2/S3 serverless tiles | Spec CC0; JS BSD-3 | **Yes — default** |
| **tippecanoe** | GeoJSON → MVT/mbtiles | BSD-2 | Bake |
| **GDAL / rio-cogeo** | DEM → Terrain-RGB; COG | MIT-ish / BSD | Bake |
| **Martin** | Postgres/COG → tiles | MIT | Later if PG is up |
| **titiler** | COG dynamic tiles | MIT | Later env rasters |
| **pg_tileserv / Tegola** | PostGIS MVT | various | Later |
| **Cesium ion / Cesium terrain builder** | quantized-mesh | mixed | Stack 3 optional |

**Verdict:** Prototype = **no server**. `python -m http.server` or Vite + PMTiles/GeoJSON. Pilot = object store + CloudFront/R2, still no Martin unless Postgres already exists for RLS.

---

## 15. Cloud geospatial platforms

Evaluated as a class: **Cesium ion**, **Mapbox Tiling Service**, **ArcGIS Online / Image Server**, **Google Earth Engine**, **Foursquare Studio**, **Felt**, **AWS Location**, **Carto**.

| Criterion | Why they lose for v1 |
|---|---|
| Cost | Recurring + egress vs $0 local / $30–80/mo geospatial envelope |
| Privacy | Uploading partner-adjacent geometry to a SaaS is a DUA event |
| No global lake | GEE/Carto patterns pull planetary rasters |
| Reproducibility | Vendor style ids ≠ `feature_snapshot_id` |
| Commercial v1 | Email/PDF does not need ion |

**Allowed later:** static hosting of **our** PMTiles on R2/S3 (already in storage plan). That is object storage, not a geospatial SaaS.

**Verdict:** **Rejected for MVP and for any PRIVATE data.** Re-evaluate ion **only** if stack 3 needs world quantized-mesh and self-host has failed.

---

## 16. Why not Kepler.gl (explicit)

Rejected as globe, prototype, and default analyst UI.

- Wrong affordance (GPS dump → hexbin heatmap).  
- No visual-truth states, no privacy_tier, no as-of cutoff.  
- Makes AIS-as-abundance and “top holes” one checkbox away.  
- Red-team map rules (`prediction_contract.md` §6) and sensitive-location policy forbid that product.

If a scientist already has Kepler installed, they may load **PUBLIC coarsened parquet only**, with GPS columns stripped — same rule as notebooks. We will not document Kepler as a supported stack.

---

## 17. Why not NASA WorldWind (explicit)

Rejected as globe engine.

- NASA project **suspended** (2019); official elevation/imagery services gone.  
- Community JS fork is not Cesium-class maintained.  
- No 3D Tiles, weak vector-tile story, poor mobile web, tiny hiring pool.  
- CesiumJS is the maintained Apache-2.0 ellipsoid globe if we need one.

WorldWind **Java** remains a possible **offline NASA desktop** curiosity; it is not stack 1–3.

---

## 18. Adjacent notes (not in spec M list, but deciding)

| Piece | Role |
|---|---|
| **H3** (`h3-py` / `h3-js`) | Analytical index — Apache-2.0. Already chosen. |
| **Plotly.js** (MIT) or **Observable Plot** (ISC) | MVP depth curtain / depth curve |
| **Leaflet** (BSD-2) | Rung-3 no-WebGL fallback |
| **Vite + TypeScript** | Prototype bundler (sibling prototype agent) |
| **DuckDB** | Tile baker joins |

---

## 19. Decision input to `stack_recommendation.md`

1. **MVP:** MapLibre GL JS + PMTiles + fixture DEM + Plotly depth panel + static snapshot JSON; Mercator default; globe projection optional; Leaflet/static fallback.  
2. **Analyst:** QGIS + GDAL + DuckDB/tippecanoe baker + Jupyter/cartopy; ParaView when a licensed cube exists.  
3. **Long-term volume:** CesiumJS host + 3D Tiles for surfaces + vtk.js (then custom WebGPU) for **AOI-clipped** volumes + deck.gl for big PUBLIC H3; MapLibre remains the 2D/mobile fallback **forever**.
