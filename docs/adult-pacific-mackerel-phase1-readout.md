# Adult Pacific mackerel — Phase 1 (data + viability gate)

Species: **Pacific mackerel** (*Scomber japonicus*, ITIS TSN 172409)  
Branch: `cursor/fishai-adult-pacific-mackerel`  
Pilot bbox: `data/SOURCES.yaml` → `pilot` (32–35°N, 121–117°W)

## Data ingest

| Source | ERDDAP | Outcome |
|--------|--------|---------|
| Trawl haul catch | `FRDCPSTrawlLHHaulCatch` | **504 Gateway Timeout** on yearly oceanview subsets (pilot bbox) |
| Trawl specimens | `FRDCPSTrawlLHSpecimen` | Not attempted after haul 504 |
| Nearshore set catch | `FRDCPSNearshoreSetCatch` | Not attempted (same ERDDAP risk) |
| Nearshore specimens | `FRDCPSNearshoreSpecimen` | Not attempted |

**Fallback (public NOAA GCS mirror, InPort item 20693):**  
`scripts/sync_adult_cps_from_gcs_mirror.py` → `src/fishai/ingestion/adult/gcs_mirror.py`

Processed pilot counts after GCS sync:

| Table | Pilot rows |
|-------|------------|
| Trawl hauls | 597 |
| Trawl catch rows | 5,630 |
| Nearshore sets | 189 |
| Nearshore catch rows | 529 |
| Trawl specimens (length) | 26,628 |
| Nearshore specimens (length) | 10,876 |

Raw CSVs and parquets stay under `data/` (git-ignored). Sync summary: `data/processed/adult_cps_gcs_mirror_sync.json` (local only).

## Viability gate — non–presence-only presences

Command: `python3 scripts/count_cps_species_viability.py --scientific-name 'Scomber japonicus'`

| Metric | Count |
|--------|------:|
| Trawl catch rows (species) | 122 |
| Trawl presence-only excluded | 0 |
| Trawl non–presence-only **presences** | **122** |
| Nearshore catch rows (species) | 94 |
| Nearshore non–presence-only **presences** | **94** |
| **Total non–presence-only presences** | **216** |

**Verdict: viable — proceed** (≥150; not marginal).

## Staging for Phase 2 (awaiting L50 cutoff)

Specimen standard/fork length available in pilot bbox for *S. japonicus*:

| Source | Specimens | Events with lengths | Length (mm) min / median / max |
|--------|----------:|--------------------:|-------------------------------:|
| Trawl | 1,040 | 116 | 47 / 170 / 395 |
| Nearshore | 1,535 | 93 | 118 / 223 / 383 |

Coordinate filtering uses the pilot bbox above; no raw coordinates committed.

## Blocked / next gates

- **Phase 2:** waiting on **adult L50 (standard length) cutoff** before building the training table and running GLORYS join + sdmTMB fit/CV.
- **GLORYS:** Copernicus join not run in Phase 1; will report **blocked** if `COPERNICUSMARINE_*` credentials are absent at join time (no vault/credential hunting).

## Data rules

Public anonymous data only; implied-zero and presence-only exclusion unchanged from the adult CPS scaffold; no harvest advice or live tracking implied.
