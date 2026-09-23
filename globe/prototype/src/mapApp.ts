import {
  AttributionControl,
  GeoJSONSource,
  Map as MapLibreMap,
  NavigationControl,
  ScaleControl,
} from "maplibre-gl";
import type { FilterSpecification, MapLayerMouseEvent } from "maplibre-gl";
import { CUSTOM_ATTRIBUTION, installBasemap, resolutionForZoom } from "./basemap";
import {
  CAMERA,
  CameraHistory,
  bindFlightInterrupt,
  bindPointerSelectGuard,
  fitRegion,
  flyHome,
  flyToView,
  mapCameraOptions,
  motionMs,
  recastViewport,
  resetNorth as resetNorthCamera,
  resetTilt as resetTiltCamera,
  scheduleRecast,
  snapshotCamera,
  tuneNativeHandlers,
  type CameraSnapshot,
  type MapProjectionMode,
} from "./camera";
import { mayDrawCurrentEstimate, mayDrawForecast } from "./layers";
import { buildPatterns } from "./patterns";
import type { AppState, CellProperties, DepthBand, FixtureCollection } from "./types";
import { TRUTH_COLORS } from "./types";

export type { MapProjectionMode, CameraSnapshot };

const TRUTH_COLOR_EXPR = [
  "match",
  ["get", "visualTruthState"],
  "DIRECT_OBSERVATION",
  TRUTH_COLORS.DIRECT_OBSERVATION,
  "MODEL_INFERENCE",
  TRUTH_COLORS.MODEL_INFERENCE,
  "FORECAST",
  TRUTH_COLORS.FORECAST,
  "HABITAT_SUITABILITY",
  TRUTH_COLORS.HABITAT_SUITABILITY,
  "UNKNOWN",
  TRUTH_COLORS.UNKNOWN,
  "DATA_GAP",
  TRUTH_COLORS.DATA_GAP,
  "RESTRICTED_OR_COARSENED",
  TRUTH_COLORS.RESTRICTED_OR_COARSENED,
  "#888888",
] as unknown as never;

const FLAT_MAP_KEY = "fishai-prototype-flat-map";
const WILLAPA_BOUNDS: [[number, number], [number, number]] = [
  [-124.09, 46.36],
  [-123.78, 46.735],
];

const CELL_FILL_LAYERS = [
  "cells-fill",
  "cells-pattern-unknown",
  "cells-pattern-gap",
  "cells-pattern-restricted",
  "cells-pattern-habitat",
  "cells-pattern-inference",
  "cells-pattern-forecast",
  "cells-depth-missing",
  "cells-line",
  "cells-line-forecast",
  "cells-line-inference",
  "land-fill",
  "water-outline",
] as const;

function depthProperty(depth: DepthBand): string {
  if (depth === "surface") return "depthSurface";
  if (depth === "intertidal") return "depthIntertidal";
  if (depth === "0_10m") return "depth0to10";
  return "depthUnknown";
}

function depthSupportsExpr(depth: DepthBand): FilterSpecification {
  return ["==", ["get", depthProperty(depth)], true];
}

function notDepthExpr(depth: DepthBand): FilterSpecification {
  return ["!=", ["get", depthProperty(depth)], true];
}

function solidLineFilter(depth: DepthBand): FilterSpecification {
  return [
    "all",
    ["==", ["get", depthProperty(depth)], true],
    ["!=", ["get", "visualTruthState"], "FORECAST"],
    ["!=", ["get", "visualTruthState"], "MODEL_INFERENCE"],
  ];
}

function truthAndDepth(depth: DepthBand, state: string): FilterSpecification {
  return ["all", ["==", ["get", depthProperty(depth)], true], ["==", ["get", "visualTruthState"], state]];
}

function readFlatPreference(): boolean {
  try {
    return sessionStorage.getItem(FLAT_MAP_KEY) === "1";
  } catch {
    return false;
  }
}

function writeFlatPreference(flat: boolean): void {
  try {
    sessionStorage.setItem(FLAT_MAP_KEY, flat ? "1" : "0");
  } catch {
    /* session only */
  }
}

export function centroidsFromCells(
  cells: FixtureCollection<CellProperties>,
): FixtureCollection<CellProperties> {
  return {
    type: "FeatureCollection",
    features: cells.features.map((feature) => {
      const props = feature.properties as CellProperties;
      return {
        type: "Feature",
        properties: feature.properties,
        geometry: {
          type: "Point",
          coordinates: [props.centerLon, props.centerLat],
        },
      };
    }),
  };
}

export interface GlobeMap {
  map: MapLibreMap;
  apply: (state: AppState) => void;
  select: (cellId: string | null) => void;
  setPastReports: (data: FixtureCollection<{ n: number; label: string }> | null) => void;
  setAtlasMode: (mode: "willapa" | "world") => void;
  setProjectionMode: (mode: MapProjectionMode) => void;
  getProjectionMode: () => MapProjectionMode;
  resetNorth: () => void;
  resetTilt: () => void;
  showWorld: () => void;
  goBack: () => boolean;
  flyToPlace: (center: [number, number], zoom: number, bounds?: [[number, number], [number, number]]) => void;
  resolutionChip: () => string;
}

export async function createGlobeMap(options: {
  container: HTMLElement;
  land: FixtureCollection;
  water: FixtureCollection;
  cells: FixtureCollection<CellProperties>;
  stations: FixtureCollection;
  onSelect: (cellId: string) => void;
}): Promise<GlobeMap> {
  let projectionMode: MapProjectionMode = readFlatPreference() ? "mercator" : "globe";
  const history = new CameraHistory();

  const map = new MapLibreMap({
    container: options.container,
    style: "https://demotiles.maplibre.org/style.json",
    ...mapCameraOptions(projectionMode),
  });

  map.addControl(
    new AttributionControl({
      compact: true,
      customAttribution: CUSTOM_ATTRIBUTION,
    }),
    "bottom-right",
  );
  map.addControl(new NavigationControl({ showCompass: true, visualizePitch: true }), "top-right");
  map.addControl(new ScaleControl({ unit: "metric" }), "bottom-left");

  await map.once("load");

  map.setProjection({ type: projectionMode });
  map.setRenderWorldCopies(projectionMode === "mercator");
  map.setMaxBounds(null);
  tuneNativeHandlers(map);
  bindFlightInterrupt(map);
  const pointer = bindPointerSelectGuard(map);
  installBasemap(map);
  recastViewport(map);

  const patterns = buildPatterns();
  for (const [id, image] of Object.entries(patterns)) {
    if (!map.hasImage(id)) {
      map.addImage(id, image, { pixelRatio: 2 });
    }
  }

  const points = centroidsFromCells(options.cells);

  map.addSource("land", { type: "geojson", data: options.land });
  map.addSource("water", { type: "geojson", data: options.water });
  map.addSource("cells", { type: "geojson", data: options.cells, promoteId: "cellId" });
  map.addSource("centroids", { type: "geojson", data: points, promoteId: "cellId" });
  map.addSource("stations", { type: "geojson", data: options.stations });
  map.addSource("past-reports", {
    type: "geojson",
    data: { type: "FeatureCollection", features: [] },
  });

  map.addLayer({
    id: "land-fill",
    type: "fill",
    source: "land",
    layout: { visibility: "none" },
    paint: { "fill-color": "#d7cbb3", "fill-opacity": 0.55 },
  });
  map.addLayer({
    id: "water-outline",
    type: "line",
    source: "water",
    layout: { visibility: "none" },
    paint: { "line-color": "#e8f0f2", "line-width": 1.4, "line-dasharray": [3, 2] },
  });

  map.addLayer({
    id: "cells-fill",
    type: "fill",
    source: "cells",
    layout: { visibility: "none" },
    paint: {
      "fill-color": TRUTH_COLOR_EXPR,
      "fill-opacity": [
        "match",
        ["get", "visualTruthState"],
        "DIRECT_OBSERVATION",
        0.84,
        "MODEL_INFERENCE",
        0.36,
        "FORECAST",
        0.3,
        "HABITAT_SUITABILITY",
        0.42,
        "UNKNOWN",
        0.55,
        "DATA_GAP",
        0.5,
        "RESTRICTED_OR_COARSENED",
        0.4,
        0.4,
      ],
    },
  });

  map.addLayer({
    id: "cells-pattern-unknown",
    type: "fill",
    source: "cells",
    layout: { visibility: "none" },
    filter: ["==", ["get", "visualTruthState"], "UNKNOWN"],
    paint: { "fill-pattern": "hatch-unknown", "fill-opacity": 0.85 },
  });
  map.addLayer({
    id: "cells-pattern-gap",
    type: "fill",
    source: "cells",
    layout: { visibility: "none" },
    filter: ["==", ["get", "visualTruthState"], "DATA_GAP"],
    paint: { "fill-pattern": "hatch-gap", "fill-opacity": 0.9 },
  });
  map.addLayer({
    id: "cells-pattern-restricted",
    type: "fill",
    source: "cells",
    layout: { visibility: "none" },
    filter: ["==", ["get", "visualTruthState"], "RESTRICTED_OR_COARSENED"],
    paint: { "fill-pattern": "hatch-restricted", "fill-opacity": 0.85 },
  });
  map.addLayer({
    id: "cells-pattern-habitat",
    type: "fill",
    source: "cells",
    layout: { visibility: "none" },
    filter: ["==", ["get", "visualTruthState"], "HABITAT_SUITABILITY"],
    paint: { "fill-pattern": "hatch-habitat", "fill-opacity": 0.55 },
  });
  map.addLayer({
    id: "cells-pattern-inference",
    type: "fill",
    source: "cells",
    layout: { visibility: "none" },
    filter: ["==", ["get", "visualTruthState"], "MODEL_INFERENCE"],
    paint: { "fill-pattern": "hatch-inference", "fill-opacity": 0.45 },
  });
  map.addLayer({
    id: "cells-pattern-forecast",
    type: "fill",
    source: "cells",
    layout: { visibility: "none" },
    filter: ["==", ["get", "visualTruthState"], "FORECAST"],
    paint: { "fill-pattern": "hatch-forecast", "fill-opacity": 0.4 },
  });

  map.addLayer({
    id: "cells-depth-missing",
    type: "fill",
    source: "cells",
    layout: { visibility: "none" },
    filter: ["==", ["get", "cellId"], "__none__"],
    paint: { "fill-pattern": "hatch-depth-missing", "fill-opacity": 0.85 },
  });

  map.addLayer({
    id: "cells-line",
    type: "line",
    source: "cells",
    layout: { visibility: "none" },
    filter: solidLineFilter("surface"),
    paint: {
      "line-color": [
        "case",
        ["boolean", ["feature-state", "selected"], false],
        "#1c1710",
        TRUTH_COLOR_EXPR,
      ],
      "line-width": [
        "case",
        ["boolean", ["feature-state", "selected"], false],
        3.2,
        ["==", ["get", "isOpsRiskExample"], true],
        2.4,
        1.3,
      ],
    },
  });
  map.addLayer({
    id: "cells-line-forecast",
    type: "line",
    source: "cells",
    layout: { visibility: "none" },
    filter: ["==", ["get", "visualTruthState"], "FORECAST"],
    paint: {
      "line-color": TRUTH_COLORS.FORECAST,
      "line-width": 1.6,
      "line-dasharray": [2.2, 1.5],
    },
  });
  map.addLayer({
    id: "cells-line-inference",
    type: "line",
    source: "cells",
    layout: { visibility: "none" },
    filter: ["==", ["get", "visualTruthState"], "MODEL_INFERENCE"],
    paint: {
      "line-color": TRUTH_COLORS.MODEL_INFERENCE,
      "line-width": 1.6,
      "line-dasharray": [0.5, 1.3],
    },
  });

  map.addLayer({
    id: "cells-sst",
    type: "circle",
    source: "centroids",
    filter: [">", ["get", "sstC"], -900],
    layout: { visibility: "none" },
    paint: {
      "circle-radius": 9,
      "circle-color": [
        "interpolate",
        ["linear"],
        ["get", "sstC"],
        13,
        "#ffffd9",
        14.5,
        "#7fcdbb",
        16,
        "#1d91c0",
        17.5,
        "#225ea8",
      ],
      "circle-stroke-width": 1,
      "circle-stroke-color": "#1c1710",
      "circle-opacity": 0.92,
    },
  });

  map.addLayer({
    id: "cells-habitat-dots",
    type: "circle",
    source: "centroids",
    filter: ["!=", ["get", "habitatClass"], "not_applicable"],
    layout: { visibility: "none" },
    paint: {
      "circle-radius": 7,
      "circle-color": [
        "match",
        ["get", "habitatClass"],
        "reduced",
        "#e6d3a3",
        "typical",
        "#8c6d31",
        "elevated",
        "#543005",
        "#888888",
      ],
      "circle-stroke-width": 1,
      "circle-stroke-color": "#1c1710",
    },
  });

  map.addLayer({
    id: "cells-density",
    type: "symbol",
    source: "centroids",
    layout: {
      visibility: "none",
      "text-field": ["concat", "samples ", ["to-string", ["get", "observationN"]]],
      "text-size": 11,
      "text-font": ["Open Sans Regular", "Arial Unicode MS Regular"],
    },
    paint: {
      "text-color": "#1c1710",
      "text-halo-color": "#fffaf0",
      "text-halo-width": 1.4,
    },
  });

  map.addLayer({
    id: "stations",
    type: "circle",
    source: "stations",
    layout: { visibility: "none" },
    paint: {
      "circle-radius": 4,
      "circle-color": "#0072B2",
      "circle-stroke-width": 1.5,
      "circle-stroke-color": "#fffaf0",
    },
  });

  map.addLayer({
    id: "past-reports-fill",
    type: "fill",
    source: "past-reports",
    paint: {
      "fill-color": "#5c5346",
      "fill-opacity": 0.32,
      "fill-pattern": "hatch-gap",
    },
  });
  map.addLayer({
    id: "past-reports-line",
    type: "line",
    source: "past-reports",
    paint: {
      "line-color": "#3d4f55",
      "line-width": 1.2,
      "line-dasharray": [1, 1],
    },
  });

  map.addLayer({
    id: "cell-ids",
    type: "symbol",
    source: "centroids",
    layout: {
      visibility: "none",
      "text-field": ["get", "label"],
      "text-size": 11,
      "text-offset": [0, 1.3],
      "text-font": ["Open Sans Regular", "Arial Unicode MS Regular"],
    },
    paint: {
      "text-color": "#1c1710",
      "text-halo-color": "#efe7d6",
      "text-halo-width": 1.2,
      "text-opacity": 0.85,
    },
  });

  const click = (event: MapLayerMouseEvent): void => {
    if (pointer.wasDrag()) return;
    const feature = event.features?.[0];
    const id = feature?.properties?.["cellId"];
    if (typeof id === "string") options.onSelect(id);
  };
  const clickLayers = [
    "cells-fill",
    "cells-pattern-unknown",
    "cells-pattern-gap",
    "cells-pattern-restricted",
    "cells-pattern-habitat",
    "cells-pattern-inference",
    "cells-pattern-forecast",
    "cells-depth-missing",
  ];
  for (const layer of clickLayers) {
    map.on("mouseenter", layer, () => {
      map.getCanvas().style.cursor = "pointer";
    });
    map.on("mouseleave", layer, () => {
      map.getCanvas().style.cursor = "";
    });
    map.on("click", layer, click);
  }

  let selected: string | null = null;

  const select = (cellId: string | null) => {
    if (selected) {
      map.setFeatureState({ source: "cells", id: selected }, { selected: false });
    }
    selected = cellId;
    if (cellId) {
      map.setFeatureState({ source: "cells", id: cellId }, { selected: true });
    }
  };

  const setCellVisibility = (visible: boolean): void => {
    const value = visible ? "visible" : "none";
    for (const id of CELL_FILL_LAYERS) {
      if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", value);
    }
  };

  const apply = (state: AppState) => {
    const unknownOn = state.unknownMap || state.mode === "uncertainty_data_gap";
    const showCells = state.showWillapaCells;
    setCellVisibility(showCells);

    // Fixture inference/forecast encodings appear only in the Learn oyster demo.
    // A published species location or forecast layer requires an actual PUBLISHED card.
    const publishedNow = state.publishedCurrentEstimate || mayDrawCurrentEstimate(undefined);
    const publishedSoon = state.publishedForecast || mayDrawForecast(undefined);
    const showInference = showCells || publishedNow;
    const showForecast = showCells || publishedSoon;
    if (map.getLayer("cells-pattern-inference")) {
      map.setLayoutProperty("cells-pattern-inference", "visibility", showInference ? "visible" : "none");
    }
    if (map.getLayer("cells-line-inference")) {
      map.setLayoutProperty("cells-line-inference", "visibility", showInference ? "visible" : "none");
    }
    if (map.getLayer("cells-pattern-forecast")) {
      map.setLayoutProperty("cells-pattern-forecast", "visibility", showForecast ? "visible" : "none");
    }
    if (map.getLayer("cells-line-forecast")) {
      map.setLayoutProperty("cells-line-forecast", "visibility", showForecast ? "visible" : "none");
    }

    if (showCells) {
      map.setFilter("cells-depth-missing", notDepthExpr(state.depth));
      map.setFilter("cells-fill", depthSupportsExpr(state.depth));
      map.setFilter("cells-line", solidLineFilter(state.depth));
      map.setFilter("cells-pattern-unknown", truthAndDepth(state.depth, "UNKNOWN"));
      map.setFilter("cells-pattern-gap", truthAndDepth(state.depth, "DATA_GAP"));
      map.setFilter("cells-pattern-restricted", truthAndDepth(state.depth, "RESTRICTED_OR_COARSENED"));
      map.setFilter("cells-pattern-habitat", truthAndDepth(state.depth, "HABITAT_SUITABILITY"));
      map.setFilter("cells-pattern-inference", truthAndDepth(state.depth, "MODEL_INFERENCE"));
      map.setFilter("cells-pattern-forecast", truthAndDepth(state.depth, "FORECAST"));
      map.setFilter("cells-line-forecast", truthAndDepth(state.depth, "FORECAST"));
      map.setFilter("cells-line-inference", truthAndDepth(state.depth, "MODEL_INFERENCE"));
    }

    if (unknownOn && showCells) {
      map.setPaintProperty("cells-fill", "fill-color", [
        "match",
        ["get", "visualTruthState"],
        "UNKNOWN",
        "#bdbdbd",
        "DATA_GAP",
        "#9e9e9e",
        "RESTRICTED_OR_COARSENED",
        "#cc79a7",
        "#6a8f6b",
      ]);
      map.setPaintProperty("cells-fill", "fill-opacity", [
        "match",
        ["get", "visualTruthState"],
        "UNKNOWN",
        0.7,
        "DATA_GAP",
        0.75,
        "RESTRICTED_OR_COARSENED",
        0.45,
        0.22,
      ]);
    } else if (state.mode === "evidence_provenance" && showCells) {
      map.setPaintProperty("cells-fill", "fill-color", TRUTH_COLOR_EXPR);
      map.setPaintProperty("cells-fill", "fill-opacity", 0.28);
    } else if (showCells) {
      map.setPaintProperty("cells-fill", "fill-color", TRUTH_COLOR_EXPR);
      map.setPaintProperty("cells-fill", "fill-opacity", [
        "match",
        ["get", "visualTruthState"],
        "DIRECT_OBSERVATION",
        0.84,
        "MODEL_INFERENCE",
        0.36,
        "FORECAST",
        0.3,
        "HABITAT_SUITABILITY",
        0.42,
        "UNKNOWN",
        0.55,
        "DATA_GAP",
        0.5,
        "RESTRICTED_OR_COARSENED",
        0.4,
        0.4,
      ]);
    }

    const showSst = state.overlays.sst && !unknownOn && showCells;
    const showHabitat = state.overlays.habitat && !unknownOn && showCells;
    const showDensity = state.overlays.density && state.expert && showCells;
    map.setLayoutProperty("cells-sst", "visibility", showSst ? "visible" : "none");
    map.setLayoutProperty("cells-habitat-dots", "visibility", showHabitat ? "visible" : "none");
    map.setLayoutProperty("cells-density", "visibility", showDensity ? "visible" : "none");
    map.setLayoutProperty(
      "stations",
      "visibility",
      state.expert && state.mode === "evidence_provenance" && showCells ? "visible" : "none",
    );
    map.setLayoutProperty("cell-ids", "visibility", state.expert && showCells ? "visible" : "none");
  };

  const setPastReports = (data: FixtureCollection<{ n: number; label: string }> | null) => {
    const source = map.getSource("past-reports");
    if (source instanceof GeoJSONSource) {
      source.setData(data ?? { type: "FeatureCollection", features: [] });
    }
  };

  const remember = (): void => {
    history.push(map);
  };

  const showWorld = () => {
    remember();
    map.setMaxBounds(null);
    map.setMinZoom(CAMERA.MIN_ZOOM);
    flyHome(map, projectionMode);
    scheduleRecast(map);
  };

  const setAtlasMode = (mode: "willapa" | "world") => {
    map.setMaxBounds(null);
    map.setMinZoom(CAMERA.MIN_ZOOM);
    if (mode === "world") {
      showWorld();
      return;
    }
    remember();
    fitRegion(map, WILLAPA_BOUNDS, projectionMode, 10.4);
    scheduleRecast(map);
  };

  const setProjectionMode = (mode: MapProjectionMode) => {
    const snapped = snapshotCamera(map);
    projectionMode = mode;
    writeFlatPreference(mode === "mercator");
    map.setProjection({ type: mode });
    map.setRenderWorldCopies(mode === "mercator");
    const pitch = mode === "mercator" ? 0 : snapped.zoom < CAMERA.GLOBE_TILT_UNTIL_ZOOM ? CAMERA.WORLD_PITCH : snapped.pitch;
    const duration = motionMs(400);
    if (duration === 0) {
      map.jumpTo({ center: snapped.center, zoom: snapped.zoom, bearing: snapped.bearing, pitch });
      return;
    }
    map.easeTo({ center: snapped.center, zoom: snapped.zoom, bearing: snapped.bearing, pitch, duration });
    scheduleRecast(map);
  };

  const getProjectionMode = (): MapProjectionMode => projectionMode;

  const resetNorth = () => {
    resetNorthCamera(map, projectionMode);
  };

  const resetTilt = () => {
    resetTiltCamera(map, projectionMode);
  };

  const goBack = (): boolean => history.back(map);

  const flyToPlace = (
    center: [number, number],
    zoom: number,
    bounds?: [[number, number], [number, number]],
  ): void => {
    remember();
    if (bounds) {
      fitRegion(map, bounds, projectionMode, zoom);
      return;
    }
    flyToView(
      map,
      {
        center,
        zoom,
        pitch: projectionMode === "globe" && zoom < CAMERA.GLOBE_TILT_UNTIL_ZOOM ? CAMERA.WORLD_PITCH : Math.min(map.getPitch(), 48),
        bearing: 0,
      },
      860,
    );
  };

  const resolutionChip = (): string => resolutionForZoom(map.getZoom()).chip;

  apply({
    nav: "find",
    expert: false,
    mode: "earth_surface",
    unknownMap: false,
    depth: "unknown_depth",
    overlays: { sst: false, habitat: false, density: false },
    selectedCellId: null,
    selectedTaxon: null,
    dimWillapa: false,
    pastReportsVisible: false,
    showWillapaCells: false,
    publishedCurrentEstimate: false,
    publishedForecast: false,
  });

  map.jumpTo({
    center: CAMERA.WORLD_CENTER,
    zoom: CAMERA.WORLD_ZOOM,
    pitch: projectionMode === "globe" ? CAMERA.WORLD_PITCH : 0,
    bearing: 0,
  });
  scheduleRecast(map);
  map.once("idle", () => scheduleRecast(map));
  window.visualViewport?.addEventListener("resize", () => scheduleRecast(map));

  return {
    map,
    apply,
    select,
    setPastReports,
    setAtlasMode,
    setProjectionMode,
    getProjectionMode,
    resetNorth,
    resetTilt,
    showWorld,
    goBack,
    flyToPlace,
    resolutionChip,
  };
}

export function resizeLater(map: MapLibreMap): void {
  scheduleRecast(map);
}

export { FLAT_MAP_KEY, readFlatPreference };
