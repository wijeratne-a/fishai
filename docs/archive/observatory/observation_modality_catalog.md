# Observation modality catalog — Global Saltwater Life Observatory

**Program:** GLOBAL SALTWATER LIFE OBSERVATORY (FishAI scientific blueprint)  
**Agent:** OBSERVATION_MODALITY cluster  
**Date / access date for cited URLs:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/`  
**Ingestion:** none. Catalog and cite only.  
**Commercial wedge:** remains a separate one-species × one-geography product. This file is the long-horizon observing blueprint, not a product claim.

**Companions:** `satellite_capability_matrix.md` · `sensor_network_catalog/` · `direct_observation_registry/` · `telemetry_registry/` · `eDNA_registry/` · `acoustic_registry/` · `observation_coverage_maps/taxa_modality_feasibility.csv`

---

## How to read this catalog

Every capability is classified as one of:

| Code | Meaning |
| --- | --- |
| **DIRECT** | Observable today with this modality under stated conditions (an instrument records the organism, its sound, its DNA, its image, or a calibrated backscatter of the organism). |
| **INFERRED** | Estimable today from this modality plus an explicit model/assumption (habitat, occupancy, relative density). Not an observation of the animal. |
| **FORECAST** | Predictable at some horizon with **current** data streams (skill must be validated; many “forecasts” are persistence or physics of the environment, not of the organism). |
| **NEEDS_INFRA** | Physically plausible with sensors/platforms that exist, but not deployed at the required density, duty cycle, or data rights. |
| **UNPROVEN** | Scientifically plausible; published demonstrations are local, mixed, or not independently operational. |
| **SPECULATIVE** | Concept-stage; physical path exists but evidence is thin or contradictory. |
| **IMPOSSIBLE** | Violates physics, information theory, or measurement practice **now** (and often in principle). Includes “see every individual fish from a 750 m ocean-color pixel.” |

**Output classes** (for downstream twin / API typing): `DIRECTLY OBSERVED` · `REMOTELY DETECTED` · `SURVEY-DERIVED` · `TAG/TELEMETRY-DERIVED` · `OPERATIONALLY OBSERVED` · `MODEL-INFERRED` · `FORECAST` · `HYPOTHETICAL/RESEARCH MODE` · `UNKNOWN/INSUFFICIENT DATA`.

**Never claim:** exact locations of all individuals; exact census; real-time tracking without an observation; abundance from satellite surface image or vessel density; harvest legality from habitat; that a model is an observation.

**Cost labels:** `CITED` = number taken from a named source; `ESTIMATE` = order-of-magnitude judgment, not a quote; `UNKNOWN` = do not invent.

Licenses for reuse (especially commercial forecast resale) are **UNKNOWN** until a rights review. Visual access ≠ license to ingest or resell.

---

## Hard physical limits (apply to all modalities)

These are not engineering inconveniences. They bound what a global observatory can ever say.

1. **Seawater is opaque in the optical/IR.** Pure-water absorption plus dissolved and particulate matter confine sunlight useful for imaging to the upper tens of meters in clear water, often **&lt;1–10 m** in coastal/turbid water, and **~0** for thermal infrared (skin temperature of micrometres) and for most microwave SST. Jerlov water-type / \(K_d(490)\) maps (NOAA VIIRS Kd products; Copernicus transparency products) quantify this; they do not lift it. Individual animals below the optical depth are **IMPOSSIBLE** to image from air or space.

2. **Pixel vs organism.** NOAA VIIRS ocean color is nominally **750 m** (L2) / **4 km** (global L3). Copernicus OLCI plankton products include **300 m** and **4 km**. A school, whale, or reef is a sub-pixel mixture except on **very high-resolution (VHR)** commercial imagers (~0.3–2 m) **and** when the animal is at/near the surface in low sea state, low glint, low cloud. Operational ocean-color satellites **cannot** count fish.

3. **Acoustics trade frequency, range, and resolution.** Absorption rises with frequency. Fisheries survey standards cluster around **38 kHz** (and 18/70/120/200 kHz). Broadband helps but **does not uniquely identify species** when target-strength spectra overlap (ICES *Acoustic target classification*; NOAA pollock broadband study). Sound does not yield a Linnaean name without independent validation (trawl, camera, eDNA, or prior).

4. **eDNA is a tracer, not a GPS fix.** Detected DNA means molecules were at the filter. Transport + decay studies report persistence on the order of **hours to ~1 day** and modeled distances from **&lt;1 km to tens of km** depending on tide, current, temperature, and decay rate — and **models often exceed field detections** (Andruszkiewicz et al.; Murakami et al. 2019 ~30 m empirical vs ~10 km modeled). Occupancy ≠ abundance; reads ≠ biomass.

5. **Tagged animals are a biased subset.** Catchability, size, tagging location, tag type, duty cycle, premature failure, and processing all bias tracks (Sequeira et al. 2021 *MEE*). Individuals ≠ population. ATN/OTN/AniBOS are essential and still not a census.

6. **Catch and AIS are effort, not abundance.** VMS is confidential under U.S. MSA policy (NMFS 06-101). AIS is incomplete (class, garbling, switch-off). Global Fishing Watch is a vessel-activity product.

7. **A global exact census of mobile marine animals is IMPOSSIBLE** with 2026 sensors. The honest observatory is a **fusion of sparse direct observations, biased operational catches, physics, and explicit uncertainty**.

8. **Protected-species precise locations** (ESA/MMPA, spawning aggregations used for poaching, Indigenous sites) are **not publishable** even when technically observed. Coarsen, delay, or withhold.

---

## What satellites can and cannot detect today (animals)

Detailed sensor table: `satellite_capability_matrix.md`.

### Directly or remotely detectable from space **today** (conditional)

| Target | Status | Conditions | Source class |
| --- | --- | --- | --- |
| **Phytoplankton biomass / chl-a** | Operational `REMOTELY DETECTED` | Cloud-free, sunlit ocean; coastal CDOM/sediment contamination | NOAA CoastWatch VIIRS MSL12; Copernicus GlobColour |
| **Some phytoplankton groups** | Research-to-provisional `REMOTELY DETECTED` | PACE-OCI hyperspectral; MOANA picoplankton (*Prochlorococcus*, *Synechococcus*, picoeukaryotes) | NASA PACE / Earthdata MOANA 3.1 |
| **Pelagic *Sargassum* mats** | Near-operational `REMOTELY DETECTED` | Open-ocean mats at 1–10 km; nearshore mixed | USF SaWS; NOAA CoastWatch SIR v1.5 (labeled experimental) |
| **Harmful algal bloom proxies** | Operational/experimental `REMOTELY DETECTED` | Chl, fluorescence line height, cyanobacteria indices; **not** toxin | NOAA NCCOS / CoastWatch HAB products |
| **Shallow benthic habitat** (seagrass, some reefs, kelp, sand/mud) | Operational mapping `REMOTELY DETECTED` | Clear water, typically **&lt;10–30 m** (to &gt;30 m only in clearest water) | Sentinel-2 10 m; Landsat 30 m; WorldView-2/3 2 m (O’Neill / Nagel et al. 2022) |
| **Coral heat stress** | Operational **proxy** `MODEL-INFERRED` | SST-based DHW; **not** live coral count | NOAA Coral Reef Watch 5 km v3.1 |
| **Large whales at the surface** | Research `REMOTELY DETECTED` | VHR ~0.3–1 m; good sea state; manual or CNN; **not** a global census; species ID limited | Cubaynes et al.; Fretwell et al.; DFO 2022 *Megafauna from Space* |
| **Pinnipeds / walrus on ice or haulout** | Research/monitoring `REMOTELY DETECTED` | VHR; ice/land contrast | published VHR mammal reviews |
| **Seabird colonies / penguin stains** | Demonstrated `REMOTELY DETECTED` | Guano, colony extent on land/ice | Landsat/Sentinel literature |
| **Very large sharks/rays in clear shallow water** | Demonstrated, rare `REMOTELY DETECTED` | Basking shark, some rays; VHR; turbidity/glint kill detection | DFO 2022; not Sentinel-2 operational |
| **Surface slicks, foam, ice, ships (SAR)** | Operational `REMOTELY DETECTED` | Sentinel-1 / RCM / other SAR; ships ≠ fish | Copernicus / CSA / NOAA |

### Not satellite-detectable as organisms **today** (direct)

Most **finfish**, **cephalopods**, **crustaceans**, **shellfish individuals**, **larvae**, **jellyfish** except rare surface aggregations, **turtles** except anecdotal VHR, **microbes as cells**, **deep corals**, **mesopelagic fauna**, **any animal under the optical depth**.

**Elasmobranch ecology papers using “satellites” almost always mean SST/productivity as habitat covariates, not pictures of sharks** (Williamson et al. 2019 *Front. Mar. Sci.*).

### Indirect paths that **do** observe or constrain “invisible” fish (do not stop at “satellites cannot see fish”)

A living observatory does not need a satellite to image a tuna. It needs **coupling**:

1. **Physics from space + in situ depth.** SST, SSH (including SWOT mesoscale), winds, color → 3D ocean state via models (CMEMS, RTOFS, regional ROMS) **assimilating Argo/gliders/buoys**. Animals are still not in the pixel; **thermal/oxygen habitat volume** is.
2. **Tags teach movement models.** ATN/AniBOS tracks + satellite habitat → empirically parameterized habitat-use (still tagged-subset biased).
3. **Vessel sensors.** Opportunistic echosounders, hull temp, cameras, eDNA pumps on fishing/research/commercial ships, with **privacy-preserving aggregation**.
4. **AUVs/gliders** steered to satellite fronts/eddies with EK80, cameras, eDNA.
5. **Hydrophones / DAS** at cable landings and sanctuaries: vocal taxa independent of light.
6. **Cameras + ML** at photic depths (BRUV, baited, ROV, animal-borne).
7. **Prey / physics proxies** with an honest label: PACE plankton + forage acoustics → predator **encounter risk**, never “N tuna.”
8. **Data assimilation** of all of the above into an evidence-typed twin (see architecture agents): each state variable carries `DIRECTLY OBSERVED` vs `MODEL-INFERRED`.

---

## Cross-cutting cost and scale notes

| Item | Figure | Label | Source |
| --- | --- | --- | --- |
| BGC-Argo float lifetime (capital + cal + data + comms) | ~**USD 100,000** | CITED | Argo BGC mission page, accessed 2026-09-18 |
| 1000-float BGC-Argo array, annual sustainment | ~**USD 25,000,000**/yr | CITED | same (250 floats/yr × 4-year life) |
| Core Argo active fleet | **~4,000** (Euro-Argo dashboard **4,334** active as of 2026-08-09 snapshot in search); UCSD “close to 4000” | CITED | argo.ucsd.edu/about/status/; fleetmonitoring.euro-argo.eu |
| Public NOAA/Copernicus L3/L4 SST & ocean color | **$0 marginal** at catalog (agency-paid) | CITED as free access pages; **commercial-resale license UNKNOWN** | coastwatch.noaa.gov; marine.copernicus.eu |
| VHR tasking (WorldView-class) | catalog price | **UNKNOWN** (commercial) | — |
| Research ship-day | | **UNKNOWN** (varies by vessel; ESTIMATE often 10⁴–10⁵ USD/day in grey literature — **not used as cited**) | — |
| eDNA field+lab per sample | | **UNKNOWN** (protocol-dependent) | — |
| Satellite tag unit | | **UNKNOWN** | — |
| DAS interrogator + dark-fiber access | | **UNKNOWN** (partnership-dominated) | — |

**Information-per-dollar ranking** is in §Top 10 below. Reusing **already-paid** public satellites, IOOS, Argo, PAM archives, and opportunistic vessels dominates new capital.

---

## 3.1 Satellite remote sensing

| Field | Assessment |
| --- | --- |
| **Maturity** | **Operational** for SST, ocean color, altimetry, scatterometer winds, sea ice, many L4 analyses. **Provisional/research** for PACE community composition, SWOT biophysical coupling, VHR megafauna CNNs, Sargassum SIR (NOAA labels SIR experimental). |
| **TRL** | Operational NOAA/Copernicus chains: treat as **operational (high)**. VHR whale CNNs: **UNKNOWN**. Do not invent a TRL number. |
| **Data availability** | Global, daily-to-weekly with **cloud/glint/ice gaps**. NRT VIIRS/OLCI hours–1 day; L4 analyses daily. VHR tasking sparse and costly. SWOT not a daily global mapper in the same sense as VIIRS. |
| **Scientific validity** | High for **skin SST, ocean color optics, chl in Case-1 waters, SSH**. Medium for coastal chl, PFTs, floating algae indices. **Invalid** as animal abundance. |
| **Limitations** | Optical depth; clouds; land adjacency; sub-pixel mixing; diurnal SST skin vs bulk; microwave SST under rain; no species of fish; coral DHW is heat stress not mortality. |
| **Costs** | Public polar/geo: **$0 marginal, CITED free portals**. VHR: **UNKNOWN**. Ground segment already socialized via NOAA/ESA/NASA/EUMETSAT. |
| **Scalability** | Highest of any modality for **surface physics and ocean color**. Does not scale to individual animals. |
| **Latency** | NRT hours to ~1 day typical; science-quality delayed. CRW daily. |
| **Resolution** | 300 m (OLCI) to 4–25 km (many L4); geo SST ~2–5 km; VIIRS 750 m; VHR 0.3–2 m; SWOT SWOT-class SSH finer than conventional altimetry along swath. |
| **Coverage** | Global ice-free ocean for polar orbiters; coastal HF gaps remain for biology not physics. |
| **Regulatory** | Export controls on some VHR; ITAR/commercial licensing **UNKNOWN** per scene. Do not scrape paid catalogs. |
| **Privacy / ecological risk** | VHR can reveal **haulouts, nesting beaches, industrial outfalls, vessels**. Coarsen endangered aggregations. Ships in SAR/AIS fusion can unmask fishing. |
| **Integration** | Covariates in habitat models; front/eddy detection to cue gliders/ships; CRW/HAB/Sargassum as **named proxy products**; never as `DIRECTLY OBSERVED` fish. |
| **Breakthrough potential** | **PACE-class hyperspectral + SWOT + 3D assimilation** for plankton/microbes and habitat volume. **Not** a fish census. VHR+ML for whales in selected grounds: high local value, low global completeness. |

**Taxa (satellite):**

| Taxon | Direct today | Inferred | Forecast with current data | Needs new infra | Unproven / speculative | Impossible now |
| --- | --- | --- | --- | --- | --- | --- |
| Finfish | No individuals | Thermal/color habitat; sardine “potential habitat” maps (NOAA CoastWatch applications) | Habitat persistence / seasonal envelopes | Dense in situ to train 3D habitat | Nighttime bioluminescence from space as fish | Species census; deep fish |
| Sharks/rays | Rare VHR in clear shallows (basking shark class) | SST/productivity habitat (dominant literature use) | Seasonal habitat | Routine VHR+ML | Global surface-shark watch | Most species, most of the time |
| Shellfish | Intertidal beds / some aquaculture structures CONDITIONAL | SST/turbidity stress **proxies** (not mortality) | Heat-at-low-tide **physics** if fused with tides | Hyperspectral intertidal ops | Shellfish biomass from space | Subtidal individuals |
| Crustaceans | No | Weak surface habitat; **bottom T is not SST** | Phenology only if bottom T from models/in situ | Bottom-T observing | — | Lobster count from SST |
| Cephalopods | No | Weak | Weak | — | Surface squid aggregations in VHR | — |
| Marine mammals | VHR surface whales; ice pinnipeds | Prey/habitat proxies | Migration envelopes (coarse) | Operational VHR constellation + ML | Density from space without availability bias correction | All individuals, all oceans, all hours |
| Turtles | Essentially no | SST corridors | Nesting-season beach **air** products are terrestrial | VHR nesting-beach programs (privacy!) | In-water turtle from Sentinel-2 | Pelagic census |
| Seabirds | Colonies, some rafts | Foraging habitat | Colony phenology | — | Individual tracking from space | At-sea census of small spp |
| Plankton | Chl, some PFTs, blooms | Primary production algorithms | Bloom forecasts (skill **UNKNOWN** globally; regional HAB better) | PACE + BGC-Argo fusion at density | Species-level diatoms from space | Cells of most taxa |
| Jellyfish | Rare large surface aggregations | — | — | — | Routine jellyfish satellite product | Most events |
| Corals | Shallow reef **habitat** (not polyps) | CRW DHW heat stress | Bleaching **outlook** (heat, not community) | Repeated benthic imagery fusion | Health from hyperspectral | Deep corals; polyp counts global |
| Benthos | Shallow habitat classes | — | — | — | — | Deep fauna |
| Plants/algae | *Sargassum*, kelp, seagrass, some Ulva | — | Sargassum inundation risk (experimental SIR) | Higher-res nearshore | — | Sub-canopy biomass everywhere |
| Microbes | Bulk chl; PACE picoplankton groups | PFTs | — | Global MOANA validation | Pathogen maps from space | Individual microbes; most functions |
| Larvae | No | Spawn-habitat physics | Particle-tracking **of water**, not larvae, unless coupled | — | Larval overlays on SSH | Imaging a larva from orbit |

---

## 3.2 Aerial / drone

| Field | Assessment |
| --- | --- |
| **Maturity** | **Operational** for marine-mammal and seabird line-transect surveys, oil/HAB reconnaissance, some shark/turtle work. **UAV/drone** mature for nearshore, colonies, aquaculture; limited by range, icing, regulation, sea state. |
| **TRL** | Manned survey photography/IR: operational. BVLOS ocean drones: **UNKNOWN** by jurisdiction. |
| **Data availability** | Campaign-based, not global. NOAA Fisheries / USFWS / DFO / state surveys exist as **survey datasets** (rights vary). Drone imagery usually PI-owned. |
| **Scientific validity** | High for **surface-available** megafauna when availability bias is modeled. IR helps nocturnal/cryptic at surface. Turbidity still blinds subsurface. |
| **Limitations** | Weather, endurance, airspace, glare, observer fatigue, disturbance (especially drones over pinnipeds/birds). Depth same optical limit as satellites, but **higher spatial resolution and on-demand timing**. |
| **Costs** | **UNKNOWN** per flight hour. ESTIMATE: drones cheaper than ships/aircraft for small AOIs; manned aircraft still wins for wide strips. |
| **Scalability** | Regional, not planetary, unless many operators (coast guard, aquaculture, NGOs). |
| **Latency** | Hours if processed in-field; often days–months for science counts. |
| **Resolution** | cm–m. |
| **Coverage** | Coastal / ice edge / survey blocks. |
| **Regulatory** | Civil aviation; sanctuary overflight rules; MMPA/ESA take via disturbance; export of UAV. |
| **Privacy / ecological risk** | Haulouts, nesting, people on beaches, farms. Disturbance is an **ecological** cost. |
| **Integration** | Calibration of VHR satellite detections; abundance in survey blocks; cueing ships. |
| **Breakthrough potential** | Medium: **autonomous long-range UAV + ML** for whales/slicks/Sargassum. Does not solve mesopelagic fish. |

**Taxa:** Direct for marine mammals, seabirds, turtles (surface), some sharks/rays in clear water, Sargassum/HABs, intertidal algae, aquaculture gear. **Inferred** habitat only for finfish/crustaceans/cephalopods. **Impossible** for deep and most larval/microbial targets.

---

## 3.3 Underwater optical imaging

| Field | Assessment |
| --- | --- |
| **Maturity** | **Operational** in ROV/AUV surveys, BRUV, baited/unbaited cameras, towed sleds, animal-borne cameras, aquaculture nets, some cabled observatories (e.g. ONC/OOI-class cameras — site-limited). **ML classification** rapidly improving, still domain-shifted. |
| **Data availability** | Sparse geographically. OBIS/GBIF hold many occurrence records derived from imagery/video; **224M observations / 207K marine species / 7,363 datasets** in OBIS as of page access 2026-09-18 — still biased to coastal/shallow/well-known taxa (Webb et al. 2010; OBIS 2019 review: ~half of WoRMS species have any OBIS record; 56% of OBIS species have &lt;10 records). |
| **Scientific validity** | High for **presence and relative composition in the field of view** when IDs are expert-validated. Length/biomass from stereo-BRUV is established in many reefs. **Not** a density without a detectability model and survey design. |
| **Limitations** | Range **metres**; lights disturb; biofouling; turbidity; night; bait attraction bias; class imbalance in ML; deep time-on-station is expensive. |
| **Costs** | BRUV hardware **UNKNOWN** (ESTIMATE low hundreds to low thousands USD). ROV/AUV days dominated by **ship** cost **UNKNOWN**. |
| **Scalability** | Poor globally if ship-based; better as **fixed cameras + AUVs + fishing-gear cameras**. |
| **Latency** | Real-time on tethered systems; archival otherwise. |
| **Resolution** | Organism-scale in frame; survey-scale is the station spacing. |
| **Coverage** | Points, transects, reefs, canyons — tiny fraction of ocean volume. |
| **Regulatory** | Permits for protected habitats; lights/bait in MPAs; video of listed species. |
| **Privacy / ecological risk** | Exact reef holes / fishing spots in frames; disturbance; bycatch of images of people/vessels. |
| **Integration** | Ground truth for acoustics and eDNA; training data for ML; habitat maps. |
| **Breakthrough potential** | **High for benthos, reef fish, gelatinous fauna, and mesopelagic** if AUV fleets + foundation-model ID + edge processing. Still local volumes. |

**Taxa:** Direct in-frame for almost all macroscopic taxa (finfish, sharks, shellfish, crustaceans, cephalopods, turtles, jellies, corals, benthos, plants, some large plankton). Mammals/seabirds when they dive into frame. Microbes only with microscopy/fluorescence, not landscape cameras. Larvae with specialized imaging (UVP, ISIIS, Zooglider) — **DIRECT but rare platforms**.

---

## 3.4 Active acoustics / sonar

| Field | Assessment |
| --- | --- |
| **Maturity** | **Operational backbone** of pelagic fish and krill **biomass surveys** (ICES/NOAA/DFO). Multifrequency + trawl ID is standard. Broadband EK80-class **operational on many ships**, species-discrimination **not solved**. Mapping sonars / fisheries sonars operational on commercial vessels (data rarely open). |
| **Scientific validity** | High for **nautical-area-scattering-coefficient → biomass** of **validated, often swimbladdered, monospecific aggregations**. Invalid as species ID in mixed, similar-TS communities (capelin vs polar cod; herring vs Norway pout — Fernandes/Korneliussen literature; ICES CRR 344). NOAA GOA pollock broadband: **no clear pattern among swimbladder fishes** in 15–150 kHz. |
| **Limitations** | Species overlap; orientation/size; near-surface blind zone; dead zone near seabed; resonance of siphonophores mimicking fish; vessel avoidance; air-bubble noise; **bottom-dwelling crustaceans/shellfish poorly inventoried** by pelagic EK; marine mammals not a survey target (and may avoid). |
| **Costs** | Scientific EK80 **UNKNOWN**. Value is often **already installed** on research and fishing vessels — information-per-dollar high if data are shared. |
| **Scalability** | Global **if** opportunistic fishing-fleet acoustics are standardized (IMR/ICES “fishing vessel acoustics” path). Otherwise annual survey lines only. |
| **Latency** | Real-time onboard; science products months. |
| **Resolution** | Vertical: metres to tens of m depending on pulse; horizontal: ping spacing × beam. |
| **Coverage** | Survey strata; shipping/fishing tracks if opportunistic. |
| **Regulatory** | Some high-power/military sonar excluded. Scientific EK generally accepted. MMPA considerations for high-source mapping sonars **UNKNOWN** case-by-case. |
| **Privacy / ecological risk** | Echotracks can reveal **fishing spots**. High-power sources: injury/behavior risk for mammals. |
| **Integration** | **Primary biomass constraint** for pelagic fish/zooplankton in a twin; must carry trawl/camera/eDNA as ID prior. Cue AUVs. |
| **Breakthrough potential** | **High:** broadband + ML + cameras on the same platform; calibrated opportunistic fleet acoustics. **Not** a universal species classifier. |

**Sonar species-classification limits (explicit):**

- **Can separate classes** when frequency response differs: gas-bearing fish vs mackerel (no swimbladder) vs zooplankton vs resonant scatterers (Korneliussen & Ona).
- **Often cannot separate species** with similar anatomy/size.
- Identification hauls remain necessary for assessment-grade biomass (ICES survey protocols).
- Unsupervised clustering can clean broadband TS; it does not invent taxonomy.

**Taxa:** Direct backscatter: many finfish, some sharks (weaker), krill/zooplankton, some squid, siphonophores. Indirect: habitat of predators. Poor/impossible as ID: shellfish beds (need specialized MBES/seabed classification — different problem), most benthos species, microbes, larvae as named species, turtles/mammals as stock assessment (different tools).

---

## 3.5 Passive acoustics

| Field | Assessment |
| --- | --- |
| **Maturity** | **Operational monitoring** in NOAA sanctuaries (ONMS Sound; SanctSound 2018–2022 archive at NCEI), Navy/NMFS PAM, many NGO/academic moorings. Detection pipelines for some baleen/odontocete call types operational; fish choruses documented but **rarely species-to-biomass**. |
| **Data availability** | NCEI Passive Acoustic Archive (Tethys-aligned). Coverage is **a set of points**, not ocean-wide. IOOS/MBON/regional hydrophone projects exist. |
| **Scientific validity** | High for **presence of vocalizing taxa** when call catalogs exist. Density estimation requires calling-rate, detection functions, and cue rates — often **UNKNOWN**. Silence ≠ absence. |
| **Limitations** | Non-vocal taxa invisible; calling is behavioral/seasonal; masking by ships; low-frequency propagation vs high-frequency clicks (range of porpoise clicks is short); data volume. |
| **Costs** | SoundTrap-class recorders **UNKNOWN**. Archive reuse is the cheap path. |
| **Scalability** | Moorings scale linearly with dollars. **DAS (3.11)** changes the scaling law along cables. |
| **Latency** | Real-time only with cabled/satellite-linked systems (gliders, buoys, observatories). Many archival, retrieved in months. |
| **Resolution** | Localization from arrays: hundreds of m to km (geometry-dependent). Single hydrophone: presence in a detection range (km for blue/fin; much less for high-frequency). |
| **Coverage** | Sanctuaries, chokepoints, some basins (e.g. CTBTO hydroacoustic — primarily explosions, some whale science). |
| **Regulatory** | Data may include navy/test ranges; classification **UNKNOWN**. Listed-species locations. |
| **Privacy / ecological risk** | Publishing real-time whale maps can attract vessels **or** help avoidance — policy choice. Do not publish NARW-precision tracks in a public twin. |
| **Integration** | Occupancy layers for vocal mammals and some fishes; noise EOV; DAS cross-cal. |
| **Breakthrough potential** | **High for vocal megafauna** when fused with DAS + satellite AIS (ship-strike). Medium for fish choruses as **ecosystem indicators**, not stock assessments. |

**Taxa:** Direct: marine mammals (especially baleen, many odontocetes), some soniferous fishes, snapping shrimp (reef/habitat), ice/earth/ships. Not: plankton, most shellfish, larvae, microbes, most sharks (generally not vocal), turtles.

---

## 3.6 eDNA / genomics / molecular

| Field | Assessment |
| --- | --- |
| **Maturity** | **Operational-adjacent** for occupancy/biodiversity surveys; NOAA Omics strategy + PMEL Ocean Molecular Ecology + AOML samplers. **Not** operational global abundance. Metabarcoding, qPCR/dPCR for target species, eRNA (faster decay, UNPROVEN for routine marine management). |
| **Data availability** | Growing; OBIS is expanding DNA-derived data publishing (OBIS news 2026-07-10). Reference libraries incomplete for many marine invertebrates/microbes. |
| **Scientific validity** | High for **detection of taxa with good primers/references** given contamination control. Medium/low for **abundance, biomass, or precise location**. Transport/decay must be modeled (Harrison et al. 2019; Andruszkiewicz; *Environmental DNA* 2025 spatial-bound paper: modeled median **2.27–14.14 km**, up to 10× observed). Lifetime simulations **5–30 h**, transport **0.3–39 km** (Bay of Biscay Lagrangian study). |
| **Limitations** | Shedding rate unknown; PCR bias; primer dropout; contamination; inhibition; reference gaps; **rare-species false-positive inflation** (Darling, Jerde, Sepulveda 2021); vertical stratification (do not sample across thermocline naively). |
| **Costs** | Per-sample **UNKNOWN**. Autonomous samplers exist (AOML “inexpensive” prototypes — dollar figure **UNKNOWN**). Far cheaper than trawling a rare species once protocols exist. |
| **Scalability** | **High** on ships of opportunity, buoys, desalination intakes, AUVs. Lab/bioinformatics is the bottleneck more than field collection. |
| **Latency** | Hours–days for targeted qPCR if local lab; weeks typical for metabarcoding. In-situ sequencing still **UNPROVEN** operationally at scale. |
| **Resolution** | Sample is a point (or integrated filter). Spatial meaning = **plume** not pin. |
| **Coverage** | Wherever water can be filtered — including deep. Currently campaigny. |
| **Regulatory** | Nagoya/ABS for genetic resources; permit for listed species **genetic** data; Indigenous data sovereignty (CARE). Sequence data may still be sensitive for listed taxa. |
| **Privacy / ecological risk** | Revealing presence of listed/harvested species at fine scale. Dual-use of pathogen genomics — stay on biodiversity primers. |
| **Integration** | Occupancy prior; ground-truth acoustics; **eDNA2OBIS** path (PMEL). Couple to hydrodynamic models as a **tracer**. |
| **Breakthrough potential** | **Among the highest for currently invisible/cryptic taxa** (deep rare fish, larvae presence, microbes, invasive early detection). Abundance remains the hard problem. |

**Taxa:** In principle **all** with DNA in water/sediment/gut. Direct: molecular presence. Inferred: relative diversity, sometimes rank abundance after calibration. Forecast: only if occupancy time series exist (few). Needs infra: standardized autonomous time series. Impossible: exact headcount from a single uncalibrated sample.

---

## 3.7 Tagging / telemetry

| Field | Assessment |
| --- | --- |
| **Maturity** | **Operational science infrastructure:** IOOS ATN DAC (`https://portal.atn.ioos.us/`), Ocean Tracking Network, ICARUS/Argos, AniBOS (GOOS animal-borne ocean sensors). Satellite, acoustic, archival, PSAT, GPS, accelerometer, animal-borne CTD. |
| **Data availability** | ATN aggregates U.S. partner deployments (NCEI collection IOOS-ATN-STP). Global coverage is **the union of projects**, heavily biased to charismatic, fundable, catchable animals in the North Atlantic/Pacific and Southern Ocean. |
| **Scientific validity** | High for **those individuals**. Low for **population distribution** unless design-based or bias-corrected (Sequeira et al. 2021: tagging location, device, gaps, premature failure, processing). |
| **Limitations** | Taging effect; duty cycle; Argos error (km) vs GPS (m); acoustic arrays only where receivers exist; fisheries recapture bias; **cannot tag plankton, most larvae, most microbes, most benthos**. |
| **Costs** | Unit costs **UNKNOWN**. Arrays (FACT, PIRAT, OTN) are multi-million capital — exact **UNKNOWN**. Reuse of ATN is cheap. |
| **Scalability** | Poor as a census; excellent as **process information** (vertical habitat, migration speed) that **teaches models**. |
| **Latency** | Satellite tags: hours. Acoustic: when receiver is downloaded or real-time buoy. Archival: after pop-up/recapture. |
| **Resolution** | Metres (GPS) to kilometres (Argos/light). |
| **Coverage** | Paths of tagged animals, not the stock. |
| **Regulatory** | IACUC/permits; ESA/MMPA; some nations restrict tagging. |
| **Privacy / ecological risk** | **Exact tracks of listed species and of fishing-associated animals** are sensitive. Public products must coarsen. |
| **Integration** | Movement kernels; animal-borne T/S profiles (AniBOS) into ocean models; validation of habitat models. |
| **Breakthrough potential** | Medium globally, **high locally**. Cheap acoustic tags + existing receiver networks for coastal fishes/sharks. Satellite tags will not scale to millions of herring. |

**Tagged-subset bias (explicit):** tagging location inflates suitability near release; devices drop small/cryptic/unwholesome animals; survivors of capture are not random; duty cycles oversample surface in some PSATs; premature pop-off censors mortality and long trips; processing (state-space vs raw) changes apparent habitat. ATN QC flags implausible points; it **does not** fix representativeness.

**Taxa:** Direct tracks: many sharks/rays, tunas/billfish, marine mammals, turtles, seabirds, some large teleosts, some crabs/lobsters (acoustic), some squid (rare). Needs infra: most reef fishes, most invertebrates. Impossible: typical plankton/larvae/microbes as individuals.

---

## 3.8 Autonomous platforms (Argo, gliders, AUV/ROV, ASV)

| Field | Assessment |
| --- | --- |
| **Maturity** | **Argo:** GOOS operational, ~4000 active floats, core T/S/P to 2000 m; BGC subset (O2, NO3, pH, chl fluorescence, particles, irradiance) **not yet at 1000-float design**. **Deep Argo** to 6000 m growing. **OceanGliders:** GOOS emerging/operational regional. **AUV/ROV:** operational science, not a global grid. **ASV/wave gliders:** operational for metocean, some PAM/optics. |
| **Data availability** | Argo GDAC free; IOOS Glider DAC; regional RA portals (NANOOS, NERACOOS, etc.). ROV video often expedition-based (NOAA OER, Schmidt, IFREMER). |
| **Scientific validity** | Argo physics: **climate-quality** after delayed-mode QC. BGC: variable by sensor (O2 with air-cal high; chl fluorescence needs quenching corrections). Glider T/S/O2/optics: high when calibrated. AUV imagery: see 3.3. **Floats do not observe fish.** |
| **Limitations** | Argo: parking-depth drift, ice, western-boundary gaps, no steering. Gliders: slow, current-limited, biofouling. AUV: endurance/logistics. |
| **Costs** | BGC-Argo **CITED ~$100k lifetime, $25M/yr global design**. Core Argo unit **UNKNOWN** here. Glider campaigns **UNKNOWN**. |
| **Scalability** | Argo is the existence proof of global robotics. Biology payloads (optics, eDNA, acoustics) on gliders/AUVs are the **scalable path into the volume**. |
| **Latency** | Argo real-time hours (U.S. DAC Jun 2026: **3.3 h median** float→GDAC/GTS — CITED NOAA AOML metrics). Delayed-mode months. |
| **Resolution** | Argo ~3° design; profiles every ~5–10 days. Gliders: km along-track, metres vertical. |
| **Coverage** | Open ocean good; shelves, ice, EEZ permissions, and deep trenches uneven. |
| **Regulatory** | UNCLOS EEZ notifications; some coastal states restrict gliders; marine-mammal interaction low but not zero. |
| **Privacy / ecological** | Low for Argo T/S. AUV cameras: same as 3.3. |
| **Integration** | **3D physics/BGC backbone** of any twin; glider acoustics/eDNA as mobile labs; ROV for benthic ground truth. |
| **Breakthrough potential** | **High** for plankton/microbes (BGC-Argo + PACE) and for **directed sampling of features**. Fish: only with acoustic/optical/eDNA payloads — still local. |

**Taxa:** Direct: microbes/plankton **proxies** (chl, backscatter, O2 drawdown), jellies/larvae if imaging payload, benthos if ROV. Inferred: hypoxic habitat for crabs/fish. Needs infra: EK/eDNA-equipped glider networks. Impossible: Argo as a fish counter.

---

## 3.9 Fixed sensors / buoys / infrastructure

| Field | Assessment |
| --- | --- |
| **Maturity** | **Operational:** NDBC, OceanSITES, GLOSS tide gauges, IOOS buoys, CO-OPS, HF radar (surface currents 500 m–6 km by frequency — IOOS), cabled observatories (OOI, ONC, JAMSTEC DONET/N-net — geography-limited), aquaculture farm sensors. |
| **Data availability** | High for **physics** at points/coasts. Biology payloads (PAM, cameras, fluorometers, eDNA autosamplers, oyster-farm DO) **uneven**. |
| **Scientific validity** | High for the measured scalar at the sensor. Spatial representativity is the issue (a Hood Canal ORCA buoy is not Willapa). |
| **Limitations** | Point support; vandalism; biofouling; gaps between buoys of hundreds of km offshore. HF radar is **surface current**, not biology. |
| **Costs** | Mooring CAPEX **UNKNOWN**. **Reuse IOOS** is the cheap path. |
| **Scalability** | Linear with sites. Cabled nodes expensive but high bandwidth (cameras/PAM). |
| **Latency** | Minutes–hours typical for NDBC/IOOS. |
| **Resolution** | Point or HF-radar grid (0.5–6 km). |
| **Coverage** | Coasts of wealthy states; OceanSITES open-ocean sparse. |
| **Regulatory** | Permitting, aids-to-navigation, cable crossings, ITAR on some ADCPs **UNKNOWN**. |
| **Privacy / ecological** | Farm sensors are **PRIVATE** (commercial wedge policy). Public buoys OK. |
| **Integration** | Assimilation anchors; farm/charter **stress and catchability** covariates (DO, bottom T, waves). |
| **Breakthrough potential** | Medium unless **biology payloads** (PAM, eDNA, cameras) ride existing power/comms. |

**Taxa:** Direct biology only if bio-sensor present. Otherwise all taxa **INFERRED** via habitat (O2, T, pH, chl, waves). Shellfish farms: operational DO/T **DIRECT** for the cultivated stock’s environment, not wild census.

---

## 3.10 Commercial vessels / fishing gear / opportunistic

| Field | Assessment |
| --- | --- |
| **Maturity** | **Operational** as fisheries-dependent data (logbooks, observers, VMS, e-logbooks, factory scales). Research fleets (CFRF lobster, eMOLT bottom T) show the science pattern. Opportunistic oceanography: SOOP/XBT, ferrybox, CPR (plankton), EMS/echosounder on fishing vessels — **mature in pockets**. |
| **Data availability** | Catch/effort often **confidential** (MSA, EU DCF, national stats). Public landings are coarse. AIS public-incomplete; VMS restricted (NMFS 06-101). |
| **Scientific validity** | High for **catch at the gear** (`OPERATIONALLY OBSERVED`). **Catch ≠ abundance** (catchability). Observer programs better than logbooks for discards. CPR: gold-standard plankton time series along routes. |
| **Limitations** | Effort targeting; hyperstability of CPUE; misreporting; spatial preference; AIS spoof/off; bycatch under-report. |
| **Costs** | Marginal cost of extra sensors on existing trips can be low. Data-rights negotiations dominate. |
| **Scalability** | **Highest biological sampling rate on Earth** if privacy-preserving contribution exists. |
| **Latency** | Hours (AIS) to years (some official stats). |
| **Resolution** | Haul/set — too fine to publish. |
| **Coverage** | Where it is profitable to fish — **not** unfished ocean. |
| **Regulatory** | MSA confidentiality; GDPR/personal data on crew; IMO AIS carriage; IUU rules. |
| **Privacy / ecological risk** | **Secret spots, vessel identity, listed-species bycatch**. See privacy-preserving section below. |
| **Integration** | Category C CPUE labels; opportunistic acoustics; hull sensors; eDNA underway; CPR. |
| **Breakthrough potential** | **Highest information-per-dollar for exploited stocks** if DUAs exist. Zero value if used as public hotspot maps. |

**Privacy-preserving vessel contribution (explicit):**

- Store native haul GPS as `PRIVATE`; publish only **coarse cells** with k-anonymity (rule-of-3 vessels) as in the commercial privacy policy.
- Prefer **on-vessel aggregation**: share effort-normalized indices, not tracks.
- Separate **identity (MMSI)** from **science payload** (EK, T, eDNA).
- VMS: authority-to-authority only unless a government publishes delayed VMS (GFW partnerships).
- AIS: use as **effort/safety context**, never abundance; drop vessel-level public replay.
- Cameras (EM): face/crew redaction; retain catch events under DUA.
- Contribute to models as **likelihoods**, not as raw points.

**Taxa:** Direct for **target and bycatch** in gear (finfish, sharks, shellfish, crustaceans, cephalopods, sometimes turtles/mammals/birds as bycatch — sensitive). Plankton via CPR. Not a survey of unexploited taxa.

---

## 3.11 Subsea telecom cables / DAS / DTS

| Field | Assessment |
| --- | --- |
| **Maturity** | **DAS:** demonstrated for **baleen whales**, ships, storms, quakes (Bouffaut et al. 2022; Rørstadbotnen et al. 2023: eight fin whales, ~100 m localization on calibrated airgun, ~800 km²; ~40–95 km from interrogator). Frequency typically useful **≲100–150 Hz** vs hydrophones. **DTS:** temperature along fiber — oceanographic use **emerging**. **SMART cables:** ITU/WMO/UNESCO-IOC JTF; ITU-T **G.9730.2 (08/2024)** specifies T, P, 3-axis acceleration at repeaters; DFOS optional at landing. **Not** a completed global SMART grid. |
| **Data availability** | Research campaigns; cable-owner NDAs. Not an open global feed. |
| **Scientific validity** | High for **low-frequency acoustics along coupled cable**. Lower sensitivity/noisier than ceramic hydrophones; coupling and armor modulate response (MTS Journal 2025 review). SMART T/P: climate/tsunami value **modeled**, few systems in water relative to vision. |
| **Limitations** | Dark fiber access; repeatered systems harder for DAS; directionality; data **~1 Gb/s** class; not fish-finding sonar; not eDNA. |
| **Costs** | Interrogator + access **UNKNOWN**. Incremental SMART sensors advertised as modest vs new observatory — **dollar CITED increment UNKNOWN** in this catalog (Howe et al. 2019 discusses modest incremental cost qualitatively). |
| **Scalability** | **Potentially global** along ~million km of cable **if** owners agree. Politics &gt; physics. |
| **Latency** | Near-real-time demonstrated (Svalbard→NTNU stream). |
| **Resolution** | Channel spacing **~4 m** in Arctic DAS example; useful acoustic localization ~100 m in that experiment. |
| **Coverage** | Cable routes: coasts, basins, not uniformly the mesopelagic volume. |
| **Regulatory** | Critical infrastructure; UNCLOS; national security; landing licenses. |
| **Privacy / ecological** | Ship tracking along cables; whale real-time positions. |
| **Integration** | PAM layer at unprecedented along-track density; SMART T/P into climate/tsunami; **not** a substitute for fisheries acoustics. |
| **Breakthrough potential** | **Very high for vocal baleen whales and geophysics.** Low for silent invertebrates. **UNPROVEN** as a general marine-life observatory. |

**Taxa:** Direct: vocal baleen (demonstrated), ships. Unproven: some low-frequency fish. Speculative: many odontocetes (frequency too high). Impossible: imaging crabs on the abyssal plain with DAS.

---

## 3.12 Chemical / biological / physical proxies

| Field | Assessment |
| --- | --- |
| **Maturity** | **Operational** GOOS EOVs: T, S, currents, sea level, O2, nutrients, pH/DIC, chl, ocean colour. Products: CMEMS, RTOFS, GODAS, BGC-Argo, GO-SHIP, SOCAT pCO2. |
| **Scientific validity** | High as **environment**. Invalid as **animals**. Hypoxia **can** be mechanistically linked to crab/fish catchability and mortality **where calibrated**. OA is first-order for **larval calcifiers**, weak for 72 h adult oyster death (see marine-domain limitations). |
| **Limitations** | Proxy lag, non-stationarity, multiple stressors, vertical mismatch (SST ≠ bottom T). |
| **Costs** | Included in satellite/Argo/buoy programs. |
| **Scalability** | Global physics already. Biology-quality BGC still short of design density. |
| **Latency** | Hours–days models; months GO-SHIP. |
| **Resolution** | Model 1–25 km typical; coastal needs nested. |
| **Coverage** | Global with coastal/ice error. |
| **Regulatory** | Standard ocean data. |
| **Privacy** | Low. |
| **Integration** | **Always-on covariates**; habitat envelopes; stress indices (oyster heat×tide; lobster bottom T). |
| **Breakthrough potential** | Incremental except **oxygen/pH at shelf scale** (glider+BGC) which unlocks crustacean/shellfish **stress**, not maps of individuals. |

**Taxa:** All: **INFERRED habitat / stress / prey-field proxies only**. Direct for microbes only insofar as pigments/O2/NO3 are microbial processes. Forecast: physical fields skillful at 24–72 h; biological translation **must be validated per taxon**.

---

## 3.13 Human / community observations (consent, sovereignty, sensitive locations)

| Field | Assessment |
| --- | --- |
| **Maturity** | **Operational** in patches: eBird/seabird colonies, iNaturalist marine (uneven QA), stranding networks, fisher logbooks, Indigenous guardian programs, NOAA citizen HAB/Sargassum photos (AOML form linked from SIR). |
| **Scientific validity** | High when protocols exist (breeding bird counts, standardized creel). Presence-only community data are **effort-biased**. Traditional Ecological Knowledge is **valid on its own terms** and is not a free dataset. |
| **Limitations** | Spatial bias to beaches/ports; mis-ID; harassment risk if locations published; extractive research history with Indigenous nations. |
| **Costs** | Low marginal; trust is the cost. |
| **Scalability** | High for coastal visible taxa; zero for mesopelagic without gear. |
| **Latency** | Same-day possible. |
| **Resolution** | Point observations — **too fine to publish** for harvest/listed species. |
| **Coverage** | Human coastline, not ABNJ. |
| **Regulatory / sovereignty** | CARE Principles; UNDRIP; tribal IRB/data ordinances; MMPA reporting; GDPR. **Default `NEVER_PUBLISH` for Indigenous knowledge** unless a nation licenses it. |
| **Privacy / ecological** | Nesting beaches, spawning, fishing spots, sacred sites. Consent is revocable. |
| **Integration** | Occupancy, phenology, event detection (strandings, Sargassum beaching), **labels** for satellite ML. |
| **Breakthrough potential** | High for **coastal events and legitimacy**. Not a global fish twin by itself. |

**Taxa:** Direct: seabirds, some mammals (strandings, watches), turtles (nests — sensitive), intertidal, some sharks (landings), jellyfish strandings, Sargassum, HABs, catch. Weak: larvae, microbes, deep benthos.

---

## Taxa × modality summary (see CSV for full cells)

Full matrix: `observation_coverage_maps/taxa_modality_feasibility.csv` (15 taxon classes × 13 modalities).

**Reading rule:** “Direct” means the modality can record the organism (or its sound/DNA/image/backscatter) **today in some real setting**, not everywhere always.

| Taxon | Best direct tools today | Best inference | Honest forecast | Still mostly invisible without new infra |
| --- | --- | --- | --- | --- |
| Finfish | Surveys, acoustics+trawl, catch, cameras, tags (large spp), eDNA occupancy | Habitat T/O2/fronts | 24–72 h **encounter/CPUE** only with local labels | Mesopelagic diversity, global N |
| Sharks/rays | Tags, BRUV, catch, eDNA, rare VHR | SST habitat | Seasonal habitat | Oceanic rare spp abundance |
| Shellfish | Surveys, farm counts, intertidal optics, eDNA | Heat×tide, SST, HABs as **other** processes | Farm **stress windows** | Wild subtidal census |
| Crustaceans | Traps/surveys, eDNA, some acoustic tags | **Bottom T**, hypoxia | Next-trip CPUE with labels | Global lobster N from space |
| Cephalopods | Catch, cameras, some acoustics | Weak habitat | Weak | Open-ocean abundance |
| Marine mammals | PAM, DAS, tags, aerial/VHR, surveys | Prey fields | Migration envelopes | Real-time global tracks |
| Turtles | Tags, nesting counts, bycatch | SST | Nesting phenology | In-water global N |
| Seabirds | Colony counts, tags, eBird, aerial | Forage habitat | Colony | At-sea small alcids globally |
| Plankton | Ocean color, CPR, BGC-Argo, nets, UVP | Physics | Blooms regional | Species-resolved global |
| Jellyfish | Cameras, some nets, strandings | — | — | Basin abundance |
| Corals | Divers/ROV, habitat satellites, CRW heat | DHW | Bleaching outlook (heat) | Cryptic/deep diversity |
| Benthos | Grabs, ROV, imagery | Substrate maps | — | Abyssal time series |
| Plants/algae | Satellites (*Sargassum*, kelp, seagrass), drones | — | Sargassum SIR experimental | Subcanopy C globally |
| Microbes | Omics, flow cytometry, PACE PFTs, BGC-Argo | Nutrients/light | — | Function at basin scale |
| Larvae | Specialized imagers, nets, eDNA, otoliths | Particle tracking | Dispersal of **water** | Named larva everywhere |

---

## Highest-leverage ways to observe currently invisible organisms

“Invisible” here means: not in satellite pixels, not in a stock assessment, not tagged.

1. **eDNA occupancy time series on existing ships, intakes, and IOOS buoys**, interpreted as a **tracer with a hydrodynamic kernel**, not a pin on a map. Highest new taxa per dollar for cryptic fish, larvae presence, invasives, mammals in turbid water.
2. **Calibrated opportunistic fisheries acoustics** (already-paid EK on working vessels) with on-vessel aggregation and camera/eDNA ID snapshots. Makes mesopelagic and pelagic **backscatter** visible along fishing/transit graphs.
3. **PAM + DAS on existing cables/sanctuaries** for vocal taxa that light cannot reach (fin/blue/humpback, some fishes).
4. **Animal-borne sensors (AniBOS/ATN)** — not more tags for census, but **T/S/O2 profiles and movement kernels** that make habitat models honest in the vertical.
5. **AUV/glider payloads** (EK80 + camera + eDNA) **cued by satellite fronts/SWOT eddies/PACE blooms** — directed volume sampling beats random ocean.
6. **Stereo imagery + ML at photic and ROV depths** for benthos, jellies, reef fish — the only direct ID for many invertebrates.
7. **BGC-Argo toward the 1000-float design + PACE MOANA validation** — microbes/plankton in 3D, including under clouds and at night (floats).
8. **Privacy-preserving CPUE and EM** for exploited species — the densest biological samples that already exist.
9. **Community + guardian observations with CARE consent** for coastal events satellites miss (strandings, slime, scyphozoan pulses).
10. **Data assimilation that refuses to call proxies observations** — the leverage is **correct typing** so invisible remains labeled `UNKNOWN` instead of a fake map.

---

## Top 10 methods by information-per-dollar

Order-of-magnitude, **not** a procurement quote. Mix of `CITED` reuse and `ESTIMATE` judgment. All assume lawful access.

| Rank | Method | Why cheap relative to information | What you actually get |
| --- | --- | --- | --- |
| 1 | **Reuse public SST/color/altimetry/CRW/SaWS** | Agency-paid; global | Habitat, blooms, Sargassum, heat stress — **not fish N** |
| 2 | **Reuse IOOS/NDBC/HF radar/OceanSITES** | Already transmitting | Physics at points/coasts; catchability covariates |
| 3 | **Reuse Argo + push BGC toward design** | CITED ~$100k/float lifetime vs ship-days | 3D T/S/BGC; plankton/microbe proxies |
| 4 | **eDNA on ships of opportunity** | Water is free; lab scalable | Occupancy of many taxa; not abundance |
| 5 | **Opportunistic vessel EK + privacy aggregation** | Sensors already on hulls | Pelagic backscatter along tracks |
| 6 | **NCEI PAM / ONMS Sound archives + open detectors** | Tape already recorded | Vocal mammal/fish occupancy |
| 7 | **ATN/OTN/AniBOS reuse** | Tags already in water | Movement kernels; animal-borne profiles |
| 8 | **Sentinel-2/Landsat habitat mapping** | Free 10–30 m | Seagrass/kelp/shallow reef **habitat** |
| 9 | **DAS on dark fiber where owners agree** | Fiber already laid | Baleen tracking along cables (research→ops) |
| 10 | **Consenting community/stranding/CPR-like routes** | Humans already looking | Events, plankton lines, legitimacy |

**Deliberately not in the top 10:** a dedicated global VHR whale constellation (cost **UNKNOWN**, completeness low); tagging every stock; uncalibrated AIS-as-fish; a new global hydrophone grid built from scratch without cables.

---

## Integration recipe (for the digital twin)

Do not ingest in this iteration. When lawful:

1. Type every layer with the output classes above.  
2. Use satellites and models for **state of water**.  
3. Use acoustics/catch/cameras/tags/eDNA/PAM/DAS for **state of life**, each with bias models.  
4. Train movement/habitat models on tags; validate on surveys; never invert AIS to N.  
5. Cue expensive platforms (AUV, ship) with cheap wide-field (satellite, DAS event, HAB alert).  
6. Coarsen public outputs; keep partner/Indigenous/listed-species native resolution out of PUBLIC tiles.

---

## Sources (accessed 2026-09-18)

Official / agency:

- NOAA CoastWatch VIIRS ocean color & SST: https://coastwatch.noaa.gov/cwn/instruments/viirs.html · https://coastwatch.noaa.gov/cwn/product-families/sea-surface-temperature.html · https://coastwatch.noaa.gov/cwn/products/noaa-msl12-ocean-color-science-quality-viirs-snpp.html  
- NOAA Coral Reef Watch 5 km v3.1: https://coralreefwatch.noaa.gov/product/5km/  
- NOAA CoastWatch Sargassum Inundation Risk: https://cwcgom.aoml.noaa.gov/SIR/  
- NOAA NCCOS Sargassum forecasting project: https://coastalscience.noaa.gov/project/developing-an-operational-sargassum-hab-monitoring-and-forecasting-system-for-the-southeastern-u-s-and-u-s-caribbean/  
- USF Sargassum Watch System: https://optics.marine.usf.edu/projects/saws.html  
- NASA PACE: https://www.nasa.gov/missions/pace/nasas-pace-us-european-swot-satellites-offer-combined-look-at-ocean/ · MOANA: https://www.earthdata.nasa.gov/data/catalog/ob-cloud-pace-oci-l4m-moana-3.1  
- Copernicus Marine ocean colour L3 NRT: https://data.marine.copernicus.eu/product/OCEANCOLOUR_GLO_BGC_L3_NRT_009_101/description · catalogue home: https://marine.copernicus.eu/  
- IOOS: https://ioos.noaa.gov/ · data access https://ioos.noaa.gov/data/access-ioos-data/ · ATN https://ioos.noaa.gov/project/atn/ · portal https://portal.atn.ioos.us/  
- NCEI ATN: https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc%3AIOOS-ATN-STP  
- NOAA Omics: https://oceanexplorer.noaa.gov/noaa-omics/ · AOML https://www.aoml.noaa.gov/omics/ · PMEL OME https://www.pmel.noaa.gov/ocean-molecular-ecology/  
- NCEI PAM: https://www.ncei.noaa.gov/products/passive-acoustic-data · ONMS Sound https://sanctuaries.noaa.gov/science/monitoring/sound/  
- Argo status: https://argo.ucsd.edu/about/status/ · BGC mission https://argo.ucsd.edu/expansion/biogeochemical-argo-mission/ · NOAA AOML Argo https://www.aoml.noaa.gov/argo/  
- Euro-Argo fleet monitor: https://fleetmonitoring.euro-argo.eu/dashboard?Status=Active  
- OBIS: https://obis.org/ (224M observations, 207K species, 7,363 datasets on access date)  
- OceanSITES: https://www.ocean-ops.org/oceansites/  
- Global HF Radar Network: http://global-hfradar.org/  
- ITU SMART cables JTF: https://www.itu.int/en/ITU-T/climatechange/task-force-sc/Pages/default.aspx  
- NMFS VMS policy 06-101: https://www.fisheries.noaa.gov/s3/2023-10/NMFS-06-101-Data-Dissemination-2023-10.5.2023-508-Compliant-signed-1-.pdf  
- NOAA Ocean Service ATN explainer: https://oceanservice.noaa.gov/ocean/animal-telemetry.html  

Peer-reviewed / official reports (cite, do not copy):

- ICES CRR 344 Acoustic target classification https://doi.org/10.17895/ices.pub.4567  
- Korneliussen et al. acoustic species ID https://doi.org/10.1093/icesjms/fsp119  
- Jones et al. NOAA pollock broadband https://repository.library.noaa.gov/view/noaa/52568  
- Cubaynes et al. / mammal VHR review *JMSE* https://doi.org/10.3390/jmse11030595  
- DFO 2022 Megafauna from Space https://publications.gc.ca/collections/collection_2022/mpo-dfo/Fs97-4-3248-eng.pdf  
- Williamson et al. 2019 SRS in shark ecology https://doi.org/10.3389/fmars.2019.00135  
- Nagel / O’Neill Sentinel-2 vs WV-3 habitat https://www.mdpi.com/2072-4292/14/5/1254  
- Harrison et al. 2019 eDNA fate https://pmc.ncbi.nlm.nih.gov/articles/PMC6892050/  
- Andruszkiewicz / *Environmental DNA* transport reviews including https://doi.org/10.1002/edn3.405 and 2025 spatial bound https://www.frontiersin.org/articles/10.3389/fmars.2025.1613001  
- Sequeira et al. 2021 tracking bias https://doi.org/10.1111/2041-210X.13507  
- Bouffaut et al. 2022 DAS whales https://www.frontiersin.org/articles/10.3389/fmars.2022.901348  
- Rørstadbotnen et al. 2023 multi-whale DAS https://www.frontiersin.org/articles/10.3389/fmars.2023.1130898  
- Howe et al. 2019 SMART cables https://doi.org/10.3389/fmars.2019.00424  
- OBIS infrastructure review https://www.frontiersin.org/articles/10.3389/fmars.2019.00588  
- BGC-Argo guide https://www.frontiersin.org/articles/10.3389/fmars.2019.00502  

**License status:** NOAA/U.S. government works generally public domain **as publications**; dataset-level constraints still **UNKNOWN** until rights review. Copernicus Marine licence terms **UNKNOWN** for commercial forecast resale (do not assume). Journal papers: cite only, no bulk copy. OBIS: follow OBIS/publisher terms; WoRMS not to be fully redistributed.

---

## What this cluster did not do

No bulk download, no scraping behind logins, no model training, no precise maps of listed species, no claim that a global living twin already exists, no contradiction of the commercial wedge’s “no SST-as-abundance / no public secret spots” rules.
