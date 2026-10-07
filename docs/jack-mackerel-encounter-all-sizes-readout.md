# Jack mackerel encounter probability (all sizes) — model readout

**Product label (use everywhere):** jack mackerel encounter probability (all sizes).  
**Not** an adult-length model; no L50 / 250 mm gate.

Date: 2026-10-07. Branch: `cursor/fishai-adult-jack-mackerel`.  
Config: `configs/models/jack_mackerel_encounter_all_sizes.yaml`.  
CV script: `scripts/jack_mackerel_encounter_spatial_block_cv.R`.

## Data

| Stage | Jack mackerel (*Trachurus symmetricus*) encounters |
|--------|-----------------------------------------------------:|
| GCS mirror viability (pilot bbox, non–presence-only) | **305** (269 trawl + 36 nearshore) |
| Training table (`encounter` sum, all QC rows) | **305** |
| sdmTMB fit frame after mesh / covariate / duration QC | **253** presences / **536** rows |

The **198** presence figure (154 trawl + 44 nearshore) from planning assumed a different count path; this pipeline matches Phase 1 GCS viability (**305**) and the built parquet.

Length gate: **none** (`ENCOUNTER_ALL_SIZES_SPECIES` in ingestion).

## Model

- Engine: **sdmTMB** binomial **encounter-only** (`response.type: encounter_binomial`).
- Same adult CPS covariate stack and mesh/barrier settings as other pilot CPS models (GLORYS, 60 km range guess, 9 km cutoff).
- Spatial-block CV: **60 km** blocks, **4** folds, seed **20260928** (`artifacts/spatial_block_cv/adult_cps_fold_assignment.csv`).

## Spatial-block CV scores

Artifact: `artifacts/models/jack_mackerel_encounter_all_sizes/spatial_block_cv_scores.json`.

| Metric | Value |
|--------|------:|
| ELPD | **NA** (ineligible) |
| `elpd_eligible` | **false** |
| Reason | `cv_fold_nonconverged` |
| Failed folds | **1** (fold **4**: non-positive-definite Hessian) |
| Fold log-lik (1–3) | −80.83, −76.36, −166.87 |
| Fold log-lik (4) | NA |
| OOF AUC / TSS / Boyce | NA (incomplete OOF grid) |

Folds **1–3** fit with PD Hessians; **fold 4** fails under the same spec (rw0 intercept time random walk + spatial field on the fold-4 training set). Full-data refit on all rows **does** reach a PD Hessian; the failure is specific to the fold-4 holdout split.

## Verdict

**Did not validate** under FishAI ELPD rules (all folds must converge with PD Hessian).  
**24 h forecast check not run** (requires a validated model). The repo’s rolling-origin 24 h workflow is implemented for **CUFES egg** models (`run_forecast_temporal_holdout.R`), not for this CPS encounter product; CUFES jack egg remains blocked on ERDDAP 504 in this environment.

## Legacy adult (250 mm) attempt

Documented in `docs/adult-jack-mackerel-model-readout.md` (**24** presences after gate — abandoned per pivot).
