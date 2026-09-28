# Map source and license registry

Machine-readable twin: [`../public/fixtures/source-registry.json`](../public/fixtures/source-registry.json).  
Code: [`../src/basemap.ts`](../src/basemap.ts).

No Google Earth or Google Maps imagery is used.

## Wired in this build

### MapLibre demotiles

- **Use:** Vector land outlines and labels; fallback if rasters fail.
- **URL:** `https://demotiles.maplibre.org/style.json`
- **Native resolution:** Generalized world vectors. Not a satellite product.

### NASA GIBS Blue Marble shaded relief + bathymetry

- **Use:** Global globe at zoom 0–8.
- **Tiles:** `BlueMarble_ShadedRelief_Bathymetry` / `GoogleMapsCompatible_Level8`
- **Native resolution:** On the order of 500 m. Bathymetry is **shading**, not a 3D DEM and not live clouds.
- **Attribution:** NASA GIBS / EOSDIS. See NASA media guidance for Blue Marble.
- **Do not:** Overzoom this mosaic and call the extra pixels information.

### EOX Sentinel-2 cloudless 2020

- **Use:** Land and coast from about zoom 6.5–12.
- **Attribution:** Sentinel-2 cloudless by EOX (modified Copernicus Sentinel data 2020).
- **Date:** 2020 mosaic. Not a 2026 live image.
- **Fallback:** NASA layer + demotiles if the EOX host fails.

## Evaluated, not wired

### GEBCO 15-arc-second grid

- **Native resolution:** ~450 m at the equator.
- **Why not wired:** A raw GEBCO grid is not a MapLibre `raster-dem` tile set. This pass did **not** convert, host, or `setTerrain` that grid.
- **Spike result:** MapLibre 6.10 globe projection plus labeled shaded bathymetry (NASA GIBS) is enough for a global marine look. Terrain-RGB + `setTerrain` would need a hosted DEM, CORS, and a separate quality test. Engine stays MapLibre. Cesium is not adopted.

## Resolution chip

The on-map chip names the active imagery, its native scale, and that it is not live. When past-report cells are on, the chip also says the biological layer is ~1° / 100 km.
