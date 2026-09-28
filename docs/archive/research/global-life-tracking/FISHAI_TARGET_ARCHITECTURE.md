# FishAI target architecture

**Date:** 2026-09-26  
**Status:** research design. Nothing here changes the globe, trains a model, or publishes a layer.

## Principle

FishAI cannot track every animal. It can build a layered inference system in which every output states which layer and which kind of evidence supports it. A reader should always be able to tell a sighting from a survey detection, a survey zero from an absence, an ocean condition from a fish, and an internal estimate from a published one.

## What each evidence type means

| Evidence | What it tells you | What it does not tell you | Globe label |
|---|---|---|---|
| GPS or satellite tag | Where one tagged animal was, often with a delay | Where untagged animals are | `DIRECT_OBSERVATION` (never public for sensitive species) |
| Acoustic receiver detection | A tagged animal was within range of a receiver | Where it was between receivers | `DIRECT_OBSERVATION` (internal) |
| Camera or diver survey | A species was seen at a station and time under a protocol | That it was absent when not seen | `STRUCTURED_SURVEY_DETECTION` or `SURVEY_NONDETECTION` |
| eDNA sample | DNA of a taxon was in the water sample | That live animals were at that spot, or how many | `DIRECT_OBSERVATION` of DNA with an eDNA method label |
| Citizen report | Someone reported the species | Effort, absence, or abundance | `RECENT_PRESENCE_EVIDENCE` or `HISTORICAL_OCCURRENCE` |
| Habitat model | Conditions are suitable | That the animal is there | Not an observation label; shown only as suitability |
| Distribution model | Estimated occurrence or detection probability | Any individual's position | `INTERNAL_MODEL_OUTPUT` until a card is published |
| Ocean current or temperature field | Physical conditions | Animal location | `ENVIRONMENTAL_CONDITION` |
| Forecast | Future probability given forecast conditions | Certainty or live tracking | `PUBLISHED_FORECAST` only after lead-time validation |

## The ten questions and the layers they need

| Question | Layers required | Earliest level | FishAI today |
|---|---|---|---|
| 1. Where is one tagged animal now | 0, 1, 2 | 5 | None |
| 2. Where has it moved and where next | 0 to 3 | 5 | None |
| 3. Is a species likely present in an area and time | 0 to 5 | 2 to 3 | Historical past reports only |
| 4. Probability of detection on a standardized survey | 0 to 3, 5 | 1 | Internal draft for two Puerto Rico species |
| 5. Relative abundance under standardized effort | 0 to 3, 5 | 1 to 2 | Not started |
| 6. Population distribution across a region | 0 to 5 | 2 | Not started |
| 7. Migration corridors | 0 to 3, 5 | 5 | None |
| 8. Connectivity | 0 to 5 | 5 | None |
| 9. Range shift | 0 to 5 | 2 to 6 | None |
| 10. Ecosystem state | all | 6 to 7 | None |

## Layer 0 — raw evidence

**Inputs:** survey files, camera annotations, acoustic detections, eDNA results, tag detections, catches, sightings, satellite products, ocean sensor records.  
**Outputs:** unchanged source files with checksums, licenses, retrieval records, and source versions.  
**Uncertainty:** none added. Source errors are unknown until Layer 1 checks them.  
**Failure modes:** silent edits, HTML error pages saved as data, missing companion files, use without permission.  
**Validation:** checksums, content-type checks, license and terms records.  
**FishAI has:** Reef Visual Census tables for the Florida Keys (2014, 2016, 2018, 2022, 2024), Puerto Rico, the U.S. Virgin Islands, and Flower Garden Banks (four years each); four Pacific positive-count tables; one CalCOFI egg sample; 672 OBIS Keys records; MUR sea-surface temperature. Checksums matched 25 of 25 files.  
**FishAI lacks:** an off-machine backup, trawl or video surveys, eDNA, acoustics, telemetry, habitat rasters, forecast archives, and written permission for public display.  
**Minimum first implementation:** already in place. Add a restore test from a second copy.

## Layer 1 — quality-controlled evidence

**Inputs:** Layer 0 files.  
**Outputs:** events with stable identifiers, protocol, effort, units, taxonomy, location precision, time precision, license, and sensitivity class.  
**Uncertainty:** taxonomic confidence, location precision, time precision.  
**Failure modes:** missing rows turned into zeros, protocols mixed, averaged `NUM` read as a count, surface temperature labeled as bottom temperature, date-only records given invented times.  
**Validation:** schema, unit, time, and event-key tests; zero-rule tests.  
**FishAI has:** a verified Atlantic event key, a species-level zero rule, and passing label, unit, time, and contract test suites.  
**FishAI lacks:** those validators run on every acquired file as a pipeline, and a full taxonomy concordance.  
**Minimum first implementation:** run the existing validators on every raw file and store the results.

## Layer 2 — observation processes

**Inputs:** Layer 1 events.  
**Outputs:** a detection model per method: survey detection with visibility and depth, camera detection, tag detection range, acoustic detection, eDNA sample and PCR levels, citizen reporting effort, fishery catchability.  
**Uncertainty:** detection probability, false positives, false negatives.  
**Failure modes:** sources merged with only a source dummy; detection read as occupancy.  
**Validation:** replicate detections, range tests, co-located methods.  
**FishAI has:** visibility and depth used as survey covariates; an observation-process schema.  
**FishAI lacks:** a detection probability estimated separately from occupancy, and any second observation method.  
**Minimum first implementation:** check whether replicate-level detections are available. The analysis-ready Reef Visual Census table averages replicates at the second-stage unit, so an occupancy model may need a different product.

## Layer 3 — ecological state

**Inputs:** observation models plus events.  
**Outputs:** occupancy, abundance index, biomass, behavioral state, movement state, habitat use, distribution, community composition.  
**Uncertainty:** process variance and spatial-field uncertainty.  
**Failure modes:** habitat suitability labeled as occupancy; abundance inferred from presence-only records.  
**Validation:** spatial blocks and untouched years.  
**FishAI has:** survey-conditioned detection probabilities for two Puerto Rico species, internal only.  
**FishAI lacks:** explicit occupancy or abundance states, movement, and community models.  
**Minimum first implementation:** a spatial occurrence model on the Puerto Rico frame with a support mask.

## Layer 4 — environmental state

**Inputs:** reanalysis, current analyses, operational nowcasts, forecasts, climate projections.  
**Outputs:** covariates matched to events and prediction cells, with issue and valid times.  
**Uncertainty:** measurement error, model bias, forecast spread.  
**Failure modes:** present-day conditions used for past events; surface values used for bottom conditions; analyses overwriting forecasts.  
**Validation:** time-matching tests and comparison with in situ data.  
**FishAI has:** MUR sea-surface temperature matched to 174 Puerto Rico survey dates. It did not improve the 2023 holdout.  
**FishAI lacks:** bottom temperature, oxygen, currents, substrate, and a forecast archive.  
**Minimum first implementation:** one depth-relevant historical variable matched to the same Puerto Rico events.

## Layer 5 — inference and prediction

**Inputs:** ecological models plus environmental state.  
**Outputs:** historical estimate, current estimate, near-term forecast, seasonal forecast, scenario, uncertainty, and support mask.  
**Uncertainty:** parameter, process, environmental, and extrapolation uncertainty.  
**Failure modes:** predictions outside training support; forecasts scored against data that were not available at issue time.  
**Validation:** untouched years, spatial blocks, calibration, lead-time scoring.  
**FishAI has:** internal 2023 estimates for two Puerto Rico species and synthetic support-mask code.  
**FishAI lacks:** real support masks and any current or forecast estimate.  
**Minimum first implementation:** a historical estimate with a support mask, internal only.

## Layer 6 — safety and communication

**Inputs:** predictions plus sensitivity rules.  
**Outputs:** coarsened, delayed, or withheld displays; evidence explanations; limitations; freshness; attribution.  
**Failure modes:** a sensitive site inferred from high-probability cells; stale presence shown as current; internal models shown as published.  
**Validation:** exposure tests, evidence-to-map contract tests, human review.  
**FishAI has:** publication gates in the globe, evidence-to-map tests, sensitivity rules, and a passing sensitivity scan.  
**FishAI lacks:** an output coarsening service, UI states for valid time, model version, and extrapolation, a named reviewer, and written display rights.  
**Minimum first implementation:** keep the gates, add a coarsening check, and build the display states before any layer is drawn.
