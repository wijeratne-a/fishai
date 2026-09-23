# Scientific Red-Team Report — Ocean Intelligence Builder / FishAI

**Agent:** SCIENTIFIC_RED_TEAM_AGENT  
**Date:** 2026-09-18  
**Project root:** `/Users/wijeratne/dev/fishai`  
**Status of models:** none trained; none may go customer-facing.  
**Wedge lock:** UNRESOLVED (founder did not select species × geography × customer × decision).  
**Sibling artifacts reviewed:** first pass had empty directories. **Second pass (same date)** audited files that landed under `marine_domain/`, `quality_and_validation/`, `product_and_monetization/`, `requirements_and_wedge/`, `data_rights_and_privacy/`, and `geospatial_data_engineer/`. `data_discovery/` still had no files. Alignment is generally strong (Category C/D, no AIS-as-abundance, closures not labels). Residual sibling overclaims are in **§11**.

**This agent is not a qualified human domain reviewer.** No customer-facing claim, map, score, or brief is approved by this document.

---

## 0. Verdict (read this first)

| Question | Answer |
|---|---|
| Can any model go customer-facing now? | **No.** Insufficient validation is itself a high-severity blocker. There is no ground truth, no as-of snapshot, no baseline, no spatiotemporal holdout, no partner DUA, and no human domain review. |
| Highest-severity scientific risk — Oyster × WA × 72h | **Food-safety / harvest-legality contamination** of an ops-stress product, plus **SST/chlorophyll proxy misuse** for intertidal thermal mortality (2021 Salish Sea die-off was an *atmospheric* heatwave during midday emersion, not a marine SST event). |
| Highest-severity scientific risk — Chinook × CA/OR × 24–48h | **24–48h encounter is not identified by the available science.** Peer-reviewed habitat/SST work is seasonal-to-annual and stock-specific. Recreational CPUE is an effort-selected contact process truncated by bag limits, seasons, and in-season closures. A heatmap will be read as abundance and as a catch guarantee. |
| Highest-severity scientific risk — Lobster × GOM × CPUE | **CPUE ≠ abundance** (hyperstability; temperature-dependent catchability; trap saturation). **AIS / public vessel density ≠ effort ≠ abundance**, and most inshore Maine boats are not in AIS. Fine maps leak confidential fishing locations. |
| Scientifically safest wedge to *pilot* | **Pacific oyster × WA × 72h operational stress/disruption**, as a **private farm brief**, Category **D**, labels from partner farm outcomes (not DOH closures), culture-type stratified, air+tide+solar+wave (not SST-only). Still **blocked** until food-safety wall, partner labels, and a shellfish-domain reviewer are in place. |
| Least scientifically defensible public product | **Chinook 24–48h relative-encounter map.** |
| Conditional second pilot | **Lobster next-trip CPUE as a private, operator-owned Category C brief on that operator’s own strings.** Public CPUE heatmaps are a deployment blocker. |

**Rule this red team will not relax:** no user-facing prediction may be stronger than the strongest available evidence. Default public product is Category **C** (effort-normalized catch) or **D** (relative habitat / encounter / risk). Categories **A/B** require a documented survey. Category **E** (unverified) may not be a model label or a public prediction.

---

## 1. Scope, method, and truth hierarchy

### 1.1 What was attacked

Attempted falsification of scientific, statistical, product, and causal claims that this product class *will make* if built as specified:

1. Pacific oyster (`Magallana gigas` / `Crassostrea gigas`) × Washington growing areas × farm operator × 24–72h operational stress/disruption. **Must remain separate from official food-safety / harvest legality.**
2. Chinook salmon (`Oncorhynchus tshawytscha`) × bounded CA/OR coast × charter captain × 24–48h relative encounter. **Must not become abundance or a catch guarantee.**
3. American lobster (`Homarus americanus`) × bounded Gulf of Maine statistical area × commercial operator × next-trip expected CPUE. **Must not treat AIS/effort as abundance; location privacy; reporting bias.**

Hunt list (all addressed below and in `model_claims_risk_register.md`): temporal leakage; spatial leakage; autocorrelation misuse; reporting bias; effort confounding; survivorship bias; selection bias; overfitting to season/location; proxy misuse (SST, chlorophyll, vessel density, AIS, social media); unsupported causal language; misleading maps; false precision; ungrounded recommendations; sensitive-location leakage; insufficient validation; claim stronger than evidence tier.

### 1.2 Method

- Pre-model: no weights, no metrics, no “the model works” claims to audit. Falsify **identifiability**, **label validity**, **proxy mechanism**, **validation design**, and **product language**.
- Literature used as *counter-evidence*, not as marketing citations. Access date for web sources: 2026-09-18.
- HiveClaw (`/Users/wijeratne/dev/HiveClaw`) was inspected for founder intent: it is a local Apple-Silicon inference / causal-runtime project. It does **not** lock a marine species, geography, or customer. Do not import HiveClaw performance language into FishAI claims.

### 1.3 Truth hierarchy (binding)

| Tier | What it is | What it may support | What it may not support |
|---|---|---|---|
| **1** | Direct observation / field measurement (calibrated sensor, protocol survey, lab toxin result, verified farm mortality/growth, observer, tagged detection) | Observed occurrence, measured farm outcome, survey index, validated env condition | Extrapolation beyond protocol bounds without a separate, validated model |
| **2** | Operational observation (logbook, landing, charter trip, permissioned vessel/farm stream) | Catch/effort, operational results, private local outcomes | Abundance, legality, food-safety, unbiased spatial maps |
| **3** | Remote-sensing or modeled environment (SST, chlorophyll, currents, waves, reanalysis, habitat layers) | Context, covariates, anomaly, *inputs* to a Category C/D model | Presence, abundance, catch guarantee, food-safety, harvest permission |
| **4** | Unverified reports (social, forums, news, anecdotes) | Hypothesis generation, human review queue | Labels, public predictions, abundance, safety/legal claims |

**Ceiling rule:** a stack of Tier 3 rasters does not promote a prediction to Tier 1. A partner logbook (Tier 2) does not become a census (Tier 1 / Category A).

### 1.4 Prediction categories (binding)

| Cat | Name | Allowed public product? |
|---|---|---|
| A | Direct count | Only inside the surveyed unit, with protocol |
| B | Survey-derived abundance index | Only with documented survey method and attribution |
| C | Effort-normalized catch / observation index | **Default yes**, if effort is defined and bias is stated |
| D | Relative habitat / encounter / risk likelihood | **Default yes**, ranked, uncertain, not a guarantee |
| E | Unverified indicator | **Never** as a model output presented as a forecast |

---

## 2. Cross-cutting attacks (all three wedges)

These failures will appear in *any* “ocean AI map” built from public SST + chlorophyll + AIS + social posts. They are not hypothetical; they are the default failure mode of this product class.

### RT-XCUT-01 — Insufficient validation is currently total (HIGH / BLOCKER)

**Claim attacked:** that a scientifically defensible forecast can be designed and later deployed after “the model looks good.”  
**Falsification:** no target label exists, no as-of feature store exists, no baseline has been computed, random or even honest CV has not been run, no prospective issuance log exists. Retrospective fit on autocorrelated ocean fields routinely beats a fair baseline and then fails in the next year (Roberts et al. 2017, *Ecography*, spatial vs random block CV).  
**Required:** time-forward, out-of-year, spatial-block, and prospective pilot gates in `quality_and_validation/` — and those gates are not yet written. **This red team does not close the validation gate.**

### RT-XCUT-02 — Temporal leakage from “current” ocean products (HIGH)

**Claim attacked:** using today’s SST / chlorophyll / reanalysis as if it were available at forecast issuance.  
**Falsification:** delayed-mode GHRSST, 8-day chlorophyll composites, and reanalyses that assimilate observations *after* the forecast valid time will leak the future into training and into backtests. Chlorophyll composites that include days after issuance are a textbook leak. Stock-assessment abundance (annual, revised) used as a 24–72h feature is also a leak plus a category error.  
**Test:** every feature must have `availability_at_prediction_time`. Replay must freeze the snapshot. If a backtest uses a later-revised field, the score is invalid.

### RT-XCUT-03 — Spatial leakage and autocorrelation misuse (HIGH)

**Claim attacked:** random train/test splits, or neighboring H3/grid cells treated as independent.  
**Falsification:** SST, chlorophyll, and catch are spatially and temporally autocorrelated at scales larger than typical “ML grid cells.” Random splits put the same water mass in train and test. Adjacent farms, adjacent lobster strings, and adjacent charter ports are not independent replicates. Persistence (“yesterday’s CPUE,” “this lease’s 7-day mean temperature”) will often beat a fancy model; if it does, the fancy model is not a forecast.  
**Test:** blocked CV by year, by sub-basin / statistical area / growing area, and a persistence baseline that must be beaten *prospectively*.

### RT-XCUT-04 — Proxy misuse: SST, chlorophyll, AIS, vessel density, social media (HIGH)

**Claim attacked:** these layers “indicate where the animals are” or “indicate stress.”  
**Falsification:**

- **SST** is skin or near-surface. Intertidal oyster lethal heat is *aerial + solar* (Raymond et al. 2022; Hesketh & Harley 2023). Adult Chinook occupy a 3-D thermal habitat; 24–48h SST change is mixed-layer weather, not the seasonal redistribution in Shelton et al. 2021 (*Fish and Fisheries*). Lobster catchability tracks **bottom** temperature, not SST (ASMFC 2025 assessment methods; Zhang et al. 2025 LFA33).
- **Chlorophyll-a** is a noisy proxy for phytoplankton pigment, contaminated by CDOM/turbidity in Puget Sound, Columbia plume, and coastal GOM; 8-day composites miss 72h events; it is not Chinook prey, not oyster food quality, not lobster forage.
- **AIS / vessel density** is a selected subset of vessels that transmit. It is **effort and traffic**, not biomass (master prompt rule 5; Harley et al. 2001). Most Maine inshore lobster boats are <65 ft and have **no AIS carriage duty** (33 CFR 164.46).
- **Social media / forums** are Tier 4, truncated to good days, location-spoofed, and illegal as labels.

### RT-XCUT-05 — Effort confounding and hyperstability (HIGH)

**Claim attacked:** high catch or high vessel density means high abundance.  
**Falsification:** fishers go where catchability × price × habit is high. CPUE can stay high while abundance falls (Harley, Myers & Dunn 2001; ASMFC 2025 lobster peer review: landings are hyperstable and “not a reliable indicator of abundance”). Charter CPUE is further truncated by bag limits. Trap CPUE saturates (~24 h ventless-trap plateau: Watson et al. 2019, *Fishery Bulletin*).

### RT-XCUT-06 — Reporting, selection, and survivorship bias (HIGH)

- Logs exist on days people fished, not on days they did not (missing zeros).
- Partner farms/captains who buy sensors and share data are not a random sample.
- Failed farms, latent lobster licenses, and retired charters drop out (survivorship).
- Maine lobster CPUE time series used a 10% harvester sample (2008–2018), then an optimized active-harvester sample (2019+); 100% reporting began 2023; tribal licenses and some federal VTR were excluded (Hodgdon et al. 2025, *ICES JMS*). Protocol changes are not a continuous index.

### RT-XCUT-07 — Overfitting to season and location (HIGH)

Month × port, month × zone, or month × growing-area dummies will absorb most deviance in catch and farm-workability series. An “AI model” that is secretly a seasonal climatology must be **labeled as a climatology**. Beating a seasonal spatial average is the *minimum* scientific bar, not a press-release result.

### RT-XCUT-08 — Unsupported causal language (HIGH)

Forbidden in product copy even if a coefficient is significant: “caused by SST,” “driven by chlorophyll,” “warming is pushing fish here today,” “this cell is thermally lethal,” “AIS shows a hotspot of lobster.” Covariate association ≠ mechanism ≠ intervention. Tide-timed heat, handling, gear, skipper skill, soak, bait, and regulation are typical true causes.

### RT-XCUT-09 — Misleading maps and false precision (HIGH)

Smooth continuous heatmaps, 100 m cells, three-decimal probabilities (“0.73 encounter”), and red/green “go / no-go” palettes convert Category D ranks into fake Category A counts. Public maps of fishing or farm performance are also a **privacy** failure (see lobster and oyster).

### RT-XCUT-10 — Ungrounded recommendations (HIGH)

“Harvest now,” “fish this waypoint,” “move gear 2 nm east,” “safe to eat,” “legal to harvest,” “you will limit out,” “mortality will be 37%” are commands and guarantees. Product contract allows **options**, not commands, and never legal/safety authorization (master prompt non-negotiable rule 6).

### RT-XCUT-11 — Sensitive-location leakage (HIGH / BLOCKER for public maps)

Exact catch locations, vessel tracks, confidential farm yields, Indigenous/tribal knowledge, ESA-listed Chinook aggregations, spawning/nursery sites. Public product resolution must be coarsened. Partner data default: **PRIVATE**.

### RT-XCUT-12 — Master-prompt target list contains unsafe options (HIGH)

Section 15.1 allows shellfish **“closure-risk indicator”** and fish **“relative abundance percentile.”** As *customer-facing* outputs these are stronger than evidence and will be used as legality / abundance. Red-team **rejects** them as public product targets unless a human domain reviewer and the responsible authority explicitly commission a non-public research product. Official closures may appear only as a **separate, attributed, timestamped context feed**, never as a model score.

---

## 3. Wedge 1 — Pacific oyster × WA × 72h operational stress/disruption

### 3.1 What would have to be true

A 72h farm ops-risk product is scientifically possible **only if**:

- The **target is operational** (workability, gear/wave disruption, handling-stress risk, heat/emersion stress **indicator**), Category **D**.
- Labels are partner **Tier 1/2** outcomes (mortality counts with protocol, sensor exceedances, “could not work the tide,” gear loss) — **not** WA DOH growing-area classification, Vp harvest prohibition, or biotoxin closure.
- Official food-safety/harvest status is displayed as a **non-model** feed: authority, timestamp, jurisdiction, URL, boundary, last-verified time (master prompt 8.6).
- Culture method is a first-class stratum (intertidal beach, off-bottom, floating, FLUPSY/nursery). A pooled “WA oyster” model is a category error.
- Thermal features include **air temperature, solar geometry, tide/emersion, wind, and substrate**, not SST alone.
- Ploidy (triploid vs diploid) is recorded: triploids showed ~2.5× mortality after 30°C water + 4 h at 44°C air (George et al. 2024 / NOAA repository).
- Delayed mortality is in the contract: lab mortality accrued to **day 30**, not hour 72.

### 3.2 Highest-severity attacks

#### RT-OYS-01 — Food-safety / legality contamination (BLOCKER)

**Claim:** “72h operational stress” can sit next to closures, HAB, Vibrio, and harvest-window language without becoming a food-safety product.  
**Falsify:** WA commercial oyster harvest is legally controlled by WAC 246-282-006 (Vp control plan, May–Sep), NSSP, and DOH growing-area / biotoxin closures. 2026 Category 3 growing areas (Hammersley Inlet, Henderson Bay, Pickering Passage, Samish Bay, Skookum Inlet, Stony Point, Totten Inlet, plus others on the DOH list) already convert **water/air temperature at harvest** into a **24h harvest prohibition**. Any model that scores “temperature stress” or “harvest-window suitability” will be used as “is it legal/safe to harvest?” Operators are trained by the regulation itself to treat temperature as a harvest-control variable.

SoundToxins / ORHAB / WDOH toxin testing is the **only** lawful path to biotoxin status. Routine toxin testing is not a 72h continuous field. Phytoplankton alerts are not toxin results. Reopening requires DOH tissue tests, not a model.

**Product implication:** if the brief includes a single combined score, a green map, or language about “harvest window,” the food-safety wall has already failed.

#### RT-OYS-02 — SST is the wrong thermal variable for the event that actually kills WA oysters (HIGH)

**Claim:** satellite or model SST (Tier 3) forecasts 72h mortality/stress.  
**Falsify:** 26–29 June 2021 was an **atmospheric** heatwave coinciding with the lowest daytime tides, not a marine heatwave. Intertidal Pacific oysters were in poor condition where midday emersion met peak air temperature; Olympic Coast sites with morning lows fared better (Raymond et al. 2022 *Ecology*; Miner et al. 2025 *Frontiers in Marine Science*). Air temperature alone was insufficient; solar radiation and body temperature of biomimetic loggers exceed air (Hesketh & Harley 2023; Helmuth literature). SST can be near-normal while oyster tissue is lethal.

**Test:** a model using only SST/chlorophyll must fail a holdout that includes 2021-type AHW days if labels are real mortality. If it “succeeds,” the labels are wrong (probably closures or water temp, not oyster stress).

#### RT-OYS-03 — 72h horizon does not match the mortality process (HIGH)

George et al.: cumulative mortality measured at **30 days** after a multi-stressor exposure. Delayed mortality, disease interaction (*Vibrio* reducing thermal tolerance: Wendling & Wegner 2013), and handling after heat are not 72h binary events. A 72h product can honestly speak to **imminent workability, emersion-heat exposure, and wave/gear disruption**. It cannot honestly speak to “this cohort will die.”

#### RT-OYS-04 — Using official closures as labels (HIGH / BLOCKER if done)

Closures are a regulatory process with sampling lag, species-specific tissue results, and administrative thresholds. They are **not** a biological mortality label. Training “ops stress” on closures produces a shadow food-safety model. The validation agent’s own spec says closures are **context not label** — this red team **binds** that.

#### RT-OYS-05 — Spatial mismatch and farm privacy (HIGH)

Growing-area polygons are not leases. Lease performance is private by default. Publishing a fine map of “stress” infers which farms are failing. Neighboring leases share water but not gear, density, or ploidy — spatial CV must block by farm and by sub-basin (Hood Canal hypoxia ≠ Willapa).

#### RT-OYS-06 — Hypoxia, salinity, HABs, and disease are not interchangeable with “heat stress” (MEDIUM–HIGH)

Hood Canal DO, Fraser/Skagit runoff, *Heterosigma* (finfish, not a human toxin), PSP/DSP/ASP, and OsHV-1-class disease (more documented in CA than as a WA 72h driver) are different mechanisms. One “stress score” is false causal aggregation.

### 3.3 What this wedge *can* support (if walls hold)

Category **D** relative **operational disruption / environmental-stress indicator** for a **named, consenting lease**, 72h, with:

- drivers: forecast air temp, tide/emersion, wind/wave, solar, *in situ* water T/S/DO if the farm has sensors (Tier 1);
- official DOH status as a **separate** box;
- no harvest advice;
- uncertainty: low if sensors + tide-timed heat; high if SST-only.

### 3.4 Pilot safety rank

**Safest scientific pilot among the three**, because the animal is sessile, the site is fixed (no fisher targeting bias), 72h NWP/tide has real skill, and Tier 1 labels are obtainable from a design partner. It is also the **highest legal/reputational blast radius** if the food-safety wall fails.

---

## 4. Wedge 2 — Chinook × CA/OR × 24–48h relative encounter

### 4.1 What would have to be true

A defensible product is **not** a 24–48h species-distribution model. The literature supports:

- Stock-specific ocean distribution at **season / month / PFMC area** scales, often from CWT and GSI, with CPUE as a *contact rate* given effort (Satterthwaite et al. 2015 *Fisheries Research*; Satterthwaite et al. 2018; Shelton et al. 2021).
- Recreational contact ≈ function(stock mix, area, month, effort, size limits), not 24h SST.
- Juvenile presence models (e.g. Hassrick et al. 2016) are summer survey stations, natal-river distance, depth, chlorophyll — **not adult charter encounters tomorrow**.

A barely defensible MVP is Category **C or D**: **rank of expected effort-normalized catch relative to similar calendar-weather bins in the same PFMC/CDFW/ODFW area**, from **partner charter logs** (Tier 2), with regulation state as a hard mask (closed = no prediction).

### 4.2 Highest-severity attacks

#### RT-CHK-01 — 24–48h identifiability failure (BLOCKER for habitat-style models)

**Claim:** environmental fields predict relative encounter in 24–48h.  
**Falsify:** published SST–distribution links are **interannual/seasonal** (Shelton et al. 2021). Adult Chinook move; 48h displacement can exceed a “10 km cell.” Local encounter is dominated by skipper knowledge, swell/workability, bait, crowding, time-of-day, and whether the season is even open. There is no validated 24–48h adult Chinook encounter model in the sources reviewed. Chlorophyll composites cannot update on a 24h decision cycle with known mechanism for adult bite.

If an ML model appears to predict 24–48h encounter from SST/chl, the likely true features are **month, port, and whether it was fishable weather** — season/location overfitting (RT-XCUT-07).

#### RT-CHK-02 — Catch ≠ abundance ≠ encounter guarantee (BLOCKER for public wording)

CPUE is Category **C**, not A/B. Bag limits (typically two salmon/day in 2026 recreational measures) **truncate** the catch distribution; “limits” posts are not abundance. Zero trips on blown-out days are missing. In-season closures (e.g. San Francisco management area closing when the 34,900 Chinook guideline is met, Aug 2026 CDFW/NMFS actions) **select** the sample: late-season data are not the same process as early-season data. Closed areas must not receive an encounter score (that would be an invitation to illegal fishing).

#### RT-CHK-03 — Stock mix and ESA listed units (HIGH / BLOCKER for maps that concentrate effort)

“Chinook” in CA/OR is not one population. Sacramento River winter Chinook (endangered), California Coastal Chinook, Klamath/Trinity, Central Valley fall, and others mix in the ocean. GSI cannot always separate KRFC vs KRSC (Clemento et al. 2014, as cited in later KRSC distribution papers). A hotspot map that improves recreational contact rates can increase impacts on listed stocks. This is a scientific *and* conservation leakage issue. Public fine-scale maps are therefore not only statistically unjustified; they are potentially harmful.

#### RT-CHK-04 — Label pipeline cannot support 24–48h (HIGH)

CRFS PR1 samples ~20–25% of days; CPFV logs are mandatory but historically submitted **monthly**; RecFIN public catch-estimate reports **exclude salmon** (use CDFW Ocean Salmon Project). Public CPUE is lagged and aggregated to area-month, not trip-cell-hour. Without partner trip-level logs (effort hours, anglers, retained, released, area at a privacy-safe coarsening), there is **no 24–48h label**. Social media is Tier 4 and forbidden as labels.

#### RT-CHK-05 — Weather-workability disguised as biology (HIGH)

A “don’t go, small-craft advisory” product is weather-safety advice, which the master prompt **forbids**. A “fish are here” product that is actually a weather filter is a **mislabeled** product. If the only prospectively useful signal is wave height / wind, sell it as **trip workability context**, not encounter.

#### RT-CHK-06 — Spatial leakage of secret spots (HIGH)

Charter “holes” are the business. Even 1 km cells can reveal them. Public maps must be coarse (PFMC subarea or ≥10 km) and still may be too fine near ports.

### 4.3 What this wedge *can* support

Private Category **C**: “Among comparable open-season days in this management area, partner-fleet CPUE ranked in the upper/middle/lower third. Confidence: low/medium. Not a catch guarantee. Not abundance. Not legal advice. Check NMFS/CDFW/ODFW in-season rules.”

Public Category **D** habitat maps at 24–48h: **not supported**. Seasonal climatology of historical CPUE rank: maybe, as a labeled climatology, not an “AI nowcast.”

### 4.4 Pilot safety rank

**Least scientifically defensible.** Do not pilot a public encounter heatmap. A private climatology+weather rank for 1–3 design-partner charters is the only non-blocked research experiment, and it still needs a salmon-biologist reviewer plus ESA/effort-concentration review.

---

## 5. Wedge 3 — American lobster × GOM × next-trip CPUE

### 5.1 What would have to be true

A defensible product is Category **C**: expected **catch per defined effort** (e.g. legal lobsters per trap-haul, or per trap-haul-day) for a **consenting operator’s own gear**, conditional on soak, bait, zone, season, and **bottom** temperature — explicitly **not** abundance, not a public hotspot map, not AIS.

ASMFC 2025: GOM/GBK not depleted relative to the collapse threshold but **down ~34% from 2018 peak**; overfishing occurring on the assessment’s exploitation metric; peer review warns **hyperstability** and that **landings are not a reliable abundance indicator**. Ventless-trap survey indices need model-based catchability standardization (Hodgdon/Chen line of work). Temperature is used in the assessment to adjust **survey catchability**, which is the opposite of “warm water means more lobsters.”

### 5.2 Highest-severity attacks

#### RT-LOB-01 — AIS / vessel density as abundance or even as effort (BLOCKER)

**Claim:** AIS heatmaps show where lobsters are, or where the fleet is working.  
**Falsify:**

- AIS is not biomass (non-negotiable rule 5).
- Federal AIS Class A is generally for self-propelled commercial vessels **≥65 ft** (33 CFR 164.46). Typical inshore Maine lobster boats are smaller and **absent**.
- ASMFC Addendum XXIX electronic tracking (1-minute cellular trackers) applies to **federally permitted** trap-gear vessels, not the state-waters majority. Those tracks are **confidential fisheries data**, not a commercial feature store.
- Using GFW/AIS to train CPUE selects the offshore/federal/large-vessel tail of the fleet (selection bias) and encodes secret trawl locations (privacy).

#### RT-LOB-02 — CPUE ≠ abundance; catchability ≠ density (HIGH)

Mechanisms that move CPUE with **no** abundance change:

- Bottom temperature → activity → trap entry (Zhang et al. 2025: temperature-standardized CPUE differs from raw CPUE; warmer years inflate unstandardized CPUE).
- Molt cycle, bait quality, soak time, trap saturation (~24 h: Watson et al. 2019).
- Trap density / gear saturation / conspecific inhibition.
- Skipper skill and spatial targeting (hyperstability: Harley et al. 2001; ASMFC 2025 peer review).
- Gauge, v-notch, and whale-gear rules changing selectivity.

A next-trip CPUE model can still be useful to a captain **as a catch-rate forecast for their process**, if those confounders are in the model or the limitation text. It becomes false the moment copy says “more lobsters” or “stock is up in this cell.”

#### RT-LOB-03 — Reporting-protocol breaks (HIGH)

Hodgdon et al. 2025: 10% random including inactive (2008–2018) → optimized active sample (2019+) → 100% reporting (2023+); missing federal VTR subset; tribal licenses excluded. A model trained across that break will fit a paperwork change. Fine-scale public landings are also suppressed for confidentiality.

#### RT-LOB-04 — Location privacy and competitive harm (BLOCKER for public maps)

Exact string GPS is NEVER_PUBLISH. Coarsening to NMFS statistical area may still be too fine for inshore harbors. Publishing “top quintile CPUE cells” expropriates the fleet’s spatial knowledge and can increase gear conflict and whale-entanglement controversy maps. Product must be **operator-private** or coarse enough that a competitor cannot steam to a cell and set on someone else’s gear.

#### RT-LOB-05 — Next-trip vs next-cell (MEDIUM–HIGH)

Captains do not randomly sample the GOM. The decision is usually **which of *my* strings to haul, soak, or move**, not a basin-wide search. A product that recommends new secret ground is scientifically weakly identified (no zeros in unfished cells) and ethically worse. Condition on the operator’s existing effort footprint.

#### RT-LOB-06 — Right-whale / regulatory confounding (MEDIUM)

Seasonal restricted areas and weak-link/breakaway rules change where and how people fish. A CPUE drop in a closed or newly restricted zone is regulation, not biology. Do not interpret or display this as “lobsters left.”

### 5.3 What this wedge *can* support

Private Category **C**: “For your gear, given soak/bait/zone and forecast bottom-temp band, expected legal catch per trap-haul ranks in the Xth tercile of *your* comparable trips. Not abundance. Not a recommendation to set on others’ gear.”

Public Category B-style “abundance index” from AIS or raw landings: **forbidden**.

### 5.4 Pilot safety rank

**Second**, only as a **private** partner-logbook CPUE rank. Scientifically better identified than 24–48h Chinook (animals are more site-associated; effort can be defined as trap-hauls). **Worse than oyster** on privacy and on the abundance-confounding literature. Public heatmap: do not pilot.

---

## 6. Claims that MUST NEVER appear in the product

These are banned in UI, PDF, SMS, email, sales decks, and investor materials unless a qualified human domain reviewer *and* (where relevant) the statutory authority explicitly commission a different product — which this agent cannot do.

### 6.1 Universal

- Exact wild-population counts or “there are N fish/lobsters/oysters in this cell.”
- “AI abundance,” “biomass map,” “stock is healthy/up/down” from this model.
- Vessel density / AIS / VMS / GFW as fish or lobster abundance.
- Chlorophyll or SST as proof of presence, abundance, food-safety, or legality.
- Social-media or forum reports as verified presence.
- Catch, harvest, survival, yield, or revenue **guarantee**.
- Legal fishing authorization; license advice; in-season quota remaining as if official.
- Navigation or weather-safety advice (“safe to go”).
- Medical, regulatory, or environmental **certification**.
- Commands: “fish here,” “harvest now,” “move gear to …,” “eat these oysters.”
- Three-decimal probabilities or 100 m heatmaps presented as biological truth.
- Stripped provenance; silent revision of past forecasts; evaluation with future data.

### 6.2 Oyster-specific never-claims

- “Safe to eat,” “safe to harvest,” “legal to harvest,” “open,” “closed” as a **model** output.
- “Meets NSSP / FDA / WA DOH / ISSC requirements.”
- “No Vibrio risk,” “no PSP/DSP/ASP,” “toxin-free,” “below action level.”
- A single green/red score that mixes ops stress with sanitation.
- Publication of another farm’s mortality, yield, or lease polygon without permission.

### 6.3 Chinook-specific never-claims

- “You will catch fish,” “limits tomorrow,” “the bite is on at lat/lon.”
- “Abundance is high in this cell.”
- Advice that would be readable as encouragement to fish a **closed** area or to target a listed stock.
- Fine-scale public spot maps.
- Treating recreational retained catch as a survey index (Category B) without a documented survey design.

### 6.4 Lobster-specific never-claims

- “This AIS hotspot is where the lobsters are.”
- “CPUE up ⇒ stock up” or cell-level abundance.
- Public maps of high-CPUE cells, string locations, or tracker paths.
- Use of Addendum XXIX / VMS / AIS tracks without documented legal rights and privacy-safe aggregation.
- “Guaranteed landings / price / haul.”

---

## 7. Required limitation language (minimum visible text)

Full templates live in `prediction_contract.md`. Every customer-facing output must include the 14 product-output-contract fields. The following sentences are **non-optional** for the respective wedge.

**Oyster:**  
“This is an operational stress / disruption **indicator**, not a food-safety determination and not harvest authorization. Verify official growing-area and biotoxin status with the Washington State Department of Health (and tribal/FDA authorities where applicable). Temperature and satellite layers are not a substitute for tissue toxin tests or the Vp control plan.”

**Chinook:**  
“This is a **relative** encounter / CPUE **rank**, not an abundance estimate and not a catch guarantee. It does not replace weather, navigation, licensing, or NMFS/CDFW/ODFW in-season regulations. Closed areas receive no score.”

**Lobster:**  
“This is an **effort-normalized catch** rank for defined gear and effort, not abundance. AIS and vessel traffic are not lobster density. Locations are coarsened; exact sets are private. Not legal or entanglement advice.”

---

## 8. Human domain reviewer (required; this agent is not it)

No high-severity issue may be closed by another software agent. Required reviewers before any pilot brief reaches a customer:

| Wedge | Reviewer role (minimum) | Why |
|---|---|---|
| Oyster | Shellfish aquaculture extension scientist **and** a public-health / NSSP-literate reviewer (WA DOH liaison or equivalent) | Food-safety wall; ploidy; culture method; 2021 AHW mechanism |
| Chinook | Ocean salmon biologist familiar with PFMC/Klamath/Sacramento contact-rate models **and** an ESA/effort-concentration reviewer | 24–48h overclaim; listed stocks |
| Lobster | GOM lobster assessment or ME DMR science staff **and** a confidentiality/data-privacy reviewer | Hyperstability; tracker confidentiality |

Sign-off must name a human, date, scope, and which HIGH items are **resolved / bounded / accepted**. Silence is not acceptance.

---

## 9. Sources (accessed 2026-09-18)

Indicative, not exhaustive. Full URLs were retrieved during this review.

- Raymond et al. 2022. Heatwave impacts on Salish Sea intertidal shellfish. *Ecology*. https://doi.org/10.1002/ecy.3798 / PMC9786359
- George et al. 2023/2024. Triploid Pacific oysters, heatwaves, delayed mortality. NOAA repository / bioRxiv https://doi.org/10.1101/2023.03.02.530828
- Hesketh & Harley 2023; Helmuth body-temperature literature; Miner et al. 2025 *Front. Mar. Sci.* (tide timing, Olympic Coast vs Salish Sea)
- WA DOH Vp control plan; WAC 246-282-006; growing-area risk categories 2026; commercial closure portal
- NSSP Guide 2023, FDA
- SoundToxins / ORHAB / Trainer et al. *Toxins* 2023 https://www.mdpi.com/2072-6651/15/3/189
- Satterthwaite et al. 2015, 2018 *Fisheries Research* (CA recreational Chinook GSI/CPUE)
- Shelton et al. 2021 *Fish and Fisheries* (SST and Chinook ocean distribution at climate scales)
- Hassrick et al. 2016 *Fisheries Oceanography* (juvenile Chinook, chlorophyll/depth — not 24h adult)
- PFMC 2026 Preseason Report I; 2026 recreational management measures; NMFS in-season / Federal Register corrections
- CDFW CRFS survey design; RecFIN CTE001 (salmon excluded from that report)
- Harley, Myers & Dunn 2001. *CJFAS* hyperstability
- Watson et al. 2019. *Fishery Bulletin* 117(3) ventless-trap saturation
- Hodgdon et al. 2025. *ICES JMS* Maine lobster fleet CPUE / reporting change
- ASMFC 2025 American lobster benchmark assessment and peer review (hyperstability; GOM/GBK status)
- Zhang et al. 2025. Bottom temperature vs lobster CPUE, SW Nova Scotia
- ASMFC Addendum XXIX; Maine DMR tracker pages; 33 CFR 164.46 AIS
- Roberts et al. 2017. *Ecography* — spatial blocking vs random CV

---

## 10. What happens next

1. Other agents’ artifacts must be re-read; any claim that violates this report is a new HIGH finding.
2. `deployment_blockers.md` is binding until a **human** domain reviewer signs.
3. `prediction_contract.md` is the only approved claim language.
4. Do not train production models. Do not ingest restricted AIS/tracker/farm-performance data. Do not ship maps.

**Residual scientific confidence in this red-team itself:** high on *failure modes* (mechanisms and literature are specific); medium on *which private MVP will beat a baseline* (no data in-hand). That uncertainty argues for a **smaller** pilot, not a stronger claim.

---

## 11. Sibling-artifact audit (2026-09-18, second pass)

Siblings that **correctly bound** claims (do not weaken this red team): marine-domain global prohibitions; quality’s ban on random splits and on RecFIN as a 24–48h label; product “must not become” tables; data-rights default-deny GFW/VMS/live AIS; geo as-of timestamps and privacy tiers.

Siblings that **re-introduce** falsifiable claims:

### RT-SIB-01 — Oyster expert baseline is SST-first at 19 °C (HIGH)

**Where:** `quality_and_validation/baseline_model_spec.md` B4 rule 1: alert if forecast/farm SST ≥ **19 °C** for ≥12 h; Hobday **marine** heatwave flag as rule 5. Quality handoff repeats “expert-rule (SST/DO/wave/heatwave).”  
**Attack:** 19 °C is in the **growth / clearance** band for *M. gigas*, not a WA intertidal mortality law. Summer Willapa and Puget Sound water often sits near or above 19 °C; this rule will **false-alert for weeks**. The 2021 kill was **air × midday emersion × solar**, which this rule can miss while water is still ~15–17 °C. Hobday MHW (5+ days, SST percentile) is the **wrong event class** for an atmospheric heatwave.  
**Required:** B4 primary clause = forecast **air** overlapping **daytime emersion** + waves; water T/DO/S as **basin-specific** secondary clauses; drop 19 °C as a default WA alert. Until then B4 is not a scientifically valid “grower analogue.”

### RT-SIB-02 — Sample product brief uses false precision + water-temp-first + Totten (HIGH)

**Where:** `product_and_monetization/wireframe_spec.md` and `product_thesis.md` sample: “Rank ~**top 20%**”; driver 1 = “Water temp **+1.8 °C** vs Sep median (station, 3.2 km)”; geography “**Totten analog**.”  
**Attack:** No model exists; “top 20%” and +1.8 °C teach the exact false-precision and SST-first errors this red team forbids. Totten Inlet is a **2026 WA DOH Vp Category 3** growing area — the place where water/air temperature is already a **legal harvest-control** variable. A temperature-led “ELEVATED” chip there will be read as Vp/harvest advice no matter how large the “NOT FOOD-SAFETY” banner.  
**Required:** samples must lead with **air × tide**, use terciles not “top 20%,” drop one-decimal anomalies, and not use Category 3 areas as the demo geography until the wall is tested by an NSSP reviewer.

### RT-SIB-03 — “Safely work the tide” / B5 “changed harvest plans” (HIGH)

**Where:** `requirements_and_wedge/recommended_initial_wedge.md` metric B: “crew can **safely**/productively work the tide”; quality B5: “changed **harvest** or husbandry plans.”  
**Attack:** “Safely” is weather-safety advice (master prompt forbidden). “Harvest plans” is the food-safety/legality leak.  
**Required:** “workable / productive tide (not safety-certified)”; B5 wording = monitoring / husbandry / gear / **crew timing**, never harvest.

### RT-SIB-04 — Chinook 24–48h “thermal habitat with depth” as an honest v1 covariate (HIGH)

**Where:** marine-domain limitations: predictability “**Medium:** relative thermal-habitat availability (with depth caveat)”; handoff top-5 includes “Thermal habitat ~8–12 °C **with depth**”; product Chinook v0 lists **SST/chlorophyll/currents**. Quality product grain: **~10 km cell**. Geo: H3 **res 6** (~36 km², ~5.6 km spacing) sold as the “10 km cell.”  
**Attack:** 8–12 °C occupancy (Hinke et al.) **falsifies surface SST maps** (fish go deeper). It does **not** identify a 24–48h encounter rank without a skillful **subsurface** field and partner labels. Seasonal SST redistribution (Shelton 2021) is still the wrong horizon. H3 res 6 is finer than a 10×10 km square and can still burn holes near ports. Product v0 SST/chl recreates the proxy the same marine-domain dossier forbids as labels.  
**Required:** Chinook v1 drivers = **open/closed + climatology + (optional) workability confounder**. Thermal-habitat-with-depth is a **research** feature, not v1 copy. Public grain = PFMC/state area, not H3-6.

### RT-SIB-05 — Quality panel scores “label specifiable = 5” as if identifiability were solved (MEDIUM)

**Where:** `go_no_go_scorecard.md` §2: Chinook “trip encounter defined” = 5; oyster expert SST/DO/wave baseline feasibility = 4; lobster public GT = 3 because of 100% ME reports since 2023.  
**Attack:** Specifiable ≠ identifiable at the product horizon. Public ME 100% reports are **lagged / confidential / not next-trip**. SST expert-rule feasibility is inflated by RT-SIB-01.  
**Required:** cap Chinook identifiability at ≤2 until a salmon reviewer agrees; do not treat DMR trip reports as 24–96h GT.

### RT-SIB-06 — H3 res 8 as oyster analytical grid (MEDIUM–HIGH if productized)

**Where:** geo handoff: feature default res **8** (~0.74 km²) for oyster.  
**Attack:** Fine for sampling a raster onto a **private lease polygon**. Fatal if a stress surface is drawn at res 8 (identifies farms; implies bag-level skill marine-domain says is Category E).  
**Required:** product geography = named lease / DOH growing area, not H3-8 choropleth.

### RT-SIB-07 — AIS as “effort-coverage diagnostic” left ajar (MEDIUM)

**Where:** validation_protocol Chinook: AIS “may be used, if rights-approved, only as privacy-sensitive effort-coverage diagnostic.”  
**Attack:** Rights agent default-denies GFW/live AIS; carriage misses the fleet; diagnostics leak spots if mapped.  
**Required:** keep **default do not ingest**. Any diagnostic remains NEVER_PUBLISH and needs legal + red-team re-approval.

**Net after sibling pass:** marine domain and quality **agree oyster is the scientifically cleanest operator product** and Chinook is the weakest at 24–48h. This red team **still NO-GO**s customer-facing output. The most dangerous *new* artifacts are the **19 °C SST baseline** and the **Totten / top-20% / +1.8 °C sample brief** — they will be copy-pasted into a live email.
