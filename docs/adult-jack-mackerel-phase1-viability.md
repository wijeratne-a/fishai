# Adult jack mackerel (*Trachurus symmetricus*) — Phase 1 viability gate

Date: 2026-10-07. Branch: `cursor/fishai-adult-jack-mackerel`. Data: public NOAA SWFSC CPS Life History tables (GCS mirror of ERDDAP source files; oceanview ERDDAP returned HTTP 504 during this run).

## Pilot bounding box

From `data/SOURCES.yaml` → `pilot.bbox`: lat 32.0–35.0°N, lon −121.0–−117.0°E.

## Viability gate (non–presence-only presences)

| Source | Non–presence-only presences | Notes |
|--------|----------------------------:|-------|
| Mid-water trawl haul catch | **269** | `presenceOnly=Y` rows for this species in pilot: **0** |
| Nearshore purse-seine set catch | **36** | No presence-only flag in source |
| **Total** | **305** | |

**Gate verdict: PROCEED** (305 ≥ 150; not marginal).

Species label in source files: `Trachurus symmetricus` (ITIS TSN 168586).

## Coordinate check (pilot trawl presences)

Latitude 32.02–34.82°N; longitude −120.99–−117.08°E (within pilot bbox).

## Specimen length evidence (pilot; for L50 cutoff followup)

| Source | Specimens in pilot | Length field populated |
|--------|-------------------:|------------------------|
| Trawl specimens | 3,607 | `forkLength_mm`: 3,603; `standardLength_mm`: 0 |
| Nearshore specimens | 526 | `fork_length`: 526; `standard_length`: 0 |

Adult gate will need fork-length semantics for this species unless standard length is added in ingestion mapping.

## Staging

Full public mirror CSVs downloaded locally under `data/raw/gcs_mirror/` (git-ignored). Re-count:

```bash
python3 scripts/count_species_viability.py --local-dir data/raw/gcs_mirror
```

## Blocked / pending

- **Phase 2+:** Awaiting your **adult L50 (or fork-length) cutoff** before building the training table.
- **ERDDAP:** Time-bounded oceanview/coastwatch tabledap requests timed out or 504; ingestion for this species should use the NOAA GCS mirror (`nmfs_odp_swfsc` bucket) until ERDDAP is healthy.
