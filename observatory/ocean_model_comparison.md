# Ocean and ecological model comparison — honest literature review

**Agents:** SPATIOTEMPORAL_MODELING_AGENT · ECOSYSTEM_AND_FOOD_WEB_MODELING_AGENT · DATA_ASSIMILATION_AND_DIGITAL_TWIN_AGENT  
**Date:** 2026-09-18  
**Status:** Literature comparison for the observatory **model factory**. No models trained. No ingest.  
**Access date for URLs/DOIs below:** 2026-09-18.

Every family is scored for **saltwater life at operator (hours–days) vs assessment (season–year) horizons**, for **what state it can honestly emit**, and for **whether v0 should use it**. Citations are pointers, not a corpus to train on.

**Factory rule:** a method may only emit states allowed by observatory support tiers T0–T6 as defined in `global_species_registry/support_tier_framework.md` (summarized in `global_digital_twin_architecture.md` §7) and prediction-contract categories A–E. A method is not a tier. Universal output fields (predicted state, uncertainty, data support, extrapolation risk, type, assumptions, feature freshness, validation, limitations) are mandatory.

---

## 1. How to read the scores

| Score | Meaning |
|---|---|
| **Fit** | Scientific match to marine observation processes |
| **v0** | Use on the recommended oyster 72 h twin |
| **Later** | Eligible after data/rights/validation gates |
| **Reject** | Do not use for the named claim |

“Skill in the literature” is **not** transferable to FishAI until time-forward + spatial-block evaluation against **B12/B3/B4** (`artifacts/quality_and_validation/baseline_model_spec.md`). Random CV of neighboring cells is invalid (Roberts et al. 2017 *Ecography* https://doi.org/10.1111/ecog.02881).

---

## 2. Family-by-family comparison

### 2.1 Bayesian hierarchical models

**What they are.** Partial pooling of intercepts/slopes across sites, vessels, farms, strata. Gelman et al., *Bayesian Data Analysis*; marine mixed-effects: Thorson & Minto 2015 *Fish Fish.* https://doi.org/10.1111/faf.12035.

**Honest outputs.** Farm- or vessel-specific event rates or CPUE means with shrinkage; posterior intervals **if** the likelihood matches the label (Bernoulli disruption, log-CPUE). Category C/D.

**Failure modes.** Pooling across basins with different mechanisms (Willapa vs Hood Canal hypoxia); treating the posterior sd as “AI confidence” when the likelihood is misspecified; using hierarchical Bayes to invent data in empty cells (the prior then **is** the map).

| Fit | v0 | Later |
|---|---|---|
| High for Category C/D labels with n≥3 units | Optional intercepts only | Engine for T3/T4 **after** validation |

### 2.2 State-space models (ecological / assessment)

**What they are.** Hidden state \(x_t\), observation \(y_t = H(x_t)+\varepsilon\). Fisheries: Aeberhard, Mills Flemming & Nielsen 2018 *Annu. Rev. Stat. Appl.* https://doi.org/10.1146/annurev-statistics-031017-100427; SAM (Nielsen & Berg 2014 *CJFAS*). Movement SSMs: Jonsen, Flemming & Myers 2005 *Ecology*.

**Honest outputs.** Population-scale numbers **at assessment cadence**; individual movement paths; index smoother. Category B (index) or A only when a designed census exists (almost never at 10 km × 48 h).

**Failure modes.** Feeding 48 h charter CPUE into an annual SSM and reading \(N_{t+\mathrm{1\,day}}\); forgetting process-error underdispersion.

| Fit | v0 | Later |
|---|---|---|
| High at season/year; low at 72 h ops | No | Assessment **context**; tag SSMs model T5 individuals |

### 2.3 Occupancy models

**What they are.** \(\psi\) occupancy, \(p\) detection (MacKenzie et al. 2002 *Ecology* https://doi.org/10.1890/0012-9658(2002)083[2248:ESORWD]2.0.CO;2; MacKenzie et al. 2018 book).

**Honest outputs.** Probability a site is used, **if** repeated visits and a detection process exist. Category D. **Not** abundance.

**Failure modes.** Presence-only GBIF/OBIS as occupancy without a \(p\) model (selection bias, coastal accessibility); public mammal occupancy at fine grain.

| Fit | v0 | Later |
|---|---|---|
| Medium–high for detection grids | No (oysters are planted) | T2–T3 research; coarsened only |

### 2.4 N-mixture models

**What they are.** Repeated counts with binomial detection (Royle 2004 *Biometrics* https://doi.org/10.1111/j.0006-341X.2004.00142.x).

**Honest outputs.** Superpopulation counts **under strong assumptions** (closed population, constant \(p\) or modeled \(p\), designed visits).

**Failure modes.** Unidentifiability and fragile \(N\) (Barker et al. 2018 *J. Appl. Ecol.* https://doi.org/10.1111/1365-2664.12923; Link et al. 2018). **Do not** put N-mixture on unstructured citizen detections and emit Category A.

| Fit | v0 | Later |
|---|---|---|
| Low–medium, assumption-heavy | No | T3 only with designed repeats; else reject as census |

### 2.5 Integrated population models (IPMs)

**What they are.** Joint likelihood of counts, mark–recapture, fecundity (Besbeas et al. 2002 *Biometrics*; Schaub & Abadi 2011 *J. Ornithol.*; Zipkin & Saunders 2018 *Biol. Conserv.*). Fisheries analogue: integrated stock assessment (Maunder & Punt 2013 *Fish. Res.*).

**Honest outputs.** Demographic rates and abundance **at stock scale**, year time-step. Useful as Layer 4 priors (Chinook cohort size from PFMC SAFE; lobster GOM/GBK status).

**Failure modes.** Using IPM \(N_{2025}\) as tomorrow’s CPUE; mixing ESA stocks into one \(N\).

| Fit | v0 | Later |
|---|---|---|
| High at year scale | No (wrong horizon) | T3 context / masks, not 72 h DA |

### 2.6 Dynamic species distribution models (DSDMs)

**What they are.** SDMs with time (Elith & Leathwick 2009 *Annu. Rev. Ecol. Evol. Syst.* https://doi.org/10.1146/annurev.ecolsys.110308.120159; Robinson et al. 2011 marine SDMs *J. Biogeogr.* https://doi.org/10.1111/j.1365-2699.2011.02534.x; Brodie et al. 2018 *Divers. Distrib.* dynamic habitat metrics https://doi.org/10.1111/ddi.12726). Spatiotemporal geostats: VAST (Thorson 2019); sdmTMB.

**Honest outputs.** Relative habitat or encounter suitability through time (Category D); survey-standardized density fields (Category B) **inside the survey design**.

**Failure modes.** Correlative SDM as abundance; projecting to unsampled climate space without `extrapolation_risk`; 24–48 h Chinook “hotspot” from SST/chl (red-team blocker; Shelton et al. 2021 https://doi.org/10.1111/faf.12530).

| Fit | v0 | Later |
|---|---|---|
| Medium at seasonal habitat; poor at 48 h bite | No as product engine | T2–T3 research maps, coarsened |

### 2.7 GAMs

**What they are.** Penalized splines (Wood 2017 *Generalized Additive Models*). Workhorse of NOAA cetacean habitat (e.g. Becker et al. series) and many CPUE standardizations.

**Honest outputs.** Smooth effects of depth, T, DO, month on a **declared** response (CPUE, presence, stress probability). Uncertainty from Bayesian/empirical-Bayes intervals **plus** the usual “smooths are not causal” caveat.

**Failure modes.** Spatial autocorrelation ignored (too-narrow CIs); wiggly smooths filling empty space; SST as the only smooth for Chinook.

| Fit | v0 | Later |
|---|---|---|
| High as Category C/D workhorse | Not until labels exist; B4 is simpler | Yes, after beating B4; T4 only if horizon tests pass |

### 2.8 Random forests / GBM baselines

**What they are.** Breiman 2001 RF; Friedman GBM; ecology BRTs (Elith, Leathwick & Hastie 2008 *J. Anim. Ecol.* https://doi.org/10.1111/j.1365-2656.2008.01390.x).

**Honest outputs.** Nonlinear baselines for Category C/D **if** spatially blocked validation is passed. Good for detecting whether linear B4 missed an interaction.

**Failure modes.** Feature-importance theater; leakage via correlated neighbors; SHAP plots echoing PRIVATE lat/lon; claiming abundance; **must still beat B12/B4** (quality Gate 5). If they win only by memorizing month×cell, ship B12 instead.

| Fit | v0 | Later |
|---|---|---|
| Medium as competitor baseline | No (no training) | Allowed after two-iteration rule |

### 2.9 Graph neural networks (GNNs)

**What they are.** Learning on graphs (Kipf & Welling 2017 ICLR; Battaglia et al. 2018). Cells/particles as nodes, adjacency = neighbors or current-derived edges.

**Honest outputs.** Experimental interpolators of **physical** fields or traffic. Almost no validated marine **ecological** forecast literature comparable to GAMs/VAST.

**Failure modes.** Message passing **invents** values in unobserved nodes (manufactured confidence); uninterpretable; data-hungry; privacy risk if the graph is vessels.

| Fit | v0 | Later |
|---|---|---|
| Low for species state | **Reject for v0** | Research only; not a product engine without beating GAM/VAST |

### 2.10 Neural operators (FNO, DeepONet)

**What they are.** Operators between function spaces (Li et al. 2021 ICLR FNO; Kovachki et al. 2023 *JMLR*; review Azizzadenesheli et al. 2024 *Nat. Rev. Phys.*). Weather: FourCastNet/Pangu/GraphCast are **atmosphere**.

**Honest outputs.** Surrogates of **known** PDE solvers when millions of simulations exist. Not a substitute for sparse animal observations.

**Failure modes.** No FishAI simulation archive; operator learned on physics will not emit lobster \(N\); extrapolation off the training Reynolds/forcing regime is silent.

| Fit | v0 | Later |
|---|---|---|
| Physics-surrogate only | **Reject** | Maybe regional current **emulator** after a licensed model exists |

### 2.11 PINNs

**What they are.** NN + PDE residual loss (Raissi, Perdikaris & Karniadakis 2019 *J. Comput. Phys.* https://doi.org/10.1016/j.jcp.2018.10.045; Karniadakis et al. 2021 *Nat. Rev. Phys.*).

**Honest outputs.** Mesh-free solves of **specified** PDEs (advection–diffusion of a tracer) when boundary conditions are known.

**Failure modes.** Biological “PDEs” are not known; PINNs struggle with sparse noisy data and stiff advection; easy to get a smooth \(C\) that looks like a twin. **Do not** PINN-away empty surveys.

| Fit | v0 | Later |
|---|---|---|
| Narrow (tracer PDE demo) | **Reject** | Optional tracer research vs Parcels GT |

### 2.12 Spatiotemporal transformers

**What they are.** Attention over space-time patches; foundation-model weather/climate (e.g. ClimaX Nguyen et al. 2023). Ecology: few rigorous, data-poor.

**Honest outputs.** None at observatory v0. Possibly later as env **nowcast** consumers (ingest their SST), not as fish models.

**Failure modes.** Hallucinated hotspots; uncalibrated probabilities; energy/cost; cannot satisfy as-of replay if the foundation weights mix future pretraining corpora without a cutoff.

| Fit | v0 | Later |
|---|---|---|
| Low for biology | **Reject** | Env-product consumer only, with cutoff discipline |

### 2.13 Ensembles

**What they are.** SDM ensembles (Araújo & New 2007 *Trends Ecol. Evol.*); climate ensembles; stacking. Dormann et al. 2018 *Clim. Change* on when averaging helps.

**Honest outputs.** Spread across **structurally different** honest models as a **limitation** display (B4 vs B12 vs GAM). Ensemble mean is not more Category A.

**Failure modes.** Averaging a bad abundance model with a good CPUE model; using ensemble spread as calibrated uncertainty without coverage tests.

| Fit | v0 | Later |
|---|---|---|
| High as communication of disagreement | B4 vs B12 display | Yes, after members are individually valid |

### 2.14 Particle filters (SMC)

**What they are.** Sequential Monte Carlo (Gordon, Salmond & Smith 1993 *IEE Proc. F*; Doucet & Johansen tutorials). Ecology: iterated filtering (Ionides et al.). Movement: particle MCMC variants.

**Honest outputs.** Non-Gaussian tracer posteriors (eDNA/HAB); individual movement with fat-tailed errors. Requires a **forward simulator** \(\Phi\).

**Failure modes.** Degeneracy in high dimension (global 3D bio state); weights concentrating on one particle = fake certainty; running PF without licensed currents.

| Fit | v0 | Later |
|---|---|---|
| High for non-Gaussian tracers | No | First **sequential** DA candidate (one basin, one tracer) |

### 2.15 Kalman / EnKF

**What they are.** Kalman 1960; Ensemble Kalman Filter (Evensen 1994 *JGR*; Evensen 2003 *Ocean Dyn.*). Ocean DA reviews: Edwards et al. 2015 *Prog. Oceanogr.*; Carrassi et al. 2018 *WIREs Climate Change*. BGC EnKF experiments exist (e.g. NPZD); operational centers run EnKF/3DVar on **physics**.

**Honest outputs.** Updating a **Gaussian-ish** state of a model we run or a field we are licensed to perturb. Consuming CMEMS/NCODA **analyses** is preferred to DIY EnKF.

**Failure modes.** EnKF on counts without transform; covariance localization that smears PRIVATE farm signal into PUBLIC cells; underdispersed ensembles.

| Fit | v0 | Later |
|---|---|---|
| High for physics products we **consume** | Consume, don’t run | Physics covariates; observatory T6 only with operational gates |

### 2.16 Variational inference (incl. 4D-Var and INLA)

**What they are.** VI in ML (Blei, Kucukelbir & McAuliffe 2017 *JASA*); ocean 4D-Var (NEMOVAR, etc.); ecology SPDE-GMRF via INLA (Rue, Martino & Chopin 2009 *JRSS B*; Lindgren, Rue & Lindström 2011 *JRSS B*) used by VAST/sdmTMB.

**Honest outputs.** INLA/SPDE: **the** practical Bayesian spatiotemporal engine for survey **indices** (candidate T3). 4D-Var: leave to ocean centers.

**Failure modes.** VI underestimates posterior variance (manufactured confidence); 4D-Var as a science project for a three-person team.

| Fit | v0 | Later |
|---|---|---|
| INLA high for surveys; 4D-Var out of team scope | No | sdmTMB/VAST; never DIY 4D-Var |

### 2.17 ABM / IBM

**What they are.** Individual-based models (Grimm & Railsback). Larval IBMs coupled to ROMS (e.g. connectivity; Cowen & Sponaugle 2009 *Annu. Rev. Mar. Sci.*).

**Honest outputs.** Mechanism and scenario exploration (where larvae *could* go). Not calibrated N; hard to assimilate.

**Failure modes.** Pretty movies as forecasts; unidentifiable behavior parameters; compute.

| Fit | v0 | Later |
|---|---|---|
| Medium for larvae research | No (adult oysters sessile) | Research; not issuance |

### 2.18 Food-web models

**What they are.** Ecopath with Ecosim (Christensen & Walters 2004 *Ecol. Model.*); Atlantis (Fulton et al. 2011 *Fish Fish.*); size-spectrum (Andersen, Blanchard). Qualitative: too many fluxes, diet data sparse.

**Honest outputs.** Strategic ecosystem what-ifs at **season–decade**. Layer 4 priors (e.g. *Calanus* → lobster recruitment years later — ASMFC 2025).

**Failure modes.** EwE “biomass on this H3 cell this afternoon”; using food-web balance to override a farm mortality observation.

| Fit | v0 | Later |
|---|---|---|
| High as prior; zero as 72 h engine | **Reject as engine** | Dossier / management scenarios |

### 2.19 Lagrangian methods

**What they are.** Particle tracking in velocity fields (van Sebille et al. 2018 *Ocean Modelling* https://doi.org/10.1016/j.ocemod.2017.11.008; OceanParcels). Applications: larvae, plastics, oil, **eDNA**, HAB cells.

**Honest outputs.** Transport and exposure (Category D). Uncertainty from velocity-error ensembles + decay parameters.

**Failure modes.** One deterministic trajectory as truth; releasing particles from a secret farm and publishing the cloud; calling particle density “abundance.”

| Fit | v0 | Later |
|---|---|---|
| High for tracers | No | HAB/eDNA research slice |

### 2.20 Coupled physical–biological (NPZD / BGC)

**What they are.** Nutrient–phytoplankton–zooplankton–detritus and biogeochemical models on OGCM grids (Fennel et al. 2006 *GBC* and successors; Follows Darwin model; NEMO-PISCES). Skill is typically **better for physical fields and sometimes chl** than for fish.

**Honest outputs.** Habitat covariates (NO3, chl, O2 volume) as Layer 3, with product_type and cutoff. Category E if sold as animals.

**Failure modes.** Equating modeled zooplankton with Chinook forage at 48 h; global BGC cube ingest.

| Fit | v0 | Later |
|---|---|---|
| Medium as licensed chl/O2 **context** | Not needed for oyster air×tide | AOI-subset covariates only |

### 2.21 Causal models

**What they are.** DAGs / potential outcomes (Pearl; in ecology Arif & MacNeil 2022 *Nat. Ecol. Evol.* https://doi.org/10.1038/s41559-022-01923-8).

**Honest outputs.** **Assumption graphs**: bottom T → \(q\) → CPUE ← \(N\); air T × emersion → oyster tissue T → stress; AIS → effort ↛ \(N\). Used to forbid features and to write `assumptions[]`.

**Failure modes.** Claiming causal identification from a single observational SST layer; “causal AI” branding.

| Fit | v0 | Later |
|---|---|---|
| High as design discipline | **Yes — DAGs in the dossier** | Same; rarely a fitted SCM |

### 2.22 Hybrid mechanism + ML

**What they are.** Residual ML on top of a physical/ecological skeleton (Reichstein et al. 2019 *Nature* https://doi.org/10.1038/s41586-019-0912-1).

**Honest outputs.** After a mechanism (B4) is in production, a residual model **may** capture leftover variance **if** it beats B4 prospectively and residuals are not just vessel skill / privacy-laden GPS.

**Failure modes.** Residual soaks up confounding (captain skill, illegal effort, one farm’s husbandry); uninterpretable “physics-informed” stickers.

| Fit | v0 | Later |
|---|---|---|
| Medium as a **gated** upgrade | No | Only after Gate 5 two-iteration rule |

---

## 3. Cross-walk to factory tiers and FishAI candidates

Tiers = `support_tier_framework.md` (T0 taxonomy … T6 operational). **B12 climatology is a baseline, not a T4 forecast.**

| Family | Honest observatory role | Oyster 72 h | Chinook 48 h | Lobster trip | Bloom/eDNA research |
|---|---|---|---|---|---|
| Causal DAG + expert rule (B4) | T2 suitability now; T4 after horizon tests | **v0 (T2)** | Mask + thermal prior | \(q\) prior | Decay assumptions |
| Climatology B12 / persistence B3 | Baseline; never labeled 48 h forecast | **v0 baseline** | Open-season only | Strong baseline | Phenology |
| Hierarchical Bayes / GAM | T3/T4 engines after validation | After labels | After partner logs | After effort logs | — |
| Occupancy | T2 research; T3 if current-condition tests | No | Research only | No | Presence of cells |
| N-mixture / IPM / VAST | Index candidates for T3; IPM year-scale | No | Wrong horizon | Seasonal context | — |
| EnKF / 4D-Var | Consume physics/BGC; not animal N | Consume weather | Consume 3D T | Consume bottom T | Consume currents |
| Particle filter + Lagrangian | Tracer DA research | No | No | No | **First sequential DA** |
| Food-web / IBM / NPZD | Layer 4 prior | No | No | Multi-year prior | NPZD chl context |
| RF/GBM | Competitor after baselines | After baselines | After baselines | After baselines | — |
| GNN / FNO / PINN / transformer | — | **Reject** | **Reject** | **Reject** | PINN optional vs Parcels |

---

## 4. Required output fields (repeat for implementers)

Regardless of family, issuance payload includes: `predicted_state`, `uncertainty` or rationale, `data_support`, `extrapolation_risk`, `model_type`, `assumptions[]`, `feature_freshness`, `validation` (or `none`), `limitations[]`, `confidence_category`, `species_model_support_tier` (registry T0–T6), `output_class`, `prediction_contract_category`, replay IDs.

**Low observation density ⇒ do not emit a filled field.** Transformers, GNNs, and kriging-like smoothers are the highest-risk offenders.

---

## 5. v0 model choice (locked as a recommendation)

**Primary:** B4 expert-rule (tide × air × water T/DO/S × waves) + B12 seasonal-spatial climatology when labels exist + confidence **rule table**.  
**Explicitly not v0:** any neural method, any sequential DA, any food-web, any global SDM.

If B4 already matches grower workflow skill, **shipping B4 as the twin engine is a success** (quality spec §9). Observatory tier remains **T2** until time-forward tests exist. That is still a digital twin of **lease stress state**: prior ecology + env + (later) outcomes + uncertainty. It is not a lesser object because it lacks a Kalman gain.

---

## 6. Confidence of this review

| Item | Confidence |
|---|---|
| Rejection of neural operators/PINNs/transformers as species-N engines | High |
| Particle filter as first sequential DA for tracers | High as a design; low that data/rights will exist soon |
| GAM/sdmTMB as later index/forecast engines | High |
| Quantitative skill numbers for FishAI | **None** — no fits |

Papers were cited, not copied. No weights downloaded. No training.
