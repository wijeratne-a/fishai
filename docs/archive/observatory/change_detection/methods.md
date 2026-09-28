# Methods — effort-aware indices and change metrics

**Date:** 2026-09-18  
**Status:** Method card. **No series were fitted.** No bulk ingest.  
**Honesty:** IMPLEMENTABLE_NOW means “specified clearly enough to code against a future rights-approved table.” It does **not** mean “run it today.”

Anomaly classes in `event_schema.md` are assigned **after** `bias_vs_biology.md`. This file says how climatology, residuals, phenology, and shifts would be computed when (and only when) a designed index exists.

Commercial W1 does not need a global ST-GAM. It needs lease-level climatology + B4 residuals + coverage flags.

---

## 1. What is being estimated (and what is not)

| Quantity | Allowed as | Never |
|---|---|---|
| Effort-standardized catch or farm-walk rate | Category **C** index | Abundance *N* |
| Occupancy ψ with detection *p* | Category **B/D** research | Census; unsampled cells filled |
| Habitat suitability | Category **D** / EMIV driver | Current presence |
| Survey biomass index | Category **B** when a protocol exists | 24–72 h operator *N* |
| SST, chl, AIS | Covariates (often Category **E** if mislabeled) | Animals |

Default public/W1 claim strength: **C or D** (`prediction_contract.md`). Category A only as an attributed, designed count (W1: farmer already knows planted bags; the engine does not invent wild *N*).

---

## 2. Climatology, current state, anomaly, rate of change

Align with quality baselines (`artifacts/quality_and_validation/baseline_model_spec.md`):

| Piece | Method family | W1 instantiation |
|---|---|---|
| Climatology | **B12** seasonal × spatial table with shrinkage toward a parent when *n* is thin | Month (or tide-season bin) × growing area × **culture method** × depth bin (`INTERTIDAL_AIR` vs `SURFACE_0_5`) |
| Persistence | **B3** | Last 7-day ops-disruption state (onset scored separately) |
| Expert process | **B4** | Air × daytime emersion × wind/wave workability; water T / DO / S supporting with documented mismatch; **not** SST ≥ 19 °C kill law; **not** Hobday MHW SST for the 2021 atmospheric analogue |
| Current state | Same label as climatology | Rank: reduced / typical / elevated vs named comparison set |
| Anomaly | current − B12 on that scale | Residual after B4 if B4 is the relevant process model |
| Rate of change | Slope on the standardized index, or a change-point (§5) | 72 h W1: rate is **onset vs continuation**, not a decadal trend |

**Shrinkage (hypothesis, lock inside training years only):**  
\(\hat y = \frac{n}{n+k}\mathrm{local} + \frac{k}{n+k}\mathrm{parent}\), \(k=20\) farm-days or trips as a starting hypothesis (quality spec). Do not tune *k* on the test year.

**IMPLEMENTABLE_NOW:** specification of B12/B4 residual as the W1 anomaly score.  
**NOT NOW:** any fitted `B12-v0` (no labels in hand).

---

## 3. Effort-standardized indices

**Problem.** Raw counts track **where people looked**. Collins-style presence-only compilations, logbooks without hours, and landings without trap-hauls will invent declines whenever effort falls.

**Practice.**

1. Define effort *E* in physical units: farm-walks, bags inspected, angler-hours, trap-hauls × soak band, survey km, eDNA L filtered, logger hours.  
2. Model \(g(\mathbb{E}[y \mid x]) = \beta x + f(\mathrm{effort})\) or use offset \(\log E\) for counts.  
3. Keep zeros. Closed seasons and unstocked farm-days are **out of universe**, not zeros.  
4. Flag catchability covariates (bottom T, wind) as **q-terms**, not density.  
5. Hyperstability: CPUE can stay high while density falls (Harley, Myers & Dunn 2001 *Can. J. Fish. Aquat. Sci.* 58:1760–1772). A rising CPUE is not a stock boom.

**Citations (cite, do not copy):** Maunder & Punt 2004 *Fish. Res.* 70:141–159; Hilborn & Walters 1992 (book) on CPUE; Bishop 2006 *Fish. Res.* on effort metrics; Thorson 2019 *J. Fish Biol.* VAST review https://doi.org/10.1111/jfb.13948.

**W1:** planted oysters are not a capture fishery. The analogue of *E* is **inspection effort + culture inventory**, not AIS. A week with no farm log is `DATA_GAP`, not mortality.

| | IMPLEMENTABLE_NOW | Not now |
|---|---|---|
| Define *E* and universe rules | yes | |
| GLM/GAM CPUE std. on partner logs | spec yes | fit no (no logs) |
| VAST / spatio-temporal delta-GLMM | | needs designed surveys + rights |

---

## 4. Occupancy and detection probability

**Problem.** Non-detection ≠ absence. MacKenzie et al. 2002 *Ecology* 83:2248–2255 (https://doi.org/10.1890/0012-9658(2002)083[2248:ESORWD]2.0.CO;2): separate occupancy ψ from detection *p* using **repeat visits**.

**Practice.**

- Repeat surveys at a site-window, or spatial replicates with a documented *p* model.  
- Covariates for *p*: effort, sea state, turbidity, gear, observer, time-of-day, acoustic frequency, assay LOD.  
- Covariates for ψ: habitat, season — **not** the same satellite layer used as the “abundance” product.  
- Presence-only (GBIF/OBIS) without a *p* model is an **effort map**. Null model: distance-to-port + depth (red team RT-OBS-03).  
- N-mixture “stealth census” from unmarked counts is not a W1 path (Barker et al. 2018 *Stat. Sci.* critique of N-mixture as abundance).

**W1:** occupancy of wild Pacific oysters is the **wrong target** (stock is planted). Occupancy language is for later observatory taxa, not the 72 h lease brief.

| | IMPLEMENTABLE_NOW | Not now |
|---|---|---|
| Require *p* discussion on every RANGE/DISPERSAL class | yes (tree) | |
| Fit ψ/*p* | | no repeat-survey design in-repo |

---

## 5. Spatio-temporal GAM (ST-GAM) residuals

**Idea.** Fit a smooth in space, season, and year on an **effort-standardized** index; treat large residuals (after *p*/effort terms) as candidate anomalies. Then run the bias tree — residuals of an effort-blind GAM are still artifacts.

Canonical tools: Wood 2017 *Generalized Additive Models* (2nd ed.); `mgcv` `bam` / soap-film smooths on coasts; Cressie & Wikle 2011 on spatio-temporal structure. Marine applications often prefer VAST (Thorson 2019) or INLA-SPDE when the survey is designed.

**Residual rule:**

1. Include effort and catchability in the mean, not only in the error.  
2. Block CV in space and year (`validation_protocol.md`); random 80/20 is forbidden.  
3. Do not interpolate empty cells into a public heatmap (`API_specification.md`). Unsampled → `DATA_GAP`.  
4. Extreme-year holdout (2021 AHW; salmon-closed years).

**W1:** a 72 h lease indicator is a **B4 + B12 residual**, not a coastwide ST-GAM.

| | IMPLEMENTABLE_NOW | Not now |
|---|---|---|
| Residual-after-B4 as W1 anomaly | spec yes | |
| Coastwide ST-GAM / VAST | | no ingest, no GT, wrong W1 grain |

---

## 6. Change-point methods

Use on the **standardized** index, not on raw visit counts.

- PELT / pruned exact linear time: Killick, Fearnhead & Eckley 2012 *JASA*; Killick & Eckley 2014 `changepoint` package.  
- Multiple breakpoints: Bai & Perron 2003 *J. Appl. Econometrics*.  
- Marine climate context: Beaulieu & Killick and Hobday-style MHW definitions for **SST time series** — which is the **wrong** event class for the 2021 **atmospheric** heat dome × midday emersion (quality B4: drop Hobday MHW as default 72 h oyster rule).

**Always fit a parallel change-point on effort, platform flags, and regulation era.** If the biological series breaks on the same day as the e-logbook mandate, class `POSSIBLE_OBSERVATION_ARTIFACT`.

| | IMPLEMENTABLE_NOW | Not now |
|---|---|---|
| Dual change-point rule (index vs effort) as a gate | yes (logical) | |
| PELT on a live series | | no series |

---

## 7. Phenology metrics

**Ask:** early / late relative to a named climatology, **conditional on the observation calendar**.

| Metric | Use | Effort trap |
|---|---|---|
| Center of gravity of a weekly designed index | Preferred | Still needs *E* weights |
| Peak week of survey CPUE / settlement | OK if survey calendar is stable | Survey start date shifts fake “earliness” |
| First arrival / first GBIF record | Research only, usually artifact | Classic citizen-science bias |
| Degree-day hatch/molt (Mills et al. 2017 lobster season start) | Seasonal prior, **weeks** | Not next-trip CPUE; not W1 72 h |

**Citations:** Edwards & Richardson 2004 *Nature* 430:881–884 (plankton phenology); Thackeray et al. 2010 / 2016 phenological asynchrony; Parmesan 2006 *Annu. Rev. Ecol. Evol. Syst.* Ji et al. 2010 phenology metrics review.

**W1:** spawn condition is a **summer-mortality confounder**, not the 72 h target (`species_lifecycle_and_seasonality.md`). Do not emit `PHENOLOGY_SHIFT` for a lease because the first SoundToxins sample of the year was late.

| | IMPLEMENTABLE_NOW | Not now |
|---|---|---|
| Refuse first-record phenology | yes | |
| COG on a designed weekly index | spec | no W1 weekly biological index |

---

## 8. Spatial centroid and range/depth shift

**Ask:** poleward / equatorward / alongshore / offshore / inshore / deeper / shallower.

Standard fisheries metric: biomass-weighted centroid (or occupancy centroid) by year, compared to climatology — **only on a designed survey** (Perry et al. 2005 *Science* North Sea fishes; Dulvy et al. 2008 *J. Anim. Ecol.* deepening; Pinsky et al. 2013 *Science* climate velocity https://doi.org/10.1126/science.1237190). Range **edge** estimators need explicit effort at the edge (Fredston-class caveats: apparent edge follows the survey).

**Chinook trap:** adults keep ~8–12 °C by changing **depth** when SST warms (Hinke et al. 2005 *MEPS* https://doi.org/10.3354/meps304207). Surface CPUE down + SST up can be `DEPTH_SHIFT` or `POSSIBLE_OBSERVATION_ARTIFACT`, not `RANGE_SHIFT` and not abundance down.

**W1:** sessile planted stock → `spatial_shift_summary=not_applicable_sessile_lease` at 72 h. A “range shift” of farmed *M. gigas* off a lease is almost always `POSSIBLE_OBSERVATION_ARTIFACT` (nobody walked the bags) or husbandry (product moved).

**Privacy:** centroids of spawn aggregations, nests, or listed ESUs are `NEVER_PUBLISH` at native grain.

| | IMPLEMENTABLE_NOW | Not now |
|---|---|---|
| N/A flag for sessile W1 | yes | |
| Survey centroid time series | | no survey cube |

---

## 9. Process-specific notes (questions the engine must answer)

### Mortality, disease, hypoxia, heatwave, pollution, fishing

- **Heat (intertidal WA):** air × daytime emersion × solar. Literature analogue 26–28 Jun 2021 (Raymond et al. 2022 *Ecology* https://doi.org/10.1002/ecy.3798). Delayed deaths days–weeks later → 72 h window can miss the label.  
- **Marine heatwave SST (Hobday et al. 2016):** different event class; supporting covariate only if culture is fully subtidal.  
- **Hypoxia:** in situ DO at culture depth; Hood Canal ORCA ≠ Willapa. Cheney et al. 2000 *J. Shellfish Res.* 19:353–359: heat + neap + low oxygen, not a single pathogen.  
- **HAB:** split animal-stress taxa vs NSSP tissue toxins (`w1_oyster_examples.md`).  
- **Disease (OsHV-1):** do not import CA timing into WA without PCR (Dumbauld et al. 2023 *DAO*).  
- **Fishing / handling:** W1 handling during already-stressful tides is an **ops confounder**; wild fishing mortality is out of W1.  
- **Pollution / runoff:** salinity/TSS pulse as multi-stressor, not a single-ion kill law.

### Recruitment failure

Requires the **right stage and lag** (oyster spat; lobster YOY / VTS sublegal → legal in years; salmon cohort). Adult CPUE this week is not recruitment. Default `DATA_GAP` unless a stage-correct survey exists.

### Habitat suitability deteriorating

EMIV / Layer-3 physics. May explain later biological classes. **Not** a substitute for occupancy or mortality evidence (RT-OBS-05).

---

## 10. IMPLEMENTABLE_NOW vs not (summary)

| Method | IMPLEMENTABLE_NOW (spec / rules) | Not implementable in this pass |
|---|---|---|
| Observation-artifact decision tree | **Yes** | — |
| Coverage / wrong-basin `DATA_GAP` (ORCA vs Willapa) | **Yes** | — |
| W1 B12/B4 residual definition | **Yes as spec** | Fitted climatology, numeric thresholds |
| Effort definition + refuse *n_obs* as *N* | **Yes** | GLM on real logs |
| Occupancy ψ, *p* | Require the distinction | Fit |
| ST-GAM / VAST residuals | Residual philosophy | Fit, public grids |
| Change-point on index vs effort | Dual-break rule | PELT on data |
| Phenology COG / first-record ban | Ban + definition | COG series |
| Spatial/depth centroids | N/A for sessile W1; definition for research | Survey centroids |
| 2021 / 2019 case reconstruction from literature | **Yes as fixtures** | Live alerting |
| HAB toxin authorization | **Never** | — |
| Public aggregation map | **Never** | — |

---

## 11. Validation of a future detector

When a writer exists, it must beat:

- a **no-change / B12** baseline on false biological classes (do not “detect” winter effort collapse as mortality);  
- B4 on W1 onset lead time (quality oyster protocol);  
- spatial and year-blocked evaluation;  
- privacy reverse-engineering tests.

Until then, skill = **not applicable**. Fixtures are classification drills, not ROC points.
