export type VisualTruthState =
  | "DIRECT_OBSERVATION"
  | "MODEL_INFERENCE"
  | "FORECAST"
  | "HABITAT_SUITABILITY"
  | "UNKNOWN"
  | "DATA_GAP"
  | "RESTRICTED_OR_COARSENED";

export type GlobeMode = "earth_surface" | "evidence_provenance" | "uncertainty_data_gap";

export type NavView = "find" | "explore" | "evidence" | "learn";

export type DepthBand = "surface" | "intertidal" | "0_10m" | "unknown_depth";

export type OverlayId = "sst" | "habitat" | "density";

/** The six prediction targets — never collapse into “where the fish are.” */
export type PredictionTarget =
  | "observed_presence"
  | "occurrence_probability"
  | "relative_abundance"
  | "movement"
  | "habitat_suitability"
  | "unknown";

/** What a drawn object may claim. Orthogonal to PredictionTarget. */
export type ScientificStatus =
  | "confirmed_observation"
  | "current_estimate"
  | "forecast"
  | "historical_pattern"
  | "favorable_habitat"
  | "unknown";

export type LayerKind = ScientificStatus | "coarsened" | "relative_abundance" | "movement";

export interface LayerResolutionMeta {
  kind: LayerKind;
  nativeSourceResolution: string;
  displayedTileResolution: string;
  validatedModelResolution: string | null;
  positionalUncertainty: string;
  timeResolution: string;
  depthResolution: string;
  coarseningReason: string | null;
}

export type ConfidenceCategory = "high" | "medium" | "low" | "none";

export type SpeciesStatus = "no_estimate" | "oyster_demo" | "name_only";

export type SpeciesGroup = "fish" | "crustacean" | "mollusc" | "other";

export interface CellProperties {
  cellId: string;
  label: string;
  visualTruthState: VisualTruthState;
  publishClass: "PUBLIC" | "COARSENED" | "PRIVATE";
  isOpsRiskExample: boolean;
  sstC: number;
  habitatClass: string;
  observationDensity: "none" | "low" | "medium" | "high";
  observationN: number;
  lastDirectObservation: string | null;
  confidence: ConfidenceCategory;
  depthSurface: boolean;
  depthIntertidal: boolean;
  depth0to10: boolean;
  depthUnknown: boolean;
  centerLon: number;
  centerLat: number;
}

export interface Evidence16 {
  currentEstimate: string;
  forecastEstimate: string;
  confidence: { category: ConfidenceCategory; reasons: string[] };
  lastDirectObservation: { at: string | null; note: string };
  observationCount: { n: number; window: string; note: string };
  observationTypes: string[];
  environmentalInputs: { name: string; value: string; asOf: string; role: string }[];
  keyModelDrivers: string[];
  comparableHistoricalConditions: string;
  modelVersion: string;
  validationPerformance: string;
  knownLimitations: string[];
  sourceLinksAndLicenses: { name: string; url: string; license: string; note: string }[];
  dataFreshness: string;
  privacyCoarsening: string;
  whatWouldReduceUncertainty: string[];
}

export interface HonestyAnswers {
  why: string;
  trust: string;
  missing: string;
  observedInferredForecast: string;
}

export interface OpsRiskBlock {
  wedge: string;
  species: string;
  geography: string;
  target: string;
  category: string;
  status: string;
  headline: string;
  notFoodSafety: boolean;
  notHarvestAuthorization: boolean;
  verifyWaDoh: boolean;
  airTimesTideNotSstAsBodyTemp: boolean;
  options: string[];
}

export interface CellRecord {
  evidence: Evidence16;
  answers: HonestyAnswers;
  opsRisk?: OpsRiskBlock;
}

export interface TimeReadout {
  forecastIssuedAt: string;
  validFrom: string;
  validTo: string;
  environmentalInputsCurrentThrough: string;
  lastDirectObservationInAoi: string;
  forecastConfidence: string;
  modelVersion: string;
  dataCoverage: string;
}

export interface MetaFixture {
  title: string;
  generatedAt: string;
  disclaimer: string;
  aoi: { name: string; kind: string; bbox: [number, number, number, number]; note: string };
  grid: { type: string; nominalAreaKm2: string; note: string };
  timeReadout: TimeReadout;
  cellCount: number;
  visualTruthStateCounts: Record<string, number>;
  opsRiskExampleCellId: string;
  modesInPrototype: string[];
  modesNotInPrototype: string[];
}

export interface TaxonRecord {
  aphiaId: number;
  scientificName: string;
  commonNames: string[];
  group: SpeciesGroup;
  status: SpeciesStatus;
  note?: string;
}

export interface ModelCardGate {
  aphiaId: number;
  scientificName: string;
  cardId: string;
  publishStatus: "NOT_PUBLISHED" | "PUBLISHED";
  operational: boolean;
  hasCurrentEstimate: boolean;
  hasForecast: boolean;
  hasRelativeAbundance: boolean;
  hasMovement: boolean;
  predictionTarget: PredictionTarget | null;
  allowsWillapaWorkingConditionsDemo?: boolean;
  target: string;
  reviewerStatus: string;
}

export interface AnswerStrip {
  species: string;
  whereNow: string;
  soon: string;
  howSure: string;
  depth: string;
  why: string;
  thisIsNot: string;
  whatShown?: string;
  quantityNote?: string;
  supportLine?: string;
  scientificStatus?: string;
  targetsNote?: string;
}

export interface PastReportsSummary {
  scientificName: string;
  total: number | null;
  yearSpan: string | null;
  cellsDrawn: number;
  withheld: boolean;
  source: string;
  licenseNote: string;
  error?: string;
}

export interface AppState {
  nav: NavView;
  expert: boolean;
  mode: GlobeMode;
  unknownMap: boolean;
  depth: DepthBand;
  overlays: { sst: boolean; habitat: boolean; density: boolean };
  selectedCellId: string | null;
  selectedTaxon: TaxonRecord | null;
  dimWillapa: boolean;
  pastReportsVisible: boolean;
  showWillapaCells: boolean;
  publishedCurrentEstimate: boolean;
  publishedForecast: boolean;
}

export const TRUTH_COLORS: Record<VisualTruthState, string> = {
  DIRECT_OBSERVATION: "#0072B2",
  MODEL_INFERENCE: "#E69F00",
  FORECAST: "#56B4E9",
  HABITAT_SUITABILITY: "#8C6D31",
  UNKNOWN: "#7A7A7A",
  DATA_GAP: "#5C5C5C",
  RESTRICTED_OR_COARSENED: "#CC79A7",
};

export const TRUTH_LABELS: Record<VisualTruthState, string> = {
  DIRECT_OBSERVATION: "Measured",
  MODEL_INFERENCE: "Guessed",
  FORECAST: "Future",
  HABITAT_SUITABILITY: "Habitat — not a sighting",
  UNKNOWN: "Don't know",
  DATA_GAP: "Don't know",
  RESTRICTED_OR_COARSENED: "Hidden on purpose",
};

export const PLAIN_TRUTH: Record<VisualTruthState, string> = {
  DIRECT_OBSERVATION: "measured",
  MODEL_INFERENCE: "guessed",
  FORECAST: "future",
  HABITAT_SUITABILITY: "habitat, not a sighting",
  UNKNOWN: "don't know",
  DATA_GAP: "don't know",
  RESTRICTED_OR_COARSENED: "hidden on purpose",
};

export const DEPTH_LABELS: Record<DepthBand, string> = {
  surface: "Surface water",
  intertidal: "Tide flat (air or water)",
  "0_10m": "0–10 meters",
  unknown_depth: "Depth unknown",
};

export const MODE_LABELS: Record<GlobeMode, string> = {
  earth_surface: "Map",
  evidence_provenance: "Sensors",
  uncertainty_data_gap: "Gaps",
};

export interface FixtureFeature<P> {
  type: "Feature";
  properties: P;
  geometry: {
    type: string;
    coordinates: unknown;
  };
}

export interface FixtureCollection<P = Record<string, unknown>> {
  type: "FeatureCollection";
  name?: string;
  features: FixtureFeature<P>[];
}
