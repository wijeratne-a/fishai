# Adult Pacific herring encounter model readout

Branch: `cursor/fishai-adult-pacific-herring`. Species: *Clupea pallasii*.

## Disclosure (length gate)

Adult specimens were retained only if standard length >= 170 mm (Pacific herring, *Clupea pallasii*). This is the midpoint of the published maturity band of 16.5–17.8 cm at 2–3 years of age (Love 1996); it is a judgment call within that band, not a fitted L50.

## Spatial frame

The SCB pilot bbox (32–35°N) contains **zero** herring presences in public CPS data. Modeling uses the CPS survey overlap domain **32–45°N, 125–117°W** (`config/adult_pacific_herring_domain.json`). This is not live tracking or harvest advice.

## Data

Public NOAA GCS mirrors (`src/fishai/ingestion/adult/gcs_mirror.py`); ERDDAP oceanview returned 504 on year windows during Phase 1.

## Training table (dry-run biology + domain)

| Metric | Count |
|---|---:|
| Adult presences (encounter=1) | **33** (31 trawl + 2 nearshore) |
| Implied absences | 2,045 |
| Physics events | 2,077 |
| GLORYS unique event-days | 771 (75 subset batches) |

Build: `scripts/sync_cps_gcs_herring_processed.py` → `scripts/build_adult_herring_training_table.py`.

## Model (redirect: encounter-only)

- **Family:** binomial encounter (`response.type: encounter_binomial`), **not** delta-gamma hurdle.
- **Engine:** sdmTMB, `log(effort_duration_min)` offset, daily `rw0` intercept, `spatiotemporal: off`.
- **Spatial:** `[on]` single component; barrier mesh **disabled** (domain extends north of SCB shoreline asset).
- Config: `configs/models/adult_cps_herring.yaml`.

## Spatial-block CV (planned)

- 60 km blocks, seed `20260928`, **4 folds sequential** (`scripts/adult_herring_spatial_block_cv.R`).
- Scores path: `artifacts/models/adult_herring/spatial_block_cv_scores.json` (written after GLORYS join completes and R CV runs).

## 24h forecast validation

Runs only if CV validates (proxy vs persistence + DOY climatology on AUC/TSS); design per `prereg/cufes_forecast_temporal_holdout_design.md`.

## Phase status

| Step | Status |
|---|---|
| GCS ingest + 170 mm gate | Done (33 adult presences) |
| GLORYS join | In progress (75 Copernicus subset batches) |
| Binomial CV + scores | Pending training table |
| 24h forecast check | Pending CV |
