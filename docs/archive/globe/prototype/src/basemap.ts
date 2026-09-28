import type { Map as MapLibreMap, StyleSpecification } from "maplibre-gl";
import type { MapProjectionMode } from "./camera";

export interface MapSourceRecord {
  source_id: string;
  provider: string;
  source_url: string;
  attribution: string;
  license_or_contract: string;
  permitted_display_use: string;
  tile_format: string;
  coordinate_system: string;
  native_resolution: string;
  max_meaningful_zoom: number;
  min_zoom: number;
  global_or_regional_coverage: string;
  update_date: string;
  cache_rules: string;
  expected_cost_or_rate_limit: string;
  fallback_source: string | null;
  known_visual_artifacts: string;
  tiles?: string[];
  tileSize?: number;
  wired: boolean;
}

export const SOURCE_REGISTRY: MapSourceRecord[] = [
  {
    source_id: "maplibre-demotiles",
    provider: "MapLibre",
    source_url: "https://demotiles.maplibre.org/style.json",
    attribution: "MapLibre demotiles",
    license_or_contract: "Public demo vector style for MapLibre examples",
    permitted_display_use: "Vector land outlines and labels; fallback if rasters fail",
    tile_format: "MapLibre style / vector tiles",
    coordinate_system: "EPSG:3857",
    native_resolution: "Generalized world vectors",
    max_meaningful_zoom: 8,
    min_zoom: 0,
    global_or_regional_coverage: "global",
    update_date: "demo style, not a dated mosaic",
    cache_rules: "Browser HTTP cache",
    expected_cost_or_rate_limit: "Public demo; do not treat as production SLA",
    fallback_source: null,
    known_visual_artifacts: "Sparse labels; not a satellite globe",
    wired: true,
  },
  {
    source_id: "nasa-gibs-blue-marble-bathymetry",
    provider: "NASA GIBS / EOSDIS",
    source_url:
      "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg",
    attribution:
      "NASA Blue Marble shaded relief and bathymetry via <a href=\"https://earthdata.nasa.gov/gibs\" rel=\"noopener\">GIBS</a>",
    license_or_contract: "NASA imagery media guidance; attribute NASA GIBS / EOSDIS",
    permitted_display_use: "Global visual context only. Not live. Not navigation.",
    tile_format: "JPEG WMTS (GoogleMapsCompatible_Level8)",
    coordinate_system: "EPSG:3857",
    native_resolution: "On the order of 500 m; bathymetry is shaded relief, not a DEM",
    max_meaningful_zoom: 8,
    min_zoom: 0,
    global_or_regional_coverage: "global",
    update_date: "Blue Marble Next Generation mosaic (not a daily product)",
    cache_rules: "GIBS CDN / browser cache",
    expected_cost_or_rate_limit: "Public GIBS; be polite, no bulk scrape",
    fallback_source: "maplibre-demotiles",
    known_visual_artifacts: "Soft coasts above zoom 8; static clouds/lighting; not current weather",
    tiles: [
      "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg",
    ],
    tileSize: 256,
    wired: true,
  },
  {
    source_id: "eox-s2cloudless-2020",
    provider: "EOX / Copernicus Sentinel-2",
    source_url: "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/g/{z}/{y}/{x}.jpg",
    attribution:
      "<a href=\"https://s2maps.eu\" rel=\"noopener\">Sentinel-2 cloudless</a> by EOX (modified Copernicus Sentinel data 2020)",
    license_or_contract: "EOX Sentinel-2 cloudless terms; Copernicus Sentinel data 2020",
    permitted_display_use: "Closer land/coast zoom. Not a 2026 live image. Not navigation.",
    tile_format: "JPEG WMTS",
    coordinate_system: "EPSG:3857",
    native_resolution: "Sentinel-2 mosaic; do not treat zoom 12+ as extra information",
    max_meaningful_zoom: 12,
    min_zoom: 6,
    global_or_regional_coverage: "global land-weighted mosaic",
    update_date: "2020 cloudless mosaic",
    cache_rules: "EOX tiles / browser cache",
    expected_cost_or_rate_limit: "Public tiles; rate-limit unknown — fallback if they fail",
    fallback_source: "nasa-gibs-blue-marble-bathymetry",
    known_visual_artifacts: "2020 season composite; oceans are satellite water, not bathymetry",
    tiles: ["https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/g/{z}/{y}/{x}.jpg"],
    tileSize: 256,
    wired: true,
  },
  {
    source_id: "gebco-2024-15-arc-second",
    provider: "GEBCO",
    source_url: "https://www.gebco.net/data-products/gridded-bathymetry-data",
    attribution: "GEBCO Compilation Group (grid product — not tiled in this build)",
    license_or_contract: "GEBCO terms; grid download is not a browser XYZ service",
    permitted_display_use: "Evaluated only. Not converted to Terrain-RGB. Not set as MapLibre terrain.",
    tile_format: "NetCDF / GeoTIFF grid (15 arc-second, ~450 m at equator)",
    coordinate_system: "WGS84 geographic grid",
    native_resolution: "~450 m at equator (15 arc-second)",
    max_meaningful_zoom: 8,
    min_zoom: 0,
    global_or_regional_coverage: "global ocean",
    update_date: "GEBCO 2024 grid (catalog date; not ingested)",
    cache_rules: "n/a — not hosted",
    expected_cost_or_rate_limit: "Download + tile bake required before any terrain use",
    fallback_source: "nasa-gibs-blue-marble-bathymetry",
    known_visual_artifacts: "A raw grid is not a globe terrain layer",
    wired: false,
  },
];

export const CUSTOM_ATTRIBUTION =
  "NASA GIBS Blue Marble (shaded relief + bathymetry, not live) · EOX Sentinel-2 cloudless 2020 · MapLibre demotiles fallback · fixture Willapa cells · OBIS past reports when shown · not for navigation · not a live animal map";

function insertBeforeVector(map: MapLibreMap): string | undefined {
  const layers = map.getStyle().layers ?? [];
  return layers.find((layer) => layer.type !== "background" && layer.type !== "raster")?.id;
}

function addRasterLayer(
  map: MapLibreMap,
  record: MapSourceRecord,
  layerId: string,
  paint: Record<string, unknown>,
  extra: { minzoom?: number; maxzoom?: number } = {},
): boolean {
  if (!record.tiles || record.tiles.length === 0) return false;
  try {
    if (!map.getSource(record.source_id)) {
      map.addSource(record.source_id, {
        type: "raster",
        tiles: record.tiles,
        tileSize: record.tileSize ?? 256,
        attribution: record.attribution,
        maxzoom: record.max_meaningful_zoom,
        minzoom: record.min_zoom,
      });
    }
    if (!map.getLayer(layerId)) {
      map.addLayer(
        {
          id: layerId,
          type: "raster",
          source: record.source_id,
          minzoom: extra.minzoom ?? record.min_zoom,
          maxzoom: extra.maxzoom ?? 24,
          paint,
        },
        insertBeforeVector(map),
      );
    }
    return true;
  } catch {
    return false;
  }
}

export function softenDemoStyle(map: MapLibreMap): void {
  const layers = map.getStyle().layers ?? [];
  for (const layer of layers) {
    if (layer.type === "background") {
      try {
        map.setPaintProperty(layer.id, "background-color", "#07141d");
      } catch {
        /* style-specific */
      }
    }
    if (layer.type === "fill" && !layer.id.startsWith("cells") && !layer.id.startsWith("land") && !layer.id.startsWith("past")) {
      try {
        map.setPaintProperty(layer.id, "fill-opacity", 0.14);
      } catch {
        /* keep labels */
      }
    }
  }
}

export function buildGlobeStyle(mode: MapProjectionMode): StyleSpecification {
  const nasa = SOURCE_REGISTRY.find((row) => row.source_id === "nasa-gibs-blue-marble-bathymetry");
  const eox = SOURCE_REGISTRY.find((row) => row.source_id === "eox-s2cloudless-2020");
  if (!nasa?.tiles || !eox?.tiles) {
    throw new Error("Basemap registry is missing NASA or EOX tiles.");
  }
  return {
    version: 8,
    name: "FishAI marine globe",
    projection: { type: mode },
    glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
    sources: {
      [nasa.source_id]: {
        type: "raster",
        tiles: nasa.tiles,
        tileSize: nasa.tileSize ?? 256,
        maxzoom: nasa.max_meaningful_zoom,
        minzoom: nasa.min_zoom,
        attribution: nasa.attribution,
      },
      [eox.source_id]: {
        type: "raster",
        tiles: eox.tiles,
        tileSize: eox.tileSize ?? 256,
        maxzoom: eox.max_meaningful_zoom,
        minzoom: eox.min_zoom,
        attribution: eox.attribution,
      },
    },
    layers: [
      { id: "background", type: "background", paint: { "background-color": "#07141d" } },
      {
        id: "basemap-nasa",
        type: "raster",
        source: nasa.source_id,
        paint: {
          "raster-opacity": ["interpolate", ["linear"], ["zoom"], 0, 1, 7.1, 1, 8.7, 0.18],
          "raster-fade-duration": 220,
        },
      },
      {
        id: "basemap-eox",
        type: "raster",
        source: eox.source_id,
        minzoom: 6.4,
        paint: {
          "raster-opacity": ["interpolate", ["linear"], ["zoom"], 6.4, 0, 8, 0.9],
          "raster-fade-duration": 220,
        },
      },
    ],
  };
}

export function installBasemap(map: MapLibreMap): { nasa: boolean; eox: boolean } {
  if (map.getLayer("basemap-nasa") && map.getLayer("basemap-eox")) {
    return { nasa: true, eox: true };
  }
  softenDemoStyle(map);
  const nasa = SOURCE_REGISTRY.find((row) => row.source_id === "nasa-gibs-blue-marble-bathymetry");
  const eox = SOURCE_REGISTRY.find((row) => row.source_id === "eox-s2cloudless-2020");
  const nasaOk = nasa
    ? addRasterLayer(map, nasa, "basemap-nasa", {
        "raster-opacity": ["interpolate", ["linear"], ["zoom"], 0, 1, 7.1, 1, 8.7, 0.18],
        "raster-fade-duration": 220,
      })
    : false;
  const eoxOk = eox
    ? addRasterLayer(
        map,
        eox,
        "basemap-eox",
        {
          "raster-opacity": ["interpolate", ["linear"], ["zoom"], 6.4, 0, 8, 0.9],
          "raster-fade-duration": 220,
        },
        { minzoom: 6.4, maxzoom: 24 },
      )
    : false;
  return { nasa: nasaOk, eox: eoxOk };
}

export function resolutionForZoom(zoom: number): {
  source: string;
  native: string;
  date: string;
  chip: string;
} {
  if (zoom < 7.2) {
    return {
      source: "NASA GIBS Blue Marble",
      native: "about 500 m (shaded relief + bathymetry)",
      date: "static mosaic, not live",
      chip: "Imagery: NASA Blue Marble · ~500 m · not live · bathymetry is shading, not a 3D seafloor",
    };
  }
  return {
    source: "EOX Sentinel-2 cloudless 2020",
    native: "Sentinel-2 mosaic; map stops at zoom 12",
    date: "2020",
    chip: "Imagery: EOX Sentinel-2 cloudless 2020 · not a sharper biological map",
  };
}
