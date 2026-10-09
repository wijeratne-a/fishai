# FRAM groundfish-trawl pelagic bycatch — live ingestion validation (2026-10-06)

Validation run for PR #41 (`cursor/fishai-fram-ingestion-210f`). Reproduces the prior stranded validation with commit + push on this branch.

## Source labeling (mandatory)

| Rule | Application |
|------|-------------|
| **Training role** | **Adult corroboration only** — not a primary presence–absence frame |
| **Gear / survey bias** | Bottom-trawl groundfish survey; sardine/anchovy are **pelagic bycatch** |
| **Zeros** | **Presence-only** catch rows; **no implied zeros** emitted |
| **Data access** | **Public anonymous** FRAM REST only (no credentials, vault, or secret tooling) |
| **Spatial policy** | **10 km minimum** public aggregation applies downstream; this doc reports **counts only** (no coordinates or raw rows committed) |
| **Threatened species** | Standard masking rules apply in product layers (not exercised here) |
| **Out-of-domain** | Cells/rows outside model domain → **UNKNOWN** at inference (not part of this ingest QC) |

## API configuration

| Item | Value |
|------|--------|
| Base URL | `https://www.webapps.nwfsc.noaa.gov/trips/api/v1/source/` |
| Catch layer | `trawl.catch_fact` |
| Haul layer | `trawl.operation_haul_fact` |
| Project filter | `Groundfish Slope and Shelf Combination Survey` |
| Species | `Engraulis mordax`, `Sardinops sagax` |
| Window | Survey years **2021–2025** via `date_dim$year` (year also derived from `trawl_id` prefix for QC rows) |
| Legacy path | **Not used** — `www.nwfsc.noaa.gov/data/api` serves an app shell |

### Variable request / silent-drop guard

The FRAM selection API **silently omits** unrecognized variable names. The fetch layer calls `validate_response_variables()` on the first row of each non-empty response and raises `FramVariableDropError` if any requested key is missing.

**Catch variables requested:** `trawl_id`, `field_identified_taxonomy_dim$scientific_name`, `vessel`, `tow`, `project`, `performance`, `total_catch_wt_kg`, `total_catch_numbers`, `cpue_kg_per_ha_der`, `depth_m`, `station_invalid`.

**Haul variables requested:** `trawl_id`, `vessel`, `tow`, `project`, `performance`, `datetime_utc_iso`, `area_swept_ha_der`, `latitude_dd`, `longitude_dd`, `gear_start_latitude_dd`, `gear_start_longitude_dd`, `gear_end_latitude_dd`, `gear_end_longitude_dd`, `depth_hi_prec_m`, `sampling_start_hhmmss`, `sampling_end_hhmmss`, `station_invalid`.

All live fetches for 2021–2025 completed without variable-drop errors.

## Pipeline executed

```text
sync_fram_groundfish_trawl(date(2021,1,1), date(2025,12,31), fetch=True)
```

Raw JSON under `data/raw/nwfsc_fram_groundfish_trawl/` (gitignored). Processed parquet + QC JSON under `data/processed/nwfsc_fram_groundfish_trawl/` (gitignored).

Unit tests (synthetic fixtures, no network):

```text
python -m unittest tests.ingestion.test_nwfsc_fram_groundfish_trawl
```

**Result:** 8/8 passed.

## Live cross-check (2026-10-06)

| Metric | Expected | Observed | Match |
|--------|----------|----------|-------|
| Catch rows kept | 117 | 117 | yes |
| *Engraulis mordax* (ITIS 161828) | 102 | 102 | yes |
| *Sardinops sagax* (ITIS 161729) | 15 | 15 | yes |
| Catch rows read | 117 | 117 | yes |
| Tows kept (unique haul events) | 115 | 115 | yes |
| Hauls indexed (full project-year haul fact) | 3,462 | 3,462 | yes |
| Catch → haul join | 100% (117/117) | 117/117 | yes |
| CPUE (`cpue_kg_per_ha_der`) present | 115/117 | 115/117 | yes |
| CPUE missing (flagged, rows kept) | 2 | 2 | yes |
| Invalid coordinates (haul lat/lon QC) | 0 | 0 | yes |
| Catch rows in SCB pilot bbox (32–35°N, 121–117°W) | 36 | 36 | yes |
| Tows in SCB pilot bbox | — | 36 | — |

### Survey year breakdown (from `trawl_id` prefix)

| Year | Catch rows |
|------|------------|
| 2021 | 29 |
| 2022 | 23 |
| 2023 | 32 |
| 2024 | 18 |
| 2025 | 15 |

### QC drops

| Rule | Count |
|------|-------|
| `trawl_id_invalid` | 0 |
| `species_invalid` | 0 |
| `haul_join_missing` | 0 |
| `coord_invalid` | 0 |
| `performance_excluded` | 0 |
| `year_mismatch` | 0 |
| `cpue_missing` | 2 |

## Conclusion

Live FRAM trips API ingestion for West Coast groundfish combo survey pelagic bycatch (2021–2025) **matches the 2026-10-06 reference counts exactly**. The pipeline enforces variable presence, presence-only bycatch semantics, and corroborating-source metadata. No material discrepancies were found; no code changes were required for this validation pass.
