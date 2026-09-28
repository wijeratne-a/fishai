# Safety and non-targeting boundaries

**Scope:** What FishAI may research, what it may display, and what it must refuse so that distribution research does not become harvest targeting. Complements `research/global-life-tracking/SAFETY_AND_PRIVACY_LIMITS.md`. No fishing recommendations.

The more precise, current, and aggregating a map is, the more it can be used to find and take animals (Cooke et al. 2017, S84; Lennox et al. 2020, S85). Engineering cannot unsay a published grid.

## 1. Allowed scientific outputs (internal until published)

- Probability that a named survey method records a named species, with uncertainty and a baseline.
- Historical atlas of past reports, labelled as past.
- Support masks and "unknown" for unsurveyed water.
- Research nowcasts or forecasts that have passed the validation protocol, coarsened, delayed, and labelled as detection or habitat probability, not as fish location.

## 2. Forbidden outputs

- Where to fish, dive, spear, or harvest.
- Real-time or near-real-time positions of untagged fish.
- Point maps of detections for commercially valuable or sensitive species.
- Fine grids that resolve wrecks, spawning aggregations, nurseries, or FAD-scale patches.
- Individual tracks, receiver locations, or tag IDs.
- AIS or VMS used as fish location (it is vessel effort).
- Crowd catch pins used as training zeros or as a public hotspot layer.
- "Fishing forecast" language, hotspot lists, or productive-area rankings.

## 3. Species and site classes

| Class | Examples | Rule |
|---|---|---|
| Sensitive, withheld | Goliath grouper, white shark; spawning, nursery, wreck, and aggregation sites | No model card on the globe. No public coordinates. Historical habitat only if coarsened and delayed, and only after review |
| Commercially targeted | Kelp bass, tunas, many groupers | Internal detection models allowed. Public maps coarsened to at least 10 km, delayed, never points |
| Common, low targeting risk | Bicolor damselfish on RVC dives | Internal models allowed. Public display still requires `PUBLISHED` and a non-location label |
| Insufficient data | Striped bass on SBC LTER; goliath on Keys RVC | Record `INSUFFICIENT_DETECTIONS`. Do not invent a map |

GBIF and similar portals already generalize sensitive occurrences (Chapman 2020, S86). FishAI follows that practice and is stricter for aggregating fishes.

## 4. Resolution, delay, and aggregation

If a probability layer is ever published:

- Cells no finer than 10 km for targeted or sensitive taxa, and never finer than the survey can support.
- Minimum delay of 30 days for recent detections of targeted taxa; no real-time display for sensitive taxa.
- Minimum number of independent survey events behind a displayed cell (the analogue of a three-vessel fisheries confidentiality rule).
- No tracks. No receiver maps. No wreck overlays.

A coarse map of an aggregating species can still guide harvest when combined with local knowledge. Withholding remains the control that works.

## 5. Crowd data

Complete checklists with effort can enter an observation model. Photos, catch-only reports, and pins cannot.

- Do not show a public live layer of user catch locations.
- Do not rank sites by how many fish users reported.
- Do not recommend "best" sites.

eBird works because complete lists create zeros (Johnston et al. 2021, S80). FishAI may copy that structure, not the social hotspot feed.

## 6. Commercial-tool practices that must not transfer

From public fishing software (see `COMMERCIAL_FISHING_SOFTWARE_ANALYSIS.md`):

- Catch-report maps and "bites" layers.
- Sonar or FAD buoy biomass as a public targeting aid.
- Satellite SST and chlorophyll sold as "where the fish are" without a survey likelihood or a score versus climatology.
- Vessel-tracking intelligence used to infer fishing spots.

Scientifically usable pieces (front detection as a covariate hypothesis; crowd bathymetry with quality flags; dynamic ocean management's validation culture) stay inside the research pipeline. They are not user-facing fishing tools.

## 7. Legal and rights notes

- U.S. fisheries-dependent data are confidential under MSA 402(b) except in aggregates that do not identify a vessel. FishAI does not hold those data and should not seek vessel-level catch for a public product.
- NCRMP RVC rights remain `CONDITIONAL_REVIEW_REQUIRED`. Nothing from those tables is cleared for a public probability layer.
- Raw coordinates stay in gitignored storage. Reports and git must not contain them.

## 8. Required sentence on every public or internal card

> This estimate is the probability that a completed survey of the stated type would record this species. It does not show where fish are now, how many there are, or where to catch them.
