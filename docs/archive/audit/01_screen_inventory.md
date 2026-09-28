# Screen inventory — actual GUI (not the intended observatory)

**Inspected:** 2026-09-19, `http://localhost:5173/`, viewport 1440×900.  
**Source of truth:** `globe/prototype/index.html`, `src/*.ts`, `src/styles.css`, `public/fixtures/*`.  
**Other HTML/React/UI in repo:** none (only `globe/prototype/index.html` + its `dist/` build). No routes, no species pages, no login, no settings.

---

## 1. Application identity

| Surface | What ships |
|---|---|
| Document title | `FishAI Ocean Life Globe — Willapa prototype (fixture)` — `index.html` `<title>` |
| Meta description | “FishAI Ocean Life Globe prototype for Willapa Bay. Fixture data only. Not a live fish map.” |
| Visible product mark | `FishAI · Ocean Life Globe` — `.banner__mark` |
| Boot selection | `WILLAPA-C17` because `meta.json` `opsRiskExampleCellId` and `main.ts` `showCell(opsId)` |
| Geography lock | MapLibre `center [-123.97, 46.54]`, `maxBounds` Willapa only — `mapApp.ts` |
| Species on screen | Pacific oyster only, and only after reading C17 ops block (`evidence-by-cell.json` `opsRisk.species`) |
| Yellowfin / any other taxon | **Absent** from UI, fixtures, and options |

---

## 2. Chrome regions (single layout, no pages)

Desktop CSS: `body` grid = banner / `.shell` (3 columns) / `.timebar` (`styles.css`).

| Region | DOM | Default visible job | User-goal job |
|---|---|---|---|
| Skip link | `a.skip` → `#evidence` | Keyboard skip | Does not skip to search (there is none) |
| Banner | `header.banner` | Legal/scientific disclaimer | Occupies first 64px with acronyms, not a goal statement |
| Left rail | `aside.rail` | Controls + (below fold) jump list + legend | No species search; modes 2–7/10 as dead lists |
| Map | `#map` `role="application"` | 27 hex cells, land fill, dashed water outline, cell-id labels | Looks like “where things are” but cells are truth-states for oyster/env fixtures |
| Map stamp | `.map-stamp` | `FIXTURE · NOT FOR NAVIGATION · NOT A LIVE ANIMAL MAP` | Correct honesty; competes with hex IDs |
| MapLibre chrome | zoom, compass rotate, scale, attribution, cooperative-gesture hint | “Use ⌘ + scroll to zoom the map” | Extra chrome, rotate control on a 2D bay map |
| Evidence | `aside#evidence` | 16-field explorer; C17 OPS-RISK first | Not a species detail page |
| Timebar | `footer.timebar` 7 columns | Issued / valid / inputs / last obs / confidence / model / coverage | ISO+PDT doubled clocks; not a “soon” slider |
| Live status | `#map-status.sr-live` | Clipped visually; `aria-live="polite"` | Screen-reader only |

**Mobile (`max-width: 1100px`):** stack rail → 50vh map → evidence; timebar 2 columns. No drawer, no search, no sticky answer strip. Not a phone product.

---

## 3. Left rail sections (in DOM order)

Measured fold on 1440×900: rail viewport **64–800px**. `rail.scrollHeight = 1267`.

| # | Heading | Controls | Above fold? |
|---|---|---|---|
| 1 | **AOI** | Static paragraph: Willapa, H3-like ~20 km², not shoreline, not lease | Yes (76–182) |
| 2 | **Globe mode** | Radios Mode 1 / 8 / 9; list “Later modes (not in prototype)” 2–7, 10 | Yes (197–448) — **252px of mode taxonomy** |
| 3 | **Unknown map** | Checkbox “Show ignorance as the feature” | Yes |
| 4 | **Depth (stub)** | Surface / Intertidal / emersion / 0–10 m / Unknown depth + disclaimer | Yes but dense |
| 5 | **Layer stubs** | SST / Habitat class / Observation density | **Clipped** (starts 784) |
| 6 | **Jump to cell** | `<select id="cell-select">` 28 options | **No** (top 958) |
| 7 | **Legend** | 7 truth-state swatches + hints | **No** (top 1034, h 278) |

Mode 9 auto-checks Unknown map (`main.ts`). Stations layer visible only in Mode 8 (`mapApp.ts` `stations` visibility).

---

## 4. Map layers (always-on unless noted)

From `mapApp.ts`:

| Layer id | What it shows | Visible default |
|---|---|---|
| `background` | `#8aa3a8` | Yes |
| `land-fill` | Approximate land `#d7cbb3` | Yes |
| `water-outline` | Dashed bay outline | Yes |
| `cells-fill` | Truth-state fill + opacity | Yes (filtered by depth flags) |
| `cells-pattern-*` | Hatch/stipple per UNKNOWN, DATA_GAP, RESTRICTED, HABITAT, INFERENCE, FORECAST | Yes |
| `cells-depth-missing` | Hatch when cell lacks selected depth band | On depth mismatch |
| `cells-line` / `-forecast` / `-inference` | Solid / dashed / dotted outlines | Yes |
| `cells-sst` | Color circles of `sstC` | Off until overlay |
| `cells-habitat-dots` | Green dots reduced/typical/elevated | Off until overlay |
| `cells-density` | Text `n=` + `observationN` | Off unless density overlay or Mode 9 |
| `stations` | Fictional in-water sensors | Mode 8 only |
| `cell-ids` | `WILLAPA-C01` … `C27` labels | **Always** |

Click targets: fill + pattern layers. VERIFICATION.md: canvas clicks easy to miss; jump list is the reliable path — and that list is below the fold.

---

## 5. Evidence panel states

### Empty (only if boot did not select C17)

Copy in `index.html`:

> Click a cell, or choose one in the list. Every cell has exactly one visual-truth state and the 16 provenance fields.

No prompt to search a species.

### Selected cell (all 27 cells)

`evidence.ts` `renderEvidenceHtml`:

1. Place `label` (geojson), e.g. “Nahcotta-adjacent public water (W1 OPS-RISK example cell)”
2. Badges: `cellId`, `visualTruthState` (enum), `publishClass`
3. **If C17:** full OPS-RISK block (`renderOps`) — 1181px tall on first-run
4. Honesty questions (why / trust / missing / observed-inferred-forecast)
5. Button **Copy cell JSON**
6. Articles **1–16** (`FIELD_TITLES`)

C17 evidence `scrollHeight = 3802` vs visible `736`. Honesty block **not in view** on default cell.

### C17 OPS-RISK block (unique screen)

Heading: `W1 oyster OPS-RISK (Category D)`  
Flags: NOT food-safety · NOT harvest authorization · Verify WA DOH · Air × tide — not SST = body temperature  
Status: `ELEVATED (fixture tercile, not a calibrated probability)`  
~220-word headline (WAC, Vp, FDA, tissue toxin…)  
Species line with **AphiaID 836033**  
Target: Category D 72h operational disruption…  
Options A–D + “Never 'harvest now'”  
Links: WA DOH viewers, NOAA CO-OPS Toke Point analog

This is a **farm working-conditions brief** stuffed into a map side panel. It is not a species-location card.

---

## 6. Cell catalog (the only “places” in the app)

Source: `public/fixtures/willapa-cells.geojson` + `evidence-by-cell.json`. Counts from `meta.json`.

| Truth state | n | Example cell | Label (plain geography) |
|---|---|---|---|
| DIRECT_OBSERVATION | 3 | C01, C02, C13 | Northern entrance / Eastern channel — **water temperature, not animals** |
| FORECAST | 6 | C03, C09, C15, **C17**, C19, C25 | Env/workability forecast; C17 = OPS-RISK |
| MODEL_INFERENCE | 4 | C08, C14, C18, C24 | “Rules are not animals” |
| HABITAT_SUITABILITY | 4 | C04, C10, C20, C26 | Habitat class reduced/typical — **not presence** |
| UNKNOWN | 3 | C05, C12, C21 | Insufficient evidence |
| DATA_GAP | 5 | C06, C11, C16, C22, C27 | No fixture this cell×window |
| RESTRICTED_OR_COARSENED | 2 | C07, C23 | Privacy withhold |

Dropdown text is **not** the place name. It is `WILLAPA-C17 · FORECAST · W1 OPS-RISK` (`main.ts`).

---

## 7. Timebar fields (always on)

Filled by `main.ts` `fillTimebar` from `meta.json` `timeReadout`:

| Label | Fixture value (as displayed) |
|---|---|
| Forecast issued at | `2026-09-18T23:00:00Z · Sep 18, 2026, 16:00 PDT` |
| Valid for | same ISO+PDT range → +72h |
| Inputs current through | `2026-09-18T21:00:00Z · … 14:00 PDT` |
| Last direct observation | `2026-09-18T16:10:00Z · … 09:10 PDT` (AOI-level, not the selected cell) |
| Forecast confidence | `low (category, not a %)` |
| Model version | `GLOBE-PROTO-FIXTURE-2026-09-18-v0` |
| Data coverage | `27 coarsened cells; 5 DATA_GAP; 3 UNKNOWN; 0 live ingest` |

No playback, no “now vs +24h” control (`time_and_forecast_ui.md` MVP: static clocks). Footer is 100px of expert metadata.

---

## 8. Screens that do not exist (but the product name implies)

| Expected for “Ocean Life Globe” / 30s species goal | Status |
|---|---|
| Home / search | Missing |
| Species results | Missing |
| Species detail (yellowfin) | Missing |
| Global or basin map | Missing (Willapa `maxBounds`) |
| Forecast timeline for a species | Missing |
| Learn / glossary | Missing (jargon is inline) |
| Expert vs simple mode | Missing (everything is expert) |
| Account, alerts, email brief UI | Out of this prototype; commercial is email/PDF spec only |
| Routes `/`, `/species/:id`, `/map`, `/learn` | **No router** |

---

## 9. Spec screens vs implemented screens

| Spec | File | In prototype? |
|---|---|---|
| Globe chrome MVP | `globe/wireframes.md` §1 | Partial: 3-pane + timebar + banner |
| Evidence 16 fields | `evidence_explorer.md` | Yes, all 16 |
| Unknown map | `unknown_map.md` | Toggle + Mode 9 |
| W1 ops-stress view | `wireframes.md` §4 | C17 block only, not a dedicated view |
| Commercial email/PDF | `artifacts/product_and_monetization/wireframe_spec.md` | **Not this app** |
| Species picker | explicitly later / out of scope | **Not built** |
