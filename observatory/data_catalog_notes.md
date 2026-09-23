# Global Saltwater Life Observatory — data catalog notes

**Date:** 2026-09-18  
**Agents:** GLOBAL_BIODIVERSITY_DATA_AGENT + OCEAN_PHYSICS_AND_CHEMISTRY_AGENT + HABITAT_AND_BATHYMETRY_AGENT + FISHERIES_AND_VESSEL_DATA_AGENT + AQUACULTURE_DATA_AGENT (catalog only)  
**Ingest:** none. Modest documentation/API-metadata lookups only.  
**This is not legal advice.** Visual access is not commercial use.

## What was written

| File | Role |
|------|------|
| `observatory/global_data_catalog.csv` | **140** source-family rows (39 columns specified in the brief) |
| `observatory/global_ocean_variable_catalog.csv` | **46** variables with inference role and leakage notes |
| `observatory/data_catalog_notes.md` | This file |
| `observatory/artifacts/data_catalog/agent_handoff.md` | Handoff for other agents |
| `observatory/scripts/build_global_catalogs.py` | Regenerator (no bulk download) |

All catalog rows have `integration_status=catalog_only_not_ingested` and `last_verified_at=2026-09-18`.

## Relationship to existing FishAI discovery

`artifacts/data_discovery/` (wedge-scoped ~56-row catalog, US oyster/Chinook/lobster) was **read and not overwritten**. This observatory catalog **extends globally**: one representative source (or small family) per observing class, not thousands of duplicate regional ERDDAP datasets. Local IOOS/NANOOS/WA DOH detail remains in the wedge catalog.

## Design rules used

- Catalog **lawful source families** with one or few concrete portals, not every national portal clone.
- SST, chlorophyll, and AIS/VMS are **never** treated as abundance.
- Licences were taken from official pages or marked **UNKNOWN**. Mixed aggregators (OBIS, GBIF, IOOS, EMODnet originators, PANGAEA) are **per-dataset**.
- Aquaculture is **catalog only** (FAO stats, NASO, NOAA siting, ISSC/NSSP authority text, Sea Grant literature, EUMOFA). No farm performance.
- Seabed products **must not be used for navigation**. NSSP/ISSC **must not** be used as FishAI harvest authorization.

## Row counts by family (140)

| Category | n | Representative sources |
|----------|--:|------------------------|
| ocean_observing_system | 12 | Argo, GOOS/OceanOPS, IOOS, OceanSITES, GO-SHIP, OOI, IMOS, ONC, EMSO, GDP drifters, SeaDataNet |
| satellite_provider | 11 | CMEMS OC/SST, Sentinel-3/2, NASA Earthdata/PACE, SWOT, GHRSST, OISST, CoastWatch, SMAP, ESA CCI, Landsat |
| weather_wave_tide_current | 9 | NWS/GFS, GFS-Wave, ERA5, CO-OPS, NDBC, OSCAR, CMEMS altimetry, PSMSL, CMEMS waves |
| fisheries_survey | 7 | ICES DATRAS, NOAA NEFSC/NWFSC/AFSC, CalCOFI, DFO, IMOS |
| stock_assessment | 6 | RAM Legacy, Stock SMART, ICES advice, FIRMS, ICCAT, WCPFC/SPC |
| taxonomy_registry | 6 | WoRMS, ITIS, CoL, NCBI Taxonomy, FishBase (NC), IUCN Red List (NC/IBAT) |
| biodiversity_occurrence | 6 | OBIS, GBIF, OBIS-SEAMAP, EMODnet Biology, Reef Life Survey, PANGAEA |
| aquaculture | 6 | FAO aquaculture, NASO, NOAA AOA, ISSC/NSSP, Sea Grant, EUMOFA |
| commercial_vendor | 6 | AIS vendors, Planet, Maxar, Sofar, Saildrone mix, cable map |
| plus bathymetry (5), BGC (5), eDNA (5), infrastructure (5), models (5), vessel/gear (5), acoustics (4), catch (4), habitat (4), MPA (4), reef/kelp/seagrass (4), telemetry (4), cameras (3), citizen (3), coral (3), plankton (3), runoff (3), MHW (2) | | |

Legal-status mix: **37** `APPROVED_OPEN_COMMERCIAL`, **38** `APPROVED_WITH_ATTRIBUTION`, **49** `CONDITIONAL_REVIEW_REQUIRED`, **10** `NONCOMMERCIAL_ONLY`, **5** `PAID_LICENSE_REQUIRED`, **1** `RESTRICTED` (NOAA VMS). Counsel still required before any ingest, including “APPROVED_*” rows (attribution, traceability, product-level credits).

## Best starting sources for a digital-twin **prior** (not a nowcast of animals)

These support a first physics/habitat prior **without claiming they are ingested**. Prefer this stack over occurrence firehoses.

1. **3D physics prior:** Copernicus Marine `GLOBAL_ANALYSISFORECAST_PHY_001_024` + **GLORYS12** reanalysis (commercial derivatives allowed with credit + traceability). Fallback: NOAA RTOFS / HYCOM (confirm current terms).
2. **In-situ subsurface constraint:** **Argo GDAC** (unrestricted with DOI acknowledgement). Not a shelf/estuary product.
3. **Climatology backbone:** **WOA23 / WOD23** (NOAA: free, unrestricted per WOD manual).
4. **Surface thermal state:** **NOAA OISST v2.1** + GHRSST/MUR (check Earthdata collection) + **NOAA CoastWatch**.
5. **Ocean colour (habitat proxy only):** NASA Earthdata (CC0 default for NASA-led) and CMEMS OC TAC. Never as fish or HAB toxin.
6. **Atmosphere / waves:** **ERA5** (historical forcing) + **NWS/GFS** + **GFS-Wave** / CMEMS waves. Do not confuse ERA5 with paid ECMWF operational IFS.
7. **Bathymetry:** **GEBCO** (commercial OK, attribution, **not navigation**). US inshore: NCEI CRM. Europe: EMODnet DTM (CC BY) vs permissioned surveys.
8. **Taxonomy kernel:** **WoRMS REST** (cite; **do not redistribute the full database**).
9. **Biology prior (optional, licence-filtered):** OBIS/GBIF **CC0 or CC BY only**; Reef Life Survey if terms cleared; ICES DATRAS / RAM Legacy for assessed stocks. Not a 24–72 h local abundance layer.
10. **Coral heat stress (if reef twin):** NOAA Coral Reef Watch (US Gov). Allen Coral Atlas **maps** are CC BY 4.0 but **Planet mosaic is NC** and **global habitat dump needs ASU consent**.

**Do not start the twin on:** GFW, WDPA, UNEP-WCMC General License layers, FishBase/AquaMaps, Sea Around Us, iNaturalist (default NC + commercial AI ban), VMS, raw AIS identity, NASA CSDA, confidential logbooks.

## Critical global gaps

1. **No global lawful label for next-trip CPUE or farm mortality.** Public catch is annual/national (FAO) or confidential at haul scale (MSA, ICES RDBES, most RFMOs). This is the same blocker the wedge catalog found, now stated globally.
2. **Coastal subsurface oxygen, bottom temperature, and carbonate chemistry** are sparse outside a few observatories (IOOS, IMOS, EMSO, OA buoys). Global models do not resolve leases/fjords.
3. **Named HAB taxa and toxins** have no lawful global NRT layer. HAEDAT is events; NSSP is legal status; satellite chl is the wrong variable.
4. **Tropical / Global South fishery-independent time series** are thinner than ICES/NOAA. RAM Legacy and FIRMS are incomplete and lagged.
5. **eDNA/genomics** are presence of DNA, not biomass; ABS/Nagoya and per-submitter IP remain open.
6. **Habitat map licences are a minefield:** WDPA and many UNEP-WCMC Ocean Data Viewer layers forbid commercial use/redistribution by default.
7. **Telemetry and marine mammal acoustics** are scientifically gold and legally/ethically high-sensitivity (embargoes, CARE, MMPA).
8. **Polar, deep pelagic, and mesopelagic** life remain severely under-sampled relative to coastal fishes.
9. **AIS/VMS/GFW** cannot close the biology gap and introduce privacy + NC/paid/restricted landmines.
10. **IOOS/NANOOS-class regional datasets** often have **empty licence fields** — free download ≠ commercial grant (already flagged in rights work).

## Legal landmines (do not “just download”)

| Landmine | Why |
|----------|-----|
| **Global Fishing Watch** | CC BY-NC 4.0 + TOS; scraping banned; public API is noncommercial; commercial needs custom licence |
| **WDPA / Protected Planet** | No commercial use of data **or derivatives** without UNEP-WCMC written permission; IBAT is the commercial path |
| **UNEP-WCMC General Data License** (seagrass, many coral/habitat layers) | No commercial use or redistribution without permission |
| **FAO FishStat (capture and aquaculture)** | Advertised CC BY 4.0 **plus** terms forbidding use to promote a commercial enterprise/product/service; HUMAN LEGAL REVIEW |
| **OBIS / GBIF mixed CC** | CC BY-NC subsets cannot enter a commercial product; must filter on the download DOI |
| **FishBase / AquaMaps** | CC BY-NC |
| **Sea Around Us** | CC BY-NC 4.0 |
| **iNaturalist** | Per-record mix; default CC BY-NC; TOS **prohibits commercial AI/ML training** |
| **NASA CSDA** | Scientific noncommercial EULA; no revenue-generating use of data or derivatives |
| **NOAA VMS / MSA confidential stats / observers** | Statutory; never ingest |
| **Marine Cadastre AIS** | Public-domain vs no-redistribute conflict; vessel identity private; not abundance |
| **Commercial AIS** | Paid TOS; do not scrape MarineTraffic et al. |
| **OceanSITES** | Default attribute: **contact PI before commercial use** |
| **WoRMS full DB** | Webservice OK; entire database needs written agreement; images often NC-SA |
| **BOLD public packages** | CC BY-**SA** 4.0 share-alike architecture risk |
| **Allen Coral Atlas mosaic** | Planet CC BY-NC-SA; full global habitat republication needs written consent |
| **ISSC / NSSP** | Authority document only — product must not authorize harvest |
| **IUCN Red List spatial** | Commercial typically IBAT; sensitive ranges |
| **Indigenous / TEK / treaty data** | CARE; default deny |
| **ECMWF operational NWP** | Not ERA5; paid commercial licences |
| **Website scraping / forums** | Rejected |

## Variable catalog — how to read `evidence_tier_if_used_as_biology`

Many excellent ocean variables are **T4 if sold as animals** and **T1–T2 as habitat or operations**. The variable file states both. Digital-twin priors should use physics/habitat as **priors and masks**, then add licence-filtered biology. Do not invert chlorophyll or vessel density into species counts.

## Verification notes

Looked up (2026-09-18) official terms or current licence statements for: Copernicus Marine, Sentinel Legal Notice, Argo acknowledgement, FAO statistical DB terms, ICES data policy/DATRAS, EMODnet terms, GEBCO terms, NASA Earthdata guidance, NCEI open data policy, GFW TOS/NC, WDPA legal, UNEP-WCMC general licence, Allen Coral Atlas FAQ, Movebank data policy, OTN 2024 policy, FishBase citation, AquaMaps terms, FathomNet data use, NCBI/ENA policies, BOLD data packages, RAM Legacy Zenodo CC BY, Sea Around Us terms, IMOS conditions of use, OceanSITES licence attribute, ISSC/NSSP guide location, iNaturalist TOS (commercial AI ban). FAO HTML and Argo acknowledgement page fetches **timed out** once; classifications use search-verified official URLs plus the rights agent’s 2026-09-18 matrix. **Re-read live pages before ingest.**

## Regenerating

```bash
python3 observatory/scripts/build_global_catalogs.py
```
