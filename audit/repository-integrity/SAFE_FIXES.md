# Safe fixes (integrity)

These fixes are recommendations only. This workstream did **not** edit files owned by other agents. If a mechanical fix is needed inside this exclusive directory, use the note files here — not patches to `scripts/`, manifests, or globe code.

## Recommended (owners elsewhere)

1. **Manifest filename for status** (`IM-001` / `BR-001`)  
   Either rename `data/manifests/update-state.json` → `source-update-state.json`, or change `scripts/project_status.py` to read `update-state.json`. Prefer one canonical name and update both sides together.

2. **Observatory script path** (`IM-003` / `BR-009`)  
   Update `observatory/artifacts/data_catalog/agent_handoff.md` to cite `observatory/scripts/build_global_catalogs.py`.

3. **Geospatial schema paths** (`IM-002` / `BR-002`–`BR-008`)  
   Point artifact docs at `artifacts/geospatial_data_engineer/schemas/…`, or add explicit “not root schemas/” wording so they are not confused with FishAI canonical contracts.

4. **Rank script status text** (`IM-004`)  
   Refresh `scripts/modeling/rank_regional_readiness.py` printed statuses to match `audit/multi-species/MODEL_RESULTS.csv` vocabulary without changing scores. Do not re-rank by holdout.

5. **Goliath species code spelling** (`IM-005`)  
   Align species docs to `EPI ITAJ` for the Florida Keys extract (keep portal `EPIITAJ` only where describing portal rules).

6. **Makefile validate alias** (`IM-006`)  
   Optional: add a `validate-atlantic-frames` target calling `scripts/validation/validate_atlantic_frames.py` without removing `validate-data`.

## Applied here

None. No owned production scripts were changed. No shim was added that could be mistaken for a production path rewrite.

## Explicitly not done

- No edits under `data/raw`, `data/manifests`, `scripts/acquisition`, or `globe/`.
- No model refit or score change.
- No claim that optional `security/SCAN_RESULT.md` must exist.
