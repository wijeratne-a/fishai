# Data source priority queue

**Date:** 2026-09-18 (W1 GT relabel)  
**Scale:** 0–1 weighted score (see `scoring_and_verification.md`)  
**Status:** nothing ingested  
**Label correction:** WA DOH closures are a P0 **constraint**, not ops GT. See `ground_truth_relabel_W1.md`.

P0 = needed for a wedge-locked MVP **feature, constraint, or label** store. Within P0, ingest **public NOAA/Copernicus first**, then agency **constraint** exports, then partner **GT**. Do not treat a high score with `rights_score ≤ 0.30` as a download target. Do not treat a high constraint score as a training label.

## Must-show W1 constraint (not in raw top 10 after relabel)

| Score | source_id | Role | Rights flag |
|------:|-----------|------|-------------|
| 0.745 | WDOH-GROWING-AREA-CLOSURES | Official **harvest legally open?** overlay + user-facing authority link. **Not** `ops_disruption_72h`. Still **P0**. | UNKNOWN redistribution |

SPS fell from 0.885 because `expected_predictive_lift` is scored against the **ops-stress model**, which closures do not train.

## Top 10 sources overall (unique `source_id`, after relabel)

| Rank | Score | source_id | Why it is in the top 10 | Wedges | Rights flag |
|------|------:|-----------|-------------------------|--------|-------------|
| 1 | 0.883 | NOAA-GOMOFS | 72 h GOM 3D physics matched to next-trip | W3 | U.S. Gov / CONDITIONAL TOS |
| 2 | 0.880 | NWS-API-FORECAST | Go-no-go weather for all three | all | Public domain disclaimer retrieved |
| 3 | 0.845 | NOAA-WCOFS | West Coast 3D nowcast/forecast | W1 W2 | U.S. Gov / CONDITIONAL TOS |
| 4 | 0.842 | UW-LIVEOCEAN | Only estuary-resolving 72 h Salish Sea forecast cataloged | W1 | **UNKNOWN commercial** |
| 5 | 0.837 | NOAA-COOPS-WATERLEVEL | Tides + station T/wind; Seattle metadata probed | all | U.S. Gov / identify `application=` |
| 6 | 0.833 | EMOLT-BOTTOM-TEMP | Direct lobster catchability **covariate** | W3 | NOAA as-is + location sensitivity |
| 7 | 0.823 | NANOOS-ORCA-MOORINGS | In-situ T/S/DO covariates; **Hood Canal ≠ Willapa** | W1 | Cite metadata; commercial UNKNOWN |
| 8 | 0.820 | CMEMS-GLO-PHY-001-024 | Global 10-day T/S/currents; **commercial allowed with attribution** | all | Copernicus licence retrieved |
| 9 | 0.817 | NOAA-GFS-WAVE | Operational waves for gear/trip risk | all | NOMADS HTTPS (OpenDAP retired) |
| 10 | 0.815 | NANOOS-NVS-SHELLFISH-GROWERS | Grower-oriented WQ covariates | W1 | Cite metadata; commercial UNKNOWN |

Honorable P0: CDFW-OCEAN-SALMON-REGS (0.812, W2 **constraint**), NOAA-PFEL-UPWELLING (0.810), NERACOOS-BUOYS (0.808), PARTNER-FARM-OPS-LOGS (0.780, **the W1 ops label**; rights-limited).

**If ranking by lawful commercial clarity instead of raw score:** start with NWS, CO-OPS, GoMOFS, WCOFS, CMEMS PHY/WAV, GFS-Wave, GEBCO, PFEL, MUR (CONDITIONAL Earthdata), then state/IOOS. Show DOH as an authority link, not a model target.

## Queue by wedge (ingest order if that wedge is locked)

### W1 oyster — P0 sequence (public covariates → harvest-open constraint → partner **label**)

1. NWS-API-FORECAST  
2. NOAA-COOPS-WATERLEVEL (WA stations + predictions)  
3. USGS-WATERDATA-DISCHARGE (gages tied to **conditional harvest-open** rules, not mortality labels)  
4. NOAA-WCOFS  
5. CMEMS-GLO-PHY-001-024 (fallback / offshore)  
6. NOAA-MUR-SST-v4.1 (or geo-polar SST)  
7. NOAA-GFS-WAVE  
8. NANOOS-ORCA-MOORINGS + NANOOS-NVS-SHELLFISH-GROWERS + NERRS-CDMO (Padilla Bay). **Do not treat Hood Canal ORCA as Willapa coverage.**  
9. WDOH-GROWING-AREA-CLOSURES + WDOH-COMMERCIAL-VIEWER (**agency export of harvest-open history**, not HTML scrape; **constraint overlay only**)  
10. WORMS-TAXONOMY (bind *Magallana gigas*)  
11. PARTNER-FARM-OPS-LOGS (**the `ops_disruption_72h` label**: mortality, workability, intervention)  
12. UW-LIVEOCEAN **only after written terms** (covariate)  
13. SOUNDTOXINS **partner account / DUA** (covariate, not legal reopen)  
14. WDFW-WAHH-AQUACULTURE **only as aggregated harvest-volume context**, never as ops GT  

P1: PNW HAB Bulletin, ISSC/NSSP (constraint ontology), NOAA-NCEI-COASTAL-RELIEF, GEBCO.  
P2: ESP pDA, CMEMS waves as WW3 fallback.  
P3: Ecology EIM, Argo (offshore validation only), OBIS range prior.

### W2 Chinook — P0 sequence

1. PFMC-NOAA-OCEAN-SALMON-REGS + CDFW-OCEAN-SALMON-REGS (hard zeros; **constraint**)  
2. NWS-API-FORECAST + NOAA-NDBC + NOAA-GFS-WAVE  
3. NOAA-WCOFS + NOAA-PFEL-UPWELLING + NOAA-MUR-SST-v4.1  
4. NOAA-COASTWATCH-CHL (science-quality for train, NRT for infer)  
5. USGS-WATERDATA-DISCHARGE (Klamath/Eel/Columbia plume)  
6. CMEMS-GLO-PHY-001-024 fallback  
7. ODFW-OCEAN-SALMON-CATCH-INDEX (**request CSV**, do not scrape PDFs)  
8. RECFIN-SALMON-CATCH-EST (public **salmon** report, **not CTE001**)  
9. PARTNER-CHARTER-LOGS (required for 24–48 h claim)

P1: CRFS program coordination, NANOOS coastal buoys/HFR for OR/WA-adjacent, CMEMS BGC.  
P3: CCIEA (feature pedigree only). Do not P0 JSOES microdata.

### W3 lobster — P0 sequence

1. NWS-API-FORECAST + NOAA-GFS-WAVE + NOAA-NDBC  
2. NOAA-GOMOFS  
3. NERACOOS-BUOYS  
4. EMOLT-BOTTOM-TEMP (**bin locations**; do not ship raw fishing GPS)  
5. CMEMS-GLO-PHY-001-024 + MUR SST fallback  
6. NOAA-ALWTRP polygons + NOAA-RIGHTWHALE-SLOW-ZONES alerts (**constraints**)  
7. ME-DMR-LANDINGS (seasonality/price only; **not CPUE**)  
8. PARTNER-LOBSTER-TRIP-LOGS **or** ME-DMR-HARVESTER-LEEDS DUA (labels; LEEDS microdata **not** public)

P1: CO-OPS New England water level/temp.  
P2: VTR only with NAO 216-100 paperwork (confidential).  
P3: Ventless, ME-NH trawl dashboard.  
P4: NEFSC trawl, ASMFC assessment, FOSS.

## Do-not-queue (this iteration)

- HTML scrapers for DOH, ODFW, CDFW FileHandler, SoundToxins maps  
- Training `ops_disruption_72h` on DOH/NSSP closures or growing-area class  
- Parallel ERDDAP/NOMADS/Copernicus pulls  
- Confidential VTR/LEEDS/WAHH microdata without DUA  
- CC BY-NC OBIS/GBIF subsets in a commercial model  
- GEBCO or OFS as navigation/safety-at-sea products  
- New buoys/cameras/app telemetry before partner logs exist
