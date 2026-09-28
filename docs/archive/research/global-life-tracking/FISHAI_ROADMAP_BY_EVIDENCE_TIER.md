# FishAI roadmap by evidence tier

**Date:** 2026-09-26

Each level adds a kind of evidence and a kind of claim. A level is reached only when its validation gate passes. Levels are not dates.

**Where FishAI is now:** publicly Level 0. Internally, a partial Level 1 for two Puerto Rico reef fish. A Level 2 test with sea-surface temperature was run and did not pass.

## Level 0 — historical atlas

- **Can claim:** where and when records of a species exist.
- **Cannot claim:** current presence, absence, or abundance.
- **Data:** occurrence records and survey summaries.
- **Models:** none.
- **Validation:** provenance, coarsening, and correct labels.
- **Operations:** periodic refresh of records.
- **Safety risks:** historical points at aggregation or nursery sites.
- **Bottleneck:** none. This level is working.

## Level 1 — standardized survey intelligence

- **Can claim:** the probability that a species is detected on a documented survey, in a surveyed region and year; a relative abundance index under that protocol.
- **Cannot claim:** presence outside surveyed places, live locations, or population size.
- **Data:** effort-aware repeated surveys with explicit zeros.
- **Models:** detection or occupancy regression; delta models for averaged counts.
- **Validation:** spatial blocks, untouched years, calibration, and a baseline that the model must beat.
- **Operations:** refit when a new survey year is published.
- **Safety risks:** low for common species; rare aggregating species stay withheld.
- **Bottleneck:** few species pass. Two of sixteen passed on untouched years, by small margins.

## Level 2 — dynamic distribution estimates

- **Can claim:** a probability surface across the surveyed domain as a function of habitat and historical environment.
- **Cannot claim:** current conditions or live presence.
- **Data:** Level 1 data plus matched historical environment and habitat.
- **Models:** spatial GLMMs and species distribution models with support masks.
- **Validation:** environmental covariates must beat the survey-only model on untouched years; predictions outside support are masked.
- **Operations:** an environmental matching pipeline.
- **Safety risks:** maps can point to sensitive sites.
- **Bottleneck:** depth-relevant covariates are missing. Sea-surface temperature did not help in Puerto Rico.

## Level 3 — current-condition nowcasting

- **Can claim:** an estimate for the present, driven by current analyzed ocean conditions, inside training support.
- **Cannot claim:** individual positions.
- **Data:** operational analyses for the variables that passed Level 2, with latency tracking.
- **Models:** the Level 2 model applied to current fields.
- **Validation:** prospective scoring against observations collected after issue.
- **Operations:** daily ingestion and stale-data handling.
- **Safety risks:** real-time display of sensitive species.
- **Bottleneck:** a variable must first earn its place at Level 2. Reef surveys come every one to two years, so prospective validation needs continuous sensors or partner data.

## Level 4 — short-term distribution forecasts

- **Can claim:** probabilities for coming days conditional on ocean forecasts, with skill reported by lead time.
- **Cannot claim:** certainty or individual movement.
- **Data:** archived ocean forecasts with issue and valid times that are never overwritten.
- **Models:** the Level 3 model with forecast inputs.
- **Validation:** lead-time scoring against later observations.
- **Operations:** a forecast archive.
- **Safety risks:** forecasts used to target animals.
- **Bottleneck:** no forecast source has been acquired, and skill decays with lead time.

## Level 5 — movement-informed distributions

- **Can claim:** distributions improved by telemetry-derived movement, residency, and connectivity.
- **Cannot claim:** that tagged animals represent the whole population without evidence.
- **Data:** tracks, receiver detections, larval parameters, current fields.
- **Models:** state-space, hidden Markov, step-selection, and particle-tracking models linked to the distribution model.
- **Validation:** held-out individuals and independent surveys.
- **Operations:** partner agreements and embargo handling.
- **Safety risks:** the highest of any level, because tracks and receivers can reveal aggregations.
- **Bottleneck:** data access and representativeness of tagged animals.

## Level 6 — population monitoring network

- **Can claim:** multi-source estimates that combine continuous local detection, periodic surveys, and telemetry.
- **Cannot claim:** complete knowledge of every place.
- **Data:** surveys, acoustic and eDNA sensors, telemetry, environment.
- **Models:** integrated species distribution models, hierarchical fusion, state-space assimilation.
- **Validation:** cross-method agreement and holdout.
- **Operations:** sensor maintenance and field programs that FishAI cannot run alone.
- **Safety risks:** broad; every sensor site needs review.
- **Bottleneck:** field infrastructure and partnerships.

## Level 7 — global ecological digital twin

- **Can claim, in theory:** a continuously updated representation of ecosystem state with uncertainty.
- **Cannot claim:** that it is achievable with current public data. It is not.
- **Data:** observation systems far beyond what exists.
- **Models:** coupled physical and biological assimilation.
- **Validation:** unsolved at this scale.
- **Safety risks:** extreme.
- **Bottleneck:** observations.

## Gates between levels

| Move | Gate |
|---|---|
| 0 to 1 | A survey-conditioned model beats prevalence on spatial blocks and an untouched year, with a run manifest. |
| 1 to 2 | An environmental or habitat covariate beats the survey-only model on the same untouched year, and a support mask exists. |
| 2 to 3 | The same covariates are available operationally with known latency, and the model is scored prospectively. |
| 3 to 4 | Archived forecasts exist, and skill is reported by lead time against later observations. |
| 4 to 5 | Movement data are available under agreement, and adding them improves holdout performance. |
| Any public display | Written rights, a named reviewer, coarsening, and correct evidence labels. |
