# Adult CPS training table validation

Date: 2026-10-06. Branch: `cursor/fishai-adult-training-table-fbde`. Pilot bbox from
`data/SOURCES.yaml` (`pilot.bbox`: 32–35°N, 121–117°W).

## Disclosure (training-table metadata)

Adult specimens were retained only if standard length >= 160 mm (Pacific sardine) or >= 98 mm
(northern anchovy). These cutoffs are the lengths at 50% maturity (L50): sardine 160.6 mm SL
from the 2024/2025 Pacific sardine stock assessment (Kuriyama et al. 2024; n=4,561 females,
histological staging), consistent with Dorval et al. (2015) L50=150.9 mm SL; anchovy 98.2 mm SL
from the SCB-pooled 2021 central-subpopulation northern anchovy assessment. A hard L50 cutoff is
the convention in both assessments' spawning-biomass calculations; limited juvenile contamination
remains by design. Presence-only records were excluded. Absences are implied zeros from
fully-enumerated hauls/sets only.

## Adult length gate (`ADULT_MIN_LENGTH_MM`)

| Species | Minimum SL (mm) | Basis |
|---|---:|---|
| *Sardinops sagax* | 160 | L50 160.6 mm SL (2024/2025 stock assessment) |
| *Engraulis mordax* | 98 | L50 98.2 mm SL (2021 central-subpopulation assessment) |

Per-event **median** standard length among retained specimens must meet the cutoff for a
**presence** row. Implied-absence rows do not require specimen evidence.

## Implied-zero rule (replaces empty zero-frame YAMLs)

For each trawl haul or nearshore set that has **≥1 enumerated catch row**, any pilot target
species (*Sardinops sagax*, *Engraulis mordax*) with **no non–presence-only catch row** in that
event receives `encounter=0` (`absence_evidence=implied_zero_enumerated_frame`).

**Enumeration criteria**

- **Trawl:** `presence_only != 'Y'` **and** `subsample_count` is not null.
- **Nearshore:** `total_number` is not null.

**Excluded entirely:** all `presence_only=Y` trawl rows (not used for enumeration or presences).

### Evidence for full catch enumeration (2021–2026 validation slice)

In the 2021–2026 pilot-bbox validation slice, **all 174 trawl hauls** and **all nearshore sets**
with enumerated multi-species catch also recorded non-target taxa (squid, krill, pyrosomes,
mackerel, herring, jellyfish, etc.). That pattern is consistent with complete catch enumeration
on those events, so implied zeros are limited to hauls/sets meeting the enumeration criteria above
rather than per-cruise YAML gates (`config/cps_*_zero_frame_evidence.yaml` remain empty).

Prior build excluded **6,773** presence-only trawl rows; the same rule applies here.

## Public inputs (ERDDAP)

| Dataset | URL |
|---|---|
| Trawl haul catch | https://oceanview.pfeg.noaa.gov/erddap/tabledap/FRDCPSTrawlLHHaulCatch.csv |
| Trawl specimens | https://oceanview.pfeg.noaa.gov/erddap/tabledap/FRDCPSTrawlLHSpecimen.csv |
| Nearshore set catch | https://oceanview.pfeg.noaa.gov/erddap/tabledap/FRDCPSNearshoreSetCatch.csv |
| Nearshore specimens | https://oceanview.pfeg.noaa.gov/erddap/tabledap/FRDCPSNearshoreSpecimen.csv |

`FRDCPSTrawlLHLengthFrequency` is **not** used (deprecated; zero sardine/anchovy in prior audit).

Nearshore catch uses **half-year** time windows on the **oceanview** mirror when coastwatch drops
connections.

## GLORYS join

Training covariates follow `src/fishai/ingestion/physics/cufes_training_covariates.py` (point
events for purse-seine sets; segment mean for trawl tows). Join runs only when
`COPERNICUSMARINE_SERVICE_USERNAME` and `COPERNICUSMARINE_SERVICE_PASSWORD` are set in the
environment. If absent, the build writes `adult_cps_events.parquet` and a biology-only observation
table without Copernicus fields.

## Validation checklist

Row counts by species, source, and encounter; effort completeness; pilot bbox; deduplication;
ITIS TSN sanity — recorded in `data/processed/adult_cps/adult_cps_build_summary.json` after a
local build (not committed).
