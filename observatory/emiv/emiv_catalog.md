# EMIV catalog (human-readable) — set v0.1

**Registry:** [`emiv_registry.csv`](emiv_registry.csv) (`v0.1-draft`, **84** rows)  
**Date:** 2026-09-18  
**OPERATIONAL count:** 0  
**Read with:** [`README.md`](README.md) (versioning and official EOV/EBV/IOOS URLs), [`acceptance_gate.md`](acceptance_gate.md)

This catalog groups the registry **A–F**. It does not repeat every CSV field. Definitions for category C include **claim-class**. Privacy: do not publish native-grain rows marked NEVER_PUBLISH in the registry or in [`../sensitive_location_policy.md`](../sensitive_location_policy.md).

Status key: `W1_CORE` | `W1_PROXY` | `CANDIDATE` | `DEFERRED` | `REJECTED_AS_ABUNDANCE_PROXY` · validation `UNVALIDATED` | `PROTOCOL_ONLY` | `LITERATURE` | `OPERATIONAL`.

---

## A — PHYSICAL (19)

Temperature is split on purpose: **air**, **tissue/bag thermistor**, **in situ bulk water**, **depth-resolved**, **bottom**, and **satellite skin/foundation SST** are different measurands. Incoming **solar / insolation during emersion** is a radiative driver, not chlorophyll. Collapsing these is how oyster and lobster products fail.

| ID | Name | Unit | Use | Validation | Standards (short) |
| --- | --- | --- | --- | --- | --- |
| EMIV-PHY-ATEMP-001 | Near-surface air temperature | degC | **W1_CORE** | LITERATURE | Superset; GCOS air T ECV (not a GOOS EOV) |
| EMIV-PHY-WTEMP-001 | Near-surface bulk water temperature | degC | **W1_CORE** | LITERATURE | GOOS SST/subsurface T (bulk); IOOS Temperature |
| EMIV-PHY-WTEMP-002 | Depth-resolved water temperature | degC by depth | CANDIDATE | LITERATURE | GOOS Subsurface Temperature; Argo |
| EMIV-PHY-WTEMP-003 | Bottom / seafloor temperature | degC | CANDIDATE | LITERATURE | GOOS Subsurface T (near-bottom); eMOLT |
| EMIV-PHY-SST-001 | Satellite SST (skin or foundation) | degC | **W1_PROXY** | PROTOCOL_ONLY | GOOS Sea Surface Temperature; GHRSST |
| EMIV-PHY-SALIN-001 | Practical salinity | 1 (PSS-78) | **W1_CORE** | LITERATURE | GOOS SSS/subsurface S; IOOS Salinity |
| EMIV-PHY-CURR-001 | Surface currents | m s-1 | CANDIDATE | PROTOCOL_ONLY | GOOS Surface Currents; IOOS Currents |
| EMIV-PHY-CURR-002 | Subsurface currents | m s-1 by depth | CANDIDATE | PROTOCOL_ONLY | GOOS Subsurface Currents |
| EMIV-PHY-WAVE-001 | Sea state / waves | m, s, deg | **W1_CORE** | LITERATURE | GOOS Sea State; IOOS Surface waves |
| EMIV-PHY-WIND-001 | Surface wind | m s-1, deg | **W1_CORE** | PROTOCOL_ONLY | IOOS Wind; GCOS (superset vs GOOS ocean EOVs) |
| EMIV-PHY-TIDE-001 | Tide stage / water level | m vs datum | **W1_CORE** | PROTOCOL_ONLY | GOOS SSH (coastal); IOOS Sea level; CO-OPS |
| EMIV-PHY-EMERS-001 | Intertidal emersion | h + elevation | **W1_CORE** | LITERATURE | Superset: derived from sea-level EOV + culture elevation |
| EMIV-PHY-SOLAR-001 | Incoming solar / insolation during emersion | W m-2; geometry flag | **W1_CORE** | LITERATURE | GCOS surface radiation / incoming shortwave (not a GOOS EOV); **not chlorophyll** |
| EMIV-PHY-TISST-001 | Tissue or bag/bed thermistor temperature | degC | CANDIDATE (W1_CORE when partner sensor exists) | LITERATURE | Superset: no organism/gear-T EOV; not GHRSST |
| EMIV-PHY-SEALV-001 | Coastal sea level / surge | m vs datum | CANDIDATE | PROTOCOL_ONLY | GOOS Sea Surface Height; GLOSS |
| EMIV-PHY-STRAT-001 | Water-column structure | m / density | CANDIDATE | LITERATURE | Derived from GOOS subsurface T/S |
| EMIV-PHY-BATHY-001 | Bathymetry | m | CANDIDATE | PROTOCOL_ONLY | IOOS Bathymetry; GEBCO **not navigation** |
| EMIV-PHY-SUBST-001 | Substrate / bottom character | class | CANDIDATE | LITERATURE | IOOS Bottom character |
| EMIV-PHY-LIGHT-001 | Underwater light / PAR / Kd | PAR; m-1 | CANDIDATE | PROTOCOL_ONLY | GOOS Ocean Colour (optical); IOOS Optical properties |

**Notes**

- **SST is a physical EMIV and a W1 proxy with mismatch.** It is not air temperature, not tissue/bag T, not bottom T, not fish.
- **Incoming solar** (`EMIV-PHY-SOLAR-001`) is midday sun / insolation during emersion. It is **not** chlorophyll and **not** underwater PAR (`EMIV-PHY-LIGHT-001`).
- **Tissue/bag T** (`EMIV-PHY-TISST-001`) is the organism or gear thermal state. Distinct from SST (proxy) and bulk water T. CANDIDATE until a partner thermistor exists; then W1_CORE.
- Moon phase is **not** an EMIV; tides already carry the 72 h information.
- Ice and ocean surface heat flux are IOOS/GOOS physics that are **out of this 84-row cut** (not required for W1; add later if a polar/heat-flux decision appears).

---

## B — BGC (12)

| ID | Name | Unit | Use | Validation | Standards (short) |
| --- | --- | --- | --- | --- | --- |
| EMIV-BGC-DOXY-001 | Dissolved oxygen | umol kg-1 or mg L-1 | **W1_CORE** | LITERATURE | GOOS Oxygen; IOOS Dissolved oxygen |
| EMIV-BGC-PH-001 | pH (scale named) | 1 | CANDIDATE | LITERATURE | GOOS Inorganic Carbon related; IOOS Acidity |
| EMIV-BGC-NUTR-001 | Dissolved nutrients N/P/Si | umol L-1 or kg-1 | CANDIDATE | LITERATURE | GOOS Nutrients; IOOS Dissolved nutrients |
| EMIV-BGC-CHL-001 | Chlorophyll-a | mg m-3 | CANDIDATE | PROTOCOL_ONLY | GOOS Ocean Colour / phytoplankton; IOOS Ocean color |
| EMIV-BGC-PROD-001 | Primary productivity | mg C m-2 d-1 | CANDIDATE | UNVALIDATED | GEO BON EBV Primary productivity |
| EMIV-BGC-TURB-001 | Turbidity / TSS | NTU; mg L-1 | CANDIDATE | LITERATURE | IOOS Total suspended matter |
| EMIV-BGC-CARB-001 | Inorganic carbon (DIC, TA, pCO2) | umol kg-1; uatm | CANDIDATE | PROTOCOL_ONLY | GOOS Inorganic Carbon; IOOS pCO2 |
| EMIV-BGC-OMEGA-001 | Aragonite saturation Ω | 1 | CANDIDATE | LITERATURE | Derived from Inorganic Carbon EOV |
| EMIV-BGC-POLL-001 | Chemical pollutants | analyte-specific | CANDIDATE | UNVALIDATED | IOOS Contaminants |
| EMIV-BGC-RUNOFF-001 | Freshwater runoff / delivery | m3 s-1; mm | **W1_PROXY** | LITERATURE | IOOS Stream flow (land hydrology superset) |
| EMIV-BGC-FECAL-001 | Fecal indicator bacteria | MPN or CFU / 100 mL | CANDIDATE | PROTOCOL_ONLY | IOOS Pathogens (indicator); NSSP labs |
| EMIV-BGC-CDOM-001 | CDOM | m-1 / FDOM | CANDIDATE | PROTOCOL_ONLY | IOOS CDOM |

**Notes**

- **No satellite DO.** Missing oxygen stays UNKNOWN.
- **pH/Ω are larval/OA**, not W1 adult 72 h headlines.
- **Fecal indicators are not oyster heat-kill** and are not FishAI harvest authority.
- Chlorophyll is a valid BGC EMIV and an **invalid animal-abundance EMIV** (see C rejected rows).
- Vibrio/food-safety pathogens are **not** a v0.1 headline EMIV (impersonation wall).

---

## C — BIODIVERSITY (17, including 3 rejected mappings)

Every living row states a **claim-class**. Mixing classes is how SST/AIS products get sold as fish.

### Valid measurands

| ID | Name | Claim-class | Use | Validation | Privacy (public) |
| --- | --- | --- | --- | --- | --- |
| EMIV-BIO-OCC-001 | Taxon occurrence | DIRECT_DETECTION (or protocol absence) | CANDIDATE | UNVALIDATED | NEVER_PUBLISH native for rare/listed/spawn/haul-out |
| EMIV-BIO-ABUND-001 | Abundance — direct count | DIRECT_COUNT in the surveyed unit | CANDIDATE | UNVALIDATED | Farm inventory PRIVATE; wild aggregations NEVER_PUBLISH |
| EMIV-BIO-ABUND-002 | Abundance — survey index | SURVEY_INDEX | CANDIDATE | PROTOCOL_ONLY | Haul GPS often restricted |
| EMIV-BIO-CPUE-001 | Catch per unit effort | CPUE (not N) | CANDIDATE | UNVALIDATED | Native fishing grain NEVER_PUBLISH |
| EMIV-BIO-BIOM-001 | Biomass | DIRECT_WEIGHED or documented index | CANDIDATE | UNVALIDATED | Farm biomass PRIVATE |
| EMIV-BIO-DIST-001 | Distribution / range | RANGE_ENVELOPE | CANDIDATE | UNVALIDATED | Coarsen; not current presence |
| EMIV-BIO-STAGE-001 | Life stage / structure | DIRECT or index | CANDIDATE | LITERATURE | Stage papers must match product stage |
| EMIV-BIO-SIZE-001 | Body size | DIRECT morphology | CANDIDATE | PROTOCOL_ONLY | Follows occurrence join policy |
| EMIV-BIO-GENE-001 | Genetic diversity | LABORATORY genetics | CANDIDATE | UNVALIDATED | Farm genetics NEVER_PUBLISH |
| EMIV-BIO-COMM-001 | Community composition | ASSEMBLAGE index | CANDIDATE | UNVALIDATED | Rare members NEVER_PUBLISH at stations |
| EMIV-BIO-PHENO-001 | Phenology | OBSERVED event or degree-day INDEX | CANDIDATE | LITERATURE | Aggregation timing NEVER_PUBLISH native |
| EMIV-BIO-BEHAV-001 | Behavior / movement | TELEMETRY_INDIVIDUAL ≠ population | CANDIDATE | UNVALIDATED | Raw sensitive tracks NEVER_PUBLISH |
| EMIV-BIO-SUIT-001 | Habitat suitability | SUITABILITY (Cat D) — not presence | CANDIDATE | UNVALIDATED | Must not invert to nests |
| EMIV-BIO-EDNA-001 | eDNA occupancy | MOLECULAR_OCCUPANCY_INDEX | CANDIDATE | UNVALIDATED | Rare positives NEVER_PUBLISH native GPS |

GEO BON **Species distributions / Species abundances / Genetic composition / Species traits (morphology, phenology) / Community composition** are the EBV home for this group ([What are EBVs?](https://geobon.org/ebvs/what-are-ebvs/)). GOOS BioEco **Fish abundance and distribution** and analogue taxon EOVs map here **only at the correct claim-class** ([EOV sheets](https://goosocean.org/document-list/168)).

### Rejected instantiations (keep IDs; do not build)

| ID | Name | `model_use_status` |
| --- | --- | --- |
| EMIV-BIO-SSTN-001 | Taxon abundance from SST | REJECTED_AS_ABUNDANCE_PROXY |
| EMIV-BIO-AISN-001 | Taxon abundance from AIS/vessel density | REJECTED_AS_ABUNDANCE_PROXY |
| EMIV-BIO-CHLN-001 | Taxon abundance from chlorophyll/ocean color | REJECTED_AS_ABUNDANCE_PROXY |

These exist so a source catalog cannot “map Copernicus SST → BIO-ABUND-001” without hitting a dead-end ID.

---

## D — ECOSYSTEM (13)

| ID | Name | Use | Validation | Notes |
| --- | --- | --- | --- | --- |
| EMIV-ECO-PREY-001 | Prey / forage field | CANDIDATE | UNVALIDATED | Named prey; chl is a weak proxy only |
| EMIV-ECO-PRED-001 | Predator pressure | **DEFERRED** | UNVALIDATED | No public mammal/shark pins |
| EMIV-ECO-FOODWEB-001 | Food-web / trophic structure | **DEFERRED** | LITERATURE | Year-scale models, not 72 h |
| EMIV-ECO-HABEXT-001 | Habitat extent | CANDIDATE | PROTOCOL_ONLY | Official polygons; not animal N |
| EMIV-ECO-HABQUAL-001 | Habitat quality | CANDIDATE | LITERATURE | CRW DHW = heat stress, not coral count |
| EMIV-ECO-CORAL-001 | Coral cover and composition | CANDIDATE | PROTOCOL_ONLY | GOOS/IOOS hard coral; remnants NEVER_PUBLISH unpublished |
| EMIV-ECO-KELP-001 | Kelp / macroalgal canopy | CANDIDATE | LITERATURE | GOOS/IOOS macroalgae |
| EMIV-ECO-SEAGR-001 | Seagrass extent and composition | CANDIDATE | PROTOCOL_ONLY | GOOS/IOOS seagrass; unpublished remnants coarsen/withhold |
| EMIV-ECO-DIS-001 | Disease / pathogen in host | **DEFERRED** | LITERATURE | OsHV-1 not a default WA 72 h driver |
| EMIV-ECO-HAB-001 | HAB cells (animal-stress taxa) | CANDIDATE | LITERATURE | Split from NSSP harvest toxins |
| EMIV-ECO-EPROD-001 | Ecosystem productivity | CANDIDATE | UNVALIDATED | Not next-trip CPUE |
| EMIV-ECO-SPAWN-001 | Spawning / nursery / nesting habitat | CANDIDATE | UNVALIDATED | **NEVER_PUBLISH native grain** |
| EMIV-ECO-OPSOUT-001 | Aquaculture ops outcome | **W1_CORE** | UNVALIDATED | Mortality / workability / intervention; PRIVATE |

**Partner farm mortality is this last row** (biodiversity/ecosystem **ops** outcome), not a wild GOOS Fish EOV and not a DOH closure.

---

## E — HUMAN PRESSURE (13)

Official harvest/closure is a **pressure/constraint**, not abundance and not farm mortality.

| ID | Name | Use | Validation | Privacy |
| --- | --- | --- | --- | --- |
| EMIV-HUM-FISH-001 | Fishing effort | CANDIDATE | UNVALIDATED | Native effort NEVER_PUBLISH |
| EMIV-HUM-AIS-001 | AIS-derived vessel activity | **DEFERRED** | UNVALIDATED | Identity NEVER_PUBLISH; not abundance |
| EMIV-HUM-NOISE-001 | Anthropogenic ocean sound | CANDIDATE | PROTOCOL_ONLY | GOOS/IOOS Ocean sound; no mammal bearings |
| EMIV-HUM-POLL-001 | Pollution pressure (sources) | CANDIDATE | UNVALIDATED | Not a targeting layer |
| EMIV-HUM-HABDAM-001 | Habitat damage | CANDIDATE | UNVALIDATED | Remnants NEVER_PUBLISH |
| EMIV-HUM-SHIP-001 | Shipping / transit pressure | CANDIDATE | UNVALIDATED | Not fishing effort; not N |
| EMIV-HUM-AQUA-001 | Aquaculture siting / pressure | CANDIDATE | PROTOCOL_ONLY | Outlines maybe public; KPIs never |
| EMIV-HUM-CONST-001 | Offshore construction / energy | CANDIDATE | UNVALIDATED | Unpublished cables NEVER_PUBLISH |
| EMIV-HUM-CLIM-001 | Climate stress (MHW / compound) | CANDIDATE | LITERATURE | W1 pathway is often **air+emersion**, not SST MHW |
| EMIV-HUM-MPA-001 | Marine protection designation | CANDIDATE | PROTOCOL_ONLY | Exact official polygons |
| EMIV-HUM-HARV-001 | Official harvest / closure status | CANDIDATE | PROTOCOL_ONLY | WA DOH/NSSP/PFMC **constraint** |
| EMIV-HUM-CULT-001 | Culture method / tidal elevation | CANDIDATE | LITERATURE | Required W1 metadata; PRIVATE |
| EMIV-HUM-HAND-001 | Handling / crowding / gear ops | CANDIDATE | LITERATURE | Farm logs only |

**AIS effort is HUMAN PRESSURE** (`EMIV-HUM-AIS-001` / `FISH-001` / `SHIP-001`). Using it as abundance hits `EMIV-BIO-AISN-001`.

---

## F — OBSERVATION QUALITY (10)

These are first-class EMIVs. A twin cell without them is incomplete, not “high confidence.”

| ID | Name | Use | Validation | Role |
| --- | --- | --- | --- | --- |
| EMIV-QUA-PDETECT-001 | Detection probability | CANDIDATE | UNVALIDATED | Non-detection ≠ absence if p UNKNOWN |
| EMIV-QUA-SEFFORT-001 | Survey / sampling effort | CANDIDATE | PROTOCOL_ONLY | Denominator; zeros without effort = UNKNOWN |
| EMIV-QUA-SCOV-001 | Spatial coverage | CANDIDATE | UNVALIDATED | Unsampled ≠ zero biology |
| EMIV-QUA-TCOV-001 | Temporal coverage / duty cycle | CANDIDATE | UNVALIDATED | Daily L4 ≠ 6-min tide |
| EMIV-QUA-TAXCONF-001 | Taxonomic ID confidence | CANDIDATE | PROTOCOL_ONLY | Acoustics ≠ Linnaean name without validation |
| EMIV-QUA-CALIB-001 | Sensor calibration / fouling | CANDIDATE | PROTOCOL_ONLY | QARTOD; DO/S/pH/optics |
| EMIV-QUA-FRESH-001 | Data freshness / as-of | CANDIDATE | UNVALIDATED | No future leakage |
| EMIV-QUA-SRCCONF-001 | Source confidence / rights | CANDIDATE | UNVALIDATED | UNKNOWN blocks paid resale |
| EMIV-QUA-QFLAG-001 | Provider quality flags | CANDIDATE | PROTOCOL_ONLY | GHRSST/QARTOD/Argo/QUID |
| EMIV-QUA-DCOV-001 | Depth coverage | CANDIDATE | UNVALIDATED | SST coverage ≠ bottom-T coverage |

QARTOD: https://ioos.noaa.gov/project/qartod/

---

## Counts by `model_use_status`

| Status | n |
| --- | --- |
| CANDIDATE | 65 |
| W1_CORE | 10 |
| DEFERRED | 4 (`PRED`, `FOODWEB`, `DIS`, `AIS`) |
| REJECTED_AS_ABUNDANCE_PROXY | 3 |
| W1_PROXY | 2 (SST, RUNOFF) |
| **Total** | **84** |

No row is `OPERATIONAL`.
