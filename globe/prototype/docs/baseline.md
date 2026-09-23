# Phase 0 — Baseline (pre-upgrade)

**Recorded:** 2026-09-22  
**App:** `globe/prototype` at MapLibre GL JS 6.10.0, Vite 6.4.3  
**Method:** Code inspection of `src/mapApp.ts`, `src/main.ts`, `index.html`, `styles.css`, and `VERIFICATION.md`. This is not a performance claim and is not a “Google Earth smooth” score.

## Honesty flows (already specified)

| Flow | Pre-upgrade behavior |
|---|---|
| Cold load | Empty answer: “Search a species or pick a place.” Willapa Category D does not open. |
| Yellowfin tuna | “No issued location.” “No forecast issued.” Optional coarse OBIS past reports. |
| Pacific oyster from search | “No issued location.” Demo stays on Learn. |
| Learn → oyster | Working-conditions fixture on Nahcotta. |
| Sensitive withhold | White shark (AphiaID 105838) is in the OBIS withhold set; not in the local catalog. |
| 2D toggle | Session-scoped mercator vs globe projection. |

## Camera and interaction (as shipped)

| Setting | Value |
|---|---|
| Style | `https://demotiles.maplibre.org/style.json` |
| Optional raster | EOX Sentinel-2 cloudless 2020 WMTS, opacity 0.85 |
| Projection | `globe` default; `mercator` if session flag set |
| Center / zoom / pitch | `[0, 12]`, zoom `1.15`, pitch `38` |
| minZoom / maxZoom | `0` / `14` |
| maxPitch | `60` |
| dragRotate / pitchWithRotate / touchPitch | true |
| cooperativeGestures | false |
| Dedicated camera module | none |
| Wheel around cursor | MapLibre default (not tuned) |
| Drag inertia | MapLibre default (not tuned) |
| Flight interrupt on user input | not implemented |
| Click-vs-drag guard | relies on MapLibre `click` only |
| Keyboard extras (home, tilt, back, Escape panels) | not implemented |
| Camera history | not implemented |

`maxZoom: 14` is above NASA Blue Marble’s meaningful zoom and can overstretch the EOX mosaic. `minZoom: 0` can lose the planet in globe projection.

## Layout

The page is a document grid: header, h1, search, answer strip, then a two- or three-column shell, then a time bar. The map is not the visual centerpiece. Explore controls live in a left rail that is hidden unless “Explore Globe” is selected.

## Assets and licenses in use

| Asset | License / attribution as coded |
|---|---|
| MapLibre demotiles | Public demo style; named in AttributionControl |
| EOX S2 cloudless 2020 | “Sentinel-2 cloudless by EOX (modified Copernicus Sentinel data 2020)” |
| Willapa GeoJSON | Synthetic fixtures, 2026-09-18 |
| OBIS past reports | Official occurrence API, coarsened, when a species is searched |
| NASA GIBS / GEBCO | not used |

## Performance

Not measured in this baseline. No device-specific frame-rate or TTI number is claimed.

## Screenshots

Phase 0 did not attach a separate image archive. Phase 6 records the upgraded globe after the camera, basemap, and layout work.
