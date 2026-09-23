# Agent handoff — Population dynamics / change detection / anomaly engine

**Agent:** POPULATION_DYNAMICS_CHANGE_DETECTION_ANOMALY_ENGINE  
**Date:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/change_detection/` only  
**Did not write:** `globe/**`, `artifacts/integration/**`, `project_state.json`, `observatory/emiv/**`, `observatory/observation_planner/**`  
**Ingest / live alerts:** none. Fixtures only.

Read (present): `observatory/sensitive_location_policy.md`; `artifacts/marine_domain/**`; `artifacts/scientific_red_team/prediction_contract.md`; `artifacts/quality_and_validation/**`; observatory contracts/API/architecture as context. **EMIV IDs** later bound to `observatory/emiv/` `v0.1-draft` (this wiring pass).

Read (originally absent on authoring day): `observatory/emiv/**`, `observatory/observation_planner/**` — consumer field names remain in `event_schema.md`; variable tokens now use registry IDs.

---

## 1. Executive finding

The engine is a **typed, effort-aware classifier**, not a watch desk. It asks whether a series is a range/depth/phenology shift, a relative-index high/low, a new aggregation or dispersal, habitat deterioration as a **driver**, recruitment failure at the **right stage**, a mortality/HAB/hypoxia/heat/pollution/fishing process, or **observation bias**. It stores climatology, current state, anomaly, rate, spatial/depth/timing shifts, uncertainty, evidence, and alternatives — then emits **exactly one** closed class.

**Observation-artifact rule (binding):** do not treat a change in detections as a change in animals until effort and detection probability are comparable, coverage exists at the claimed grain/depth/stage, official closures are not used as biological labels, and SST/chlorophyll/AIS are not treated as abundance. Otherwise class `DATA_GAP` or `POSSIBLE_OBSERVATION_ARTIFACT`. **Reduced observation rate is never population decline.**

**W1 (commercial):** ops-stress on a permissioned lease — `POSSIBLE_MORTALITY_EVENT` (air × daytime emersion, **not SST-only**; 2021 heat-dome analogue), `POSSIBLE_HAB_EVENT` (**animal-stress** taxa, **not** NSSP harvest authorization), `POSSIBLE_OBSERVATION_ARTIFACT`, `DATA_GAP` (including **Willapa ≰ Hood Canal ORCA**), `NO_SIGNIFICANT_CHANGE`. **Not** a public aggregation map. **Not** food-safety. **Not** operational alerts in this pass.

No detector ran. `issued_as_operational_alert=false` on every fixture.

---

## 2. Evidence table

| Finding | Evidence | Confidence | Relevance |
|---|---|---|---|
| 2021 WA intertidal oyster mortality is air × lowest tides, delayed deaths possible | Raymond et al. 2022 *Ecology* doi:10.1002/ecy.3798; WSG Rapid Response | High (literature mechanism) | W1 class `POSSIBLE_MORTALITY_EVENT`; B4 alignment |
| SST ≥ 19 °C is not a WA kill law; Hobday MHW SST is the wrong 2021 class | prediction_contract.md; baseline_model_spec.md B4 | High (policy + domain) | FIX-CD-FIXT-006 artifact |
| DOH/NSSP closures are not ops GT | ground_truth_relabel_W1.md; marine_domain | High | FIX-CD-2019-003 `DATA_GAP` |
| Hood Canal ORCA ≠ Willapa DO | marine_domain limitations; quality handoff | High | FIX-CD-2026-004 |
| HAB animal-stress ≠ harvest toxin | SoundToxins split; variable matrix; WDFW 2019 narrative | Medium (event mixed) | FIX-CD-2019-002 |
| Effort/*p* before biology | MacKenzie 2002; Harley et al. 2001; RT-OBS-03 | High | Tree N3–N4 |
| Aggregations NEVER_PUBLISH at native grain | sensitive_location_policy.md §5–6 | High | FIX-CD-RES-011 |
| Planted oysters do not 72 h range-shift | marine_domain sessile lease | High | W1 allowlist |
| EMIV / planner dirs | glob 2026-09-18 absent at authoring; **bound 2026-09-18 wiring pass** | Certain | Registry IDs in `related_env_anomalies` |
| No GT in-repo | quality/data discovery | Certain | No fits |

---

## 3. Source / license table

Citations only. **No ingest.** Rights remain UNKNOWN until the rights agent says otherwise.

| Source | Use | Note |
|---|---|---|
| Raymond et al. 2022 | 2021 fixture pathway | Journal copyright; cite |
| Cheney et al. 2000 JSR | Multi-stressor confounders | Cite |
| WDFW 2019 die-off note | HAB vs heat narrative | Tier 3 communication |
| WA Sea Grant Rapid Response | Event context | Cite |
| SoundToxins | Animal-stress vs NSSP split | Do not impersonate |
| WA DOH growing areas | Frame + Module A constraint | Not *y* |
| Ecology ORCA (Hood Canal) | Wrong-basin DATA_GAP | Not Willapa |
| MacKenzie et al. 2002; Maunder & Punt 2004; Harley et al. 2001; Thorson 2019; Wood 2017; Killick et al. 2012; Edwards & Richardson 2004; Pinsky et al. 2013; Hinke et al. 2005; Mills et al. 2017 | Methods citations | Cite |
| Sibling FishAI artifacts | Contract alignment | Do not overwrite |

---

## 4. Confidence and limitations

| Item | Confidence | Limitation |
|---|---|---|
| Closed class set + W1 allowlist | High | Founder could demand a public map; refuse |
| Observation-artifact rule | High as policy | Not empirically tuned |
| 2021 classification drill | High as *class* | Low as product score; no lease % |
| 2018–19 HAB fraction | Low–medium | Multi-stressor; unconfirmed disease |
| Numeric phenology/centroid methods | Spec only | IMPLEMENTABLE_NOW ≠ fitted |
| Live skill | N/A | Zero series |

This agent is **not** a human shellfish or NSSP reviewer. HIGH review gates stay open.

---

## 5. Recommended decision

1. Accept the closed class set and the observation-artifact rule as the observatory change-detection contract.  
2. Bind W1 to lease ops-stress classes only; keep food-safety and public aggregations structurally impossible.  
3. Consume `event_schema.md` field names; `emiv_id` is the `v0.1-draft` registry ID.  
4. Do not implement a live writer or `/anomalies` heatmap.  
5. First compute (after wedge + rights + partner logs): B12/B4 residuals + coverage flags — not ST-GAM.

---

## 6. Rejected alternatives

| Alternative | Why |
|---|---|
| Live 2026 anomaly alerts using 2021 copy | Forbidden operational look-alike |
| SST or Hobday MHW as 2021 mortality | Wrong variables |
| DOH closure as HAB/mortality class | Wrong label; legal wall |
| ORCA → Willapa hypoxia | Wrong basin |
| *n_obs* down = decline | Artifact rule |
| Public aggregation / kill choropleth | Privacy + prediction contract |
| Eleventh class “habitat crashed” as biology | EMIV driver only |
| Occupancy fill of empty cells | Manufactured confidence |
| W1 `RANGE_SHIFT` at 72 h | Sessile planted stock |

---

## 7. Follow-up questions

1. Founder W1 lock (Willapa vs other single estuary)?  
2. Unresolved `other` anomaly tokens (e.g. tidal transport) — bind later or leave as `other`?  
3. Named shellfish + NSSP humans for G-HUMAN?  
4. Partner mortality/workability DUA (without this, W1 stays `DATA_GAP`)?  
5. Confirm no public biological story from fixtures?

---

## 8. Artifacts generated

All under `/Users/wijeratne/dev/fishai/observatory/change_detection/`:

| File | Role |
|---|---|
| `README.md` | Index, questions, classes, artifact rule |
| `event_schema.md` | Record fields; EMIV registry + planner bindings |
| `methods.md` | Indices, occupancy, ST-GAM, change-point, phenology, centroids; IMPLEMENTABLE_NOW |
| `bias_vs_biology.md` | Mandatory tree |
| `w1_oyster_examples.md` | 2021 / HAB vs ops / ORCA narratives |
| `fixture_events.csv` | 12 fixtures; all 10 classes; no operational alerts |
| `validation_and_review_gates.md` | Human review before stories |
| `agent_handoff.md` | This file |

---

## 9. Red-team?

**Yes.** Highest remaining abuses: issuing a 2026 alert from FIX-CD-2021-001; mixing HAB-stress with NSSP; publishing FIX-CD-RES-011; filling Willapa DO from ORCA; calling FIX-CD-FIXT-007 harvest-safe.

---

## 10. Suggested next experiment (no ingest)

Paper protocol already proposed by marine domain E1: reconstruct 26–28 Jun 2021 **air × predicted daytime emersion** vs SST-only ranking of affected vs less-affected sites using **published** Raymond maps — as a **classification/method test**, not an alert. Stop if SST-only “wins” and someone wants to ship it anyway.

---

## Return block (requested)

### Event classes (closed)

`RANGE_SHIFT` · `DEPTH_SHIFT` · `PHENOLOGY_SHIFT` · `AGGREGATION_EVENT` · `DISPERSAL_EVENT` · `POSSIBLE_MORTALITY_EVENT` · `POSSIBLE_HAB_EVENT` · `POSSIBLE_OBSERVATION_ARTIFACT` · `DATA_GAP` · `NO_SIGNIFICANT_CHANGE`

W1 allowlist: mortality (ops), HAB-stress, artifact, gap, no-change. Aggregations default `NEVER_PUBLISH`. Habitat deterioration is an EMIV driver, not an 11th class.

### W1 fixture events

| ID | Class | Point |
|---|---|---|
| **FIX-CD-2021-001** | `POSSIBLE_MORTALITY_EVENT` | 2021 heat dome: **air × daytime emersion**, not SST-only; delayed death; PRIVATE; not a 2026 alert |
| **FIX-CD-2019-002** | `POSSIBLE_HAB_EVENT` | Animal-stress HAB hypothesis; **not** food-safety authorization |
| **FIX-CD-2019-003** | `DATA_GAP` | DOH/NSSP status is not ops *y* |
| **FIX-CD-2026-004** | `DATA_GAP` | **Willapa ≠ Hood Canal ORCA** |
| **FIX-CD-FIXT-005** | `POSSIBLE_OBSERVATION_ARTIFACT` | Visit-rate drop ≠ planted-stock decline |
| **FIX-CD-FIXT-006** | `POSSIBLE_OBSERVATION_ARTIFACT` | SST-only warm pixel ≠ mortality |
| **FIX-CD-FIXT-007** | `NO_SIGNIFICANT_CHANGE` | Typical June ≠ harvest-safe |

Research rows 008–012 exercise the other classes without W1 product claims.

### Observation-artifact rule

Before any biological class: complete `bias_vs_biology.md`. Missing or incomparable effort, changing *p*/catchability/platform, wrong-basin instruments, SST/chl/AIS-as-animals, or official closures-as-*y* → `DATA_GAP` or `POSSIBLE_OBSERVATION_ARTIFACT`. **A drop in observation rate is never population decline** without effort and detection-probability correction. Sensitive aggregations are not published at harmful precision.
