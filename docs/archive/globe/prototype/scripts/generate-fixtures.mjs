/**
 * Generate synthetic Willapa Bay fixtures for the Ocean Life Globe prototype.
 * Public water-body geography only. No OBIS/GBIF/AIS/GFW. No real leases.
 * Run: node scripts/generate-fixtures.mjs
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dir = dirname(fileURLToPath(import.meta.url));
const outDir = join(__dir, "..", "public", "fixtures");
mkdirSync(outDir, { recursive: true });

const ISSUED = "2026-09-18T23:00:00Z";
const VALID_FROM = "2026-09-18T23:00:00Z";
const VALID_TO = "2026-09-21T23:00:00Z";
const INPUTS_THROUGH = "2026-09-18T21:00:00Z";
const MODEL_VERSION = "GLOBE-PROTO-FIXTURE-2026-09-18-v0";

/** Approximate public water-body outline (not a survey, not DOH growing areas, not leases). */
const WILLAPA_WATER = [
  [-124.08, 46.73],
  [-123.96, 46.735],
  [-123.9, 46.71],
  [-123.84, 46.68],
  [-123.8, 46.64],
  [-123.81, 46.59],
  [-123.84, 46.54],
  [-123.83, 46.48],
  [-123.85, 46.43],
  [-123.89, 46.39],
  [-123.96, 46.365],
  [-124.03, 46.38],
  [-124.055, 46.44],
  [-124.05, 46.5],
  [-124.048, 46.56],
  [-124.055, 46.62],
  [-124.07, 46.68],
  [-124.08, 46.73],
];

const LAND = {
  type: "FeatureCollection",
  name: "approximate_public_land_masses",
  features: [
    {
      type: "Feature",
      properties: {
        name: "Long Beach Peninsula (approximate, not a cadastral map)",
        kind: "land",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-124.09, 46.35],
            [-124.035, 46.35],
            [-124.03, 46.55],
            [-124.038, 46.64],
            [-124.055, 46.705],
            [-124.08, 46.728],
            [-124.1, 46.7],
            [-124.09, 46.35],
          ],
        ],
      },
    },
    {
      type: "Feature",
      properties: {
        name: "Willapa mainland (approximate, not a cadastral map)",
        kind: "land",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-123.78, 46.35],
            [-123.62, 46.35],
            [-123.62, 46.76],
            [-123.88, 46.76],
            [-123.94, 46.72],
            [-123.9, 46.69],
            [-123.82, 46.66],
            [-123.78, 46.58],
            [-123.79, 46.48],
            [-123.81, 46.4],
            [-123.78, 46.35],
          ],
        ],
      },
    },
  ],
};

function pointInRing(lon, lat, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0];
    const yi = ring[i][1];
    const xj = ring[j][0];
    const yj = ring[j][1];
    const intersect =
      yi > lat !== yj > lat && lon < ((xj - xi) * (lat - yi)) / (yj - yi + 0.0) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

function hexPolygon(lon, lat, radiusLatDeg) {
  const coords = [];
  const lonScale = Math.cos((lat * Math.PI) / 180);
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI / 180) * (60 * i - 30);
    coords.push([
      lon + (radiusLatDeg * Math.cos(angle)) / lonScale,
      lat + radiusLatDeg * Math.sin(angle),
    ]);
  }
  coords.push(coords[0]);
  return coords;
}

function hexCenters(radiusLatDeg) {
  const lat0 = 46.54;
  const lon0 = -123.97;
  const lonScale = Math.cos((lat0 * Math.PI) / 180);
  const size = radiusLatDeg;
  const out = [];
  for (let q = -8; q <= 8; q++) {
    for (let r = -8; r <= 8; r++) {
      const x = size * Math.sqrt(3) * (q + r / 2);
      const y = size * 1.5 * r;
      const lat = lat0 + y;
      const lon = lon0 + x / lonScale;
      if (pointInRing(lon, lat, WILLAPA_WATER)) {
        out.push({ lon, lat, q, r });
      }
    }
  }
  out.sort((a, b) => b.lat - a.lat || a.lon - b.lon);
  return out;
}

function dist2(a, b) {
  const dlon = (a.lon - b.lon) * Math.cos((46.5 * Math.PI) / 180);
  const dlat = a.lat - b.lat;
  return dlon * dlon + dlat * dlat;
}

function nearestIndex(centers, lon, lat) {
  let best = 0;
  let bestD = Infinity;
  centers.forEach((c, i) => {
    const d = dist2(c, { lon, lat });
    if (d < bestD) {
      bestD = d;
      best = i;
    }
  });
  return best;
}

function placeName(lon, lat) {
  if (lat >= 46.68) return "Northern entrance (Shoalwater / Toke Point reach)";
  if (lat >= 46.6 && lon > -123.92) return "Northeast reach (Tokeland–South Bend water)";
  if (lon <= -124.02 && lat >= 46.52) return "Peninsula inner shore, north (public water)";
  if (lon <= -124.02) return "Peninsula inner shore, Nahcotta–Oysterville reach (public water)";
  if (lat <= 46.42) return "South Bay (public water)";
  if (lat <= 46.5) return "Southern central Willapa (public water)";
  if (lon > -123.9) return "Eastern channel (public water)";
  return "Central Willapa Bay (public water)";
}

function linksContextOnly() {
  return [
    {
      name: "WA DOH Commercial Shellfish Map Viewer",
      url: "https://fortress.wa.gov/doh/oswpviewer/index.html",
      license: "Official public page (not ingested)",
      note: "Context link only. This app does not model harvest open/closed and did not download growing-area polygons.",
    },
    {
      name: "WA DOH Growing Area Closures",
      url: "https://fortress.wa.gov/doh/eh/portal/odw/si/GrowingAreaClosures.aspx",
      license: "Official public page (not ingested)",
      note: "Those pages win on harvest legality. This globe never paints open/closed.",
    },
    {
      name: "NOAA CO-OPS Toke Point (9440910) — named analog only",
      url: "https://tidesandcurrents.noaa.gov/stationhome.html?id=9440910",
      license: "Not ingested in this prototype",
      note: "Fixture timestamps do not come from this station. Named so operators know what a real brief would cite.",
    },
  ];
}

function baseEvidence(cell) {
  return {
    currentEstimate: "",
    forecastEstimate: "",
    confidence: { category: "none", reasons: [] },
    lastDirectObservation: {
      at: null,
      note: "No direct observation in the fixture for this cell.",
    },
    observationCount: {
      n: 0,
      window: "2026-09-11 through 2026-09-18 (fixture window)",
      note: "Counts are synthetic protocol rows, not animals.",
    },
    observationTypes: [],
    environmentalInputs: [],
    keyModelDrivers: ["None issued — see visual-truth state."],
    comparableHistoricalConditions: "No comparison set issued for this cell.",
    modelVersion: MODEL_VERSION,
    validationPerformance:
      "Never evaluated. This prototype has no skill score, no calibration plot, and no prospective window.",
    knownLimitations: [
      "Fixture / synthetic data only (generated 2026-09-18).",
      "Not a live animal map.",
      "Approximate public water-body cells, not farm leases and not DOH growing-area polygons.",
      "No OBIS, GBIF, AIS, GFW, or catch locations.",
    ],
    sourceLinksAndLicenses: linksContextOnly(),
    dataFreshness: `Inputs current through ${INPUTS_THROUGH} in the fixture clock. Nothing was fetched live.`,
    privacyCoarsening: cell.publishClass,
    whatWouldReduceUncertainty: [],
  };
}

function answers(why, trust, missing, classPhrase) {
  return { why, trust, missing, observedInferredForecast: classPhrase };
}

function evidenceDirect(cell, stationId, tempC, observedAt) {
  const e = baseEvidence(cell);
  e.currentEstimate = `DIRECT_OBSERVATION (fixture): in-water temperature ${tempC.toFixed(1)} °C at fictional station ${stationId}. Units: °C, water — not oyster tissue, not a fish count.`;
  e.forecastEstimate = "No forecast issued from this observation. A temperature reading is not a 72h ops-stress rank.";
  e.confidence = {
    category: "medium",
    reasons: [
      "FRESH:ok — fixture timestamp inside the demo window",
      "DENSITY:low — one fictional station, not a survey",
      "IN_DOMAIN:n/a — not a trained model",
      "LABEL_SUPPORT:none — no biological labels",
    ],
  };
  e.lastDirectObservation = {
    at: observedAt,
    note: `${stationId} water temperature (fixture). Method: fictional in-situ sensor. Not an animal.`,
  };
  e.observationCount = {
    n: cell.observationN,
    window: "last 7 days (fixture)",
    note: "Synthetic hourly samples at one point. Not abundance.",
  };
  e.observationTypes = ["in-situ temperature (fixture sensor)", "no survey", "no tag", "no eDNA", "no catch/effort"];
  e.environmentalInputs = [
    {
      name: "In-water temperature",
      value: `${tempC.toFixed(1)} °C`,
      asOf: observedAt,
      role: "DIRECTLY measured at a fictional point (water), not tissue",
    },
  ];
  e.keyModelDrivers = ["None. This cell is an observation, not a model field."];
  e.comparableHistoricalConditions =
    "Not computed. A single station does not define a tercile of ops-stress.";
  e.knownLimitations.push(
    "Point measurement ≠ lease or bay mean.",
    "No depth profile; intake depth is unknown in the fixture (unknown-depth flag applies if you ask for 0–10 m biology).",
  );
  e.whatWouldReduceUncertainty = [
    "A real permissioned on-site logger with documented depth and calibration.",
    "A survey protocol if the question is biological — temperature is not that protocol.",
  ];
  e.privacyCoarsening = `PUBLIC coarsened cell ${cell.cellId}. Station coordinates are fictional and snapped to the cell, not a secret GPS.`;
  return {
    evidence: e,
    answers: answers(
      `A fixture in-situ temperature was recorded at ${stationId}. That is the only claim.`,
      "Trust the number as a demo temperature, not as oyster or fish presence. Medium confidence on the sensor story; none on biology.",
      "On-cell biology, tissue temperature, dissolved oxygen, toxin tests, harvest status.",
      "OBSERVED (environmental). Not inferred occupancy. Not a forecast.",
    ),
  };
}

function evidenceForecast(cell, isOps) {
  const e = baseEvidence(cell);
  if (isOps) {
    e.currentEstimate =
      "No current biological estimate. Planted oysters are not being counted. This cell carries a Category D operational-stress indicator (fixture).";
    e.forecastEstimate =
      "FORECAST (fixture): Elevated 72h operational stress / work-window indicator vs a fictional late-summer comparable-tide set for this coarsened public cell. Rank: upper tercile of that set. Not a probability. Not % dead.";
    e.confidence = {
      category: "low",
      reasons: [
        "FRESH:ok on fixture NWS-analog / tide-analog clocks",
        "DENSITY:low — no on-cell sensors",
        "LABEL_SUPPORT:none — no farm outcomes",
        "CALIBRATION_OK:low — never evaluated",
        "Rule: SST-only would be Low or None; this demo uses air × daytime emersion, still Low without lease sensors",
      ],
    };
    e.lastDirectObservation = {
      at: "2026-09-17T18:40:00Z",
      note: "Nearest fixture station is off-cell. Not a lease logger. Not an animal observation.",
    };
    e.observationCount = {
      n: 0,
      window: "72h forecast window",
      note: "Zero biological observations. Ops-stress is not a count.",
    };
    e.observationTypes = ["none on cell", "forecast inputs are environmental analogs (not ingested)"];
    e.environmentalInputs = [
      {
        name: "Forecast air × daytime low-tide emersion × solar geometry",
        value: "overlap flagged Sat–Sun in the fixture clock",
        asOf: INPUTS_THROUGH,
        role: "PRIMARY driver — not SST, not body temperature",
      },
      {
        name: "Wind / seas workability",
        value: "above a fictional easy-work rule of thumb",
        asOf: INPUTS_THROUGH,
        role: "PRIMARY operational input",
      },
      {
        name: "Synthetic SST (supporting only)",
        value: cell.sstC === null ? "missing" : `${cell.sstC.toFixed(1)} °C water skin`,
        asOf: INPUTS_THROUGH,
        role: "SUPPORTING covariate with spatial mismatch — not oyster tissue temperature",
      },
    ];
    e.keyModelDrivers = [
      "Air temperature overlapping daytime emersion (PRIMARY)",
      "Wind/wave workability (PRIMARY)",
      "Water T/DO/S if present are supporting only and were NOT used as a kill law",
    ];
    e.comparableHistoricalConditions =
      "Fixture comparison set: this coarsened cell, similar tides, late-summer season. Not a calibrated climatology. Not 'top 20%'. Tercile only.";
    e.knownLimitations.push(
      "NOT food-safety. NOT harvest authorization. NOT NSSP. NOT a toxin test.",
      "Satellite or fixture SST is not oyster body temperature.",
      "Does not replace WAC 246-282-006 / the Vp control plan.",
      "Air×tide language is physical exposure, not mortality.",
      "No on-lease microclimate, ploidy, handling, or last-14d mortality.",
    );
    e.whatWouldReduceUncertainty = [
      "Permissioned on-lease air/emersion loggers timed to the tide clock.",
      "Partner workability / protocol mortality outcomes (PRIVATE).",
      "A prospective scoring window — none exists yet.",
    ];
    e.privacyCoarsening =
      "PUBLIC coarsened water-body cell. NOT a farm lease polygon. PRIVATE operational outcomes are not on this map. Exact farm performance is withheld.";
  } else {
    e.currentEstimate = "No current occupancy issued.";
    e.forecastEstimate = `FORECAST (fixture): 24–72h environmental-workability context for ${cell.label}. Dashed encoding = future window. Not species presence.`;
    e.confidence = {
      category: "low",
      reasons: ["Forecast-only fixture", "No biological labels", "Unvalidated"],
    };
    e.lastDirectObservation = { at: null, note: "None in this cell." };
    e.observationCount = { n: 0, window: "72h", note: "Zero biological rows." };
    e.observationTypes = ["forecast environmental analog only"];
    e.environmentalInputs = [
      {
        name: "Fixture NWP-analog air/wind",
        value: "see time readout",
        asOf: INPUTS_THROUGH,
        role: "forecast driver",
      },
    ];
    e.keyModelDrivers = ["Forecast air/wind analog — not SST=animals"];
    e.whatWouldReduceUncertainty = ["Direct observations in this cell and depth band."];
    e.privacyCoarsening = `COARSENED public cell ${cell.cellId}.`;
  }
  return {
    evidence: e,
    answers: answers(
      isOps
        ? "A fixture rule flagged forecast air overlapping daytime emersion plus wind/wave workability. That is an operational-stress indicator, not a census."
        : "The fixture clock has a forecast environmental field here. Nothing was observed on cell.",
      "Low. Unvalidated. Do not change a high-cost action on this demo.",
      isOps
        ? "On-lease sensors, ploidy, handling, HAB toxin (always missing from this target), last-14d mortality, official harvest status as a model input (forbidden)."
        : "Any biological observation; depth-resolved records; validation.",
      "FORECAST. Not observed. Not a present-time occupancy inference.",
    ),
  };
}

function evidenceInference(cell) {
  const e = baseEvidence(cell);
  e.currentEstimate = `MODEL_INFERENCE (fixture): relative environmental-stress / workability inference for ${cell.label}. Dotted, translucent on purpose. Not occupancy. Not abundance.`;
  e.forecastEstimate = "No separate forecast layer on this cell. Inference is a present-window rule output from fixture drivers.";
  e.confidence = {
    category: "low",
    reasons: ["No local labels", "Rule is unvalidated", "Observation density low"],
  };
  e.lastDirectObservation = { at: null, note: "None. Inference is not an observation." };
  e.observationCount = { n: cell.observationN, window: "7d fixture", note: "Sparse or zero protocol rows." };
  e.observationTypes = ["none sufficient", "environmental proxies only"];
  e.environmentalInputs = [
    {
      name: "Fixture air / tide analog",
      value: "present-window",
      asOf: INPUTS_THROUGH,
      role: "inference driver — not body temperature",
    },
  ];
  e.keyModelDrivers = ["Unvalidated air×tide rule (fixture)", "Not chlorophyll", "Not AIS"];
  e.comparableHistoricalConditions = "No locked comparison set. Do not read this as a percentile of animals.";
  e.whatWouldReduceUncertainty = [
    "Direct observations with a protocol.",
    "A named baseline evaluated in a prospective lane.",
  ];
  e.privacyCoarsening = `PUBLIC coarsened cell. Inference is not a reason to publish finer geometry.`;
  return {
    evidence: e,
    answers: answers(
      "A fixture environmental rule was applied. Rules are not animals.",
      "Low. Treat as a watch on the method, not a sure bet on biology.",
      "Protocol observations, depth, calibration, farm/vessel outcomes.",
      "INFERRED. Not observed. Not a forecast plume.",
    ),
  };
}

function evidenceHabitat(cell, rank) {
  const e = baseEvidence(cell);
  e.currentEstimate = `HABITAT_SUITABILITY (fixture): estuarine intertidal / shallow-water habitat class = ${rank}. Separate palette from observations and from ops-stress. Not presence. Not abundance. Not a farm score.`;
  e.forecastEstimate = "Habitat class is a slow spatial prior in this prototype, not a 72h forecast.";
  e.confidence = {
    category: "low",
    reasons: ["Literature-like envelope only", "No substrate survey ingested", "T1-style prior, not T3"],
  };
  e.lastDirectObservation = { at: null, note: "No habitat survey row in the fixture." };
  e.observationCount = { n: 0, window: "n/a", note: "Envelope, not a count." };
  e.observationTypes = ["none — habitat class is not an observation type"];
  e.environmentalInputs = [
    {
      name: "Estuary / intertidal setting (public geography)",
      value: rank,
      asOf: "static fixture",
      role: "habitat prior",
    },
  ];
  e.keyModelDrivers = ["Coarse estuary class only. Not SST-as-oysters."];
  e.comparableHistoricalConditions = "Not an anomaly. No reference climatology of habitat was computed.";
  e.whatWouldReduceUncertainty = ["A real benthic/substrate survey with rights clearance."];
  e.privacyCoarsening = "PUBLIC water-body. Habitat is not a lease map.";
  return {
    evidence: e,
    answers: answers(
      "The cell sits in a coarsened public estuary polygon, so a habitat class was assigned as a prior.",
      "Low as a biological claim. Habitat ≠ anyone is there.",
      "Substrate, emersion hours measured on site, any species observation.",
      "HABITAT PRIOR. Not observed presence. Not a forecast of animals.",
    ),
  };
}

function evidenceGap(cell, kind) {
  const e = baseEvidence(cell);
  const label = kind === "UNKNOWN" ? "UNKNOWN / insufficient evidence" : "DATA_GAP — no fixture in this cell×window";
  e.currentEstimate = `${label}. This is a successful product state. It is not zero animals and not 'safe' or 'empty'.`;
  e.forecastEstimate = "Cannot issue. No forecast is drawn through a gap.";
  e.confidence = {
    category: "none",
    reasons: [
      "No recent direct observations in this coarsened cell",
      "No depth-specific biological records",
      "No validated survey data",
      "Issuing a filled heatmap here would be interpolation theater",
    ],
  };
  e.lastDirectObservation = { at: null, note: "None." };
  e.observationCount = { n: 0, window: "7d fixture", note: "Zero. Gap ≠ absence." };
  e.observationTypes = ["none"];
  e.environmentalInputs = [];
  e.keyModelDrivers = ["None issued."];
  e.comparableHistoricalConditions = "Not computed across gaps. No kriging of animals.";
  e.whatWouldReduceUncertainty = [
    "A designed survey or permissioned sensor in this cell and depth band.",
    "Season-matched repeats — one visit does not close a gap forever.",
    "Declared depth. Unknown depth blocks High confidence.",
  ];
  e.privacyCoarsening =
    kind === "RESTRICTED_OR_COARSENED"
      ? "RESTRICTED_OR_COARSENED: geometry is intentionally large. Private farm or fine-scale data are not shown."
      : "PUBLIC cell with nothing to show. Hiding the hatch would be the dishonest option.";
  if (kind === "RESTRICTED_OR_COARSENED") {
    e.currentEstimate =
      "RESTRICTED_OR_COARSENED: values that would identify a farm, string, or fine location are withheld. You are looking at a privacy-preserving empty/coarse cell, not a biological zero.";
    e.forecastEstimate = "No public forecast at a finer grain.";
    e.observationTypes = ["withheld"];
  }
  const classPhrase =
    kind === "RESTRICTED_OR_COARSENED"
      ? "WITHHELD / COARSENED. Not observed. Not a public inference."
      : "UNKNOWN. Not observed. Not inferred. Not forecast. Not absence.";
  return {
    evidence: e,
    answers: answers(
      kind === "RESTRICTED_OR_COARSENED"
        ? "Privacy / coarsening rules forbid showing a finer public claim here."
        : "The fixture contains no supporting observation or validated model for this cell.",
      "Do not trust a filled-in animal story. Confidence is None. That is the product.",
      kind === "RESTRICTED_OR_COARSENED"
        ? "Permission from the data owner; even then public grain stays coarse."
        : "Any protocol observation at this depth and season; a model that has been evaluated rather than interpolated.",
      classPhrase,
    ),
  };
}

const STATES = [
  "DIRECT_OBSERVATION",
  "FORECAST",
  "MODEL_INFERENCE",
  "HABITAT_SUITABILITY",
  "UNKNOWN",
  "DATA_GAP",
  "RESTRICTED_OR_COARSENED",
];

function assignStates(n, opsIdx, tokeIdx) {
  const states = Array(n).fill("DATA_GAP");
  const pattern = [
    "DIRECT_OBSERVATION",
    "MODEL_INFERENCE",
    "FORECAST",
    "HABITAT_SUITABILITY",
    "UNKNOWN",
    "DATA_GAP",
    "RESTRICTED_OR_COARSENED",
    "MODEL_INFERENCE",
    "FORECAST",
    "HABITAT_SUITABILITY",
    "DATA_GAP",
    "UNKNOWN",
    "DIRECT_OBSERVATION",
    "MODEL_INFERENCE",
    "FORECAST",
    "DATA_GAP",
  ];
  for (let i = 0; i < n; i++) states[i] = pattern[i % pattern.length];
  states[opsIdx] = "FORECAST";
  states[tokeIdx] = "DIRECT_OBSERVATION";
  return states;
}

const radius = 0.026;
const centers = hexCenters(radius);
if (centers.length < 12) {
  throw new Error(`Too few cells: ${centers.length}`);
}

const opsIdx = nearestIndex(centers, -124.02, 46.5);
const tokeIdx = nearestIndex(centers, -123.97, 46.71);
const southIdx = nearestIndex(centers, -123.95, 46.4);
const states = assignStates(centers.length, opsIdx, tokeIdx);

const habitatCycle = ["reduced", "typical", "elevated"];
const cells = [];
const evidenceByCell = {};
const stations = [];

centers.forEach((c, i) => {
  const cellId = `WILLAPA-C${String(i + 1).padStart(2, "0")}`;
  const visualTruthState = states[i];
  const isOps = i === opsIdx;
  const label = isOps
    ? "Nahcotta-adjacent public water (W1 OPS-RISK example cell)"
    : placeName(c.lon, c.lat);
  const sst =
    visualTruthState === "DATA_GAP" || visualTruthState === "UNKNOWN"
      ? null
      : 14.2 + (c.lat - 46.36) * 4.5 + (c.lon + 124.0) * 1.2;
  const sstC = sst === null ? null : Math.round(sst * 10) / 10;

  let depthSurface = true;
  let depthIntertidal = false;
  let depth0to10 = false;
  let depthUnknown = false;
  if (visualTruthState === "FORECAST" || visualTruthState === "HABITAT_SUITABILITY" || isOps) {
    depthIntertidal = true;
  }
  if (visualTruthState === "DIRECT_OBSERVATION" || visualTruthState === "MODEL_INFERENCE") {
    depth0to10 = i % 3 === 0;
  }
  if (visualTruthState === "DATA_GAP" || visualTruthState === "UNKNOWN") {
    depthUnknown = true;
    depthSurface = visualTruthState === "UNKNOWN";
  }
  if (visualTruthState === "RESTRICTED_OR_COARSENED") {
    depthUnknown = true;
    depthSurface = true;
  }

  const observationN =
    visualTruthState === "DIRECT_OBSERVATION"
      ? 24 + (i % 7)
      : visualTruthState === "MODEL_INFERENCE"
        ? 2 + (i % 3)
        : visualTruthState === "FORECAST"
          ? 0
          : 0;

  const observationDensity =
    observationN === 0 ? "none" : observationN < 8 ? "low" : observationN < 20 ? "medium" : "high";

  const publishClass =
    visualTruthState === "RESTRICTED_OR_COARSENED" ? "COARSENED" : "PUBLIC";

  const habitatClass =
    visualTruthState === "HABITAT_SUITABILITY" ? habitatCycle[i % 3] : "not_applicable";

  const lastObs =
    visualTruthState === "DIRECT_OBSERVATION"
      ? i === tokeIdx
        ? "2026-09-18T16:10:00Z"
        : i === southIdx
          ? "2026-09-17T18:40:00Z"
          : "2026-09-16T21:05:00Z"
      : isOps
        ? "2026-09-17T18:40:00Z"
        : null;

  const cell = {
    cellId,
    label,
    visualTruthState,
    publishClass,
    isOpsRiskExample: isOps,
    sstC,
    habitatClass,
    observationDensity,
    observationN,
    lastDirectObservation: lastObs,
    confidence:
      visualTruthState === "DIRECT_OBSERVATION"
        ? "medium"
        : visualTruthState === "DATA_GAP" ||
            visualTruthState === "UNKNOWN" ||
            visualTruthState === "RESTRICTED_OR_COARSENED"
          ? "none"
          : "low",
    depthSurface,
    depthIntertidal,
    depth0to10,
    depthUnknown,
    centerLon: Math.round(c.lon * 10000) / 10000,
    centerLat: Math.round(c.lat * 10000) / 10000,
  };

  let packed;
  if (visualTruthState === "DIRECT_OBSERVATION") {
    const sid =
      i === tokeIdx ? "FIXTURE-STATION-TOKE" : i === southIdx ? "FIXTURE-STATION-SOUTH" : `FIXTURE-STATION-${cellId}`;
    packed = evidenceDirect(cell, sid, sstC ?? 15.0, lastObs);
    stations.push({
      id: sid,
      cellId,
      lon: c.lon,
      lat: c.lat,
      observedAt: lastObs,
      variable: "sea_water_temperature",
      valueC: sstC,
      note: "Fictional in-water sensor. Not an animal. Not a farm.",
    });
  } else if (visualTruthState === "FORECAST") {
    packed = evidenceForecast(cell, isOps);
  } else if (visualTruthState === "MODEL_INFERENCE") {
    packed = evidenceInference(cell);
  } else if (visualTruthState === "HABITAT_SUITABILITY") {
    packed = evidenceHabitat(cell, habitatClass);
  } else {
    packed = evidenceGap(cell, visualTruthState);
  }

  if (isOps) {
    packed.opsRisk = {
      wedge: "W1",
      species: "Pacific oyster (Magallana gigas / Crassostrea gigas), AphiaID 836033",
      geography:
        "Willapa Bay, Washington — coarsened PUBLIC water-body cell. Not a farm lease. Not Totten Inlet. Not a Vp Category 3 harvest-control demo.",
      target: "Category D 72h operational disruption / environmental-stress indicator (workability, emersion-heat, wave/gear).",
      category: "D",
      status: "ELEVATED (fixture tercile, not a calibrated probability)",
      headline:
        "Elevated operational stress indicator for coarsened public cell WILLAPA-C" +
        String(i + 1).padStart(2, "0") +
        " over the next 72 hours, associated with forecast air temperature overlapping daytime emersion and wave/wind exposure. Comparison set: this cell, similar tides, late-summer season (FIXTURE). Confidence: Low. Category D. Strongest evidence: Tier 3 forecast only. This is not a food-safety determination and not harvest authorization. Verify official growing-area and biotoxin status with the Washington State Department of Health (and tribal or FDA authorities where applicable). Satellite temperature is not oyster body temperature and is not a tissue toxin test. It does not replace the Vibrio parahaemolyticus control plan (WAC 246-282-006).",
      notFoodSafety: true,
      notHarvestAuthorization: true,
      verifyWaDoh: true,
      airTimesTideNotSstAsBodyTemp: true,
      options: [
        "A. Consider shifting labor off the hottest daytime emersion.",
        "B. Consider increasing monitoring on the daylight tide.",
        "C. Consider inspecting gear after the forecast wave/wind event.",
        "D. Keep the current plan if your on-site read disagrees.",
        "Choose none if official DOH status, your Vp plan, or your observations disagree. Never 'harvest now'.",
      ],
    };
  }

  evidenceByCell[cellId] = packed;

  cells.push({
    type: "Feature",
    properties: {
      ...cell,
      sstC: sstC === null ? -999 : sstC,
    },
    geometry: {
      type: "Polygon",
      coordinates: [hexPolygon(c.lon, c.lat, radius * 0.92)],
    },
  });
});

const stateCounts = {};
for (const s of STATES) stateCounts[s] = 0;
for (const f of cells) stateCounts[f.properties.visualTruthState] += 1;

const meta = {
  title: "FishAI Ocean Life Globe prototype — Willapa Bay fixture",
  generatedAt: "2026-09-18",
  disclaimer:
    "ALL DATA ARE SYNTHETIC FIXTURES generated locally on 2026-09-18. This is not a live fish map, not a harvest map, not a farm-performance map, and not an endangered-species map. No OBIS, GBIF, AIS, GFW, or catch locations were downloaded. Approximate public water-body geography only.",
  aoi: {
    name: "Willapa Bay, Washington, USA",
    kind: "named public water body (approximate bbox/outline)",
    bbox: [-124.12, 46.34, -123.62, 46.76],
    note: "Not a farm lease map. Not WA DOH growing-area polygons. Not for navigation.",
  },
  grid: {
    type: "H3-like hexagons generated locally",
    nominalAreaKm2: "~20",
    note: "Not Uber H3 indexes. Coarser than a farm. Area is approximate; hexes are not equal-area on the ellipsoid.",
  },
  timeReadout: {
    forecastIssuedAt: ISSUED,
    validFrom: VALID_FROM,
    validTo: VALID_TO,
    environmentalInputsCurrentThrough: INPUTS_THROUGH,
    lastDirectObservationInAoi: "2026-09-18T16:10:00Z",
    forecastConfidence: "low",
    modelVersion: MODEL_VERSION,
    dataCoverage: `${cells.length} coarsened cells; ${stateCounts.DATA_GAP} DATA_GAP; ${stateCounts.UNKNOWN} UNKNOWN; 0 live ingest`,
  },
  cellCount: cells.length,
  visualTruthStateCounts: stateCounts,
  opsRiskExampleCellId: cells[opsIdx].properties.cellId,
  modesInPrototype: ["earth_surface", "evidence_provenance", "uncertainty_data_gap"],
  modesNotInPrototype: [
    "semi_transparent_subsurface",
    "vertical_depth_slice",
    "horizontal_depth_slice",
    "seafloor_habitat",
    "timelapse_forecast",
    "side_by_side_comparison",
    "ecosystem_foodweb",
  ],
};

const waterOutline = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        name: "Willapa Bay approximate public water-body outline",
        note: "Not a shoreline survey. Not DOH. Not leases.",
      },
      geometry: { type: "Polygon", coordinates: [WILLAPA_WATER] },
    },
  ],
};

const cellFc = {
  type: "FeatureCollection",
  name: "willapa_fixture_cells",
  features: cells,
};

const stationFc = {
  type: "FeatureCollection",
  name: "fictional_in_water_sensors",
  features: stations.map((s) => ({
    type: "Feature",
    properties: {
      id: s.id,
      cellId: s.cellId,
      observedAt: s.observedAt,
      variable: s.variable,
      valueC: s.valueC,
      units: "°C",
      note: s.note,
    },
    geometry: { type: "Point", coordinates: [s.lon, s.lat] },
  })),
};

writeFileSync(join(outDir, "meta.json"), JSON.stringify(meta, null, 2));
writeFileSync(join(outDir, "willapa-cells.geojson"), JSON.stringify(cellFc, null, 2));
writeFileSync(join(outDir, "willapa-land.geojson"), JSON.stringify(LAND, null, 2));
writeFileSync(join(outDir, "willapa-water-outline.geojson"), JSON.stringify(waterOutline, null, 2));
writeFileSync(join(outDir, "stations.geojson"), JSON.stringify(stationFc, null, 2));
writeFileSync(join(outDir, "evidence-by-cell.json"), JSON.stringify(evidenceByCell, null, 2));

console.log(`Wrote ${cells.length} cells to ${outDir}`);
console.log("Counts", stateCounts);
console.log("OPS-RISK example", cells[opsIdx].properties.cellId);
