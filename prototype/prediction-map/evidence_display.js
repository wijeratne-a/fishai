/** Schema enum (data contract) → README display doctrine (UX labels). Both stay visible in UI. */
export const SCHEMA_EVIDENCE_STATES = [
  "HINDCAST_GLORYS",
  "NOWCAST_UNVALIDATED",
  "FORECAST",
  "DEGRADED",
  "UNKNOWN",
];

/** README.md "Evidence-state vocabulary" — display doctrine only. */
export const DISPLAY_DOCTRINE = [
  "Direct Observation",
  "Historical Pattern",
  "Current Nowcast",
  "Forecast",
  "Unknown",
];

/** Per CUFES contract + README: secondary display line for each schema enum. */
export const SCHEMA_TO_DISPLAY = {
  HINDCAST_GLORYS: "Historical Pattern",
  NOWCAST_UNVALIDATED: "Current Nowcast",
  FORECAST: "Forecast",
  DEGRADED: "Current Nowcast",
  UNKNOWN: "Unknown",
};

export function displayDoctrineForSchema(schemaEnum) {
  return SCHEMA_TO_DISPLAY[schemaEnum] ?? "Unknown";
}

/** Plain words for each schema evidence state. Every line names eggs. */
export const PLAIN_EVIDENCE = {
  HINDCAST_GLORYS: "Historical pattern of eggs from past ocean conditions",
  NOWCAST_UNVALIDATED: "Egg estimate for the current day, not yet checked against new egg samples",
  FORECAST: "Egg estimate for a coming day in this spawning habitat",
  DEGRADED: "Egg estimate with a weaker ocean input, so the range is wider",
  UNKNOWN: "Unknown egg evidence — not enough to say if eggs are likely",
};

export function plainEvidence(schemaEnum) {
  return PLAIN_EVIDENCE[schemaEnum] ?? PLAIN_EVIDENCE.UNKNOWN;
}

/** Contract: ood_level >= 2 is out of domain and must render as UNKNOWN. */
export function isUnknownRow(row) {
  return row.evidence_state === "UNKNOWN" || Number(row.ood_level) >= 2;
}

export function effectiveEvidenceState(row) {
  return isUnknownRow(row) ? "UNKNOWN" : row.evidence_state;
}
