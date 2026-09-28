# Direct observation registry

**Program:** GLOBAL SALTWATER LIFE OBSERVATORY  
**Date / access:** 2026-09-18  
**Scope:** modalities that put an **organism (or a calibrated echo/image of one)** in the record: visual surveys, cameras, nets/grabs, fisheries catch, BRUV/ROV, some acoustics-with-ID, colony counts.  
**Not this folder:** satellite habitat (see `../satellite_capability_matrix.md`), uncalibrated eDNA (see `../eDNA_registry/`), tags (see `../telemetry_registry/`), hydrophones without visual ID (see `../acoustic_registry/`).

No observations were ingested. This is a **method registry**, not a database of sightings.

---

## What “direct” means here

| Qualifies as direct | Does not qualify |
| --- | --- |
| Animal (or colony/mat) in a photo/video/eyewitness protocol | SST, chl, AIS |
| Catch in a net, trap, or hook with taxon ID | CPUE interpreted as N without catchability model |
| Calibrated acoustic backscatter **after** identification haul/camera | Raw EK as “cod map” |
| Quadrat/transect counts, grabs, cores | Habitat suitability |
| *Sargassum* index when the pixel is the algae | Coral DHW |

Output class: `DIRECTLY OBSERVED` or `SURVEY-DERIVED` or `OPERATIONALLY OBSERVED`.

---

## Method families

### 1. Ship and small-boat scientific surveys

- **Trawl / seine / longline / trap surveys** (e.g. NOAA NEFSC BTS, Maine VTS, ICES IBTS): `SURVEY-DERIVED` abundance indices with design. Latency months–years. Gold standard for many stocks; **not** 24–72 h. Rights: agency; microdata often confidential.
- **Ichthyoplankton / plankton nets, CPR:** larvae and plankton **DIRECT** on the line/station. CPR: https://www.cprsurvey.org/ (licence **UNKNOWN**).
- **Visual line-transect** for mammals/seabirds (NOAA ship/aircraft): availability and perception bias must be modeled.
- Cost: ship-time **UNKNOWN**. Information: high per stratum, low globally.

### 2. Optical platforms

| Platform | Taxa | Range | Bias | Scalability |
| --- | --- | --- | --- | --- |
| SCUBA / snorkel transects | Reef fish, corals, benthos, plants | Metres | Depth, vis, observer | Local |
| BRUV / stereo-BRUV | Finfish, sharks, some inverts | Metres + bait plume | Bait attraction | Medium (cheap units) |
| Drop / towed camera | Benthos, habitat, some fish | Metres | Transect placement | Medium |
| ROV | Deep corals, benthos, jellies, fishes | Metres, deep | Light, noise | Low (ship) |
| AUV imaging | Same, repeatable grids | Metres | Navigation, light | Medium if fleet |
| ISIIS / UVP / Zooglider | Plankton, larvae, jellies | Small volume | Patchiness | Low platforms |
| Animal-borne cameras | Prey, behavior | Individual FOV | Tagged subset | Low |
| Fixed cabled cameras | Whatever swims by | Point | Attract/avoid lights | Low sites |
| EM cameras on gear | Catch composition | Haul | Privacy, weather | High if DUA |

ML ID: useful, **not** a species authority without a voucher/expert loop. Domain shift between reefs/oceans is the failure mode.

### 3. Fisheries-dependent (operational)

Logbooks, observers, dockside, EM, factory weights: `OPERATIONALLY OBSERVED` catch. Highest volume biological samples on Earth. **Catch ≠ abundance.** Confidentiality: MSA / national stats. Privacy-preserving contribution: coarsen, k-anonymity, on-vessel indices (catalog §3.10).

### 4. Colony, haulout, nest, stranding

Seabirds, pinnipeds, turtle nests, whale strandings: often the **only** population counts for those taxa. Nesting-beach GPS is **NEVER_PUBLISH** by default.

### 5. Intertidal and aquaculture husbandry counts

Farmers already count oysters/mussels. That is direct for **cultured stock**, not wild populations. Treat as `PRIVATE` partner outcomes (commercial wedge alignment).

### 6. Community / guardian observations

iNaturalist, eBird, Sargassum photo forms (NOAA AOML via SIR page), fisher ecological knowledge. Consent and CARE for Indigenous data. Effort bias.

---

## Taxon cheat sheet (direct methods)

| Taxon | Primary direct methods today | Structural hole |
| --- | --- | --- |
| Finfish | Surveys, catch, BRUV, acoustics+ID | Mesopelagic IDs; 24 h maps |
| Sharks/rays | BRUV, catch, aerial in clear water | Oceanic density |
| Shellfish | Dredge/quadrat, farm counts, intertidal | Subtidal wild census |
| Crustaceans | Traps/trawl, ventless surveys | Global N |
| Cephalopods | Catch, cameras, some jigs | Open ocean |
| Marine mammals | Aerial/ship visual, VHR research, strandings | Global real-time |
| Turtles | Nesting, tags (telemetry folder), bycatch | In-water census |
| Seabirds | Colony counts, at-sea surveys, eBird | Small alcids at sea |
| Plankton | CPR, nets, UVP, color (remote — satellite folder) | Species global |
| Jellyfish | Cameras, nets, strandings | Basin N |
| Corals | Divers/ROV, photo quadrats | Deep / cryptic |
| Benthos | Grabs, cores, imagery | Abyssal time |
| Plants/algae | Quadrats, drones, satellites for canopies | Subcanopy C |
| Microbes | Microscopy, flow cytom, omics (eDNA folder) | Function maps |
| Larvae | Nets, imaging, otoliths | Named larva everywhere |

---

## OBIS as a registry of past directs

https://obis.org/ — **224 million** species observations, **207 thousand** marine species, **7,363** datasets (accessed 2026-09-18). Useful as a **historical occurrence prior**, not as nowcast. Biases: coastal, shallow, common species (OBIS 2019 *Front. Mar. Sci.*: ~50% of WoRMS species have no OBIS record; 56% of OBIS species have &lt;10 records).

Do not download bulk in this iteration. Taxonomy via WoRMS AphiaIDs when a later agent catalogs species.

---

## Integration

Direct observations are the **only legitimate labels** for abundance/occupancy models. Satellites, AIS, and SST may be features. A twin that trains on chl to predict “fish” without survey/catch/camera labels is Category E (forbidden).

---

## Costs

Per-station BRUV **UNKNOWN**. Survey cruise **UNKNOWN**. Marginal cost of keeping EM/observer taxon fields: often already paid — **highest information-per-dollar** if rights exist.

---

## Sensitive locations

No file in this registry should ever list coordinates of listed-species aggregations, turtle nests, or private fishing spots. If a later ingest happens, apply the commercial privacy policy coarsening rules.
