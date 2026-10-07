# Adult Pacific sardine encounter model readout

Branch: `cursor/fishai-adult-sardine-off-off-refit-40b0`. Public SWFSC CPS catch
(NOAA InPort / GCS mirror when ERDDAP times out) + Copernicus GLORYS covariates.

## Question and labels

This model estimates **adult spawning encounter evidence** from SWFSC CPS trawl and
nearshore set catch (L50 length gates; implied zeros on enumerated frames only). Outputs
describe **survey-based adult/spawning encounter likelihood**, not live fish tracking,
real-time positions, or harvest advice.

## Model specification (this refit)

Mirrors the validated CUFES egg delta pipeline (`sdmTMB` Poisson-link delta-gamma,
barrier mesh, daily `rw0` intercept). **Spatiotemporal and spatial random fields are
both off:** `spatial: [off, off]`, `spatiotemporal: [off, off]` (refit after
`spatial: [off, on]` non-PD Hessian on gamma spatial fields with 58–59 presences).

## Spatial-block CV

- Block size: **60 km** (`max(mesh.cutoff_km=9, mesh.range_guess_km=60)`)
- Folds: **4**, seed **`prediction.seed: 20260928`**
- Fold assignment on **`adult_cps_events.parquet`** (706 physics events in pilot bbox after QC)
- Folds run **sequentially** (`n_workers = 1`)

Scores: `artifacts/models/adult_sardine/spatial_block_cv_scores.json`

## Training table validation (local rebuild 2026-10-07)

Sources: SWFSC FRD trawl/nearshore catch CSV from
`https://storage.googleapis.com/nmfs_odp_swfsc/Fisheries%20Resources%20Division/`
(mirror of InPort distributions; ERDDAP `oceanview.pfeg.noaa.gov` returned HTTP 504
during this run). GLORYS join via public Copernicus credentials in environment.

| Check | Count |
|---|---:|
| Observation rows (presences + implied absences) | 1,144 |
| Training rows after GLORYS QC (all species) | 883 |
| Physics events (pilot bbox, pre-covariate) | 709 |

Pacific sardine modeling frame after species filter, GLORYS exclusions, and
positive effort: **458 rows** (**59** presences) — consistent with prior ~456 / 58
within one refresh cycle.

## Spatial-block CV results — non-spatial refit (2026-10-07)

| Fold | Holdout log-likelihood | Status |
|---:|---:|---|
| 1 | −64.28 | OK |
| 2 | — | non-PD Hessian |
| 3 | — | non-PD Hessian |
| 4 | −66.99 | OK |

**Summed ELPD (protocol):** not eligible (`n_failed_folds = 2`; all four folds must
converge).

**Out-of-fold discrimination (full 4-fold):** not computed (incomplete OOF).

**Sum of completed fold log-likelihoods (folds 1+4 only, not a protocol ELPD):**
−131.27.

Per instruction, no further specification changes after this `[off, off]` refit.

Fold assignment: `artifacts/spatial_block_cv/adult_cps_fold_assignment.csv`.
