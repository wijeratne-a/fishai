# User-flow audit

**Primary goal:** Where is [species] likely to be now or soon, how certain, what depth, why?  
**Clock:** 30 seconds for a normal person. Test species: **yellowfin tuna**.  
**App:** single page `globe/prototype/index.html`. No router.

Click counts assume a new user at `http://localhost:5173/` after load (C17 already selected). “Scroll” is counted when the target is below the fold (measured 1440×900).

---

## First-run (0–5 seconds) — FAIL

| Second | What the GUI actually says | What the user needed |
|---|---|---|
| 0 | Title: Willapa prototype (fixture). Banner: not a live fish map, OBIS, GBIF, AIS, GFW, WA DOH | “Search a species” |
| 1 | Left: **AOI** · H3-like cells · not a lease map | Place + species |
| 2 | **Globe mode** Mode 1 / 8 / 9 + seven later modes | One map, one job |
| 3 | Map of Willapa hexes labeled `WILLAPA-Cxx` | Where is the animal |
| 4 | Right: “Nahcotta-adjacent public water **(W1 OPS-RISK example cell)**” · badges WILLAPA-C17 / FORECAST / PUBLIC | Yellowfin / any species |
| 5 | Heading **W1 oyster OPS-RISK (Category D)** + ALL-CAPS flags | Plain: what is this estimate |

There is **no path** that starts with a species name. Boot path is `main.ts` → `meta.opsRiskExampleCellId` → oyster Category D.

Founder failure is this screen, not a missing tutorial.

---

## Yellowfin tuna 30s test (canonical)

**Procedure:** type or find “yellowfin tuna”; read now / soon / certainty / depth / why.

| Step | Action | Result | Clicks |
|---|---|---|---|
| 1 | Look for search | No `<input type="search">`. CDP: `searchExists: false`. `tunaMatches: []` on all 28 `<option>`s | ∞ — **blocked** |
| 2 | Cmd-F page for “yellowfin” | `hasYellowfin: false` on `document.body.innerText` | 0, fail |
| 3 | Pan/zoom map to ocean | `maxBounds` clamps to Willapa (`mapApp.ts`) | 0, fail |
| 4 | Switch Mode 8 / 9 | Still 27 Willapa cells | 1, fail |
| 5 | Read evidence | Pacific oyster AphiaID 836033 on C17 | 0, fail |

**Outcome: P0 FAIL.** Not “later.” The GUI cannot perform the product’s stated 30s job.

Honest pass (not implemented): 1 click/focus in search + type “yellowfin tuna” + Enter → no-data species panel (confidence None, no heatmap). That would be **2 interactions**, ~15s.

---

## Core flows A–I (click counts)

Flows are scored against the **primary species goal**. Where the app only supports the oyster fixture, that is called out.

### A. Name / find a species

| | |
|---|---|
| **Needed** | Search or browse “yellowfin tuna” |
| **Actual** | No search. Jump list is cell IDs + enums, **below the fold** (rail y≈958) |
| **Clicks** | Impossible (0 path). If user means “find C17”: 1 scroll + 1 select = **2**, still not a species |
| **P0** | Yes |

### B. Where is it **now**

| | |
|---|---|
| **Needed** | A place in space for that species, labeled now vs not-now |
| **Actual** | C17 field 1 (below honesty, itself below fold): “No current biological estimate. Planted oysters are not being counted…” DIRECT_OBSERVATION cells (C01) show **15.7 °C water**, “not a fish count” |
| **Clicks from boot** | C17 “now” is not in the first screen. Scroll evidence **~1200px** past OPS-RISK to field 1, or never find it. **0 clicks + long scroll**, still not yellowfin |
| **P0** | Yes |

### C. Where **soon** (forecast)

| | |
|---|---|
| **Needed** | A future window for the species |
| **Actual** | Timebar “Valid for” 72h is **AOI fixture clock**, not a species forecast. C17 forecast is **ops-stress tercile**, “Not a probability. Not % dead.” Dashed hex encoding = FORECAST of **working conditions**, not animal movement |
| **Clicks** | 0 to see clocks (footer always on) but clocks are unreadable ISO soup; 1 scroll to field 2 |
| **P0** | Yes for species; P1 even for oyster (soon ≠ location) |

### D. How certain

| | |
|---|---|
| **Needed** | High / Medium / Low / None in human words, on the answer strip |
| **Actual** | Footer: `low (category, not a %)`. C17 panel: “Category: **LOW**” in field 3 with `FRESH:ok`, `DENSITY:low`, `LABEL_SUPPORT:none`, `CALIBRATION_OK:low`. C05: confidence **none** (good honesty, hidden behind jump list) |
| **Clicks** | 0 to see “low” in footer if the user knows “forecast confidence” ≠ “I am sure fish are here.” To see reasons: scroll past OPS-RISK + honesty (~1600px) |
| **P0** | Comprehension P0: “low (category, not a %)” is not a sentence a person can use |

### E. What depth

| | |
|---|---|
| **Needed** | Depth of the animal / estimate |
| **Actual** | Radios: Surface (water skin) / Intertidal / emersion / 0–10 m / Unknown depth. Default **surface**. Disclaimer: “not a water column of animals.” Intertidal copy is **oyster air vs water**, “not a 50-layer z-grid” (`main.ts`) |
| **Clicks** | 1 to change band. Selecting Unknown depth updates disclaimer. **Does not answer “what depth is yellowfin.”** C17 has `depth0to10: false` — 0–10 m hatches the cell as depth-missing, easy to read as “no oysters” despite copy |
| **P0** | Control exists but is the wrong question (farm emersion stub) |

### F. Why (drivers / evidence)

| | |
|---|---|
| **Needed** | One sentence above the fold |
| **Actual** | Spec (`evidence_explorer.md`) requires why/trust/missing/class **above the fold**. Live C17: `.answers` top **1372px**, panel bottom **800px**. Why text: “A fixture rule flagged forecast air overlapping daytime emersion plus wind/wave workability.” |
| **Clicks** | **1 long scroll** (no click). On C05 (UNKNOWN), answers **are** near the top — but reaching C05 is 1 scroll + 1 select because Jump is below the fold |
| **P0** | Default cell violates the spec the panel was built for |

### G. Observed vs inferred vs forecast vs unknown

| | |
|---|---|
| **Needed** | Readable from the map without a seminar |
| **Actual** | Encoding is in `mapApp.ts` (solid/dotted/dashed/hatch) and `legend.ts`. Legend **below fold**. Map labels are `WILLAPA-C17` not “Forecast.” Badge on panel says `FORECAST` (enum). Honesty sentence below fold on C17. Unknown vs DATA_GAP vs RESTRICTED are three hatches with expert captions |
| **Clicks** | 0 if user already knows the visual language; else 1 rail-scroll to legend **plus** decoding “DIRECT_OBSERVATION” in the dropdown |
| **P0** | Encoding exists; **legibility** fails |

### H. Limits / do-not-use

| | |
|---|---|
| **Needed** | Short, sticky, understood |
| **Actual** | Banner (64px, 34 words, acronyms). Map stamp. C17 repeats NOT food-safety etc. in flags + headline + field 12. Commercial “does-not-mean” strip from `user_output_contract_visual.md` is **not** a compact map overlay; it is buried in the ops essay |
| **Clicks** | 0 — limits are the loudest thing on screen, and still not understood (founder) |
| **P0** | Volume ≠ comprehension |

### I. No data / low confidence

| | |
|---|---|
| **Needed** | Searching a species with no model → clear empty state |
| **Actual** | C05/C06 etc. are good **cell-level** UNKNOWN/DATA_GAP copy (“not zero animals”). There is **no species-level** empty state. Timebar still shows a 72h forecast clock even on UNKNOWN cells (`time_and_forecast_ui.md` says n/a if no forecast — **not implemented**; footer always filled from AOI meta) |
| **Clicks to C05** | Scroll rail + select = **2**. Map click unreliable (VERIFICATION.md) |
| **P0** | Cell empty states exist; **product** empty state for yellowfin does not |

---

## Secondary flows (what the GUI *can* do)

| Flow | Steps | Clicks | Notes |
|---|---|---|---|
| Open oyster OPS-RISK demo | Load app | **0** | Forced. Wrong default |
| Open another cell via list | Scroll rail, open select, pick `WILLAPA-C01 · DIRECT_OBSERVATION` | **2 + scroll** | Options are enums |
| Open cell via map | Click hex | **1** (often 0 effect) | Cooperative gestures overlay; hit-test misses |
| Toggle unknown map | Check “Show ignorance as the feature” | **1** | Phrase is not “show where we have no data” |
| Mode 9 | Click Mode 9 radio | **1** | Forces unknown map; adds `n=` labels |
| Mode 8 | Click Mode 8 | **1** | Fills more transparent; shows fictional stations; no extra provenance UI beyond the same panel |
| SST overlay | Scroll to Layer stubs, check SST | **1 + scroll** | Circles of °C; suppressed if unknown map on |
| Copy JSON | Scroll evidence to button (below answers) | **1 + long scroll** | Expert |
| Depth band | Click Intertidal | **1** | Oyster-specific disclaimer |
| Leave Willapa / search tuna | — | **Impossible** | |

Commercial email/PDF flows in `artifacts/product_and_monetization/wireframe_spec.md` (**open email, read Elevated, tap WDOH, log 30s outcome**) are **not implemented** in this GUI.

---

## Flow scoreboard

| Flow | Possible? | Clicks to success | 30s? |
|---|---|---|---|
| A Find species | No | — | No |
| B Where now | No (species); oyster “now” = no biological estimate | Scroll | No |
| C Soon | No (species); oyster soon = work-stress rank | 0–1 | No |
| D Certainty | Partial, jargon | 0 + decode | No |
| E Depth | Wrong depth model | 1 | No |
| F Why | Buried on default cell | Scroll | No |
| G Observed vs forecast | Encoded, unexplained | Scroll to legend | No |
| H Limits | Present, unreadably stacked | 0 | No |
| I No-data species | No | — | No |

**Net:** the app has a scientist’s **cell inspector**. It does not have a user’s **species journey**.
