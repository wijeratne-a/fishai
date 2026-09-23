# Telemetry registry

**Program:** GLOBAL SALTWATER LIFE OBSERVATORY  
**Date / access:** 2026-09-18  
**Modality:** 3.7 tagging/telemetry (+ AniBOS animal-borne oceanography).  
**Ingestion:** none.

---

## Infrastructure (lawful catalogs)

| System | Role | URL | License |
| --- | --- | --- | --- |
| U.S. ATN | DAC for U.S. partner satellite/acoustic/archival tags; asset inventory | https://ioos.noaa.gov/project/atn/ · https://portal.atn.ioos.us/ | **UNKNOWN** per dataset; provider-controlled |
| ATN NCEI archive subset | netCDF locations/profiles | https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc%3AIOOS-ATN-STP | **UNKNOWN** |
| FACT | SE U.S. acoustic array | https://secoora.org/fact/ | **UNKNOWN** |
| PIRAT | Pacific Islands acoustic | https://piratnetwork.org/ | **UNKNOWN** |
| Ocean Tracking Network | Global acoustic cooperative | https://oceantrackingnetwork.org/ | **UNKNOWN** |
| AniBOS | GOOS animal-borne T/S | GOOS / OceanOPS | **UNKNOWN** |
| Argos / Iridium | Satellite comms | commercial | commercial |

ATN QC (ioos_qc / QARTOD): flags implausible speed/location; truncates to deployment dates. **Does not correct representativeness bias** (https://ioos.github.io/ioos-atn-data/quality-control.html).

---

## Tag classes

| Class | Locates how | Typical taxa | Spatial error | Latency | Population inference |
| --- | --- | --- | --- | --- | --- |
| Argos satellite | Doppler / GPS if equipped | Turtles, mammals, sharks, tunas, birds | GPS metres; Argos often km | Hours | Individual ≠ stock |
| Fastloc GPS | Snapshot GPS | Same | Metres | Hours | Same |
| PSAT pop-up archival | Light-based geolocation + pop-up | Tunas, sharks, billfish | Tens–hundreds of km typical | After pop-up | Vertical habitat excellent; XY poor |
| Acoustic coded tags | Receiver detections | Coastal fishes, sharks, crabs, some turtles | Array geometry (m–km) | Download or live buoy | Only where receivers exist |
| PIT | Antenna gates | Salmonids, some others | Gate | When passing | Fishery/river specific |
| Archival recapture | Logged T/P/light | Fishes | After recapture | Months–years | Recapture-biased |
| Accelerometer / camera tags | Behavior/prey | Mammals, birds, some fishes | On-animal | Delayed | Process, not N |
| Animal-borne CTD | Ocean profiles | Elephant seals, some turtles, sharks | Profile at animal | Hours | Oceanography bonus |

Costs per tag: **UNKNOWN**. Acoustic tags often cheaper than PSATs (**ESTIMATE** only — do not budget from this file).

---

## What telemetry can say (honest)

**DIRECT today:** tracks, dive profiles, temperature occupancy of **tagged individuals**; some mortality if pop-off/premature; AniBOS T/S profiles along tracks.

**INFERRED:** habitat preference, migration corridors, vertical refuge (e.g. tuna/salmon in thermocline) — still tagged-subset.

**FORECAST:** short-horizon movement if a validated movement model exists for that population (often **UNKNOWN** skill). Seasonal phenology better than 24 h.

**NEEDS_INFRA:** receiver curtains in new seas; cheaper tags for small fishes; sharing agreements.

**UNPROVEN:** scaling tags to assessment-grade **N**.

**IMPOSSIBLE:** tagging all larvae, plankton, microbes; treating ATN heatmaps as abundance.

---

## Tagged-subset bias (mandatory caveats)

From Sequeira et al. 2021 *Methods Ecol. Evol.* https://doi.org/10.1111/2041-210X.13507 and ATN practice:

1. **Tagging location** overweights waters around capture sites.  
2. **Device type** changes apparent distribution (GPS vs Argos vs light).  
3. **Gaps / duty cycles** oversample surface or daytime.  
4. **Premature failure / detachment** censors long movements and mortality.  
5. **Processing** (state-space vs raw) changes habitat inference.  
6. **Catchability:** only animals that can be handled; healthy-enough; permit-allowed species/sizes.  
7. **Array detection:** acoustic maps are maps of **receivers ∩ tagged animals**, not of the species.

Use telemetry to **parameterize movement and vertical habitat**, then validate against surveys/catch/eDNA. Do not draw a public “all sharks are here” layer from ATN hex bins (the ATN portal itself shows bins of **data availability**, which is easily misread).

---

## Taxa

| Taxon | Telemetry today | Gap |
| --- | --- | --- |
| Finfish | Tunas, billfish, some salmon, some reef fishes (acoustic), cod/others in arrays | Small pelagics, mesopelagic |
| Sharks/rays | Among the best-tagged taxa | Rare deep rays |
| Shellfish | Rare (some acoustic on large bivalves **UNPROVEN** ops) | Essentially none |
| Crustaceans | Acoustic on lobster/crab in some studies | Not stock-wide |
| Cephalopods | Occasional | Poor |
| Marine mammals | Extensive satellite | Still tiny % of individuals; listed-species sensitivity |
| Turtles | Extensive | In-water N |
| Seabirds | Extensive GPS | Small petrels less |
| Plankton–microbes–larvae | Essentially none as individuals | Use other modalities |
| Corals/benthos/plants | N/A movement | Imagery |

---

## Privacy / regulation

- ESA/MMPA/state permits; IACUC.  
- **Do not publish precise tracks of listed species or of animals tagged at fishing hotspots.** Coarsen to ATN-style hexes or coarser; delay.  
- Some datasets remain PI-embargoed; ATN is not a warrant to republish.  
- Dual use: tracks can aid hunting/harassment.

---

## Integration method

1. Ingest only after DUA (future).  
2. Store native tracks `RESTRICTED`/`PRIVATE`.  
3. Derive movement kernels and vertical habitat histograms.  
4. Fuse with satellite/model fields as **covariates the animal actually occupied** (AniBOS).  
5. Teach 24–72 h encounter models for commercial wedges (Chinook/lobster) only if the tagged species/stage matches — often it **does not** (wrong stage problem).

---

## Breakthrough

More of the same satellite tags will not reveal invisible invertebrates. Highest leverage: **acoustic arrays + cheap tags on data-poor coastal fishes/sharks**, and **AniBOS profiles in undersampled latitudes**, not a million tuna PSATs.
