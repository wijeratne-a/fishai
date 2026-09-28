# FishAI data gap analysis

**Checked against the repository on 2026-09-27.** This is based on `data/manifests/`, `data/raw/`, `data/restricted/`, and the audit folders. Source ids refer to `SOURCE_INDEX.csv`.

**Bottom line:** FishAI has enough data for one question, survey detection probability for common species in a few survey frames. It has no data that can validate a nowcast, a forecast, individual movement, or larval connectivity. The binding gaps are:

- contemporaneous observations;
- archived ocean forecasts;
- habitat layers;
- depth-resolved environment beyond temperature;
- telemetry;
- untouched test years.

## 1. What FishAI holds

### Biological observations

| Dataset | Observation process | Coverage on disk | Explicit zeros | Effort | Supports | Notes |
|---|---|---|---|---|---|---|
| NCRMP Reef Visual Census, Florida Keys | Diver stationary point count, 15 m cylinder, about 10 minutes, length bins | 2014, 2016, 2018, 2022, 2024. The 2021 file has no Keys dives | Yes, species list repeated per dive, `NUM = 0` | Implicit: fixed protocol per dive | Question 2; question 3 as a relative index | `NUM` is a real-valued average. Rights record says `CONDITIONAL_REVIEW_REQUIRED` |
| NCRMP RVC, Puerto Rico | Same | 2016, 2019, 2021, 2023 | Yes | Same | Question 2 | 2023 is burned: reused for selection and tuning |
| NCRMP RVC, U.S. Virgin Islands | Same | 2017, 2019, 2021, 2023 | Yes | Same | Question 2 | Older logistic fits diverged. Convergence is now enforced |
| NCRMP RVC, Flower Garden Banks | Same | 2018, 2022, 2023, 2024 | Yes | Same | Question 2, small samples | 38 events in 2024 |
| NCRMP RVC, Hawaii, American Samoa, CNMI/Guam, PRIAs | Diver counts | Two years each | No, positive counts only | Partly | Presence-only | Non-detections cannot be built |
| SBC LTER kelp-forest fish (`knb-lter-sbc.17.41`) | Diver belt transect, 40 m by 2 m, 0 to 2 m off the bottom | 2000 to 2025, 11 fixed sites, late July to August | Yes | Fixed transect area | Question 2; question 3 as counts | No per-transect depth. Same-day giant kelp counts in `knb-lter-sbc.18.30` |
| ICES DATRAS NS-IBTS | Bottom trawl haul | 2019 quarter 1 only (HH and HL) | Only `HLNoAtLngt == 0` on a completed haul | Haul duration | Question 3 in principle | One quarter is not a time series |
| DFO Maritimes summer research vessel survey | Bottom trawl set | 2023 sample tables | Needs the event table to build | Set records | Question 3 in principle | Sample only |
| Reef Life Survey, Method 1 | Diver transect | Small public sample | Per transect | Transect | Question 2 or 3 in principle | Sample only |
| CalCOFI CUFES and net tows | Egg pump and ichthyoplankton nets | Cruise 202204 only | Per station | Tow volume | Eggs and larvae only | Eggs are not adults |
| OBIS, Florida Keys box | Compiled occurrences | 672 records, 2026-06-26 to 2026-07-23 | No | No | Presence-only | Never zeros or training rows |
| GBIF, bicolor damselfish | Compiled occurrences | Download `0009727-260921141020460`, about 58,000 records requested | No | No | Presence-only | Catalog only |

### Environmental data

| Product | Variable | Coverage | Matched to surveys | Status |
|---|---|---|---|---|
| HYCOM GOFS 3.1 (one experiment per year) | Water temperature at all depths | Keys: 260 of 279 survey dates. Santa Barbara: all 166 dates | Yes, at dive depth, same day or past day only | Keys: tested, dropped. Santa Barbara: tested, failed on 2022 |
| MUR and OISST | Sea-surface temperature | Puerto Rico survey dates | Yes | Untrusted: future-day join and holdout reuse |
| VIIRS SNPP weekly | Chlorophyll | 136 weeks, Keys box | Not used | Mostly masked or contaminated by the bottom over shallow reef |
| MUR latest snippet | Sea-surface temperature | One day, 2026-09-23 | No | Not a nowcast input |
| Habitat layers | Bathymetry, rugosity, substrate, coral, seagrass, kelp canopy | None: `data/raw/habitat/` is empty | Only survey habitat codes | Gap |

### Model results

| Model | Question | Result |
|---|---|---|
| Florida Keys bicolor damselfish, habitat + depth + visibility | 2 | Beat prevalence on 2022, scored once: Brier 0.095 versus 0.125, AUC 0.86. Failed the calibration check (0.907 predicted versus 0.855 observed) |
| Santa Barbara kelp bass, with temperature | 2 | Lost to prevalence on 2022: Brier 0.296 versus 0.244 |
| Santa Barbara barred sand bass | 2 | Lost to prevalence. Only 9 usable 2022 detections |
| Puerto Rico 2023, two species | 2 | Untrusted |
| Older 16-species suite | 2 | 14 of 16 failed an untouched year. The two passes are the untrusted Puerto Rico results |

## 2. Test years: what is still unused

A validation claim needs data that no decision has touched. FishAI has spent much of its supply.

| Frame | Burned or exposed | Still usable | Constraint |
|---|---|---|---|
| Puerto Rico | 2023 burned | None, until a new year is published | Next NCRMP cycle |
| Florida Keys | 2022 scored for bicolor damselfish. 2024 was the old multi-species holdout. HYCOM is missing after 2024-09-05 | 2022 for other species, disclosed as partly exposed through design choices | The next Keys year needs a temperature source after HYCOM GLBy ends |
| Santa Barbara | 2022 scored for kelp bass and barred sand bass. Aggregate detection counts for every year were printed during exploration | 2023 and 2024, disclosed as count-exposed | 2025 and later need a temperature source other than HYCOM GLBy |
| USVI, Flower Garden Banks | 2023 and 2024 used as old holdouts | Limited | Small samples, especially Flower Garden Banks |

**Gap:** one clean test year per species is the realistic ceiling until new survey years are published. That is enough to reject a model, and weak evidence for accepting one.

## 3. Gaps by question

Readiness labels: `DO_NOW`, `DO_AFTER_ENVIRONMENTAL_JOINS`, `DO_AFTER_MORE_STRUCTURED_DATA`, `REQUIRES_TELEMETRY`, `REQUIRES_PARTNERSHIP_OR_RESTRICTED_DATA`, `NOT_RECOMMENDED`, `UNSUPPORTED_BY_AVAILABLE_EVIDENCE`.

| # | Question | What it needs | What FishAI has | Gap | How to close it | Readiness |
|---|---|---|---|---|---|---|
| 1 | Population distribution | Representative surveys with zeros across the region; habitat and environment layers everywhere a prediction is made; spatial validation | RVC random-stratified sites; 11 fixed Santa Barbara sites; no habitat rasters | Habitat and bathymetry layers; prediction-surface covariates | Public bathymetry, benthic habitat maps, kelp canopy series. Then spatial models on Keys RVC | `DO_AFTER_ENVIRONMENTAL_JOINS` |
| 2 | Survey detection | Zero-bearing survey, observation covariates, one untouched later period | Yes, for common species in the RVC and Santa Barbara frames | More species; convergence-checked fits; manifests; unused years | More species on the existing frames, each tested once | `DO_NOW` |
| 3 | Relative abundance | Counts with effort; a count model; catchability kept constant within a program | RVC averages, Santa Barbara counts, one trawl quarter | Multi-year trawl series; a count model; size selectivity | Full DATRAS or DFO series; delta models | `DO_AFTER_MORE_STRUCTURED_DATA` |
| 4 | Individual movement | Tag detections or positions, receiver metadata, detection range | None | All of it | Partnership with a tagging program; results stay internal | `REQUIRES_TELEMETRY` |
| 5 | Population movement and seasonal redistribution | Surveys across seasons, or many representative tags | Summer-only surveys | Seasonal coverage | Trawl programs with several seasons; telemetry networks | `DO_AFTER_MORE_STRUCTURED_DATA` |
| 6 | Larval connectivity | Current fields at larval depths; spawning timing; larval duration; vertical behavior; parentage or otolith validation at the same sites | One CalCOFI cruise; HYCOM | Larval biology parameters; genetic/otolith validation. Wrong vertical behaviour can beat a passive particle run in the wrong direction (Bode et al. 2019, P312). Almany et al. 2017 (P311) parentage scales are not a Keys damselfish result. | Literature parameters plus a partnership for genetic or recruitment data | `REQUIRES_PARTNERSHIP_OR_RESTRICTED_DATA` |
| 7 | Nowcasting | A validated model with an environmental term that beats survey-only; current analyzed fields; contemporaneous independent observations | No environmental term has passed. No contemporaneous observations | Covariate skill; independent real-time observations; analysis archive | First get an environmental term through a locked test. Then set up contemporaneous checklists or monitoring at sentinel sites | `UNSUPPORTED_BY_AVAILABLE_EVIDENCE` (today) |
| 8 | Short-term forecasting | Everything in 7, plus archived forecasts with issue and valid times | None | Forecast archive; lead-time verification | Start archiving forecasts now, then verify later | `UNSUPPORTED_BY_AVAILABLE_EVIDENCE` (today) |
| 9 | Climate redistribution | Long series across regimes; downscaled projections | Santa Barbara 2000 to 2025; RVC 2014 to 2024 | Out-of-regime validation; projections | Hindcast tests across the 2014 to 2016 marine heatwave; downscaled CMIP6 | `DO_AFTER_MORE_STRUCTURED_DATA` |

## 4. Cross-cutting gaps

1. **Habitat structure.** None on disk beyond survey habitat codes. Reef and kelp fish are expected to respond to structure, depth, and substrate more strongly than to daily temperature. This is the most plausible covariate gap for question 1.
2. **Depth-resolved environment beyond temperature.** No bottom oxygen, salinity at depth, or current at depth has been joined. For demersal fish, surface fields are not an accepted proxy.
3. **Archived forecasts.** FishAI holds no ocean forecast with its issue time. A forecast cannot be verified retroactively without one, because using an analysis in place of a forecast leaks information.
4. **Contemporaneous biological observations.** No independent observation stream is collected within days of a nowcast. A nowcast cannot be validated without one.
5. **Observation-process data.** No repeat visits within a closed period. No observer identity in the current fits. No second method at the same sites. This means occupancy cannot be separated from detection.
6. **Taxonomy.** There is no WoRMS accepted-name mapping. Species codes are used as published. A split or synonym change would silently break a series.
7. **Rights.** The RVC rights record still says `CONDITIONAL_REVIEW_REQUIRED`, and permission letters were not sent. Nothing is cleared for public display.
8. **Reproducibility.** The newest runs have manifests and locks. Older fits do not, and much of the work is uncommitted with no remote.
9. **Ocean data continuity.** HYCOM.org lists GOFS 3.1 GLBy through **2024-09-04** (P500). FishAI preregistration used **2024-09-05**. Do not collapse those dates. ESPC-D-V02 is public from 2024-08-10, 8-day forecast, last 8 runs then scrubbed, page flag `[missing data]` (P501). RTOFS is still on NOMADS HTTPS (`rtofs.20260926/27`, P507); OpenDAP on NOMADS retired 2026-02-23 (P506); CoastWatch ERDDAP RTOFS search HTTP 404 (P508). GLORYS12 is a reanalysis, not a forecast (P513). Any later survey year needs a product-shift test (GOFS vs ESPC vs GLORYS).

## 5. What cannot be closed with public occurrence records

Presence-only records from OBIS, GBIF, iNaturalist, or catch apps cannot supply:

- non-detections;
- effort;
- detectability;
- abundance;
- a current position;
- validation for a nowcast.

They can supply a relative presence intensity only with a sampling-bias model and a stated reference effort (Phillips et al. 2009, S67; Renner et al. 2015, S68). They can also act as a second data source in an integrated model that gives them their own observation process (Isaac et al. 2020, S69; Fletcher et al. 2019, S70). No amount of these records turns into a live fish location.

## 6. Priority order for closing gaps

1. More species on the existing zero-bearing frames, each with a lock and a single test (question 2). No new data needed.
2. Habitat and bathymetry layers joined to Keys RVC sites, then a spatial model with a support mask (question 1).
3. Start archiving ocean analyses and forecasts with issue times now, because the value of the archive grows with time (questions 7 and 8).
4. A multi-year trawl series with haul-level zeros (questions 3 and 5).
5. A partnership for contemporaneous independent observations at a few sentinel sites. Examples are structured diver checklists, fixed acoustic recorders, or replicated eDNA (question 7 validation).
6. A telemetry partnership, internal only (question 4).
