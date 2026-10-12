import {
  SCHEMA_EVIDENCE_STATES,
  displayDoctrineForSchema,
  effectiveEvidenceState,
  isUnknownRow,
  plainEvidence,
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

const PLACE_MARKERS = [
  { name: "San Diego", lat: 32.7157, lon: -117.1611 },
  { name: "Los Angeles", lat: 34.0522, lon: -118.2437 },
  { name: "Channel Islands", lat: 33.45, lon: -119.55 },
];

const PLACE_ANCHORS = PLACE_MARKERS.map((p) => ({
  ...p,
  lat: p.lat,
  lon: p.lon,
}));

const Cesium = window.Cesium;
let dotAlpha = 0;

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

function eggDotsForRow(row, spacingKm) {
  const unknown = isUnknownRow(row);
  if (!unknown && row.p_encounter != null) {
    if (!(row.p_encounter > 0)) return [];
    const ll = parseCellId(row.cell_id);
    if (!ll) return [];
    const spanKm = Math.max(FLOOR_KM, spacingKm || 50);
    const slots = Math.max(1, Math.round(spanKm / FLOOR_KM));
    const count = Math.min(MAX_DOTS, Math.max(1, Math.round(row.p_encounter * slots * slots)));
    const rng = mulberry32(hashString(row.cell_id + row.species + row.valid_day));
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

const SPECIES_LABEL = {
  sardine: "Sardine",
  anchovy: "Anchovy",
};

const SPECIES_EGG_NAME = {
  sardine: "Sardine eggs",
  anchovy: "Anchovy eggs",
};

function formatShortDay(isoDay) {
  const [y, m, d] = isoDay.split("-").map(Number);
  const month = new Date(Date.UTC(y, m - 1, d)).toLocaleString("en-US", {
    month: "short",
    timeZone: "UTC",
  });
  return month + " " + d + ", " + y;
}

function titleCaseSpecies(species) {
  return SPECIES_LABEL[species] || species;
}

function nearestPlaceName(lat, lon) {
  let best = PLACE_ANCHORS[0].name;
  let bestDist = Number.POSITIVE_INFINITY;
  PLACE_ANCHORS.forEach((place) => {
    const dLat = lat - place.lat;
    const dLon = (lon - place.lon) * Math.cos((lat * Math.PI) / 180);
    const dist = dLat * dLat + dLon * dLon;
    if (dist < bestDist) {
      bestDist = dist;
      best = place.name;
    }
  });
  return best;
}

function rowsForView(allRows, species, validDay) {
  return allRows.filter((r) => r.species === species && r.valid_day === validDay);
}

function uniqueDays(allRows, meta) {
  if (Array.isArray(meta.demo_days) && meta.demo_days.length) {
    return [...meta.demo_days];
  }
  return [...new Set(allRows.map((r) => r.valid_day))].sort();
}

function dayControlLabel(day, rowsOnDay) {
  const states = new Set(rowsOnDay.map((r) => effectiveEvidenceState(r)));
  if (states.has("FORECAST") && !states.has("NOWCAST_UNVALIDATED")) {
    return `${formatShortDay(day)} · coming days (demo)`;
  }
  if (states.has("NOWCAST_UNVALIDATED")) {
    return `${formatShortDay(day)} · today, not yet checked`;
  }
  return `${formatShortDay(day)} · past ocean patterns`;
}

function computeSummaryHeadline(rows, species) {
  const active = rows.filter(
    (r) => r.species === species && !isUnknownRow(r) && r.p_encounter != null && r.p_encounter > 0,
  );
  if (!active.length) {
    return `No spawning patches with egg likelihood for ${titleCaseSpecies(species).toLowerCase()} on this day.`;
  }
  let top = active[0];
  active.forEach((row) => {
    if (row.p_encounter > top.p_encounter) top = row;
  });
  const ll = parseCellId(top.cell_id);
  const place = ll ? nearestPlaceName(ll.lat, ll.lon) : "this region";
  const pct = Math.round(top.p_encounter * 100);
  return `${active.length} patches with spawning activity · highest ${pct}% near ${place}`;
}

function renderLegend(container) {
  const plainStates = SCHEMA_EVIDENCE_STATES.map(
    (s) =>
      `<li><span class="plain">${plainEvidence(s)}</span> <code class="muted">${s}</code> · ${displayDoctrineForSchema(s)}</li>`,
  ).join("");
  container.innerHTML = `
    <h2>How to read spawning activity</h2>
    <p class="watermark" data-testid="watermark"></p>
    <p class="hint">Gold dots mark 10 km patches where eggs are more likely. More dots = higher egg likelihood. Empty water means eggs are unlikely or unknown. This map never draws finer than 10 km.</p>
    <section aria-label="Egg evidence in plain words">
      <h3>Evidence behind each patch</h3>
      <ul class="evidence-list">${plainStates}</ul>
    </section>
  `;
}

function renderSpeciesToggle(container, speciesList, active, onChange) {
  container.innerHTML = speciesList
    .map((sp) => {
      const label = titleCaseSpecies(sp);
      return `<button type="button" class="species-btn ${sp === active ? "active" : ""}" data-species="${sp}" aria-label="${label} egg spawning layer">${label}</button>`;
    })
    .join("");
  container.querySelectorAll(".species-btn").forEach((btn) => {
    btn.addEventListener("click", () => onChange(btn.dataset.species));
  });
}

function renderDayControl(container, days, allRows, activeDay, onChange) {
  container.replaceChildren();
  const label = document.createElement("label");
  label.className = "day-label";
  label.htmlFor = "day-select";
  label.textContent = "Spawning day";
  const select = document.createElement("select");
  select.id = "day-select";
  select.setAttribute("data-testid", "day-select");
  days.forEach((day) => {
    const rowsOnDay = allRows.filter((r) => r.valid_day === day);
    const option = document.createElement("option");
    option.value = day;
    option.textContent = dayControlLabel(day, rowsOnDay);
    option.selected = day === activeDay;
    select.appendChild(option);
  });
  const hint = document.createElement("p");
  hint.className = "day-hint";
  hint.textContent =
    "Demo / unvalidated egg spawning view — not a checked nowcast or forecast product.";
  container.append(label, select, hint);
  select.addEventListener("change", () => onChange(select.value));
}

function renderCellList(container, rows, species) {
  const filtered = rows.filter((r) => r.species === species);
  container.innerHTML = filtered
    .map((row) => {
      const state = effectiveEvidenceState(row);
      const eggName = SPECIES_EGG_NAME[row.species] || `${row.species} eggs`;
      const ll = parseCellId(row.cell_id);
      const place = ll ? nearestPlaceName(ll.lat, ll.lon) : "offshore";
      const hidden = isUnknownRow(row) || row.p_encounter == null || row.p_encounter <= 0;
      const headline = hidden
        ? `${eggName}: no egg dots in this 10 km patch · ${plainEvidence(state)}`
        : `${eggName}: ~${(row.p_encounter * 100).toFixed(0)}% chance in this 10 km patch · ${plainEvidence(state)}`;
      const interval = hidden
        ? `<p class="muted">No egg likelihood shown (unknown or out of domain).</p>`
        : `<p class="muted">Range ${(row.p_lo90 * 100).toFixed(0)}–${(row.p_hi90 * 100).toFixed(0)}% · near ${place}</p>`;
      const unknownLine =
        row.unknown_reason != null
          ? `<p class="unknown-reason muted">Internal reason: <code>${row.unknown_reason}</code></p>`
          : "";
      return `<article class="cell-card" data-cell-id="${row.cell_id}">
        <h4>${headline}</h4>
        <p class="evidence-line"><span class="plain">${plainEvidence(state)}</span> <code class="muted">${state}</code></p>
        ${interval}
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
  const labels = await Cesium.ArcGisMapServerImageryProvider.fromUrl(
    "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer",
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
  viewer.imageryLayers.addImageryProvider(labels);
  viewer.scene.globe.enableLighting = false;
  viewer.scene.globe.baseColor = Cesium.Color.fromCssColorString("#16324f");
  viewer.scene.screenSpaceCameraController.minimumZoomDistance = 25_000;
  return viewer;
}

function addGeographicContext(viewer) {
  viewer.entities.add({
    name: "pilot-domain",
    rectangle: {
      coordinates: Cesium.Rectangle.fromDegrees(
        DOMAIN.lonMin,
        DOMAIN.latMin,
        DOMAIN.lonMax,
        DOMAIN.latMax,
      ),
      material: Cesium.Color.fromCssColorString("#38bdf8").withAlpha(0.08),
      outline: true,
      outlineColor: Cesium.Color.fromCssColorString("#7dd3fc").withAlpha(0.75),
      outlineWidth: 2,
      height: 0,
    },
  });
  PLACE_MARKERS.forEach((place) => {
    viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(place.lon, place.lat, 0),
      point: {
        pixelSize: 8,
        color: Cesium.Color.fromCssColorString("#e2e8f0"),
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      },
      label: {
        text: place.name,
        font: "13px system-ui, sans-serif",
        fillColor: Cesium.Color.WHITE,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 3,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        pixelOffset: new Cesium.Cartesian2(0, -20),
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 2_500_000),
      },
    });
  });
}

function regionCameraDestination() {
  return Cesium.Cartesian3.fromDegrees(-119.2, 33.55, 520_000);
}

function paintDots(viewer, collection, rows, species, meta) {
  collection.removeAll();
  const spacing = meta.cell_spacing_km;
  const filtered = rows.filter((r) => r.species === species);
  filtered.forEach((row) => {
    const state = effectiveEvidenceState(row);
    const dots = eggDotsForRow(row, spacing);
    const ll = parseCellId(row.cell_id);
    if (ll && dots.length > 0) {
      const labelEntity = viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(ll.lon, ll.lat, 2000),
        label: {
          text: `${SPECIES_EGG_NAME[row.species] || "Eggs"}\n${plainEvidence(state)}`,
          font: "12px system-ui, sans-serif",
          fillColor: Cesium.Color.fromCssColorString("#fff4cc"),
          outlineColor: Cesium.Color.BLACK,
          outlineWidth: 3,
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          pixelOffset: new Cesium.Cartesian2(0, -18),
          distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 900_000),
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
        },
      });
      labelEntity.eggLayer = true;
    }
    dots.forEach((dot) => {
      const primitive = collection.add({
        position: Cesium.Cartesian3.fromDegrees(dot.lon, dot.lat, 0),
        pixelSize: 7,
        color: Cesium.Color.fromCssColorString("#ffe08a").withAlpha(dotAlpha),
        outlineColor: Cesium.Color.fromCssColorString("#3a2a00"),
        outlineWidth: 1,
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      });
      primitive._eggRank = dot.rank;
      primitive._eggCellId = row.cell_id;
    });
  });
}

function setDotAlpha(collection, alpha) {
  dotAlpha = alpha;
  for (let i = 0; i < collection.length; i += 1) {
    const dot = collection.get(i);
    const color = dot.color;
    dot.color = new Cesium.Color(color.red, color.green, color.blue, alpha);
  }
}

function fadeEggDots(collection, viewer) {
  const start = performance.now();
  const step = (now) => {
    const alpha = Math.min(1, (now - start) / 1400);
    setDotAlpha(collection, alpha);
    viewer.scene.requestRender();
    if (alpha < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

function playEggFlyIn(viewer, collection) {
  setDotAlpha(collection, 0);
  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(-125, 8, 20_000_000),
  });
  viewer.camera.flyTo({
    destination: regionCameraDestination(),
    duration: new URLSearchParams(location.search).get("shot") === "1" ? 0.3 : 6.2,
    easingFunction: Cesium.EasingFunction.CUBIC_IN_OUT,
    complete: () => fadeEggDots(collection, viewer),
    cancel: () => fadeEggDots(collection, viewer),
  });
}

function zoomToRegion(viewer, collection) {
  setDotAlpha(collection, dotAlpha || 1);
  viewer.camera.flyTo({
    destination: regionCameraDestination(),
    duration: 1.4,
    easingFunction: Cesium.EasingFunction.CUBIC_IN_OUT,
  });
}

function eggReadoutText(row) {
  const state = effectiveEvidenceState(row);
  const name = SPECIES_EGG_NAME[row.species] || row.species;
  if (isUnknownRow(row) || row.p_encounter == null || row.p_encounter <= 0) {
    return `${name}: no egg dots in this spawning patch. ${plainEvidence(state)} (${state}).`;
  }
  const pct = (row.p_encounter * 100).toFixed(0);
  return `${name}: ~${pct}% chance of eggs in this 10 km spawning patch. ${plainEvidence(state)} (${state}).`;
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
  const { rows: allRows, meta } = payload;

  const legend = document.getElementById("legend");
  const toggles = document.getElementById("species-toggle");
  const dayControl = document.getElementById("day-control");
  const list = document.getElementById("cell-list");
  const globeEl = document.getElementById("globe");

  renderLegend(legend);
  const wm = legend.querySelector(".watermark");
  const demoMark = `${meta.watermark} Demo data.`;
  const globeWm = document.querySelector("[data-testid=globe-watermark]");
  if (globeWm) globeWm.textContent = demoMark;
  if (wm) wm.textContent = demoMark;

  const speciesSet = [...new Set(allRows.map((r) => r.species))].sort();
  let activeSpecies = speciesSet.includes("anchovy") ? "anchovy" : speciesSet[0] ?? "sardine";
  const days = uniqueDays(allRows, meta);
  let activeDay = meta.valid_day && days.includes(meta.valid_day) ? meta.valid_day : days[0];

  const viewer = await createGlobe(globeEl);
  addGeographicContext(viewer);
  const dots = viewer.scene.primitives.add(new Cesium.PointPrimitiveCollection());

  const title = document.getElementById("map-title");
  const summary = document.getElementById("summary-headline");

  const refresh = () => {
    const rows = rowsForView(allRows, activeSpecies, activeDay);
    viewer.entities.values
      .filter((e) => e.eggLayer)
      .forEach((e) => viewer.entities.remove(e));

    paintDots(viewer, dots, rows, activeSpecies, meta);
    applyDotLod(viewer, dots);
    renderCellList(list, rows, activeSpecies);
    if (title) {
      title.textContent = `${titleCaseSpecies(activeSpecies)} spawning activity — ${formatShortDay(activeDay)} · demo`;
    }
    if (summary) {
      summary.textContent = computeSummaryHeadline(rows, activeSpecies);
    }
    renderSpeciesToggle(toggles, speciesSet, activeSpecies, (sp) => {
      activeSpecies = sp;
      refresh();
    });
    renderDayControl(dayControl, days, allRows, activeDay, (day) => {
      activeDay = day;
      refresh();
    });
  };
  refresh();

  viewer.camera.moveEnd.addEventListener(() => applyDotLod(viewer, dots));

  const readout = document.getElementById("egg-readout");
  const showReadout = (row) => {
    if (!readout) return;
    readout.textContent = row
      ? eggReadoutText(row)
      : "No egg dots here. Empty water means eggs are unlikely, or the egg evidence is unknown.";
  };
  const rowAt = (windowPosition) => {
    const picked = viewer.scene.pick(windowPosition);
    const cellId = picked && picked.primitive && picked.primitive._eggCellId;
    if (!cellId) return null;
    const rows = rowsForView(allRows, activeSpecies, activeDay);
    return rows.find((r) => r.cell_id === cellId) || null;
  };
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
  handler.setInputAction((movement) => {
    showReadout(rowAt(movement.endPosition));
  }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);
  handler.setInputAction((click) => {
    const row = rowAt(click.position);
    showReadout(row);
    if (row) {
      const card = list.querySelector(`[data-cell-id="${row.cell_id}"]`);
      if (card) card.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

  const replay = document.getElementById("replay-flyin");
  if (replay) replay.addEventListener("click", () => playEggFlyIn(viewer, dots));
  const zoomBtn = document.getElementById("zoom-region");
  if (zoomBtn) zoomBtn.addEventListener("click", () => zoomToRegion(viewer, dots));
  playEggFlyIn(viewer, dots);
  document.body.dataset.eggGlobe = "ready";
}

main().catch((err) => {
  console.error(err);
  document.body.insertAdjacentHTML(
    "beforeend",
    `<p role="alert">Failed to load spawning activity map: ${err.message}</p>`,
  );
});
