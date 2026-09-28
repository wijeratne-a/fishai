# Sensor network catalog

**Program:** GLOBAL SALTWATER LIFE OBSERVATORY  
**Date / access:** 2026-09-18  
**Ingestion:** none.  
**Machine table:** `networks.csv` (this folder).

This catalog lists **existing observing networks** that can host or already host life-relevant sensors. It is not an asset-level inventory (those change weekly). Exact platform counts not on an official dashboard are **UNKNOWN**.

Biology is sparse on physics networks. The observatory value is often **adding eDNA / PAM / optics / acoustics onto paid power and comms**, not building new hulls.

---

## Network classes

| Class | What it measures today | Life relevance | Scale |
| --- | --- | --- | --- |
| Profiling floats (Argo / BGC / Deep) | T, S, P; BGC subset | Plankton/microbe **proxies**; 3D habitat | ~4000 active core; BGC below 1000-float design |
| Gliders (OceanGliders / IOOS DAC) | T, S, O2, optics, sometimes acoustics/PAM | Directed sections; HAB; fish habitat | Regional, campaign |
| Moored buoys (NDBC, OceanSITES, DBCP, IOOS RAs) | Metocean, some bio-optics | Catchability, stress, PAM if equipped | Points |
| HF radar | Surface current/waves | Transport of eDNA, larvae **as water**, search-and-rescue — **not animals** | U.S. coasts + growing global |
| Tide gauges (CO-OPS, GLOSS) | Sea level | Intertidal emersion (shellfish stress) | Coasts |
| Cabled observatories | High-bandwidth seafloor | Cameras, PAM, ADCP | Few sites |
| Animal telemetry DACs (ATN, OTN, AniBOS) | Tracks + some T/S | Direct animals (biased subset) | Project union |
| PAM archives (NCEI, ONMS Sound) | Sound | Vocal taxa | Point time series |
| Biodiversity aggregators (OBIS, GBIF, MBON) | Occurrences | Historical/survey `SURVEY-DERIVED` | Global biased |
| Ships (GO-SHIP, SOOP, CPR, fisheries) | Discrete / routes | Gold-standard BGC; plankton; catch | Lines |

---

## Flagship networks (official URLs)

### Global / UN

| ID | Name | URL | Notes |
| --- | --- | --- | --- |
| GOOS | Global Ocean Observing System | https://goosocean.org/ | Coordinates Argo, OceanSITES, OceanGliders, DBCP, AniBOS, HF radar, etc. |
| Argo | Profiling floats | https://argo.ucsd.edu/about/status/ | ~4000 active; 5–600 floats/yr to maintain (UCSD). Euro-Argo dashboard listed **4334 active** (2026-08-09 snapshot in search). |
| BGC-Argo | BGC floats | https://argo.ucsd.edu/expansion/biogeochemical-argo-mission/ | Design 1000 floats; **CITED** ~$100k lifetime, ~$25M/yr. Variables: pH, O2, NO3, chl, particles, irradiance. |
| OceanSITES | Open-ocean time series | https://www.ocean-ops.org/oceansites/ | Full-depth multidisciplinary **points**. |
| OceanGliders | Glider network | via GOOS / OceanOPS | Emerging/operational; data FAIR push. |
| AniBOS | Animal-borne ocean sensors | GOOS network | Animals as profilers (T/S). |
| GLOSS | Sea level | GLOSS / IOC | Tides/sea level. |
| OBIS | Biodiversity occurrences | https://obis.org/ | **224M** observations, **207K** species, **7,363** datasets (page access 2026-09-18). Not real-time tracking. |
| SMART cables JTF | ITU/WMO/UNESCO-IOC | https://www.itu.int/en/ITU-T/climatechange/task-force-sc/Pages/default.aspx | Future T/P/accel on repeaters; DAS optional. |

### U.S. IOOS family (high reuse value)

| ID | Name | URL | Life-relevant payload |
| --- | --- | --- | --- |
| IOOS | U.S. Integrated Ocean Observing System | https://ioos.noaa.gov/ | 11 Regional Associations; sensor map |
| IOOS data | Access / DACs | https://ioos.noaa.gov/data/access-ioos-data/ | Buoys, HF radar, gliders |
| ATN | Animal Telemetry Network | https://ioos.noaa.gov/project/atn/ · https://portal.atn.ioos.us/ | Tags; FACT, PIRAT acoustic nets |
| Glider DAC | IOOS gliders | ioos.us / glider DAC | T/S/O2/optics |
| HF radar DAC | Surface currents | IOOS; 500 m–6 km | Transport only |
| MBON | Marine Biodiversity Observation Network | IOOS marine life | Biodiversity time series (not global) |
| NANOOS | Pacific NW RA | https://www.nanoos.org/ | Shellfish grower sensors — **farm PRIVATE** if partner-owned |
| NERACOOS | Northeast RA | https://www.neracoos.org/ | GOM bottom T context (lobster **covariate**) |
| NDBC | National Data Buoy Center | https://www.ndbc.noaa.gov/ | Metocean |
| CO-OPS | Tides & currents | https://tidesandcurrents.noaa.gov/ | Emersion timing |
| NOAA CoastWatch | Satellite | https://coastwatch.noaa.gov/ | SST/OC regional |
| NCEI PAM | Passive acoustic archive | https://www.ncei.noaa.gov/products/passive-acoustic-data | Hydrophones |
| ONMS Sound | Sanctuary hydrophones | https://sanctuaries.noaa.gov/science/monitoring/sound/ | 10+ sanctuaries |
| NOAA Omics | Molecular | https://oceanexplorer.noaa.gov/noaa-omics/ | eDNA strategy |
| Coral Reef Watch | Heat stress | https://coralreefwatch.noaa.gov/product/5km/ | Proxy |

### Europe / other (catalog, no ingest)

| ID | Name | URL | Notes |
| --- | --- | --- | --- |
| CMEMS | Copernicus Marine Service | https://marine.copernicus.eu/ | Models + satellite + in situ products; licence **UNKNOWN** for resale |
| EMODnet | European marine data | emodnet.ec.europa.eu | Biology/physics lots; licence **UNKNOWN** |
| OTN | Ocean Tracking Network | oceantrackingnetwork.org | Acoustic telemetry (Canada-led global) |
| ICES | Fisheries science | ices.dk | Acoustic surveys, DATRAS — assessment-grade, not 24 h |

---

## Adding biology to physics networks (integration method)

| Host | Feasible add-on | Maturity | Constraint |
| --- | --- | --- | --- |
| Research / fishing vessels | EK calibration share, underway eDNA, CPR analog, hull T | Proven in pockets | Privacy, calibration, crew time |
| IOOS buoys | Fluorometer, PAM, eDNA autosampler (AOML-class) | Mix of ops/research | Power, fouling, vandalism |
| Gliders | EK80, camera, eDNA filter | Research→ops | Endurance, noise, permits |
| Argo | Already BGC optics; eDNA **not** standard | SPECULATIVE/UNPROVEN for DNA | Volume, contamination, energy |
| Telecom cable | DAS interrogator; SMART T/P/accel | DAS research; SMART early | Owner agreement |
| Desal / power plant intakes | eDNA time series | Proven locally | Access agreements |
| Aquaculture leases | DO, T, cameras | Operational private | **PRIVATE**; not wild census |

---

## Cost / scale (do not invent)

| Item | Value | Label |
| --- | --- | --- |
| BGC-Argo lifetime / global year | ~$100k / ~$25M | CITED Argo BGC page |
| Core Argo replacements | 5–600 floats/yr | CITED UCSD status |
| New NDBC-class mooring | — | **UNKNOWN** |
| Glider month | — | **UNKNOWN** |
| Dark-fiber DAS year | — | **UNKNOWN** |

---

## Regulatory / privacy

- EEZ research clearances for gliders/AUVs.
- VMS/AIS: see modality 3.10; not a sensor of fish.
- Farm and fishing sensors: partner DUA; coarsen public.
- OBIS occurrences of listed species: follow aggregator and national sensitive-species policies; do not republish nests/haulouts at native resolution.

---

## Gaps (honest)

There is **no global biological sensor grid**. Physics (Argo, satellites, NDBC) is the only near-global layer. Life observations are **surveys, fisheries, tags, PAM points, and coastal RAs**. Filling the gap is eDNA + opportunistic acoustics + DAS + directed AUVs, not a second Argo of cameras.
