# Adult Pacific hake — Phase 1 viability gate

Date: 2026-10-07. Branch: `cursor/fishai-adult-pacific-hake`. Target: *Merluccius
productus* (Pacific hake). Pilot bbox: `data/SOURCES.yaml` → `pilot.bbox` (32–35°N,
121–117°W).

## Data acquisition

| Dataset | Primary URL | This run |
|---|---|---|
| Trawl haul catch | ERDDAP `FRDCPSTrawlLHHaulCatch` | **HTTP 504** on `oceanview.pfeg.noaa.gov` (quarterly pilot-bbox probes) |
| Nearshore set catch | ERDDAP `FRDCPSNearshoreSetCatch` | Not reached (same ERDDAP outage pattern) |
| Trawl / nearshore specimens | ERDDAP specimen tabledaps | Staged via GCS mirror (below) |

**Fallback (public):** SWFSC FRD CSV distributions on NOAA Open Data Platform GCS  
`https://storage.googleapis.com/nmfs_odp_swfsc/Fisheries%20Resources%20Division/`  
(files `CPS_Trawl_LifeHistory_*.csv`, last modified 2025-05-20 in bucket metadata).  
Raw CSVs are **not** committed (`data/raw/` is git-ignored).

## Viability rule

Count **non–presence-only presences** in the pilot bbox:

- **Trawl:** `presence_only != Y` and positive `subsample_count` and/or catch weight fields.
- **Nearshore:** positive `total_number` and/or `total_weight_kg` (no presence-only flag).

| Threshold | Action |
|---:|---|
| &lt; 100 presences | **STOP** — species not viable |
| 100–150 | Proceed, flag marginal |
| ≥ 150 | Proceed |

## Exact counts (pilot bbox)

| Source | Metric | Count |
|---|---|---:|
| Trawl haul catch (GCS) | Total catch rows in file | 26,417 |
| Trawl | *M. productus* rows (all regions) | 353 |
| Trawl | Presence-only *M. productus* rows in pilot | 4 |
| Trawl | **Non–presence-only presences (pilot)** | **57** |
| Nearshore set catch (GCS) | Total catch rows in file | 1,496 |
| Nearshore | *M. productus* rows (all regions) | 5 |
| Nearshore | **Presences (pilot)** | **1** |
| **Combined** | **Non–presence-only presences (pilot)** | **58** |

**Verdict: species not viable** (&lt; 100). Phases 2–3 (training table, sdmTMB fit/CV,
24h forecast check) are **not** executed pending a different species or domain.

Reference artifact: `configs/species/adult_pacific_hake_viability_gate.json`.

## Coordinate and specimen staging (productive wait)

- All **58** combined presences fall inside the pilot bbox by construction (lat/lon filter).
- **Specimen length data (GCS, not adult-gated):**
  - Trawl specimens: 2,492 *M. productus* records file-wide; **731** in pilot bbox; **2,490**
    with at least one length field (mostly `forkLength_mm` / `totalLength_mm`; only **28** with
    `standardLength_mm` in file-wide hake specimens).
  - Nearshore specimens: **120** file-wide; **1** in pilot; **0** with length in that pilot row set.
- **L50 cutoff:** awaiting your follow-up (required before any adult training table build).

## GLORYS / Copernicus

`COPERNICUSMARINE_SERVICE_USERNAME` and `COPERNICUSMARINE_SERVICE_PASSWORD` are present in
this environment; join was not run because the viability gate stopped the pipeline.

## Compliance

Public anonymous data only; no coordinates or raw survey rows committed; no harvest advice or
live-tracking claims.
