import type { LayerKind, LayerResolutionMeta, ModelCardGate, PastReportsSummary, PredictionTarget } from "./types";

export const GOLIATH_APHIA_ID = 159353;

export const PREDICTION_TARGETS: readonly PredictionTarget[] = [
  "observed_presence",
  "occurrence_probability",
  "relative_abundance",
  "movement",
  "habitat_suitability",
  "unknown",
];

export function mayDrawCurrentEstimate(card: ModelCardGate | undefined): boolean {
  return card?.publishStatus === "PUBLISHED" && card.hasCurrentEstimate === true;
}

export function mayDrawForecast(card: ModelCardGate | undefined): boolean {
  return card?.publishStatus === "PUBLISHED" && card.hasForecast === true;
}

export function mayDrawOccurrenceProbability(card: ModelCardGate | undefined): boolean {
  return (
    mayDrawCurrentEstimate(card) &&
    (card?.predictionTarget === "occurrence_probability" || card?.predictionTarget == null)
  );
}

export function mayDrawRelativeAbundance(card: ModelCardGate | undefined): boolean {
  return card?.publishStatus === "PUBLISHED" && card.hasRelativeAbundance === true;
}

export function mayDrawMovement(card: ModelCardGate | undefined): boolean {
  return card?.publishStatus === "PUBLISHED" && card.hasMovement === true;
}

export const PAST_REPORTS_RESOLUTION: LayerResolutionMeta = {
  kind: "historical_pattern",
  nativeSourceResolution: "OBIS occurrence grid, 1° cells (~100 km)",
  displayedTileResolution: "Same 1° cells; at most 80 cells; n < 3 hidden",
  validatedModelResolution: null,
  positionalUncertainty: "Cell is a sampling bin, not an animal GPS point",
  timeResolution: "Year span of compiled records, not a current timestamp",
  depthResolution: "Not modeled",
  coarseningReason: "Public display coarsened; sensitive taxa withheld before draw",
};

export const WILLAPA_FIXTURE_RESOLUTION: LayerResolutionMeta = {
  kind: "unknown",
  nativeSourceResolution: "Synthetic Willapa fixture cells (2026-09-18)",
  displayedTileResolution: "Named growing-area scale placeholders",
  validatedModelResolution: null,
  positionalUncertainty: "Fixture only — not a published biological model",
  timeResolution: "Demo 72-hour working-conditions window",
  depthResolution: "Intertidal air / surface water flags on the fixture",
  coarseningReason: "Learn demo; never a harvest or animal-location product",
};

export function layerKindLabel(kind: LayerKind): string {
  switch (kind) {
    case "confirmed_observation":
      return "Confirmed observation";
    case "historical_pattern":
      return "Historical pattern — past reports, not now";
    case "current_estimate":
      return "Current estimate";
    case "forecast":
      return "Forecast";
    case "favorable_habitat":
      return "Favorable conditions — not confirmed species presence";
    case "unknown":
      return "Unknown — not absence";
    case "coarsened":
      return "Coarsened / withheld";
    case "relative_abundance":
      return "Relative abundance";
    case "movement":
      return "Movement";
  }
}

export function zoomBeyondBiologicalResolution(zoom: number, nativeDeg = 1): boolean {
  return zoom > 6 && nativeDeg >= 1;
}

export function scientificStatusCopy(options: {
  demo: boolean;
  past: PastReportsSummary | null;
  publishedNow: boolean;
  publishedSoon: boolean;
  withheld?: boolean;
}): string {
  if (options.demo) return "Learn demo encodings (measured / estimate / forecast) — not a published species location.";
  if (options.publishedNow) return "Model estimate available (experimental).";
  if (options.publishedSoon) return "Forecast (published card).";
  if (options.past?.withheld || options.withheld) return "Unknown now. Historical pattern withheld.";
  if (options.past && options.past.cellsDrawn > 0) {
    return "Past reports (historical pattern). Unknown as a current estimate.";
  }
  return "Unknown.";
}

export function targetsCopy(options: {
  card: ModelCardGate | undefined;
  past: PastReportsSummary | null;
  demo: boolean;
}): string {
  if (options.demo) {
    return "Observed presence: not counted. Occurrence probability: none issued. Relative abundance: none issued. Movement: none issued. Habitat suitability: favorable conditions only — not confirmed presence. Unknown: default outside this demo.";
  }
  const occ = mayDrawOccurrenceProbability(options.card) ? "issued (published card)" : "no issued location";
  const abun = mayDrawRelativeAbundance(options.card) ? "issued (published card)" : "none issued";
  const move = mayDrawMovement(options.card) ? "issued (published card)" : "none issued";
  let observed = "none now";
  if (options.past?.withheld) observed = "historical reports withheld — not present-day presence";
  else if (options.past && options.past.total && options.past.total > 0) {
    observed = "historical pattern only (past reports) — not present-day presence";
  }
  return `Observed presence: ${observed}. Occurrence probability: ${occ}. Relative abundance: ${abun}. Movement: ${move}. Habitat suitability: not a presence claim. Unknown: default.`;
}
