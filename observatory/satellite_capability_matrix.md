# Satellite capability matrix — what spaceborne sensors actually measure

**Program:** GLOBAL SALTWATER LIFE OBSERVATORY  
**Date / URL access:** 2026-09-18  
**Companion:** `observation_modality_catalog.md` §3.1  
**Rule:** a satellite product is `REMOTELY DETECTED` only when the sensor records photons/radar from the target (or a well-posed optical index of that target). Habitat fields used to infer animals are `MODEL-INFERRED`.

No scenes were downloaded. Resolutions and latencies are from agency product pages cited below; where a page did not state a number, the cell is **UNKNOWN**.

---

## 1. Sensor / product matrix (physics and bulk biology)

| Platform / product | Owner | Band / technique | Nominal resolution | Typical revisit / latency | Direct marine-life relevant measurand | Not a measurand | Maturity | License (as findable) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VIIRS SNPP / NOAA-20 / NOAA-21 ocean color (MSL12) | NOAA CoastWatch/STAR | Visible nLw, chl-a, Kd(490), Kd(PAR), true color | L2 **750 m**; global L3 **4 km**; sector L3 750 m | Daily polar; NRT and science-quality | Surface ocean color, chl-a, diffuse attenuation | Fish, whales, most algae mats at sub-pixel | Operational | U.S. Gov work typical; **dataset TOS UNKNOWN** |
| VIIRS ACSPO SST L2P/L3U | NOAA | IR SST (GHRSST GDS2) | Native VIIRS (~750 m class); CoastWatch L3 750 m / 4 km | ~10-min granules; ~144/day/sat | Skin SST | Bulk 10 m T; bottom T; animals | Operational | same |
| NOAA geo-polar blended SST | NOAA NESDIS | Geo IR + LEO IR | **0.05° (~5 km)** daily L4 | Daily | Analyzed skin SST (night, day/night, diurnal flavors) | Animals | Operational | same |
| Sentinel-3 OLCI (via CMEMS GlobColour) | ESA/EUMETSAT → CMEMS | Ocean colour, PFTs, SPM, ZSD, KD490, BBP | **300 m** OLCI datasets and **4 km** multi-sensor | Daily NRT (product page: update ~22:00) | Chl, some phytoplankton functional types, transparency | Individual organisms | Operational | CMEMS licence **UNKNOWN** for commercial resale |
| Copernicus GlobColour L3/L4 (OCEANCOLOUR_GLO_BGC_*) | CMEMS / ACRI-ST | Multi (SeaWiFS–OLCI–VIIRS) | 4 km; OLCI 300 m | Daily L3; L4 monthly/gap-free | Plankton, optics, PP monthly | Fish N | Operational | same |
| MODIS-Aqua heritage color/SST | NASA | Visible/IR | ~1 km / 4 km products | Daily, aging mission | Climate continuity | — | Operational/clim | NASA Earthdata TOS **UNKNOWN** |
| PACE OCI | NASA | Hyperspectral ocean color | L3 mapped **4 km** / 0.1° (literature) | 1–2 day class polar | Chl; **MOANA** *Prochlorococcus*, *Synechococcus*, picoeukaryotes (cells mL⁻¹, provisional) | Fish; most zooplankton | Provisional science (chl/MOANA labeled provisional in 2024–25 literature) | NASA Earthdata |
| SWOT | NASA/CNES | Ka-band radar interferometry SSH | Fine along-swath SSH (product-spec **UNKNOWN** here; much finer than nadir altimetry) | Non-daily global in the VIIRS sense | Sea-surface height, eddies | Animals; chl (combine with PACE) | Science mission | NASA/CNES |
| Conventional altimetry (Jason-class, Sentinel-3 SRAL, etc.) | NOAA/EUMETSAT/CMEMS | Radar SSH | ~km along-track | Days | SSH, geostrophic currents | Biology | Operational | mixed |
| Scatterometers (ASCAT, etc.) | EUMETSAT/NOAA | Ku/C-band winds | ~12.5–25 km | Daily | Surface wind stress | Animals | Operational | mixed |
| Sentinel-1 / RCM / other C-band SAR | ESA / CSA | SAR roughness | ~5–20 m class (mode-dependent **UNKNOWN** exact here) | Days, weather-independent | Ships, ice, oil, some wind/waves, some *Sargassum*/biogenic slicks **UNPROVEN** as routine biology | Subsurface life | Operational (ships/ice) | Copernicus/CSA |
| Sentinel-2 MSI | ESA | VNIR 10 m; red-edge | **10 m** (selected bands) | ~5 day (2-sat) | Shallow benthos, seagrass, kelp, turbidity, some blooms | Individual fish; deep reef | Operational mapping | Copernicus |
| Landsat 8/9 OLI | USGS/NASA | VNIR **30 m** | 16-day (together more) | Seagrass/reef/kelp, colonies, glacial/ice penguin stains | Animals at sea | Operational | USGS |
| WorldView-2/3 and peers (Maxar class) | Commercial | Pan **~0.3 m** (WV-3); MS ~1.2 m; 8-band coastal | Tasked | Surface whales, sharks/rays in clear shallows, haulouts, fine benthos | Global daily census; turbid/deep | Research / tasked | **Commercial; UNKNOWN price** |
| ICESat-2 ATLAS | NASA | Green photon-counting lidar | Photon footprints | Repeat tracks | Ice, some bathymetry/canopy, experimental ocean optics | Fish schools as inventory | Science | NASA |
| SMAP / SMOS SSS | NASA/ESA | L-band microwave | ~40–50 km class | Days | Sea-surface salinity | Biology | Operational science | mixed |
| NOAA CRW CoralTemp / DHW 5 km v3.1 | NOAA | SST analysis → heat-stress metrics | **5 km** daily | Daily NRT | **Proxy** bleaching heat stress (HotSpot, DHW, Alert Area) | Live coral cover, species | Operational | U.S. Gov |
| USF SaWS / NOAA SIR v1.5 | USF + NOAA AOML/CoastWatch | AFAI / floating algae index from ocean-color class sensors | SaWS maps **1–10 km** (USF); SIR coastal risk categories | Daily SIR | Pelagic *Sargassum* mats; inundation **risk** | Nearshore mixed pixels; other macroalgae always | SaWS used operationally by stakeholders; SIR **experimental** per NOAA page | check each product |
| VIIRS/OLCI HAB indices (various NCCOS/CoastWatch) | NOAA | Color/FLH/CI | 300 m–1 km class | Daily cloud-limited | Bloom **proxies** | Toxin, species always | Mixed operational/experimental | U.S. Gov |

---

## 2. Animal / habitat detection matrix (honest)

Legend: **Y** demonstrated operationally or routinely; **R** research/demonstrated, not global ops; **P** proxy only; **N** not feasible with that sensor class; **U** UNKNOWN.

| Target | VIIRS/OLCI color | PACE hyperspectral | S2/Landsat 10–30 m | VHR ≤2 m | SAR | SST L4 | Altimetry/SWOT | CRW DHW |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Chl-a / bloom extent | Y | Y | Y coastal | R | N | N | P eddy context | N |
| Picoplankton groups | N/limited PFT | R/Y MOANA | N | N | N | N | N | N |
| *Sargassum* mats | Y/R SaWS | U | R nearshore | R | U | N | P transport | N |
| HAB toxin | N | N | N | N | N | N | N | N |
| Kelp / seagrass canopy | R/N (too coarse often) | U | Y | Y | R (some kelp SAR) | N | N | N |
| Shallow reef habitat | N | U | Y | Y | N | N | N | P heat only |
| Coral polyps / % bleached live | N | U | N | N/R | N | N | N | P |
| Baleen whale surfacing | N | N | N | R | N | P habitat | P | N |
| Dolphins / porpoises | N | N | N | N/R (size) | N | P | N | N |
| Pinniped haulout | N | N | R | Y/R | R ice | N | N | N |
| Whale shark / basking shark | N | N | N | R clear shallow | N | P | N | N |
| Typical reef shark | N | N | N | N | N | P | N | N |
| Tuna / herring school ID | N | N | N | N | N | P | P | N |
| Turtle in water | N | N | N | N/R anecdotal | N | P | N | N |
| Seabird colony | N | N | Y/R | Y | N | N | N | N |
| Seabird at sea | N | N | N | N/R | N | P | N | N |
| Jellyfish swarm | N | N | N/R | R | N | N | N | N |
| Oyster reef structure | N | N | R intertidal | R | U | P stress | N | N |
| Lobster / crab | N | N | N | N | N | **N** (need bottom T) | N | N |
| Squid | N | N | N | N | N | P | N | N |
| Larvae | N | N | N | N | N | P | P | N |
| Microbes (cells) | P pigment | R groups | N | N | N | N | N | N |

---

## 3. Optical depth and sea-state gates (physical)

| Gate | Effect | Consequence |
| --- | --- | --- |
| \(K_d\) / Jerlov type | Light e-folding metres to tens of metres | Bottom mapping and animal imaging confined to clear shallow water; VIIRS Kd(490) is the right **mask**, not a fish layer |
| Clouds / ice | No VNIR/IR | Use microwave SST/SSH/SAR; biology waits or uses in situ |
| Sun glint / waves / whitecaps | False targets, missed whales | VHR mammal papers require calm, low-glint windows (DFO 2022) |
| CDOM / sediment | Coastal color invalid as chl | Do not infer “fish food” in river plumes from chl algorithms blindly |
| Skin vs bulk SST | IR sees micrometres | Night analyses preferred for coral/habitat; still **not** bottom T |
| Pixel mixture | 10–4000 m pixels | School of fish is a spectral soup |

Depth penetration literature cited in habitat-mapping reviews: **&lt;1 m** very turbid to **&gt;30 m** clearest water (O’Neill/Nagel 2022 and references therein).

---

## 4. Indirect satellite paths into “invisible” organisms

Do not implement as “satellite sees fish.” Implement as **cue → in situ modality**.

| Satellite cue | Cue type | Follow-on modality | Organism class | Output class if fused correctly |
| --- | --- | --- | --- | --- |
| SST front / chl edge / SWOT eddy | Physics/prey proxy | Glider EK + eDNA + camera | Pelagic fish, plankton, some sharks | `MODEL-INFERRED` habitat + `SURVEY-DERIVED` if glider samples |
| PACE bloom / PFT shift | Bulk microbes | BGC-Argo, CPR, nets | Plankton, microbes, larval food | `REMOTELY DETECTED` microbes + in situ validation |
| SaWS *Sargassum* | Floating algae | Ship/aerial/community | Algae; associated fish **not counted** | `REMOTELY DETECTED` algae |
| CRW DHW | Heat stress | Divers/ROV/eDNA | Corals | `FORECAST`/`MODEL-INFERRED` stress; imagery = `DIRECTLY OBSERVED` |
| VHR whale candidate | Image | Aerial/PAM confirmation | Baleen | `REMOTELY DETECTED` if confirmed |
| SAR vessel cluster | Effort | Must **not** convert to fish | Exploited stocks | `OPERATIONALLY OBSERVED` effort only |
| SSH / particle trajectory | Transport | eDNA interpretation, larval models | eDNA plumes, larvae (water, not larva unless coupled) | `MODEL-INFERRED` |
| Geo SST + tides (model) | Intertidal heat | Farm sensors | Shellfish **stress** | `MODEL-INFERRED` stress, not abundance |

---

## 5. Latency, coverage, cost (order of magnitude)

| Class | Coverage | Latency | Cost to observatory | Label |
| --- | --- | --- | --- | --- |
| NOAA/CMEMS L3/L4 SST & OC | Global ice-free, cloud gaps | Hours–2 days NRT | $0 marginal portal access | CITED free portals; **commercial licence UNKNOWN** |
| CRW 5 km | Global reefs/SST field | Daily | $0 portal | CITED |
| SaWS / SIR | Tropical Atlantic / Caribbean / Gulf | Daily | $0 viewer | CITED pages; SIR experimental |
| S2/Landsat | Global land+coast | Days | $0 | CITED |
| PACE/SWOT | Global science | Days (processing) | $0 Earthdata | CITED missions |
| VHR tasking | Tiny swaths | Days if tasked | **UNKNOWN** commercial | UNKNOWN |
| SAR | Global all-weather surface | Days | Copernicus free; other **UNKNOWN** | mixed |

---

## 6. Regulatory, privacy, ecological

- VHR and aerial-equivalent space photos can disclose **listed-species aggregations, nesting, haulouts, and vessels**. Public observatory layers: coarsen, delay, or withhold.
- Do not fuse public AIS with SAR to publish a named highliner’s fishing graph.
- Coral DHW is not a harvest or restoration authorization.
- Sargassum SIR is **risk**, experimental, not a navigation product.
- Export/ITAR on some commercial imagery: **UNKNOWN** per provider — do not scrape.

---

## 7. Breakthrough vs dead ends

**Breakthrough-adjacent (keep):** PACE community composition + BGC-Argo vertical; SWOT submesoscale + biology; operational *Sargassum*/HAB; S2 habitat change detection; limited VHR+ML for whales in **survey blocks** with availability-bias models.

**Dead ends (do not fund as census):** VIIRS “fish maps”; SST-as-lobster; AIS-as-abundance; Sentinel-2 tuna ID; global real-time shark VHR.

---

## Sources (accessed 2026-09-18)

- https://coastwatch.noaa.gov/cwn/instruments/viirs.html  
- https://coastwatch.noaa.gov/cwn/product-families/sea-surface-temperature.html  
- https://coastwatch.noaa.gov/cwn/products/noaa-msl12-ocean-color-science-quality-viirs-snpp.html  
- https://coastwatch.star.nesdis.noaa.gov/cwn/products/noaa-msl12-ocean-color-near-real-time-viirs-single-sensor-snpp-and-noaa-20.html  
- https://data.marine.copernicus.eu/product/OCEANCOLOUR_GLO_BGC_L3_NRT_009_101/description  
- https://data.marine.copernicus.eu/product/OCEANCOLOUR_GLO_BGC_L4_NRT_009_102/services  
- https://documentation.marine.copernicus.eu/PUM/CMEMS-OC-PUM.pdf  
- https://coralreefwatch.noaa.gov/product/5km/  
- https://cwcgom.aoml.noaa.gov/SIR/  
- https://optics.marine.usf.edu/projects/saws.html  
- https://www.earthdata.nasa.gov/data/catalog/ob-cloud-pace-oci-l4m-moana-3.1  
- https://www.nasa.gov/missions/pace/nasas-pace-us-european-swot-satellites-offer-combined-look-at-ocean/  
- https://doi.org/10.3390/jmse11030595  
- https://publications.gc.ca/collections/collection_2022/mpo-dfo/Fs97-4-3248-eng.pdf  
- https://doi.org/10.3389/fmars.2019.00135  
- https://www.mdpi.com/2072-4292/14/5/1254  
