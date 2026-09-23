# Agent handoff — OBSERVATION_MODALITY cluster

**Project:** GLOBAL SALTWATER LIFE OBSERVATORY / FishAI scientific blueprint  
**Date / URL access:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/` only  
**Did not write:** `/Users/wijeratne/dev/fishai/artifacts/**`  
**Ingestion:** none. No bulk download, no sequences, no EK, no AIS firehose.

**Relation to commercial wedge:** The 1-species product (oyster / Chinook / lobster candidates) stays narrow. This cluster catalogs **how saltwater life can be observed at all**. It agrees with marine-domain prohibitions: SST/chl/AIS are not abundance; catch ≠ N; listed-species points are not public; oyster DOH closures are not stress labels; lobster needs **bottom T** not SST.

---

## 1. Executive finding

There is **no global sensor that sees most marine animals**. A living observatory is a **fusion problem** with typed evidence, not a satellite product.

**Direct from space today (conditional):** phytoplankton/chl and some PACE picoplankton groups; pelagic *Sargassum* mats; HAB **proxies** (not toxin); shallow seagrass/kelp/reef **habitat**; coral **heat-stress** (CRW DHW, not live coral); VHR surface whales and ice/land pinnipeds (research, not census); rare large sharks/rays in clear shallows; seabird colonies.

**Not from space as organisms:** almost all finfish, crustaceans, cephalopods, larvae, microbes-as-cells, deep fauna. **Lobster/crab from SST is impossible as a measurement** (wrong depth).

**Indirect paths that do constrain “invisible” fish:** satellite physics + Argo/glider 3D habitat; tags teaching movement; opportunistic EK; eDNA as a tracer with a hydrodynamic kernel; PAM/DAS for vocal taxa; cameras+ML in the photic/ROV volume; privacy-preserving vessel CPUE; data assimilation that refuses to relabel proxies as observations.

**Highest leverage for currently invisible organisms:** (1) eDNA occupancy time series on existing ships/intakes/buoys, (2) calibrated opportunistic fisheries acoustics, (3) PAM+DAS on existing cables, (4) AniBOS/ATN as vertical-habitat teachers not censuses, (5) AUV payloads cued by satellite fronts, (6) BGC-Argo toward the CITED 1000-float / ~$25M/yr design.

**Top information-per-dollar:** reuse already-paid NOAA/Copernicus satellites, IOOS/NDBC, Argo, NCEI PAM, ATN/OTN, Sentinel-2 habitat, CPR/SOOP, then eDNA-on-SOOP and privacy-preserving vessel EK. Do not lead with a VHR whale constellation or tagging every stock.

**Hard physical limits:** seawater opacity (optical/IR); pixel vs organism; acoustic frequency–range–ID overlap; eDNA plume ≠ GPS; tagged subset ≠ population; catch/AIS = effort; global exact census of mobile animals is **IMPOSSIBLE**.

---

## 2. Evidence table

| Finding | Evidence | Confidence |
| --- | --- | --- |
| VIIRS OC 750 m L2 / 4 km L3; SST ACSPO + 5 km blended | NOAA CoastWatch product pages | High |
| OLCI 300 m and 4 km plankton products | CMEMS OCEANCOLOUR_GLO_BGC_L3_NRT_009_101 | High |
| PACE MOANA picoplankton groups | NASA Earthdata MOANA 3.1; SWOT+PACE papers | High (product still provisional in literature) |
| CRW daily 5 km DHW operational | coralreefwatch.noaa.gov/product/5km | High |
| Sargassum SIR daily; labeled **experimental** | NOAA AOML CoastWatch SIR v1.5 | High |
| VHR whales/sharks research not ops census | Cubaynes *JMSE*; DFO 2022 *Megafauna from Space* | High |
| Elasmobranch “satellites” usually = SST habitat | Williamson et al. 2019 | High |
| Acoustic species ID structurally limited | ICES CRR 344; NOAA pollock broadband | High |
| eDNA transport hours / 0.3–39 km; models often > field | Harrison 2019; edn3.405; 2025 spatial-bound; edn3.70140 | High on **range**, not a single kernel |
| ~4000 Argo; BGC ~$100k/float, $25M/yr design 1000 | argo.ucsd.edu; Euro-Argo 4334 active snapshot | High |
| DAS baleen tracking demonstrated | Bouffaut 2022; Rørstadbotnen 2023 | High as research |
| SMART cables standardized T/P/accel | ITU-T G.9730.2 (2024-08) | High as spec; low as deployed grid |
| OBIS 224M obs / 207K spp / 7363 datasets | obis.org 2026-09-18 | High as counts; biased coverage |
| VMS confidential; AIS ≠ fish | NMFS 06-101; GFW | High |
| ATN exists; QC ≠ representativeness | IOOS ATN; Sequeira 2021 | High |

Costs other than BGC-Argo lifetime/array: **UNKNOWN** (not invented). CMEMS/IOOS **commercial-resale licences UNKNOWN**.

---

## 3. Source / license table (planning only)

| Source | URL | Licence as findable | Use |
| --- | --- | --- | --- |
| NOAA CoastWatch / CRW / NDBC / CO-OPS / ONMS / Omics | linked in catalog | U.S. Gov works typical; **dataset TOS UNKNOWN** | Physics, PAM, omics strategy |
| Copernicus Marine | https://marine.copernicus.eu/ | **UNKNOWN** commercial resale | Catalog |
| NASA PACE/Earthdata | earthdata.nasa.gov | Earthdata TOS **UNKNOWN** | Picoplankton |
| IOOS / ATN | ioos.noaa.gov | **UNKNOWN** per feed | Networks, tags |
| OBIS | https://obis.org/ | Follow OBIS terms | Occurrence prior |
| ITU SMART / G.9730.2 | itu.int JTF pages | ITU rec | Cable future |
| Journals listed in catalog | DOIs | Cite, do not copy | Limits |

---

## 4. Confidence and limitations of **this dossier**

| Area | Confidence | Limitation |
| --- | --- | --- |
| Physical impossibility of satellite fish census | High | Indirect fusion still required |
| Operational vs research split (CRW vs VHR whales vs SIR experimental) | High | Labels change; re-check pages |
| eDNA kernel metres vs km | Medium | Literature disagrees; local oceanography required |
| DAS as general life observatory | High that it is **not** | Baleen-only sweet spot |
| Cost ranking | Medium | Only BGC-Argo dollars CITED |
| Global completeness % | **UNKNOWN** | Not estimated |
| TRLs | **UNKNOWN** | Maturity described in words |
| 2026 PACE operational status | Medium | MOANA still described as provisional in sources |

Did not: ingest, interview, map listed-species sites, claim a twin exists, contradict as-of-replay / privacy tiers of the geospatial agent.

---

## 5. Recommended decisions (observatory, not wedge lock)

1. Treat satellites as **water-state and a few surface-biology products**, never as fish N.  
2. Fund **reuse** (Argo/IOOS/PAM/ATN/S2/CPR) before new hulls.  
3. For invisible taxa, prioritize **eDNA-on-SOOP + opportunistic EK + DAS partnerships + directed AUV**.  
4. Type every twin layer: `DIRECTLY OBSERVED` vs `MODEL-INFERRED` vs `FORECAST` vs `UNKNOWN`.  
5. Privacy-preserving vessel contribution is mandatory if M10 is used (k-anonymity, no MMSI in PUBLIC, no VMS without authority DUA).  
6. Commercial wedge: oyster → M09+M12+tides (not SST-as-oyster); Chinook → M12 habitat + M10 labels (not chl-as-bite); lobster → **bottom T** + M10 CPUE (not M01).

---

## 6. Rejected alternatives

| Alternative | Why rejected |
| --- | --- |
| “Satellites cannot see fish, stop” | Ignores fusion paths the spec required |
| VIIRS/AIS fish maps | Category error; privacy |
| Uncalibrated eDNA biomass | Transport/decay/shedding unknown |
| DAS as universal hydrophone replacement | Band, SNR, coupling |
| Tagging toward census | Subset bias; cannot tag plankton |
| Global VHR whale ops as first spend | Cost UNKNOWN; completeness low |
| Invented TRLs and ship-day prices | Honesty rule |

---

## 7. Follow-ups

1. Rights agent: CMEMS, OBIS, ATN, NANOOS, PAM archive commercial use.  
2. Hypothetical-tech agent: in-situ eDNA sequencers, eRNA kernels, DAS fish, BGC-eDNA on floats — keep typed as UNPROVEN/SPECULATIVE until evidence.  
3. Architecture/DA: evidence-typed assimilation of M01+M04+M06+M07+M10.  
4. If wedge locks C1/C2/C3, instantiate only the modalities in §5.6, not this global catalog.

---

## 8. Artifacts produced

| Path | Role |
| --- | --- |
| `observatory/observation_modality_catalog.md` | All 13 modalities; taxa; limits; top 10; citations |
| `observatory/satellite_capability_matrix.md` | Sensor vs animal detection matrix |
| `observatory/sensor_network_catalog/README.md` | Network classes |
| `observatory/sensor_network_catalog/networks.csv` | Machine catalog |
| `observatory/direct_observation_registry/README.md` | Surveys, cameras, catch |
| `observatory/telemetry_registry/README.md` | Tags + bias |
| `observatory/eDNA_registry/README.md` | Transport/decay meaning |
| `observatory/acoustic_registry/README.md` | EK, PAM, DAS, ID limits |
| `observatory/observation_coverage_maps/taxa_modality_feasibility.csv` | 195-cell matrix |
| `observatory/observation_coverage_maps/README.md` | How to read matrix |
| `observatory/observation_coverage_maps/_build_feasibility.py` | Regenerator |
| `observatory/artifacts/modalities/agent_handoff.md` | This file |

---

## 9. Red-team?

**Yes — scientific.** Highest-severity misreads:

- Publishing VHR/PAM/DAS whale points.  
- Training “fish” on chl.  
- Selling SIR/CRW as navigation or harvest.  
- Treating ATN hexes as abundance.  
- Treating eDNA hits as GPS.  
- Treating opportunistic EK as public hotspot maps.

---

## 10. Suggested next experiment (no ingest)

Paper protocol: for one named shelf box, list **already public** layers (CRW or SST, one NDBC/IOOS buoy, one OBIS occurrence count by taxon class — counts from the portal UI only if TOS allow, else skip). Score which of the 15 taxon classes have `DIRECT` vs `UNKNOWN` **in that box**. Stop if the only “biology” layer is chl. That is the cheapest honesty test of a twin pixel.

---

## Return block (for parent agent)

**Satellites today:** operational for SST/color/altimetry/CRW heat-stress/*Sargassum* (SIR experimental); PACE picoplankton provisional; VHR whales/pinnipeds/clear-water megafauna **research**; **cannot** census fish, lobster, larvae, most sharks.

**Indirect paths:** habitat volume (sat+Argo) → tags/movement → vessel EK/CPUE (private) → eDNA tracer → PAM/DAS → AUV cameras → assimilation with typed uncertainty.

**Sonar:** biomass of validated scatterers yes; species ID no when TS overlap (ICES/NOAA).

**eDNA:** occupancy in a plume (hours; 0.3–39 km modeled; field often shorter); not N.

**Tags:** individuals; location/device/gap/failure bias (Sequeira 2021).

**Vessels:** densest biology if privacy-preserving; VMS restricted; AIS ≠ abundance.

**Highest leverage / top $/info / hard limits:** see §1 and `observation_modality_catalog.md` closing sections.

**Matrix:** 15 × 13 = 195 rows in `observation_coverage_maps/taxa_modality_feasibility.csv`.
