# First-model feasibility — Atlantic goliath grouper

**Date:** 2026-09-23  
**Branch:** `integrate/globe-ux-2026-09-23`  
**This file is a feasibility note.** It is not a fitted model, not a current-location estimate, not a forecast, and not an abundance estimate.

**Project stage.** Data clearance before the first prediction model. The verified globe build remains a historical atlas: goliath status `no_estimate`, card `NOT_PUBLISHED`. That describes what is issued today. It is not the name of the next milestone.

**Next milestone.** Prediction MVP — Florida Keys Goliath Grouper Detection Nowcast.

Success for that milestone is a validated, calibrated probability of detection conditional on standardized Reef Visual Census effort, with explicit region, depth, time, and resolution limits. Observation, nowcast, and forecast stay separate layers. Sensitive sites stay undisclosed. A human-reviewed model card is required before any nowcast is issued. A map that merely looks predictive is not success.

The nowcast does not exist yet. A short forecast, initially 1–7 days, is a later step. It waits until the nowcast is stable, uses forecast environmental inputs, and states how skill degrades with lead time.

**Species.** Atlantic goliath grouper, *Epinephelus itajara*, WoRMS AphiaID 159353. Western Atlantic population as delimited by the accepted name. The eastern Pacific sister species is not included.

---

## 1. Prediction target

No target is authorized for fitting until the gates below are cleared. The target that the public survey design can support, if the file layout and rights checks succeed, is:

> Survey-season probability of detection of Atlantic goliath grouper during a standardized Reef Visual Census dive on a primary sample unit in the Florida Keys RVC region, within the depth interval recorded for that sample, conditional on the documented two-stage visual-survey protocol.

A monthly version of the same sentence is allowed only where the sample day is populated. The portal publishes year and day fields. This pass did not confirm that those fields are complete. FWC states that Keys surveys are generally conducted from April through September. Until the extract is checked, the time support is that **survey season attached to the sample year**, not a calendar month invented from a climatology.

### Target card

| Item | Definition |
|---|---|
| Species / population | *Epinephelus itajara*, AphiaID 159353. Fish that the RVC protocol would identify on a dive. Not eggs, not a separate genetic stock. |
| Region | Florida Keys region code in the RVC design. Dry Tortugas and southeast Florida stay available as later blocks in the same protocol. They are not pooled into one density. |
| Time interval | The RVC field season for that sample year. Month only if the event date is complete. |
| Depth range | The depth band recorded on the secondary sample unit. Do not substitute a FishBase maximum depth. |
| Spatial support | The RVC primary sample unit. Not a 1-degree OBIS cell. Not a point pin. |
| Unit of observation | One diver survey (secondary unit) nested in a primary sample unit. The design paper named by the portal is Smith et al. 2011. The nesting must be taken from that design before any fit. |
| Observation method | Two-stage stratified random stationary visual census, as operated by NOAA SEFSC and partners. |
| Presence | The species code `EPIITAJ` recorded with a count of at least one on that diver survey. |
| Non-detection | That code absent on a diver survey that is in the complete sample frame. This is protocol non-detection, not proof the species was absent from the reef. |
| Effort | The completed diver survey: stratum, visibility, and the protocol’s unit of search. Bottom time enters only if the approved extract actually contains it. |
| Target population | Reef habitat inside the Florida Keys RVC frame during the years and seasons sampled from 1999 onward, or from 2008 onward if the FWC collaboration is the rights-cleared slice. |
| Use case | A research prototype of detection given documented visual effort, compared with baselines, under spatial and time holdout. |
| Excluded use cases | Real-time tracking; exact location; abundance or biomass; catch probability; harvest or spear-fishing advice; “safe to dive” advice; spawning-aggregation maps; nursery maps; wreck guides; any globe layer labeled current or forecast. |
| Expected limitations | Detection is not occupancy of an individual. Divers miss fish. Visibility and depth change detection. Biennial sampling after 2014 leaves gaps. A sample unit that overlaps structure must not be published as a site. The model does not apply outside the RVC frame, including Brazil, the wider Gulf, or estuarine juveniles. |

### Targets that are not proposed

- “Where are goliath grouper right now?”
- A Gulf-wide or Atlantic-wide probability surface.
- A June artificial-reef count (Great Goliath Grouper Count) as a public map.
- A juvenile Ten Thousand Islands model. That would be a different gear, a different life stage, and a higher nursery risk. It can be reassessed only with an FWC inshore extract that contains zeros and an approved sensitivity review.
- Any use of the 332,628 OBIS rows as the likelihood.

---

## 2. Minimum baseline suite

No complex model is in scope until it beats all of these on the same holdout. None of them are fitted in this pass.

### 1. Seasonal climatology baseline

- **Inputs.** Detection/non-detection on approved RVC samples, plus the sample’s month or, if month is incomplete, the survey-season label.
- **Output.** The historical frequency of detection in that season, constant across space inside the Keys frame.
- **Evaluation.** Log-loss and Brier score on a time-forward holdout.
- **Why.** Stops a spatial model from taking credit for the fact that almost all dives happen in the same season.
- **Improvement.** Lower log-loss than this frequency, with calibration that is no worse.

### 2. Habitat-only baseline

- **Inputs.** The survey habitat code and stratum already on the sample. An external habitat map is optional and must be aggregated to the sample unit.
- **Output.** Detection frequency by habitat class.
- **Evaluation.** Same holdout. Classes with very few samples are pooled before scoring, and the pooling rule is fixed before looking at the test years.
- **Why.** Habitat suitability is the obvious simpler story. It is still not a sighting.
- **Improvement.** Skill beyond habitat class alone.

### 3. Detection-effort baseline

- **Inputs.** Visibility, recorded depth, and the protocol effort unit. No AIS.
- **Output.** A small binomial GLM: detection probability as a function of those effort terms only.
- **Evaluation.** Time-forward log-loss. Coefficients are not a habitat map.
- **Why.** A model that only rediscovers “divers see more when visibility is high” is not an ecological result.
- **Improvement.** Skill beyond effort.

### 4. Spatial smoothing baseline

- **Inputs.** Historical detection rate in the same stratum, or in a pre-registered neighborhood of sample units. Neighborhood size is fixed before the test period.
- **Output.** A smoothed past detection rate. Labeled historical. Not current presence.
- **Evaluation.** Spatial-block holdout, so the smoother cannot see the test block.
- **Why.** Occupancy models often lose to a simple spatial rate.
- **Improvement.** Skill in a block the smoother did not see.

### 5. Regional baseline

- **Inputs.** RVC region code (Keys vs Dry Tortugas vs southeast Florida) and season.
- **Output.** A separate detection frequency per region code.
- **Evaluation.** Hold out one region code.
- **Why.** Prevents a Keys fit from being sold as a Florida-wide or Gulf-wide surface.
- **Improvement.** Within-Keys skill that still fails honestly when the region code changes, unless a pre-registered transfer test says otherwise.

**Model family, only after those baselines exist.** A binomial GLM or a single-season occupancy model on the diver survey, with the effort terms above. Random effects no finer than the primary sample unit. Not VAST. Not a spatiotemporal forecast. Not a count model sold as abundance. The model is discarded if it does not beat baselines 1–4 on both a spatial-block holdout and a time-forward holdout.

---

## 3. Gates

### Gate A — Rights

| Check | Mark |
|---|---|
| Training rights confirmed | BLOCKED |
| Display rights confirmed | BLOCKED |
| Attribution recorded | UNKNOWN |
| No prohibited reuse | UNKNOWN |
| Sensitive-location policy approved for this extract | BLOCKED |

Public CSV pages are not approvals. OBIS CC BY-NC and the tagging resource’s CC BY 4.0 do not clear the RVC files.

### Gate B — Observation design

| Check | Mark |
|---|---|
| Enough structured detections | UNKNOWN |
| Effort available | PARTIAL |
| Non-detections available | UNKNOWN |
| Spatial coverage adequate | PARTIAL |
| Temporal coverage adequate | PARTIAL |
| Depth and habitat metadata adequate | PARTIAL |
| Survey method consistent or modeled explicitly | PARTIAL |

PARTIAL means the RVC documentation describes the design. UNKNOWN means this pass did not open the table. A prototype cannot start while non-detections are UNKNOWN.

### Gate C — Covariates

| Check | Mark |
|---|---|
| Covariates match the sample’s time and space | BLOCKED |
| Depth represented as recorded sample depth | PARTIAL |
| Source resolution not overstated | READY as a rule; no covariate grid is in use |
| Missingness documented | UNKNOWN |
| Covariates not mistaken for observations | READY as a rule in the current app |

### Gate D — Validation

| Check | Mark |
|---|---|
| Spatial-block holdout feasible | PARTIAL |
| Time-forward holdout feasible | PARTIAL |
| Performance metric defined | READY as a plan (log-loss, Brier). Not computed |
| Calibration metric defined | READY as a plan (reliability). Not computed |
| Out-of-domain handling defined | READY as a rule: outside the RVC Keys frame the output is “not estimated” |
| Prospective validation path identified | UNKNOWN |

`VALIDATION.md` remains a design. No test in it has been run.

### Gate E — Publication

| Check | Mark |
|---|---|
| Named scientific reviewer | BLOCKED |
| Model card template ready | PARTIAL |
| Human publication authority identified | BLOCKED |
| Sensitive-site review process identified | PARTIAL |
| Rollback path identified | PARTIAL |

The app already refuses current, forecast, abundance, and movement layers unless a card is `PUBLISHED`. That refusal stays. This feasibility note does not publish a card.

---

## 4. If the conditional path is followed

**Recommended region.** Florida Keys Reef Visual Census frame. Not the Ten Thousand Islands, not the Gulf as a whole, not Brazil.

**Minimum data sources.**

1. An RVC extract whose rights review is recorded, containing every sample unit, not only positive goliath rows.
2. The protocol definition (Smith et al. 2011, as cited by the NOAA portal) so the likelihood matches the two-stage design.
3. Sample depth, habitat code, visibility, region, year, and day.
4. No tagging tracks. No Great Goliath Grouper Count site list. No AIS. No OBIS pins in the likelihood.

**Sensitivity safeguards.** Publish, if anything is ever published, only the sample-unit probability inside the survey frame, coarsened so a cell cannot be used as a wreck, aggregation, or nursery coordinate. Withhold any unit a reviewer flags. The existing past-report rule (coarsened, minimum count, cap on cells) is a display rule for OBIS, not a substitute for this review.

**Named missing approvals.**

- NOAA SEFSC / portal terms for training and for display.
- A written statement that non-detections may be derived from the sample frame.
- Sensitive-site review before any geometry is stored.
- A named scientific reviewer.
- A named human publisher. The agent is not that publisher.

**Criterion for leaving feasibility and starting implementation.** All of the following, in writing, in this directory:

1. Gate A training and display marks move from BLOCKED to READY for a named file hash.
2. A short data note states the number of Keys diver surveys, the number with `EPIITAJ`, the rule used to build zeros, and the year span, without listing coordinates.
3. Zeros are greater than zero in count. A file of only positive rows fails the criterion.
4. Gate E names a reviewer and a publisher.
5. The implementation ticket repeats the excluded use cases in section 1.

Until that list is complete, the correct product behavior is unchanged: historical pattern where a coarsened past report exists, and unknown everywhere else.

---

## 5. Why this is not a no-go

A no-go would mean no public design could even define the estimand. The Reef Visual Census is a real stratified visual survey with a public file portal, a depth field, a habitat field, and a bounded Florida reef-tract frame. That is enough to write the target in statistical language. It is not enough to fit it. The blocking gaps are rights, proof of zeros, and the absence of a named reviewer.

---

## 6. What remains prohibited

SST and habitat are not sightings. No public record is not absence. Opportunistic occurrences are not abundance. Resolution stops at the sample unit. Aggregation, spawning, and nursery sites stay off the map. AIS is not fish location. This note is not a prediction product. `NOT_PUBLISHED` stays.

---

## 7. Immediate sequence

The current step is 1, and it is not complete. `RVC_RIGHTS_RECORD.md` names NCEI Accession 0208321 v1.1 and records the pages read on 2026-09-23. Training and display stay unapproved. The file was not downloaded and has no hash. Steps 3–6 stay closed.

1. **Rights-cleared extract.** Obtain a named Reef Visual Census extract and record its file hash, license, training permission, display permission, survey protocol, and attribution. A public download page does not complete this step. The 2026-09-23 reading leaves this step at `CONDITIONAL_REVIEW_REQUIRED`.
2. **Frame and zeros.** Confirm total dives, `EPIITAJ` detections, non-detections, dates, depth, effort, and a usable spatial representation. Store no wreck, aggregation, or nursery coordinates.
3. **Baselines, then one occurrence model.** Fit the seasonal detection rate, the depth/habitat model, and the spatial smoother. Compare a regularized occurrence model only against those baselines. Match covariates to the sample’s time and space before that comparison.
4. **Validation.** Spatial-block holdout, time-forward holdout, calibration, and an explicit out-of-domain result.
5. **Nowcast publication.** Issue a bounded probabilistic nowcast only if it beats the baselines and passes rights and sensitive-site review. A named human reviewer has to move the card off `NOT_PUBLISHED`.
6. **Forecast.** Add a 1–7 day forecast only after that nowcast is stable. Environmental inputs must be forecasts, and the card must show skill by lead time.

---

CONDITIONAL GO — feasible only after named data/rights gaps are resolved
