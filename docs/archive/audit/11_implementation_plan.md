# Implementation plan (do not implement in this audit)

Work **P0 first**, then **P1**, then **only P2 that help comprehension**. P3 is leftover hygiene. Do not add Cesium, food-web, or a tuna heatmap to “look done.”

**Done means:** yellowfin 30s test **passes honestly** (no-data strip + hatch + limits). Founder can read the GUI aloud.

---

## Phase 0 — stop the wrong default (P0-02, P0-03, P0-12)

**Effort:** S  
**Files:** `globe/prototype/index.html`, `src/main.ts`, `public/fixtures/meta.json` (stop using `opsRiskExampleCellId` as boot selection; do not delete the fixture).

1. Remove `showCell(opsId)` on load. Empty evidence = “Search a species or pick a place.”  
2. Delete **Later modes** list from the rail.  
3. Hide Mode 8 / Mode 9 as peer radios; keep their paint as Explore toggles later.  
4. Page title + banner mark: honest demo or Find Species, not “Ocean Life Globe” as a tracker.

**Accept:** Cold load is not C17 Category D. No Food-web list.

---

## Phase 1 — language and fold (P0-04, P0-05, P0-06, P0-07, P0-08, P0-11)

**Effort:** M  
**Files:** `index.html`, `legend.ts`, `evidence.ts`, `main.ts` `formatClock`/`fillTimebar`, `styles.css`.

1. Apply `04_language_and_jargon_audit.csv` to **main-screen** strings (not every JSON limitation bullet yet).  
2. Answer strip component: Now / Soon / Sure / Depth / Why / Not — **above** any OPS essay.  
3. Move OPS-RISK + 16 fields + JSON behind `Expert` (default off).  
4. Sticky 4-item legend on `.map-wrap`.  
5. Jump-to-place **above** depth; options use geojson `label` + plain truth word (`P1-01` can ride along).  
6. Timebar → one local as-of + horizon or “No forecast issued”; if selected state is UNKNOWN, do not show an issued animal forecast (`time_and_forecast_ui.md` n/a).  
7. Hide `cell-ids` by default.

**Accept:** At 1440×900, why + measured-vs-future visible without scroll. Legend visible. Footer readable. Expert still has 16 fields.

---

## Phase 2 — Find Species + yellowfin no-data (P0-01, P0-09, P0-10)

**Effort:** M  
**Files:** new search UI in `index.html` + small `src/search.ts` (client-only). Fixture: a `taxa.json` with `{ id, name, status: "no_estimate" | "oyster_demo" }`.

1. Home control: search. Synonyms: yellowfin, Thunnus albacares → `no_estimate`.  
2. No-data panel + map hatch (world or “this map is Willapa oysters, not tuna”).  
3. Depth on that panel: **unknown**, not Surface (water skin).  
4. Pacific oyster query can deep-link Learn demo (not required for yellowfin pass).  
5. Do **not** add occupancy/SST-as-tuna layers.

**Accept:** Type yellowfin tuna → 30s: no location, no forecast, sure none, depth unknown, why in one sentence, not-tracking limits, **no smooth fill**.

This is the **product** P0. Phases 0–1 make the oyster fixture human; Phase 2 makes the **stated** goal true.

---

## Phase 3 — Explore IA + depth copy (P0-09 remainder, P0-12 remainder)

**Effort:** M  
**Files:** `index.html` rail, `mapApp.ts` filters unchanged scientifically.

1. Four nav items (can be in-page tabs; still no router required).  
2. Unknown: “Highlight where we have no estimate.”  
3. Depth labels per CSV; oyster emersion sentence only when oyster demo active.  
4. Overlay group collapsed; SST caption stays.

**Accept:** ≤4 nav. No numbered Mode 8 on home.

---

## Phase 4 — P1 comprehension only

Do these; skip P1 that is polish without reading gain if timeboxed.

| ID | Do? | Why |
|---|---|---|
| P1-01 place names in select | Yes | Rides on P0-07 |
| P1-03 quantity chip on measured temp cells | Yes | Stops blue=fish |
| P1-04 one last-obs clock | Yes | Trust |
| P1-05 habitat not green-as-safe | Yes | Spec + reading |
| P1-09 shorten banner | Yes | First 5s |
| P1-11 Learn page (one screen) | Yes | Observed vs guessed vs unknown ≠ empty; this demo vs tuna |
| P1-12 commercial is email/PDF | Yes | One paragraph in Learn |
| P1-02 SST/unknown coupling copy | Yes | Short tooltip |
| P1-06 hide compass | Yes | XS |
| P1-07 JSON expert-only | Yes | Already Phase 1 |
| P1-08 mobile stack | Yes if any phone demo; else after |
| P1-10 station captions | With Mode-8-as-toggle |

**Accept:** C01 cannot be described as “saw fish.” Learn explains hatch.

---

## Phase 5 — P2 that help comprehension only

| ID | Do? |
|---|---|
| P2-01 skip to search/answer | Yes |
| P2-02 h1 | Yes |
| P2-04 plain live region | Yes |
| P2-06 timebar type size | Yes (with P0-08) |
| P2-07 n= caption or hide | Yes |
| P2-08 later modes already gone | — |
| P2-12 legend ≤5 | Yes (4-item default) |
| P2-03 map role=application | Yes if cheap |
| P2-05 focus ring | Yes XS |
| P2-09 grayscale theme | **No** this round |
| P2-10 CSV export | **No** this round (Expert JSON enough) |
| P2-11 target blank | Optional XS |

**Skip P3** unless touching CSS anyway (`scrollHeight`, glyphs).

---

## What not to build

- Cesium / Mode 2 volume / Mode 6 swimming playback  
- Global yellowfin occupancy from SST/chl/AIS  
- Ten-mode globe arcade  
- EMIV catalog on Find Species  
- Auto-select C17 as “showcase”  
- More disclaimer paragraphs instead of one composed answer  

---

## Suggested order of files (when someone implements)

1. `index.html` structure (nav, search, answer strip, legend on map)  
2. `main.ts` boot + clocks + no auto C17  
3. `evidence.ts` default vs expert render  
4. `legend.ts` 4 items  
5. `mapApp.ts` hide cell-ids; compass off; keep encodings  
6. `styles.css` fold, 16px, mobile order  
7. `public/fixtures/taxa.json` yellowfin no_estimate  

Fixtures for cells **stay**; they become the oyster Learn/Explore dataset.

---

## Test plan (human)

1. Cold load: no Category D.  
2. 30s yellowfin: no-data, none, unknown depth, why, limits, no heatmap.  
3. Expert on: 16 fields + C17 still exist.  
4. C05: don’t know ≠ empty.  
5. C01: measured **temperature**.  
6. Keyboard: search, then place list.  
7. 390px width: search/answer/map before mode essays.

---

## Mapping to P0 count

**12 P0 issues** in `08_prioritized_issues.csv`. Phases 0–3 close all 12. Yellowfin 30s flips to **PASS (honest no-data)** at end of Phase 2; Phases 0–1 are required so the rest of the GUI is speakable.
