# Model ensembles, disagreement, and scientific contestability

**Program:** Global Saltwater Life Observatory / FishAI commercial wedge  
**Path:** `/Users/wijeratne/dev/fishai/observatory/ensembles/`  
**Agent:** MODEL_ENSEMBLES_DISAGREEMENT_AND_CONTESTABILITY_DESIGNER  
**Date:** 2026-09-18  
**Status:** Design + synthetic disagreement fixtures only. **No models trained. No data ingested. No ensemble mean issued as a product.**  
**Wedge lock:** RECOMMENDED W1, not DECIDED. Treat W1 as the design bind, not a live SKU.

This folder specifies how multiple **honest** model classes can sit beside each other without being laundered into a single “AI score,” and how **disagreement** becomes a first-class observatory product that can queue Active Observation Planner tickets.

It does **not** implement stacking, superlearning, EnKF, or a global multi-model heatmap.

---

## Return payload (this pass)

### 1. v0 W1 ensemble membership

**Ensemble id:** `ENS-W1-OSI72-v0`  
**Target:** Category **D** 72h **operational disruption / environmental-stress indicator** (`ops_disruption_72h` / OSI-72). **Not** food-safety. **Not** abundance. **Not** harvest legality. **Not** percent dead.

| Seat | Model class | Member id | Status | In v0 mean? |
|---|---|---|---|---|
| Required | Climatology baseline (B12 seasonal × spatial event rate) | `MC-CLIM` / `B12-v0` | `BASELINE_SPEC` (specified, **not fitted**) | Optional blend only; never the only visual |
| Required | Expert-rule (air × daytime emersion × solar × wind/wave workability) | `MC-RULE` / `B4-v0` | `BASELINE_SPEC` (specified, **not fitted**; numeric gates **HYPOTHESIS**) | Optional blend only |
| Optional | Human farm-manager forecast (pre-brief intended action / watch) | `MC-HUM` / `B5-v0` | `SPEC_ONLY` until a grower logs **before** seeing the brief | **Never** silently averaged; contestability panel only |

**v0 is a disagreement product of two baselines (plus an optional human).** It is not a running habitat/SDM/spatiotemporal/food-web stack.

**Not v0 members** (remain `SPEC_ONLY` or `NOT_BUILT` until wedge lock **and** ground truth **and** rights **and** red-team bounds): habitat suitability, statistical occurrence / SDM, spatiotemporal occurrence, mechanistic movement, food-web / ecosystem, partner-data operational learners. Do not draw them as if they are emitting. See [`model_class_registry.md`](model_class_registry.md).

**Forbidden default inside `MC-RULE`:** SST ≥ 19 °C as a WA oyster kill / mortality law. SST/DO/salinity are supporting covariates with documented lag and spatial mismatch, or they are dropped. Culture without emersion **drops** the air×tide clause rather than substituting SST.

### 2. Disagreement → planner rule

**Rule id:** `DIS-PLAN-W1-v0` (hypothesis; lock after first retro, not from in-sample fit).

Emit an Active Observation Planner ticket when **any** of:

1. `disagreement_index ≥ 0.5` **and** `impact ∈ {medium, high}`  
2. A required member is `cannot_issue` **and** `impact = high` (treat as `DISAGREE_DATA_GAP`)  
3. `ood_flag = true` **and** `impact ∈ {medium, high}` (members may **agree and still be jointly wrong**)

**Do not** ticket “both Typical, in-domain, logs present.” That is agreement, not a gap.

Full field list: [`planner_handoff.md`](planner_handoff.md). Fixture that fires the rule: expert-rule **High** vs climatology **Typical** vs missing farm logs (`DISAGREE_DATA_GAP` + `DISAGREE_UNUSUAL_OCEAN`) in [`w1_fixture_disagreement.md`](w1_fixture_disagreement.md).

### 3. What must not be averaged together

These are **incomparable**. They never share an ensemble mean, a single color bar, or a combined “confidence”:

| Do not average | Why |
|---|---|
| Habitat suitability with CPUE (or with OSI-72) | Different quantity classes; T2 suitability ≠ catch ≠ planted-stock ops stress |
| OSI-72 with WA DOH / NSSP / Vp open–closed | Food-safety wall (RT-OYS-01/04/08). Official status is a **separate module** |
| Occurrence / occupancy *p* with abundance or biomass | Category D vs A/B |
| CPUE with abundance / “stock is up” | Catchability; hyperstability |
| Expert-rule air×emersion with an SST ≥ 19 °C kill law | Wrong thermal variable; the kill law is **not a member** |
| 72h ops indicator with 30-day delayed mortality | Horizon mismatch |
| Intertidal emersion stress with a subtidal-only workability rule as if one model | Culture-type mix (RT-OYS-09) |
| One farm’s PRIVATE outcome with another farm’s | Privacy; lease performance never public |
| Chinook encounter rank with oyster OSI-72 | Different wedges / labels |
| Candidate classes that have not passed gates | Pretending they run |

If two outputs fail this table, the honest product is a **split panel** or a **blocked-candidate chip**, not a mean.

---

## What this folder owns

| File | Role |
|---|---|
| [`model_class_registry.md`](model_class_registry.md) | Classes that exist per wedge; `NOT_BUILT` / `SPEC_ONLY` / `BASELINE_SPEC` |
| [`ensemble_math.md`](ensemble_math.md) | Mean, uncertainty, disagreement, weights from **prospective** skill; never hide spread in one heatmap |
| [`disagreement_taxonomy.md`](disagreement_taxonomy.md) | Agree / disagree / why codes |
| [`disagreement_map_spec.md`](disagreement_map_spec.md) | Visual contract; not red = fish; globe truth-state hooks (do not edit `globe/`) |
| [`planner_handoff.md`](planner_handoff.md) | Score fields for `observatory/observation_planner/` when that agent writes |
| [`ood_and_extrapolation.md`](ood_and_extrapolation.md) | OOD flag dimensions and joint-failure |
| [`w1_fixture_disagreement.md`](w1_fixture_disagreement.md) | Narrative fixtures (synthetic) |
| [`fixture_cells.csv`](fixture_cells.csv) | Machine-readable coarsened cells; **no real farm KPIs** |
| [`governance_hooks.md`](governance_hooks.md) | No ensemble mean without model cards and prohibited-claim checks |
| [`agent_handoff.md`](agent_handoff.md) | Recipients, rejected alternatives, next experiment |

**Did not write:** `globe/**` (in flight), `artifacts/integration/**`, `project_state.json`, observation_planner / change_detection / causal_ecology / detection_bias implementations (those trees were empty or absent on 2026-09-18).

---

## Conceptual outputs (every issuance, when an ensemble is computed)

These are **schema fields**, not computed numbers. Nothing here is a skill claim.

| Field | v0 W1 meaning |
|---|---|
| Model-specific predictions | `B12` band, `B4` band, optional `B5` log — same ordinal: `typical` / `elevated` / `high` / `cannot_issue` |
| Weights | **Equal and unlabeled as skill** until a prospective slice exists. Then region × season weights from locked out-of-sample skill only |
| Ensemble mean | Optional, **suppressed by default** in v0. If shown: “unvalidated blend of baselines,” never “AI consensus” |
| Ensemble uncertainty | Member spread **plus** each member’s own confidence rule (`uncertainty_policy.md`). Spread ≠ calibration |
| Disagreement index | First-class. `0` agree, `0.5` one band apart, `1.0` Typical vs High; `null` if a required member cannot issue |
| Validation by region/season | Score **each member** on basin × month slices. A global mean that hides summer-Willapa failure is a fail |
| OOD flag | Boolean + dimensions (space, season, climate/AHW, management era, culture/farm, missing envelope) |

**Product rule:** disagreement is the feature. An ensemble mean that converts B4 **High** + B12 **Typical** into **Elevated** is a **ship block**.

---

## Honesty constraints (inherited)

- Quality: `/Users/wijeratne/dev/fishai/artifacts/quality_and_validation/` — B12/B4/B5 families; no SST ≥ 19 °C kill law; prospective beat-the-baseline.  
- Red team: `/Users/wijeratne/dev/fishai/artifacts/scientific_red_team/` — Category D ceiling; food-safety wall; no public lease maps.  
- Observatory output contract: `../user_output_contract.md`. A model is never `DIRECTLY OBSERVED`.  
- Twin v0 engine (architecture): open-loop B4 + B12, no EnKF.  
- Privacy: coarsened public cells; farm performance `PRIVATE` / `NEVER_PUBLISH`; no sensitive aggregations that isolate a lease.  
- Globe (later, do not edit here): `visual_truth_states.md` already has a **Disputed** modifier (“do not average secretly”). This folder is the science-side of that modifier.

**Support tier reminder:** *Magallana gigas* registry eligibility is T2 globally. A W1 OSI-72 brief does **not** upgrade the taxon to T4/T6. Factory emission remains `UNKNOWN/INSUFFICIENT DATA` until a publish step exists.

---

## What “scientific contestability” means here

Operators and reviewers must be able to see **which class said what, on which target, with which missing inputs**, and to file that a class is wrong without the UI swallowing the dissent.

Contestability is **not**: a leaderboard of neural nets, a single heatmap with a disclaimer, or averaging habitat with catch “to be complete.”
