# Map / globe / scientific-honesty audit

**Map stack:** MapLibre GL JS 6.10.0, 2D, no Cesium (`package.json`, `mapApp.ts`). **Keep 2D as default.**  
**Data:** synthetic fixtures `public/fixtures/*.geojson` generated 2026-09-18. No live ocean ingest.

---

## 1. What the map actually encodes

Each hex has **exactly one** `visualTruthState` (`types.ts`, `visual_truth_states.md`). Fills, opacities, and patterns in `mapApp.ts`:

| State | Color (Okabe–Ito-ish) | Texture | Outline | Honest meaning in *this* fixture |
|---|---|---|---|---|
| DIRECT_OBSERVATION | `#0072B2` ~84% | Solid | Solid | **Water temperature at a fictional sensor**, not an animal |
| MODEL_INFERENCE | `#E69F00` ~36% + stipple | Dotted line | Env/workability **rule**, “not occupancy” |
| FORECAST | `#56B4E9` ~30% + dash hatch | Dashed | Future **workability / env**, including C17 OPS-RISK |
| HABITAT_SUITABILITY | `#009E73` + dots | — | Habitat class, **not presence** |
| UNKNOWN | grey + diagonal hatch | — | Belief emptiness |
| DATA_GAP | darker hatch cross | — | Sampling emptiness |
| RESTRICTED_OR_COARSENED | `#CC79A7` + dots | — | Privacy withhold |

This is **not** a yellowfin distribution. It is not even an oyster count. C01’s “observation” is 15.7 °C water (`evidence-by-cell.json`). Painting that as a solid blue hex **looks like** “we saw life here.”

**Honesty of the encoding system:** high.  
**Honesty of the first impression:** low. Blue solid + product name “Ocean Life Globe” = fish-are-here, unless the user has read `visual_truth_states.md`.

---

## 2. Observed vs inferred vs forecast — can a non-scientist tell?

**From the map alone, first 5 seconds: no.**

Reasons, tied to files:

1. **Legend is below the fold** (`#legend` top ≈ 1034px; rail clip 800px). The sentence that teaches solid/dotted/dashed lives in `legend.ts` where users do not look.
2. **Map labels are `WILLAPA-C17`**, not “Forecast” (`cell-ids` layer, `text-field: cellId`).
3. **Seven states** plus unknown-map recolor plus optional SST/habitat/`n=` overlays. Spec forbids a single red heatmap (`visual_truth_states.md` §1) — good — but the replacement is a **semiotics exam**.
4. **UNKNOWN vs DATA_GAP vs RESTRICTED** are three stripe languages. Scientists care. Users see “grey puzzle.”
5. **Mode 9** mutes non-gap cells to 22% green (`mapApp.ts` unknownOn paint). Meaning: “some fixture exists.” Users will read muted green as “oysters / fish present.”

**From the panel, if they scroll:** C17 honesty line is clear: “FORECAST. Not observed…” — at y≈1372. C05 is clearer because there is no 1181px ops essay. Default boot is C17.

**Verdict:** the distinction exists in data and in CSS patterns. It is **not available as a human sentence on the first screen**. That is the scientific-honesty UX failure.

---

## 3. What the map is careful about (do not throw away)

Keep these; they are the reason not to ship a fake tuna heatmap:

- No red sequential “life” field (`legend.ts` copy; Okabe–Ito in `TRUTH_COLORS`).
- Hatch for unknown/gap; patterns not color-only (`patterns.ts`, `accessibility_and_trust.md`).
- Forecast dashed, inference dotted (`cells-line-forecast`, `cells-line-inference`).
- Depth-missing hatch ≠ biological absence (`cells-depth-missing`, `main.ts` depthNote).
- SST labeled water skin; overlay does not replace truth outlines (`legend.ts`, `index.html` hint).
- Unknown map refuses to krige (`C05` “interpolation theater”; `unknown_map.md` rules).
- C17 flags: not food-safety, not harvest, SST ≠ body temperature (`renderOps`).
- Banner + stamp + attribution repeat fixture / not navigation / not live animals.
- Cooperative gestures + min/max zoom + maxBounds prevent “flying to the tuna grounds.”
- Stations are fictional and only in Mode 8.

**Do not “fix usability” by filling UNKNOWN with climatology or a tuna prior.** That is the forbidden path in `unknown_map.md` §3 and `visual_truth_states.md` anti-patterns.

---

## 4. Where honesty becomes unreadable (still a failure)

| Mechanism | File | Effect |
|---|---|---|
| Triple disclaimers | banner + stamp + every evidence paragraph | Users stop reading **all** of it, including the one line that matters (forecast vs observed) |
| Category D + Tier 3 + WAC + Vp in one headline | `opsRisk.headline` | Legal/scientific dump; the forecast nature is clause 4 |
| “Fixture” on every value | evidence JSON | Trains people to ignore the content as fake **and** not to learn the encodings |
| Footer always looks like a live forecast | `fillTimebar` always from `meta.timeReadout` | UNKNOWN cell still sits under “Forecast issued at…” — **contradicts** `time_and_forecast_ui.md` n/a rule |
| DIRECT_OBSERVATION of temperature | C01–C02–C13 | Strongest visual (solid blue) is the **weakest biological claim** |
| Hex IDs always on | `cell-ids` | Looks like a cadastral / ops tool, not an ocean |
| Habitat green | `cells-habitat-dots` `#008837` | Spec says green must not mean harvest-OK (`accessibility_and_trust.md`); overlay is still green sequential “elevated” |
| OPS-RISK thicker outline | `isOpsRiskExample` line-width 2.4 | Draws the eye to C17 as the “important fish cell” |

Honesty that nobody understands **is** a product failure. The encodings are a museum label written in the curator’s shorthand.

---

## 5. Globe vs map (3D)

`globe/README.md` and `globe_modes.md` allow 2D MapLibre as MVP fallback. The prototype **is** that fallback. Mode 1 copy even says “(2D map).”

**Recommendation:** 2D default permanently for v1. A 3D globe would add:

- Fake volume (“fish in the column”) Mode 2 was deferred to avoid (`globe_modes.md` Mode 2 blocker).
- Worse click targeting (already weak in 2D).
- No yellowfin data to put on a sphere.

Expert later: globe as **Explore** presentation, never as the species-answer surface.

---

## 6. Spatial honesty

| Claim a user might make from the picture | True? |
|---|---|
| This is Willapa Bay | Approximately yes (`aoi.note`: not shoreline survey) |
| Cells are farms | **No** — public water, coarsened (`meta.json`, C17 privacy) |
| Blue = oysters or fish | **No** — temperature or truth-state |
| Empty/hatched = no animals | **No** — by design |
| Dashed = animals will be there in 72h | **No** — workability/env forecast |
| I can pan to the Pacific for tuna | **No** — `maxBounds` |
| n=24 on a cell is 24 oysters | **No** — synthetic protocol rows |
| SST circles are oyster body T | **No** — copy says so; circles still look biological if legend is hidden |

Grain ~20 km² is honest for privacy (`README.md`). It is **dishonest as a tuna search UI** because tuna questions are basin-scale and this canvas cannot leave the bay.

---

## 7. Time honesty

Clocks exist (issued, valid, inputs, last obs). Good.

Problems:

- `formatClock` shows **ISO-Z and PDT** for every field — looks like machine logs, not “as of 4pm Pacific.”
- Valid window is **72h ops-stress**, easy to read as “fish forecast horizon.”
- Selected-cell last obs (C17: 2026-09-17 off-cell station) ≠ footer last obs (2026-09-18 16:10Z Toke analog). Two truths, no reconciliation on the map.
- No visual difference on the hex for stale vs fresh except opacity recipes that users cannot decode.
- No “now” vs “+24h” map frames (Mode 6 not built — **good**; don’t animate swimming).

---

## 8. Depth honesty

Depth is a **view filter** on boolean flags (`depthSurface`, `depthIntertidal`, `depth0to10`, `depthUnknown`), not a measured animal depth.

- Default “Surface (water skin)” is SST-language, not yellowfin thermocline.
- “Intertidal / emersion” is oyster-specific (`main.ts` disclaimer).
- Unknown depth “blocks High confidence” — policy-honest, phrase-opaque.
- Switching to 0–10 m hatches cells with `depth0to10: false` (C17). Easy to see as “they’re not at 0–10m” rather than “no fixture for that band.”

For yellowfin, this control would be the wrong axis until a species with depth bins exists. Do not imply a water column of animals (`volume_4d_spec.md` later).

---

## 9. What “scientific honesty” must look like on a usable map

For each painted pixel, a non-scientist should answer without scrolling to field 16:

1. **What quantity?** (working conditions / water temperature / habitat / no estimate) — never “life.”
2. **Measured, guessed, or future?** — one word on the chip, not only a dash pattern.
3. **How sure?** — Low / None in English.
4. **How old?** — one local time.
5. **How deep?** — or “depth unknown.”
6. **What would be a lie?** — one line: not tracking, not harvest, not a count.

The prototype has (2)(3)(4) in **pieces** across banner, footer, panel, and hatch. It never **composes** them into one answer. That composition is the P0 map spec (`09_redesign_spec.md`), still **without** a tuna heatmap.

Yellowfin specifically: the honest map is **hatch + “no yellowfin product in this build,”** or a Learn card pointing at Willapa oysters. Anything smoother is the anti-pattern list in `visual_truth_states.md` §7.
