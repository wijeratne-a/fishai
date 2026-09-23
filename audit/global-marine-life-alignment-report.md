# Global Marine Life Intelligence System — Codebase Alignment Audit

**Date:** 2026-09-22  
**Auditor mode:** Read-only except this file.  
**Live product code inspected:** `globe/prototype/` (Vite + TypeScript + MapLibre GL JS).  
**Spec libraries inspected:** `GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md`, `observatory/`, `globe/*.md`, `audit/00–11`, commercial artifacts.  
**Design folder:** present but empty (`design/`); `design/competitor-synthesis.md` not cited.  
**Code modified:** none (only this report created).

---

## 1. Executive Summary

**Success question:** This codebase is **not** yet building a planetary saltwater marine-life intelligence system that estimates where species are likely to be now and in the future. It is an **honest, human-usable MapLibre globe prototype** (species search, answer strip, past-report grids, Willapa fixture demo) **plus a large specification / catalog library** (observatory markdown/CSV, model-card gates, rights policies). There is **no separate backend**, **zero `PUBLISHED` location/forecast models**, and **no digital twin** in runnable code.

Post–P0 redesign work (Phases A–G, verified in `globe/prototype/VERIFICATION.md`) fixed the earlier UX failure where cold load opened Category D OPS-RISK: Find Species + empty answer strip now pass the yellowfin “honest no-data” test. That improves **alignment of chrome with the vision**, not delivery of the vision’s scientific core.

| Dimension | Score (0–100) |
|---|---|
| 3.1 Vision alignment | **38** |
| 3.2 Geospatial and ocean-state | **28** |
| 3.3 Species, behavior, climate | **22** |
| 3.4 Inference, forecasting, digital twin | **18** |
| 3.5 Globe, map, visualization | **58** |
| 3.6 UX and plain language | **70** |
| 3.7 Active observation and data gaps | **30** |
| 3.8 Data rights, FAIR/CARE, sensitive locations | **55** |

---

## 2. Intended System Summary

Judged against the goal:

> A planetary saltwater marine-life intelligence system, with an interactive Google Earth–style globe UI, at the most granular geospatial level justified by data, that estimates where species are likely to be **now** and in the **future**, with species-specific biology, behavior, and climate dynamics, clear uncertainty, and a human-friendly, highly visual interface.

And against `GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md`:

- Scientific honesty: distinguish OBSERVED / INFERRED / FORECAST / UNKNOWN; never invent live density from SST, chlorophyll, AIS, or empty water (`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` L7–8, L14–43).
- UI contract §32: Google Earth–style globe; Find Species default; answer first (where now, soon, certainty, depth, why); separate observed vs model vs forecast; depth/time; Expert Mode for science; 2D fallback (`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` L55–260).
- Flagship demo: likelihood now + 3–7 day forecast animation + depth slices + env overlay + confidence — “impressive visually, conservative scientifically” (`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` L402–424).

Prior audit P0 honesty decisions (still binding; do not contradict):

- No fake tuna heatmap; empty = don’t know, not absence (`audit/00_executive_summary.md` L61–63; `audit/05_map_globe_scientific_honesty_audit.md` L47–62).
- Current location / forecast only behind published model cards (`audit/09_redesign_spec.md` L1–5; `globe/prototype/public/fixtures/model-cards.json` L1–2).
- Cold load must not open Category D; Expert holds 16 fields (`audit/11_implementation_plan.md` L9–19, L28–34).
- Commercial email/PDF farm wedge is a separate product surface, not the globe (`audit/00_executive_summary.md` L98–100; `artifacts/product_and_monetization/wireframe_spec.md` L3–5).

---

## 3. Alignment Findings by Dimension

### 3.1 Vision alignment — score **38**

**What the plan requires**  
A planetary biological intelligence layer: species likelihood now/future on a globe, biology/behavior/climate, uncertainty, human-friendly visuals (`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` L61–64, L402–422). Root README still frames a commercial 1×1×1×1 wedge and `STATE_10_PAUSED_FOR_HUMAN_DECISION` (`README.md` L7–14, L35).

**What the code actually does**  
One Vite SPA. No API server. Species search returns honest **no issued location / no forecast** for essentially all taxa; only Magallana gigas has a Learn-gated working-conditions demo; OBIS past reports are historical, not “now.”

**Positive alignment**

```4:6:globe/prototype/README.md
**Stack:** Vite 6.4.3 + TypeScript 5.9.3 + MapLibre GL JS 6.10.0 (2D map; no Cesium).

Search a fish or crustacean name. Most species return **no current location** and **no forecast**.
```

```202:226:globe/prototype/src/main.ts
  const speciesAnswer = (taxon: TaxonRecord): AnswerStrip => {
    const card = cardFor(taxon.aphiaId, cards);
    const publishedNow = card?.publishStatus === "PUBLISHED" && card.hasCurrentEstimate;
    const publishedSoon = card?.publishStatus === "PUBLISHED" && card.hasForecast;
    // ...
      whereNow: publishedNow
        ? "A published current estimate exists (none in this build)."
        : "No issued location.",
      soon: publishedSoon ? "A published forecast exists (none in this build)." : "No forecast issued.",
```

```1:16:globe/prototype/public/fixtures/model-cards.json
  "note": "A species may show current location or a forecast only when a card is PUBLISHED and a baseline was beaten. Today that count is zero.",
  "cards": [
    {
      "aphiaId": 836033,
      ...
      "publishStatus": "NOT_PUBLISHED",
      "hasCurrentEstimate": false,
      "hasForecast": false,
```

**Misalignment / missing**

- No runnable path from search → current likelihood map → forecast playback (prompt §32 H).
- Observatory digital-twin / ensemble / ecology material is markdown only (e.g. `observatory/hypothesis_experiment_cards/H-4.4_digital_twin_data_assimilation.md` L1–15: fish twin `REQUIRES_RESEARCH_BREAKTHROUGH`).
- Repo still carries commercial email-wedge specs that do not advance the globe goal (`artifacts/product_and_monetization/wireframe_spec.md` L3–5: “No GIS app”).

**Impact**  
Users and stakeholders can confuse “impressive docs + honest globe chrome” with a working planetary estimator. Scientifically the project correctly refuses fake now-maps; product-wise the vision remains aspirational.

**Recommended actions**  
- **DOCUMENT:** Keep root/product copy stating “honest prototype + specs, not a live twin.”  
- **RE-SCOPE:** Explicitly separate (A) globe atlas R&D, (B) Willapa farm email wedge, (C) observatory catalog — three tracks.  
- **FLESH OUT:** One taxon × one basin with a real publish gate path (still honesty-first).  
- **REALIGN:** Do not market flagship “Google Earth for marine life” until a published card exists.

---

### 3.2 Geospatial and ocean-state — score **28**

**What the plan requires**  
Global spatial index with LOD; env overlays (currents, temperature, productivity) as toggles; depth slices; granularity justified by data/privacy (`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` L181–187, L262–298). Observatory catalogs EMIVs and ocean variables (`observatory/emiv/emiv_catalog.md`, `observatory/data_catalog_notes.md` L19–20: `catalog_only_not_ingested`).

**What the code actually does**  
MapLibre demotiles + optional Sentinel-2 raster; Willapa hex fixtures; OBIS ~1° past-report grid; fixture SST/habitat overlays on Willapa only (not global ocean-state assimilations).

**Positive alignment**

```132:165:globe/prototype/src/mapApp.ts
  const map = new MapLibreMap({
    container: options.container,
    style: "https://demotiles.maplibre.org/style.json",
    center: WORLD_CENTER,
    zoom: WORLD_ZOOM,
    pitch: projectionMode === "globe" ? WORLD_PITCH : 0,
    ...
  });
  ...
  map.setProjection({ type: projectionMode });
```

```102:115:globe/prototype/src/obis.ts
    const grid = (await obisGet(
      `https://api.obis.org/v3/occurrence/grid/1?scientificname=${name}`,
    )) as {
```

```113:115:globe/prototype/index.html
            <label><input type="checkbox" id="overlay-sst" /> Water-skin temperature (°C)</label>
            <label><input type="checkbox" id="overlay-habitat" /> Habitat class (not animals)</label>
```

**Misalignment / missing**

- No tiling/LOD biological grid at sub-km where justified (`globe/tile_and_lod_design.md` is design-only; not wired).
- No live CMEMS/ocean physics ingest (`observatory/data_catalog_notes.md` L7: “Ingest: none”).
- Depth radios filter Willapa fixture flags; they are not a water-column model (`main.ts` L314–316: “not a water column of animals”).
- `meta.json` lists modes not in prototype: vertical/horizontal depth slices, seafloor habitat, timelapse forecast (`modesNotInPrototype` includes those strings — verified via fixture load).

**Impact**  
Geospatial **presentation** exists; geospatial **ocean intelligence** does not. Past-report coarsening is the only planetary biological layer.

**Recommended actions**  
- **FLESH OUT:** Env overlays from catalogued PUBLIC sources as labeled covariates (never as abundance).  
- **REALIGN:** Wire a real global coverage/uncertainty hatch from catalog metadata before claiming planetary grain.  
- **DOCUMENT:** README line still says “2D map” while code defaults to globe projection — fix docs only when allowed outside audit.  
- **REMOVE/ARCHIVE:** Do not implement 3D water-column volume until data justifies (`globe/volume_4d_spec.md` remains speculative).

---

### 3.3 Species, behavior, climate — score **22**

**What the plan requires**  
Species cards with biology, behavior, climate response; Learn mode species cards (`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` L209–217). Support tiers T0–T7 (`observatory/global_species_registry/support_tier_framework.md` L8–69). Ecology profiles factory step (`observatory/species_ecology_profiles/README.md`).

**What the code actually does**  
Local `taxa.json` (37 taxa: 36 `no_estimate`, 1 `oyster_demo`) + WoRMS name lookup. No behavior models, no climate-response surfaces, no ecology profile cards in product.

**Positive alignment**

```12:28:globe/prototype/src/search.ts
export function searchLocal(query: string, catalog: TaxonRecord[]): TaxonRecord[] {
  const q = normalize(query);
  ...
  return scored.slice(0, 12).map((row) => row.taxon);
}
```

```74:86:globe/prototype/src/worms.ts
  return {
    aphiaId,
    scientificName,
    commonNames: record.vernacular ? [record.vernacular] : [],
    group,
    status: "name_only",
    note: `Name from WoRMS (${UA_NOTE}). Not a location estimate.`,
  };
```

```1:8:observatory/global_species_registry/support_tier_framework.md
# Species support-tier framework
...
No taxon may be upgraded without cited evidence. Most saltwater taxa in the world are T0 or T1.
```

**Misalignment / missing**

```1:5:observatory/species_ecology_profiles/README.md
# Species ecology profiles

**Status:** empty of profile cards  
**Date:** 2026-09-18  
```

- Learn panel teaches encodings + oyster demo button; no species biology cards (`index.html` L136–156).
- Climate dynamics / migration only as hypothesis markdown (e.g. `observatory/hypothesis_experiment_cards/`).

**Impact**  
Name resolution works; species **intelligence** does not. Climate/behavior remain paper plans.

**Recommended actions**  
- **FLESH OUT:** One ecology profile + support-tier row surfaced in Learn for a non-demo fish.  
- **REALIGN:** UI “Why” should eventually cite drivers from EMIV relevance graph, not only OBIS counts.  
- **DOCUMENT:** Keep T0/T1 as default product truth until publish gates fire.

---

### 3.4 Inference, forecasting, digital twin — score **18**

**What the plan requires**  
Published model cards before current/forecast claims; digital twin / DA as research track (`observatory/model_cards/permitted_vs_prohibited_claims.md` L19; `H-4.4` fish twin breakthrough-gated).

**What the code actually does**  
Hard gate on `PUBLISHED` + `hasCurrentEstimate` / `hasForecast`. Count = zero. Willapa “FORECAST” cells are farm **working-conditions** fixtures (Category D), not animal location forecasts. No twin loop, no ensemble runtime.

**Positive alignment**

```1:2:globe/prototype/public/fixtures/model-cards.json
  "note": "A species may show current location or a forecast only when a card is PUBLISHED and a baseline was beaten. Today that count is zero.",
```

```90:96:globe/prototype/src/evidence.ts
function renderOpsPlain(ops: OpsRiskBlock): string {
  return `<section class="ops ops-plain" aria-label="Oyster working-conditions demo">
    <h3>Farm working conditions (demo)</h3>
    <p>This is a risk estimate for farm work over the next 72 hours — not a count of oysters, not food-safety, and not permission to harvest.
```

```11:15:observatory/hypothesis_experiment_cards/H-4.4_digital_twin_data_assimilation.md
**readiness (physics/BGC twin as prior):** `REQUIRES_PARTNERSHIP` ...
**readiness (fish twin):** `REQUIRES_RESEARCH_BREAKTHROUGH`  
**forbidden quantity:** assimilated fish/shellfish abundance
```

**Misalignment / missing**

- No inference service, no forecast time slider animation of species likelihood.
- Draft model cards under `observatory/model_cards/cards/` are SPEC/DRAFT, not consumed by the SPA except the fixture gate JSON.
- Timebar “Soon” is “No forecast issued” unless oyster demo (`main.ts` L182–184).

**Impact**  
Strong honesty; near-zero delivery of the “now and future” estimator. This is correct scientifically and a large gap vs the stated goal.

**Recommended actions**  
- **FLESH OUT:** End-to-end publish pipeline (card → claim pack → globe paint) for one non-animal-GPS claim class first if needed, then one T3 species-region.  
- **DOCUMENT:** “Digital twin” language stays offline until H-4.4 readiness changes.  
- **REALIGN:** Never paint habitat/SST as current occurrence (already prohibited in `permitted_vs_prohibited_claims.md` L29–31).

---

### 3.5 Globe, map, visualization — score **58**

**What the plan requires**  
Google Earth–like pan/zoom/tilt; globe + 2D fallback; legend for likelihood / observed / inferred / forecast / uncertainty; forecast animation; depth visualization (`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` L222–259).

**What the code actually does**  
**Verified:** MapLibre **globe** projection (not Cesium); drag/zoom/tilt; flat mercator toggle; North-up reset; Willapa visual-truth patterns; OBIS past-report layer; sticky Measured/Guessed/Future/Don’t know legend. **Not** a 3D water column. **Not** species likelihood heatmaps.

**Positive alignment**

```108:118:globe/prototype/src/mapApp.ts
export type MapProjectionMode = "globe" | "mercator";
...
  setProjectionMode: (mode: MapProjectionMode) => void;
  resetNorth: () => void;
```

```641:659:globe/prototype/src/mapApp.ts
  const setProjectionMode = (mode: MapProjectionMode) => {
    projectionMode = mode;
    writeFlatPreference(mode === "mercator");
    map.setProjection({ type: mode });
    ...
  };
  const resetNorth = () => {
    map.easeTo({
      bearing: 0,
      pitch: projectionMode === "globe" && map.getZoom() < 3.5 ? WORLD_PITCH : map.getPitch(),
```

```253:294:globe/prototype/src/mapApp.ts
  map.addLayer({
    id: "cells-pattern-unknown",
    ...
    paint: { "fill-pattern": "hatch-unknown", "fill-opacity": 0.85 },
  });
  ...
  map.addLayer({
    id: "cells-pattern-forecast",
    ...
    paint: { "fill-pattern": "hatch-forecast", "fill-opacity": 0.4 },
  });
```

```5:13:globe/prototype/src/legend.ts
  const items = [
    { cls: "obs", text: "Measured" },
    { cls: "inf", text: "Guessed" },
    { cls: "fc", text: "Future" },
    { cls: "unk", text: "Don't know" },
  ];
  if (state.pastReportsVisible) {
    items.push({ cls: "past", text: "Past reports" });
  }
```

**Misalignment / missing**

- No species “more likely / less likely” legend items (prompt first-run legend).
- No forecast playback slider for distributions.
- Visual truth on Willapa encodes water T / ops stress, not animal presence (`audit/05` still correct on encoding risk; mitigated by dimming Willapa on non-oyster search — `mapApp.ts` L582–594).
- README still claims “2D map” (`globe/prototype/README.md` L4) while UI stamp says “3D globe” (`index.html` L123).

**Impact**  
Strongest shipped dimension: the globe interaction story is real. Biological visualization of **likelihood** is still missing by design until models publish.

**Recommended actions**  
- **FLESH OUT:** Time slider UI stub that remains disabled until `hasForecast`.  
- **REALIGN:** Legend entry for past reports vs measured-now (already partly done).  
- **DOCUMENT:** Align README with globe projection.

---

### 3.6 UX and plain language — score **70**

**What the plan requires**  
Answer hierarchy: where / certainty / depth / soon / why; four modes; Expert progressive disclosure; 30s yellowfin test (`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` L128–139, L304–353; `audit/09_redesign_spec.md` L1–18).

**What the code actually does**  
Implements the P0 redesign: Find Species home, answer strip fields, four nav buttons, Expert toggle, Learn oyster demo, cold load empty answer. `VERIFICATION.md` records yellowfin / Dungeness / cold-load checks.

**Positive alignment**

```4:14:globe/prototype/src/answer.ts
export function emptyAnswer(): AnswerStrip {
  return {
    species: "No species selected",
    whereNow: "Search a species or pick a place.",
    soon: "No forecast issued.",
    howSure: "None",
    depth: "Depth unknown",
    why: "Nothing has been asked yet.",
    thisIsNot: "Live tracking, a fishing map, or a count of animals.",
  };
}
```

```599:601:globe/prototype/src/main.ts
  setStrip(emptyAnswer());
  setNav("find");
  applyUi();
```

```7:10:globe/prototype/VERIFICATION.md
| Cold load 1440×900 | Empty answer: “Search a species or pick a place.” Four nav items. One-line banner. No Category D, AphiaID, or later-modes list. |
| Yellowfin tuna | Where now = no issued location; Soon = no forecast; How sure = None; Depth unknown. Then 246,964 past reports ... |
```

```164:168:globe/prototype/src/evidence.ts
  const fields = expert
    ? FIELD_TITLES.map(
        ({ key, title }) =>
          `<article><h3>${escapeHtml(title)}</h3>${renderValue(key, record.evidence)}</article>`,
```

(`FIELD_TITLES` lists all 16 provenance fields at `evidence.ts` L10–27.)

**Misalignment / missing**

- Explore Ocean (env animation, split comparisons) is largely Willapa controls, not global ocean exploration (`index.html` L60–117).
- Evidence mode is the same side panel; no scientific export filters (prompt Mode 3).
- Older audits (`audit/00_executive_summary.md`) describe pre-redesign UI — **superseded for UX facts** by code + `VERIFICATION.md`; honesty constraints therein remain valid.

**Impact**  
UX is now directionally aligned with §32 for the **honest no-data** product. It does not yet deliver the flagship “likely to be now” experience.

**Recommended actions**  
- **FLESH OUT:** Mode 2 env exploration with PUBLIC rasters + clear “not animals” chrome.  
- **REALIGN:** Keep oyster demo Learn-only (`main.ts` L413–434, L591–593) — already correct; do not regress cold load.  
- **DOCUMENT:** Mark `audit/00` as historical snapshot so agents do not re-assert “no search box.”

---

### 3.7 Active observation and data gaps — score **30**

**What the plan requires**  
Show data gaps; unknown ≠ absence; evidence of observations vs effort; observation planner (`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` L20–21, L192–199; `observatory/observation_planner/`).

**What the code actually does**  
Unknown/gap hatching; unknown-map toggle; past-report copy; quantity note that measured blue is water temperature not animals; fictional stations only in expert evidence mode. No live observation network or planner API. Gap **messaging** is strong; **active** observation (planner scoring, tasking, effort layers) is design-only (`observatory/observation_planner/README.md`: `DESIGN_ONLY`).

**Positive alignment**

```50:53:globe/prototype/index.html
      <p class="hint">
        The map stays striped until we have an estimate. Stripes mean we do not know — not empty
        ocean.
```

```62:66:globe/prototype/src/main.ts
function quantityNote(props: CellProperties): string | undefined {
  if (props.visualTruthState === "DIRECT_OBSERVATION" && props.habitatClass === "not_applicable") {
    return `Water temperature (measured): ${props.sstC} °C. This is not a sighting of animals.`;
  }
```

```140:146:globe/prototype/src/evidence.ts
  return `<p class="lede">${name}</p>
    <section class="answers" aria-label="Past reports">
      <p><strong>Past reports</strong> — ${escapeHtml(total)}. ${years}</p>
      <p>These cells are where people sampled and recorded this name. This is not where the animals are now.</p>
```

**Misalignment / missing**

- Stations are fixture/fictional (`globe/prototype/README.md` L62–63).
- Observation planner is markdown/CSV only (`observatory/observation_planner/README.md` etc.), not in SPA.
- No detection-effort layer on the OBIS grid (counts only).

**Impact**  
Gap messaging is honest and visible. “Active observation” as a system (sensors, planner, assimilation) is not running.

**Recommended actions**  
- **FLESH OUT:** Effort/coverage hatch for past-report grids.  
- **RE-SCOPE:** Treat observation planner as observatory R&D until partner sensors exist.  
- **REALIGN:** Keep SST/chlorophyll/AIS out of abundance encodings (no such paint in `src/` — verified by design of overlays + legend notes).

---

### 3.8 Data rights, FAIR/CARE, sensitive locations — score **55**

**What the plan requires**  
Documented rights; no precise sensitive locations; FAIR/CARE for Indigenous data; coarsening (`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` L27–28, L300; `observatory/sensitive_location_policy.md`; `observatory/data_rights_register.md`).

**What the code actually does**  
Implements coarsening/withhold for public past reports; license notes; publish-class fields in fixtures; strong policy docs. No FAIR repository or CARE consent workflow in software. Legal review still required (docs). Score credits **implemented** withhold/coarsen rails, not markdown volume.

**Positive alignment**

```3:9:globe/prototype/src/obis.ts
/** Taxa we never draw as a public past-report grid (listed / aggregation-sensitive). */
const WITHHOLD_APHIA = new Set<number>([
  105838, // Carcharodon carcharias — withhold native grain
]);

const MIN_CELL_N = 3;
const MAX_CELLS = 80;
```

```51:62:globe/prototype/src/obis.ts
  if (WITHHOLD_APHIA.has(aphiaId)) {
    const withheld: PastReportsResult = {
      collection: null,
      summary: {
        ...
        withheld: true,
        licenseNote: "Locations withheld. Listed or sensitive taxon.",
```

```19:21:observatory/data_rights_register.md
**Verdict**
**A global public species map is unsafe as observatory v1.** ...
```

```11:11:globe/sensitive_display_rules.md
**A global public map of saltwater life is unsafe as v1 and is rejected.**
```

**Misalignment / missing**

- CARE/FAIR are policy statements, not product features.
- Withhold list is a single AphiaID stub — not a full sensitive-taxa registry wired from observatory CSV.
- Commercial private lease data path is email-wedge, not globe (`wireframe_spec.md`).

**Impact**  
Concrete code rails (withhold, coarsen, disclaimers) plus policy docs reduce harm risk. FAIR/CARE remain pre-code commitments, so this is not a complete rights/ops system.

**Recommended actions**  
- **FLESH OUT:** Load withhold/coarsen rules from a versioned registry used by OBIS client.  
- **DOCUMENT:** Keep “not legal advice / human legal review required” visible.  
- **REMOVE/ARCHIVE:** Do **not** delete scientific honesty / rights docs when cleaning commercial drift.  
- **RE-SCOPE:** Public globe remains coverage + coarsened history + published estimates only.

---

## 4. Non-Goal Code and Scope Drift

| Area | Path / evidence | Relation to globe goal | Disposition |
|---|---|---|---|
| Commercial farm email/PDF/WhatsApp MVP | `artifacts/product_and_monetization/wireframe_spec.md` L3–5; `README.md` STATE_10 | Parallel monetization wedge; not the planetary globe | **RE-SCOPE** / keep; do not delete honesty docs |
| Willapa Category D OPS-RISK fixture | `evidence-by-cell.json` ~L1342–1347; Learn-gated in `main.ts` L591–593 | Useful honesty demo of non-GPS claims; can confuse “species location” | **DOCUMENT** + keep Learn-only |
| Observatory catalogs, EMIV, ensembles, KG, planners | `observatory/**` markdown/CSV; `data_catalog_notes.md` L7 ingest none | Spec library for a future twin — not running | **FLESH OUT** selectively into runtime; do not pretend live |
| Globe design markdown (4D volume, modes, tiles) | `globe/volume_4d_spec.md`, `globe_modes.md`, etc. | Ahead of code | **DOCUMENT** as design debt |
| Empty dirs / stubs | `ingestion_pipeline/`, `model_registry/`, `data_dictionary/`, empty `design/` | Placeholder | Ignore until filled |
| Historical UX audits | `audit/00_executive_summary.md` (pre-search UI) | Useful honesty; outdated UI inventory | **DOCUMENT** as superseded for UI facts |
| Dist bundles | `globe/prototype/dist/` | Build output | Not source of truth |

No recommendation to delete `observatory/sensitive_location_policy.md`, model-card claim packs, or scientific red-team materials.

---

## 5. Highest-Priority Realignment Recommendations (concrete steps)

1. **DOCUMENT** in root README + prototype README: “Runnable product = honest MapLibre prototype; planetary twin = specs only; zero published location models.”  
2. **DOCUMENT** that `audit/00`–`08` UX inventory is pre–2026-09-22 redesign; keep their honesty P0s.  
3. **REALIGN** docs that still say “2D only” with `mapApp.ts` globe default (`setProjection({ type: "globe" })`).  
4. **FLESH OUT** a single published-card path (even if first publish is still “no estimate” validation) so the gate is exercised for real.  
5. **FLESH OUT** effort-aware past-report visualization (coverage vs count) without implying now-presence.  
6. **FLESH OUT** withhold/coarsen registry (beyond Aphia 105838) shared by OBIS client and policy CSV.  
7. **FLESH OUT** Learn: one fish ecology + support-tier card from observatory CSV (read-only).  
8. **REALIGN** Explore mode toward PUBLIC ocean env layers labeled as covariates (`overlay-sst` pattern generalized).  
9. **RE-SCOPE** commercial email wedge as `artifacts/product_and_monetization/` product; stop cross-linking as if the globe is the paid SKU.  
10. **FLESH OUT** disabled time-slider + depth-slice UI that stays inert until `hasForecast` / depth data exist (prevents fake playback).  
11. **REALIGN** “digital twin” language in any user-facing string to physics/BGC priors only (`H-4.4`).  
12. **FLESH OUT** minimal backend only when fixtures + client-side OBIS/WoRMS rate limits become insufficient — not before.  
13. **DOCUMENT** FAIR/CARE as blocked on legal review; no Indigenous TEK layers.  
14. **REMOVE/ARCHIVE** (when cleanup is allowed) unused “later modes” copy if any residual remains in fixtures/meta user strings — not the scientific mode specs.  
15. **FLESH OUT** verification checklist into CI smoke (cold load, yellowfin no-publish, oyster Learn-only, withhold taxon).  
16. **RE-SCOPE** observation planner / ensembles / KG to “feed the first published card,” not parallel globe features.  
17. **REALIGN** any marketing of Google Earth flagship demo until likelihood+forecast for one species ships under a `PUBLISHED` card.  
18. **DOCUMENT** that OBIS past reports ≠ current location in every species answer (already in `speciesAnswer` / `renderPastReportsHtml` — preserve).

---

## 6. Methodology

1. Read master prompt (`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md`), prototype `README.md` + `VERIFICATION.md`, redesign/honesty audits (`audit/00`, `05`, `09`, `11`), and key observatory docs (support tiers, model claims, EMIV, data catalog notes, sensitive location / data rights, H-4.4, ecology profiles README, knowledge graph README).  
2. Scanned repo tree; identified live UI exclusively under `globe/prototype/src` + `index.html` + `public/fixtures`. Confirmed no Cesium dependency and no app backend.  
3. Read and line-cited: `main.ts`, `mapApp.ts`, `answer.ts`, `search.ts`, `worms.ts`, `obis.ts`, `evidence.ts`, `legend.ts`, `types.ts`, `model-cards.json`, `taxa.json` statuses, Category D fixture block, commercial `wireframe_spec.md`.  
4. Verified known facts against code (globe projection, answer strip, WoRMS/OBIS coarsening, Learn-only oyster demo, `NOT_PUBLISHED`, Expert 16 fields, cold load empty strip). Corrected outdated audit claims that the homepage still auto-opens Category D.  
5. `design/` was empty; competitor synthesis not used.  
6. Scored eight dimensions without inflating: UI/honesty high; planetary inference/twin low.  
7. **Changed no code, config, fixtures, CSS, HTML, or existing markdown** other than creating this file.

---

## Return packet (for parent agent)

**Report path:** `/Users/wijeratne/dev/fishai/audit/global-marine-life-alignment-report.md`

**Scores:** 3.1=38, 3.2=28, 3.3=22, 3.4=18, 3.5=58, 3.6=70, 3.7=30, 3.8=55

**Success answer:** The codebase is an honest MapLibre globe prototype (search, answer strip, past reports, Willapa working-conditions demo) plus a large observatory/commercial specification library — not a running planetary marine-life intelligence / digital-twin system. No published current estimates or forecasts exist. Code changes: none.
