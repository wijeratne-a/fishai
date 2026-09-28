# Acoustic registry (active + passive + DAS)

**Program:** GLOBAL SALTWATER LIFE OBSERVATORY  
**Date / access:** 2026-09-18  
**Modalities:** 3.4 active acoustics · 3.5 passive acoustics · 3.11 DAS/DTS  
**Ingestion:** none. No raw audio or EK files.

---

## A. Active acoustics / sonar

### What is measured

Volume backscattering (\(s_v\)), area backscattering (NASC), target strength (TS), and (broadband) frequency response. Conversion to biomass requires **TS and species composition**.

### Operational use today

- ICES/NOAA/DFO **pelagic assessment surveys** (typically **38 kHz** plus 18/70/120/200 kHz).  
- Identification still relies on **trawl/camera** (ICES survey protocols).  
- Broadband EK80 widely installed; **species ID not solved** for similar swimbladder fishes.

### Species classification limits (do not overclaim)

| Separable (often) | Not separable (often) | Source |
| --- | --- | --- |
| Gas-bearing fish vs mackerel-like (no bladder) vs zooplankton vs resonant siphonophores | Herring vs Norway pout; capelin vs polar cod; many gadoids vs each other | Korneliussen et al. https://doi.org/10.1093/icesjms/fsp119 ; ICES CRR 344 https://doi.org/10.17895/ices.pub.4567 |
| Some school-morphology + geography + season priors | Mixed-species layers | ICES CRR 344 |
| Near-resonant information from broadband | Walleye pollock vs other swimbladder fishes in 15–150 kHz | Jones et al. NOAA https://repository.library.noaa.gov/view/noaa/52568 |

**Bottom line:** acoustics give **excellent density of scatterers** and **weak Linnaean names**. Pair with cameras, eDNA, or nets.

### Blind zones and physics

- Near-surface bubble/turbulence layer; near-bottom dead zone (misses flatfish/crabs).  
- Frequency ↑ → resolution ↑ and range ↓ (absorption).  
- Vessel avoidance; airguns/mapping sonars are a different (MMPA) regime.

### Opportunistic fleet acoustics

Fishing-vessel EK is the **scalable** path (information-per-dollar). Requires calibration, clock sync, privacy aggregation (no public fish-finder maps).

Cost of scientific echosounder: **UNKNOWN**. Marginal cost if already installed: low.

---

## B. Passive acoustics (hydrophones)

### Official U.S. holdings

| Holding | URL | Notes |
| --- | --- | --- |
| NCEI Passive Acoustic Archive | https://www.ncei.noaa.gov/products/passive-acoustic-data | Tethys-aligned; 2017+ stewardship |
| ONMS Sound | https://sanctuaries.noaa.gov/science/monitoring/sound/ | Coordinated sanctuary network (East, Gulf, West, Pacific Islands) |
| SanctSound 2018–2022 | ONMS + NCEI | 30 sites, 7 sanctuaries + 1 monument |

### What PAM can say

| Taxon / source | Direct? | Density? |
| --- | --- | --- |
| Baleen songs/calls | Yes if cataloged | Only with cue rates (often UNKNOWN) |
| Odontocete clicks/whistles | Yes, range often short for HF | Same |
| Soniferous fishes | Choruses yes; species sometimes | Rarely biomass |
| Snapping shrimp | Habitat indicator | Not “shrimp N” |
| Ships, wind, ice, quakes | Yes | Noise EOV |
| Sharks, turtles, most inverts, plankton | No | — |

Silence ≠ absence. Real-time whale products have **ship-strike benefit vs harassment/poaching risk** — coarsen listed species (especially NARW).

Latency: cabled/glider real-time; many archival months.

---

## C. DAS / DTS / SMART cables

| Item | Status | Citation |
| --- | --- | --- |
| Baleen whale DAS | Demonstrated Arctic/Australia | Bouffaut et al. 2022 https://www.frontiersin.org/articles/10.3389/fmars.2022.901348 ; Rørstadbotnen et al. 2023 https://www.frontiersin.org/articles/10.3389/fmars.2023.1130898 |
| Channels / gauge | 4.08 m spacing, ~30k channels on 120 km example | Bouffaut 2022 |
| Multi-whale tracking | 8 fin whales; ~100 m vs airgun; ~800 km² | Rørstadbotnen 2023 |
| Useful band vs hydrophone | Often **≲100–150 Hz**; missed higher calls | JASA 2025 comparison; Kiel MSc 2024 |
| Sensitivity | Lower / noisier than ceramic hydrophone; coupling/armor matter | MTS J. 2025 review https://doi.org/10.4031/mtsj.59.1.12 |
| Data rate | ~1 Gb/s class | same review |
| SMART repeaters | T, P, 3-axis accel; DFOS optional at landing | ITU-T G.9730.2 (08/2024); Howe et al. 2019 https://doi.org/10.3389/fmars.2019.00424 |
| DTS oceanography | Emerging | **UNKNOWN** operational life products |
| Cost | Interrogator + fiber access | **UNKNOWN** |
| Access | Cable-owner NDAs, critical infrastructure | Regulatory heavy |

DAS is **not** fisheries sonar and **not** a crab census. It is a potential **global-along-cable PAM** for low-frequency whales and ships.

---

## D. Taxa × acoustic family

| Taxon | Active | Passive | DAS |
| --- | --- | --- | --- |
| Finfish | DIRECT backscatter; ID limited | Some choruses | UNPROVEN LF fish |
| Sharks/rays | Weak TS; not survey standard | Generally silent | N |
| Shellfish | Seabed classification maybe habitat | N | N |
| Crustaceans | Poor (bottom dead zone); krill/zooplankton yes | Snapping shrimp | N |
| Cephalopods | Some aggregations | N | N |
| Marine mammals | Avoid / not target | DIRECT | DIRECT baleen LF |
| Turtles | N | N | N |
| Seabirds | N | N | N |
| Plankton | Zooplankton multifrequency | N | N |
| Jellyfish | Weak / mixed | N | N |
| Corals / benthos | MBES habitat not species | snapping shrimp habitat | N |
| Plants | N | N | N |
| Microbes | N | N | N |
| Larvae | N as named larvae | N | N |

---

## E. Integration

1. Active: **biomass constraint** with ID prior from trawl/camera/eDNA.  
2. Passive/DAS: **occupancy and noise**; cue slow platforms.  
3. Never publish fine-scale listed-whale nowcasts in a public API.  
4. Opportunistic EK: privacy-preserving indices into the twin as `OPERATIONALLY OBSERVED` scatter, not species.

---

## F. Breakthrough vs limit

**Breakthrough:** DAS on dark fiber; calibrated fishing-vessel broadband + cameras; glider PAM in chokepoints.  
**Hard limit:** overlapping TS spectra; non-vocal life; absorption vs range; cable routes ≠ ocean volume.
