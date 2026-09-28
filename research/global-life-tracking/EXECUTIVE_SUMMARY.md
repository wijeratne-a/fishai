# Global life tracking — executive summary

**Date:** 2026-09-26  
**Scope:** how people estimate the location, abundance, movement, and distribution of huge populations, and what that means for FishAI. Research only. No globe change, no new model, no sensitive data.

**FUNDAMENTAL FINDING:** No operational system tracks every individual of a wild population at large scale. The systems that work at continental or planetary scale are layered inference: a few directly tracked individuals, standardized surveys with effort, sensors that detect animals near themselves or measure aggregate biomass, environmental fields, and models that keep each observation process separate. Their outputs are probabilities, indices, and intensities with uncertainty, not live positions. Fish face an extra limit: water blocks GPS and radio, so direct tracking of fish is mostly acoustic detection near receivers, plus satellite tags on a few large species.

**WHAT CAN BE TRACKED DIRECTLY:** individual tagged animals (few, biased toward animals that can be caught, often delayed underwater); presence at a sensor at a moment (a diver survey, camera frame, hydrophone call, or eDNA sample); aggregate biomass passing a radar or sonar beam, without species identity.

**WHAT MUST BE INFERRED:** where a species is between sensors and surveys, how many there are, population distribution, corridors, connectivity, range shifts, ecosystem state, and everything about the future.

**WHAT FISHAI CAN BUILD FIRST:** Level 1, the probability that a common species is detected on a documented Reef Visual Census survey in a surveyed Atlantic region and year, shown with uncertainty and a baseline. It exists internally for two Puerto Rico species. On 2023 surveys their Brier scores were 0.195 versus 0.205 for a prevalence baseline, and 0.233 versus 0.248.

**WHAT FISHAI MUST NOT CLAIM:** live locations of wild fish; tracking of all fish; absence from missing records; abundance from presence-only records; accuracy percentages that a constant guess would match; forecasts without archived-forecast validation; anything that points to aggregation, spawning, nursery, or wreck sites.

**MOST VALUABLE NEW DATA TYPES:** more effort-aware repeated surveys with explicit zeros; depth-relevant historical environment and archived forecasts matched to survey events; continuous fixed-site detection series, from passive acoustics or replicated eDNA, with measured error rates.

**MOST VALUABLE NEW METHODS:** occupancy and spatial models that keep the observation process explicit; integrated species distribution models that give each data source its own likelihood; dynamic distribution models driven by data-assimilative ocean analyses and scored by lead time.

**MOST IMPORTANT SCIENTIFIC LIMIT:** detection is not presence, and presence is not abundance. A record's meaning is set by its observation process and effort. Without effort-aware zeros and representative sampling, no model can recover where marine animals are. Even with them, reef surveys every one to two years cannot validate a nowcast without observations collected at the same time.

**RECOMMENDED NEXT CAPABILITY:** finish Level 1 across more species and all four Atlantic zero-bearing survey frames, with a run manifest for every fit. Then test one depth-relevant historical variable, such as bottom temperature or habitat structure, against the survey-only model on untouched years. That is the Level 2 gate.

**LONG-TERM ARCHITECTURE:** seven layers: raw evidence, quality-controlled evidence, observation processes, ecological state, environmental state, inference and prediction, and safety and communication. Every output is labeled with the layer and evidence behind it. Raw storage is immutable. Forecasts are archived and never overwritten. The safety layer can coarsen, delay, or withhold.

## The ten questions

| Question | Direct or inferred | Evidence that can answer it | FishAI now |
|---|---|---|---|
| Where is one tagged animal now | Direct for the tagged animal | GPS, Argos, acoustic receivers | None |
| Where has it moved and where next | Inferred from ordered tracks | State-space and hidden Markov models | None |
| Is a species likely present here and now | Inferred | Surveys plus environment plus models | Past reports only |
| Probability of detection on a standard survey | Inferred from surveys with zeros | Occupancy and detection models | Internal draft, two species |
| Relative abundance under standard effort | Inferred | Count or delta models on surveys | Not started |
| Population distribution | Inferred | Spatial models with support masks | Not started |
| Migration corridors | Inferred from many tracks | Movement and network models | None |
| Connectivity | Inferred | Particle tracking, genetics, tags | None |
| Range shift | Inferred from long series | Spatiotemporal models | None |
| Ecosystem state | Inferred from many sources | Integrated and joint models | None |

## Operational systems that work, and what they output

These were re-checked in this pass.

- **BirdCast** forecasts nocturnal bird migration intensity from 23 years of weather radar and weather data. It explained up to 81 percent of variation, and 62 to 76 percent at 1 to 7 days ahead. It predicts aggregate intensity, not species or individuals (S20).
- **Motus** detects small tagged birds, bats, and insects near a shared network of receiving stations (S03).
- **EcoCast** combines daily satellite ocean data with species models from observer and tag data to map fishing-suitability and bycatch risk. Its dynamic closures could be 2 to 10 times smaller than the existing static closure (S74).
- **A near real-time whale acoustic buoy** reported daily occurrence with 0 percent false detections for three species and 12 to 42 percent daily missed detections. It matched right whale sightings and not humpback sightings (S31).
- **Close-kin mark-recapture** estimated eastern Australian and New Zealand white sharks from juvenile DNA, first at about 280 to 650 adults and later at about 750 (S48).
- **ICARUS** satellite tracking ran on the ISS from 2020 to March 2022 and is rebuilding with new receivers launched in November 2025 and May 2026 (S05). It serves animals that can transmit through air.

None of these systems claims to know where every animal is.

## Where FishAI stands

Publicly, FishAI is a historical atlas (Level 0). Internally, it has a partial Level 1 for two Puerto Rico reef fish. Fourteen of sixteen species models failed on untouched years. Sea-surface temperature was joined for 174 Puerto Rico survey dates and did not improve either species. Goliath grouper has 8 detection events in 2,113 Florida Keys surveys. Pacific survey tables have no zeros.

## Files in this folder

| File | Content |
|---|---|
| `TRACKING_METHODS_MATRIX.csv` | 24 tagging and tracking methods |
| `SENSOR_NETWORK_MATRIX.csv` | 22 sensor and survey networks |
| `ABUNDANCE_ESTIMATION_MATRIX.csv` | 20 abundance and occurrence methods |
| `MOVEMENT_INFERENCE_MATRIX.csv` | 25 movement and distribution-change methods |
| `DATA_FUSION_MATRIX.csv` | 14 ways to combine evidence |
| `GLOBAL_INFRASTRUCTURE_MATRIX.csv` | 24 infrastructure choices tied to FishAI needs |
| `FISHAI_TARGET_ARCHITECTURE.md` | Seven layers with inputs, outputs, gaps, and first steps |
| `FISHAI_CAPABILITY_GAP_ANALYSIS.csv` | 22 capabilities with current state and next action |
| `FISHAI_ROADMAP_BY_EVIDENCE_TIER.md` | Levels 0 to 7 with gates |
| `TRANSFERABLE_LESSONS_FROM_*.md` | Insects, birds, mammals, marine life |
| `SAFETY_AND_PRIVACY_LIMITS.md` | Harm risks and controls |
| `RESEARCH_SOURCES.csv` | 123 sources; each marked as checked this pass, read from the repo, or cited from established literature without re-fetching |

## Ranked recommendations

**1. Three best next data types**

1. Effort-aware repeated surveys with explicit zeros: more NCRMP years when they are published, more regions, and trawl or video surveys that keep event-level zeros.
2. Depth-relevant historical environment and habitat structure matched to survey events, followed by archived operational forecasts with issue and valid times.
3. Continuous fixed-site detection series, from passive acoustics for sound-producing reef fish or replicated eDNA at survey stations, each with measured false-positive and false-negative rates.

**2. Three best next model families**

1. Occupancy and spatial generalized linear mixed models with explicit observation covariates, using delta models where averaged counts matter.
2. Integrated species distribution models with a separate likelihood for each source.
3. Dynamic distribution models driven by data-assimilative ocean analyses and scored by lead time.

**3. Three best next sensor or network concepts**

1. Sentinel sites with continuous passive acoustic recorders, calibrated against co-located visual surveys, following the pattern of the near real-time whale buoys and gliders.
2. Replicated eDNA sampling at reef survey stations, with field and laboratory controls, to build an eDNA observation model.
3. Stereo baited video stations to extend surveys below diver depth, analyzed with an explicit model for MaxN.

A telemetry partnership comes after the distribution layer works, and stays internal.

**4. Three largest risks of misleading users**

1. A probability surface read as "fish are here now," when it is a detection-given-survey estimate or habitat suitability.
2. Stale or presence-only records shown as current, and survey zeros shown as absence.
3. Environmental layers or ocean forecasts presented as fish forecasts, or fine grids that look precise while extrapolating beyond training support.

**5. The clearest path from FishAI today to a real dynamic marine distribution system**

Grow the survey-conditioned detection model across species and zero-bearing regions with reproducible runs. Add a depth-relevant historical variable only if it beats the survey-only model on untouched years. Apply that model to current analyzed ocean conditions and score it against observations collected afterward. Archive ocean forecasts with issue and valid times and score predictions by lead time. Display only coarsened, evidence-labeled, support-masked outputs after human review and written permission. None of these steps requires tracking individual fish.
