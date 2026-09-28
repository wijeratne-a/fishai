# FishAI / Global Saltwater Life Observatory — UX audit executive summary

**Auditor:** Human-centered product and UX (read-only).  
**Date:** 2026-09-19  
**Runnable GUI inspected:** `http://localhost:5173/` (`globe/prototype/`, Vite + MapLibre 2D).  
**Product code modified:** none. This folder is the only write target.

---

## Verdict

| Test | Result |
|---|---|
| Yellowfin tuna 30-second test | **FAIL** (P0, not a footnote) |
| First 5 seconds of the actual GUI | **FAIL** the primary user goal |
| Founder: “not human usable… cannot understand anything the GUI is saying” | **Confirmed on the live screen** |
| Scientific honesty of encodings (fixture, not harvest, unknown ≠ empty) | Careful **and** unreadable — still a product failure |

**P0 count: 12** (see `08_prioritized_issues.csv`).  
**Yellowfin 30s test: FAIL.**  
**This file:** `audit/00_executive_summary.md`.

---

## What the GUI actually is

The only runnable UI in the repo is **one page with no routes**: a Willapa Bay hex-cell MapLibre demo of **visual-truth states** for **Pacific oyster OPS-RISK (Category D)**.

It is **not** a species-search product. It cannot name, find, or forecast yellowfin tuna. There is no search box, no species list, no ocean-scale map, no “where is this animal.” The combobox options are `WILLAPA-C01` … `WILLAPA-C27` labeled `DIRECT_OBSERVATION` / `FORECAST` / `W1 OPS-RISK`. Zero matches for tuna / yellowfin / Thunnus (`index.html`, `main.ts` cell list, `public/fixtures/*`).

This is specified, not accidental:

- `globe/globe_modes.md` § MODE 1: “Species search, taxon group, life-stage, climate comparison = **disabled, labeled later**.”
- `globe/wireframes.md` §6: “Global multi-taxon arcade / Species picker” out of scope. “If a designer asks where the pretty fish go: **they don’t.**”
- `artifacts/product_and_monetization/wireframe_spec.md`: commercial MVP is **email + PDF + WhatsApp**, “No GIS app.” Species picker explicitly out of scope.
- Repo-wide HTML/React/UI search: **only** `globe/prototype/index.html`.

The current chrome **opens** on `WILLAPA-C17` (`meta.json` `opsRiskExampleCellId`, `main.ts` boot `showCell(opsId)`). The right panel’s first heading is **“W1 oyster OPS-RISK (Category D)”** with AphiaID 836033, WAC 246-282-006, “fixture tercile,” “emersion,” “NOT SST = BODY TEMPERATURE.” That is the first-run product.

---

## Primary user goal (30 seconds)

> Where is **[species]** likely to be **now or soon**, **how certain**, **what depth**, **why**?

**First 5 seconds on the live GUI (1440×900, measured):**

1. Dark banner: “Not a live fish map” + OBIS/GBIF/AIS/GFW/WA DOH (34 words of **what this is not**).
2. Left rail starts at **AOI**, **Globe mode** (Mode 1 / 8 / 9), seven **later modes that do not exist**, **Show ignorance as the feature**, **Depth (stub)**.
3. Center: Willapa hexes stamped `WILLAPA-Cxx`, overlay **FIXTURE · NOT FOR NAVIGATION · NOT A LIVE ANIMAL MAP**.
4. Right: **Evidence explorer** auto-filled with the oyster OPS-RISK wall. The four honesty questions (`evidence.ts` `renderAnswers`) sit at **y ≈ 1372px**; the visible panel ends at **y = 800**. User never sees why / trust / observed-vs-forecast without scrolling past a **1181px** ops block.
5. Footer timebar: `2026-09-18T23:00:00Z · Sep 18, 2026, 16:00 PDT` × four clocks, plus `GLOBE-PROTO-FIXTURE-2026-09-18-v0` and `5 DATA_GAP; 3 UNKNOWN; 0 live ingest`.
6. **Legend is below the left-rail fold** (legend top ≈ 1034px; rail visible to 800). **Jump to cell** (the reliable keyboard path) is also below the fold.

A normal person cannot search yellowfin. They cannot tell what animal the map is about unless they decode “W1 OPS-RISK” and *Magallana gigas*. They cannot answer now / soon / certainty / depth / why in 30s.

**Current answer to the success criterion: no.**

---

## What must change (P0 path to “yes” without a fake tuna heatmap)

Do **not** paint a live-looking yellowfin density field. Honesty that ships a heatmap of nothing is worse than a blank search.

P0 work that makes the 30s test **pass honestly**:

1. **Home = Find Species.** A search field is the first control. Placeholder: “Search a saltwater species (e.g. yellowfin tuna).”
2. **Yellowfin (and any taxon not in this build) returns a first-class no-data page in <30s**, not a Willapa oyster cell:
   - **Where now:** no issued location. Map = world or basin hatch, or “this demo geography is Willapa Bay, Washington — oysters, not tuna.”
   - **Soon:** no forecast issued.
   - **Certainty:** None.
   - **Depth:** unknown / not estimated.
   - **Why:** we have no yellowfin observations or evaluated model in this product.
   - **Limits:** not tracking; not a fishing map; not abundance.
3. **Plain-language chrome.** Replace AOI / Mode 8 / OPS-RISK / Category D / WILLAPA-C17 / EMIV / H3 on the main screen. Default nav ≤4: **Find Species / Explore Globe / Evidence / Learn**. Expert Mode holds the 16-field panel, Category D, model IDs.
4. **Default map stays 2D MapLibre** (already true; do not add Cesium for v1).
5. **Above-the-fold answer strip** on every species or cell: Now | Soon | Confidence | Depth | Why this (one sentence) | What this is not.
6. **Stop auto-opening C17 OPS-RISK** as the welcome state. If oyster working-conditions remains a demo, it is a labeled **Learn / Expert** example, not the homepage.

That is a successful yellowfin 30s: the user **understands there is no yellowfin product yet**, and why, without being shown a fake school of fish.

---

## Honesty is real — and still failing as UX

The prototype is careful where it counts scientifically:

- Persistent “not a live fish map / not harvest / not food-safety.”
- One visual-truth state per cell; hatch for unknown/gap; dashed forecast; dotted inference (`visual_truth_states.md`, `mapApp.ts`, `legend.ts`).
- UNKNOWN ≠ zero animals (`unknown_map.md`, C05 copy).
- No red “life” heatmap; Okabe–Ito + pattern.
- Fixture timestamps; no OBIS/AIS ingest.

**That does not make it usable.** Honesty copy is so dense that a non-scientist cannot extract observed vs inferred vs forecast. The default C17 headline is a single paragraph that names Category D, Tier 3, WAC, Vp, SST, tissue toxin, tribal/FDA, and “fixture tercile” before the user sees “FORECAST” in the honesty block — which is **below the fold**. Honesty nobody can read is a product failure.

---

## Commercial vs this globe

Commercial wireframes (`artifacts/product_and_monetization/wireframe_spec.md`) are **email / 1-page PDF / WhatsApp** for oyster **farm working conditions**, not this GUI. Do not treat the globe as the paid SKU. Do not pretend this MapLibre page is the yellowfin observatory either. Today it is an **internal visual-truth fixture** that was shipped with the product name “Ocean Life Globe.”

---

## Audit index

| File | Contents |
|---|---|
| `01_screen_inventory.md` | Every actual surface, control, route (none), fixture cell |
| `02_user_flow_audit.md` | First-run + flows A–I with click counts |
| `03_information_architecture_audit.md` | IA vs 30s goal |
| `04_language_and_jargon_audit.csv` | Every visible string class + replacements |
| `05_map_globe_scientific_honesty_audit.md` | Map encodings + honesty vs comprehension |
| `06_accessibility_audit.md` | A11y against the live DOM |
| `07_performance_cognitive_load_audit.md` | Words, folds, overlay stack |
| `08_prioritized_issues.csv` | P0–P3 backlog |
| `09_redesign_spec.md` | Home, species, map, evidence, empty, expert, tokens |
| `10_before_after_wireframes.md` | ASCII before/after |
| `11_implementation_plan.md` | P0 then P1 then comprehension-only P2 — **do not implement here** |
