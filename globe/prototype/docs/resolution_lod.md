# Geospatial resolution and level of detail

Maximum **defensible** detail, not maximum pixel density.

## Basemap

| Zoom | Imagery | Native scale | If the user zooms further |
|---|---|---|---|
| 0–7 | NASA GIBS Blue Marble shaded relief + bathymetry | ~500 m | Soft coasts; chip stays honest |
| 7–12 | EOX Sentinel-2 cloudless 2020 | Sentinel-2 mosaic | Map `maxZoom` is 12. No fake extra detail. |

Bathymetry in this build is **shaded relief** from NASA GIBS. It is not GEBCO terrain, not a water-column mesh, and not navigation.

## Biological layers

Each layer tracks, separately:

- native source resolution
- displayed tile resolution
- validated biological model resolution (null unless published)
- positional uncertainty
- time resolution
- depth resolution
- sensitivity-driven coarsening

Past reports (the only species geometry in this build):

- Native: OBIS 1° occurrence grid (~100 km)
- Displayed: same cells, max 80, n < 3 hidden
- Validated model resolution: none
- Time: year span of compiled records
- Depth: not modeled
- Sensitive taxa: withheld before draw (client hide is not the only rule; the API request is skipped for withheld AphiaIDs)

When the camera is zoomed past that 1° grain, the resolution chip says the biological layer is still ~100 km.

## Willapa fixtures

Synthetic cells at growing-area scale. Learn demo only. Not a published biological resolution.
