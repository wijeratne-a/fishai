# Pacific herring encounter probability (all sizes) — model readout

Branch: `cursor/fishai-adult-pacific-herring`. Species: *Clupea pallasii*.

**Product label (use everywhere):** Pacific herring encounter probability (all sizes). This is **not** an adult-length or harvest-advice model.

## Spatial frame

- CPS ingest and biology domain: **32–45°N, 125–117°W** (`config/adult_pacific_herring_domain.json`, `length_gate: false`).
- **GLORYS × WCOFS covariates** are built on the **SCB pilot physics footprint** (`data/derived/physics/wcofs_h_glorys_pilot.zarr`), which effectively supports events near **32–35°N** only.

## Biology counts (all sizes, no length gate)

| Source | encounter=1 | encounter=0 (incl. implied) |
|---|---:|---:|
| Trawl | 81 | 1,783 |
| Nearshore | 15 | 271 |
| **Total presences** | **96** | — |

Reconciliation vs a planning figure of 111 (83+28): this GCS mirror snapshot and bbox filter at ingest yield **96** presences on synced parquets; see `config/adult_pacific_herring_training_counts.json`.

## Training table after GLORYS join

Build: `scripts/sync_cps_gcs_herring_processed.py` → `scripts/build_adult_herring_training_table.py` (2026-10-07).

| Metric | Value |
|---|---:|
| Physics events | 2,149 |
| Rows after covariate QC (kept) | 756 |
| **Presences kept (encounter=1)** | **0** |
| Unique events dropped (missing covariate) | 1,384 |

**Blocker:** All **96** presence events lie **north of ~35°N** (OR/WA/ northerly CA). Every kept row is an absence in **32–35°N** where WCOFS bathymetry and GLORYS subsetting succeed. There are **zero** herring presences in the SCB pilot box with usable physics — same viability conclusion as Phase 1, extended only in catch geography, not in covariate coverage.

Outputs: `data/processed/adult_cps_herring/herring_all_sizes_training_table.parquet` (local; gitignored).

## Model spec (encounter-only binomial)

- **Family:** binomial encounter (`response.type: encounter_binomial`).
- **Engine:** sdmTMB, `log(effort_duration_min)` offset, daily `rw0` intercept, `spatiotemporal: off`, spatial `[on]`, barrier mesh **off**.
- Config: `configs/models/adult_cps_herring.yaml`.

## Spatial-block CV (4 folds, sequential)

Script: `scripts/adult_herring_spatial_block_cv.R`  
Scores: `artifacts/models/adult_herring/spatial_block_cv_scores.json`

| Metric | Result |
|---|---|
| `n_fit_rows` | 726 |
| `n_presence_rows` | **0** |
| ELPD | NA (`elpd_eligible: false`, `cv_fold_failed`) |
| OOF AUC / TSS / Boyce | NA |
| Failed folds | 2 — training fold lacks both zeros and positives |

**Verdict:** CV **does not validate** (no positive class in the physics-overlap training frame). Do **not** issue forecasts from this table.

## 24h forecast validation

**Not run** — gated on CV validation; prerequisite failed.

## Phase status

| Step | Status |
|---|---|
| All-sizes ingest + domain | Done |
| GLORYS join | Done (local table) |
| Binomial CV + scores | Done — **failed** (0 presences after physics QC) |
| 24h forecast check | Skipped |
