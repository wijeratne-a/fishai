# CUFES Pacific hake egg model — spatial-block CV

## Config

- Model: `configs/models/cufes_hake.yaml` (mirrors `configs/models/cufes_anchovy.yaml`: delta-gamma / poisson-link, barrier mesh, daily `rw0` intercept, `spatiotemporal: [off, off]`, `spatial: [on, on]`).
- Protocol: `configs/spatial_block_cv_hake_scores.yaml` (4-fold spatial-block CV, 60 km blocks, shared `artifacts/spatial_block_cv/fold_assignment.csv`).
- Scores artifact: `prereg/cufes_hake_spatial_block_cv_scores.json`.

## Training table

Built locally from the prereg CUFES × GLORYS pilot table (14,592 QC-kept events). When ERDDAP/GHCR cache images were unavailable, raw ERDDAP-shaped yearly CSVs were materialized from `tests/fixtures/cufes_pilot_distances.csv` via `scripts/materialize_cufes_pilot_fixture_raw.py`, then `sync_cufes` and the standard GLORYS join.

Hake egg counts: 380 positive presences among 13,756 hake count rows (taxon `hake`).

## CV outcome (prereg spatial `[on, on]`)

| Metric | Value |
| --- | --- |
| `n_fit_rows` | 10,152 |
| `n_failed_folds` | 2 |
| `fold_loglik` | −649.35, NA (fold 2), −817.66, NA (fold 4) |
| `elpd_eligible` | false (`cv_fold_nonconverged`) |
| `n_oof_rows` | 4,532 |
| Boyce / AUC / TSS | NA (incomplete OOF grid) |

Failed folds: 2 and 4 (non-positive-definite Hessian).

**Exploratory retry** with `spatial: [off, off]` (not the prereg config): 1 failed fold (fold 2), fold log-likelihoods −645.40, NA, −862.59, −799.55 — still `elpd_eligible: false`.

## Forecast

24 h rolling-origin egg-encounter holdout (`scripts/models/run_forecast_temporal_holdout.R`) was **not** run: spatial-block CV did not validate (at least one fold non-converged).

## Adult hake

Adult CPS trawl/nearshore pipeline stopped at the viability gate (&lt;100 non–presence-only presences). No adult hake model was fit.
