# Agent handoff — GLOBAL SALTWATER LIFE OBSERVATORY catalogs

**Date:** 2026-09-18  
**Agents:** GLOBAL_BIODIVERSITY_DATA_AGENT + OCEAN_PHYSICS_AND_CHEMISTRY_AGENT + HABITAT_AND_BATHYMETRY_AGENT + FISHERIES_AND_VESSEL_DATA_AGENT + AQUACULTURE_DATA_AGENT (catalog only)  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/`  
**Ingest:** none. **Counsel:** none. Not legal advice.

---

## 1. Executive finding

A **lawful global catalog** for a Saltwater Life Observatory can be built from **~140 source families** (not thousands of duplicate portals). Nothing is ingested.

A first **digital-twin prior** should be **physics + bathymetry + taxonomy**, not occurrence firehoses or AIS:

- **Copernicus Marine** physics/waves/reanalysis (commercial derivatives with attribution + traceability)
- **Argo** (unrestricted with DOI acknowledgement)
- **WOA/WOD + NOAA OISST/CoastWatch + NASA Earthdata ocean colour** (US Gov / CC0 defaults)
- **ERA5 + NWS/GFS + GFS-Wave**
- **GEBCO** (commercial OK; **not navigation**)
- **WoRMS webservice** (cite; no full-DB redistrib)

Biology enters later as a **licence-filtered presence prior** (OBIS/GBIF CC0/CC BY only; ICES DATRAS; RAM Legacy), never as a 24–72 h abundance nowcast.

**Binding global gap:** there is still **no lawful global label** for next-trip CPUE or farm-level outcomes. FAO catch is too coarse; GFW/AIS is not fish; confidential logbooks stay restricted.

**Do not start** on GFW, WDPA, UNEP-WCMC General License habitat layers, FishBase/AquaMaps, Sea Around Us, iNaturalist (commercial AI ban), VMS, or NASA CSDA.

Wedge-specific US catalogs in `artifacts/data_discovery/` were **extended, not overwritten**.

---

## 2. Counts

| Artifact | Rows |
|----------|-----:|
| `observatory/global_data_catalog.csv` | **140** sources × 39 columns |
| `observatory/global_ocean_variable_catalog.csv` | **46** variables × 9 columns |

`integration_status` for every source row: `catalog_only_not_ingested`.  
`last_verified_at`: `2026-09-18`.

Legal-status mix: 37 open-commercial (US Gov-class), 38 attribution-OK (Copernicus/CC BY/Argo/GEBCO-class), 49 conditional, 10 noncommercial, 5 paid, 1 restricted (VMS).

P0 physics/twin-prior IDs: `WORMS-TAXONOMY`, `ARGO-GDAC`, `GOOS-OCEANOPS`, `IOOS-CATALOG` (discovery only until per-dataset licence), `CMEMS-SATELLITE-OC-SST`, `NASA-EARTHDATA-OCEAN`, `GHRSST` (per-collection), `NOAA-OISST`, `NOAA-COASTWATCH`, `CMEMS-GLO-PHY`, `CMEMS-GLO-WAV`, `CMEMS-GLORYS12`, `NOAA-RTOFS`, `NOAA-GFS-WAVE`, `C3S-ERA5`, `NOAA-GFS`, `GEBCO-GRID`, `NOAA-COOPS`, `NOAA-NDBC`, `WOA23`, `WOD23`.

---

## 3. Evidence table

| Finding | Evidence | Confidence |
|---------|----------|------------|
| CMEMS allows credited commercial derivatives | https://marine.copernicus.eu/user-corner/service-commitments-and-licence (rights agent 2026-09-18 + this catalog) | High on posted text |
| Argo “freely available without restriction” + DOI acknowledgement | https://argo.ucsd.edu/data/acknowledging-argo/ | High |
| GEBCO commercial OK, not navigation | https://www.gebco.net/data-products/gridded-bathymetry/terms-of-use | High |
| ICES public data CC BY 4.0; RDBES/VMS/logbook excluded | https://www.ices.dk/data/guidelines-and-policy/pages/ices-data-policy.aspx | High |
| EMODnet **products** generally CC BY 4.0; originator surveys may not be | https://emodnet.ec.europa.eu/en/terms-use-emodnet-online-services-data-and-data-products | High |
| GFW CC BY-NC / no public commercial licence | https://globalfishingwatch.org/terms-of-use/ | High |
| WDPA no commercial use of data or derivatives without permission | https://www.protectedplanet.net/en/legal | High |
| UNEP-WCMC General License no commercial use/redistribution | https://www.unep-wcmc.org/en/general-data-license. | High |
| FAO FishStat CC BY **plus** no promotion of commercial enterprise | https://www.fao.org/contact-us/terms/db-terms-of-use/en/ | High on posted extra terms; product use needs counsel |
| OBIS/GBIF per-dataset CC0/CC BY/CC BY-NC | OBIS policy; GBIF data-user agreement | High |
| FishBase / AquaMaps NC | FishBase citation page; AquaMaps TermsConditions.php | High |
| Allen Atlas maps CC BY; mosaic NC; no full global habitat republish without consent | https://allencoralatlas.org/resources/ | High |
| iNaturalist TOS bans commercial AI training | iNaturalist terms | High |
| OceanSITES: contact PI before commercial use | OceanSITES NetCDF `license` attribute / format manual | High |
| WoRMS: no full DB redistrib | https://marinespecies.org/about.php | High |
| NASA-led Earthdata default CC0; CSDA noncommercial | ESDIS guidance + CSDA EULAs | High |
| RAM Legacy v4.65 CC BY 4.0 | Zenodo 10.5281/zenodo.11995054 | High |
| Sea Around Us CC BY-NC 4.0 | https://www.seaaroundus.org/terms-and-conditions/ | High |
| IMOS/AODN majority CC BY 4.0 + acknowledgement | https://imos.org.au/conditions-of-use | High |
| ISSC/NSSP is authority text, not a sensor | FDA 2023 NSSP Guide; ISSC nssp-guide | High |
| IOOS “open sharing” ≠ user commercial licence | IOOS policy + rights agent | High |
| Movebank/OTN/ATN are per-study / embargoed | Movebank data policy; OTN 2024 policy; ATN DAC | High that commercial use is conditional |

---

## 4. Source / licence table (families)

Full rows: `global_data_catalog.csv`. Summary:

| Family | Prototype role | Legal class (as cataloged) |
|--------|----------------|----------------------------|
| Copernicus Marine PHY/WAV/BGC/OC | Twin prior / forecast | APPROVED_WITH_ATTRIBUTION |
| NOAA-created env (NWS, NDBC, CO-OPS, OISST, WOA, surveys as annotated) | Twin prior / US in situ | APPROVED_OPEN_COMMERCIAL |
| NASA-led unmarked Earthdata | Ocean colour / SWOT / SMAP | APPROVED_OPEN_COMMERCIAL |
| Argo / GO-SHIP / WOD | Subsurface constraint | APPROVED_WITH_ATTRIBUTION / open |
| GEBCO | Bathymetry prior | APPROVED_WITH_ATTRIBUTION (not navigation) |
| WoRMS webservice | Taxon kernel | APPROVED_WITH_ATTRIBUTION (no full dump) |
| ICES DATRAS / public catch cubes | Survey indices | APPROVED_WITH_ATTRIBUTION (not RDBES) |
| RAM Legacy | Stock-scale prior | APPROVED_WITH_ATTRIBUTION |
| OBIS/GBIF | Presence prior | CONDITIONAL — strip NC |
| EMODnet products | Europe habitat/bathy/biology | APPROVED_WITH_ATTRIBUTION; originators differ |
| Allen Coral Atlas maps | Reef habitat | CONDITIONAL (maps CC BY; mosaic NC; no global dump) |
| ISSC/NSSP | Sanitation ontology only | APPROVED_OPEN_COMMERCIAL as **citation** |
| FAO FishStat / NASO | National stats | CONDITIONAL (extra FAO terms) |
| Sea Grant | Literature, not a DB | CONDITIONAL per publication |
| GFW / FishBase / AquaMaps / SAU / WDPA / UNEP-WCMC general / CSDA / iNat default | Do not use in commercial twin | NONCOMMERCIAL_ONLY |
| AIS vendors / Planet / Maxar / Sofar | Paid | PAID_LICENSE_REQUIRED |
| NOAA VMS | Blocked | RESTRICTED |
| Partner farm/logbook data | Not in this global catalog | Requires DPA (see rights agent) |

---

## 5. Critical global gaps

1. Outcome labels at operational horizon (trip CPUE, farm mortality) — **missing worldwide** in public lawful form.  
2. Coastal 3D oxygen / bottom T / OA at lease scale.  
3. Named HAB cell/toxin NRT (global).  
4. Fishery-independent surveys outside North Atlantic / US / Australia / parts of Europe.  
5. eDNA as biomass (scientifically and legally unready).  
6. Commercial-use habitat polygons (WDPA/UNEP-WCMC).  
7. Polar / deep / mesopelagic life.  
8. CARE-compliant Indigenous data (default deny).  
9. IOOS and many RA ERDDAP licence blanks.  
10. Mixing ERA5 (delayed) with NRT forecasts without `published_at` cutoff (leakage — see geospatial as-of design).

---

## 6. Recommended decision

1. Treat this catalog as the **global family map** for the observatory; bind a **single wedge** before any connector.  
2. If building a twin sandbox, implement **P0 physics + GEBCO + WoRMS** only, AOI-clipped, after rights sign-off on the exact product IDs.  
3. Implement an allowlist that **denies** GFW, CC BY-NC, VMS, CSDA, WDPA, UNEP-WCMC General, FishBase, AquaMaps, SAU, scrape.  
4. If biology is needed for a prior, **filter OBIS/GBIF licences in the download**, coarsen sensitive taxa, and state presence-only.  
5. Aquaculture remains catalog-only: FAO/EUMOFA context + NSSP as **constraint ontology**, never authorization, never farm KPIs without a DPA.  
6. Do not ingest `artifacts/data_discovery/` or this catalog’s URLs until DATA_RIGHTS + founder wedge lock.

---

## 7. Rejected alternatives

| Alternative | Why rejected |
|-------------|--------------|
| Global OBIS/GBIF lake as v1 | NC contamination, sampling bias, not a nowcast, CARE |
| GFW as “fishing = fish” | False scientifically; NC legally |
| WDPA as default MPA mask in a commercial product | Written-permission commercial ban |
| FAO FishStat as CPUE | No effort; extra commercial-promotion terms |
| Satellite chl as HAB or abundance | Wrong variable |
| Live AIS / VMS | Privacy, statute, not abundance |
| Full WoRMS dump | Terms forbid without agreement |
| Allen Atlas Planet mosaic in commercial UI | CC BY-NC-SA |
| Scraping ISSC/state viewers | TOS + impersonation risk |
| Overwriting wedge `data_discovery` catalog | Out of scope; that catalog stays US-wedge |

---

## 8. Follow-ups

- DATA_RIGHTS: re-read FAO extra terms vs CC BY; IOOS empty licences; GHRSST collection EULAs; LiveOcean (wedge); Allen Atlas download vs WMS; BOLD share-alike product impact.  
- GEOSPATIAL: connector stubs only for P0 IDs; licence field required; as-of cutoff for ERA5 vs GFS.  
- MARINE_DOMAIN: keep SST/chl/AIS out of abundance claims (variable catalog encodes this).  
- PRODUCT: no harvest/navigation/weather-safety authorization copy.  
- Founder: still must lock ONE species × geography × customer × decision before ingest.

---

## 9. Artifacts

Under `/Users/wijeratne/dev/fishai/observatory/`:

1. `global_data_catalog.csv` (140)  
2. `global_ocean_variable_catalog.csv` (46)  
3. `data_catalog_notes.md`  
4. `artifacts/data_catalog/agent_handoff.md` (this file)  
5. `scripts/build_global_catalogs.py`

Did **not** modify `/Users/wijeratne/dev/fishai/artifacts/data_discovery/`.

---

## 10. Next experiment (catalog only)

If a wedge locks: subset this global catalog to the AOI, join to the wedge `data_catalog.csv`, and run a **licence allowlist dry-run** (no download) listing every P0 product ID, DOI, and attribution string. Stop if any licence is UNKNOWN.
