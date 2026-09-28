# Species–geography scope (three candidate wedges)

**Agent:** MARINE_DOMAIN_AGENT  
**Project:** Ocean Intelligence Builder / FishAI  
**Date:** 2026-09-18  
**Access date for all URLs below:** 2026-09-18  
**Wedge status:** UNRESOLVED. This dossier describes three candidate species–geography–operator–horizon combinations. It does not select a product wedge.

**Prediction-target vocabulary used throughout**

| Code | Label | Meaning here |
|------|--------|----------------|
| A | Direct Count | Absolute number of animals in a defined volume/area |
| B | Survey Index | Standardized fishery-independent relative abundance |
| C | Effort-normalized catch | Catch per unit effort (CPUE), not abundance |
| D | Relative habitat-encounter-risk | Ranked chance of encountering suitable/stressful conditions or animals given habitat, not a count |
| E | Unverified indicator | Convenient ocean layer (SST, chlorophyll, AIS) treated as if it were the animal |

**Non-negotiable:** SST, AIS, and chlorophyll are never treated as fish or shellfish abundance. Food-safety harvest authorization, catch guarantees, and exact abundance are out of scope for all three candidates. Precise locations of ESA-listed salmon ESUs or large whales are not prediction targets.

---

## Candidate 1 — Pacific oyster × Washington growing areas × farm operator × 24–72 h operational stress/disruption

### 1.1 Taxonomy (WoRMS vs NOAA)

| Field | Record |
|--------|--------|
| **WoRMS accepted name** | *Magallana gigas* (Thunberg, 1793) |
| **AphiaID (accepted)** | 836033 |
| **LSID** | urn:lsid:marinespecies.org:taxname:836033 |
| **Original combination** | *Ostrea gigas* Thunberg, 1793 |
| **Principal synonym (unaccepted)** | *Crassostrea gigas* (Thunberg, 1793), AphiaID **140656**, status: unaccepted > superseded combination |
| **Other frequent synonyms** | *Crassostrea (Magallana) gigas*; *Ostrea gigas*; historically also *Ostrea talienwhanensis*, *Ostrea laperousii* (junior synonyms on WoRMS) |
| **Authority / nomenclatural note** | Genus *Magallana* Salvi & Mariottini, 2016; new combination in Salvi & Mariottini 2017 (nomenclatural availability 2016), *Zool. J. Linn. Soc.* 179:263–276. Community debate is documented (Backeljau 2018, NSA Quarterly Newsletter). |
| **NOAA Fisheries** | Header lists **both** “Crassostrea gigas; Magallana gigas”. Classification table uses Kingdom Animalia; Phylum Mollusca; Class Bivalvia; Order Ostreida; Family Ostreidae; **Genus Magallana; Species gigas**. Last updated 2026-04-13. |
| **Industry / WA agencies** | WDFW, WA DNR lease language, and most farm records still use *Crassostrea gigas*. Treat as the same biological species, not a second taxon. |
| **NCBI** | txid29159, current name *Magallana gigas* (Thunberg, 1793); homotypic synonym *Crassostrea gigas*. |
| **ITIS** | Historically catalogued as *Crassostrea gigas*; do not treat ITIS vs WoRMS as two species. |

**Disagreement summary:** WoRMS and NCBI accept *Magallana gigas*. NOAA Fisheries dual-labels the species and already uses Genus *Magallana* in its classification table. WA farm, lease, and many peer-reviewed papers still say *Crassostrea gigas*. **Use *Magallana gigas* as accepted name; retain *C. gigas* as a required synonym for data joins.**

**Official URLs**

- WoRMS accepted: https://www.marinespecies.org/aphia.php?p=taxdetails&id=836033  
- WoRMS unaccepted *C. gigas*: https://www.marinespecies.org/aphia.php?p=taxdetails&id=140656  
- NOAA Fisheries species page: https://www.fisheries.noaa.gov/species/pacific-oyster  
- NOAA InPort Olympia & Pacific oyster portal (uses *Magallana gigas*): https://www.fisheries.noaa.gov/inport/item/65431  

### 1.2 Common-name ambiguity (must disambiguate in any UI or label)

| Common name | Risk | Correct taxon |
|-------------|------|----------------|
| Pacific oyster, Pacific cupped oyster, Japanese oyster, Miyagi oyster | Target | *M. gigas* |
| Portuguese oyster | **High.** WoRMS lists “Portuguese oyster” as an English vernacular on the *gigas* synonym page; true Portuguese oyster is *Magallana angulata* / *Crassostrea angulata* | Do not synonymize |
| Olympia oyster, native oyster | **High in WA.** Different genus and ecology | *Ostrea lurida* Carpenter, 1864 (native) |
| Eastern / Atlantic / Virginia oyster | Different coast and species | *Crassostrea virginica* |
| “Oysters” in WA DOH growing-area maps | Mix of Pacific, Olympia, Manila clam, mussels | Growing-area polygons are **food-safety geography**, not a species layer |

### 1.3 Life stages in scope

Farm operator 24–72 h stress is about **already-planted stock**, not wild population abundance.

| Stage | Relevance to 24–72 h farm operations |
|--------|--------------------------------------|
| Broodstock / hatchery larvae | High for hatcheries; **out of this wedge** unless the operator is a hatchery. Larvae are the stage most sensitive to aragonite saturation state (2009 WA “oyster seed crisis”). |
| Spat / seed | High. Small seed more vulnerable to heat, handling, and (where present) OsHV-1. |
| Juvenile grow-out | High. Summer mortality literature is often juvenile/submarket. |
| Market-size adults | High. 2018–2019 and 2021 WA events killed market oysters as well as seed. |
| Wild set on reserves | Secondary. WDFW Willapa oyster reserves exist, but the operator is a **farm**, not a wild-stock assessment. |

Adults are sessile after settlement. That is the scientific reason this candidate can support a **Category D** target: the animals do not leave the lease in 72 h. Biomass on the lease is known to the operator; the question is **stress/disruption risk**, not “where are the oysters.”

### 1.4 Geography (Washington growing areas)

**Intended spatial frame:** commercial aquaculture leases and adjacent classified growing waters in Washington State, especially:

- **Willapa Bay** (Pacific County) — largest historical Pacific oyster production; WDFW state oyster reserves (Nemah, Long Island, Long Island Slough, Bay Center, Willapa River; RCW 77.60.010); DNR aquaculture leases on state-owned tidelands.
- **Grays Harbor**
- **Puget Sound / Salish Sea**, including South Sound, Whidbey Basin, Discovery Bay, Hood Canal

**DOH “growing areas” are a spatial convenience, not the prediction target.** Washington State Department of Health classifies commercial growing areas (Approved, Conditionally Approved, Restricted, Prohibited) under the National Shellfish Sanitation Program (NSSP) using sanitary surveys and fecal-coliform water quality. Those polygons locate farms. **They authorize human harvest, they do not measure oyster physiological stress.** Biotoxin and *Vibrio* closures are likewise **food-safety / legal harvest** and are **explicitly out of this wedge**.

Official growing-area URLs:

- https://doh.wa.gov/community-and-environment/shellfish/growing-areas  
- Commercial Shellfish Map Viewer: https://fortress.wa.gov/doh/oswpviewer/index.html  
- WA DNR aquaculture leasing: https://dnr.wa.gov/aquatics/shellfish/aquaculture  

**Recommended bounded v1 geography (scientific, not founder-locked):** one estuary with mixed intertidal and off-bottom culture and existing sensors — **Willapa Bay** *or* **a named South/Central Puget Sound growing-area cluster** — not “all Washington tidelands.” Hood Canal hypoxia and Willapa heat/food gradients are different mechanisms; pooling them without a site ID will confound a 72 h model.

### 1.5 Operator and horizon

- **Operator:** farm manager (bottom culture, bag/rack, longline, or raft). Decisions in 24–72 h: delay handling, lower bags, add shade/cooling, postpone planting, retrieve gear before a blow, change tidal work windows.
- **Horizon:** 24–72 h operational **stress/disruption**, not harvest legality.
- **In-scope disruption classes:** aerial/marine heat, hypoxia, acute low salinity from runoff, storm/wave gear loss, feeding shutdown from some HABs, handling mortality during already-stressful conditions.
- **Out of scope:** NSSP harvest classification, PSP/DSP/ASP biotoxin harvest bans, *Vibrio parahaemolyticus* post-harvest controls, tribal/civil harvest rights.

### 1.6 Habitat requirements and covariates

**Causal / biologically relevant at 24–72 h**

| Variable | Mechanism (farmed *M. gigas*) | Notes |
|----------|-------------------------------|--------|
| **Air temperature × tidal emersion** | Intertidal animals experience aerial heat and desiccation at low tide. The June 2021 PNW heat dome coincided with the year’s lowest tides and caused mass intertidal mortality (Raymond et al. 2022, *Ecology*; Washington Sea Grant Rapid Response Network). Pacific oysters were more affected than lower-intertidal Olympia oysters. | Strongest 24–72 h signal for intertidal culture. |
| **Water temperature** | Eurythermal, but summer mortality and heat-wave mortality rise as water and tissue temperatures climb. NANOOS grower guidance flags water >64°F (~17.8°C) for >24 h as concern; literature often associates elevated risk near ~19–20°C with co-stressors (Cheney et al. 2000). FAO culture envelope is much wider (−1.8 to 35°C survival; spawning generally >18–20°C). | Causal for metabolism, spawning, *Vibrio*, and OsHV-1 risk *where virus is present*. |
| **Dissolved oxygen** | Hypoxia is a documented co-stressor in Puget Sound summer mortality (Cheney et al. 2000: elevated temperature, neap tides, oxygen-depleted water). Hood Canal and some South Sound basins stratify. FAO culture sheet: DO >2 mg L⁻¹ as a culture minimum — that is a floor, not a no-effect level. | Causal, highly local. Satellite DO does not exist. |
| **Salinity / runoff** | Euryhaline (culture often 10–35; optimum often cited ~20–25). Acute freshwater pulses increase TSS, drop DO, and can add contaminants; mortalities after floods are typically **multi-stressor**, not salinity alone. | Causal for estuarine leases after rain. |
| **Tides** | Control emersion duration, neap-tide flushing (DO), and work windows. | Causal as a **modulator**, not a toxin. |
| **Storms / wind / waves** | Gear loss, burial, stranding, handling impossibility. | Causal for **disruption**, not physiology. |
| **HABs that affect the oyster (not the eater)** | *Heterosigma*, *Protoceratium reticulatum*/yessotoxins, and high-biomass blooms can reduce feeding or add toxicity to the animal (WDFW 2019 die-off notes; SoundToxins). Distinct from Alexandrium PSP **harvest** closures. | Mixed: some causal for stress, many HAB products are food-safety. |
| **Spawning / condition** | Summer spawning is energetically expensive; “summer mortality” often hits ripe animals. Trigger is seasonal degree-days, not a 48 h forecast of gamete release. | Seasonal confounder. |
| **Culture method / tidal elevation / crowding** | Intertidal vs subtidal, bag vs bottom, density, and handling determine exposure. Same weather, different mortality. | Causal but **operator-controlled**. |
| **Disease (OsHV-1, *Vibrio* spp.)** | OsHV-1 has caused CA farm mortalities; USDA-ARS sentinel work did **not** detect OsHV-1 at tested OR/WA sites in 2020 (Dumbauld et al. DAO 2023). Still a WA R&D priority (heat × virus). Bacterial secondary infection after heat/hypoxia is plausible. | Do not assume OsHV-1 is the WA 72 h driver without farm PCR. |

**Available but not causal for 24–72 h farm stress (proxies / wrong question)**

| Variable | Why it is not the target |
|----------|-------------------------|
| **Satellite SST** | Useful **proxy** for water heat in well-mixed shallows; misses aerial temperature, intertidal microclimate, and stratified bottom water. Not oyster abundance (oysters are planted). |
| **Chlorophyll-a** | Food for growth and condition (Willapa “fattening line”: lower estuary higher chl, faster growth; Ruesink et al. / Lowe et al. in PMC7809371). Weak as a 72 h **mortality** predictor unless a crash or HAB. **Never abundance.** |
| **pH / Ω_aragonite** | First-order for **larval** calcification (2009 seed crisis; NOAA OAP). Adult shells already formed; 72 h farm-adult mortality is rarely a pH event. |
| **Nutrients** | Drive phytoplankton; indirect. |
| **Currents / residence time** | Explains Willapa spatial growth patterns (Banas et al. 2007 residence-time contrast) at seasonal scale, not 48 h mortality. |
| **Moon** | Only via tides. |
| **AIS** | Irrelevant to sessile farm stock. |
| **Fecal coliform / NSSP class** | Harvest legality, not animal stress. |

### 1.7 Confounders

- **Ploidy and pedigree:** triploid vs diploid; Molluscan Broodstock Program / USDA-ARS Pacific Shellfish Breeding Center families differ in summer survival.
- **Prior stress / priming:** previous heat or handling changes subsequent mortality.
- **Microhabitat:** bag color, orientation, mud vs gravel, shade, elevation in cm.
- **Co-occurring species:** burrowing shrimp, eelgrass, fouling.
- **Operator behavior:** the decision the model would advise is also a confounder of observed mortality.

### 1.8 What cannot be predicted at useful 24–72 h resolution

- Absolute mortality percent on a bag without on-site temperature/DO and culture metadata.
- Viral load / OsHV-1 outbreak timing in WA (virus not established as the local 72 h driver).
- Food-safety closure (out of scope; also a regulatory, not biological, process).
- Larval settlement / wild set over 72 h.
- Bay-wide “oyster abundance.”

### 1.9 Appropriate prediction target

**Category D — Relative habitat-encounter-risk of operational stress/disruption** on a named lease or growing-area cluster over 24–72 h, stratified by culture method (intertidal vs subtidal).

Not A (farmers already know how many bags they planted). Not B (no standardized coastwide farm-mortality survey). Not C (this is not a capture fishery). Not E (do not ship SST as “oyster risk” without tide × air × local water).

### 1.10 Standardized survey / assessment data?

**No Pacific oyster stock assessment analogous to ASMFC lobster or PFMC salmon.** Farmed *M. gigas* in WA is an introduced aquaculture species (NOAA: introduced from Japan in the 1920s by the Washington Department of Fisheries).

What **does** exist (lawful, official or published; not ingested here):

| Program | What it is | Fit to 24–72 h farm stress |
|---------|------------|----------------------------|
| WA DOH growing-area monitoring | Fecal coliform, sanitary survey, biotoxins | **Wrong target** (food safety) |
| NANOOS NVS Shellfish Growers | Temperature, salinity, chl, turbidity, DO, some carbonate | **Right variables**, sparse sites |
| Padilla Bay NERR / Ecology / ORCA Hood Canal | Estuarine time series | Good covariates, not farm mortality |
| SoundToxins (WA Sea Grant + NWFSC origin) | HAB cells, some temp/salinity | HAB stress vs harvest toxin must be split |
| Pacific Shellfish Institute / grower mortality logs | Farm mortality, some experiments | Best **ground truth** if shared; not a public survey |
| WDFW medium report on 2019 die-offs | Event narrative | Historical case, not a time series |
| USDA-ARS PSBC sentinel OsHV-1 | Disease surveillance | Disease, seasonal |
| Willapa oyster reserves (WDFW) | Managed naturalized set / seed | Not 72 h stress |

### 1.11 Key scientific references and local expert orgs

- NOAA Fisheries Pacific oyster: https://www.fisheries.noaa.gov/species/pacific-oyster  
- FAO cultured species fact sheet (*C. gigas*): https://www.fao.org/fishery/docs/CDrom/aquaculture/I1129m/file/en/en_pacificcuppedoyster.htm  
- Cheney, D.P., B.F. Macdonald, R.A. Elston. 2000. *J. Shellfish Res.* 19:353–359. Puget Sound multi-stressor summer mortality.  
- Raymond, W.W. et al. 2022. Assessment of the 2021 heatwave on Salish Sea intertidal shellfish. *Ecology* https://doi.org/10.1002/ecy.3798  
- Washington Sea Grant Rapid Response Network: https://waseagrant.uw.edu/our-programs/seafood-fisheries-aquaculture/aquaculture/rapid-response-network/  
- WDFW 2019 die-off note: https://wdfw.medium.com/whats-been-causing-mass-shellfish-die-offs-around-puget-sound-1ada7071a242  
- Willapa growth / food: PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC7809371/  
- NANOOS Shellfish Growers: https://nvs.nanoos.org/ShellfishGrowers  
- SoundToxins: https://soundtoxins.org/about.html  
- Pacific Shellfish Institute: https://www.pacshell.org/  
- USDA-ARS Pacific Shellfish Breeding Center / OSU MBP: https://marineresearch.oregonstate.edu/comes/molluscan-broodstock-programusda-ars-pacific-shellfish-breeding-center  
- NOAA Ocean Acidification Program (larval context): https://oceanacidification.noaa.gov/  

Evidence tiers for this candidate are dominated by **tier 1–2** physical mechanisms (heat × tide, DO) and **tier 2–3** farm mortality observations. There is **no** tier-1 24–72 h operational-stress forecast product today.

---

## Candidate 2 — Chinook salmon × bounded CA/OR coastal area × charter captain × 24–48 h relative encounter likelihood

### 2.1 Taxonomy (WoRMS vs NOAA)

| Field | Record |
|--------|--------|
| **WoRMS accepted name** | *Oncorhynchus tshawytscha* (Walbaum, 1792) |
| **AphiaID** | 158075 |
| **LSID** | urn:lsid:marinespecies.org:taxname:158075 |
| **Original name** | *Salmo tshawytscha* Walbaum, 1792 |
| **ITIS TSN** | 161980 — valid; authority “Walbaum in Artedi, 1792” |
| **NCBI** | txid74940; heterotypic spelling *O. tschawytscha* |
| **NOAA Fisheries** | *Oncorhynchus tshawytscha*; also known as king, spring, tyee, winter, quinnat, blackmouth. Page: https://www.fisheries.noaa.gov/species/chinook-salmon |

**Disagreement summary:** **None material.** WoRMS, ITIS, NCBI, and NOAA agree on the species. Record the Walbaum vs “Walbaum in Artedi” authority string difference only.

### 2.2 Common-name and stock ambiguity

| Label | Risk |
|-------|------|
| King salmon | Same species; standard CA/OR sport name |
| Spring salmon | Can mean spring-run **life history**, not a different species |
| Blackmouth | Immature resident/ocean Chinook (Puget Sound usage); not the typical CA/OR ocean charter target |
| Quinnat | Same species (older / Southern Hemisphere name) |
| Silver / coho | **Different species** *O. kisutch*; CA ocean coho retention is prohibited |
| Steelhead | *O. mykiss*; not the ocean Chinook charter target |
| “Salmon” in CRFS/ORBS tables | Chinook + coho (and rare pink); must filter species |
| ESA ESUs mixed in the same ocean catch | California Coastal, Sacramento winter-run, Central Valley spring-run, and others can co-occur with hatchery Central Valley fall Chinook. **Do not emit precise locations or stock-specific hotspots for listed ESUs.** |

Ocean fisheries off CA/OR catch a **mixture of stocks**. Recreational GSI work shows Central Valley Fall Chinook usually dominate California sport catch, with stock-specific CPUE patterns that change through summer (Satterthwaite / CSUMB GSI analyses). Klamath River fall Chinook is a management constraint, not a guarantee of local encounter.

### 2.3 Life stages in scope

The charter captain in 24–48 h is targeting **legal-size ocean-phase immature and maturing Chinook**, typically on the continental shelf, by troll or mooching.

| Stage | In this wedge? |
|--------|----------------|
| Freshwater egg–fry–smolt | No (except as lagged cohort size, year-scale) |
| Estuary entry | No |
| Juvenile ocean (JSOES surface trawl, May–June, WA/OR) | **Wrong stage and mostly wrong geography** for a CA/OR adult charter day |
| Subadult / adult ocean (legal size) | **Yes** |
| Spawning migration in rivers | No, except late-season near river mouths where regulations often close fishing |

**Do not use juvenile Chinook–chlorophyll habitat papers as if they were adult charter encounter models.** Those papers (e.g. Bi et al.; Pool et al.; Hassrick et al. 2016 *Fish. Oceanogr.*) show juveniles concentrated in shallow, high-chlorophyll water near natal rivers. Adult archival tags (Hinke et al. 2005 MEPS 304:207–220) show a different behavior: persistent use of **8–12°C** water, often by changing **depth** when the surface warms.

### 2.4 Geography (bounded CA/OR coastal area)

**Biological range (context only):** Monterey Bay area of California to the Chukchi Sea (NOAA Fisheries Chinook page).

**Wedge geography must be bounded.** Scientifically coherent bounding units already used by managers (pick one later; none is founder-locked here):

| Candidate bound | Why it is a real unit | Caution |
|-----------------|----------------------|---------|
| PFMC/CDFW ocean salmon management areas: CA KMZ, Fort Bragg, San Francisco, Monterey | Harvest guidelines, in-season catch tracking, CRFS sampling | 2023–2024 CA sport ocean salmon was closed or nearly closed; 2026 reopened with area harvest guidelines |
| ODFW ocean catch areas: Brookings, Coos, Newport, Tillamook, Columbia | Weekly sport catch/effort estimates | Mixed Chinook/coho; weather days dominate effort |
| A single port + 3–30 nm box (e.g. Newport, OR or Fort Bragg, CA) | Matches a charter’s actual day | Sample size for 48 h validation is small |

**Recommended scientific bound for a later experiment (not a product lock):** **one PFMC recreational management area south of Cape Falcon** with an open season and published in-season catch, e.g. Newport catch area (OR) *or* San Francisco area (Point Arena–Pigeon Point). Do not mix CA KMZ with Monterey without a stock-mix model.

Official URLs:

- NOAA ocean salmon: https://www.fisheries.noaa.gov/west-coast/sustainable-fisheries/ocean-salmon-fisheries-west-coast  
- CDFW ocean salmon: https://wildlife.ca.gov/Fishing/Ocean/Regulations/Salmon  
- ODFW ocean salmon program weekly estimates (example 2026 Wk 36): https://www.dfw.state.or.us/mrp/salmon/docs/Wk_36_2026_Sport_Salmon_Estimates.pdf  
- PFMC Review of 2025 Ocean Salmon Fisheries (SAFE): https://www.pcouncil.org/documents/2026/02/review-of-2025-ocean-salmon-fisheries.pdf/  
- NOAA ocean indicators (juvenile marine **survival**, not 48 h adult encounter): https://www.fisheries.noaa.gov/west-coast/science-data/ocean-ecosystem-indicators-pacific-salmon-marine-survival-northern  

### 2.5 Operator and horizon

- **Operator:** recreational charter captain. 24–48 h decisions: go/no-go, area along the coast, depth, distance offshore, start time vs wind/swell.
- **Target:** **relative encounter likelihood** vs a local baseline (e.g. higher/lower than the recent port-area CPUE), **not** number of fish, **not** a catch guarantee, **not** a stock-assessment abundance.
- **Regulations dominate operational feasibility:** bag limits, size limits, coho prohibition, area closures, harvest guidelines. A “high habitat” day in a closed area is not an encounter product.

### 2.6 Habitat requirements and covariates

**Causal / biologically relevant for adult ocean Chinook *presence in fishable habitat***

| Variable | Mechanism | Causal vs proxy |
|----------|-----------|-----------------|
| **Thermal habitat (≈8–12°C)** | Archival tags: Chinook off CA/OR persistently occupy a narrow temperature band and change depth when SST is too warm (Hinke et al. 2004 MEPS 285; 2005 MEPS 304). | **Causal for habitat use.** SST is a **surface proxy**; fish may be deeper. **Not abundance.** |
| **Depth / shelf position** | Adults use shelf waters; recreational catch is often nearer shore than commercial troll (NOAA CWT distribution analyses). Juveniles even more nearshore. | Causal for *where to look*, not how many exist. |
| **Season / run timing / age** | Legal fish availability is seasonal (spring–fall ocean; port-specific peaks in ODFW historical tables 1979–2025). | Strong **calendar** effect; not a 24 h ocean feature. |
| **Forage (anchovy, sardine, herring, squid, krill)** | Adults piscivorous; local bait balls can concentrate fish. | Causal but **rarely observed** at 48 h with lawful public data. |
| **Upwelling / fronts / river plumes** | Structure prey and turbidity; Columbia and Klamath plumes matter regionally. | Mixed; often proxy. |
| **Wind, swell, fog** | Catchability and whether the boat leaves the harbor. | Causal for **realized encounters**, not fish density. |

**Available but not abundance, and often not 48 h encounter**

| Variable | Why not |
|----------|---------|
| **Satellite SST as “fish count”** | Habitat envelope at best. Warm SST can mean fish deeper, not absent. |
| **Chlorophyll-a** | Correlated with **juvenile** presence in WA/OR June surveys (Bi et al.; Pool et al.). For **adults**, chl indexes productivity/food-web topology (Hinke et al. 2005), not a head count. **Never treat chl as Chinook abundance.** |
| **AIS fishing-vessel density** | **Effort**, crowding, and sometimes secrecy. Not fish. Using AIS as abundance is a category error. |
| **NWFSC stoplight ocean indicators** | Built for **juvenile marine survival → adult returns 1–2 years later**, not tomorrow’s charter CPUE. |
| **PDO / ENSO / marine heatwave indices** | Seasonal to multi-year. |
| **DO, pH, nutrients** | Can constrain vertical habitat in strong upwelling (low-DO deep water), but not a 48 h fish counter. |
| **Moon** | Weak/unverified for ocean Chinook troll encounter. |
| **Tides** | Minor vs wind and thermal structure for offshore troll; more relevant near mouths (often closed). |

### 2.7 Confounders

- **Hatchery vs wild; mark-selective rules** (more north of Cape Falcon).
- **Captain skill, gear, bait, time-of-day.**
- **Crowding / secret spots** (social, not oceanographic).
- **In-season closures** when harvest guidelines are hit (CDFW 2026 trackers; NOAA in-season actions).
- **Mixed-stock composition** changing by month and latitude.
- **Using last week’s catch as if it were next 48 h ocean state** (serial correlation of effort and of remaining quota).

### 2.8 What cannot be predicted at useful 24–48 h resolution

- Catch guarantee or number of Chinook per rod.
- Absolute ocean abundance in a port box.
- Precise locations of ESA-listed ESUs.
- Individual school positions.
- Tomorrow’s CPUE from SST or chlorophyll alone.
- Juvenile survey indices as adult charter forecasts.

### 2.9 Appropriate prediction target

**Category D — Relative habitat-encounter-risk** for legal-size Chinook in an **open** recreational ocean area over 24–48 h, expressed as a ranked anomaly vs recent port-area CPUE, with explicit uncertainty.

Category C (effort-normalized catch) is the right **evaluation metric** (charter or CRFS/ORBS CPUE) but is **not** a 48 h abundance estimate. Do not sell Category C as Category A/B.

Category E (raw SST/chl/AIS) is scientifically rejected.

### 2.10 Standardized survey / assessment data?

**Yes, extensive, but mostly the wrong timescale or stage.**

| Program | Scale | Use for this wedge |
|---------|--------|---------------------|
| PFMC Salmon SAFE / Preseason I–III | Annual stock status, ocean catch by area | Cohort size / season context, not 48 h |
| CDFW CRFS + ocean salmon harvest tracking | Half-month recreational catch | Ground-truth **after** the fact; coarse for 48 h |
| ODFW Ocean Salmon Management weekly port estimates | Weekly Chinook/coho and angler trips | Best public **sport CPUE** time series on OR coast |
| RecFIN / PacFIN | Regional catch | Not 48 h habitat |
| NWFSC JSOES | May–June juvenile surface trawl, WA/OR | **Do not use as adult CA charter truth** |
| Coded-wire tag recoveries / GSI | Stock composition | Mixing, not a daily map |
| SWFSC / CDFW genetic sampling | Stock ID | Same |
| ESA status reviews | Listed ESUs | Conservation constraint; no fine-scale maps in product |
| Newport Hydrographic Line | Biweekly oceanography | Covariates for OR coast, not fish counts |

### 2.11 Key scientific references and local expert orgs

- NOAA Chinook: https://www.fisheries.noaa.gov/species/chinook-salmon  
- NOAA protected Chinook ESUs: https://www.fisheries.noaa.gov/species/chinook-salmon-protected  
- Hinke et al. 2005: https://doi.org/10.3354/meps304207  
- Hinke et al. 2004 autumn habitat: https://doi.org/10.3354/meps285181  
- Hassrick et al. 2016 early ocean juveniles: https://onlinelibrary.wiley.com/doi/10.1111/fog.12141  
- Bi, Peterson, et al. habitat models (MEPS 336:249; *Fish. Oceanogr.* 2008, 2011)  
- PFMC: https://www.pcouncil.org/salmon-management-documents/  
- CDFW: https://wildlife.ca.gov/Fishing/Ocean/Regulations/Salmon  
- ODFW MRP salmon: https://www.dfw.state.or.us/MRP/salmon/  
- Oregon Sea Grant / NWFSC ocean indicators: URLs above  

---

## Candidate 3 — American lobster × bounded Gulf of Maine statistical area × commercial operator × next-trip CPUE / effort allocation

### 3.1 Taxonomy (WoRMS vs NOAA)

| Field | Record |
|--------|--------|
| **WoRMS accepted name** | *Homarus americanus* H. Milne Edwards, 1837 |
| **AphiaID** | 156134 |
| **LSID** | urn:lsid:marinespecies.org:taxname:156134 |
| **ITIS TSN** | 97314 — valid |
| **NCBI** | txid6706 (authority sometimes written without “H.”) |
| **NOAA Fisheries** | *Homarus americanus*; classification Animalia; Arthropoda; Malacostraca; Decapoda; Nephropidae; *Homarus*; *americanus*. Last updated 2026-05-22. https://www.fisheries.noaa.gov/species/american-lobster |

**Disagreement summary:** **None material** on identity. Record H. Milne Edwards vs Milne Edwards authority punctuation only.

### 3.2 Common-name ambiguity

| Label | Risk |
|-------|------|
| American lobster, Maine lobster, Canadian lobster, northern lobster, North Atlantic lobster | Same species (marketing names) |
| “Lobster” in US restaurants | Often this species in New England; **spiny lobster** (*Panulirus argus* and others) elsewhere — **no large claws** |
| European lobster | *Homarus gammarus* — different species |
| Slipper / squat “lobsters” | Not Nephropidae |

NOAA explicitly distinguishes true (clawed) lobster from spiny lobster: https://www.fisheries.noaa.gov/national/outreach-and-education/fun-facts-about-luscious-lobsters  

### 3.3 Life stages in scope

Next-trip commercial CPUE is about **legal-size benthic juveniles/adults** entering baited traps.

| Stage | Relevance |
|--------|-----------|
| Egg on female (9–11 months) | Protected; v-notch / eggers discarded; affects **legal** CPUE not total density |
| Pelagic larvae (stages I–IV) | Settlement surveys index **future** recruitment (years), not next trip |
| Early benthic YOY | Settlement collectors; climate/Calanus links in ASMFC 2025 |
| Sublegal juveniles | Ventless trap survey (VTS) CPUE; leading indicator of later legal CPUE, **seasonal** |
| Legal recruits (post-molt) | **Primary** next-trip catch in inshore GOM; ASMFC/Mills et al.: a large share of landings are recently molted into legal size |
| Large adults / offshore migrants | Area 3 / offshore; different fleet |

### 3.4 Geography (bounded GOM statistical area)

**Biological range:** Labrador to Cape Hatteras; most abundance Maine–New Jersey; offshore to ~2,300 ft (NOAA; WoRMS distribution note).

**Management geography (do not confuse):**

| Unit | What it is |
|------|------------|
| ASMFC stocks | **GOM/GBK** vs **SNE**. 2025 assessment: GOM/GBK not depleted but **overfishing**; SNE significantly depleted, not overfishing. |
| NMFS statistical areas | **511, 512, 513** cover inshore Maine GOM (used by DMR VTS and sea sampling) |
| Maine lobster management zones | A–G (state effort control) |
| LCMA | Area 1 (inshore GOM) is the core commercial small-boat fishery |

**Recommended bounded v1 geography (scientific, not founder-locked):** **one NMFS statistical area** (512 *or* 513) *or* one Maine zone, not the entire GOM/GBK stock. Eastern (511/512) and western (513) sublegal trends have diverged (Maine DMR 2024 monitoring update).

**This wedge is US GOM commercial.** DFO LFA 34 (SW Nova Scotia) is the same biological population complex but a different management unit (DFO 2024: LFA 34 is not a biological stock). Cite DFO as adjacent science, not as the operator’s area.

Official URLs:

- ASMFC species: https://asmfc.org/species/american-lobster/  
- 2025 assessment overview: https://asmfc.org/wp-content/uploads/2025/11/AmericanLobsterStockAssmtOverview_Oct2025.pdf  
- NOAA species: https://www.fisheries.noaa.gov/species/american-lobster  
- Maine DMR VTS: https://www.maine.gov/dmr/science/species-information/maine-lobster/surveys/ventless-trap-survey  
- Maine DMR sea sampling: https://www.maine.gov/dmr/science/species-information/maine-lobster/surveys/sea-sampling-survey  
- Maine landings: https://www.maine.gov/dmr/fisheries/commercial/landings-program/historical-data  

### 3.5 Operator and horizon

- **Operator:** commercial trap fisher planning the **next trip** (hours to a few days): where to set/haul within a statistical area, soak, bait, whether weather allows a haul.
- **Target:** **expected CPUE** and **effort allocation** (relative among depths/grounds), **not** exact abundance.
- **Critical scientific distinction:** trap CPUE = density × **catchability** × gear/competition × legal selectivity. Temperature, molt, and bait change catchability **without** a matching abundance change (McLeese & Wilder 1958 onward; Miller 1990; Jury & Watson 2013; ASMFC 2025 uses temperature-based catchability covariates in surveys). **Catch ≠ abundance.**

### 3.6 Habitat requirements and covariates

**Causal / biologically relevant**

| Variable | Mechanism | Next-trip role |
|----------|-----------|----------------|
| **Bottom temperature** | Activity, appetite, movement into traps; molt phenology (threshold ~5–6°C then degree-days; Mills et al. 2017 *Front. Mar. Sci.*); inshore–offshore seasonal movement. ASMFC: adult physiological stress ~20°C; optimal often cited 12–18°C. GOM bottom temps still generally favorable vs SNE. | **Top covariate for catchability.** Satellite SST is a **poor substitute** (ASMFC peer review 2025: satellite SST routine; bottom T is not). |
| **Molt timing / shell hardness** | Post-molt animals feed heavily and recruit to legal size; landings phenology follows molt (Mills et al. 2017; Staples et al. 2024 *Fish. Oceanogr.*). | Seasonal, region/sex/maturity specific. |
| **Depth** | Inshore shallows get the summer/fall pulse of the small-boat fleet; VTS is depth-stratified (2–32 fathom in ME). | Allocation variable. |
| **Substrate / shelter** | Rocky cover preferred inshore; mud burrows possible; territorial. | Slow-changing; good as a static map, not a daily layer. |
| **Storms / wind** | Haulability; also mixing and catchability. | Go/no-go. |
| **Soak time, bait, trap design, trap density** | Standard CPUE confounders. | Must normalize or hold in operator metadata. |
| **Legal selectivity** | Escape vents, min/max size, v-notch, egger release. | CPUE of **legal** lobster ≠ survey of all lobster. |

**Prey / climate (wrong timescale for next trip, right for stock)**

- Larval food *Calanus finmarchicus*: ASMFC 2025 links declining *Calanus* and phenological mismatch to GOM recruitment even where temperature remains suitable. **Year-class**, not next haul.
- Chlorophyll, nutrients, pH: ecosystem context, not trap CPUE tomorrow.
- Moon / tides: fishermen lore; published GOM trap-CPUE evidence is **weak/inconsistent** (tidal signal reported more in some eastern analyses). Treat as **tier 4** until tested in the chosen statistical area.

**DO, salinity:** generally well within GOM inshore ranges; hypoxia is a **SNE / LIS** story (NOAA species page: 1999/2002 Long Island Sound die-offs). Do not import SNE hypoxia as a GOM next-trip driver without local evidence.

### 3.7 Confounders

- **Temperature-dependent catchability** (the central confounder of “CPUE = abundance”).
- **Competition among traps** and among boats.
- **Bait type/quality and soak.**
- **Discarding** (sublegal, v-notch, eggers) — sea sampling records this; landings do not.
- **Whale-safe gear rules** (Atlantic Large Whale Take Reduction Plan) change configuration and haul tactics. **Do not predict whale locations.**
- **Zone trap limits and latent effort.**
- **Using landings as biomass** (DFO and ASMFC both warn against this).

### 3.8 What cannot be predicted at useful next-trip resolution

- Exact abundance in a statistical area.
- Tomorrow’s landings from SST or chlorophyll.
- Settlement or recruitment to legal size within one trip (except during a known molt pulse, and even then only as a regional phenology, not a tow-level count).
- Individual trap outcomes.
- Fine-scale maps of North Atlantic right whales or other protected species.

### 3.9 Appropriate prediction target

**Category C — Effort-normalized catch:** expected legal CPUE (e.g. legal count or weight per trap-haul) for the next trip, **relative** among candidate depths/grounds inside one statistical area, with an explicit statement that the quantity is **catchability-influenced catch**, not abundance.

Category B survey indices (VTS, NEFSC trawl, settlement) are **inputs/context** at seasonal scale, not the next-trip label. Category D habitat suitability can be a **feature** (bottom T × substrate × depth) feeding Category C, not a substitute for CPUE. Category A is impossible. Category E (SST/AIS/chl as lobster abundance) is rejected.

### 3.10 Standardized survey / assessment data?

**Yes — among the strongest of the three candidates, at seasonal/stock scale.**

| Program | Index type | Timescale |
|---------|------------|-----------|
| ASMFC 2025 benchmark assessment | Stock status GOM/GBK & SNE | Terminal year 2023; not next trip |
| NEFSC spring/fall bottom trawl | Fishery-independent (offshore-biased for inshore lobster) | Seasonal |
| Maine DMR Ventless Trap Survey | Sublegal CPUE, 276 sites, SA 511–513, Jun–Aug | Seasonal |
| Maine DMR sea sampling | At-sea catch/effort, legal and discard | Monthly within season |
| Maine settlement survey | YOY | Annual |
| MENH inshore trawl (spring/fall) | Inshore index | Seasonal |
| CFRF Lobster Research Fleet | Biological + some ventless + bottom T | Trip, research fleet |
| eMOLT | Bottom temperature on commercial gear | **Right covariate timescale** |
| DFO ILTS / RV / NEFSC in LFA 34 | Adjacent Canada | Seasonal |
| Dealer landings / zone landings | Catch, not CPUE unless effort known | Monthly |

ASMFC 2025 peer review: satellite SST is not an adequate substitute for **bottom** temperature; interpolations from ocean models were too coarse for some assessment uses; trap-sensor programs (eMOLT-type) are the path forward.

### 3.11 Key scientific references and local expert orgs

- NOAA American lobster: https://www.fisheries.noaa.gov/species/american-lobster  
- ASMFC 2025 press: https://asmfc.org/news/press-releases/american-lobster-benchmark-stock-assessment-finds-gom-gbk-stock-not-depleted-but-experiencing-overfishing-sne-stock-significantly-depleted-but-experiencing-overfishing/  
- Mills et al. 2017 fishery timing: https://doi.org/10.3389/fmars.2017.00337  
- Tanaka / Friedland habitat (NOAA IR): https://repository.library.noaa.gov/view/noaa/54024  
- Maine DMR 2024 monitoring update: https://www.maine.gov/dmr/sites/maine.gov.dmr/files/inline-files/2024%20Lobster%20monitoring%20updateFinal.pdf  
- eMOLT: https://www.emolt.org/  
- CFRF fleet: https://www.cfrfoundation.org/jonah-crab-lobster-research-fleet  
- DFO LFA 34 2024 update: https://publications.gc.ca/collections/collection_2025/mpo-dfo/fs70-7/Fs70-7-2024-040-eng.pdf  
- Maine Sea Grant; University of Maine School of Marine Sciences; Gulf of Maine Lobster Foundation; ASMFC Lobster Technical Committee / SAS  

---

## Cross-candidate comparison (scientific only; wedge remains unresolved)

| | C1 Pacific oyster WA | C2 Chinook CA/OR | C3 Lobster GOM |
|--|----------------------|------------------|----------------|
| Mobility at horizon | Sessile on lease | Highly mobile | Mobile but trap-local |
| Right target class | **D** stress risk | **D** encounter risk (evaluate with **C**) | **C** CPUE (not abundance) |
| 24–72 h physical mechanism | Strong (heat × tide, DO, storms) | Moderate (thermal habitat, weather) | Strong catchability (bottom T, weather, molt season) |
| Standardized surveys | Weak for farm mortality | Strong for **annual** stocks; weak for 48 h adults | Strong for **seasonal** stock; moderate for next trip |
| Main scientific failure mode | Confusing DOH harvest closure with animal stress | Treating SST/chl/AIS or juvenile surveys as adult abundance/catch | Treating CPUE or SST as abundance |
| Protected-species issue | Low (don’t map other listed species as byproduct) | **High** (mixed ESA Chinook ESUs) | **High** if product drifts into whale maps; keep out |

**No candidate supports Direct Count (A) or Unverified Indicator (E) as an honest v1 product.**
