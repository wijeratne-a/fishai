# Validation protocol — Global Saltwater Life Observatory

**Agents:** MODEL_VALIDATION_AND_UNCERTAINTY_AGENT (lead), with PHYSICS_AND_FEASIBILITY_RED_TEAM_AGENT + SCIENTIFIC_PEER_REVIEW_RED_TEAM_AGENT  
**Date:** 2026-09-18  
**Version:** `OBS-VAL-PROTOCOL-2026-09-18-v1`  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/validation_protocol.md`  
**Status:** Design only. No observatory products issued. No models trained. No bulk ingest.  
**Does not overwrite:** `/Users/wijeratne/dev/fishai/artifacts/quality_and_validation/validation_protocol.md` (FishAI wedge protocol). This file is the **observatory-scale** acceptance test. Where a locked FishAI wedge exists, **both** protocols apply; the stricter gate wins.

**Numeric thresholds:** **HYPOTHESES** until pre-registered on the first honest retrospective. They are not performance claims.

**Species support tiers T0–T6** are defined in `global_species_registry/support_tier_framework.md` (binding). This protocol does **not** invent a second 0–6 ladder. It specifies the **validation evidence required to assign or keep** those tiers. **T6 = operational grade.**

Related observatory files (read, not overwritten):

- `global_species_registry/support_tier_framework.md` — T0–T6 meanings
- `observation_modality_catalog.md` — DIRECT/INFERRED/FORECAST/NEEDS_INFRA/UNPROVEN/SPECULATIVE/IMPOSSIBLE
- `physics_feasibility_reports/physical_limits.md` — hard stops; `PHYSICALLY_UNLIKELY`
- `scientific_red_team_reports/observatory_red_team_01.md` — leakage, false claims, peer review
- `sensitive_location_policy.md` — `DELAYED` / `NEVER_PUBLISH`; global public life map rejected
- `artifacts/validation_redteam/agent_handoff.md` — return payload

Related FishAI siblings (read-only): `artifacts/quality_and_validation/**`, `artifacts/scientific_red_team/**`, `artifacts/geospatial_data_engineer/as_of_replay_design.md`, `artifacts/geospatial_data_engineer/canonical_data_model.md`.

---

## 0. Purpose

No observatory estimate is accepted because it looks plausible, is spatially complete, or is labeled “AI.”

This protocol defines:

1. The **evidence contract** every estimate must carry (including **UNKNOWN** / `UNKNOWN/INSUFFICIENT DATA`).  
2. How validation **V1–V9** maps onto species support **T0–T6**, with **T6 = operational**.  
3. Tests that can **fail** a model: historical / spatial / temporal holdout; independent sources; simple baseline; literature; ecological plausibility; calibration; adversarial review.  
4. The rule: **if it does not beat the locked simple baseline on honest evaluation, it is NOT READY FOR USE** as a forecast or biological nowcast (framework T6 text). Packaging a winning baseline honestly is allowed (same rule as FishAI `baseline_model_spec.md` §9).

It does **not** authorize a global product. FishAI remains one species × one geography × one customer × one decision until the founder locks a wedge.

---

## 1. Evidence contract (mandatory on every estimate)

An “estimate” is any number, rank, heatmap cell, occupancy flag, acoustic NASC, eDNA detection, tag location, or fused score shown to a user **or** stored as if it were a fact.

If any required field is missing, the estimate is **invalid** and must not be displayed as knowledge. Prefer:

> **UNKNOWN: not enough evidence.**

Do not interpolate, inpaint, or spatially smooth across UNKNOWN cells to manufacture coverage (`physical_limits.md` PX-20; scientific red team RT-XCUT-09).

### 1.1 Required fields

Align names with the observation kernel (`artifacts/geospatial_data_engineer/schemas/_ObservationKernel.schema.json`) plus observatory extensions.

| Field | Meaning | Forbidden substitute |
|---|---|---|
| `observed_at_utc` | When the **phenomenon** occurred (or window start) | Using `issued_at` as if it were observation time |
| `published_at_utc` / `available_at_utc` | When this **version** could have been used | Delayed-mode GHRSST/chlorophyll treated as NRT |
| `issued_at_utc` | When *we* emitted the estimate | Silent overwrite of past issuances |
| `latency` | `issued_at − available_at` of the limiting input, plus biological latency (eDNA decay window, tag pop-up, acoustic processing) | “Real-time” without a number |
| `geographic_precision` | Native + public grain; `geographic_uncertainty_meters`; H3 res; official unit | 100 m heatmap from a 4 km ocean-color pixel |
| `depth_precision` | Meters positive down; vertical validity (skin, mixed layer, bottom, unknown) | SST as 3-D habitat |
| `evidence_type` | Sensor class: optical satellite, in situ, active acoustics, passive acoustics/DAS, eDNA, tag, catch/effort, survey, model, unverified | “AI fused observation” |
| `evidence_tier` | T1 direct / T2 operational / T3 remote or modeled / T4 unverified (FishAI hierarchy) | Stacking T3 until it looks like T1 |
| `prediction_contract_category` | A–E (`prediction_contract.md`) | Habitat sold as count |
| `provenance` | `source_id`, `source_record_id`, URL/DOI, license, transform hash | Stripped basemap |
| `model_or_baseline_version` | id + training cutoff + code hash | “the model” |
| `uncertainty` | Interval **or** `uncertainty_rationale`; confidence High/Medium/Low/**None** | Lone 0–100 score |
| `legal_privacy_tier` | PUBLIC / COARSENED / RESTRICTED / PRIVATE / NEVER_PUBLISH | Fine public spots |
| `ecological_sensitivity` | listed stock, nursery, mammal, harvest-sensitive | Silent |
| `limitations[]` | What this estimate is **not** | Disclaimer under a go-fish map |
| `unknown_flag` | true if evidence insufficient | Filling the globe |
| `output_class` | Exactly one of: `DIRECTLY OBSERVED` \| `REMOTELY DETECTED` \| `SURVEY-DERIVED` \| `TAG/TELEMETRY-DERIVED` \| `OPERATIONALLY OBSERVED` \| `MODEL-INFERRED` \| `FORECAST` \| `HYPOTHETICAL/RESEARCH MODE` \| `UNKNOWN/INSUFFICIENT DATA` (`README.md`) | Mixing classes in one colormap |
| `support_tier` | T0–T6 for taxon × stage × geography | Upgrading because the taxon is commercially interesting |

### 1.2 Confidence labels (only these)

Reuse FishAI `uncertainty_policy.md` vocabulary, plus **None** and **UNKNOWN**.

| Label | Meaning for observatory |
|---|---|
| **High** | Recent local **verified** T1/T2 outcomes, in-domain, sources healthy, last **prospective** slice calibrated |
| **Medium** | Adequate environment, sparse biology, or mild domain excursion |
| **Low** | Missing critical input, novel climate/management era, outage, or uncalibrated modality |
| **None** | Do not issue a biological score; context-only |
| **UNKNOWN** | Cell/time not sampled at the claimed grain; **not** a zero |

**High is illegal** when: only T3 inputs exist; spatial gap-fill was used; independent-source test failed; baseline was not beaten; fouling/service date unknown for in situ; eDNA lacks assay metadata; acoustics uncalibrated.

Do not print three-decimal probabilities until a human reviewer accepts a **prospective** reliability diagram.

### 1.3 UNKNOWN policy (non-negotiable)

| Situation | Required output |
|---|---|
| No sample in cell at claimed grain | `UNKNOWN`, hatched / blank, not zero |
| Sample exists but assay/calibration failed | `UNKNOWN` + quality flag |
| Model extrapolated outside training envelope | `Low` or `None` + `extrapolation_flag=true`; if no analog year, **UNKNOWN** |
| Coverage fraction of AOI sampled \< locked threshold | Publish **coverage map**; forbid “global” language |
| Independent sources disagree beyond tolerance | `UNKNOWN` or `Low` with conflict note; do not average them into fake certainty |

**Do not manufacture confidence in sparse cells.** Shrinkage toward a climatology is allowed **only** if the product is labeled climatology (B12), not “observed life.”

---

## 2. Species support tiers T0–T6 (validation mapping)

Use the framework names. A tide gauge can be T6 for **water level** and T0 for **fish abundance**. Promotion is per **taxon × life-stage × geography × claimed output**. Example CSV rows in iteration 1 are **T0–T2 only**; T3–T6 assigned count is **0** (`support_tier_framework.md`).

| Support tier | Honest meaning (framework) | Validation required before this observatory may **emit** that class |
|---|---|---|
| **T0** | Taxonomy only | WoRMS identity. No distribution product. Output: `UNKNOWN/INSUFFICIENT DATA`. |
| **T1** | Historical occurrence | Compiled records with provenance; effort bias stated; **no** current-presence language. V3 (independent source) recommended. |
| **T2** | Habitat suitability | T1 + mechanistic envelope (literature V5). **Forbidden:** “animals are here now.” Physics PX-05. |
| **T3** | Current condition estimate | V1 temporal + V2 spatial holdout at claimed grain; V3 independent source; V6 ecology; V9 physics. Habitat maps **do not** auto-promote. Stock-assessment terminal year **≠** T3 spatial grid. |
| **T4** | Short-horizon forecast | T3-quality state + V1/V2/V4 (**must beat baseline**) + V7 calibration. Climatology labeled as climatology stays T1/T2, not T4. |
| **T5** | Direct observation / telemetry | Lawful recent observation or tag with latency/error; individual ≠ population; `NEVER_PUBLISH` if sensitive (`sensitive_location_policy.md`). No interpolating tracks into a census. |
| **T6** | **Operational grade** | **All of §7.** T4 or T5 as claimed **plus** prospective beat of baseline, rights, resilience, outcome loop, red-team, human sign-off. |

**Today (2026-09-18):** observatory biological **emissions** are T0–T1 (catalog). No T3–T6. FishAI commercial forecasts are **not started**. Environmental **authoritative** feeds (NWS, CO-OPS) may be **linked as official context** without claiming them as observatory biology.

**Do not upgrade** oyster, Chinook, or lobster to T3–T6 because a product team is researching them (`README.md`).

---

## 3. Universal tests V1–V9 (all biological or fused estimates)

Numbered **V*** so they are not confused with support tiers **T0–T6**. Run in this order. A later “pass” does not erase an earlier fail.

### V1 — Historical / temporal holdout (time-forward)

- Train only on data with `published_at ≤ issued_at`.  
- Expanding or sliding windows.  
- **Leave-one-year-out** required for any product that might memorize a good year (Chinook run strength; marine heatwaves; lobster reporting-era breaks).  
- Out-of-season test when the label is seasonal.  
- **Fail if** skill exists only in-sample or only when delayed-mode / revised fields are used (`as_of_replay_design.md` honest vs corrected lanes).

### V2 — Spatial holdout and autocorrelation

- Block by residual SAC range of the **seasonal baseline**, or by official unit (growing area, PFMC area, lobster zone), whichever is **larger** (Roberts-class spatial CV; FishAI `validation_protocol.md` §3.2).  
- Adjacent H3 cells on the same day are **not** independent.  
- Geographic transfer (train basin A, test basin B) is **required** before any cross-region claim.  
- **Fail if** random row splits were used, or if neighbors leak the same water mass.

### V3 — Independent source

At least one of:

- a different **modality** (e.g. acoustics vs catch; eDNA vs visual/BRUV; farm mortality vs sensors **if sensors are not the label**),  
- a different **institution**,  
- a held-out **partner** never in training.

**Fail if** the only “validation” is another transform of the same raster (chlorophyll vs Kd vs nFLH).

### V4 — Simple baseline (must beat)

Lock **before** advanced models, from the FishAI family:

| ID | Family |
|---|---|
| B12 | Seasonal × spatial climatology |
| B3 | Persistence / last observation |
| B4 | Transparent expert rule (physics-allowed covariates only) |
| B5 | User’s pre-brief intended action (prospective) |

`relevant_baseline` = strongest of {B12, B3, B4} on the first time-forward retrospective, then **frozen**.

**Rule:** After **two major model iterations**, if the model does not beat `relevant_baseline` on the primary metric in **time-forward and spatial** evaluation, **NOT READY FOR USE** as a forecast. Stop complexity. Ship the baseline **as a baseline** or stop.

A model that only restates “July is better than January in this port” is a climatology. Call it that.

### V5 — Literature consistency

- Mechanism must exist in peer-reviewed or official science at the **same stage, depth, and horizon**.  
- Juvenile chlorophyll–presence papers do not validate adult 48 h encounter (Hassrick 2016 vs charter Chinook).  
- **Fail if** the only citations are marketing or wrong-scale ecology.

### V6 — Ecological plausibility

Domain checklist (must be signed, not “the AI learned it”):

- Life stage and phenology match the label.  
- Vertical habitat possible (Hinke thermal refuge).  
- Catchability vs density separated (Harley 2001; lobster bottom T).  
- Zeros: unfished / unsampled ≠ absent.  
- Predators, molt, emersion, gear saturation not ignored if they dominate.  
- **Fail if** the map contradicts known closures, land, or lethal physics without a documented exception.

### V7 — Calibration

- Reliability diagrams / ECE for probabilities.  
- Interval coverage if intervals are printed (80% interval must cover ~0.70–0.90 in the current slice or **stop printing it** — FishAI `uncertainty_policy.md`).  
- High-confidence issuances must be **more accurate** than Low; if not, the confidence system **fails** even if AUROC looks fine.  
- **Fail if** >95% of cells are High, or if sparse cells are High.

### V8 — Adversarial / red-team review

Minimum attacks (full list in `observatory_red_team_01.md`):

1. Temporal leakage (future composites, revised reanalyses, stock-assessment as 24 h feature).  
2. Spatial leakage / SAC.  
3. Learning **sampling effort** instead of biology.  
4. Learning **vessel behavior** instead of fish (AIS).  
5. Habitat suitability sold as **current presence**.  
6. Hotspot overfitting (month × place dummies).  
7. Climate-anomaly failure (2021 AHW; marine heatwave years).  
8. Hiding low coverage.  
9. False cross-species or cross-region transfer.  
10. Sensitive-location leak.  
11. Claims > evidence tier.  
12. Failure to beat seasonal average.

**This software agent cannot close HIGH/BLOCKER items.** A named human (fisheries scientist / acoustician / molecular ecologist as relevant) must sign.

### V9 — Physics gate

If `physical_limits.md` or `observation_modality_catalog.md` marks the claim `IMPOSSIBLE` / `PHYSICALLY_UNLIKELY`, the claim stays **T0** (or T2 habitat-only, if that is what the physics actually supports) until a written mechanism + measurement plan reverses that row. **No amount of holdout skill on a proxy label resurrects a wrong physical target** (SST-only “winning” on oyster mortality means the **labels are wrong** — RT-OYS-02).

---

## 4. Modality-specific gates (summary)

Details of physical ceilings: `physical_limits.md`. Validation extras:

### 4.1 Optical satellite / ocean color / SST

- Vertical validity = skin or first optical depth only.  
- Independent check: in situ radiometry or moorings, **not** another satellite in the same constellation family unless disclosed as non-independent.  
- Cloud/land/Case-2 flags must propagate to UNKNOWN.  
- **Never** a fish label.

### 4.2 Active fisheries acoustics

- Sphere calibration log; \(\alpha\) formula + water-mass; TS model citation; dead-zone fraction.  
- Species mixing: net/optical samples or multifrequency rule **pre-registered**.  
- Independent: biological sampling on the same survey.  
- Opportunistic hull data: Category E until the above exist.

### 4.3 eDNA

- Marker, primers, reference database **date**, blanks, LOD, inhibition.  
- Decay + transport kernel (even a crude one) or **no spatial claim finer than the plausible plume**.  
- Independent: visual, catch, or acoustic occupancy on a subset.  
- Reads ≠ biomass unless a calibrated production model exists (expected: it does not, for v0).

### 4.4 Tags

- Report Argos class / GPS error, duty cycle, pop-up programmed date, **surface-drift latency**.  
- n and selection bias in the limitation line.  
- Independent: fishery recapture or acoustic array, not the tag vendor dashboard alone.

### 4.5 DAS / passive acoustics

- Gauge length, sample rate, useful bandwidth vs range, detector precision/recall on a **labeled** subset.  
- Independent: hydrophone or visual/acoustic tag.  
- Listed-species detections: NEVER_PUBLISH at fine grain.

### 4.6 Catch / effort / AIS

- Effort definition required for Category C.  
- AIS is **never** a biological label (project non-negotiable).  
- Hyperstability test: CPUE vs survey index through a known decline, if data exist.

### 4.7 Fusion / “foundation ocean model”

Fusion is a **new model**. It inherits the **strictest** limitation of its inputs.  
**Fail immediately if** fusion output is higher category (A/B) than any contributing biological evidence, or if coverage is filled from T3 rasters.

---

## 5. Primary metrics (hypotheses)

Do not mix product types into one AUROC press release.

| Product type | Primary | Must also report |
|---|---|---|
| Occupancy / encounter | PR-AUC vs B12; visited-cell rank lift | Brier, ECE, coverage fraction, UNKNOWN rate |
| Risk / ops-stress | Recall @ locked precision; false alerts / site-month; lead time | BSS vs B12; vs B4 |
| CPUE / rate | Spearman + MAE vs **both** B3 and B12 | Interval coverage; high-liner slice |
| Acoustic index | Relative to survey design CV; bias vs nets | \(\alpha\) sensitivity; dead-zone |
| eDNA occupancy | Detection vs independent occupancy; not copy-number R² unless pre-registered | Blank rate; spatial plume width |

**Slices always:** season, subregion, depth band, observation density, freshness, extreme-event flag, platform. A global average that hides failure in the high-value season is a **fail** (FishAI protocol §3.4).

---

## 6. Prospective rules (shared with FishAI §5)

- Pre-register target, baseline, threshold, falsifiers, privacy coarsening.  
- Immutable issuance log (`forecast_id` never updated).  
- Outcomes including **zeros** and **no-work** days.  
- No threshold fishing on the pilot.  
- Confirmation requires a **new** time window after freeze.

---

## 7. Minimum bar for **T6 operational grade**

Framework T6 already requires: T4 or T5 as claimed, plus prospective validation, calibrated uncertainty, source resilience, documented rights, outcome feedback, and **beat a simple baseline or NOT READY FOR USE**.

This section binds that sentence. Missing any item ⇒ **not T6**. Do not assign T6 because the taxon is commercially important.

### 7.1 Scope lock

- Named taxon or explicitly **community** (not “life”).  
- Named geography with official units.  
- Named target, horizon, grain, universe (e.g. open-season only).  
- Prediction category C or D for public biology; A/B only as **attributed survey quote**.  
- Physics row not `IMPOSSIBLE`. Modality catalog class not `IMPOSSIBLE` for the claimed detection.

### 7.2 Data and rights

- Rights class `APPROVED_*` for every training/serving source.  
- Partner DUA if T1/T2 outcomes are private.  
- As-of timestamps on every feature.  
- Privacy reverse-engineering test passed (`privacy_and_sensitive_location_policy.md` §4.2).  
- Sensitive-species policy applied.

### 7.3 Validation (the user’s list, bound)

| Test | Operational requirement |
|---|---|
| V1 Historical / temporal holdout | ≥1 time-forward + ≥1 leave-one-year-out; honest as-of lane only |
| V2 Spatial holdout | Blocked CV; SAC documented |
| V3 Independent source | Documented agreement/disagreement table |
| V4 Simple baseline | **Beats frozen relevant baseline** on primary metric **prospectively** (or product **is** that baseline, labeled as such — then operational **climatology/rule**, not “AI observatory T6 forecast”) |
| V5 Literature | Mechanism memo at matching scale |
| V6 Ecological plausibility | Named human domain reviewer |
| V7 Calibration | Confidence reliability + interval coverage in lock-window |
| V8 Adversarial review | `observatory_red_team_01.md` HIGH/BLOCKER closed, bounded, or human-accepted |
| V9 Physics | Claim not `IMPOSSIBLE`; depth/latency match the modality |

### 7.4 Operations

- Coverage / UNKNOWN published, not hidden.  
- Drift monitor (covariate, label, performance, source health). Pause if rolling 28-day primary metric \(<\) baseline for **two consecutive weeks** (hypothesis, from FishAI protocol).  
- Biofouling/service metadata for in situ.  
- Named humans: fisheries scientist **and** (if acoustics) acoustician **and** (if eDNA) molecular ecologist — as applicable.  
- 14-field product contract on every user output (`prediction_contract.md`).  
- Stop-ship list live (food-safety, navigation, abundance, catch guarantee, closed-cell scores, spot maps).

### 7.5 Explicit non-goals at T6

T6 for a **Willapa 72 h ops-stress indicator** is **not** T6 for a global saltwater life map.  
T6 for **CO-OPS water level** is not T6 for fish.  
T5 tagged animals are **not** T6 population nowcasts.  
A global public animal atlas is **rejected** as v1 (`artifacts/rights_safety/agent_handoff.md`).

---

## 8. Failure taxonomy (required on every evaluation report)

Copy FishAI protocol §6, plus observatory codes:

17. physics mismatch (wrong band, depth, tracer)  
18. effort-as-biology  
19. coverage theater (smooth UNKNOWN)  
20. fusion category inflation  
21. independent-source conflict ignored  
22. fouling / calibration drift  
23. tag/eDNA latency treated as synoptic

---

## 9. Relation to FishAI wedge protocol

| If founder later locks… | Observatory protocol adds… |
|---|---|
| W1 oyster | Physics: air×tide not SST; never eDNA-as-mortality; coverage of leases not globe |
| W2 Chinook | Independent source ≠ RecFIN monthly as 48 h label; AIS attack mandatory |
| W3 lobster | Independent source ≠ AIS; bottom T vs SST; hyperstability slice |

Eight ML gates in `artifacts/quality_and_validation/go_no_go_scorecard.md` remain **closed** as of 2026-09-18. Observatory work **must not** open them. Cost/UI agents recommend P0 Willapa OSI-72 as the smallest honest twin (`artifacts/product_cost/agent_handoff.md`) — still **not T6** until this protocol’s §7 is actually scored.

---

## 10. Protocol approval checkbox

| Item | Status 2026-09-18 |
|---|---|
| Evidence contract written | YES |
| UNKNOWN allowed / required | YES |
| Species support T0–T6 mapped to tests | YES |
| Tests V1–V9 specified | YES |
| T6 minimum written | YES |
| Any biological layer T3–T6 | **NO** (framework assigned count 0) |
| Approved to train observatory foundation model | **NO** |

**Next required action:** do not collect a global ocean lake. If a wedge locks, run FishAI Gates 1–8 **and** observatory V1–V9 on **that** target only.
