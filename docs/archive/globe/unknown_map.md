# Unknown map — ignorance as a feature

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/unknown_map.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Binding. **MVP mode.** A hatched cell is a successful render.

The globe must visualize ignorance, not hide it. The Unknown / data-gap view is a **core product feature**, not an error state, spinner, or empty texture.

Commercial analogue: “Cannot issue” is a successful brief. Observatory analogue: most taxa stay T0–T2.

---

## 1. What the mode shows

A global-or-AOI **coverage** canvas. In MVP, **Willapa only**; zooming out = hatch + “no AOI loaded,” not a world of fake density.

Layerable coverage dimensions (parent brief). MVP implements the starred rows; others are labeled later.

| Dimension | MVP | Encoding |
|---|---|---|
| Direct observation density | **Yes** (synthetic) | Sequential gray counts of **samples**, caption *sampling, not animals* |
| Observation recency | **Yes** | Time-since last stamp; `none in window` hatch |
| Depth coverage | **Stub** | Emersion / 0–5 m / unknown |
| Taxonomic coverage | Later | T0–T6 chip, not a richness heatmap sold as biodiversity |
| Seasonal coverage | Later | Calendar holes |
| Survey coverage | Later | Cruise polygons as effort |
| Acoustic coverage | Later | Duty-cycle, not whale GPS |
| eDNA coverage | Later | Station grid of **common** taxa only |
| Telemetry coverage | Later | n tags, **not** tracks if sensitive |
| Habitat-data coverage | Stub | Bathy yes / substrate unknown |
| Environmental-data coverage | **Yes** | Which drivers exist at cutoff |
| Model-validation coverage | **Yes** | `none` for fixture |
| Forecast confidence | **Yes** | H/M/L/None |
| Source outage zones | Later | |
| Extrapolation zones | Stub | Magenta ticks if env out of envelope |
| Unknown areas | **Yes** | Diagonal hatch |

---

## 2. Required low-confidence copy

When confidence is Low or None, the UI **must** be able to print a sentence of this form (fill only true clauses):

> This prediction has low confidence because:  
> — no recent direct observations within {X} km;  
> — no depth-specific records;  
> — environmental conditions outside the model training range;  
> — sparse records during this season;  
> — no validated survey data;  
> — {other listed missing inputs}.

W1 fixture paragraph (required when OSI is Low):

> UNKNOWN / LOW: not enough evidence to estimate on-lease tissue temperature or dissolved oxygen. Nearest station is {distance} km (fixture). OSI-72 is a **relative environmental/workability indicator**, not a count of animals and not a harvest decision. Satellite temperature is not oyster body temperature. This is not food-safety and not harvest authorization. Verify WA DOH.

If **no prediction is issued**:

> Cannot issue an operational-stress score. Official tides/weather/DOH links only. Insufficient evidence is the result.

---

## 3. Visual rules

1. Hatch **does not** mean absence of animals. Caption always: `No estimate / no samples — not “zero fish.”`  
2. Do not krige, IDW, or neural-fill across hatch.  
3. Do not default missing cells to climatology without a **climatology** layer explicitly toggled and labeled.  
4. Observation density is **effort of observation**, never AIS.  
5. Color scale never labeled oysters, fish, or life.  
6. Official DOH outlines remain context, not biology.  
7. Cannot-issue / unknown uses **black/white**, not a broken-image icon, not a spinner that “resolves” into a guess.

---

## 4. Absent vs not detected vs no observations

The Unknown map is where this triad is taught. Full policy: `biological_variables_visual.md`.

| Phrase | When allowed | Visual |
|---|---|---|
| No observations available | Default empty cell | `DATA_GAP` hatch |
| Not detected | Protocol that can report nondetection **and** effort | Separate stamp `nondetection` · still not proof of absence without detectability |
| Species absent | Strong designed survey + detectability model **or** impossible habitat with documented envelope | Extremely rare on a globe; do not use for unsurveyed ocean |

---

## 5. Relation to W1 email

The weekly operator does **not** need a globe. If a local visual is added later, Unknown map + Evidence panel are the **first** map modes — not a choropleth of stress that looks like a harvest map.

NANOOS already maps water. Our differentiator is **honest missingness + contract**, not denser color.
