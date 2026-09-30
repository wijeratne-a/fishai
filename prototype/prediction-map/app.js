import {
  SCHEMA_EVIDENCE_STATES,
  DISPLAY_DOCTRINE,
  displayDoctrineForSchema,
  isUnknownRow,
} from "./evidence_display.js";

const DOMAIN = {
  latMin: 32,
  latMax: 35,
  lonMin: -121,
  lonMax: -117,
};

const FIXTURE_URL = "./fixtures/synthetic_cufes_grid.json";

function parseCellId(cellId) {
  const m = /^pilot_([0-9.]+)_(-[0-9.]+)$/.exec(cellId);
  if (!m) return null;
  return { lat: Number(m[1]), lon: Number(m[2]) };
}

function latLonToCanvas(lat, lon, width, height, pad) {
  const x =
    pad +
    ((lon - DOMAIN.lonMin) / (DOMAIN.lonMax - DOMAIN.lonMin)) * (width - 2 * pad);
  const y =
    pad +
    ((DOMAIN.latMax - lat) / (DOMAIN.latMax - DOMAIN.latMin)) * (height - 2 * pad);
  return { x, y };
}

function eggEncounterColor(p) {
  const t = Math.max(0, Math.min(1, p));
  const r = Math.round(255 * (1 - t * 0.7));
  const g = Math.round(180 + t * 60);
  const b = Math.round(220 - t * 120);
  return `rgb(${r},${g},${b})`;
}

function renderLegend(container) {
  container.innerHTML = `
    <h2>Spawning-habitat egg-encounter map (internal prototype)</h2>
    <p class="watermark" data-testid="watermark"></p>
    <section aria-label="Schema evidence_state enum">
      <h3>Schema evidence_state (data contract)</h3>
      <ul>${SCHEMA_EVIDENCE_STATES.map((s) => `<li><code>${s}</code></li>`).join("")}</ul>
    </section>
    <section aria-label="Display doctrine vocabulary">
      <h3>Display doctrine (README Evidence-state vocabulary)</h3>
      <ul>${DISPLAY_DOCTRINE.map((d) => `<li>${d}</li>`).join("")}</ul>
    </section>
    <p class="hint">Each cell shows both the schema enum and the display doctrine line. UNKNOWN cells show egg evidence state only — no probability fill.</p>
  `;
}

function renderSpeciesToggle(container, speciesList, active, onChange) {
  container.innerHTML = speciesList
    .map(
      (sp) =>
        `<button type="button" class="species-btn ${sp === active ? "active" : ""}" data-species="${sp}">${sp} egg-encounter</button>`,
    )
    .join("");
  container.querySelectorAll(".species-btn").forEach((btn) => {
    btn.addEventListener("click", () => onChange(btn.dataset.species));
  });
}

function drawMap(canvas, rows, species, meta) {
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  const pad = 36;
  ctx.clearRect(0, 0, w, h);

  ctx.fillStyle = "#0a1628";
  ctx.fillRect(0, 0, w, h);

  ctx.strokeStyle = "#3a5068";
  ctx.lineWidth = 1;
  for (let lat = DOMAIN.latMin; lat <= DOMAIN.latMax; lat += 0.5) {
    const { y } = latLonToCanvas(lat, DOMAIN.lonMin, w, h, pad);
    ctx.beginPath();
    ctx.moveTo(pad, y);
    ctx.lineTo(w - pad, y);
    ctx.stroke();
  }
  for (let lon = DOMAIN.lonMin; lon <= DOMAIN.lonMax; lon += 0.5) {
    const { x } = latLonToCanvas(DOMAIN.latMin, lon, w, h, pad);
    ctx.beginPath();
    ctx.moveTo(x, pad);
    ctx.lineTo(x, h - pad);
    ctx.stroke();
  }

  ctx.fillStyle = "#9fb3c8";
  ctx.font = "12px system-ui, sans-serif";
  ctx.fillText("32°N", pad, h - 8);
  ctx.fillText("35°N", pad, pad - 8);
  ctx.fillText("121°W", pad, h - 22);
  ctx.fillText("117°W", w - pad - 36, h - 22);

  const filtered = rows.filter((r) => r.species === species);
  const cellSize = 44;

  filtered.forEach((row) => {
    const ll = parseCellId(row.cell_id);
    if (!ll) return;
    const { x, y } = latLonToCanvas(ll.lat, ll.lon, w, h, pad);
    const unknown = isUnknownRow(row);

    if (!unknown && row.p_encounter != null) {
      ctx.fillStyle = eggEncounterColor(row.p_encounter);
      ctx.fillRect(x - cellSize / 2, y - cellSize / 2, cellSize, cellSize);
    } else {
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = "#e8a838";
      ctx.lineWidth = 2;
      ctx.strokeRect(x - cellSize / 2, y - cellSize / 2, cellSize, cellSize);
      ctx.setLineDash([]);
      ctx.fillStyle = "#e8a838";
      ctx.font = "10px system-ui, sans-serif";
      ctx.fillText("?", x - 3, y + 4);
    }

    ctx.strokeStyle = "#ffffff88";
    ctx.lineWidth = 1;
    ctx.strokeRect(x - cellSize / 2, y - cellSize / 2, cellSize, cellSize);
  });

  const title = document.getElementById("map-title");
  if (title) {
    title.textContent = `${species} spawning-habitat egg-encounter cells — ${meta.valid_day} (synthetic fixture)`;
  }
}

function renderCellList(container, rows, species) {
  const filtered = rows.filter((r) => r.species === species);
  container.innerHTML = filtered
    .map((row) => {
      const doctrine = displayDoctrineForSchema(row.evidence_state);
      const prob =
        isUnknownRow(row) || row.p_encounter == null
          ? `<em>No egg-encounter probability (UNKNOWN)</em>`
          : `Egg-encounter p = ${(row.p_encounter * 100).toFixed(1)}% · 90% interval ${(row.p_lo90 * 100).toFixed(1)}–${(row.p_hi90 * 100).toFixed(1)}%`;
      const unknownLine =
        row.unknown_reason != null
          ? `<p class="unknown-reason">Unknown reason: <code>${row.unknown_reason}</code></p>`
          : "";
      return `<article class="cell-card" data-cell-id="${row.cell_id}">
        <h4>${row.cell_id}</h4>
        <p><strong>Schema evidence_state:</strong> <code>${row.evidence_state}</code></p>
        <p><strong>Display doctrine:</strong> ${doctrine}</p>
        <p>${prob}</p>
        ${unknownLine}
      </article>`;
    })
    .join("");
}

async function main() {
  const res = await fetch(FIXTURE_URL);
  const payload = await res.json();
  const { rows, meta } = payload;

  const watermarkEl = document.querySelector("[data-testid=watermark]");
  if (watermarkEl) watermarkEl.textContent = meta.watermark;

  const speciesSet = [...new Set(rows.map((r) => r.species))].sort();
  let activeSpecies = speciesSet[0] ?? "sardine";

  const legend = document.getElementById("legend");
  const toggles = document.getElementById("species-toggle");
  const canvas = document.getElementById("map-canvas");
  const list = document.getElementById("cell-list");

  renderLegend(legend);
  const wm = legend.querySelector(".watermark");
  if (wm) wm.textContent = meta.watermark;

  const refresh = () => {
    drawMap(canvas, rows, activeSpecies, meta);
    renderCellList(list, rows, activeSpecies);
    renderSpeciesToggle(toggles, speciesSet, activeSpecies, (sp) => {
      activeSpecies = sp;
      refresh();
    });
  };
  refresh();
}

main().catch((err) => {
  console.error(err);
  document.body.insertAdjacentHTML(
    "beforeend",
    `<p role="alert">Failed to load spawning-habitat egg fixture: ${err.message}</p>`,
  );
});
