# Agent Handoff — QUALITY_AND_VALIDATION_AGENT

**Agent ID:** QUALITY_AND_VALIDATION_AGENT  
**Date:** 2026-09-18  
**Project:** Ocean Intelligence Builder / FishAI  
**Write path:** `/Users/wijeratne/dev/fishai/artifacts/quality_and_validation/`  
**Project state implication:** Wedge UNRESOLVED. Advanced ML **blocked**. No training, no bulk ingest.

---

## 1. Executive finding

**Better data** is lawful, as-of-honest, decision-relevant data that improves skill, lead time, actionability, coverage, defensibility, uncertainty, or resilience — scored on 18 dashboard dimensions — not a larger ocean lake.

**Better forecast** is a Category C/D claim that beats the frozen relevant simple baseline on time-forward **and** spatial-holdout evaluation **and** a prospective pilot, with calibrated high/medium/low confidence (no opaque score). Random splits of nearby correlated observations are forbidden.

Three candidate **labels and gates are specified as hypotheses**. None can be scored today: Gate 1 (wedge), Gate 3 (ground truth in hand), and Gate 4 (rights) are open.

Public data **does not** currently support 24–72h product-grain labels:

- Oyster farm disruption needs **partner** mortality/workability logs. WA DOH closures are **context**, never a food-safety label.
- Chinook 24–48h encounter needs **partner** catch/no-catch + effort. RecFIN/CRFS is a **seasonal-spatial baseline**, not the label. AIS is never abundance.
- Lobster next-trip CPUE needs **effort + soak** and low latency. Maine 100% e-reporting since 2023 is real but **monthly** and **one 10-minute square per trip**; it can support climatology/persistence research if licensed, not by itself a next-trip GO.

**Do not train advanced ML.** If a wedge locks, ship **B12/B3/B4 baselines** packaged as a brief until minima in §5 are met. Stop adding model complexity if the model fails to beat the relevant baseline after **two major iterations**.

---

## 2. Evidence table

| Finding | Why it matters | Evidence | Confidence | Relevance to customer decision |
| --- | --- | --- | --- | --- |
| WA DOH growing-area program classifies harvest *safety* via sanitary survey / NSSP | Closures must not be `y` for ops-stress models | WA DOH Growing Areas page; commercial closures portal | High (program existence) | Oyster: display as authority context |
| Pacific oyster summer mortality is multi-stressor (T, DO, algae, spawning) | Expert-rule baseline is environmental; label should be **operator outcome** | Cheney et al. 2000 JSR; WA Sea Grant Rapid Response; NOAA shellfish-killing phytoplankton review | Medium–high (mechanism); **not** a skill claim | Justifies B4 ≠ official closure |
| Hood Canal and other basins have documented hypoxia | DO is a covariate; basin-level SAC | Ecology marine WQ reports (e.g. 1998–2000 hypoxia <3 mg/L) | Medium (historical) | Spatial blocking by basin |
| CRFS/OSP/CPFV logs + RecFIN estimates are the lawful public catch/effort spine for CA/OR rec salmon | Public GT exists but is **coarse / lagged** | CDFW CRFS Background; RecFIN InPort 55977; 2023 RecFIN-MRIP plan; CA Open Data ds3184 CPUA | High (program existence) | Chinook B12 only |
| CPFV logs submitted **monthly** | Cannot be same-day labels without partners | CRFS Background | High | Partner form required for 24–48h |
| ME 100% electronic lobster trip reporting since 2023-01-01; due 10th of next month; traps, soak, pounds, one TMS | Strongest public-adjacent CPUE architecture; lag + location coarsening | DMR news 2023-01-03; Chapter 8; 2023 FAQ | High (regulation) | Lobster GT if licensed; still not real-time |
| GOM/GBK stock and landings are non-stationary; gauge measures triggered under Addendum XXVII | CPUE not comparable across eras without flags | ASMFC 2025 assessment news; ASMFC species page | High (management context) | Comparability dimension |
| Random CV overestimates spatial model skill | Forbids i.i.d. row splits | Roberts 2025 *Frontiers in Remote Sensing*; arXiv:2502.03480 (AUC inflation up to ~0.16 reported in that study’s setting — **not** a FishAI number) | High (methods) | Split design |
| ROC sample size grows fast when comparing two models | 200 trips may detect AUC 0.65 vs 0.5; not enough to declare a model beats B12 by 0.05 | Hanley & McNeil 1982 logic (classic) | Medium (order-of-magnitude only) | Chinook n hypotheses |
| No FishAI labels exist in-repo | Gate 3 fail | Empty `/Users/wijeratne/dev/fishai` data | High | No empirical go/no-go |

---

## 3. Source / license table

This agent **did not approve** any source for ingest. Rights class is **indicative pending DATA_RIGHTS_AND_PRIVACY_AGENT**.

| Source | Owner | URL or ID | Access date | Likely rights (not legal advice) | Geography / species | Evidence tier | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WA DOH Growing Areas | WA DOH | https://doh.wa.gov/community-and-environment/shellfish/growing-areas | 2026-09-18 | Public government info; redistribution of GIS **HUMAN LEGAL REVIEW** | WA shellfish | 1 | Context layer only |
| WA growing area closures | WA DOH | https://fortress.wa.gov/doh/eh/portal/odw/si/GrowingAreaClosures.aspx | 2026-09-18 | Same | WA commercial harvest | 1 | Context; never food-safety label |
| WA Sea Grant Rapid Response | WSG | https://waseagrant.uw.edu/our-programs/seafood-fisheries-aquaculture/aquaculture/rapid-response-network/ | 2026-09-18 | Public page; form data not ours | WA shellfish mortality | 2–4 | Research pointer |
| CDFW CRFS Background | CDFW | https://wildlife.ca.gov/Conservation/Marine/CRFS/Background | 2026-09-18 | Public method doc | CA rec fisheries | 2 | Methods |
| RecFIN catch estimates | PSMFC/NMFS | https://www.fisheries.noaa.gov/inport/item/55977 | 2026-09-18 | Dataset license **REVIEW** | West Coast rec | 2 | B12 if licensed |
| CRFS salmon CPUA ds3184 | CDFW Open Data | lab.data.ca.gov dataset ds3184 | 2026-09-18 | CA Open Data terms **REVIEW** | CA salmon blocks | 2 | Coarse B12 |
| RecFIN-MRIP RIP 2023 | NMFS/PSMFC | fisheries.noaa.gov PDF | 2026-09-18 | Public PDF | CA/OR/WA rec | 2 | Methods |
| ME DMR 100% reporting notice | Maine DMR | maine.gov/dmr news 2023-01-03 | 2026-09-18 | Public notice; **microdata restricted** | ME lobster | 2 | GT existence |
| DMR Chapter 8 | Maine DMR | Chapter08 PDF | 2026-09-18 | Regulation | ME landings | 1 | Field list |
| ASMFC lobster | ASMFC | https://asmfc.org/species/american-lobster/ | 2026-09-18 | Public | GOM/GBK, SNE | 2 | Era/non-stationarity |
| NOAA lobster resources | NOAA Fisheries | fisheries.noaa.gov species page | 2026-09-18 | Public; eVTR rules | US lobster | 2 | eVTR 2024-04-01 context |
| Cheney et al. 2000 | JSR | bibliographic | 2026-09-18 | Copyrighted; cite only | PS oyster mortality | 1–2 | Mechanism |
| Spatial CV literature | various | Roberts 2025; arXiv:2502.03480; CRAN blockCV | 2026-09-18 | Publisher/open | methods | methods | Split rules |

**Unresolved:** commercial use of RecFIN micro vs aggregates; ME/NOAA harvester confidentiality; partner DUA templates (owned by rights/product agents).

---

## 4. Confidence and limitations

| Area | Confidence | Limitation |
| --- | --- | --- |
| Need for temporal/spatial blocking | **High** | Exact km block sizes are hypotheses until SAC is measured on real residuals |
| Recommended labels | **Medium–high** as product definitions | Not field-tested with growers/captains |
| Numeric GO thresholds (0.60 recall, 0.65 AUROC, 0.35 Spearman, etc.) | **Low** | Order-of-magnitude hypotheses; **not proven**; must be pre-registered then revised from first retro **without** peeking at a model bake-off |
| Min sample sizes | **Low–medium** | Classic ROC/power logic + rare-event SE; not a FishAI power analysis on real prevalence |
| Which wedge is “best” | **N/A — not this agent’s call** | Validatability ≠ sellability ≠ rights |
| Sibling artifacts | **Low** | Other agents were concurrent; this pass did not depend on their unfinished files |
| No empirical skill | **Certain** | Zero models, zero ingested labels |

---

## 5. Recommended decision

**Orchestrator / founder:**

1. Keep state at research / pause for human wedge lock. **Do not open STATE_6 modeling.**
2. Treat this folder as **APPROVED_AS_DESIGN** for validation, not **APPROVED_FOR_TRAINING**.
3. When a wedge is locked, run Gate 3 (min GT) and Gate 4 (rights) **before** any feature store.
4. First “model” is **B12 + B3 + B4** only.
5. Adopt the per-candidate return values below as the default spec until domain/product agents file a conflict.

### Return values (requested)

#### Candidate A — Pacific oyster × WA × 72h farm ops stress/disruption

| Item | Recommendation |
| --- | --- |
| Target label | **`ops_disruption_72h`**: binary farm-zone event = mortality spike **or** workability disruption **or** emergency intervention. **Not** sensor-threshold-only. **Not** WA DOH/NSSP closure (context only). Category **D**. |
| Min GT | **3** distinct partner farms; **2** seasons; daily or ≥4×/week logs; **≥1,500** farm-days; **≥30 independent events** (gap ≥7 d) to start advanced ML; sensors SST required, DO strongly preferred. Prospective: 3 farms × ≥90 d; ≥15 events or pre-registered rarity plan; ≥70% form completion. |
| Primary metric | **Recall at locked T with precision ≥ 0.40**, plus **false alerts / farm-month**, plus **onset median lead time**. BSS vs B12 secondary. |
| Baseline to beat | **B4 expert-rule** (air × daytime emersion × wind/wave workability; SST/DO/salinity as supporting covariates with documented lag/mismatch — **not** SST ≥ 19 °C as a kill law) **and** **B12** month×growing-area event rate. B5 (grower’s pre-brief plan) for decision-value. |
| GO (hypothesis) | Recall ≥ **0.60** @ P≥0.40; false alerts ≤ **3**/farm-month; onset lead ≥ **12 h**; BSS ≥ **0.10**; beat B4 on recall@P or EDV; prospective. |
| NO-GO / stop complexity | After **2 major iterations**, recall < **0.40** @ that P floor, **or** false alerts > **6**/farm-month, **or** no beat of B4 on BSS and recall, **or** no outcome logging. |

#### Candidate B — Chinook × CA/OR × 24–48h relative encounter

| Item | Recommendation |
| --- | --- |
| Target label | **`encounter_48h`**: ≥1 Chinook kept or released on a standardized charter trip-cell with **angler-hours**, **open-season universe only**. Category **D** user claim, evaluated as **C**. Secondary: CPUE and top-quintile rank among **visited** cells. **Never AIS as y or abundance.** Monthly RecFIN/CRFS = **B12**, not y. |
| Min GT | **≥400** partner trips (zeros kept) across **≥2** open seasons and **≥3** vessels to fit baselines; **≥600** trips hypothesized before advanced ML. Prospective: ≥3 charters, ≥80 briefs with outcomes, ≥60% completion. Public monthly CPUA **insufficient** for a 24–48h GO. |
| Primary metric | **PR-AUC lift vs B12** and **top-20% visited-cell lift**; Brier skill + ECE co-required. AUROC reported, not sufficient. |
| Baseline to beat | **B12** spatial×month encounter/CPUA; also **B3** persistence of last spot; **B5** captain’s pre-brief intended grounds. |
| GO (hypothesis) | PR-AUC ≥ B12 + **0.08**; AUROC ≥ **0.65**; BSS ≥ **0.05**; top-20% lift ≥ **1.30**; ECE ≤ **0.08**; prospective; no AIS-as-abundance. |
| NO-GO / stop complexity | After 2 major iterations, AUROC < **0.55** **or** no PR-AUC/Brier lift vs B12 **or** no zeros logged **or** catch-guarantee language. |

#### Candidate C — American lobster × GOM × next-trip CPUE

| Item | Recommendation |
| --- | --- |
| Target label | **Soak-adjusted legal CPUE** (pounds or legal count per trap-haul), next trip, TMS or coarser. Category **C**. Universe = trips with hauls > 0. Era-flag gauge changes. |
| Min GT | **≥2,000** trip-level records with effort+soak, **≥2** years post-2023 if using ME reports, **≥2** zones; partner path: **≥8** vessels × 2 seasons, outcome latency ≤48 h. Prospective: ≥8 vessels, ≥400 issued+realized, ≥70% completion. Dealer pounds without effort **rejected**. |
| Primary metric | **Spearman ρ** + **top-quartile lift** + **MAE_log1p vs persistence**. |
| Baseline to beat | **B3 persistence** (last comparable trip same TMS/zone) **and** **B12** TMS×month mean. Must beat **both** for GO. |
| GO (hypothesis) | ρ ≥ **0.35**; Q4 lift ≥ **1.20**; MAE_log1p ≤ **0.85×B3** and ≤ B12; 80% PI coverage **0.70–0.90**; lift not only high-liners. |
| NO-GO / stop complexity | After 2 major iterations, neither MAE nor rank beats both B3 and B12; **or** effort missing; **or** AIS as abundance. |

**Unified scorecard:** `go_no_go_scorecard.md` + empty metric tables in `forecast_scorecard_template.md`.

---

## 6. Rejected alternatives

| Alternative | Why rejected |
| --- | --- |
| Train a global SDM now “to learn the stack” | Gates 1–4 fail; violates smallest-valid-experiment rule |
| Use WA DOH closures as oyster y | Wrong decision (food safety); project non-negotiable |
| Use AIS density as Chinook encounter | Effort ≠ fish; forbidden |
| Use RecFIN monthly CPUA as 24–48h label | Temporal resolution fail; would manufacture false skill |
| Use dealer landings without effort as lobster CPUE | Not Category C |
| Random 80/20 split of farm-days or trips | Spatial/temporal leakage |
| Single 0–100 score | Violates uncertainty policy |
| One composite loss mixing oyster mortality + closure + DO crash | Circularity and mixed claims |
| Declaring numeric thresholds “validated” | No data scored |
| Picking the wedge as Quality | Needs product + rights + founder; we only scored **validatability** |
| Treating “winning baseline” as failure | Allowed v0 product if packaged honestly |

---

## 7. Follow-up questions

1. Which wedge will the founder lock, and is a partner DUA possible in 30 days?  
2. Oyster: will growers share **daily** mortality/workability, not only sensor dumps?  
3. Chinook: will charters log **zeros and angler-hours**, and pre-log intended grounds (B5)?  
4. Lobster: can we get **same-day** partner logs, or only lagged agency files?  
5. DATA_RIGHTS: RecFIN/CRFS/ME harvester **commercial-use** class for training vs display?  
6. MARINE_DOMAIN: freeze oyster B4 thresholds and lobster soak function `f(soak)`?  
7. PRODUCT: cost of false alert vs missed event (needed for EDV GO)?  
8. RED_TEAM: any high-severity blocker on these label definitions?  
9. GEO: H3 resolution vs 10 km / TMS / growing-area join keys?  
10. If no partner in 30 days, is the company willing to **pause** rather than backtest the wrong grain?

---

## 8. Artifacts generated

All under `/Users/wijeratne/dev/fishai/artifacts/quality_and_validation/`:

| File | Role |
| --- | --- |
| `validation_protocol.md` | Better data/forecast definitions; splits; per-candidate protocols; ML gates; prospective rules |
| `baseline_model_spec.md` | B1–B5 + B12 for three candidates; relevant-baseline freeze rule |
| `data_quality_dashboard_spec.md` | 18 dimensions, 0–5 anchors, promotion gates |
| `forecast_scorecard_template.md` | Metric tables by product type + slices |
| `go_no_go_scorecard.md` | Unified card; hypothesized numeric gates; stop rules |
| `uncertainty_policy.md` | High/medium/low rules; suppression; no opaque score |
| `agent_handoff.md` | This 10-part handoff |

---

## 9. Whether work should be red-teamed

**Yes.** Priority falsification targets for SCIENTIFIC_RED_TEAM_AGENT:

1. Oyster label circularity (sensors as both x and y).  
2. Closure leakage into ops-risk claims.  
3. Chinook unfished-cell pseudo-absences and AIS.  
4. Interannual salmon-run memorization posing as 48h skill.  
5. Lobster reporting lag treated as next-trip features.  
6. High-liner overfitting.  
7. Hypothesized thresholds presented as if measured.  
8. Any heatmap that reveals exact productive locations.

This validation design should **not** be treated as empirically proven.

---

## 10. Suggested next experiment

**Smallest high-value experiment (after or in parallel with wedge lock):**

Do **not** ingest bulk environmental cubes.

1. Founder names one candidate **or** authorizes three parallel partner asks.  
2. Obtain **one** lawful sample of outcome-shaped data (even n=1 farm month, n=20 charter trips, or a **redacted** lobster log schema) **or** a signed DUA timeline.  
3. Fill the data-quality dashboard **once** for that sample (completeness of effort/zeros/mortality).  
4. If n meets **baseline** minima only, compute **B12/B3/B4** on as-of-safe public climatology **without** ML.  
5. Pre-register the numeric hypotheses in `go_no_go_scorecard.md` as `HYPOTHESIS-v1` so later tuning is visible.

**If partners refuse outcomes:** STOP modeling; consider a workflow/packaging product or a different wedge.

**Handoff recipients:** ORCHESTRATOR (state machine), REQUIREMENTS_AND_WEDGE (Gate 1), DATA_RIGHTS (Gate 4), MARINE_DOMAIN (B4 freeze), PRODUCT (EDV + contract copy), SCIENTIFIC_RED_TEAM (leakage), GEOSPATIAL (as-of snapshots when ingest exists).

---

**End of QUALITY_AND_VALIDATION_AGENT pass.**
