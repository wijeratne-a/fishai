# Adult market squid (`Doryteuthis opalescens`) — Phase 1 readout

Branch: `cursor/fishai-market-squid-pipeline-86df`.

## Data acquisition

| Source | ERDDAP attempt | Fallback |
| --- | --- | --- |
| Trawl haul catch | `oceanview.pfeg.noaa.gov` → HTTP **504** (yearly window) | Public GCS mirror (InPort 20693) |
| Trawl specimens | (not attempted after 504) | Same GCS mirror |
| Nearshore catch + specimens | Staged via GCS mirror directly | `CPS_Trawl_LifeHistory_Nearshore_*.csv` |

GCS base (anonymous): `https://storage.googleapis.com/nmfs_odp_swfsc/Fisheries%20Resources%20Division/`

InPort CSV column names are normalized in `src/fishai/ingestion/adult/inport_csv.py` before the standard CPS transforms. Raw CSV and processed parquet remain **gitignored** (`data/raw/`, `data/processed/`).

## Pilot bbox (`data/SOURCES.yaml` → `pilot`)

| Field | Value |
| ---: | ---: |
| lat | 32.0 – 35.0 °N |
| lon | −121.0 – −117.0 °E |

Coordinate checks: trawl haul `lat`/`lon` and nearshore set `latitude`/`longitude` joined to catch rows for bbox filtering.

## Viability gate (non–presence-only presences, pilot bbox)

Counts from `scripts/count_adult_species_viability.py` → `prereg/market_squid_viability_gate.json`.

| Source | Catch rows in bbox | Non–presence-only presences |
| --- | ---: | ---: |
| CPS trawl | 5,630 | **291** |
| CPS nearshore | 529 | **18** |
| **Total** | — | **309** |

**Gate:** **proceed** (≥150; not marginal).

Species aliases counted: `Doryteuthis opalescens`, `Loligo opalescens`.

## Specimen length availability (pre–L50 cutoff)

| Source | Matched specimen length rows | Events with median length |
| --- | ---: | ---: |
| Trawl | 26 | 4 |
| Nearshore | 0 | 0 |

Trawl lengths for market squid in mirror (all areas, not bbox-filtered in this table): median **98.5 mm**, range **50–115 mm** (n=26). Adult L50 cutoff **not applied** until follow-up.

## Phase 2 blockers / status

- **Awaiting user L50 (standard length) cutoff** before `ADULT_MIN_LENGTH_MM` and training-table build.
- GLORYS join: requires `COPERNICUSMARINE_*` credentials in environment (check at Phase 2 start; do not hunt secrets).

## Next steps (after cutoff follow-up)

1. Add `Doryteuthis opalescens` to adult CPS species constants + implied-zero frame.
2. Build training table (`scripts/build_adult_cps_training_table.py` pattern).
3. GLORYS join, sdmTMB hurdle fit, 60 km spatial-block CV (seed 20260928, 4 sequential folds).
4. If validated: 24 h forecast proxy check per `prereg/cufes_forecast_temporal_holdout_design.md`.
