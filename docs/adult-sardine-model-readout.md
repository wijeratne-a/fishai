# Adult Pacific sardine encounter model readout

Branch: `cursor/fishai-adult-sardine-fit`. Training table from
`cursor/fishai-adult-training-table-fbde` (public ERDDAP catch + GLORYS covariates).

## Question and labels

This model estimates **adult spawning encounter evidence** from SWFSC CPS trawl and
nearshore set catch (L50 length gates; implied zeros on enumerated frames only). Outputs
describe **survey-based adult/spawning encounter likelihood**, not live fish tracking,
real-time positions, or harvest advice.

## Model specification

Mirrors the validated CUFES egg delta pipeline (`sdmTMB` Poisson-link delta-gamma,
barrier mesh, daily `rw0` intercept). Spatiotemporal fields remain **`[off, off]`**
(OOM on 15 GiB VM). Sardine spatial random fields follow the PR #39 egg winner:
**`spatial: [off, on]`** (encounter vs positive-weight components).

## Spatial-block CV

- Block size: **60 km** (`max(mesh.cutoff_km=9, mesh.range_guess_km=60)`)
- Folds: **4**, seed **`prediction.seed: 20260928`**
- Fold assignment recomputed on **`adult_cps_events.parquet`** (species-agnostic physics events)
- Folds run **sequentially** (`n_workers = 1`)

Scores: `artifacts/models/adult_sardine/spatial_block_cv_scores.json`

## Training table validation (local rebuild)

`python3 scripts/build_adult_cps_training_table.py` (2026-10-06):

| Check | Count |
|---|---:|
| Observation rows (presences + implied absences) | 1,141 |
| Presence rows (both species) | 307 |
| Physics events (pilot bbox) | 706 |
| Training rows after GLORYS QC (all species) | 879 |

Pacific sardine modeling frame after species filter, GLORYS exclusions, and
positive effort: **456 rows** (**58** presences).

## Spatial-block CV results (2026-10-06)

| Fold | Holdout log-likelihood | Status |
|---:|---:|---|
| 1 | — | non-PD Hessian |
| 2 | -120.24 | OK |
| 3 | -234.32 | OK |
| 4 | — | non-PD Hessian |

**Summed ELPD (protocol):** not eligible (`n_failed_folds = 2`; all four folds
must converge for ELPD).

**Sum of completed fold log-likelihoods (folds 2+3 only, not a protocol ELPD):**
-354.56.

**Out-of-fold discrimination (full 4-fold):** not computed (incomplete OOF).

**Partial OOF from successful folds 2–3 only (290 holdout rows; not preregistered):**
AUC 0.631, TSS 0.192, Boyce 0.90 (moving-window `cbi_continuous`).

Fold assignment: `artifacts/spatial_block_cv/adult_cps_fold_assignment.csv`.
