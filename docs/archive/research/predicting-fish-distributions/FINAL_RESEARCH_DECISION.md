# FINAL RESEARCH DECISION

CORE PROBLEM: Estimating where fish occur, move, aggregate, or are detected from sparse, biased, intermittent data is not one problem. It is nine: population distribution, survey detection, relative abundance, individual movement, population redistribution, larval connectivity, nowcast, forecast, and climate redistribution. Collapsing them produces maps that look like locations and are not.

WHAT FISHAI CAN REALISTICALLY PREDICT: Probability that a completed survey of a stated method records a named common species, in a named region and season, inside training support. Validated internally for Florida Keys bicolor damselfish on 2022 (Brier 0.095 vs 0.125 prevalence; AUC 0.86; miscalibrated high by ~0.05). Unknown elsewhere.

WHAT FISHAI CANNOT PREDICT: Current location of untagged fish; abundance from GBIF/OBIS; movement without tags; connectivity from one egg cruise; nowcasts or forecasts that beat climatology; most species even where zeros exist (Puerto Rico 2023 untrusted; 14/16 older models failed; SBC kelp bass and barred sand bass failed 2022).

BEST NEAR-TERM METHOD: Locked, species-specific survey-detection models (L2 logistic or simple GAM) on zero-bearing Reef Visual Census and equivalent frames; habitat, depth, visibility; no year dummies; proper scores versus prevalence; one unused later year.

BEST LONG-TERM METHOD: Observation-process models per source, spatial GLMMs on dense surveys, habitat structure, environmental terms only after locked later-year tests, then optional analysis-driven nowcast research if contemporaneous surveys exist. Telemetry and larval particle models remain separate.

MOST IMPORTANT NEW DATA: Unused survey years; bathymetry and benthic habitat; ocean analysis and forecast archives with issue times; sentinel contemporaneous observations; telemetry only for movement.

MOST IMPORTANT ENVIRONMENTAL VARIABLES: Habitat, depth, visibility first; reef structure and bathymetry next; depth-resolved temperature as a testable hypothesis only (failed as a kept feature for damselfish and kelp bass); not SST-as-bottom unless mixed-layer depth is verified at occupied depth; not shallow-reef chlorophyll.

BEST VALIDATION DESIGN: Preregister and hash; score the test period once; cluster by site; Brier and log loss versus a named baseline; calibration check; causal (same-day or past) environment; refuse missing and out-of-range inputs. Spatial CV is not a later-year test.

COMMERCIAL TOOL INSIGHTS WORTH ADAPTING: Named layers; issue and valid times; uncertainty on the map; bathymetry and front/SST as covariates; EcoCast-style one-question validation. AIS/SAR describe vessels (Paolo 2024: 72–76% of industrial fishing missing from public AIS), not fish.

COMMERCIAL TOOL PRACTICES TO AVOID: Catch-report hotspots, BiteScores, fishing-forecast products, sonar/FAD targeting layers, AIS as fish location, CPUE-on-a-front as occurrence, unvalidated "fish probability" marketing.

TELEMETRY ROLE: Direct data for tagged individuals only; not a census; internal; coarsen or withhold. Not a prerequisite for survey-detection models. No movement method is `DO_NOW`. Next movement-adjacent step is Keys survey center-of-gravity after habitat joins.

NOWCAST REQUIREMENTS: Environmental term that beat survey-only on a locked later year; issue-time analyzed ocean fields at the right depth; independent observations after freeze; skill versus climatology; safety coarsening. Not met.

FORECAST REQUIREMENTS: Nowcast requirements plus archived forecasts and lead-time skill versus climatology and persistence. Not met. Archive first: ESPC forecast folder retains ~8 runs then scrubs (P501); RTOFS remains on NOMADS HTTPS (P507) after OpenDAP retirement 2026-02-23 (P506); CoastWatch ERDDAP RTOFS ids 404 (P508).

TOP FIVE RESEARCH PRIORITIES:
1. Expand locked RVC detection models (`DO_NOW`).
2. Habitat rasters and Keys spatial models (`DO_AFTER_ENVIRONMENTAL_JOINS`).
3. Archive ocean analyses and forecasts (`DO_AFTER_ENVIRONMENTAL_JOINS`).
4. Additional structured surveys with a fresh test year (`DO_AFTER_MORE_STRUCTURED_DATA`).
5. Sentinel observations, then internal telemetry (`REQUIRES_PARTNERSHIP_OR_RESTRICTED_DATA` / `REQUIRES_TELEMETRY`).

FINAL RECOMMENDATION: `FOCUS_ON_STRUCTURED_SURVEY_EXPANSION_FIRST`

## Why this option, not the others

- `FOCUS_ON_REGIONAL_SURVEY_DETECTION_NOWCASTS` would skip the missing covariate skill and contemporaneous labels. FishAI already saw temperature fail a later year after passing spatial CV.
- `FOCUS_ON_TELEMETRY_FOR_MOVEMENT_RESEARCH` answers a different question and needs data the repo does not have.
- `FOCUS_ON_LARVAL_CONNECTIVITY_RESEARCH` needs currents plus larval biology plus genetic or recruitment validation; one CUFES/net cruise is not that.
- `INSUFFICIENT_EVIDENCE_FOR_PREDICTION_PROGRAM` is too strong: question 2 is already testable on several frames, and one species passed a locked later-year Brier test.

Structured survey expansion is the only recommendation that matches the data, the one honest success, the crowd-checklist path, and the non-targeting rules.
