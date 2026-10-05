import {
  SCHEMA_EVIDENCE_STATES,
  DISPLAY_DOCTRINE,
  displayDoctrineForSchema,
  effectiveEvidenceState,
  isUnknownRow,
} from "./evidence_display.js";

const DOMAIN = {
  latMin: 32,
  latMax: 35,
  lonMin: -121,
  lonMax: -117,
};

const FIXTURE_URL = "./fixtures/synthetic_cufes_grid.json";
const FLOOR_KM = 10;
const MAX_DOTS = 25;

const Cesium = window.Cesium;

function parseCellId(cellId) {
  const m = /^pilot_([0-9.]+)_(-[0-9.]+)$/.exec(cellId);
  if (!m) return null;
  return { lat: Number(m[1]), lon: Number(m[2]) };
}

function hashString(text) {
  let h = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function mulberry32(seed) {
  let a = seed >>> 0;
  return function next() {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function kmToDegrees(lat, eastKm, northKm) {
  const dLat = northKm / 111;
  const dLon = eastKm / (111 * Math.cos((lat * Math.PI) / 180));
  return { dLat, dLon };
}

/** 10 km lattice inside the cell. Count tracks egg-encounter probability. */
function eggDotsForRow(row, spacingKm) {
  const unknown = isUnknownRow(row);
  if (!unknown && row.p_encounter != null) {
    if (!(row.p_encounter > 0)) return [];
    const ll = parseCellId(row.cell_id);
    if (!ll) return [];
    const spanKm = Math.max(FLOOR_KM, spacingKm || 50);
    const slots = Math.max(1, Math.round(spanKm / FLOOR_KM));
    const count = Math.min(MAX_DOTS, Math.max(1, Math.round(row.p_encounter * slots * slots)));
    const rng = mulberry32(hashString(row.cell_id + row.species));
    const order = [];
    for (let i = 0; i < slots; i += 1) {
      for (let j = 0; j < slots; j += 1) order.push([i, j]);
    }
    for (let k = order.length - 1; k > 0; k -= 1) {
      const swap = Math.floor(rng() * (k + 1));
      const tmp = order[k];
      order[k] = order[swap];
      order[swap] = tmp;
    }
    const origin = -((slots - 1) * FLOOR_KM) / 2;
    return order.slice(0, count).map(([i, j], rank) => {
      const northKm = origin + i * FLOOR_KM;
      const eastKm = origin + j * FLOOR_KM;
      const { dLat, dLon } = kmToDegrees(ll.lat, eastKm, northKm);
      return {
        lat: ll.lat + dLat,
        lon: ll.lon + dLon,
        rank,
        cellId: row.cell_id,
      };
    });
  }
  return [];
}

function dotsToKeep(cameraHeight) {
  if (cameraHeight > 8_000_000) return 1;
  if (cameraHeight > 2_500_000) return 4;
  if (cameraHeight > 900_000) return 9;
  return MAX_DOTS;
}

function renderLegend(container) {
  container.innerHTML = `
    <h2>Spawning-habitat egg-encounter globe (internal prototype)</h2>
    <p class="watermark" data-testid="watermark"></p>
    <section aria-label="Egg-encounter schema evidence_state enum">
      <h3>Egg-encounter schema evidence_state (data contract)</h3>
      <ul>${SCHEMA_EVIDENCE_STATES.map((s) => `<li><code>${s}</code></li>`).join("")}</ul>
    </section>
    <section aria-label="Spawning-habitat egg display doctrine vocabulary">
      <h3>Spawning egg evidence display doctrine (README Evidence-state vocabulary)</h3>
      <ul>${DISPLAY_DOCTRINE.map((d) => `<li>${d}</li>`).join("")}</ul>
    </section>
    <p class="hint">Egg-encounter likelihood is discrete dots on a 10 km lattice: denser where the spawning probability is higher. Zero-probability and UNKNOWN egg cells render nothing. This spawning-habitat globe never draws finer than 10 km.</p>
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

function renderCellList(container, rows, species) {
  const filtered = rows.filter((r) => r.species === species);
  container.innerHTML = filtered
    .map((row) => {
      const state = effectiveEvidenceState(row);
      const doctrine = displayDoctrineForSchema(state);
      const hidden = isUnknownRow(row) || row.p_encounter == null || row.p_encounter <= 0;
      const prob = hidden
        ? `<em>No egg-encounter probability (UNKNOWN)</em>`
        : `Egg-encounter p = ${(row.p_encounter * 100).toFixed(1)}% · 90% interval ${(row.p_lo90 * 100).toFixed(1)}–${(row.p_hi90 * 100).toFixed(1)}%`;
      const unknownLine =
        row.unknown_reason != null
          ? `<p class="unknown-reason">Egg-encounter unknown reason: <code>${row.unknown_reason}</code></p>`
          : "";
      const dotLine = hidden
        ? `<p>Egg-encounter globe: no dots (UNKNOWN or zero).</p>`
        : `<p>Egg-encounter globe: dot density on a 10 km lattice.</p>`;
      return `<article class="cell-card" data-cell-id="${row.cell_id}">
        <h4>${row.cell_id}</h4>
        <p><strong>Egg-encounter schema evidence_state:</strong> <code>${state}</code></p>
        <p><strong>Spawning egg display doctrine:</strong> ${doctrine}</p>
        <p>${prob}</p>
        ${dotLine}
        ${unknownLine}
      </article>`;
    })
    .join("");
}

async function createGlobe(container) {
  const imagery = await Cesium.ArcGisMapServerImageryProvider.fromUrl(
    "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer",
    { enablePickFeatures: false },
  );
  const viewer = new Cesium.Viewer(container, {
    animation: false,
    timeline: false,
    baseLayerPicker: false,
    geocoder: false,
    homeButton: true,
    sceneModePicker: false,
    navigationHelpButton: false,
    fullscreenButton: false,
    infoBox: false,
    selectionIndicator: false,
    baseLayer: new Cesium.ImageryLayer(imagery),
    terrainProvider: new Cesium.EllipsoidTerrainProvider(),
  });
  viewer.scene.globe.enableLighting = false;
  viewer.scene.globe.baseColor = Cesium.Color.fromCssColorString("#16324f");
  viewer.scene.screenSpaceCameraController.minimumZoomDistance = 80_000;
  return viewer;
}

function paintDots(viewer, collection, rows, species, meta) {
  collection.removeAll();
  const spacing = meta.cell_spacing_km;
  const filtered = rows.filter((r) => r.species === species);
  filtered.forEach((row) => {
    const state = effectiveEvidenceState(row);
    const doctrine = displayDoctrineForSchema(state);
    const dots = eggDotsForRow(row, spacing);
    const ll = parseCellId(row.cell_id);
    if (ll && dots.length > 0) {
      viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(ll.lon, ll.lat, 2000),
        label: {
          text: "egg " + doctrine + "\n" + state,
          font: "12px system-ui, sans-serif",
          fillColor: Cesium.Color.fromCssColorString("#fff4cc"),
          outlineColor: Cesium.Color.BLACK,
          outlineWidth: 3,
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          pixelOffset: new Cesium.Cartesian2(0, -18),
          distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 1_200_000),
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
        },
      });
    }
    dots.forEach((dot) => {
      const primitive = collection.add({
        position: Cesium.Cartesian3.fromDegrees(dot.lon, dot.lat, 0),
        pixelSize: 7,
        color: Cesium.Color.fromCssColorString("#ffe08a"),
        outlineColor: Cesium.Color.fromCssColorString("#3a2a00"),
        outlineWidth: 1,
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      });
      primitive._eggRank = dot.rank;
    });
  });
}

function applyDotLod(viewer, collection) {
  const height = viewer.camera.positionCartographic.height;
  const keep = dotsToKeep(height);
  for (let i = 0; i < collection.length; i += 1) {
    const dot = collection.get(i);
    dot.show = dot._eggRank < keep;
  }
  viewer.scene.requestRender();
}

async function main() {
  const res = await fetch(FIXTURE_URL);
  const payload = await res.json();
  const { rows, meta } = payload;

  const legend = document.getElementById("legend");
  const toggles = document.getElementById("species-toggle");
  const list = document.getElementById("cell-list");
  const globeEl = document.getElementById("globe");

  renderLegend(legend);
  const wm = legend.querySelector(".watermark");
  if (wm) wm.textContent = meta.watermark;
  const globeWm = document.querySelector("[data-testid=globe-watermark]");
  if (globeWm) globeWm.textContent = meta.watermark;

  const speciesSet = [...new Set(rows.map((r) => r.species))].sort();
  let activeSpecies = speciesSet[0] ?? "sardine";

  const viewer = await createGlobe(globeEl);
  const dots = viewer.scene.primitives.add(new Cesium.PointPrimitiveCollection());

  const title = document.getElementById("map-title");
  const refresh = () => {
    viewer.entities.removeAll();
    paintDots(viewer, dots, rows, activeSpecies, meta);
    applyDotLod(viewer, dots);
    renderCellList(list, rows, activeSpecies);
    if (title) {
      title.textContent =
        activeSpecies +
        " spawning-habitat egg-encounter globe — " +
        meta.valid_day +
        " (synthetic fixture)";
    }
    renderSpeciesToggle(toggles, speciesSet, activeSpecies, (sp) => {
      activeSpecies = sp;
      refresh();
    });
  };
  refresh();

  viewer.camera.moveEnd.addEventListener(() => applyDotLod(viewer, dots));
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(-119, 33.5, 1_800_000),
    duration: 0,
  });
  applyDotLod(viewer, dots);
  document.body.dataset.eggGlobe = "ready";
}

main().catch((err) => {
  console.error(err);
  document.body.insertAdjacentHTML(
    "beforeend",
    `<p role="alert">Failed to load spawning-habitat egg globe: ${err.message}</p>`,
  );
});
