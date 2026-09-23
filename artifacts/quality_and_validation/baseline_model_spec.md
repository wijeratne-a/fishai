# Baseline Model Spec — Ocean Intelligence Builder / FishAI

**Agent:** QUALITY_AND_VALIDATION_AGENT  
**Date:** 2026-09-18  
**Version:** `BASELINE-SPEC-2026-09-18-v1`  
**Status:** Specification only. No baselines fitted. No bulk ingest.  
**Wedge:** UNRESOLVED. Five baseline **families** are specified for each of three candidates.

This document is Gate 5 of the advanced-ML blocker list. An advanced model may be called “better” only if it beats the **relevant** baseline **prospectively**, using `validation_protocol.md`.

---

## 1. Purpose and non-negotiable rule

Baselines exist to prevent a common failure: shipping a complex model that is no better than seasonality, last week’s map, or a grower’s existing **air × tide × wave** rule of thumb. **SST ≥ 19 °C is not a WA oyster mortality law** and must not be used as one.

**Rule:** if the advanced model does not beat the relevant baseline on the pre-registered primary metric after **two major iterations**, stop adding model complexity. Diagnose via the failure taxonomy. Consider whether the product is a **data-packaging / workflow** problem rather than a forecasting problem.

Baselines must:

- use only data available at `issued_at`
- share the same label, grain, horizon, and universe as the candidate model
- be versioned (`baseline_id`, code hash, training cutoff)
- be scored on the same slices as the model
- include a **customer current-workflow** baseline when the user will log an intended action *before* seeing the brief

---

## 2. Five required baseline families

Every locked wedge implements all five. “Relevant baseline to beat” is the **strongest simple baseline** on the primary metric in the first time-forward retrospective, frozen before advanced ML.

| ID | Family | Intent |
| --- | --- | --- |
| B1 | Seasonal historical average | Climatology: month / week-of-year / management-season |
| B2 | Spatial historical average | “This place is usually like this” |
| B3 | Persistence / no-change | Last observed outcome at same unit |
| B4 | Simple expert-rule | Transparent thresholds or lookup from domain knowledge |
| B5 | Customer current-workflow | What the user would have done without us |

**B1×B2 interaction** (seasonal-spatial table) is usually stronger than B1 or B2 alone and **is required**. Treat `B12` as the default climatology baseline.

---

## 3. Shared implementation contract

For each baseline version record:

```
baseline_id
family (B1..B5 or B12)
candidate_id (A_oyster | B_chinook | C_lobster)
label_id
horizon
spatial_grain
issued_at_rule
training_cutoff_rule
smoothing / shrinkage
missing_value_behavior
privacy_tier
code_version
feature_sources[]
what_it_does_not_claim
```

**Shrinkage (hypothesis):** where counts are thin, shrink cell-month estimates toward region-month:

`ŷ = (n / (n + k)) * local + (k / (n + k)) * parent`  
with `k = 20` trips or farm-days as a starting hypothesis, tuned **only** inside training years.

**Prohibition:** do not use future-year information to choose `k`.

---

## 4. Candidate A — Oyster 72h operational disruption

**Label:** `ops_disruption_72h` (binary). See validation protocol §4.1.  
**Grain:** farm-zone × issuance day.  
**Universe:** days the farm is stocked.

### B1 — Seasonal historical average

- Event rate by **calendar month** (or ISO week if n allows) pooled across the farm’s own history, else across farms in the same WA DOH growing area.
- Output: `p_season = P(event | month, growing_area)`.
- Alert if `p_season ≥ T_season` (T locked from training years only; hypothesis starting T = month 90th percentile of daily rates, or a simple “alert in Jul–Sep” if events cluster).

### B2 — Spatial historical average

- Event rate by growing area (or basin: Hood Canal / South Sound / Willapa, etc.) ignoring season.
- Weak alone; used for shrinkage parent of B12.

### B12 — Seasonal-spatial (required climatology)

- `P(event | month × growing_area)` with shrinkage to basin-month.
- This is the **Brier-skill reference**.

### B3 — Persistence

- `ŷ = 1` if an event occurred in the previous **7 days** at that farm (hypothesis: disruption clusters), else 0.
- Alternative (co-report): yesterday’s binary state, and yesterday’s mortality rate carried forward.
- Persistence will look strong during multi-day mortality events; the model must still show **lead time** on event *onsets*. Score onset-only recall separately.

### B4 — Simple expert-rule (likely the relevant baseline to beat)

Transparent OR of **operational** rules, using only data available at issuance. **Primary mechanism is air temperature × low-tide emersion × wind/wave workability**, matching the 2021 atmospheric heatwave × midday emersion pathway — **not** satellite SST as oyster body temperature and **not** a kill / percent-mortality law.

**All numeric gates below are HYPOTHESIS.** Lock numbers with MARINE_DOMAIN + a human shellfish reviewer before scoring. Do **not** treat them as WA operational standards or as food-safety / harvest controls.

Alert (`1`) if any **primary** clause fires. Supporting clauses may raise monitoring attention but **do not** by themselves authorize a mortality or harvest claim.

**Primary (required if the culture type can emersion-heat or if the partner has a workability rule):**

1. **Air × daytime emersion × solar (HYPOTHESIS):** forecast **air** temperature overlapping **daytime low-tide emersion** on an intertidal / exposed lease (solar geometry as an input). This flags a **work-window / handling-stress indicator**, not “these oysters will die” and not body temperature. If culture is fully subtidal with no emersion, **drop this clause** rather than substituting SST. **Forbidden default:** SST ≥ 19 °C for ≥12 h (19 °C is a published **growth / clearance** band, not a WA intertidal mortality law; summer Willapa/Puget Sound water often sits there).
2. **Wind / wave workability (HYPOTHESIS):** forecast wind or significant wave height above the **farm-specific** “do not work this tide” rule (partner-provided). If the partner has not given a threshold, **do not invent one — drop this clause**.

**Supporting covariates (lag / mismatch must be documented; never sold as oyster temperature or as a kill law):**

3. **Water T / SST (HYPOTHESIS, supporting only):** nearest in-situ or forecast water temperature may be logged as a **lagged, spatially mismatched** covariate (satellite skin ≠ intertidal tissue; station may be kilometers from the lease). If used at all, use a **basin-specific** watch band supplied by domain review — **no 19 °C WA default**. SST-only issuance ⇒ product confidence **Low** or **None**.
4. **Dissolved oxygen (HYPOTHESIS, supporting only):** latest or forecast DO in a hypoxia watch band. Ecology has documented <3 mg/L in **Hood Canal**; a 5 mg/L operational watch is a **hypothesis**, not a Willapa law. Document sensor lag vs bags/beds.
5. **Salinity / runoff (HYPOTHESIS, supporting only):** |ΔS| ≥ 5 PSU in 24 h at farm or nearest estuary station is a **hypothesis**. Document mismatch to the lease.

**Dropped as a default 72h oyster rule:** Hobday-style **marine** heatwave flags (5+ days, SST percentile). That is the wrong event class for an **atmospheric** heatwave during midday emersion.

**Must not include:** WA DOH biotoxin, fecal-coliform, Vp prohibition, or growing-area open/closed. Those are official **context**, never B4 labels. B4 must not output “harvest window,” “safe,” or percent dead.

B4 is the closest analogue to a competent grower checking **tides + air/heat + NWS workability**, with NANOOS water-quality as supporting context. **If B4 already has acceptable recall/false-alert tradeoff, advanced ML must beat B4, not merely beat B1.**

### B5 — Customer current-workflow

Before opening the brief, grower answers:

- “Would you have increased monitoring / changed husbandry, gear, or crew-timing plans in the next 72 h based on your usual sources?” `{yes, no, already planned}`  
  (**Never** “harvest plans” — harvest legality is WA DOH / NSSP, not this product.)
- Optional: which sources (NANOOS, DOH, consultant, gut).

B5 scoring: treat `yes` as an alert. Compare our brief’s action suggestion to B5 (agreement, and whether outcomes favor our disagreements).

If growers refuse to pre-log B5, the workflow baseline is **missing** (Gate 5 partial fail for decision-value claims; ML skill vs B4 can still be computed).

### Relevant baseline to beat (oyster)

| Claim | Must beat |
| --- | --- |
| “Better than climatology” | B12 on Brier skill and PR-AUC |
| “Better than a grower’s instrument thresholds” | **B4** on recall-at-precision and false alerts/farm-month |
| “Better than what they already do” | **B5** on expected decision value in prospective pilot |
| Deploy as superior forecast | Beat **B4 and B12** prospectively; B5 if collected |

---

## 5. Candidate B — Chinook 24–48h relative encounter

**Label:** `encounter_48h` (binary) on standardized charter trips; secondary CPUE.  
**Grain:** coarsened ~10 km cell × day (product); trip-level for evaluation.  
**Universe:** open recreational Chinook days only. Closed days excluded (not zeros).

### B1 — Seasonal historical average

- Encounter rate and CPUA by **month** (or week-of-season) in the study area, using partner trips if n≥400, else RecFIN/CRFS port-area × month.
- Interannual run size: optionally multiply by a **lagged, public** ocean-abundance / PFMC preseason index **only if** that index is published before `issued_at`. If not yet published, do not sneak it in.

### B2 — Spatial historical average

- Encounter rate by cell / port-complex / CRFS district, pooled over months in-season.
- Thin cells shrink to district.

### B12 — Seasonal-spatial (default relevant climatology)

- `P(encounter | month × port-complex or cell)` with shrinkage `k=20` trips (hypothesis).
- For ranking: historical CPUA percentile of that cell-month among cells.

**Public-data caveat:** CRFS/RecFIN monthly district CPUA **is** B12 at coarse grain. It is a valid baseline for “is this month generally good?” It is **not** a 24–48h cell forecast. A model that only restates B12 at district-month has **zero product lift** even if AUROC vs naive 50% looks fine.

### B3 — Persistence

- Last **successful** trip’s cell (or last trip, including zeros — **co-report both**).
- “Yesterday’s fleet best cell” if multi-vessel partner data exist at issuance (privacy: coarsen; do not leak another captain’s exact spot).
- Persistence is strong inside a bite week and weak across season breaks.

### B4 — Simple expert-rule

**Not a customer-facing 24–48h habitat model.** If this wedge is ever locked, v1 drivers are **open/closed + climatology + optional workability confounder**. Any SST band is a **research** clause only (HYPOTHESIS), not “fish are here.”

1. Start from B12 cell-month rank.
2. Optionally boost cells whose latest SST is inside a **training-only** productive SST band (do not import a global “salmon like 10–14 °C” meme without local calibration).
3. Zero out closed cells, MPAs where fishing is illegal, and cells beyond the vessel’s documented operating range.
4. **Do not** boost cells using AIS density.

If domain agent supplies a documented local rule (tide, swell, river plume), add as named clauses. Each clause needs a biological one-liner and an as-of source.

### B5 — Customer current-workflow

Captain logs **intended primary cell / port-area** before viewing the brief.

Score: realized encounter/CPUE of intended cell vs top recommended cell (paired). This is the **decision-value** baseline.

### Relevant baseline to beat (Chinook)

| Claim | Must beat |
| --- | --- |
| “Better than typical month-and-place” | **B12** on PR-AUC, Brier skill, visited-cell top-20% lift |
| “Better than going back to yesterday’s spot” | **B3** on the same ranking metrics |
| “Better than the captain’s plan” | **B5** paired CPUE / encounter in prospective pilot |
| Deploy as superior forecast | Beat **B12** prospectively; beat B3 in non-persistence weeks (slice); B5 if logged |

A model that beats B3 only by copying B12 in a new moon of the season, but loses to B12 overall, **fails**.

---

## 6. Candidate C — Lobster next-trip CPUE

**Label:** soak-adjusted legal CPUE (pounds or count per trap-haul).  
**Grain:** vessel × TMS (or zone) × trip.  
**Universe:** trips with traps hauled > 0.

### B1 — Seasonal historical average

- Mean / median soak-adjusted CPUE by **month** (or week) in the study area, post-2023 reporting era only unless a break-adjusted series is documented.
- Segment pre/post gauge-size changes (ASMFC Addendum XXVII trigger).

### B2 — Spatial historical average

- TMS (or zone) mean CPUE pooled over years, same era.

### B12 — Seasonal-spatial (climatology)

- TMS × month mean with shrinkage toward zone-month (`k=20` trips, hypothesis).
- This is strong in GOM because the fishery is spatially structured and seasonal. **Beating B12 is the real test.**

### B3 — Persistence (likely co-primary relevant baseline)

- Vessel’s **last trip** soak-adjusted CPUE in the **same TMS**, else same zone, else vessel last trip anywhere.
- Fallback chain must be recorded.
- Persistence captures vessel skill, soak habits, and short-term local density. Models that ignore vessel ID often lose to B3.

### B4 — Simple expert-rule

Hypothesis:

1. Predict B12 (TMS × month).
2. Adjust with a coarse depth band if partner/log depth exists (inshore vs mid-depth seasonal movement — exact function from MARINE_DOMAIN).
3. Suppress TMS with known regulatory closure / whale-related restriction **as a mask**, not as CPUE.
4. Optional: recent water-temperature anomaly vs month climatology, linear coefficient fit **only** on training years.

No AIS density term.

### B5 — Customer current-workflow

Before the brief: intended TMS or zone, planned trap-hauls.

Score: realized CPUE of intended TMS vs predicted top-quartile TMS the vessel could have reached (distance/time constraint from partner, not from AIS reconstruction unless rights-approved).

### Relevant baseline to beat (lobster)

| Claim | Must beat |
| --- | --- |
| “Better than last soak in that square” | **B3** MAE_log1p and rank |
| “Better than typical square-month” | **B12** MAE and rank |
| “Better than the skipper’s intended set” | **B5** in prospective |
| Deploy as superior forecast | Beat **B3 and B12** prospectively on the pre-registered pair (see validation protocol §4.3) |

---

## 7. How to declare “the relevant baseline”

After the **first** time-forward retrospective (no advanced ML yet):

1. Score B1, B2, B12, B3, B4 on the locked primary metric.
2. Set `relevant_baseline_id` = argmax skill among {B12, B3, B4} (B5 is prospective-only).
3. Freeze `relevant_baseline_id` in `project_state.json`.
4. Advanced ML must beat **that** frozen baseline. Do not later switch to a weaker baseline to manufacture lift.

If B4 ≈ B12 ≈ B3, freeze the **ensemble of simple baselines** (e.g. average of B12 and B3 probabilities / CPUE) as `B_ens` and beat `B_ens`.

---

## 8. Baseline vs model fairness checklist

Before claiming lift:

- [ ] Same label and exclusions
- [ ] Same issuance timestamps
- [ ] Same missing-feature policy (if SST is down, B4 and the model both degrade)
- [ ] Same visited-cell / hauled-trap universe (no dummy negatives)
- [ ] Same privacy coarsening
- [ ] No test-year tuning of shrinkage `k` or expert thresholds
- [ ] Onset vs continuation split for oyster persistence
- [ ] Vessel-holdout reported for lobster
- [ ] Closed-season days excluded for Chinook

---

## 9. What baselines are allowed to “win”

A winning baseline is a **success for the company thesis** if it is packaged as a calibrated, uncertainty-aware brief that the customer did not already have in one place.

In that case:

- Do **not** train advanced ML for its own sake.
- Ship the baseline as v0.
- Spend the next iteration on outcome capture, freshness, and workflow, not on gradient boosting.

This is an explicit allowed outcome of Gate 5.

---

## 10. Versioning

| Field | Initial value |
| --- | --- |
| `current_baseline_version` | `UNSPECIFIED` (none fitted) |
| First fitted climatology | `B12-v0` |
| First expert-rule | `B4-v0` |
| First persistence | `B3-v0` |

Fitting is **out of scope** for this agent pass (no ingest). Next experiment after wedge lock: compute `B12-v0` on the minimum lawful public series (Chinook RecFIN/CRFS monthly; lobster only if a lawful aggregate exists) **or** on partner exports — without training advanced models.
