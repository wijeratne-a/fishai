# Adult Pacific sardine encounter model readout

Branch: `cursor/fishai-adult-sardine-simple-hurdle`. Training table rebuilt locally from
public SWFSC InPort CSV mirrors (GCS) plus Copernicus GLORYS covariates.

## Question and labels

This model estimates **adult spawning encounter evidence** from SWFSC CPS trawl and
nearshore set catch (L50 length gates; implied zeros on enumerated frames only). Outputs
describe **survey-based adult/spawning encounter likelihood**, not live fish tracking,
real-time positions, or harvest advice.

## Model specification (simplified hurdle attempt)

- Engine: `sdmTMB` Poisson-link **delta-gamma** hurdle (same as CUFES egg pilot)
- **Spatial / spatiotemporal:** `[off, off]` / `[off, off]` (non-spatial refit)
- **Fixed effects:** shared **linear** terms on all six z-scored covariates (no smooths)
  — reduces positive-component parameters versus six `k = 3` smooths (~58 presences)
- Barrier mesh, daily `rw0` intercept, 60 km spatial blocks, seed `20260928` unchanged

Note: `sdmTMB` requires identical main-effects formulas on both delta components when
smoothers are present, so encounter and positive components share the linear spec.

Config: `configs/models/adult_cps_sardine.yaml`

## Spatial-block CV

- Block size: **60 km**
- Folds: **4**, sequential (`n_workers = 1`)
- Fold assignment on `adult_cps_events.parquet` (regenerated for this rebuild)

Scores: `artifacts/models/adult_sardine/spatial_block_cv_scores.json`

## Training table (local rebuild)

`python3 scripts/build_adult_cps_training_table.py` after staging public CPS CSV inputs:

| Check | Count |
|---|---:|
| Physics events (pilot bbox) | 709 |
| Training rows kept (all species, GLORYS QC) | 883 |

Pacific sardine modeling frame after species filter and positive effort: **458 rows**
(**59** presences).

## Spatial-block CV results

| Fold | Holdout log-likelihood | Status |
|---:|---:|---|
| 1 | -73.34 | OK |
| 2 | -120.43 | OK |
| 3 | -325.41 | OK |
| 4 | -69.77 | OK |

**Summed ELPD:** **-588.95** (eligible; all four folds converged).

**Out-of-fold discrimination (moving-window Boyce):**

| AUC | TSS @ 0.5 | Boyce |
|---:|---:|---:|
| 0.677 | 0.195 | 0.754 |

Fold assignment: `artifacts/spatial_block_cv/adult_cps_fold_assignment.csv`.
