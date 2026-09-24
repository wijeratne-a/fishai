import "maplibre-gl/dist/maplibre-gl.css";
import "./styles.css";
import { setWorkerUrl } from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import { composeLiveSentence, emptyAnswer, renderAnswerStrip } from "./answer";
import { renderEvidenceHtml, renderPastReportCellHtml, renderPastReportsHtml } from "./evidence";
import {
  GOLIATH_APHIA_ID,
  mayDrawCurrentEstimate,
  mayDrawForecast,
  PAST_REPORTS_RESOLUTION,
  scientificStatusCopy,
  targetsCopy,
} from "./layers";
import { renderLegend } from "./legend";
import { createGlobeMap, resizeLater, type PastReportPick } from "./mapApp";
import { fetchPastReports } from "./obis";
import { exactPlace, searchPlaces, type NamedPlace } from "./places";
import { displayName, resolveSpecies, searchLocal } from "./search";
import type {
  AnswerStrip,
  AppState,
  CellProperties,
  CellRecord,
  DepthBand,
  FixtureCollection,
  MetaFixture,
  ModelCardGate,
  NavView,
  PastReportsSummary,
  TaxonRecord,
} from "./types";
import { DEPTH_LABELS, PLAIN_TRUTH } from "./types";

setWorkerUrl(workerUrl);

const HINT_KEY = "fishai-first-run-dismissed";

async function loadJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load ${url}: ${response.status}`);
  }
  return (await response.json()) as T;
}

function formatLocal(iso: string | null | undefined): string {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return new Intl.DateTimeFormat("en-US", {
    timeZone: "America/Los_Angeles",
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function setText(id: string, value: string): void {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function cellSupportsDepth(props: CellProperties, depth: DepthBand): boolean {
  if (depth === "surface") return props.depthSurface;
  if (depth === "intertidal") return props.depthIntertidal;
  if (depth === "0_10m") return props.depth0to10;
  return props.depthUnknown;
}

function quantityNote(props: CellProperties): string | undefined {
  if (props.visualTruthState === "DIRECT_OBSERVATION" && props.habitatClass === "not_applicable") {
    return `Water temperature (measured): ${props.sstC} °C. This is not a sighting of animals.`;
  }
  return undefined;
}

function cardFor(aphiaId: number, cards: ModelCardGate[]): ModelCardGate | undefined {
  return cards.find((card) => card.aphiaId === aphiaId);
}

function supportLine(taxon: TaxonRecord, card: ModelCardGate | undefined, past: PastReportsSummary | null): string {
  if (mayDrawCurrentEstimate(card)) {
    return "A published model card exists for a current estimate.";
  }
  if (taxon.status === "oyster_demo") {
    return "Past reports are not the point here. This demo is farm working conditions, not oyster GPS.";
  }
  if (past?.withheld) {
    return "Past reports exist but locations are withheld.";
  }
  if (past && past.total && past.total > 0) {
    return "Past reports exist. This is not where it is right now.";
  }
  if (taxon.status === "name_only" || taxon.status === "no_estimate") {
    return "Not enough data to estimate where it lives right now. No forecast issued.";
  }
  return "Not enough data to estimate where it lives.";
}

function whatShownFor(taxon: TaxonRecord | null, past: PastReportsSummary | null, demo: boolean): string {
  if (demo) return "Farm working-conditions demo — not a species location.";
  if (past?.withheld) return "Unknown now. Historical pattern withheld.";
  if (past && past.cellsDrawn > 0) return "Historical pattern (past reports). Not a current estimate.";
  if (taxon) return "Unknown — no issued location.";
  return "Empty globe. No species layer. Unknown is the scientific status.";
}

async function main(): Promise<void> {
  const mapEl = document.getElementById("map");
  const evidenceBody = document.getElementById("evidence-body");
  const evidenceEmpty = document.getElementById("evidence-empty");
  const cellSelect = document.getElementById("cell-select");
  const legendEl = document.getElementById("map-legend");
  const statusEl = document.getElementById("map-status");
  const depthDisclaimer = document.getElementById("depth-disclaimer");
  const answerEl = document.getElementById("answer-strip");
  const searchInput = document.getElementById("species-search");
  const searchBtn = document.getElementById("species-find");
  const resultsEl = document.getElementById("species-results");
  const noMatchEl = document.getElementById("species-empty");
  const stampEl = document.getElementById("map-stamp");
  const viewStatusEl = document.getElementById("map-view-status");
  const headingEl = document.getElementById("page-h1");
  const hintEl = document.getElementById("first-run");
  const controlsPanel = document.getElementById("rail-explore");
  const answerDock = document.getElementById("answer-dock");
  const evidenceDetails = document.getElementById("evidence-details");
  const resolutionEl = document.getElementById("resolution-chip");
  const coordsEl = document.getElementById("map-coords");
  const toggleControls = document.getElementById("toggle-controls");
  const toggleAnswer = document.getElementById("toggle-answer");
  const toolProjection = document.getElementById("tool-projection");
  const toolNorth = document.getElementById("tool-north");
  const toolHome = document.getElementById("tool-home");
  const toolZoomIn = document.getElementById("tool-zoom-in");
  const toolZoomOut = document.getElementById("tool-zoom-out");
  const mapHints = document.getElementById("map-hints");
  if (
    !(mapEl instanceof HTMLElement) ||
    !(evidenceBody instanceof HTMLElement) ||
    !(evidenceEmpty instanceof HTMLElement) ||
    !(cellSelect instanceof HTMLSelectElement) ||
    !(legendEl instanceof HTMLElement) ||
    !(statusEl instanceof HTMLElement) ||
    !(depthDisclaimer instanceof HTMLElement) ||
    !(answerEl instanceof HTMLElement) ||
    !(searchInput instanceof HTMLInputElement) ||
    !(searchBtn instanceof HTMLButtonElement) ||
    !(resultsEl instanceof HTMLElement) ||
    !(noMatchEl instanceof HTMLElement) ||
    !(stampEl instanceof HTMLElement) ||
    !(viewStatusEl instanceof HTMLElement) ||
    !(headingEl instanceof HTMLElement) ||
    !(hintEl instanceof HTMLElement) ||
    !(controlsPanel instanceof HTMLElement) ||
    !(answerDock instanceof HTMLElement) ||
    !(evidenceDetails instanceof HTMLDetailsElement) ||
    !(resolutionEl instanceof HTMLElement) ||
    !(coordsEl instanceof HTMLElement) ||
    !(toggleControls instanceof HTMLButtonElement) ||
    !(toggleAnswer instanceof HTMLButtonElement) ||
    !(toolProjection instanceof HTMLButtonElement) ||
    !(toolNorth instanceof HTMLButtonElement) ||
    !(toolHome instanceof HTMLButtonElement) ||
    !(toolZoomIn instanceof HTMLButtonElement) ||
    !(toolZoomOut instanceof HTMLButtonElement) ||
    !(mapHints instanceof HTMLElement)
  ) {
    throw new Error("Prototype markup is missing required nodes.");
  }

  const [meta, cells, land, water, stations, evidence, taxaFile, cardsFile] = await Promise.all([
    loadJson<MetaFixture>("/fixtures/meta.json"),
    loadJson<FixtureCollection<CellProperties>>("/fixtures/willapa-cells.geojson"),
    loadJson<FixtureCollection>("/fixtures/willapa-land.geojson"),
    loadJson<FixtureCollection>("/fixtures/willapa-water-outline.geojson"),
    loadJson<FixtureCollection>("/fixtures/stations.geojson"),
    loadJson<Record<string, CellRecord>>("/fixtures/evidence-by-cell.json"),
    loadJson<{ taxa: TaxonRecord[] }>("/fixtures/taxa.json"),
    loadJson<{ cards: ModelCardGate[] }>("/fixtures/model-cards.json"),
  ]);

  const catalog = taxaFile.taxa;
  const cards = cardsFile.cards;
  let past: PastReportsSummary | null = null;

  const propertiesById = new Map<string, CellProperties>();
  for (const feature of cells.features) {
    const props = feature.properties as CellProperties;
    propertiesById.set(props.cellId, props);
  }

  const state: AppState = {
    nav: "find",
    expert: false,
    mode: "earth_surface",
    unknownMap: false,
    depth: "unknown_depth",
    overlays: { sst: false, habitat: false, density: false },
    selectedCellId: null,
    selectedTaxon: null,
    dimWillapa: false,
    pastReportsVisible: false,
    showWillapaCells: false,
    publishedCurrentEstimate: false,
    publishedForecast: false,
  };

  const optionNodes = [...propertiesById.values()]
    .sort((a, b) => a.label.localeCompare(b.label) || a.cellId.localeCompare(b.cellId))
    .map((props) => {
      const option = document.createElement("option");
      option.value = props.cellId;
      const extra = props.visualTruthState === "DIRECT_OBSERVATION" ? " water temperature" : "";
      option.textContent = `${props.label} — ${PLAIN_TRUTH[props.visualTruthState]}${extra}`;
      return option;
    });
  cellSelect.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select a Willapa demo place";
  cellSelect.append(placeholder, ...optionNodes);

  const setControlsOpen = (open: boolean): void => {
    controlsPanel.hidden = !open;
    toggleControls.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.classList.toggle("controls-open", open);
    resizeLater(globe.map);
  };

  const setAnswerOpen = (open: boolean): void => {
    answerDock.hidden = !open;
    toggleAnswer.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.classList.toggle("answer-open", open);
    resizeLater(globe.map);
  };

  try {
    if (sessionStorage.getItem(HINT_KEY) === "1") hintEl.hidden = true;
  } catch {
    /* keep hint */
  }

  const fillTimebar = (): void => {
    const taxon = state.selectedTaxon;
    const card = taxon ? cardFor(taxon.aphiaId, cards) : undefined;
    const cell = state.selectedCellId ? propertiesById.get(state.selectedCellId) : undefined;
    const demoSoon = card?.allowsWillapaWorkingConditionsDemo && taxon?.status === "oyster_demo" && state.showWillapaCells;
    setText("t-asof", formatLocal(meta.timeReadout.environmentalInputsCurrentThrough));
    setText("t-soon", demoSoon ? "Next 72 hours (working conditions demo)" : "No forecast issued");
    setText(
      "t-obs",
      cell?.lastDirectObservation ? formatLocal(cell.lastDirectObservation) : "—",
    );
    setText("t-model", state.expert ? meta.timeReadout.modelVersion : "—");
    document.querySelectorAll(".expert-only").forEach((node) => {
      if (node instanceof HTMLElement) node.hidden = !state.expert;
    });
  };

  const setStrip = (strip: AnswerStrip): void => {
    renderAnswerStrip(answerEl, strip);
    statusEl.textContent = composeLiveSentence(strip);
  };

  const speciesAnswer = (taxon: TaxonRecord): AnswerStrip => {
    const card = cardFor(taxon.aphiaId, cards);
    const publishedNow = mayDrawCurrentEstimate(card);
    const publishedSoon = mayDrawForecast(card);
    const demo = taxon.status === "oyster_demo" && Boolean(card?.allowsWillapaWorkingConditionsDemo) && state.showWillapaCells;
    const name = `${displayName(taxon)} (${taxon.scientificName})`;
    if (taxon.aphiaId === GOLIATH_APHIA_ID) {
      const hist =
        past && past.total && past.total > 0 && !past.withheld
          ? `Public databases list ${past.total.toLocaleString()} compiled records${past.yearSpan ? ` (${past.yearSpan})` : ""}. Those are past reports at about 1° / 100 km — not where the animals are now. Exact spawning wrecks and nursery pins are withheld.`
          : past?.withheld
            ? "Historical locations are withheld."
            : past?.error
              ? `No evaluated model. Past-report lookup failed (${past.error}).`
              : "No published occurrence model. Optional past reports, if they appear, are historical and coarsened.";
      return {
        species: name,
        whereNow: "No issued location.",
        soon: "No forecast issued.",
        howSure: "Not assessed.",
        depth:
          "Ecology note, not a live map: juveniles in mangrove and estuary shallows; adults mostly on structure in about 0–50 m (published sources also list to ~100 m). Depth is not modeled here.",
        why: hist,
        thisIsNot: "Live tracking, a wreck map, a spawning-site list, or a count of animals.",
        whatShown: whatShownFor(taxon, past, false),
        scientificStatus: scientificStatusCopy({
          demo: false,
          past,
          publishedNow,
          publishedSoon,
          withheld: Boolean(past?.withheld),
        }),
        supportLine: supportLine(taxon, card, past),
        targetsNote: targetsCopy({ card, past, demo: false }),
        whatCouldBeWrong:
          "A past-report cell can be sampling bias, not a living fish. Mangrove or reef conditions are not confirmed presence. July–September is a published spawning season, not a live aggregation. This product does not know where every goliath grouper is.",
      };
    }
    if (demo) {
      return {
        species: name,
        whereNow: "Planted oysters are not counted on this map.",
        soon: "Farm working conditions, next 72 hours (demo rule).",
        howSure: "Low",
        depth: "Tide flat: air at low tide, water at high tide.",
        why: "Hot air at low tide, plus wind and waves. Sea-surface temperature is not body temperature.",
        thisIsNot: "Food-safety, harvest permission, or oyster GPS.",
        whatShown: whatShownFor(taxon, past, true),
        scientificStatus: scientificStatusCopy({ demo: true, past, publishedNow, publishedSoon }),
        supportLine: supportLine(taxon, card, past),
        targetsNote: targetsCopy({ card, past, demo: true }),
      };
    }
    return {
      species: name,
      whereNow: publishedNow ? "A published current estimate is on the map." : "No issued location.",
      soon: publishedSoon ? "A published forecast is on the map." : "No forecast issued.",
      howSure: "None",
      depth: "Depth unknown / not modeled.",
      why:
        past && past.total && past.total > 0 && !past.withheld
          ? `Public databases list ${past.total.toLocaleString()} past reports${past.yearSpan ? ` (${past.yearSpan})` : ""}. Those are old detections, not where the animals are now. ${PAST_REPORTS_RESOLUTION.nativeSourceResolution}.`
          : past?.error
            ? `No evaluated model in this product. Past-report lookup failed (${past.error}).`
            : "No observations or evaluated model for this species in this product.",
      thisIsNot: "Live tracking, a fishing map, or a count of animals.",
      whatShown: whatShownFor(taxon, past, false),
      scientificStatus: scientificStatusCopy({
        demo: false,
        past,
        publishedNow,
        publishedSoon,
        withheld: Boolean(past?.withheld),
      }),
      supportLine: supportLine(taxon, card, past),
      targetsNote: targetsCopy({ card, past, demo: false }),
    };
  };

  const showCell = (cellId: string): void => {
    const taxon = state.selectedTaxon;
    if (taxon && taxon.status !== "oyster_demo") {
      return;
    }
    if (!state.showWillapaCells) return;
    const props = propertiesById.get(cellId);
    const record = evidence[cellId];
    if (!props || !record) return;
    state.selectedCellId = cellId;
    cellSelect.value = cellId;
    evidenceEmpty.hidden = true;
    evidenceBody.hidden = false;
    evidenceBody.innerHTML = renderEvidenceHtml(
      props.cellId,
      props.label,
      PLAIN_TRUTH[props.visualTruthState],
      props.publishClass,
      record,
      state.expert,
    );
    const oysterDemoCell = taxon?.status === "oyster_demo" && props.isOpsRiskExample;
    const strip: AnswerStrip = oysterDemoCell && taxon
      ? {
          ...speciesAnswer(taxon),
          quantityNote: quantityNote(props),
        }
      : {
          species: taxon ? displayName(taxon) : "Willapa place (no species)",
          whereNow: `${props.label} — ${PLAIN_TRUTH[props.visualTruthState]}.`,
          soon:
            props.visualTruthState === "FORECAST"
              ? "A future window is shown for this demo cell."
              : "No forecast issued.",
          howSure: props.confidence,
          depth: cellSupportsDepth(props, state.depth)
            ? DEPTH_LABELS[state.depth]
            : "This place has no fixture for the selected depth — not biological absence.",
          why: record.answers.why,
          thisIsNot: "Live tracking, harvest permission, or a count of animals.",
          whatShown: "Willapa working-conditions demo cell.",
          scientificStatus: scientificStatusCopy({ demo: true, past, publishedNow: false, publishedSoon: false }),
          quantityNote: quantityNote(props),
          targetsNote: targetsCopy({ card: taxon ? cardFor(taxon.aphiaId, cards) : undefined, past, demo: true }),
        };
    setStrip(strip);
    fillTimebar();
    globe.select(cellId);
    setAnswerOpen(true);
  };

  const showPastReportCell = (pick: PastReportPick): void => {
    evidenceEmpty.hidden = true;
    evidenceBody.hidden = false;
    evidenceBody.innerHTML = renderPastReportCellHtml(state.selectedTaxon, pick.label, pick.n);
    evidenceDetails.open = true;
    setAnswerOpen(true);
    const taxon = state.selectedTaxon;
    setStrip({
      species: taxon ? `${displayName(taxon)} (${taxon.scientificName})` : "No species selected",
      whereNow: "No issued location.",
      soon: "No forecast issued.",
      howSure: taxon?.aphiaId === GOLIATH_APHIA_ID ? "Not assessed." : "None",
      depth:
        taxon?.aphiaId === GOLIATH_APHIA_ID
          ? "Ecology note, not a live map: juveniles in mangrove and estuary shallows; adults mostly on structure in about 0–50 m. Depth is not modeled here."
          : "Depth unknown / not modeled.",
      why: `Past-report cell “${pick.label}” has ${pick.n.toLocaleString()} compiled records. This is a partial extract of historical reports, not where the animals are now. Missing cells are not biological absence.`,
      thisIsNot: "Live tracking, a fishing map, or a count of animals.",
      whatShown: "Past reports (historical pattern). Not a current estimate.",
      scientificStatus: scientificStatusCopy({
        demo: false,
        past,
        publishedNow: false,
        publishedSoon: false,
      }),
      supportLine: "Past reports exist. This is not where it is right now.",
      whatCouldBeWrong:
        taxon?.aphiaId === GOLIATH_APHIA_ID
          ? "A past-report cell can be sampling bias, not a living fish. This product does not know where every goliath grouper is."
          : "A past-report cell can be sampling bias, not a living animal.",
    });
  };

  const globe = await createGlobeMap({
    container: mapEl,
    land,
    water,
    cells,
    stations,
    onSelect: showCell,
    onPastReportSelect: showPastReportCell,
  });

  const syncProjectionChrome = (): void => {
    const flat = globe.getProjectionMode() === "mercator";
    const flatBox = document.getElementById("flat-map");
    if (flatBox instanceof HTMLInputElement) flatBox.checked = flat;
    toolProjection.textContent = flat ? "2D flat map" : "3D globe";
    toolProjection.setAttribute("aria-pressed", flat ? "true" : "false");
    mapHints.textContent = flat
      ? "Drag to pan the map. Scroll or pinch to zoom. Click a highlighted area for details."
      : "Drag to rotate the globe. Scroll or pinch to zoom. Click a highlighted area for details.";
  };

  const viewLabel = (): string =>
    globe.getProjectionMode() === "globe" ? "3D globe" : "2D flat map";

  const refreshResolution = (): void => {
    let chip = globe.resolutionChip();
    if (state.pastReportsVisible) {
      chip += " · Past reports: ~1° / 100 km. Zooming in does not sharpen the biology.";
    }
    resolutionEl.textContent = chip;
  };

  const refreshViewStatus = (extra?: string): void => {
    const base = `${viewLabel()} · Not live tracking`;
    const line = extra ? `${base} · ${extra}` : base;
    viewStatusEl.textContent = line;
    if (!extra) {
      stampEl.textContent = base;
    }
    refreshResolution();
  };

  const applyUi = (): void => {
    globe.apply(state);
    renderLegend(legendEl, state);
    syncProjectionChrome();
    if (state.selectedTaxon?.status === "oyster_demo" && state.showWillapaCells && state.depth === "intertidal") {
      depthDisclaimer.textContent =
        "Tide flat: oysters can be in air at low tide. That is not a stack of swimming animals.";
    } else if (state.depth === "unknown_depth") {
      depthDisclaimer.textContent = "Depth is unknown unless a record or model actually has it.";
    } else {
      depthDisclaimer.textContent =
        "This depth band is a filter on the demo cells. It is not a water column of animals.";
    }
    const gapHint = document.getElementById("gap-hint");
    if (gapHint) {
      gapHint.textContent = state.unknownMap
        ? "Gap view is on. Temperature dots are hidden so they are not mistaken for animals."
        : "Stripes mean we do not know. They do not mean the ocean is empty.";
    }
    const pastExtra =
      past && past.cellsDrawn > 0
        ? past.yearSpan
          ? `Past reports ${past.yearSpan} · not where they are now`
          : "Past reports (coarse) · not where they are now"
        : null;
    if (pastExtra) {
      stampEl.textContent = pastExtra;
      refreshViewStatus(pastExtra);
    } else if (state.dimWillapa) {
      stampEl.textContent = "No estimate for this species";
      refreshViewStatus("No issued location");
    } else if (state.selectedTaxon?.status === "oyster_demo" && state.showWillapaCells) {
      stampEl.textContent = "Willapa working-conditions demo · not harvest advice";
      refreshViewStatus("Working-conditions demo");
    } else {
      refreshViewStatus();
    }
    fillTimebar();
    if (state.selectedCellId && state.showWillapaCells) showCell(state.selectedCellId);
  };

  const setNav = (nav: NavView): void => {
    state.nav = nav;
    document.querySelectorAll<HTMLButtonElement>(".nav-btn").forEach((btn) => {
      btn.classList.toggle("is-active", btn.dataset.nav === nav);
    });
    const learn = document.getElementById("learn");
    if (learn) learn.hidden = nav !== "learn";
    headingEl.textContent =
      nav === "find"
        ? "Find a saltwater species"
        : nav === "explore"
          ? "Explore the ocean"
          : nav === "evidence"
            ? "Evidence and data"
            : "Learn and methods";
    if (nav === "explore") {
      state.mode = "earth_surface";
      setControlsOpen(true);
      setAnswerOpen(true);
      if (!state.selectedTaxon || !state.showWillapaCells) {
        if (!(past && past.cellsDrawn > 0)) {
          globe.showWorld();
        }
      }
    } else if (nav === "find") {
      setAnswerOpen(true);
      searchInput.focus();
    } else if (nav === "evidence") {
      setAnswerOpen(true);
      evidenceDetails.open = true;
      document.getElementById("evidence")?.focus();
    } else if (nav === "learn") {
      setAnswerOpen(true);
    }
    applyUi();
    resizeLater(globe.map);
  };

  const renderMatches = (matches: TaxonRecord[], places: NamedPlace[]): void => {
    resultsEl.innerHTML = "";
    if (matches.length === 0 && places.length === 0) {
      resultsEl.hidden = true;
      return;
    }
    resultsEl.hidden = false;
    for (const place of places) {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = `Place — ${place.name}`;
      button.addEventListener("click", () => {
        resultsEl.hidden = true;
        flyToNamedPlace(place);
      });
      li.append(button);
      resultsEl.append(li);
    }
    for (const taxon of matches) {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = `${displayName(taxon)} — ${taxon.scientificName}`;
      button.addEventListener("click", () => {
        void selectTaxon(taxon);
      });
      li.append(button);
      resultsEl.append(li);
    }
  };

  const flyToNamedPlace = (place: NamedPlace): void => {
    globe.flyToPlace(place.center, place.zoom, place.bounds);
    setStrip({
      species: "No species selected",
      whereNow: `${place.name} — geographic view only.`,
      soon: "No forecast issued.",
      howSure: "None",
      depth: "Depth unknown",
      why: "This is a place on Earth, not a species location estimate.",
      thisIsNot: "Live tracking, a fishing map, or a count of animals.",
      whatShown: "Basemap and bathymetry shading only. Unknown as a species map.",
      scientificStatus: "Unknown.",
      targetsNote:
        "Observed presence, occurrence probability, relative abundance, and movement are not issued. This is a place, not a species estimate.",
    });
    setAnswerOpen(true);
    refreshViewStatus(`Viewing ${place.name}`);
  };

  const selectTaxon = async (
    taxon: TaxonRecord,
    options: { openOysterDemo?: boolean } = {},
  ): Promise<void> => {
    resultsEl.hidden = true;
    state.selectedTaxon = taxon;
    past = null;
    state.pastReportsVisible = false;
    globe.setPastReports(null);
    const card = cardFor(taxon.aphiaId, cards);
    state.publishedCurrentEstimate = mayDrawCurrentEstimate(card);
    state.publishedForecast = mayDrawForecast(card);
    const demo =
      taxon.status === "oyster_demo" &&
      Boolean(card?.allowsWillapaWorkingConditionsDemo) &&
      Boolean(options.openOysterDemo);

    if (taxon.status === "oyster_demo" && !demo) {
      state.dimWillapa = true;
      state.showWillapaCells = false;
      state.selectedCellId = null;
      cellSelect.value = "";
      globe.select(null);
      globe.showWorld();
      evidenceEmpty.hidden = true;
      evidenceBody.hidden = false;
      evidenceBody.innerHTML = `<p class="lede">${displayName(taxon)}</p>
        <p>This name has a Willapa working-conditions demo on Learn. It is farm air, tide, and waves — not oyster GPS.</p>`;
      setStrip({
        species: `${displayName(taxon)} (${taxon.scientificName})`,
        whereNow: "No issued location.",
        soon: "No forecast issued.",
        howSure: "None",
        depth: "Depth unknown / not modeled.",
        why: "No published location model. Open the demo from Learn for farm working conditions only.",
        thisIsNot: "Food-safety, harvest permission, or oyster GPS.",
        whatShown: "Empty globe. Demo stays on Learn. Unknown is the scientific status.",
        scientificStatus: "Unknown.",
        supportLine: "Not enough data to estimate where it lives right now. No forecast issued.",
        targetsNote: targetsCopy({ card, past: null, demo: false }),
      });
      setAnswerOpen(true);
      applyUi();
      return;
    }

    if (demo) {
      state.dimWillapa = false;
      state.showWillapaCells = true;
      globe.setAtlasMode("willapa");
      setStrip(speciesAnswer(taxon));
      stampEl.textContent = "Willapa working-conditions demo · not harvest advice";
      setNav("explore");
      const opsId = meta.opsRiskExampleCellId;
      if (opsId) showCell(opsId);
      applyUi();
      return;
    }

    state.dimWillapa = true;
    state.showWillapaCells = false;
    state.selectedCellId = null;
    globe.select(null);
    evidenceEmpty.hidden = true;
    evidenceBody.hidden = false;
    evidenceBody.innerHTML = renderPastReportsHtml(taxon, null);
    setStrip(speciesAnswer(taxon));
    globe.showWorld();
    setAnswerOpen(true);
    applyUi();

    const reports = await fetchPastReports(taxon.scientificName, taxon.aphiaId);
    if (state.selectedTaxon?.aphiaId !== taxon.aphiaId) return;
    past = reports.summary;
    evidenceBody.innerHTML = renderPastReportsHtml(taxon, past);
    setStrip(speciesAnswer(taxon));
    if (reports.collection && reports.collection.features.length > 0) {
      globe.setPastReports(reports.collection);
      state.pastReportsVisible = true;
      stampEl.textContent = past.yearSpan
        ? `Past reports ${past.yearSpan} · not where they are now`
        : "Past reports (coarse) · not where they are now";
    } else {
      globe.setPastReports(null);
      state.pastReportsVisible = false;
    }
    applyUi();
  };

  const runSearch = async (): Promise<void> => {
    const query = searchInput.value;
    noMatchEl.hidden = true;
    const placeHit = exactPlace(query);
    const resolved = await resolveSpecies(query, catalog);
    if (resolved.matches.length === 0 && !placeHit && searchPlaces(query).length === 0) {
      resultsEl.hidden = true;
      noMatchEl.hidden = false;
      noMatchEl.textContent = "No matching name.";
      state.selectedTaxon = null;
      past = null;
      state.dimWillapa = false;
      state.showWillapaCells = false;
      state.pastReportsVisible = false;
      state.publishedCurrentEstimate = false;
      state.publishedForecast = false;
      globe.setPastReports(null);
      globe.showWorld();
      setStrip(emptyAnswer());
      applyUi();
      return;
    }
    renderMatches(resolved.matches, searchPlaces(query));
    if (resolved.exact) {
      await selectTaxon(resolved.exact);
      return;
    }
    if (placeHit && resolved.matches.length === 0) {
      resultsEl.hidden = true;
      flyToNamedPlace(placeHit);
    }
  };

  searchInput.addEventListener("input", () => {
    const matches = searchLocal(searchInput.value, catalog);
    noMatchEl.hidden = true;
    renderMatches(matches, searchPlaces(searchInput.value));
  });
  searchBtn.addEventListener("click", () => {
    void runSearch();
  });
  searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      void runSearch();
    }
  });

  document.querySelectorAll<HTMLButtonElement>(".nav-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const nav = btn.dataset.nav as NavView | undefined;
      if (nav) setNav(nav);
    });
  });

  const expertBox = document.getElementById("expert-mode");
  if (expertBox instanceof HTMLInputElement) {
    expertBox.addEventListener("change", () => {
      state.expert = expertBox.checked;
      applyUi();
    });
  }

  const unknownBox = document.getElementById("unknown-map");
  if (unknownBox instanceof HTMLInputElement) {
    unknownBox.addEventListener("change", () => {
      state.unknownMap = unknownBox.checked;
      applyUi();
    });
  }

  document.querySelectorAll<HTMLInputElement>('input[name="depth"]').forEach((input) => {
    input.addEventListener("change", () => {
      if (!input.checked) return;
      state.depth = input.value as DepthBand;
      applyUi();
    });
  });

  const bindOverlay = (id: string, key: "sst" | "habitat" | "density"): void => {
    const box = document.getElementById(id);
    if (!(box instanceof HTMLInputElement)) return;
    box.addEventListener("change", () => {
      state.overlays[key] = box.checked;
      applyUi();
    });
  };
  bindOverlay("overlay-sst", "sst");
  bindOverlay("overlay-habitat", "habitat");
  bindOverlay("overlay-density", "density");

  cellSelect.addEventListener("change", () => {
    if (cellSelect.value) showCell(cellSelect.value);
  });

  evidenceBody.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLButtonElement) || !target.classList.contains("copy-json")) return;
    const cellId = target.getAttribute("data-cell");
    if (!cellId) return;
    const props = propertiesById.get(cellId);
    const record = evidence[cellId];
    const payload = JSON.stringify({ cell: props, record, disclaimer: meta.disclaimer }, null, 2);
    await navigator.clipboard.writeText(payload);
    target.textContent = "Copied";
    window.setTimeout(() => {
      target.textContent = "Copy cell JSON";
    }, 1200);
  });

  const flatBox = document.getElementById("flat-map");
  if (flatBox instanceof HTMLInputElement) {
    flatBox.checked = globe.getProjectionMode() === "mercator";
    flatBox.addEventListener("change", () => {
      globe.setProjectionMode(flatBox.checked ? "mercator" : "globe");
      applyUi();
    });
  }

  toolProjection.addEventListener("click", () => {
    const next = globe.getProjectionMode() === "globe" ? "mercator" : "globe";
    globe.setProjectionMode(next);
    applyUi();
  });
  toolNorth.addEventListener("click", () => {
    globe.resetNorth();
  });
  toolHome.addEventListener("click", () => {
    globe.showWorld();
  });
  toolZoomIn.addEventListener("click", () => {
    globe.zoomBy(1);
  });
  toolZoomOut.addEventListener("click", () => {
    globe.zoomBy(-1);
  });

  document.getElementById("north-up")?.addEventListener("click", () => {
    globe.resetNorth();
  });
  document.getElementById("reset-tilt")?.addEventListener("click", () => {
    globe.resetTilt();
  });
  document.getElementById("home-view")?.addEventListener("click", () => {
    globe.showWorld();
  });
  document.getElementById("view-back")?.addEventListener("click", () => {
    globe.goBack();
  });

  document.getElementById("learn-oyster")?.addEventListener("click", () => {
    const oyster = catalog.find((taxon) => taxon.aphiaId === 836033);
    if (oyster) void selectTaxon(oyster, { openOysterDemo: true });
  });

  document.getElementById("first-run-dismiss")?.addEventListener("click", () => {
    hintEl.hidden = true;
    try {
      sessionStorage.setItem(HINT_KEY, "1");
    } catch {
      /* session only */
    }
  });

  toggleControls.addEventListener("click", () => {
    setControlsOpen(controlsPanel.hidden);
  });
  toggleAnswer.addEventListener("click", () => {
    setAnswerOpen(answerDock.hidden);
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      resultsEl.hidden = true;
      hintEl.hidden = true;
      if (document.activeElement === searchInput) searchInput.blur();
      return;
    }
    const target = event.target;
    if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement) {
      return;
    }
    if (event.key === "h" || event.key === "H") globe.showWorld();
    if (event.key === "n" || event.key === "N") globe.resetNorth();
    if (event.key === "0") globe.resetTilt();
    if (event.key === "[") globe.goBack();
  });

  globe.map.on("mousemove", (event) => {
    coordsEl.textContent = `${event.lngLat.lat.toFixed(2)}°, ${event.lngLat.lng.toFixed(2)}°`;
  });
  globe.map.on("zoomend", refreshResolution);
  globe.map.on("moveend", refreshResolution);

  window.addEventListener("resize", () => resizeLater(globe.map));
  resizeLater(globe.map);

  setStrip(emptyAnswer());
  setAnswerOpen(true);
  setControlsOpen(false);
  setNav("find");
  applyUi();
  refreshResolution();
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : "Unknown boot error";
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<p role="alert" class="banner-line">${message}. Fixtures must be present under /public/fixtures.</p>`,
  );
  console.error(error);
});
