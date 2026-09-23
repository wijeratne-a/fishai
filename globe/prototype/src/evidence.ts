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
  { key: "environmentalInputs", title: "7. Environmental inputs" },
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
    <p><strong>Measured, guessed, or future?</strong> ${escapeHtml(answers.observedInferredForecast)}</p>
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
      <p>Past-report lookup failed (${escapeHtml(past.error)}). The map stays striped: we do not know, not empty ocean.</p>`;
  }
  const total =
    past.total && past.total > 0
      ? `${past.total.toLocaleString()} compiled records`
      : "no compiled records in this lookup";
  const years = past.yearSpan ? `Years: ${escapeHtml(past.yearSpan)}.` : "Year span unknown.";
  return `<p class="lede">${name}</p>
    <section class="answers" aria-label="Past reports">
      <p><strong>Past reports</strong> — ${escapeHtml(total)}. ${years}</p>
      <p>These cells are where people sampled and recorded this name. This is not where the animals are now.</p>
      <p><strong>Source:</strong> ${escapeHtml(past.source)}</p>
      <p><strong>License:</strong> ${escapeHtml(past.licenseNote)}</p>
      <p>Drawn cells: ${past.cellsDrawn} (hidden if fewer than 3 records; at most 80 cells; about 1° / 100 km).</p>
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
  const answers = renderAnswers(record.answers);
  const ops = record.opsRisk
    ? expert
      ? renderOpsExpert(record.opsRisk)
      : renderOpsPlain(record.opsRisk)
    : "";
  const fields = expert
    ? FIELD_TITLES.map(
        ({ key, title }) =>
          `<article><h3>${escapeHtml(title)}</h3>${renderValue(key, record.evidence)}</article>`,
      ).join("")
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
    ${ops}
    ${answers}
    ${jsonButton}
    ${expert ? `<div class="fields">${fields}</div>` : ""}
  `;
}
