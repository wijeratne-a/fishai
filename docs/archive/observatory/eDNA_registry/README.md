# eDNA / genomics / molecular registry

**Program:** GLOBAL SALTWATER LIFE OBSERVATORY  
**Date / access:** 2026-09-18  
**Modality:** 3.6  
**Ingestion:** none. No sequences downloaded.

---

## What eDNA is (and is not)

Environmental DNA/RNA is molecules shed into water, sediment, or biofilm. A positive assay is **`DIRECTLY OBSERVED` molecules** and only **`MODEL-INFERRED` organism presence in a neighborhood** after transport/decay are considered.

It is **not**: a headcount, a biomass, a GPS of the animal, a harvest authorization, or a substitute for morphological vouchers when naming new operational products.

---

## Official programs (catalog)

| Program | URL | Role |
| --- | --- | --- |
| NOAA Omics | https://oceanexplorer.noaa.gov/noaa-omics/ | Agency strategy: fisheries, protected species, monitoring |
| NOAA Omics Strategic Plan (PDF) | https://oceanexplorer.noaa.gov/wp-content/uploads/2025/05/Omics-Strategic-Plan_Final-Signed.pdf | Time series, autonomous devices, reference libraries |
| AOML Omics | https://www.aoml.noaa.gov/omics/ | Coral, fisheries, inexpensive autosamplers |
| PMEL Ocean Molecular Ecology | https://www.pmel.noaa.gov/ocean-molecular-ecology/ | Standards, BeBOP protocols, eDNA2OBIS, autonomous ROSCI/PPS |
| OBIS DNA-derived publishing | https://obis.org/ (news 2026-07-10 on DNA-derived data capacity) | Occurrence aggregator path |
| IOOS / MBON | https://ioos.noaa.gov/ | Regional biodiversity + omics pilots |

Licence/TOS for sequence reuse: **UNKNOWN** until rights review. Nagoya Protocol / ABS may apply to genetic resources outside the U.S. CARE principles for Indigenous genomics.

---

## Assay types

| Assay | Output | Abundance? | Best use |
| --- | --- | --- | --- |
| Metabarcoding (12S/16S/18S/COI etc.) | Community list | Rank at best, biased | Occupancy, diversity, invasives |
| qPCR / dPCR | Target species copies | Sometimes after calibration | Listed/invasive/fishery targets |
| eRNA | Shorter-lived tracer | **UNPROVEN** ops | Possibly tighter space/time |
| Shotgun / metagenome | Functions + taxa | Hard | Microbes |
| eDNA from sediment | Longer archive | Mixed | Benthos, history |
| Tissue / barcoding | Voucher | N/A | Reference libraries (bottleneck) |

Reference-library gaps: many marine invertebrates, larvae, and microbes cannot be named to species. PMEL explicitly invests in reference mitogenomes for this reason.

---

## Spatial and temporal meaning (transport and decay)

Published marine results **do not agree on a single kernel**. Report ranges, not a fake precision.

| Source | Finding | Use |
| --- | --- | --- |
| Harrison et al. 2019 *Proc. R. Soc. B* https://pmc.ncbi.nlm.nih.gov/articles/PMC6892050/ | Fate = shedding × decay × transport; environment-specific | Do not copy freshwater kernels into the ocean |
| Andruszkiewicz et al. (cited in decay reviews) | Modeled order-of **~10 km in a few days** | Upper modeled bound |
| Murakami et al. 2019 (cited in *eDNA* 2023 review https://doi.org/10.1002/edn3.405) | Field detections often **≲30 m** from source in that study | Models can **overestimate** transport |
| Front. Mar. Sci. 2025 spatial bound https://www.frontiersin.org/articles/10.3389/fmars.2025.1613001 | Modeled median **2.27–14.14 km**; tides first, then temperature/decay; up to **10×** observed | Local oceanography required |
| Lagrangian Bay of Biscay study https://doi.org/10.1002/edn3.70140 | Persist **5–30 h**; transport **0.3–39.1 km** by site/month/decay/depth; **current speed** dominates transport | Species- and T-specific decay needed |
| Darling, Jerde, Sepulveda 2021 (cited in *eDNA* 2025 methods review) | Rare-species **false-positive inflation** (base-rate fallacy) | Do not over-claim occupancy of rares |

**Operational interpretation rules for this observatory:**

1. Treat a hit as **presence of DNA in a plume**, not “the shark was at this lat/lon.”  
2. Couple positives to a **hydrodynamic / tidal excursion** model; if no model, set spatial class to `UNKNOWN/INSUFFICIENT DATA`.  
3. Do not sample blindly across a thermocline and call it one community (2025 spatial-bound paper: stratification reduces detectability).  
4. Quantitative copies → biomass only with **paired calibration** (tanks, paired trawls) for that taxon and water mass.  
5. Negative ≠ absence (dilution, primer dropout, inhibition).  
6. eRNA may tighten the kernel (**UNPROVEN** at management scale).

---

## Taxa (molecular)

In principle **all cellular life**. In practice:

| Taxon | Today | Limit |
| --- | --- | --- |
| Finfish | 12S metabarcoding / qPCR widely used | Abundance; larval vs adult DNA mixed |
| Sharks/rays | Good when references exist | Rare spp false positives |
| Shellfish / crustaceans / cephalopods | COI/16S mix; reference gaps | Larch/settlement vs adult |
| Mammals / turtles / birds | Possible; contamination from boats/colonies | Ethics of publishing listed-species hits at fine scale |
| Plankton / microbes | Strongest omics use | Function vs name |
| Corals / benthos | Water + sediment | Cryptic complexes |
| Jellies / larvae | Uneven references | Names |
| Plants/algae | Possible | Same as others |

---

## Platforms / integration

| Host | Status | Note |
| --- | --- | --- |
| CTD Niskin / ship underway | Operational science | ASSESS shipboard system (PMEL) |
| Autonomous filter (McLane ROSCI/PPS; AOML cheap autosamplers) | Research→ops | Enables time series without ships |
| Glider / AUV | UNPROVEN–emerging | Contamination, volume |
| Buoy / intake / desal | High leverage | Access agreements |
| Argo | Not standard; **SPECULATIVE** | Energy, sterility |
| Pair with acoustics/cameras | Recommended | ID prior |

Latency: targeted PCR hours–days if a lab is near; metabarcoding typically weeks. In-situ sequencers: **UNPROVEN** operational marine network.

Cost per sample: **UNKNOWN** (chemistry + labor + sequencing vary by an order of magnitude). Information-per-dollar is still **high vs trawling rare taxa**.

---

## Regulatory / privacy / ecology

- Permits for water in MPAs; ABS/Nagoya for non-U.S. samples.  
- Sequence data of listed species at fine space/time: coarsen.  
- Do not build pathogen-enhancement datasets (out of scope).  
- Contamination from ship hulls/ballast: false community.

---

## Forecast / twin role

eDNA time series can support **occupancy nowcasts** (`MODEL-INFERRED`) and, with calibration, relative indices. They should **not** be the sole 24–72 h CPUE product for Chinook or lobster. They **are** among the highest-leverage tools for currently **invisible** diversity (deep rare fishes, invasives, larval presence).
