# Validation Protocol — Ocean Intelligence Builder / FishAI

**Agent:** QUALITY_AND_VALIDATION_AGENT  
**Date:** 2026-09-18  
**Project root:** `/Users/wijeratne/dev/fishai`  
**Status:** Protocol design only. No models trained. No bulk data ingested.  
**Wedge:** UNRESOLVED. This document specifies protocols for three candidate wedges, then how they share one scorecard.  
**Version:** `VAL-PROTOCOL-2026-09-18-v1`  
**Numeric thresholds:** **HYPOTHESES**, not proven. They are proposed gates to be confirmed or revised after the first locked retrospective evaluation and the first prospective pilot.

Related artifacts:

- `baseline_model_spec.md` — baselines that any advanced model must beat
- `data_quality_dashboard_spec.md` — definition of “better data”
- `forecast_scorecard_template.md` — metric tables by product type
- `go_no_go_scorecard.md` — unified decision card
- `uncertainty_policy.md` — high/medium/low confidence rules (no opaque single score)

---

## 0. What this protocol is for

This protocol exists so the project can say, **before model building**, what would count as:

1. **Better data** than the current approved set.
2. **A better forecast** than the customer’s current workflow and the locked simple baselines.

It is the acceptance test for STATE_5 (baseline and validation design) and a hard gate for STATE_6+ (minimum product, prospective testing, advanced ML).

It does **not** choose the wedge. It does not claim any candidate currently has a valid forecast.

---

## 1. Definitions (lock these before any training)

### 1.1 Better data

**Better data** is not more data. A candidate source or derived table is better data **if and only if** all of the following hold:

1. **Lawful.** Rights status is `APPROVED_OPEN_COMMERCIAL`, `APPROVED_WITH_ATTRIBUTION`, `APPROVED_INTERNAL_ONLY`, `APPROVED_PARTNER_CONSENT`, or human-approved after review. Unknown, restricted, research-only, or noncommercial-only sources are not production data.
2. **Decision-relevant.** It maps to the locked target label, horizon, and customer action for the selected wedge.
3. **Honest at issuance.** `published_at` / `available_at` is known so the record can be used in as-of replay. Data that cannot be time-stamped is research-only.
4. **Material lift or resilience.** Relative to the current approved set it is expected to improve at least one of:
   - A. prediction quality on honest validation
   - B. forecast lead time
   - C. user actionability
   - D. coverage of an economically meaningful risk or opportunity
   - E. defensibility via permissioned, outcome-linked feedback
   - F. scientific credibility or uncertainty estimation
   - G. reliability / resilience of a critical input
5. **Does not fail** privacy, ecological-sensitivity, or outcome-linkage gates (see dashboard spec).
6. **Beats its cost.** Legal, maintenance, privacy, and ecological risk do not exceed expected decision value.

**Reject** a source that is merely available, merely high-volume, or merely “ocean-themed.”

Operational scoring of better data is the 18-dimension dashboard in `data_quality_dashboard_spec.md`. A source may enter research use with documented limitations; it may not enter a customer-facing forecast until dashboard gates in §6 of that spec pass.

### 1.2 Better forecast

A forecast is **better** than the locked baseline **if and only if** all of the following hold:

1. It uses a **locked prediction contract** (Category C or D for public products; never convert habitat, AIS, or effort into abundance or a catch/harvest guarantee).
2. It is evaluated with **time-forward** and **spatial** honesty (this document). Random splits of nearby correlated observations are forbidden without a written scientific justification.
3. On the **primary metric** for that product type, it **beats the relevant baseline** on:
   - at least one locked retrospective time-forward split, **and**
   - at least one spatial holdout or geographic-transfer test, **and**
   - a prospective pilot (required before any customer-facing superiority claim).
4. It is **calibrated** enough to support the stated confidence language (see `uncertainty_policy.md`).
5. It shows at least one of: superior predictive skill, superior **expected decision value**, meaningful **lead-time** advantage, uniquely useful coverage, observed customer behavior change, or willingness to pay.
6. Failures are classified (label / data / bias / shift / product mismatch) rather than hidden in an average score.

**A model that fits history and fails prospectively is not a better forecast.**  
**A model that beats random chance but not the seasonal-spatial baseline is not a better forecast.**  
**A model that is uncalibrated, or that uses a single opaque score, is not deployable.**

### 1.3 Prediction-contract categories (from the project claims policy)

Every target must be classified as exactly one of:

| Code | Category | Allowed as initial public product? |
| --- | --- | --- |
| A | Direct count | No, except bounded survey quote |
| B | Survey-derived abundance index | Only if a documented survey protocol exists |
| C | Effort-normalized catch / observation index | Yes |
| D | Relative habitat, encounter, or risk likelihood | Yes |
| E | Unverified indicator | Never as the product claim |

Default public output is **C or D**. Category A/B claims may appear only as attributed survey context.

### 1.4 Independent observation (for sample-size and split design)

Two labeled records are **not independent** if they share the same:

- farm and calendar week (oyster),
- vessel-day or adjacent 10 km cells on the same calendar day (Chinook),
- vessel-trip or adjacent 10-minute squares in the same calendar week (lobster),
- or they fall inside the empirical spatial autocorrelation (SAC) range computed on residuals of the seasonal baseline.

Sample-size hypotheses below count **independent events / trips / farm-weeks**, not raw rows.

---

## 2. Gates that must pass before advanced ML

Do not begin advanced model training until **all eight** are true. Today, with wedge UNRESOLVED, **Gate 1 fails**, so advanced ML is blocked for every candidate.

| # | Gate | Pass criterion | Owner |
| --- | --- | --- | --- |
| 1 | Wedge defined | One species × geography × customer × recurring decision locked in `project_state.json` | REQUIREMENTS_AND_WEDGE + founder |
| 2 | Target label defined | Single primary label with unit, horizon, spatial grain, positive-class rule, and exclusions (this file §4) | QUALITY + MARINE_DOMAIN |
| 3 | Ground truth available | Minimum dataset in §4 actually in hand under an approved rights class, not merely identified | DATA_DISCOVERY + PARTNER |
| 4 | Rights approved | Every training/eval/feature source in an approved class; partner DUA signed if private outcomes are used | DATA_RIGHTS |
| 5 | Baseline defined | Five baseline families specified and versioned (`baseline_model_spec.md`) | QUALITY |
| 6 | Validation protocol approved | This document (or a successor) accepted; splits generated from as-of data only | QUALITY + RED_TEAM |
| 7 | Red-team: no unresolved blocker | High-severity leakage, proxy-misuse, privacy, or claims issues resolved or explicitly bounded | SCIENTIFIC_RED_TEAM |
| 8 | Prediction contract defined | 14 product-output-contract fields; Category C/D; “what it does not mean” locked | PRODUCT + QUALITY |

**Diminishing-returns / stop rule:** if the advanced model **fails to beat the relevant baseline** on the primary metric in honest evaluation after **two major model iterations**, stop model complexity. Diagnose. Do not add species, regions, or architecture.

A **major model iteration** is a change to (a) target definition, (b) a feature family, or (c) model class. Hyperparameter search inside one class is not a major iteration.

---

## 3. Universal validation design (applies to all three candidates)

### 3.1 Forbidden evaluation practices

Unless a written justification is attached to the evaluation report, **do not**:

1. Randomly split nearby correlated observations (same day, adjacent cells, same farm-week, same trip) into train and test.
2. Tune on the test year or test region.
3. Evaluate a historical forecast using data published or revised **after** `issued_at` unless the run is explicitly labeled `retrospective_corrected_data_analysis` and is **not** used for go/no-go.
4. Use AIS / VMS / vessel density as a label or as an abundance target.
5. Use official shellfish closures as a food-safety or legal-harvest label.
6. Convert a habitat or risk score into a fish count, catch guarantee, or harvest authorization.
7. Report a single skill number without slices (season, subregion, habitat, observation density, freshness).
8. Impute test-set labels or drop difficult zeros without counting them in the denominator.
9. Train on partner data then evaluate on the same partners’ overlapping trips/farms without a partner-holdout.
10. Claim calibration from in-sample reliability diagrams.

### 3.2 Required evaluation methods

Every candidate must run, in this order:

| Method | Purpose | Pass / fail use |
| --- | --- | --- |
| **Time-forward (expanding or sliding window)** | Mimic issuance: train on past, predict future | Primary retrospective gate |
| **Out-of-year (leave-one-year-out)** | Interannual biological / climate / fishery shifts | Required robustness |
| **Out-of-season** | If the decision concentrates in one season (salmon openers; oyster summer mortality; lobster shed/molt) | Required if seasonality dominates the label |
| **Spatial holdout** | Block by growing area / PFMC-CDFW district or 10 km cells / lobster zone or 10-minute square groups | Required |
| **Geographic transfer** (if ≥2 subregions) | Train in one basin, test in another | Informs expansion; not a deploy gate for the first farm/fleet |
| **Prospective pilot** | Lock forecast before outcome exists | **Required** for any “better than baseline” customer claim |

**Block construction:**

1. Compute a SAC diagnostic on residuals of the seasonal-spatial baseline (variogram or Moran’s I vs distance). Record the practical range.
2. Set spatial block size ≥ that range, or a domain-justified administrative unit (WA DOH growing area; CDFW CRFS district / 1′ block aggregation; Maine lobster zone / 10-minute square clusters), whichever is **larger**.
3. Assign **blocks** (not rows) to folds. Random assignment of blocks is allowed; random assignment of rows is not.
4. Ensure each evaluation fold contains both classes (occurrence / alert products) or ≥20 continuous outcomes (CPUE). If a fold is degenerate, skip its AUROC/PR-AUC and report the skip.

Literature that motivates blocking rather than i.i.d. CV (methods, not FishAI results): Roberts et al. 2025, *Frontiers in Remote Sensing* (marine spatial block CV); spatiotemporal CV for SDMs (arXiv:2502.03480); `blockCV` package guidance that block size should track the SAC range.

### 3.3 As-of replay (non-negotiable)

Every evaluation row must carry:

- `issued_at` (when the forecast would have been delivered)
- `forecast_window_start` / `forecast_window_end`
- `training_data_cutoff`
- `source_data_cutoff` per input
- `feature_snapshot_id`
- `model_or_baseline_version`
- `label_available_at` (when the outcome could first have been known)

A feature is illegal in a replay if `available_at > issued_at`.

Official closure snapshots, SST analyses, and landings tables **revise**. Use the vintage available at issuance for the primary scorecard. A parallel “finalized data” scorecard may be produced and must be labeled as such.

### 3.4 Slices (always)

Report the primary and secondary metrics sliced by:

- season (or management season: salmon opener; oyster summer/fall; lobster calendar quarter)
- subregion
- habitat or depth band (when known)
- observation density (low / medium / high)
- data freshness at issuance (fresh / stale / missing-critical)
- customer / vessel / farm type
- extreme-event flag (marine heatwave, storm, hypoxia, fishery closure of *other* species, gauge-size change)

A global average that hides failure in the high-value season is a **fail**.

### 3.5 Uncertainty is part of validation

Do not accept a point forecast without the fields in `uncertainty_policy.md`. Validation must score:

- interval coverage (nominal 50% and 80% or 90%)
- confidence-category reliability (do “high” cases actually have lower error / better Brier?)
- suppression rate (how often the product correctly refuses to speak)

### 3.6 Decision-value evaluation (not optional for go)

ML metrics are necessary but not sufficient. For each product define:

- action the user could take
- cost of action
- cost of missed event
- cost of false alert
- value of true alert

`Expected Decision Value = P(event) × Value_true − P(false alert) × Cost_false − Cost_of_action`  
(hypothesis formula; inputs from PRODUCT_AND_MONETIZATION interviews, not assumed here).

A model may progress on decision value even with modest skill **only if** the action is cheap, lead time is real, and false-alert cost is measured — not asserted.

### 3.7 Drift monitoring (after any live issuance)

Track, at least weekly during a pilot:

- covariate shift: PSI or energy distance on SST, DO, effort, depth vs training window
- label shift: event rate / mean CPUE vs history
- performance drift: rolling primary metric vs locked baseline
- source health: latency, null rate, schema hash (see dashboard spec)
- confidence mix: share of high/medium/low issuances

Trigger a **pause** if rolling 28-day primary metric falls below the baseline for two consecutive weeks, or if a critical source is down without an approved fallback.

---

## 4. Candidate-specific protocols

All **recommended labels, sample sizes, and numeric gates are hypotheses**.

Shared rule: **one primary label per candidate**. Secondary labels are diagnostic only and may not be mixed into a single loss without a separate spec.

---

### 4.1 Candidate A — Pacific oyster × Washington × 72h farm operational stress / disruption

| Field | Specification |
| --- | --- |
| Species | Pacific oyster (*Magallana gigas* / *Crassostrea gigas*). Taxonomy authority to be locked by MARINE_DOMAIN (WoRMS). |
| Geography | Washington State growing areas (Puget Sound / Hood Canal / coastal estuaries such as Willapa–Grays Harbor as subregions). Spatial grain: **partner farm-zone** (private) nested in **WA DOH growing area** (public context). |
| Customer | Farm operator |
| Horizon | 72 hours from `issued_at` |
| Cadence | Daily brief, issued morning local time, timestamped UTC |
| Product type | **Risk-alert** |
| Contract category | **D — relative operational-risk likelihood**. Not food safety. Not legal harvest authorization. |
| Official closure | **CONTEXT only.** Display WA DOH / NSSP status with authority, timestamp, jurisdiction, source URL, boundary, last-verified time. **Never** the model label for food safety. |

#### Recommended primary target label (hypothesis)

**`ops_disruption_72h` ∈ {0,1}** at farm-zone grain.

Positive (`1`) if **any** of the following occurs inside the 72h window, using partner operations records:

1. **Mortality spike:** observed mortality rate ≥ **max(2× trailing 28-day median daily mortality, farm-agreed absolute floor)**. Absolute floor hypothesis: **1% of standing stock per day** or a count-based equivalent the grower already uses. The floor must be locked per farm before training.
2. **Workability disruption:** planned husbandry, harvest, or planting is postponed, shortened, or judged unsafe **because of environmental or access conditions** (waves, wind, tide window, water-column conditions) — not because of labor no-show or market price.
3. **Emergency intervention:** unplanned emergency harvest, relay, aeration, density reduction, or similar recorded action.

**Exclusions (must not flip the label to 1):**

- WA DOH / NSSP classification change, rainfall-conditional closure, or biotoxin closure (PSP/DSP/ASP) used as if they were biological farm stress. Those are **context**.
- Equipment failure unrelated to environmental stress.
- Predicted sensor-threshold crossings **alone**. Using the same DO/SST series as both feature and label is circular.

**Secondary diagnostic labels (not the product claim):**

- `mortality_rate` (continuous)
- `growth_increment` if measured
- `env_stress_hours` (hours SST / DO / salinity / pH beyond farm thresholds) — **features or diagnostics, not the primary label**
- official `closure_status` — context dashboard only

**Scientific rationale (mechanism, not a performance claim):** Pacific oyster summer mortality in Puget Sound is a multi-stressor problem (temperature, DO, salinity shocks, harmful algae, reproductive stress), documented over decades (e.g. Cheney et al. 2000, *Journal of Shellfish Research*; Washington Sea Grant Rapid Response Network for climate-driven mortality; NOAA/NCCOS work on shellfish-killing phytoplankton in Washington). WA DOH Growing Area Program classifies harvest *safety*, which is a different decision (https://doh.wa.gov/community-and-environment/shellfish/growing-areas). Ecology marine monitoring has documented late-summer hypoxia (<3 mg/L) in Hood Canal and other basins — useful **covariate** geography, not a food-safety label.

**Circularity control:** if a farm’s only recorded “event” is a sensor alarm, that farm cannot be used to train a model whose features are those same sensors. Require operator-observed mortality, workability, or intervention as the label.

#### Ground truth

| Source | Role | Evidence tier | Notes |
| --- | --- | --- | --- |
| Partner farm mortality, growth, workability, intervention logs | **Primary label** | 1–2 | Private; DUA required |
| Partner or existing lease sensors (T, S, DO, pH, waves) | Features / diagnostics | 1 | Calibrate; record depth |
| WA Sea Grant / PSI mortality reporting forms | Research context; possible opt-in | 2–4 | Not a substitute for partner logs; commercial growers may have separate WDFW transfer-permit duties |
| WA DOH growing area classification and commercial harvest closures | **Context only** | 1 (authority) | NSSP; not ops-stress label |
| NANOOS / ORCA / Ecology / NDBC / CMEMS SST, DO, waves | Features | 3 | As-of vintage; not labels |

Public data **cannot** currently replace partner outcomes at farm-zone, 72h grain. **No partner log ⇒ Gate 3 fails ⇒ no advanced ML.**

#### Minimum ground-truth dataset (hypothesis)

**Retrospective (to approve a baseline + first model iteration):**

- ≥ **3** geographically distinct partner farms (not three zones of one company in one bay)
- ≥ **2** growing seasons with summer–early fall coverage
- Daily (preferred) or ≥ **4 days/week** structured logs of mortality and workability
- ≥ **1,500** labeled farm-days
- ≥ **30 independent disruption events** (events at one farm separated by ≥7 days). If event count < 30, do **not** train advanced ML; run expert-rule baseline and collect more outcomes.
- Sensors: at least SST at farm or nearest in-basin station with documented offset; DO strongly preferred in Hood Canal / stratified basins

**Prospective pilot:**

- ≥ **3** farms receiving a daily brief for ≥ **90 consecutive days** in the high-risk season (typically Jun–Sep, lock with domain agent)
- ≥ **15 independent events** in the pilot window **or** a pre-registered decision-value analysis if events are rarer than expected (rarity is a stop/narrow trigger, not an excuse to skip scoring)
- Outcome form completed on ≥ **70%** of farm-days (hypothesis)

#### Spatial / temporal splits

- Time-forward: train through season *t−1*, test season *t*; also expanding monthly windows inside season.
- Out-of-year: leave-one-year-out.
- Out-of-season: train non-summer, test summer (expect collapse; documents that skill is seasonal).
- Spatial holdout: leave-one-**growing area** out; do not treat adjacent leases in the same basin as independent.
- Transfer test (optional): train Puget Sound, test Willapa / Grays Harbor.

**Block size hypothesis:** growing area or 10–20 km, whichever exceeds residual SAC.

#### Primary metric

**Risk-alert suite, primary number for go/no-go:**

1. **Recall** of `ops_disruption_72h = 1` at a locked operating point with **precision ≥ 0.40** (hypothesis)
2. **False alerts per farm-month** (primary operational constraint)
3. **Median lead time (hours)** among true alerts, for events that are physically predictable (exclude same-hour equipment failures)

Secondary: PR-AUC, Brier score, Brier skill vs seasonal baseline, calibration (reliability + ECE), action rate.

**Why not AUROC as primary:** disruption is (hypothesis) uncommon; AUROC can look acceptable while missing events. AUROC is reported but not the go metric.

#### Baseline that must be beaten

**Primary baseline to beat:** simple **expert-rule** environmental thresholds (see `baseline_model_spec.md` §A), because that is the closest analogue to a competent grower’s current toolset (NANOOS/ORCA + local knowledge).

**Required comparison set:** seasonal historical event rate by month × growing area; persistence of yesterday’s alert; customer current-workflow (when logged).

#### Prospective pilot protocol (oyster)

1. Lock brief template, model/baseline version, and operating threshold *T* before day 1.
2. Issue daily 72h brief by a fixed UTC time. Store snapshot.
3. Grower files a 30-second outcome: mortality band, workability (worked as planned / delayed / cancelled), intervention (y/n), optional sensor export.
4. After each 72h window, score alerts vs labels. No retroactive threshold fishing.
5. Weekly internal scorecard. No public “accuracy %” marketing.
6. Red-team reviews one week of briefs for food-safety language leakage.

#### Hypothesized go / no-go (oyster)

See `go_no_go_scorecard.md` for the unified card. Candidate-specific **hypotheses**:

| Result | Hypothesis threshold |
| --- | --- |
| GO (pilot superiority claim) | Recall ≥ **0.60** at precision ≥ **0.40**; false alerts ≤ **3 / farm-month**; median lead time ≥ **12 h** on lead-time-eligible events; Brier skill vs seasonal baseline ≥ **0.10**; expert-rule also beaten on recall-at-precision **or** on false-alert-adjusted decision value |
| CONDITIONAL | Recall 0.45–0.60 with false alerts ≤ 3 and qualitative grower action; or skill only in one basin |
| NO-GO / stop model complexity | After **two major iterations**, recall < **0.40** at precision 0.40, **or** false alerts > **6 / farm-month**, **or** no beat of expert-rule on BSS and recall, **or** growers will not log outcomes |

---

### 4.2 Candidate B — Chinook × CA/OR coast × 24–48h relative encounter

| Field | Specification |
| --- | --- |
| Species | Chinook salmon (*Oncorhynchus tshawytscha*) |
| Geography | Bounded CA/OR coastal ocean. Spatial grain for product: **~10 km cell** (H3 resolution to be locked with geospatial engineer; CDFW 1′ blocks are too fine to publish). Evaluation may use coarser RecFIN/CRFS districts for public-data baselines. |
| Customer | Charter / CPFV captain |
| Horizon | 24–48 hours |
| Cadence | Daily (afternoon-before / morning-of), only during **open** salmon recreational seasons |
| Product type | **Occurrence / relative encounter ranking** |
| Contract category | **D** as the user-facing claim, evaluated against **C** (effort-normalized catch/no-catch). Not abundance. Not a catch guarantee. Not navigation, weather-safety, or license advice. |
| AIS / VMS | **Never a label. Never an abundance proxy.** May be used, if rights-approved, only as a **privacy-sensitive effort-coverage diagnostic** (where people fished), never as “fish are here.” Default: do not ingest AIS for this wedge unless red-team and rights both pass. |

#### Recommended primary target label (hypothesis)

**`encounter_48h` ∈ {0,1}** for a standardized charter trip-cell.

Positive if the trip records **≥1 Chinook** kept **or** released (all dispositions), given:

- species confirmed as Chinook (not “salmon unk” unless a documented mapping rule exists)
- effort recorded: **angler-hours** (preferred) or anglers × hours
- spatial cell of **primary fishing effort** (captain-provided coarsened cell; not a public GPS heatmap)
- trip occurs in an **open** management cell/day (closed days are out of universe, not zeros)

**Secondary:** `cpue_chinook = count / angler-hours`; `top_quintile_cell` among cells fished that day in the study area.

**Do not** use monthly RecFIN/CRFS CPUA as the 24–48h label. Those series are the **seasonal-spatial baseline and a covariate of interannual run strength**, not the product target.

Public lawful CPUE that **may** support baseline / context (not the 24–48h label):

- CDFW CRFS / Ocean Salmon Project; CPFV logbooks (mandatory, monthly submission) — https://wildlife.ca.gov/Conservation/Marine/CRFS/Background
- RecFIN comprehensive recreational catch estimates (CRFS, ORBS, WDFW OSP) — NOAA InPort item 55977
- CDFW Open Data salmon catch-per-unit-angler by 1′ block, multi-year aggregates (too coarse in time for 24–48h) — CA Open Data ds3184

**Partner charter logs are required** for a 24–48h product. Public monthly district estimates cannot validate a 24–48h claim.

#### Ground truth

| Source | Role | Evidence tier | Bias |
| --- | --- | --- | --- |
| Partner charter / CPFV structured catch + effort | **Primary 24–48h label** | 2 | Skill, targeting, weather cancellation, reporting |
| Lawful public CRFS/RecFIN/ORBS CPUA | Baseline, season context, interannual index | 2 | Mode mixing, delayed estimates, coarse space/time |
| CPFV official logbooks (if license + DUA allow) | Additional C-tier labels | 2 | Monthly lag; compliance |
| Dock sampling / OSP | Context, not daily cell labels | 1–2 | Sampled days only |
| AIS | **Forbidden as abundance / encounter label** | — | Effort ≠ fish |

#### Minimum ground-truth dataset (hypothesis)

**Retrospective:**

- ≥ **400** partner trips with catch/no-catch + effort spanning **≥2 open seasons**
- ≥ **3** independent vessels (not one captain’s notebook)
- Both CA and OR only if the locked geography includes both; otherwise do not claim transfer
- Zero-catch trips **retained**
- For AUROC discrimination vs 0.50 at hypothesized AUC 0.65, prevalence ~0.30: on the order of **~200+ independent trips** is a lower bound (Hanley & McNeil 1982-style ROC sample-size logic). For **comparing** two models differing by ~0.05 AUC, n is much larger (**hypothesis: ≥600** labeled trips before advanced ML is justified)
- Public RecFIN/CRFS monthly series: ≥ **8 years** for seasonal baseline, with management-season flags (open/closed)

**Prospective:**

- ≥ **3** charter partners
- ≥ **80** issued trip-briefs with subsequent outcome logs in one open season (hypothesis)
- Outcome completion ≥ **60%** of issued briefs (zeros required)

If the recreational Chinook season is closed in the study area, the candidate is **out of universe** (pause), not a model failure.

#### Spatial / temporal splits

- Time-forward by week within season; train prior weeks, predict next 48h.
- Out-of-year: leave-one-year-out **mandatory** (Chinook ocean abundance is strongly interannual; a model that memorizes “2022 was good” will fail).
- Out-of-season: not applicable inside a short opener except early vs late season blocks.
- Spatial holdout: leave-one-CRFS-district or leave-one-port-complex; block size ≥ residual SAC, hypothesized **20–50 km**.
- Transfer: train CA, test OR (only if both are in-scope).
- **Never** put the same vessel-day’s adjacent cells in both train and test.

#### Primary metric

**Primary:** **PR-AUC lift vs seasonal-spatial baseline** (prevalence-aware), plus **top-20% zone lift** among cells that were actually fished (avoid rewarding empty-ocean ranking).

**Co-primary for probabilities:** Brier skill score vs seasonal-spatial baseline; calibration ECE ≤ hypothesized 0.08 on the prospective set.

**Secondary:** AUROC (report; not sufficient alone), recall/precision at product threshold, Spearman rank of `cpue` vs predicted score, NDCG@k.

**Effort rule:** evaluate only on trips with known effort. Do not treat unfished cells as true negatives unless a documented presence-absence survey exists (it does not). Ranking metrics among **visited** cells are the honest product metric; occupancy maps of the whole EEZ are out of scope.

#### Baseline that must be beaten

**Primary baseline to beat:** **spatial × month historical encounter rate** (and CPUA) from partner logs if n allows, else CRFS/RecFIN port-area × month, downscaled only with an explicit, leak-free method.

**Also required:** persistence (“yesterday’s best cell / last successful trip”); simple expert SST/season rule; customer current workflow if captains log intended grounds before seeing the brief.

#### Prospective pilot protocol (Chinook)

1. Pre-register: universe = open salmon-legal days only; cells = coarsened 10 km; threshold or rank card.
2. Deliver brief **T−18h to T−6h** before typical departure. Captains record **intended** grounds **before** opening the brief (workflow baseline).
3. After the trip: catch/no-catch, count band, angler-hours, coarsened cell, weather abort (y/n). Weather aborts are **censored**, not zeros.
4. Score encounter classification and ranking among cells fished by the partner set that day.
5. Prohibit publishing heatmaps of exact productive locations.

#### Hypothesized go / no-go (Chinook)

| Result | Hypothesis threshold |
| --- | --- |
| GO | Prospective PR-AUC ≥ baseline + **0.08**; AUROC ≥ **0.65**; Brier skill ≥ **0.05**; top-20% visited-cell lift ≥ **1.30**; ECE ≤ **0.08**; no AIS-as-abundance anywhere in the pipeline |
| CONDITIONAL | Skill in one district/year only; or ranking lift without calibration |
| NO-GO | After two major iterations, AUROC < **0.55** **or** no PR-AUC/Brier lift vs spatial-month baseline **or** captains will not log zeros **or** product language drifts to catch guarantee |

---

### 4.3 Candidate C — American lobster × Gulf of Maine × next-trip expected CPUE

| Field | Specification |
| --- | --- |
| Species | American lobster (*Homarus americanus*), GOM/GBK stock context |
| Geography | Bounded Gulf of Maine statistical areas / Maine lobster zones. Spatial grain: **10-minute square (TMS)** as the public/harvester reporting unit; product may coarsen further. Do not publish exact trap GPS. |
| Customer | Commercial lobster operator |
| Horizon | **Next trip** (typically 1–3 days; soak-adjusted) |
| Cadence | Per-trip or daily during active fishing |
| Product type | **Continuous / ranked CPUE** |
| Contract category | **C — effort-normalized catch index**. Not stock abundance. Not a quota recommendation. Not AIS-implied biomass. |

#### Recommended primary target label (hypothesis)

**`cpue_next_trip` = legal lobster catch / standardized effort**

Preferred unit: **pounds (or count of legal lobsters) per trap-haul**, with soak-time normalization:

`cpue_soakadj = catch / (trap_hauls × f(soak_hours))`

where `f` is a locked saturating function (hypothesis: cap soak credit at **24–48 h** so multi-day soaks do not look like higher productivity). Exact `f` is a domain+data decision, frozen before training.

**Secondary:** `P(trip CPUE in top quartile of that vessel’s own history for the same month × zone)`.

**Universe:** trips with traps hauled > 0. Negative reports (no activity) are not CPUE zeros.

#### Ground truth and reporting bias (required handling)

Official programs (existence cited; access and commercial-use rights **not** assumed approved):

- Maine DMR 100% electronic trip-level harvester reporting for commercial lobster licenses effective **2023-01-01**; due by the **10th of the following month**. Elements include traps hauled, soak, pounds, primary statistical area, lobster zone, and **one 10-minute square** (the area fished most that day) — DMR Chapter 8 Landings Program; DMR news 2023-01-03; 2023 e-reporting FAQ.
- ASMFC Addendum XXVI (100% harvester reporting timeline; 10-minute square spatial resolution).
- Federal eVTR for federal lobster permits (electronic VTR required beginning **2024-04-01**, NOAA Fisheries lobster resources).
- ASMFC 2025 benchmark: GOM/GBK not depleted but experiencing overfishing; landings off 2012–2018 highs — context for **non-stationarity**, not a label.

**Bias controls (must be in the evaluation spec, not a footnote):**

| Bias | Control |
| --- | --- |
| **One TMS per trip** (primary area only) | Treat TMS as noisy location; do not claim sub-TMS skill; optional partner multi-TMS logs |
| **Monthly reporting lag** | Official microdata **cannot** be a same-week feature for other vessels. Partner same-day logs can. Vintage all agency files. |
| **High-liner vs average** | Slice metrics by vessel-CPUE quartile; evaluate a **new-vessel** holdout; do not train only on top producers if the product is sold to a mixed fleet |
| **Dealer vs harvester mismatch** | Prefer harvester effort-normalized catch; dealer landings without effort are **not** CPUE |
| **Gauge / vent changes** (Addendum XXVII triggered 2023) | Segment pre/post management-measure eras; do not pool CPUE as if comparable |
| **Soak / total gear in water** | Always model effort; raw pounds is rejected as a label |
| **Confidentiality / suppression** | Follow agency aggregation rules; private by default at vessel grain |
| **AIS** | Effort context at most; **never** abundance |

**Partner electronic logbooks** (VESL-like or in-app) with same-day catch + trap-hauls + soak + coarsened cell are the only path to a true **next-trip** label with low latency.

Public 10-minute-square monthly CPUE, if licensed, supports **seasonal-spatial baselines** and out-of-year tests, not a same-week forecast claim.

#### Minimum ground-truth dataset (hypothesis)

**Retrospective:**

- ≥ **2,000** trip-level trap-haul CPUE records
- ≥ **2** calendar years in the **post-2023 100% reporting** era (comparability)
- ≥ **3** statistical areas or **≥2** lobster zones
- Effort fields non-null on ≥ **95%** of rows used
- Partner path (preferred for next-trip): ≥ **8** vessels × **2** seasons of trip logs with outcome latency ≤ **48 h**

**Prospective:**

- ≥ **8** vessels
- ≥ **400** issued next-trip forecasts with realized CPUE
- Completion ≥ **70%** of issued forecasts

To detect a **15% MAE reduction** vs persistence given high CV of trip CPUE, hypothesized evaluation n is **≥400–800** trips. Below 400, only rank-lift pre-tests, not a go for “better CPUE forecast.”

#### Spatial / temporal splits

- Time-forward by week; next-trip prediction may use that vessel’s history up to the previous trip.
- Out-of-year: leave-one-year-out, with gauge-size era flags.
- Spatial: hold out lobster **zones** or clusters of TMS; block size hypothesized **30–60 km** or full zone.
- Vessel holdout: ≥1 entire vessel never seen in training (skill transfer).
- Do not split hauls from the same trip across train/test.

#### Primary metric

**Primary:** **Spearman rank correlation** between predicted and realized soak-adjusted CPUE, **and** **top-quartile lift** (mean realized CPUE in predicted top quartile / mean in the rest), **and** **MAE on log1p(CPUE)** vs persistence.

Ranking is co-primary because the decision is *where/whether to set*, not the exact pound forecast.

Secondary: RMSE, pinball/quantile loss, 80% interval coverage, NDCG@k TMS list, effort-normalized uplift vs baseline.

#### Baseline that must be beaten

**Primary baseline to beat (co-primary):**

1. **Persistence:** that vessel’s last comparable-gear trip CPUE in the same TMS (or zone if TMS sparse)
2. **Spatial × month historical average** CPUE (soak-adjusted) for that TMS

The advanced model must beat **both** on the agreed primary pair (rank **or** MAE, pre-registered) in prospective evaluation. Beating only persistence in a strong seasonal ramp, or only climatology in a noisy week, is CONDITIONAL.

Also: expert-rule (depth band × month × zone); customer workflow (intended TMS logged before the brief).

#### Prospective pilot protocol (lobster)

1. Pre-register effort definition, soak function, quartile definition (global vs vessel-specific — **vessel-specific recommended** to avoid punishing smaller boats).
2. Issue next-trip expected CPUE **band** + rank of candidate TMS + confidence. No exact-spot map.
3. Operator logs: TMS (or coarsened cell), trap-hauls, soak, pounds/count, weather abort.
4. Score only trips that hauled gear. Compare to persistence and climatology.
5. Privacy: vessel-level outcomes PRIVATE; public research uses agency-approved aggregates only.

#### Hypothesized go / no-go (lobster)

| Result | Hypothesis threshold |
| --- | --- |
| GO | Spearman ρ ≥ **0.35**; top-quartile lift ≥ **1.20**; MAE_log1p ≤ **0.85 × persistence MAE** (i.e. ≥15% reduction) **and** ≤ climatology MAE; 80% PI coverage in **0.70–0.90**; bias slices (high-liner vs others) do not reverse the sign of lift |
| CONDITIONAL | Rank lift without MAE lift, or skill only in one zone/season, or only on high-liners |
| NO-GO | After two major iterations, neither MAE nor rank beats **both** persistence and spatial-month average; **or** only dealer landings without effort exist; **or** AIS used as abundance; **or** operators will not report effort |

---

## 5. Prospective pilot — shared operating rules

These apply once a wedge is locked and Gates 1–8 pass.

### 5.1 Pre-registration (written before first issuance)

- target definition and exclusions
- baseline versions
- operating threshold(s) or rank-k
- primary metric and slices
- sample-size stop/go hypotheses
- what would falsify the product
- privacy / coarsening rules
- food-safety / navigation / catch-guarantee prohibition language

### 5.2 Per-forecast lock

For each issued forecast store the full as-of bundle (project §11 fields). **Never overwrite.** Corrections are new records.

### 5.3 Outcome collection

- 30-second form; zeros and no-work days required
- consent version on every submission
- missing outcomes counted (completion rate is a go/no-go metric, not just a data-quality footnote)

### 5.4 Analysis discipline

- Primary analysis is intent-to-score on all issued forecasts with outcome **or** a documented censor (weather abort, season closure)
- No threshold re-tuning on the pilot
- One pre-registered subgroup analysis (e.g. Hood Canal vs other; early vs late salmon season; inshore vs mid-coast lobster)
- Human qualitative: did the user **do something different**? Binary, logged

### 5.5 What “prospective” forbids

Using the pilot outcomes to select features and then reporting that same pilot as confirmation. Confirmation requires a **new** time window or a pre-registered freeze.

---

## 6. Failure taxonomy (required on every evaluation report)

When skill is absent or drops, classify as one or more of:

1. label issue  
2. data quality issue  
3. insufficient outcome data  
4. spatial resolution mismatch  
5. temporal resolution mismatch  
6. feature latency / leakage  
7. sampling bias  
8. reporting bias  
9. geography shift  
10. seasonal shift  
11. climate anomaly  
12. biological mechanism missing  
13. model selection issue  
14. product decision mismatch  
15. user behavior mismatch  
16. wrong customer / use case  

For each: document, quantify, decide fixable vs stop, pick the smallest next experiment.

---

## 7. Unified scorecard usage

After a wedge is selected, fill `forecast_scorecard_template.md` and `go_no_go_scorecard.md` on every iteration. Until then, use the **candidate comparison panel** in `go_no_go_scorecard.md` §2 (validation feasibility only — not a product pick).

**Orchestrator rule:** this protocol may be marked `APPROVED_AS_DESIGN` while Gate 1 is open. It may not be marked `APPROVED_FOR_TRAINING` until Gates 1–8 pass for the locked wedge.

---

## 8. Uncertainty (summary)

Full rules: `uncertainty_policy.md`.

No customer-facing output may ship as a single opaque score. Minimum visible bundle:

- confidence category (high / medium / low) with **reasons**
- interval or qualitative uncertainty rationale
- input freshness
- observation density
- missing-data state
- extrapolation flag
- known limitations

Validation must test that “high” is actually more reliable than “low.” If it is not, the confidence model is failed even if AUROC looks fine.

---

## 9. Source notes for this protocol (methods and programs, not performance)

| Source | Owner | URL or ID | Access date | Use | License / rights (this agent) | Evidence tier |
| --- | --- | --- | --- | --- | --- | --- |
| WA DOH Shellfish Growing Areas | Washington State Department of Health | https://doh.wa.gov/community-and-environment/shellfish/growing-areas | 2026-09-18 | Closure = context; classification process | Public government information; commercial reuse **HUMAN LEGAL REVIEW** if redistributing GIS | 1 (authority process) |
| WA DOH commercial growing area closures portal | WA DOH | https://fortress.wa.gov/doh/eh/portal/odw/si/GrowingAreaClosures.aspx | 2026-09-18 | Biotoxin/commercial harvest context | Same | 1 |
| WA Sea Grant Rapid Response Network | Washington Sea Grant | https://waseagrant.uw.edu/our-programs/seafood-fisheries-aquaculture/aquaculture/rapid-response-network/ | 2026-09-18 | Mortality-event monitoring context | Public page; forms not a GT substitute | 2–4 |
| CRFS Background (CPFV logs, OSP) | CDFW | https://wildlife.ca.gov/Conservation/Marine/CRFS/Background | 2026-09-18 | Lawful public catch/effort architecture | State survey; log microdata rights **CONDITIONAL** | 2 |
| RecFIN comprehensive rec catch estimates | PSMFC / NMFS | https://www.fisheries.noaa.gov/inport/item/55977 | 2026-09-18 | CA/OR/WA rec estimates | InPort metadata; dataset license **REVIEW** | 2 |
| CRFS salmon CPUA 2004–2024 | CDFW Open Data ds3184 | https://lab.data.ca.gov/dataset/california-recreational-fisheries-survey-catch-per-unit-angler-for-salmon-r7-2004-2024-cdfw-ds3 | 2026-09-18 | Coarse CPUA baseline | CA Open Data terms **REVIEW** | 2 |
| RecFIN-MRIP Regional Implementation Plan 2023 | NMFS / PSMFC | https://www.fisheries.noaa.gov/s3/2023-09/RecFIN-2023-Regional-Implementation-Plan.pdf | 2026-09-18 | CRFS/ORBS/OSP methods | Public PDF | 2 |
| ME DMR 100% lobster e-reporting | Maine DMR | https://www.maine.gov/dmr/news/tue-01032023-1200-new-reporting-requirement-commercial-lobster-license-holders | 2026-09-18 | GT existence / lag | Public notice; **microdata not open** | 2 |
| ME DMR Chapter 8 Landings Program | Maine DMR | https://www.maine.gov/dmr/sites/maine.gov.dmr/files/inline-files/Chapter08_RR011012022.pdf | 2026-09-18 | Required fields: traps, soak, TMS | Regulation | 1 (legal requirement) |
| ASMFC American lobster | ASMFC | https://asmfc.org/species/american-lobster/ | 2026-09-18 | Stock/reporting context | Public | 2 |
| NOAA American lobster resources | NOAA Fisheries | https://www.fisheries.noaa.gov/species/american-lobster/resources | 2026-09-18 | eVTR 2024-04-01; stock status | Public | 2 |
| Cheney et al. 2000 summer mortality | JSR | bibliographic | 2026-09-18 | Multi-stressor rationale | Copyrighted paper; cite, do not copy | 1–2 (science) |
| Spatial block CV (Roberts 2025; arXiv:2502.03480; blockCV) | various | URLs in text | 2026-09-18 | Why not random CV | Open/publisher | methods |

**Rights status for all of the above as training data: not granted by this agent.** DATA_RIGHTS_AND_PRIVACY_AGENT owns the register.

---

## 10. Protocol approval checkbox

| Item | Status 2026-09-18 |
| --- | --- |
| Definitions of better data / better forecast written | YES |
| Three candidate labels proposed | YES — hypotheses |
| Splits specified | YES — not yet generated (no data ingest) |
| Prospective pilots specified | YES |
| Numeric thresholds | HYPOTHESIS only |
| Wedge locked | NO — Gate 1 open |
| Approved for advanced ML | **NO** |

**Next required human/orchestrator action:** lock wedge (or explicitly keep researching), then run Gate 3 (ground truth in hand) before any training.
