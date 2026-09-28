# Change detection / population-dynamics / anomaly engine

**Program:** Global Saltwater Life Observatory (FishAI scientific blueprint)  
**Owner:** POPULATION_DYNAMICS / CHANGE_DETECTION / ANOMALY_ENGINE  
**Date:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/change_detection/` only  
**Status:** Design + **fixture examples**. No detector is running. No bulk ingest. No operational alerts.

This folder specifies how the observatory *would* turn an effort-aware time series into a typed anomaly — and how it **refuses** to treat missing sampling as biology.

It is **not** a live watch desk, **not** a public hotspot map, and **not** a food-safety HAB authorization service.

Commercial W1 (if later locked): **ops-stress anomalies on a named, permissioned lease** — Category D, prediction-contract language. Not NSSP/WA DOH harvest legality. Not a public aggregation map.

---

## 1. What this engine asks (every series)

For each **taxon × official geography × depth bin × time window**, the engine is required to ask, and to record an answer or `UNKNOWN`:

| Question | Honest quantity | Forbidden shortcut |
|---|---|---|
| Range shift (poleward / equatorward / alongshore)? | Effort- and detectability-corrected occupancy or survey centroid vs a named baseline | Raw GBIF/OBIS dots moving with funding |
| Deeper / shallower? | Depth-stratified index or tag-informed habitat, with *p*(detect) | Surface CPUE or SST as vertical biology |
| Offshore / inshore? | Distance-to-shore or isobath centroid on a designed survey | AIS fleet tracks as animals |
| Phenology early / late? | Timing metric **conditional on effort calendar** (peak, center-of-gravity of a designed index) | First citizen-science report |
| Relative abundance high / low? | Effort-standardized **index** (Category B/C), never *N* | Landings, SST, chlorophyll, vessel density |
| New aggregation? | Independent evidence of concentration **and** privacy/harm review | Public spawn/nursery GPS |
| Dispersal / spreading? | Occupancy gain after effort correction, or a transport model labeled as such | eDNA hit = animals at the filter |
| Habitat suitability deteriorating? | Environmental / EMIV anomaly on a **named mechanism**; not presence | Suitability raster titled “the stock crashed” |
| Recruitment failure? | Stage-correct survey (YOY, spat, legal recruits) at the right lag | Adult CPUE down this week |
| Mortality / disease / HAB / hypoxia / heatwave / pollution / fishing event? | Process class with the **right variables** (e.g. air × daytime emersion, not SST-only for intertidal oysters) | One satellite layer as a kill law |
| Real biology vs observation bias? | Mandatory tree in `bias_vs_biology.md` | Skip the tree because the map “looks like decline” |

**Non-negotiable:** reduced observation rate is **never** population decline without effort **and** detection-probability correction. If that correction cannot be done, the class is `DATA_GAP` or `POSSIBLE_OBSERVATION_ARTIFACT`, not a biological event.

---

## 2. Required output classes (closed set)

Exactly one `event_class` per record:

| Class | Meaning (one line) |
|---|---|
| `RANGE_SHIFT` | Occupancy or survey centroid moved in space after effort/*p* correction |
| `DEPTH_SHIFT` | Vertical distribution of a designed index moved after detectability correction |
| `PHENOLOGY_SHIFT` | Seasonal timing of a designed index moved after effort-calendar correction |
| `AGGREGATION_EVENT` | Unusual concentration; **default publish tier `NEVER_PUBLISH` at native grain** |
| `DISPERSAL_EVENT` | Occupancy/spread increase after effort/*p* correction, or labeled transport |
| `POSSIBLE_MORTALITY_EVENT` | Independent mortality/outcome evidence and/or a named lethal pathway |
| `POSSIBLE_HAB_EVENT` | Named phytoplankton (or toxin-producer) with an **animal-stress** mechanism — **not** NSSP harvest authorization |
| `POSSIBLE_OBSERVATION_ARTIFACT` | Sign of the anomaly is explained as well or better by effort, *p*, platform, regulation, or coverage |
| `DATA_GAP` | Claimed grain/depth/stage/process is not observed; `UNKNOWN` is the product |
| `NO_SIGNIFICANT_CHANGE` | After corrections, residual is within the pre-registered climatology noise band |

There is **no** eleventh class “habitat crashed” or “stock down.” Habitat deterioration is an **environmental driver** (EMIV), attached as `related_env_anomalies[]`. Relative abundance high/low is a **magnitude on a Category B/C index** attached to one of the classes above, or it is not issued.

W1 ops-stress maps onto `POSSIBLE_MORTALITY_EVENT` (when mortality/workability outcomes or the air×emersion pathway support it), `POSSIBLE_HAB_EVENT` (animal-stress taxa only), `POSSIBLE_OBSERVATION_ARTIFACT`, `DATA_GAP`, or `NO_SIGNIFICANT_CHANGE`. W1 does **not** emit public `AGGREGATION_EVENT` maps. Planted oysters do not produce a 72 h wild `RANGE_SHIFT`.

---

## 3. Per-series conceptual state vector

Computed **conceptually** (specified here; **not fitted** in this pass) for every taxon × region × depth × window:

1. **Climatology** — named baseline period + method (usually seasonal×spatial, quality B12 family).  
2. **Current state** — index or indicator in the window, with units and category A–E.  
3. **Anomaly** — current − climatology on the **same** effort-standardized scale.  
4. **Rate of change** — slope or change-point on that scale, with window length.  
5. **Spatial shift** — centroid / occupancy-edge metrics or `not_identifiable`.  
6. **Depth shift** — or `not_identifiable`.  
7. **Seasonal timing shift** — or `not_identifiable`.  
8. **Uncertainty** — `high|medium|low|none` plus rationale (no fake ±).  
9. **Evidence source** — provenance, as-of cutoff, evidence output class.  
10. **Alternative explanations** — including observation-process explanations **first**.

Every stored anomaly record also carries: baseline period, effect magnitude, confidence, observation coverage, confounders, related env anomalies, affected species/life stages, recommended observation task (planner schema), human-review flag. Schema: `event_schema.md`.

---

## 4. The observation-artifact rule (binding)

**Before** any of `RANGE_SHIFT`, `DEPTH_SHIFT`, `PHENOLOGY_SHIFT`, `AGGREGATION_EVENT`, `DISPERSAL_EVENT`, `POSSIBLE_MORTALITY_EVENT`, or `POSSIBLE_HAB_EVENT` may be assigned:

1. Run `bias_vs_biology.md` to completion. The tree is not optional and is not an LLM vibe check.  
2. If effort is missing or incomparable across baseline vs window → `DATA_GAP` or `POSSIBLE_OBSERVATION_ARTIFACT`.  
3. If detection probability (*p*), catchability, platform, water clarity, observer, or regulation can produce the same sign → prefer `POSSIBLE_OBSERVATION_ARTIFACT` until those terms are modeled or bounded.  
4. **A drop in visit rate, trip count, satellite clear-sky days, eDNA stations, or logbook completeness is not a decline.**  
5. SST, chlorophyll, and AIS/VMS/GFW are never relative abundance, range, or mortality by themselves.  
6. Official harvest/sanitation closures are **constraints**, not biological *y*.  
7. Sensitive aggregations are not published at harmful precision (`sensitive_location_policy.md`).

Full tree: [`bias_vs_biology.md`](bias_vs_biology.md).

---

## 5. Commercial W1 vs observatory research

| | W1 (Pacific oyster × WA lease × 24–72 h) | Observatory research classes |
|---|---|---|
| Target | Category **D** operational stress / workability on **planted** stock | Effort-corrected indices, occupancy, phenology, shift metrics |
| Allowed classes | `POSSIBLE_MORTALITY_EVENT`, `POSSIBLE_HAB_EVENT` (animal-stress only), `POSSIBLE_OBSERVATION_ARTIFACT`, `DATA_GAP`, `NO_SIGNIFICANT_CHANGE` | Full closed set, still fixture-only today |
| Geography | Named growing area + permissioned lease (PRIVATE KPIs) | Official units; public grain per privacy policy |
| HAB | Feeding/stress taxa ≠ NSSP toxin stamp | Same wall |
| Aggregation map | **Forbidden** | `AGGREGATION_EVENT` default `NEVER_PUBLISH` |
| Hood Canal ORCA | **Not** Willapa truth | `DATA_GAP` if used as a Willapa proxy |

Prediction contract: `artifacts/scientific_red_team/prediction_contract.md`. Oyster mechanism: air × daytime emersion × workability, not SST ≥ 19 °C as a kill law (`artifacts/quality_and_validation/baseline_model_spec.md` B4).

---

## 6. Sibling catalogs (this pass)

| Path | Status | Consequence |
|---|---|---|
| `observatory/emiv/**` | **Present** `v0.1-draft` | `related_env_anomalies[]` binds registry `emiv_id`. Fixture `EMIV-FIX-*` keys remain record IDs. Crosswalk: `observatory/emiv/engine_id_crosswalk.md`. |
| `observatory/observation_planner/**` | **Present** (design fixtures) | `recommended_observation_task` fields stay as specified here. |
| Bulk observations / partner logs | **Absent** (forbidden) | No fitted climatology, GAM, occupancy, or change-point. CSV rows are **fixtures**. |

---

## 7. Files in this folder

| File | Role |
|---|---|
| `README.md` | This index |
| `event_schema.md` | Record fields, enums, planner/EMIV bindings, privacy |
| `methods.md` | Effort indices, occupancy, ST-GAM residuals, change-point, phenology, centroids; citations; IMPLEMENTABLE_NOW |
| `bias_vs_biology.md` | Mandatory decision tree (observation-artifact rule) |
| `w1_oyster_examples.md` | Narrative for W1 fixtures (2021 heat dome; HAB vs ops; Willapa vs ORCA) |
| `fixture_events.csv` | Fixture records only; `issued_as_operational_alert=false` |
| `validation_and_review_gates.md` | Which classes need human review before any user-facing story |
| `agent_handoff.md` | Return block for the parent agent |

---

## 8. Live emission today

**None.** Default observatory output remains `UNKNOWN/INSUFFICIENT DATA` (`user_output_contract.md`). Fixtures reconstruct **how a past, published case would be classified**, with `record_status=FIXTURE_RESEARCH_ONLY` and `story_eligible=false`.
