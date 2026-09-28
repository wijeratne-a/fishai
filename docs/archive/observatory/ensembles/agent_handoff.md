# Agent handoff — Model ensembles, disagreement, scientific contestability

**Date:** 2026-09-18  
**From:** MODEL_ENSEMBLES_DISAGREEMENT_AND_CONTESTABILITY_DESIGNER  
**To:** ORCHESTRATOR, QUALITY_AND_VALIDATION, SCIENTIFIC_RED_TEAM, PRODUCT, OBSERVATION_PLANNER (when created), GLOBE UI (do not overwrite), ARCHITECTURE / DA, MARINE_DOMAIN, DATA_RIGHTS, REQUIREMENTS_AND_WEDGE, founder  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/ensembles/` only  
**Did not write:** `globe/**`, `artifacts/integration/**`, `project_state.json`  
**Did not:** train, ingest, fit B12/B4, issue a mean, task sensors.

Read and aligned with: `artifacts/quality_and_validation/**`, `artifacts/scientific_red_team/**`, observatory architecture/API/output contract. `observatory/observation_planner/**`, `change_detection/**`, `causal_ecology/**`, `detection_bias/**`, and `observatory/species_support_tiers.csv` were **not present** at write time (registry framework exists under `global_species_registry/`; Pacific oyster example tier T2).

---

## 1. Executive finding

**v0 W1 ensemble membership:** only **climatology (B12)** + **expert-rule (B4: air × daytime emersion × solar × partner waves — not SST ≥ 19 °C kill law)** + **optional human farm-manager forecast (B5)** when logged **before** the brief. Habitat suitability, SDM/occurrence, spatiotemporal, mechanistic movement, food-web, and partner-data learners are **candidates**, status `SPEC_ONLY` or `NOT_BUILT`. They are **not running**. Do not draw them.

**v0 is a disagreement product**, not a stacked posterior. Default `ensemble_mean_status = suppressed_unvalidated`. Averaging B4 **High** with B12 **Typical** into **Elevated** is a ship block.

**Disagreement → planner (`DIS-PLAN-W1-v0`):** ticket if (1) \(D \ge 0.5\) and impact medium/high, (2) required member `cannot_issue` and impact high, or (3) OOD and impact medium/high even when members agree. First observation is almost always **outcome logs + culture/workability metadata**, not a new model class.

**Must not be averaged:** habitat with CPUE (or with OSI-72); OSI-72 with DOH/NSSP/Vp; occurrence with abundance; CPUE with stock; 72h ops with 30-day delayed mortality; intertidal B4 with subtidal-as-same-model; candidate classes that failed gates; two farms’ PRIVATE outcomes.

**Canonical fixture FX-02:** expert-rule High vs climatology Typical vs missing farm logs = `DISAGREE_UNUSUAL_OCEAN` + `DISAGREE_ECOLOGICAL_ASSUMPTIONS` + `DISAGREE_DATA_GAP` → planner P0.

---

## 2. Evidence table

| Finding | Why it matters | Evidence | Confidence |
|---|---|---|---|
| W1 target is Category D ops-risk, not food-safety or abundance | Stops illegal ensemble members | Prediction contract §3; recommended wedge; quality label `ops_disruption_72h` | High (as design); Low (commercial lock) |
| Relevant simple models are B12 and B4; B5 is workflow | v0 seats | `baseline_model_spec.md` §4 | High |
| SST ≥ 19 °C is not a WA 72h kill law | B4 membership | Quality B4 rewrite; RT-SIB-01; Raymond et al. 2022 mechanism (cite only) | High |
| Averaging unlike quantities is a known ensemble failure | Same-object test | `ocean_model_comparison.md` §2.13 | High |
| Architecture v0 twin is open-loop B4+B12 | No EnKF ensemble | architecture agent handoff | High |
| Globe already forbids secret averaging | Visual hook | `globe/visual_truth_states.md` Disputed modifier (not edited) | High (if globe file remains binding) |
| No GT, no rights, no fitted baselines | Nothing to weight | Quality/red-team gates 1,3,4 fail | Certain |
| Support tier T2 for *M. gigas* is eligibility not T4 forecast | No up-tier via ensemble spec | `support_tier_framework.md`; registry README | High |

---

## 3. Source / license table

No datasets used. Citations inherited; commercial reuse **not** granted here.

| Source | Use |
|---|---|
| Quality baseline + uncertainty + validation protocol | Member families, ordinal confidence, slices |
| Red-team prediction contract + risk register | Never-claims; food-safety wall |
| Observatory user output contract + species factory | Model ≠ observation; T0–T6 |
| Sensitive location / privacy policies | Coarsened cells; no public lease performance |
| Ocean model comparison §2.13 | Ensemble-as-communication |
| Raymond et al. 2022 *Ecology* (DOI in red-team) | AHW × midday emersion mechanism pointer — **not** a scored fixture |

---

## 4. Confidence and limitations

| Item | Confidence | Limitation |
|---|---|---|
| v0 membership (B12+B4+optional B5) | **High** as design bind for recommended W1 | Wedge UNRESOLVED; founder may lock W2/W3 |
| \(D\) on a 3-level ordinal | **Medium** as a communication device | Not a calibrated posterior; two members only |
| Planner cutoffs (0.5, P0/P1) | **Low** | Hypotheses; will be wrong on ticket volume |
| FX cells | **n/a** | Synthetic; must not be cited as Willapa skill |
| Sibling planner/change-detection/bias folders | **None** | Absent; inbound contract only |
| This agent as domain sign-off | **Invalid** | Need human shellfish + NSSP |

---

## 5. Recommended decision

1. Treat `ENS-W1-OSI72-v0` as **B12 vs B4 (vs B5)**, mean **off**.  
2. If a brief ever ships (quality non-ML path), show the **split table**, not a blend.  
3. Wire planner to `DIS-PLAN-W1-v0` when `observation_planner/` is written; first need = partner outcome form.  
4. Keep `MC-HAB` / SDM / food-web **off** the OSI legend.  
5. Do not train. Do not ingest. Do not promote oyster to T4/T6 because this spec exists.  
6. Globe: later apply Disputed split fill; do not add a red disagreement heatmap.

---

## 6. Rejected alternatives

| Alternative | Why rejected |
|---|---|
| Superlearner / stacking of all nine classes | Classes not built; incomparable quantities; in-sample weights |
| Equal-weight mean as the only UI | Hides B4 High vs B12 Typical |
| SST ensemble (MUR + OSTIA + …) as oyster stress | Wrong variable; still not body T |
| Habitat + CPUE “robust ensemble” | Category error |
| Food-web 72h member | Wrong horizon |
| Persistence as a hidden third vote in v0 | User-specified membership is clim+rule+optional human |
| Public lease disagreement map | Privacy BLOCKER |
| Using DOH closures to break ties | Food-safety contamination |
| Training a disagreement neural net | No labels; theater |

---

## 7. Follow-up questions

1. Founder lock W1 Willapa (or named SPS polygons) vs other wedge?  
2. Culture mix of design partners (intertidal vs float)?  
3. Will B5 pre-brief logging be required in the pilot form?  
4. Who names the shellfish + NSSP reviewer (G8)?  
5. Observation-planner agent: accept `DIS-PLAN-W1-v0` payload as-is?  
6. Globe: confirm Disputed modifier will consume taxonomy codes without a new red life scale?  
7. PRODUCT: email three-row table vs any map in v1?

---

## 8. Artifacts generated

All under `/Users/wijeratne/dev/fishai/observatory/ensembles/`:

| File | Role |
|---|---|
| `README.md` | Membership, planner rule, do-not-average list |
| `model_class_registry.md` | Per-wedge class status |
| `ensemble_math.md` | Mean / \(D\) / weights / slices |
| `disagreement_taxonomy.md` | Why-codes |
| `disagreement_map_spec.md` | Visual; globe hook |
| `planner_handoff.md` | Ticket fields |
| `ood_and_extrapolation.md` | Joint failure |
| `w1_fixture_disagreement.md` | Narrative FX-01…08 |
| `fixture_cells.csv` | Synthetic coarsened rows |
| `governance_hooks.md` | No mean without cards |
| `agent_handoff.md` | This file |

---

## 9. Should this be red-teamed?

**Yes.** Attack at least:

- Mean that hides High B4  
- FX-06 SST kill-law sneaking back as a member  
- Public ticket maps  
- Habitat underlay on OSI  
- “Ensemble” marketing for two unfitted baselines  
- DOH mixed into \(D\)  
- Up-tier language

Re-review when planner or globe implement these fields. This designer is not the human reviewer.

---

## 10. Suggested next experiment

**Do not train. Do not ingest global cubes.**

Smallest contestability test after (or with) founder lock: one permissioned intertidal lease, **14 days**, issue a **split** B4-rule vs B12-table (even if B12 is a crude month flag) + B5 pre-log, outcome form on every day. Success = growers see disagreement without reading harvest advice; FX-02-like days keep the High chip visible; no SST kill-law. Failure = they want a single light, or treat split as DOH.

If no partner: keep fixtures; do not score synthetic rows as skill.

---

**Parent return:** v0 members = B12 + B4 + optional B5; planner rule = `DIS-PLAN-W1-v0`; do not average habitat with CPUE/OSI, or OSI with food-safety, or a High rule with Typical climatology into a calm mean.
