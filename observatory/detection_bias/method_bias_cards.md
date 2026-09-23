# Method-specific bias cards

**Date:** 2026-09-18  
**Status:** Literature + design. **No fitted FishAI \(p\) values.**  
**How to read:** each card states the detection process, typical bias direction, what is **knowable today**, what is **not**, occupancy-state mapping, and citations (accessed 2026-09-18; cite only).

Cross-cutting physics: `../observation_modality_catalog.md`, `../physics_feasibility_reports/physical_limits.md`.

Default if a card’s covariate is missing: **do not invent \(p\)**. Drop the trial or mark `DATA_UNAVAILABLE` / `effort_unknown`.

---

## Card 1 — Visual survey (boat, dive, intertidal walk, aerial)

### Process
Human (or aerial observer) searches a strip/point. Detection = **availability** (animal is visible) × **perception** (observer records it) (Marsh & Sinclair 1989 *J. Wildl. Manage.* marine-mammal split; Buckland et al. distance sampling).

### Bias direction
- **False negatives:** turbid water, glare, sea state, depth beyond optical path, cryptic / buried / nocturnal taxa, observer fatigue, fast transit.  
- **False positives:** look-alike taxa, sun glitter as animals, double-count on closing mode.  
- **Spatial:** surveys where it is safe and funded (coastal daylight).

### \(p\) drivers (this method)
Effort (km, minutes, # quadrats), observer skill, sea state, glare, water clarity, altitude/speed (aerial), emersion (intertidal), time of day, species size/contrast, behavior (surfacing, gaping).

### Knowable today
- Distance-sampling and availability-bias **theory**.  
- Marine-mammal survey programs exist (NOAA/DFO) with published detection-function practice.  
- Intertidal: emersed oysters/gaper shells are **highly detectable** to a walker on that tide; subtidal individuals are not.  
- **Not knowable:** a global visual \(p\) raster; dive \(p\) for mesopelagic fish.

### State mapping
Walk/survey with protocol + zero count → `NOT_DETECTED`.  
No survey block occupied that day → `NO_OBSERVATION`.  
Exhaustive bed map with high \(p\) + photos → possible `TRUE_ABSENCE_SUPPORTED` at **bed grain only**.

### Literature
Buckland et al. *Distance Sampling*; Marsh & Sinclair 1989; Barlow detection-function papers; Raymond et al. 2022 (intertidal heat-kill **visible** on emerged substrate — detectability of **already-dead** intertidal fauna, not of delayed cryptic mortality).

---

## Card 2 — Camera (BRUV, unbaited, ROV, farm CCTV, animal-borne)

### Process
Finite field of view, metres of range. Classification by human or ML. Baited systems **change behavior** (attraction), so \(p\) is not a density coefficient without a movement model (Cappo; Langlois; Whitmarsh, Fairweather & Huveneers 2017 *JEMBE* BRUV review).

### Bias direction
- Bait: inflates \(p\) for scavengers/predators; may depress for bait-shy taxa.  
- Lights: attraction or avoidance.  
- Turbidity / night / biofouling: \(p \to 0\).  
- ML domain shift: new water mass, new camera, new season → missed classes.  
- MaxN is **relative** in the FOV, not \(N\) in the cell.

### \(p\) drivers
Soak time, bait type, visibility, illumination, stereo vs mono, deployment habitat, time of day, species, model-ID skill, fouling.

### Knowable today
Operational on reefs, some observatories, aquaculture nets. Stereo-BRUV length methods exist **locally**.  
**Not knowable:** unbaited \(p\) for oceanic pelagics at observatory grain; species-complete ML.

### State mapping
Empty video with documented soak + visibility → `NOT_DETECTED`.  
Corrupt/fouled/no retrieval → `DATA_UNAVAILABLE`.  
No camera in cell → `NO_OBSERVATION`.  
ID from video → `PRESENT_OBSERVED` (`DIRECTLY OBSERVED`), individual ≠ population.

### Literature
Whitmarsh et al. 2017; Langlois et al. stereo-BRUV methods papers; modality catalog §3.3.

---

## Card 3 — Sonar / active acoustics (and PAM note)

### Process
**Active:** backscatter → NASC / TS. Species ID **not unique** when TS spectra overlap (ICES CRR 344; Korneliussen & Ona; Jones et al. NOAA pollock broadband: no clear pattern among many swimbladder fishes 15–150 kHz).  
**Passive:** vocalizing taxa only. **Silence ≠ absence** (modality catalog §3.5).

### Bias direction
- Near-surface **blind zone**; near-bottom **dead zone** (shellfish, lobster poorly inventoried by pelagic EK).  
- Vessel avoidance lowers \(p\).  
- Siphonophore resonance mimics fish.  
- Mixed aggregations: classification error.  
- PAM: seasonal calling, masking by ships, frequency-dependent range.

### \(p\) drivers
Frequency, pulse, SNR, vessel speed, sea state/bubbles, depth vs beam, calibration, ID-haul prior, calling rate (PAM), behavior (swimbladder, orientation).

### Knowable today
Survey standards for **validated, often swimbladdered, monospecific** aggregations. Opportunistic fishing-vessel EK **exists** but is rarely open.  
**Not knowable:** species-resolved global \(p\); lobster count from EK; fish N from DAS (DAS is low-frequency, whales/ships).

### State mapping
Calibrated transect, no echo in layer, with ID prior that the taxon would mark if present → `NOT_DETECTED` **of backscatter**, still not true absence of silent/low-TS taxa.  
No ship track → `NO_OBSERVATION`.  
Uncalibrated sounder → `DATA_UNAVAILABLE` or inferred only.

### Literature
Simmonds & MacLennan *Fisheries Acoustics*; ICES CRR 344 https://doi.org/10.17895/ices.pub.4567; Korneliussen et al. https://doi.org/10.1093/icesjms/fsp119; Jones NOAA pollock broadband.

---

## Card 4 — eDNA (decay, transport, contamination)

### Process
Detected DNA means **molecules at the filter**. Occupancy of molecules ≠ pin of the animal. Persistence often **hours to ~1 day**; modeled transport **&lt;1 km to tens of km**, often **exceeding** field detections (Harrison et al. 2019; Andruszkiewicz et al.; Murakami et al. 2019 ~30 m empirical vs ~10 km modeled; *Environmental DNA* / Frontiers 2025 spatial-bound: modeled median ~2.27–14.14 km). Lifetime simulations ~5–30 h, transport ~0.3–39 km (Bay of Biscay Lagrangian example in modality catalog).

### Bias direction
- **False positives:** contamination, PCR artifacts, rare-species inflation (Darling, Jerde & Sepulveda 2021), downstream transport from a distant source.  
- **False negatives:** primer dropout, inhibition, reference-library holes, stratified sampling across a thermocline, decay before filtration.  
- Reads ≠ biomass; shedding unknown.

### \(p\) drivers
Volume filtered, marker/assay LOD, inhibition, blanks, temperature (decay), UV, microbial activity, hydrodynamics, tissue source (mucus vs gametes), lab protocol, contamination controls.

### Knowable today
Occupancy/community **research** is operational-adjacent (NOAA Omics; eDNA2OBIS path). Assay metadata **must** travel with any hit.  
**Not knowable:** abundance; exact location; a universal marine decay constant.

### State mapping
Hit at filter → `PRESENT_OBSERVED` of **DNA**, output class molecular; spatial meaning = plume. Infer animal occupancy only with a **hydrodynamic kernel** → usually `PRESENT_INFERRED` for the **animal**.  
Clean non-detect with blanks OK + volume documented → `NOT_DETECTED` of DNA at station (animal may still be upstream/downstream).  
No sample → `NO_OBSERVATION`.  
Failed blank / no LOD → `DATA_UNAVAILABLE`.

### Literature
Harrison et al. 2019 https://pmc.ncbi.nlm.nih.gov/articles/PMC6892050/ ; Andruszkiewicz et al. 2019 https://doi.org/10.1038/s41598-019-40788-z ; Darling et al. 2021; hypothesis card `H-4.1_global_ocean_edna_mesh.md`.

**Never** train animal-absence from a single uncalibrated non-detect.

---

## Card 5 — Tag-selection (telemetry)

### Process
Tagged animals are a **biased subset** of the population (Sequeira et al. 2021 *MEE* https://doi.org/10.1111/2041-210X.13507): catchability, size, tagging location, device, duty cycle, premature failure, processing.

### Bias direction
- Release-site inflation of apparent habitat.  
- Small/cryptic/unwholesome animals dropped.  
- Capture survivors ≠ random.  
- Surface-oversampling on some PSAT duty cycles.  
- Premature pop-off censors mortality and long trips.  
- Acoustic arrays only where receivers exist (`NO_OBSERVATION` off-array, not absence).  
- Individuals ≠ population.

### \(p\) / selection drivers
Gear used to catch taggees, size window, location, tag type, duty cycle, array geometry, processing SSM vs raw.

### Knowable today
ATN/OTN/AniBOS exist; QC flags implausible points **do not** fix representativeness (modality catalog §3.7).  
**Not knowable:** population occupancy from n tags without a design-based or explicit selection model.

### State mapping
Tag fix → `PRESENT_OBSERVED` / `TAG/TELEMETRY-DERIVED` for **that individual**.  
No tag in cell → `NO_OBSERVATION` of tagged subset, **not** `NOT_DETECTED` of the stock.  
Do not invent stock-level `TRUE_ABSENCE_SUPPORTED` from empty tag maps.

---

## Card 6 — Vessel / catch effort

### Process
Catch is \(N \times q \times E\) with catchability \(q\) unknown and effort \(E\) poorly observed. **Catch ≠ abundance.** CPUE hyperstability: CPUE stays high while biomass falls when animals aggregate and gear finds aggregations (Harley, Myers & Dunn 2001 *CJFAS*). Trap saturation further flattens CPUE (Watson et al. 2019 *Fish. Bull.*).

### Bias direction
- Targeting, price, weather, skill, regulation, bag limits (truncation).  
- Misreporting, discarded catch.  
- Spatial preference: fishers go where \(q \times\) price is high.  
- AIS/VMS: **selected transmitting subset**, confidential VMS (NMFS 06-101).  
- Dealer landings without effort: **not** a detection process.

### \(p\) / \(q\) drivers
Soak, bait, gear, depth, **bottom T** (lobster activity), swell, crew, management era (gauge, vents), saturation / trap density.

### Knowable today
The inequality CPUE ≠ \(N\) is **settled**. Partner logs with effort can support Category **C**. Public monthly RecFIN/CRFS ≠ 24–48 h trials. Maine 100% e-reporting since 2023 is lagged and coarsened (one TMS per trip).  
**Not knowable:** inshore lobster effort from AIS (Card 6b / W3 note).

### State mapping
Trip with effort and zero catch → `NOT_DETECTED` (encounter), **not** stock absence.  
No trip → `NO_OBSERVATION`.  
Confidential log not licensed → `DATA_UNAVAILABLE` / `RIGHTS`.  
AIS ping → traffic, **not** \(y\).

### Literature
Harley et al. 2001; Maunder & Punt CPUE standardization reviews; ASMFC 2025 lobster assessment / peer review (hyperstability; bottom T catchability); Hodgdon et al. 2025 reporting-protocol breaks.

---

## Card 7 — Citizen-science participation

### Process
Opportunistic records (iNaturalist, eBird-at-sea, strandings, HAB photos). Effort is **participation**, not a survey grid. Spatial bias to beaches, ports, weekends, photogenic taxa (Isaac et al. 2014 occupancy-for-citizen-science; Geldmann et al. 2016).

### Bias direction
- Presence-only.  
- Mis-ID.  
- Harassment risk if locations published.  
- TEK is **not** a free citizen dataset (CARE; default `NEVER_PUBLISH` unless licensed).

### \(p\) drivers
Human density, access, weather, platform UX, taxon charisma, event (stranding, slime), moderation/QA.

### Knowable today
eBird-style **checklist occupancy** can work **when effort is in the protocol**. iNaturalist marine is uneven QA.  
**Not knowable:** mesopelagic occupancy; a zero from “no iNaturalist points.”

### State mapping
Verified photo → `PRESENT_OBSERVED` (privacy coarsen).  
No records in cell → `NO_OBSERVATION`.  
**Never** `NOT_DETECTED` unless a **protocol checklist** with effort (complete eBird-like list) says the taxon was looked for.

### Literature
Isaac et al. 2014 *Methods Ecol. Evol.*; Johnston / Fink eBird occupancy series; modality catalog §3.13; Webb et al. 2010 OBIS bias.

---

## Card 8 — Satellite surface-visibility

### Process
Photons from the **first optical depth** (often &lt;1–10 m coastal; ~0 for TIR skin). Pixel vs organism: VIIRS ~750 m; OLCI ~300 m; VHR ~0.3–2 m **and** animal at/near surface, low sea state, low glint, low cloud (modality catalog hard limits 1–2). SST/ocean color are **not** animals (Williamson et al. 2019: shark “satellite” papers are usually habitat covariates).

### Bias direction
- Cloud, night, glint, turbidity → **no optical trial**.  
- Subpixel mixing.  
- VHR whale CNNs: availability at surface; species ID limited.  
- Intertidal: can map **beds/structures** under conditions; **not** bag-level mortality.  
- Coral DHW: heat stress, not polyp counts.

### \(p\) drivers
Kd, clouds, glint, sea state, pixel size, taxon size/contrast, sun zenith, atmospheric correction, coastal adjacency.

### Knowable today
Operational: SST, color, *Sargassum*, HAB **proxies**, shallow habitat. Research: some whales/pinnipeds/seabird colonies.  
**Impossible now:** finfish/crustacean/shellfish **individuals** below optical depth; lobster from SST.

### State mapping
Cloud/night/glint on optical pass → `NO_OBSERVATION` for imagery (physics), not `NOT_DETECTED` of fish.  
Clear pass, VHR, expert/CNN whale with QA → `PRESENT_OBSERVED` / `REMOTELY DETECTED` of **that surfacing**, not census.  
SST pixel → **never** `PRESENT_OBSERVED` of oysters/Chinook/lobster.

### Literature
Gordon & McCluney 1975 optical depth; Cubaynes / DFO 2022 *Megafauna from Space*; Williamson et al. 2019 https://doi.org/10.3389/fmars.2019.00135 ; `../satellite_capability_matrix.md`.

---

## Card 9 — Survey-season (seasonal availability vs occupancy)

### Process
Many programs sample **a season**, not a year: summer VTS, spring trawl, calling-season PAM, daylight BRUV, open salmon months only. Seasonal **availability** (molt, calling, emersion heat, migration) is a \(p\) process; seasonal **range** is a \(\psi\) process. Conflating them paints animals as absent in unsampled months.

### Bias direction
- Lobster: temperature-cued activity → summer CPUE ≠ winter occupancy.  
- PAM: non-calling season silence ≠ absence.  
- Chinook: closed season has **no legal encounter trial**.  
- Oyster: winter storms vs summer heat — different **detectable** harms.

### \(p\) drivers
Month, phenology priors, calling catalogs, molt timing (Mills et al. 2017 season-**start**, weeks not hours), survey calendar.

### Knowable today
Program calendars are public. Phenology priors exist at **season** scale.  
**Not knowable:** 24–48 h availability from a seasonal survey mean.

### State mapping
Off-season, no protocol → `NO_OBSERVATION` (or `DATA_UNAVAILABLE` if a different program’s data exist but are out of window).  
Do not carry summer VTS zeros into January as `TRUE_ABSENCE_SUPPORTED`.

---

## Card 10 — Habitat-access (sampling access, not habitat suitability)

### Process
Observers sample **accessible** habitat: ports, shelves, diving depths, lease roads, fair-weather windows, EEZ permissions. OBIS/GBIF map **access + funding** (Webb, Vanden Berghe & O’Dor 2010; Menegotto & Rangel 2018 depth bias). Distance-to-port is an **effort-null** (RT-OBS-03).

### Bias direction
- Deep, polar, ABNJ, turbid, restricted, and unsafe cells under-sampled.  
- “Range edge” often = end of the ship-day.  
- Habitat-suitability models trained on accessible presence **learn access**.

### \(p\) / effort-null drivers
Distance-to-port, depth, slope, ice, wind climate, permitting, income/tourism, language of platforms.

### Knowable today
Bias is **certain** in occurrence DBs. Target-group background (Phillips et al. 2009) can **reduce** (not eliminate) access bias for **presence-background SDMs**, and still does **not** create absences.

### State mapping
Inaccessible / unsampled cell → `NO_OBSERVATION`.  
Do not code deep water as `NOT_DETECTED` for a surface visual survey.

### Literature
Webb et al. 2010; Menegotto & Rangel 2018 *Nat. Ecol. Evol.*; Phillips et al. 2009 *Ecol. Appl.* target-group background; Robinson et al. sampling-bias SDM reviews; observatory red team RT-OBS-03.

---

## Cross-card cheat sheet

| Method | Empty database | Documented zero trial | High-bar unoccupied |
| --- | --- | --- | --- |
| Visual / walk | `NO_OBSERVATION` | `NOT_DETECTED` | Possible at tiny grain |
| Camera | `NO_OBSERVATION` | `NOT_DETECTED` | Rare |
| Acoustics | `NO_OBSERVATION` | `NOT_DETECTED` of backscatter/calls | Almost never for silent taxa |
| eDNA | `NO_OBSERVATION` | `NOT_DETECTED` of DNA | Only with kernel + repeats |
| Tags | `NO_OBSERVATION` of tagged subset | N/A for untagged stock | Forbidden as stock absence |
| Catch | no trip = `NO_OBSERVATION` | zero catch with effort = `NOT_DETECTED` | Forbidden as \(N=0\) |
| Citizen | `NO_OBSERVATION` | only complete checklists | Forbidden |
| Satellite optical | cloud/night = `NO_OBSERVATION` | clear empty VHR of **surface-visible** class | Not for subsurface fish |
| Survey-season | off-calendar = `NO_OBSERVATION` | in-calendar zero | Not transferable across seasons |
| Habitat-access | no access = `NO_OBSERVATION` | — | — |
