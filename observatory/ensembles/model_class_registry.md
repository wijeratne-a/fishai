# Model class registry

**Date:** 2026-09-18  
**Status:** Registry of classes that *may* exist for high-value taxa. **None are built. None are fitted.**  
**Status vocabulary (only these three):** `NOT_BUILT` | `SPEC_ONLY` | `BASELINE_SPEC`

| Status | Meaning |
|---|---|
| `NOT_BUILT` | Named as a long-horizon class. No observatory spec beyond this row. Do not emit. |
| `SPEC_ONLY` | Described in this program or in commercial artifacts. Not a quality baseline family, **or** a baseline that is optional/uncollected, **or** a candidate blocked on gates. Do not emit as running. |
| `BASELINE_SPEC` | Specified in `artifacts/quality_and_validation/baseline_model_spec.md` for a locked-or-recommended wedge. Versioned id exists. **Not fitted.** Eligible for a v0 ensemble seat if `w1_v0_member` says so. |

**Gates before any candidate (`SPEC_ONLY` / `NOT_BUILT`) may join an ensemble:** (1) founder wedge lock, (2) ground truth in hand at product grain, (3) rights class ≠ UNKNOWN/REJECTED, (4) red-team HIGH/BLOCKER bounded, (5) same **quantity class + horizon + grain + prediction category** as the ensemble target, (6) model card + prediction-contract 14 fields, (7) time-forward + spatial-block evaluation vs the frozen relevant baseline.

Until those gates pass, drawing a class on a map is a **false stack**.

---

## 1. Class catalog (all wedges)

Ids are stable. Do not invent a new class to smuggle a forbidden claim (e.g. “thermal habitat nowcast” as if it were `MC-RULE`).

| Class id | Name | Honest output class | Typical contract category | Typical factory tier ceiling |
|---|---|---|---|---|
| `MC-CLIM` | Climatology baseline | `FORECAST` of a **historical rate / rank**, labeled as climatology | C or D matching the label | T1–T4 (T4 only after prospective tests of the *same* climatology issued as a forecast) |
| `MC-RULE` | Expert-rule | `FORECAST` / rule issuance | D (ops/habitat-like) or mask | n/a — a rule, not a survey |
| `MC-HUM` | Human expert forecast | `OPERATIONALLY OBSERVED` intent (the log) plus a forecast claim | Same as product | n/a |
| `MC-HAB` | Habitat suitability | `MODEL-INFERRED` suitability | **D only** | ≤ T2 |
| `MC-OCC` | Statistical occurrence / SDM | `MODEL-INFERRED` occupancy / encounter *p* | D | T2–T3 after validation |
| `MC-ST` | Spatiotemporal occurrence / index | `MODEL-INFERRED` or `SURVEY-DERIVED` index | C or D | T3+ |
| `MC-MECH` | Mechanistic movement | `TAG/TELEMETRY-DERIVED` or `MODEL-INFERRED` path/kernel | Individual ≠ population | T5 path; not a census |
| `MC-FW` | Food-web / ecosystem | `HYPOTHETICAL/RESEARCH MODE` at 72h; assessment-scale later | Not a 24–72h product | Layer-4 prior, not v0 engine |
| `MC-PART` | Partner-data operational learner | `FORECAST` trained on permissioned outcomes | C or D of **that** label | T6 path only after prospective GO |

**Persistence (quality B3)** is a **diagnostic baseline**, not a ninth ensemble class in v0. If added later, give it `MC-PERS` and the same quantity-class rules. It is **not** in `ENS-W1-OSI72-v0` because W1 v0 membership is climatology + expert-rule + optional human only.

---

## 2. W1 — Pacific oyster × WA × 72h OPS-RISK

**Target quantity class:** `operational_stress_indicator`  
**Label:** `ops_disruption_72h` (binary event) mapped to ordinal bands `typical` / `elevated` / `high` for product display.  
**Grain:** PRIVATE farm-zone nested in PUBLIC/COARSENED WA DOH growing area (or bay).  
**Horizon:** 24–72h from `issued_at`.  
**Universe:** days the farm is stocked.  
**Recommended geography bind (not decided):** Willapa Bay system growing areas.

| Class id | W1 status | `w1_v0_member` | Why this status |
|---|---|---|---|
| `MC-CLIM` | `BASELINE_SPEC` | **yes** | B12: `P(event \| month × growing_area)` with shrinkage to basin-month. Brier-skill reference. **Not fitted.** |
| `MC-RULE` | `BASELINE_SPEC` | **yes** | B4: **air × daytime emersion × solar** (intertidal/exposed) **OR** partner wind/wave workability. Supporting water T / DO / salinity only with lag/mismatch documented. **No SST ≥ 19 °C kill law. No Hobday MHW as default 72h oyster rule.** Thresholds HYPOTHESIS until a human shellfish reviewer locks them. |
| `MC-HUM` | `SPEC_ONLY` | **optional** | B5: grower pre-brief “would you have increased monitoring / changed husbandry or crew timing?” Never harvest-plan language. Missing until collected — **DATA_GAP**, not a silent zero. |
| `MC-HAB` | `SPEC_ONLY` | **no** | Wild/culture habitat envelopes are T2 research. Planted grow-out occupancy is known. Suitability ≠ 72h ops disruption. **Must not enter `ENS-W1-OSI72-v0`.** |
| `MC-OCC` | `SPEC_ONLY` | **no** | Occurrence SDMs are the wrong label for a stocked lease. Presence-only OBIS/GBIF is not a farm event. |
| `MC-ST` | `NOT_BUILT` | **no** | Spatiotemporal farm-event field would need partner labels + blocked CV. Gates 1/3/4 open. |
| `MC-MECH` | `NOT_BUILT` | **no** | Sessile farmed adults. Movement kernels do not estimate bag heat or workability. Larval connectivity is a **different question**. |
| `MC-FW` | `SPEC_ONLY` | **no** | Food-web / EwE / Atlantis are year-scale (`ocean_model_comparison.md`). Not a 72h engine. Do not average an ecosystem index into OSI-72. |
| `MC-PART` | `SPEC_ONLY` | **no** | Partner operational learner is the T6 *path*, not a v0 member. Needs DUA, n minima, and beat of **B4 and B12** prospectively. |

**W1 v0 membership sentence (copy this):**

> `ENS-W1-OSI72-v0` contains only `MC-CLIM` (B12) and `MC-RULE` (B4). `MC-HUM` (B5) is an optional contestability overlay when a pre-brief log exists. Habitat, SDM, spatiotemporal, movement, food-web, and partner learners are candidates, not running members.

### W1 B4 clause map (for disagreement reasons)

| Clause | If missing | Effect on member |
|---|---|---|
| Air × daytime emersion × solar | Subtidal / no emersion culture | **Drop clause** (do not substitute SST). If it was the only primary clause, `cannot_issue` or degrade to workability-only |
| Wind / wave workability | Partner has not given a farm-specific “do not work this tide” threshold | **Drop clause**. Do not invent a number |
| Water T / SST | No in-situ; satellite skin only | Supporting context; SST-only issuance ⇒ member confidence **Low** or **None** (do not issue High) |
| DO | No basin sensor | Supporting; document. Hood Canal hypoxia ≠ Willapa heat |
| Salinity / runoff | No estuary station | Supporting; drop |
| Ploidy / culture type | Unknown | `DISAGREE_UNRESOLVED_BIOLOGY` / OOD on farm dimension; do not pool intertidal with subtidal |

**Must not include in B4:** WA DOH biotoxin, fecal-coliform, Vp prohibition, growing-area open/closed.

---

## 3. W2 — Chinook × CA/OR × 24–48h relative encounter (not v0 bind)

If the founder locks W2 instead, **do not reuse `ENS-W1-OSI72-v0`**. A future `ENS-W2-ENC48-v0` would still be climatology-first.

| Class id | W2 status | Notes |
|---|---|---|
| `MC-CLIM` | `BASELINE_SPEC` | B12 month × port-complex / coarsened cell. Public RecFIN/CRFS is this baseline, **not** the 24–48h label. |
| `MC-RULE` | `SPEC_ONLY` | Quality B4 here is **not** a customer-facing 24–48h habitat model. Open/closed mask + climatology + optional workability confounder. SST band is research-only. |
| `MC-HUM` | `SPEC_ONLY` | Captain intended cell before brief. |
| `MC-HAB` | `SPEC_ONLY` | **Blocked as product** (RT-CHK-01). Seasonal thermal habitat ≠ 48h encounter. |
| `MC-OCC` | `SPEC_ONLY` | Same identifiability failure if sold as 48h. |
| `MC-ST` | `NOT_BUILT` | Candidate only with partner trips + year-block. |
| `MC-MECH` | `NOT_BUILT` | Tags ≠ fleet encounter; ESA / NEVER_PUBLISH for listed units. |
| `MC-FW` | `SPEC_ONLY` | Chlorophyll ≠ adult bite tomorrow. |
| `MC-PART` | `SPEC_ONLY` | Partner CPUE rank is the only honest product-class experiment. |

**Do not average** a habitat SDM with partner CPUE and call it encounter.

---

## 4. W3 — American lobster × GOM × next-trip CPUE (not v0 bind)

| Class id | W3 status | Notes |
|---|---|---|
| `MC-CLIM` | `BASELINE_SPEC` | B12 TMS × month soak-adjusted CPUE. |
| `MC-RULE` | `SPEC_ONLY` | Depth-band × month × zone; closures as **mask**, not CPUE. |
| `MC-HUM` | `SPEC_ONLY` | Intended TMS before brief. |
| `MC-HAB` | `SPEC_ONLY` | Bottom-T habitat ≠ next-trip CPUE; SST skin ≠ bottom. |
| `MC-OCC` | `SPEC_ONLY` | Occupancy of “legal lobster” is not soak-adjusted CPUE. |
| `MC-ST` | `NOT_BUILT` | Survey indices (VAST-like) are seasonal, not next-trip. |
| `MC-MECH` | `NOT_BUILT` | Movement of tagged lobster ≠ operator CPUE. |
| `MC-FW` | `SPEC_ONLY` | Ecosystem models ≠ next haul. |
| `MC-PART` | `SPEC_ONLY` | Operator’s own logs; **never** AIS-as-N. |

**Do not average** habitat suitability with CPUE. **Do not average** CPUE with abundance.

---

## 5. Cross-wedge mixing

There is **no** global multi-species ensemble. A cell that could host oysters, Chinook, and lobster still has **three targets**. Mixing them is a claims violation, not a richer twin.

Observatory-wide, most taxa remain T0–T2 with `UNKNOWN/INSUFFICIENT DATA`. Registry eligibility is not ensemble membership.

---

## 6. Promotion record (empty)

| Date | Class | From | To | Evidence |
|---|---|---|---|---|
| — | — | — | — | No class has been fitted or promoted |

First allowed promotion for W1 after gates: `MC-PART` or a named statistical model may be added **beside** B4/B12, never as a replacement that hides them.
