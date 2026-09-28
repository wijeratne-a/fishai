# Repository integrity report

**As of:** 2026-09-25  
**Scope:** Light imports of `scripts/`, `models/`, `evaluation/`, `labels/`; Makefile targets; schema and path references.  
**Policy:** No edits to files owned by other workstreams. No model refits.

## Summary

| Check | Result |
|---|---|
| Makefile python targets | 9/9 paths exist |
| Light imports | 29 modules OK; 0 import failures |
| Root `schemas/*.json` | Present; no broken consumer refs to missing root schema files |
| Broken references logged | See `BROKEN_REFERENCES.csv` (12 actionable / planned; 3 info) |
| Interface mismatches | See `INTERFACE_MISMATCHES.csv` (7 rows) |

## Makefile

All targets under `.PHONY` invoke existing scripts:

- `discover-data` → `scripts/acquisition/discover_latest_survey_data.py`
- `update-structured-surveys` → `scripts/acquisition/download_ncrmp_regions.py`
- `update-recent-occurrences` → `scripts/acquisition/download_obis_recent.py`
- `update-ocean-nowcast` → `scripts/acquisition/update_current_ocean_data.py`
- `update-ocean-forecast` → `scripts/acquisition/update_ocean_forecast.py`
- `validate-data` → `scripts/validation/validate_noaa_rvc.py`
- `build-evidence-catalog` → `scripts/preprocessing/build_evidence_catalog.py`
- `rank-species` → `scripts/modeling/rank_regional_readiness.py`
- `project-status` → `scripts/project_status.py`

Note: Atlantic frame validation (`validate_atlantic_frames.py`) is documented in multi-species execution notes but is not a Makefile target. That is an interface mismatch, not a missing file.

## Imports

Candidate Python modules under `scripts/`, `models/`, `evaluation/`, and `labels/` were AST-scanned for dependency imports and light-executed. No broken third-party or local imports were found in this pass. Acquisition scripts that may hit the network were still importable because work runs under `if __name__ == "__main__"` guards.

## Highest-value broken reference

`scripts/project_status.py` reads `data/manifests/source-update-state.json`, but the tracked manifest is `data/manifests/update-state.json`. Status therefore reports `RECENT SOURCE UPDATES: UNKNOWN` even when update state exists. Fix belongs to the status/manifest owner (not applied here).

## Schema files

- Canonical FishAI contracts under `schemas/` resolve.
- Legacy geospatial schemas under `artifacts/geospatial_data_engineer/schemas/` exist but are cited as `schemas/...` from artifact markdown, which fails as a repo-root relative path.

## Safe fixes

Documented in `SAFE_FIXES.md`. No foreign files were modified. Optional local notes under this directory only.
