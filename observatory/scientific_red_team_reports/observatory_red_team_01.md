# Observatory scientific red team 01 — Global Saltwater Life Observatory

**Agents:** SCIENTIFIC_PEER_REVIEW_RED_TEAM_AGENT (lead), with MODEL_VALIDATION_AND_UNCERTAINTY_AGENT + PHYSICS_AND_FEASIBILITY_RED_TEAM_AGENT  
**Report ID:** `observatory_red_team_01`  
**Date:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/scientific_red_team_reports/`  
**Models:** none trained; none may go user-facing.  
**This agent is not a qualified human domain reviewer.** No map, score, or “life layer” is approved here.

**Does not overwrite:** `artifacts/scientific_red_team/**`. This report attacks the **observatory / “track everything” product class**. Wedge-specific HIGH/BLOCKER items in the FishAI red team remain **OPEN** and binding.

Physics companion: `../physics_feasibility_reports/physical_limits.md`.  
Validation companion: `../validation_protocol.md` (tests **V1–V9**; species support **T0–T6**).  
Do not overwrite: `../observation_modality_catalog.md`, `../sensitive_location_policy.md`, `../global_species_registry/support_tier_framework.md`.

---

## 0. Verdict

| Question | Answer |
|---|---|
| Is a global saltwater life observatory that **tracks everything** scientifically identified? | **No.** |
| Can fusion of satellites, AIS, SST, chlorophyll, eDNA, tags, DAS, and bioluminescence create a census? | **No.** Fusion cannot add photons, acoustic SNR, or tagged animals that do not exist (`physical_limits.md` PX-15). |
| Highest-severity product-class risk | **Category inflation:** habitat, effort, and tracers sold as **presence, abundance, or nowcast tracks** — plus **sensitive-location leakage** of fish, farms, and listed taxa. |
| Status of any observatory biological layer | **NO-GO.** Support-tier assigned T3–T6 count = **0**. Insufficient validation is itself a BLOCKER (FishAI RT-XCUT-01). |
| What would three skeptical reviewers reject? | See §5. In one line: *you measured sampling, ships, and water color, then labeled it life.* |

**Rule this red team will not relax:** no user-facing prediction may be stronger than the strongest evidence on that output. Unsampled cells are **UNKNOWN**, not zero. A model that does not beat a seasonal-spatial baseline is **NOT READY FOR USE**.

---

## 1. Scope and method

### 1.1 Claim under attack

The implicit observatory claim, in sales-deck form:

> We (will) observe saltwater life globally, continuously, in near-real-time, at biologically useful resolution, by combining remote sensing, acoustics, molecular methods, telemetry, fiber sensing, and AI.

This is the claim a skeptical **fisheries scientist**, **acoustician**, and **molecular ecologist** are asked to reject. They would.

### 1.2 What was already falsified (do not reopen as “new AI”)

FishAI `scientific_red_team_report.md` already kills the default ocean-AI map:

- SST/chl/AIS/social as animals  
- CPUE as abundance (hyperstability)  
- Random CV on autocorrelated fields  
- 24–48 h Chinook habitat identifiability  
- AIS as lobster  
- Closures as oyster biology  
- Fine public maps  

This report adds **observatory-scale** attacks: leakage of future data, effort-vs-biology, coverage theater, false transfer, physics category errors, and peer-review language.

### 1.3 Truth hierarchy (binding, unchanged)

Tiers 1–4 and Categories A–E as in `prediction_contract.md`. A stack of T3 rasters is still T3. eDNA occupancy is not Category A. DAS whale calls are not a fish census.

---

## 2. Attack catalog (required hunt list)

All items **OPEN**. Severity: BLOCKER > HIGH > MEDIUM.

### RT-OBS-01 — Leakage (temporal)

**Claim:** Backtest skill is the skill a user would have had.  
**Falsify:** Delayed-mode SST, 8-day chlorophyll that includes post-issuance days, reanalyses that assimilate future obs, revised landings, stock-assessment biomass used as a 24–72 h feature, eDNA batches run weeks later presented as synoptic, PSAT data decoded after pop-up presented as a live track.  
**Test:** `available_at ≤ issued_at` on every feature; freeze snapshots (`as_of_replay_design.md`). If a score needs later-revised fields, it is invalid for go/no-go.  
**Sev:** HIGH / BLOCKER for any “validated” language.

### RT-OBS-02 — Future data in training (information leak)

**Claim:** Foundation models trained on the whole archive “know the ocean.”  
**Falsify:** Random spatiotemporal crops put the same climate event, the same survey, and the same ship in train and test. Using 2024 MUR SST to “predict” 2023 chlorophyll is not prediction. Using the test year’s PFMC preseason index before it was published is a leak.  
**Test:** Year-block; embargo features by publication time; document every index’s public timestamp.  
**Sev:** HIGH.

### RT-OBS-03 — Learning sampling effort, not biology

**Claim:** High observatory score = more life.  
**Falsify:** OBIS/GBIF, eDNA stations, acoustic transects, and citizen science map **where people sampled**. Models predict **accessibility, funding, and weather windows**. Collins/OBIS-class occurrence layers are presence-only with huge spatial bias (`data_catalog.csv` OBIS notes).  
**Test:** Include effort as a feature **or** as a null model (distance-to-port, depth-of-station, ship-days). If removing biology covariates does not hurt skill, the model is an effort model.  
**Sev:** HIGH / BLOCKER for occupancy maps.

### RT-OBS-04 — Vessel behavior vs fish

**Claim:** AIS/VMS/GFW heat is fish or fishing success.  
**Falsify:** AIS is a selected transmitting subset (e.g. many inshore lobster boats have no carriage duty, 33 CFR 164.46). Fishers target catchability × price × habit (Harley, Myers & Dunn 2001). GFW is **NONCOMMERCIAL** for this project anyway (`data_rights` handoff).  
**Test:** Ban AIS as label and as abundance feature. If used as effort diagnostic, label **“traffic, not fish”** and pass reverse-engineering tests.  
**Sev:** BLOCKER (policy + science).

### RT-OBS-05 — Habitat vs current presence

**Claim:** Suitable SST/chl/depth ⇒ animals are there now.  
**Falsify:** Habitat is a **envelope**, often seasonal-to-climate scale (Shelton et al. 2021 Chinook SST). Presence requires occupancy process + detectability. Adult Chinook can leave the surface while remaining in the cell (Hinke et al. 2005). Oyster “habitat” is a farm. Lobster habitat without soak/bait is not CPUE.  
**Test:** Score occupancy against **same-week independent detections**, not against the habitat raster itself (circular).  
**Sev:** HIGH / BLOCKER for nowcast language.

### RT-OBS-06 — Hotspot overfitting

**Claim:** The model found reefs, wrecks, and “AI hotspots.”  
**Falsify:** Month × place dummies absorb most catch deviance (FishAI RT-XCUT-07). Deep models with spatial coordinates memorize ports.  
**Test:** Ablate coordinates and month; require lift vs **B12 seasonal-spatial average**. Transfer to a new port complex.  
**Sev:** HIGH.

### RT-OBS-07 — Spatial autocorrelation misuse

**Claim:** 80/20 random split, or adjacent H3 cells as i.i.d.  
**Falsify:** Roberts et al. spatial vs random CV; ocean fields correlated at scales ≫ ML cells.  
**Test:** Blocked CV; persistence baseline.  
**Sev:** HIGH / BLOCKER for “validated AI.”

### RT-OBS-08 — Climate anomaly failure

**Claim:** Training years represent tomorrow.  
**Falsify:** 2021 Pacific Northwest atmospheric heatwave (oyster mechanism is air×tide, not SST). Marine heatwaves, regime shifts, salmon closed years (CA 2023–24), lobster gauge changes (Addendum XXVII). A model that never saw the analog will still color a map.  
**Test:** Leave-one-extreme-year-out; `extrapolation_flag`; suppress to UNKNOWN/None.  
**Sev:** HIGH.

### RT-OBS-09 — Hiding low coverage

**Claim:** Global / complete / continuous layer.  
**Falsify:** Clouds, night, first optical depth, unsampled eDNA, tag n≪N, DAS only on cables, acoustic dead zone, fouled sensors. Smooth interpolators and GANs fill the globe.  
**Test:** Publish sampled fraction, last observation age, and UNKNOWN hatch. If coverage > claimed sampling, fail.  
**Sev:** BLOCKER for “global observatory” marketing.

### RT-OBS-10 — False cross-species / cross-region transfer

**Claim:** A foundation model trained on tuna/AIS/chl transfers to Willapa oysters, OR Chinook, or GOM lobster.  
**Falsify:** Wrong stage, gear, depth, culture method, stock mix, reporting protocol. OsHV-1 CA ≠ WA (marine-domain dossier). SNE lobster hypoxia ≠ GOM. Juvenile salmon chlorophyll models ≠ adult charter bite.  
**Test:** Geographic and taxonomic transfer tests **pre-registered**; default fail.  
**Sev:** HIGH / BLOCKER if used to skip local labels.

### RT-OBS-11 — Sensitive location leak

**Claim:** Fine maps are scientifically better.  
**Falsify:** Charter holes, trap GPS, farm KPIs, tribal U&A, ESA aggregations, right whales. Privacy policy: NEVER_PUBLISH (`privacy_and_sensitive_location_policy.md`). DAS whale localizations are a conservation leak if published fine.  
**Test:** Reverse-engineering 500 m recovery test; rule-of-3; coarsen or withhold.  
**Listed-species DAS/PAM localizations are `NEVER_PUBLISH`** (`sensitive_location_policy.md` §3.10, rights-safety handoff). A global public animal atlas is **rejected as v1**.  
**Sev:** BLOCKER for public maps.

### RT-OBS-12 — Claims > evidence

**Claim:** “Abundance,” “biomass,” “N animals in this cell,” “safe to harvest,” “you will catch,” “live tracks.”  
**Falsify:** Evidence ceiling table in `model_claims_risk_register.md`. Physics PX-01…20.  
**Test:** Every sentence maps to Category A–E. Upgrade without new evidence = fail.  
**Sev:** BLOCKER.

### RT-OBS-13 — Failure vs seasonal average

**Claim:** Skill because AUROC > 0.5 or because the map is pretty.  
**Falsify:** B12 month×place is the competent null. Persistence is the other.  
**Test:** Primary metric vs frozen baseline, time-forward **and** spatial **and** prospective. **If not beating baseline: NOT READY FOR USE.**  
**Sev:** BLOCKER for forecast/nowcast products.

### RT-OBS-14 — Physics category error (new vs FishAI file)

**Claim:** More sensors ⇒ census.  
**Falsify:** `physical_limits.md`. Satellites don’t see fish; eDNA is a tracer; tags are late and few; DAS gauge ≠ fish body; RF dies in seawater; fouling kills unattended truth.  
**Sev:** BLOCKER for observatory slogan.

### RT-OBS-15 — Fusion category inflation

**Claim:** Multimodal transformer outputs a “life probability” everywhere.  
**Falsify:** Outputs cannot exceed the best input evidence. Filling UNKNOWN with SST is still SST.  
**Test:** Mask fusion where all biological modalities are missing; residual must be labeled habitat or UNKNOWN.  
**Sev:** HIGH / BLOCKER.

---

## 3. Most dangerous false claims for this product class

Ranked by harm (scientific fraud × user action × conservation/legal blast radius).

| Rank | False claim | Why it is dangerous | Who gets hurt |
|---|---|---|---|
| 1 | **“We track all marine life in real time.”** | Physically false; hides UNKNOWN; invites regulation and ridicule | Every later honest product |
| 2 | **Public hotspot / biomass heatmap** | Effort confounding + spot burning + ESA/whale targeting | Listed stocks, captains, farms, NGOs |
| 3 | **AIS/vessel density as fish** | Category error + competitor tracking | Operators; MSA confidentiality analog |
| 4 | **Satellite sees the fish** | Operators steam to empty surface water; oysters die in air while SST looks fine | Growers, charters |
| 5 | **eDNA = GPS of a live animal / abundance** | Wrong grain; false invasives; false absences | Biosecurity, assessments |
| 6 | **Uncalibrated acoustics / DAS = stock size** | 17–45% biomass swings from \(\alpha\) **alone** at long 38 kHz ranges (Doonan et al. 2003); DAS is strain, not TS | Assessments, investors |
| 7 | **Catch guarantee / harvest authorization / food-safe** | Legal and safety wall (FishAI non-negotiables) | Public health, licenses |
| 8 | **Tag tracks as the population** | Tagged minority, delayed pop-up | Management advice |
| 9 | **Cross-ocean foundation model “already works here”** | Skips local labels; false transfer | All three wedges |
| 10 | **Smooth completeness** | Coverage theater; overconfidence in sparse cells | Decision-makers |

Never-claims from `prediction_contract.md` remain in force (counts, AI abundance, social as verified, commands, three-decimal fake precision, silent forecast edits).

---

## 4. Observatory vs FishAI wedges (do not launder)

| If copy says… | Red-team action |
|---|---|
| Global life layer **and** Willapa oyster brief | Split products. Oyster brief may not inherit observatory language. |
| Chinook 48 h map from ocean color + AIS | RT-CHK-01 + RT-OBS-04/05; **do not deploy** |
| Lobster abundance from DAS/AIS/SST | RT-LOB-01 + PX-09/16/19 |
| eDNA dashboard as farm mortality | Wrong tracer, wrong horizon |

Safest scientific **pilot** remains the FishAI recommendation: **private** Pacific oyster 72 h **ops-stress indicator**, Category D, air+tide+wave, DOH separate — still **NO-GO** until food-safety wall and human reviewers (`scientific_red_team` handoff). That pilot is **not** an observatory.

---

## 5. Peer review — what three skeptics reject in “track everything”

These are the reviews that would arrive on a *Nature* / *ICES JMS* / *Mol. Ecol. Resour.* desk. Software cannot sign them.

### 5.1 Skeptical fisheries scientist

**Would reject:**

1. Abundance or biomass language without a **survey design** (stratification, detectability, gear selectivity).  
2. CPUE-as-N (Harley 2001; ASMFC 2025 hyperstability warning).  
3. Spatial products that treat unfished cells as true zeros.  
4. 24–48 h operational forecasts justified with **climate-scale** SDMs.  
5. Mixing stocks (ocean Chinook ESUs) into one “species layer.”  
6. Training across management-era breaks (Maine 10% → 100% reporting; gauge changes) as one index (Hodgdon et al. 2025).  
7. Any map that would concentrate effort on listed units or nursery sites.  
8. Validation by random CV or by beating a random baseline instead of **seasonal-spatial climatology**.  
9. Hardware promises substituting for **partner outcomes**.  
10. The phrase “the AI sees the fish.”

**Would accept, narrowly:** Category C/D, effort defined, uncertainty, UNKNOWN cells, prospective beat of B12/B3, human-readable limitations.

**Quote they would write:** *This is a habitat and effort model with a life-shaped colormap.*

### 5.2 Skeptical acoustician

**Would reject:**

1. Biomass from uncalibrated, unknown-beam, unknown-\(\alpha\) sounders.  
2. Species ID from single-frequency NASC without TS models and biological sampling.  
3. Dead-zone and bubble-blind near-surface/near-bottom “census.”  
4. One frequency for both basin-scale **and** fish-body resolution (`physical_limits.md` §3).  
5. DAS as a fisheries echosounder: **gauge length 8–30 m**, bandwidth often **≲ few hundred Hz** on long cables, measurement is **axial strain**, not TS (Bouffaut/Landrø 2022).  
6. Ignoring ±2 dB km⁻¹ \(\alpha\) uncertainty and the 333 kHz formula failure (Macaulay, Chu & Ona 2020).  
7. TB/day DAS streams “classified by AI” without labeled precision/recall and independent hydrophones.  
8. Shipping noise and fish choruses mixed into “biomass.”  
9. Real-time water-column cubes over acoustic modems (kbps vs EK80 data rates).  
10. Publishing fine DAS localizations of whales.

**Would accept, narrowly:** Designed, sphere-calibrated surveys as Category B **in the surveyed unit**; DAS as **research PAM** for loud low-frequency sources with stated localization error.

**Quote they would write:** *You cannot buy range, resolution, and identity with the same ping, and a fiber is not a calibrated split-beam.*

### 5.3 Skeptical molecular ecologist

**Would reject:**

1. eDNA detection = animal present at the bottle GPS at sampling instant.  
2. Read counts or Ct as abundance without shedding, decay, dilution, and inhibition models (Sassoubre 2016; Collins 2018).  
3. Spatial grain finer than the **plausible plume** (literature spans tens of meters to tens of km).  
4. Metabarcoding species lists without: marker, reference **build date**, occupancy of the database, blank/negative rates, LOD, and contamination protocol.  
5. Primer bias and drop-outs sold as true absences.  
6. Cross-lab, cross-kit time series as a continuous index.  
7. eDNA as 24–72 h farm mortality or Chinook bite.  
8. “Global eDNA observatory” without a sampling design (again: effort vs biology).  
9. Secondary use of sequences that re-identifies sensitive locations or listed species.  
10. AI taxonomic assignment treated as ground truth.

**Would accept, narrowly:** Occupancy / relative community composition with hydrodynamics, assay metadata, independent visual/acoustic subset, and UNKNOWN off-transect.

**Quote they would write:** *You sequenced a water parcel’s recent biological exhaust, not a census, and the parcel moved.*

---

## 6. Claims that must never appear (observatory channel)

In addition to FishAI never-claims:

- “Track everything,” “living ocean digital twin of all species,” “real-time biomass cube,” “satellite fish finder.”  
- “eDNA GPS,” “DAS fish map of the EEZ,” “AI-tagged population.”  
- Completeness percentages that count interpolated cells as observed.  
- Cross-species transfer as a solved problem.  
- Investor metrics of “species tracked” that count GBIF rows or AIS MMSI.

---

## 7. Required limitation language (minimum)

If any observatory-shaped sentence is ever issued (not recommended now):

> This is a **partial observation** from named sensors, not a census of saltwater life. Satellites do not see most fish. Unsampled cells are **UNKNOWN**, not zero. Habitat and vessel traffic are not abundance. Not legal harvest, navigation, food safety, or a catch guarantee. Model version [x]. Independent validation: **not operational (below support T6).**

Wedge-specific paragraphs in `prediction_contract.md` still apply if a FishAI brief exists.

---

## 8. Human reviewers required (cannot be this agent)

| If the artifact includes… | Human seat |
|---|---|
| Any biological map or score | Fisheries scientist (stock/survey literate) |
| Acoustics or DAS | Fisheries/PAM acoustician |
| eDNA / metabarcoding | Molecular ecologist |
| Oyster + temperature | Shellfish + NSSP (FishAI B-OYS-01) |
| Chinook maps | Salmon biologist + ESA/effort review |
| Lobster maps | GOM assessment + confidentiality |
| Public coordinates | Privacy/legal |

Silence is not acceptance.

---

## 9. Residual questions for humans

- Is **any** public biological heatmap net-positive once leakage and ESA are priced in?  
- Minimum n for blocked CV on a chosen wedge (Quality hypotheses are **not** proven).  
- Public-health: is oyster “stress” still too close to Vp controls?  
- Can DAS whale detectors be run **without** storing localizable waveforms?  
- After sibling product copy lands: did anyone say “observatory,” “digital twin,” or “abundance”? **Re-open this report.**

---

## 10. Smallest falsifying experiments (do not train a foundation model)

1. **Coverage honesty:** Take 30 days of ocean-color + SST over a candidate AOI. Report fraction of cells with a **same-day** valid pixel. If marketing said “continuous,” this number falsifies it.  
2. **Effort null:** Predict OBIS/GBIF presence from distance-to-port + depth only vs adding SST/chl. If biology adds nothing, stop occupancy maps.  
3. **Baseline:** On any proposed nowcast, score B12 vs the model on a held-out year. Predicted result: climatology wins or ties (FishAI Chinook experiment).  
4. **Physics:** SST-only vs air×tide on 2021 oyster mortality narratives (already specified in marine-domain E1). If SST wins, labels are wrong.

**Stop condition:** any experiment that needs public hotspots, AIS-as-fish, closure-as-biology, or interpolated UNKNOWN cells.

---

## 11. Status board

| ID | Status 2026-09-18 |
|---|---|
| RT-OBS-01 … 15 | OPEN |
| FishAI RT-XCUT / RT-OYS / RT-CHK / RT-LOB | OPEN (sibling file) |
| Customer-facing observatory biology | **NO-GO** |
| Support T3–T6 assigned | **0** |
| T6 operational grade | **Not met** |

Re-review when founder locks a wedge, when product copy uses observatory language, or when anyone proposes training.
