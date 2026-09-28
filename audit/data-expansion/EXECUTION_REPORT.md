# Data expansion execution report

```
STRUCTURED SOURCES DISCOVERED: 8 NOAA NCEI ERDDAP datasets matching CRCP_Reef_Fish
STRUCTURED SOURCES ACQUIRED: 8. Florida Keys years were already local. Seven other regions received a newest year and one earlier year.
REGIONS ACQUIRED: Florida Keys, Puerto Rico, U.S. Virgin Islands, Flower Garden Banks, Hawaii, American Samoa, CNMI/Guam, Pacific Remote Island Areas
LATEST STRUCTURED OBSERVATION: 2024-11-26 on the Florida table. Puerto Rico ends 2023-11-16. USVI ends 2023-08-18. No 2025 file was in the ERDDAP catalog.
PRESENCE-ONLY SOURCES ACQUIRED: OBIS Florida Keys box, 90-day window, 500 of 672 reported records saved. Latest event date in that page is 2026-07-20.
CURRENT OCEAN SOURCES ACQUIRED: MUR analysed SST snippet, valid time 2026-09-23T09:00:00Z. Not joined to surveys.
TOTAL TAXA: not a single pooled count. Florida Keys RVC uses 249 species codes shared by 2018, 2022, and 2024. Other regions keep their own lists.
MODEL-READY TAXA: one fitted internal baseline, Chaetodon capistratus in the Florida Keys. Puerto Rico, USVI, and Flower Garden Banks have zero-bearing survey frames and no new species fit.
RECENT-EVIDENCE-ONLY TAXA: the OBIS Keys extract. It is not a live-location layer.
ACCOUNT-REQUIRED SOURCES: GBIF bulk occurrence download. The public search API answered without an account. Copernicus remains without credentials. CoastWatch RTOFS forecast search returned HTTP 404.
NEXT BOTTLENECK: Pacific tables have counts and no zero rows, so they cannot train a detection model yet. Atlantic frames can.
FINAL DECISION: PROCEED_TO_MULTI_SPECIES_BASELINES
```

That decision applies to the Atlantic-style tables that repeat one species list and store `NUM = 0`: Florida Keys, Puerto Rico, USVI, and Flower Garden Banks. It does not apply to the Pacific downloads or to OBIS.

## Commands

```text
python3 scripts/acquisition/download_ncrmp_regions.py
python3 scripts/acquisition/discover_latest_survey_data.py
python3 scripts/acquisition/download_obis_recent.py
python3 scripts/preprocessing/build_evidence_catalog.py
python3 scripts/modeling/rank_regional_readiness.py
python3 scripts/acquisition/update_ocean_forecast.py
```

`make discover-data` is the same discovery script.

## What the new tables showed

Puerto Rico 2023: 248 events, 137,945 rows, one species list of 481 codes, 130,575 zeros.  
USVI 2023: 562 events, 318,821 rows, one species list of 481 codes, 264,278 zeros.  
Flower Garden Banks 2024: 38 events, 7,389 rows, one species list of 103 codes, 5,937 zeros.  
Hawaii 2024, American Samoa 2023, CNMI/Guam 2022, and PRIAs 2023: positive `COUNT` rows only. No zero counts in those files. Replicate id was not in the downloaded column set, so a Pacific event key is not verified.

Those Pacific surveys are not the same protocol as the Atlantic `NUM` tables. They stay in separate files.

## Git

Raw survey files, OBIS JSON, and SST snippets are under `data/raw/` and are ignored. Manifests, scripts, and these audit notes are safe to commit. Do not commit coordinates.

## Next action

Fit the same spatial-block detection baseline already used for foureye butterflyfish on the Puerto Rico 2023 frame, for one common species that is on that year’s species list. Do not pool it with Hawaii counts, and do not treat the OBIS July records as current locations.
