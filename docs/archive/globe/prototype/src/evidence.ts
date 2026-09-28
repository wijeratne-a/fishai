import { GOLIATH_APHIA_ID } from "./layers";
import type {
  CellRecord,
  Evidence16,
  HonestyAnswers,
  OpsRiskBlock,
  PastReportsSummary,
  TaxonRecord,
} from "./types";

const FIELD_TITLES: { key: keyof Evidence16; title: string }[] = [
  { key: "currentEstimate", title: "1. Current estimate" },
  { key: "forecastEstimate", title: "2. Forecast estimate" },
  { key: "confidence", title: "3. Confidence" },
  { key: "lastDirectObservation", title: "4. Last direct observation" },
  { key: "observationCount", title: "5. Observation count in the region" },
  { key: "observationTypes", title: "6. Observation types" },
  { key: "environmentalInputs", title: "7. Environmental factors" },
  { key: "keyModelDrivers", title: "8. Key model drivers" },
  { key: "comparableHistoricalConditions", title: "9. Comparable historical conditions" },
  { key: "modelVersion", title: "10. Model version" },
  { key: "validationPerformance", title: "11. Validation performance for this species/region" },
  { key: "knownLimitations", title: "12. Known limitations" },
  { key: "sourceLinksAndLicenses", title: "13. Source links and licenses" },
  { key: "dataFreshness", title: "14. Data freshness" },
  { key: "privacyCoarsening", title: "15. Privacy / coarsening explanation" },
  { key: "whatWouldReduceUncertainty", title: "16. What would reduce uncertainty here?" },
];

export function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderValue(key: keyof Evidence16, evidence: Evidence16): string {
  switch (key) {
    case "confidence": {
      const value = evidence.confidence;
      const reasons = value.reasons.map((reason) => `<li>${escapeHtml(reason)}</li>`).join("");
      return `<p>How sure: <strong>${escapeHtml(value.category)}</strong></p><ul>${reasons}</ul>`;
    }
    case "lastDirectObservation": {
      const value = evidence.lastDirectObservation;
      const at = value.at ? `<span class="unit">${escapeHtml(value.at)}</span>` : "none";
      return `<p>${at}</p><p>${escapeHtml(value.note)}</p>`;
    }
    case "observationCount": {
      const value = evidence.observationCount;
      return `<p><span class="unit">samples: ${value.n}</span> · ${escapeHtml(value.window)}</p><p>${escapeHtml(value.note)}</p>`;
    }
    case "observationTypes":
      return `<p>${evidence.observationTypes.map((item) => escapeHtml(item)).join("; ")}</p>`;
    case "environmentalInputs": {
      const value = evidence.environmentalInputs;
      if (value.length === 0) return `<p>None issued.</p>`;
      return value
        .map(
          (row) =>
            `<p><strong>${escapeHtml(row.name)}</strong> · <span class="unit">${escapeHtml(row.value)}</span><br />as-of ${escapeHtml(row.asOf)} · ${escapeHtml(row.role)}</p>`,
        )
        .join("");
    }
    case "sourceLinksAndLicenses":
      return evidence.sourceLinksAndLicenses
        .map(
          (row) =>
            `<p><a href="${escapeHtml(row.url)}" rel="noopener noreferrer" target="_blank">${escapeHtml(row.name)}</a><br />${escapeHtml(row.license)}. ${escapeHtml(row.note)}</p>`,
        )
        .join("");
    case "keyModelDrivers":
    case "knownLimitations":
    case "whatWouldReduceUncertainty":
      return `<ul>${evidence[key].map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
    default:
      return `<p>${escapeHtml(evidence[key])}</p>`;
  }
}

function renderAnswers(answers: HonestyAnswers): string {
  return `<section class="answers" aria-label="Why this estimate">
    <p><strong>Why this?</strong> ${escapeHtml(answers.why)}</p>
    <p><strong>How much to trust it?</strong> ${escapeHtml(answers.trust)}</p>
    <p><strong>What is missing?</strong> ${escapeHtml(answers.missing)}</p>
    <p><strong>Measured, estimate, or forecast?</strong> ${escapeHtml(answers.observedInferredForecast)}</p>
  </section>`;
}

function renderOpsPlain(ops: OpsRiskBlock): string {
  return `<section class="ops ops-plain" aria-label="Oyster working-conditions demo">
    <h3>Farm working conditions (demo)</h3>
    <p>This is a risk estimate for farm work over the next 72 hours — not a count of oysters, not food-safety, and not permission to harvest. Check the Washington Department of Health for harvest status.</p>
    <p><strong>Fixture status:</strong> ${escapeHtml(ops.status)}</p>
    <p>Hot air at low tide, plus wind and waves, can make handling harder. Sea-surface temperature is not the animal’s body temperature.</p>
  </section>`;
}

function renderOpsExpert(ops: OpsRiskBlock): string {
  const flags = [
    ops.notFoodSafety ? "NOT food-safety" : null,
    ops.notHarvestAuthorization ? "NOT harvest authorization" : null,
    ops.verifyWaDoh ? "Verify WA DOH" : null,
    ops.airTimesTideNotSstAsBodyTemp ? "Air × tide — not SST = body temperature" : null,
  ]
    .filter((item): item is string => Boolean(item))
    .map((item) => `<span>${escapeHtml(item)}</span>`)
    .join("");
  const options = ops.options.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  return `<section class="ops" aria-label="Expert oyster operational stress">
    <h3>W1 oyster OPS-RISK (Category ${escapeHtml(ops.category)})</h3>
    <div class="ops-flags">${flags}</div>
    <p><strong>Status (fixture):</strong> ${escapeHtml(ops.status)}</p>
    <p>${escapeHtml(ops.headline)}</p>
    <p><strong>Species / geography:</strong> ${escapeHtml(ops.species)} · ${escapeHtml(ops.geography)}</p>
    <p><strong>Target:</strong> ${escapeHtml(ops.target)}</p>
    <ul>${options}</ul>
  </section>`;
}

function envLines(evidence: Evidence16): string {
  if (evidence.environmentalInputs.length === 0) {
    return "<p>No environmental factors issued for this cell.</p>";
  }
  return evidence.environmentalInputs
    .map(
      (row) =>
        `<p><strong>${escapeHtml(row.name)}</strong>: ${escapeHtml(row.value)} (as-of ${escapeHtml(row.asOf)})</p>`,
    )
    .join("");
}

export function renderPastReportsHtml(taxon: TaxonRecord, past: PastReportsSummary | null): string {
  const name = escapeHtml(taxon.commonNames[0] ?? taxon.scientificName);
  if (!past) {
    return `<p class="lede">${name}</p><p>Looking up past reports from public databases…</p>`;
  }
  if (past.withheld) {
    return `<p class="lede">${name}</p>
      <p>Past reports exist but locations are withheld. Listed or sensitive taxa are not drawn as a public pin map.</p>
      <p>${escapeHtml(past.licenseNote)}</p>`;
  }
  if (past.error) {
    return `<p class="lede">${name}</p>
      <p>Past-report lookup failed (${escapeHtml(past.error)}). We do not know where it is. That is not an empty ocean.</p>`;
  }
  const total =
    past.total && past.total > 0
      ? `${past.total.toLocaleString()} compiled records`
      : "no compiled records in this lookup";
  const years = past.yearSpan ? `Years: ${escapeHtml(past.yearSpan)}.` : "Year span unknown.";
  const cells = past.cellsDrawn;
  const goliathNote =
    taxon.aphiaId === GOLIATH_APHIA_ID
      ? `<p>This map can show historical reports where permitted. No issued current location estimate or forecast exists for this species in this build.</p>`
      : "";
  return `
    ${goliathNote}
    <p class="evidence-summary">
      This view shows <strong>${escapeHtml(total)}</strong>
      (${cells} coarse cells drawn), <strong>0</strong> survey encounters listed here,
      and <strong>no</strong> model-estimated likelihood (no published card).
      Environmental factors are not issued for this species layer.
    </p>
    <section class="evidence-group" aria-label="Observations">
      <h3>Observations</h3>
      <p><strong>Past reports</strong> — ${escapeHtml(total)}. ${years}</p>
      <p>Past reports = where people recorded this species in the past, not live presence.</p>
      <p>Drawn cells: ${cells}. This is a partial extract of the public grid (hidden if fewer than 3 records; at most 80 cells, in API order, about 1° / 100 km). Missing cells are not biological absence.</p>
    </section>
    <section class="evidence-group" aria-label="Model estimates">
      <h3>Model estimates</h3>
      <p>No issued location. No forecast issued. How sure: None.</p>
    </section>
    <section class="evidence-group" aria-label="Environment">
      <h3>Environment</h3>
      <p>No environmental factors issued for this species search.</p>
    </section>
    <section class="evidence-group" aria-label="Methods and limitations">
      <h3>Methods and limitations</h3>
      <p><strong>Source:</strong> ${escapeHtml(past.source)}</p>
      <p><strong>License:</strong> ${escapeHtml(past.licenseNote)}</p>
      <p>Coarse public grid only. Not a count of animals. Not live tracking.</p>
    </section>`;
}

export function renderPastReportCellHtml(
  taxon: TaxonRecord | null,
  cellLabel: string,
  reportCount: number,
): string {
  const species = taxon
    ? escapeHtml(taxon.commonNames[0] ?? taxon.scientificName)
    : "Selected species";
  return `
    <p class="evidence-summary">
      This cell shows <strong>${reportCount.toLocaleString()}</strong> past reports for
      <strong>${species}</strong>, <strong>0</strong> survey encounters listed here,
      and <strong>no</strong> model-estimated likelihood (if available).
      Environmental factors are not issued for past-report cells.
    </p>
    <section class="evidence-group" aria-label="Observations">
      <h3>Observations</h3>
      <p><strong>${escapeHtml(cellLabel)}</strong> — ${reportCount.toLocaleString()} compiled records in this coarse cell.</p>
      <p>Past reports = where people recorded this species in the past, not live presence.</p>
    </section>
    <section class="evidence-group" aria-label="Model estimates">
      <h3>Model estimates</h3>
      <p>No issued location. No forecast issued.</p>
    </section>
    <section class="evidence-group" aria-label="Environment">
      <h3>Environment</h3>
      <p>No environmental factors issued for this cell.</p>
    </section>
    <section class="evidence-group" aria-label="Methods and limitations">
      <h3>Methods and limitations</h3>
      <p>About 1° / 100 km public coarsening. Zooming in does not sharpen the biology.</p>
    </section>`;
}

export function renderEvidenceHtml(
  cellId: string,
  label: string,
  truthPlain: string,
  publishClass: string,
  record: CellRecord,
  expert: boolean,
): string {
  const evidence = record.evidence;
  const obsN = evidence.observationCount.n;
  const hasEstimate =
    evidence.currentEstimate &&
    !/no issued|none issued|not issued|unknown/i.test(evidence.currentEstimate);
  const hasForecast =
    evidence.forecastEstimate &&
    !/no issued|none issued|not issued|unknown/i.test(evidence.forecastEstimate);
  const summary = `
    <p class="evidence-summary">
      This cell shows <strong>${obsN}</strong> past reports / sample rows,
      <strong>${hasEstimate ? "a demo" : "no"}</strong> model-estimated likelihood
      ${hasEstimate ? "(demo encoding — not a published species location)" : "(if available)"},
      and the following environmental conditions when present.
      ${hasForecast ? " A forecast encoding is shown for the demo only." : " No forecast issued for a published species product."}
    </p>`;

  const observations = `
    <section class="evidence-group" aria-label="Observations">
      <h3>Observations</h3>
      <p>Last direct observation: ${
        evidence.lastDirectObservation.at
          ? escapeHtml(evidence.lastDirectObservation.at)
          : "none"
      }.</p>
      <p>${escapeHtml(evidence.lastDirectObservation.note)}</p>
      <p>Sample rows in window: <span class="unit">${obsN}</span> (${escapeHtml(evidence.observationCount.window)}).</p>
      <p>Types: ${evidence.observationTypes.map((item) => escapeHtml(item)).join("; ") || "none listed"}.</p>
    </section>`;

  const models = `
    <section class="evidence-group" aria-label="Model estimates">
      <h3>Model estimates</h3>
      <p><strong>Current:</strong> ${escapeHtml(evidence.currentEstimate)}</p>
      <p><strong>Forecast:</strong> ${escapeHtml(evidence.forecastEstimate)}</p>
      <p><strong>How sure:</strong> ${escapeHtml(evidence.confidence.category)}</p>
    </section>`;

  const environment = `
    <section class="evidence-group" aria-label="Environment">
      <h3>Environment</h3>
      ${envLines(evidence)}
    </section>`;

  const methods = `
    <section class="evidence-group" aria-label="Methods and limitations">
      <h3>Methods and limitations</h3>
      ${renderAnswers(record.answers)}
      <p>${escapeHtml(evidence.privacyCoarsening)}</p>
      <ul>${evidence.knownLimitations.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </section>`;

  const ops = record.opsRisk
    ? expert
      ? renderOpsExpert(record.opsRisk)
      : renderOpsPlain(record.opsRisk)
    : "";
  const fields = expert
    ? `<details class="expert-methods"><summary>Expert methodology (16 fields)</summary><div class="fields">${FIELD_TITLES.map(
        ({ key, title }) =>
          `<article><h3>${escapeHtml(title)}</h3>${renderValue(key, record.evidence)}</article>`,
      ).join("")}</div></details>`
    : "";
  const jsonButton = expert
    ? `<button type="button" class="copy-json" data-cell="${escapeHtml(cellId)}">Copy cell JSON</button>`
    : "";
  const badges = expert
    ? `<div class="badge-row">
        <span class="badge">${escapeHtml(cellId)}</span>
        <span class="badge">${escapeHtml(truthPlain)}</span>
        <span class="badge">${escapeHtml(publishClass)}</span>
      </div>`
    : `<div class="badge-row"><span class="badge">${escapeHtml(truthPlain)}</span></div>`;

  return `
    <p class="lede">${escapeHtml(label)}</p>
    ${badges}
    ${summary}
    ${ops}
    ${observations}
    ${models}
    ${environment}
    ${methods}
    ${jsonButton}
    ${fields}
  `;
}
