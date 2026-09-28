# Core problem definition

**Question:** how can a system estimate where fish are likely to occur, move, aggregate, or be detected when observations are sparse, biased, intermittent, regionally inconsistent, and incomplete?

**Short answer:** it cannot answer that as one question. "Where are the fish" is at least nine different estimation problems. They have different units, different data requirements, and different validation tests. A method that is sound for one of them is usually wrong for the others. Most failures in this field, including FishAI's own early results, come from answering one question with data or methods built for another.

Source ids refer to `SOURCE_INDEX.csv`.

## What is actually observed

No public dataset records where a wild, untagged fish is. Every record is produced by an observation process:

- a diver counting for a set time in a set area;
- a trawl towed for a set distance;
- a camera watching a bait bag;
- a water sample sequenced for DNA;
- a receiver hearing a tag;
- a person choosing to photograph something and upload it.

A record therefore combines two things that must be kept apart (MacKenzie et al. 2002, S42; Guillera-Arroita 2017, S37):

1. **The ecological state.** Was the species in the sampled unit at that time, and how many were there?
2. **The observation process.** Given that it was there, was it seen, caught, heard, or sequenced, and was it identified correctly?

For a single survey, the chance a species is recorded is roughly the chance it is present in the sampled unit, multiplied by the chance it is detected if present. False positives come on top of that, from misidentification or contamination. A single visit cannot separate these two parts. Separating them requires repeat visits within a period when occupancy does not change, independent detection methods, or strong external knowledge of detectability (MacKenzie et al. 2002, S42). This is why FishAI's current product is defined as detection on a survey rather than occurrence.

## The nine questions

| # | Question | Unit of prediction | Observation that can answer it | What validates it | What it cannot say |
|---|---|---|---|---|---|
| 1 | Population distribution | Probability of occurrence, or relative intensity, per area and period | Structured surveys with zeros; presence-only only for relative intensity with bias control | Held-out surveys in unsampled blocks and later periods | Where individuals are now; absolute abundance |
| 2 | Survey detection | Probability that a defined survey, with stated method and effort, records the species | The same survey program, with explicit zeros and effort | The same program in a later, untouched period | Presence when not surveyed; abundance; the same probability for a different method |
| 3 | Relative abundance or biomass | Expected count, density, or catch rate under standard effort | Counts with effort: trawl, visual census, cameras, acoustics | Held-out counts; index consistency across gears | Absolute numbers, without catchability or detectability calibration |
| 4 | Individual movement | Position or state of a tagged animal over time | Telemetry: acoustic, satellite, archival | Withheld positions; double-tagging; known-position tests | Where untagged animals are; population distribution, unless tagging is representative |
| 5 | Population movement and seasonal redistribution | Change in distribution between seasons or years | Repeated surveys across seasons; many representative tags | Later seasons and years; tag-survey agreement | Individual routes; within-season daily movement from annual surveys |
| 6 | Larval dispersal and connectivity | Probability that larvae from area A settle in area B | Ocean currents plus larval biology; validated with genetics or recruitment | Parentage or genetic structure, recruitment time series, otolith chemistry | Adult occurrence or adult movement |
| 7 | Short-term nowcasting | Detection or occurrence probability under current conditions, relative to climatology | A validated model from question 1, 2, or 3, plus current analyzed ocean fields | Contemporaneous independent observations collected after the model was frozen | Where fish are right now; improvement over climatology unless shown |
| 8 | Short-term forecasting | The same as 7, at a stated lead time, using only data available at issue time | The same, plus archived forecasts with issue and valid times | Skill by lead time against climatology and persistence, on archived forecasts | Anything at a lead time where skill has not been shown |
| 9 | Long-term climate redistribution | Projected change in suitable conditions or occurrence under a scenario | Long survey series plus climate projections | Hindcasts across past regime shifts; out-of-period tests | A forecast of a particular year; certainty under novel climates |

## Distinctions that must not collapse

**Occurrence, detection, and abundance.** A detection model estimates what a survey records. An occupancy model estimates where the species is, and it needs repeat visits or a second method. An abundance model estimates how many there are, and it needs counts with effort plus a way to handle catchability. Presence-only data can support relative intensity only with a sampling-bias model. It cannot support occurrence probability without known prevalence (Phillips et al. 2009, S67; Renner et al. 2015, S68).

**Individuals and populations.** A telemetry track describes one tagged animal, chosen by whoever caught and tagged it. Many tracks can suggest population movement only if the tagged animals represent the population in size, sex, season, and capture location (Hussey et al. 2015, S02; Hays et al. 2016, S118).

**State and observation.** Visibility, depth, observer, gear, and bait change what a survey records. They are observation covariates, not habitat preferences. Mixing the two makes a model learn where divers see well, not where fish live.

**Issue time and valid time.** A nowcast uses data available at the time it is issued. A forecast uses only data available at issue time to predict a later valid time. Using an ocean field from after the survey date is leakage, not forecasting. FishAI's untrusted Puerto Rico scores used sea-surface temperature from one and two days after the dive.

**Grain, extent, and window.** Every estimate belongs to a spatial cell size, a region, a depth band, a season, and a survey window. The Santa Barbara transects describe late July to August at 11 fixed kelp-forest sites. They say nothing about winter, about bays, or about the open coast.

## Why sparse, biased data make this hard

- **Sparse in time.** Reef Visual Census regions are surveyed every one to two years, and Santa Barbara transects once a year. That supports annual detection models. It cannot validate daily or weekly claims.
- **Sparse in space.** Surveys are sampled sites, not maps. Eleven fixed sites give a very coarse test of spatial transfer.
- **Biased in effort.** Citizen and fishery data concentrate where people go and where catches are good, so effort maps look like species maps (Johnston et al. 2021, S80).
- **Inconsistent between programs.** Diver counts, trawls, eDNA, and camera counts measure different things. Pooling them manufactures false zeros and false trends (Isaac et al. 2020, S69; Fletcher et al. 2019, S70).
- **Incomplete in covariates.** Depth-resolved temperature, oxygen, and habitat structure are often missing at the survey location. Surface fields are often the wrong layer for reef and bottom fish.
- **Non-stationary.** Relationships learned in one period can break in the next. FishAI's kelp bass model learned "warm years mean more kelp bass" from 2014 to 2018, and then failed in a cooler 2022 when kelp bass stayed common.

## What counts as success

An estimate counts as useful only when it beats a stated reference on data it never saw:

- **Reference forecasts.** The training prevalence or climatology for detection and occurrence. Persistence and climatology for nowcasts and forecasts.
- **Scores.** Proper scoring rules, such as Brier score and log loss, plus a calibration check. Accuracy and AUC alone reward guessing the common answer, or ranking without calibration.
- **Independence.** The test data must be a later period, and different sites where the design allows. Settings must be frozen before the test data are opened.
- **Uncertainty.** Resampling at the level of sites or clusters, not individual dives.

FishAI's one surviving model meets this standard for question 2 only. Florida Keys bicolor damselfish, trained on 2014, 2016, and 2018 and scored once on 2022, beat the prevalence baseline (Brier 0.095 versus 0.125). It failed the preregistered calibration check, because 2022 detections were lower than in the training years. No FishAI model has been validated for questions 1 or 3 through 9.

## The problem, restated for FishAI

The defensible problem is narrow: for a named species, region, survey method, and season, estimate the probability that a completed survey records the species, and show when conditions fall outside what the model has seen. Everything else, including nowcasts, forecasts, movement, and larval connectivity, is a separate question. Each needs its own data and its own validation before any claim is made.
