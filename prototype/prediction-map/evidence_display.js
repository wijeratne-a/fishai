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

/** Contract: ood_level >= 2 is out of domain and must render as UNKNOWN. */
export function isUnknownRow(row) {
  return row.evidence_state === "UNKNOWN" || Number(row.ood_level) >= 2;
}

export function effectiveEvidenceState(row) {
  return isUnknownRow(row) ? "UNKNOWN" : row.evidence_state;
}
