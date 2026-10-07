# Adult Pacific sardine encounter-only (binomial) readout

Branch: `cursor/fishai-sardine-encounter-only-1802`. Base: `cursor/fishai-adult-sardine-fit`.

## Product scope (mandatory)

This model estimates **encounter probability only** (presence/absence on enumerated CPS trawl and
nearshore set frames with L50 length gates). It does **not** predict catch rate, biomass density,
positive-weight gamma components, live fish tracking, real-time positions, or harvest advice.
Out-of-domain covariate combinations are masked to **UNKNOWN** in map products (same OOD rules as
egg/adult configs). Training never uses presence-only rows; events below the **10 km** minimum
track length are excluded; threatened species remain masked upstream.

## Model specification

| Field | Value |
|---|---|
| Family | `binomial`, logit link |
| Engine | `sdmTMB`, barrier mesh |
| Spatial / spatiotemporal | `[off, off]` |
| Smoothers | Six covariates, `k = 3` (same as delta encounter component) |
| Time | Daily `rw0` intercept on dense-remapped `time_idx` |
| Effort | `log(effort_duration_min)` offset |
| CV | 4 spatial blocks, **60 km**, seed **20260928**, folds **sequential** (`n_workers = 1`) |

Config: `configs/models/adult_cps_sardine_encounter.yaml`  
CV driver: `scripts/adult_sardine_spatial_block_cv.R`  
Scores path: `artifacts/models/adult_sardine_encounter/spatial_block_cv_scores.json`

## Training table rebuild (2026-10-07)

Command: `python3 scripts/build_adult_cps_training_table.py` (no `--dry-run`).

| Step | Result |
|---|---|
| CPS ERDDAP ingest (`scripts/rebuild_adult_cps_inputs.py`) | **Blocked** — `oceanview.pfeg.noaa.gov` / Akamai returns HTTP 504 or HTML error bodies from this cloud VM (TLS connects; no CSV payload). No `data/processed/adult_cps/*.parquet` present locally. |
| GLORYS join | **Not reached** — `COPERNICUSMARINE_*` credentials are present, but physics events table is empty without CPS inputs. |

Expected sardine frame (from prior delta run on the same public inputs): **456** rows (**58** presences).

## Spatial-block CV (2026-10-07)

**Not executed in this environment.** R stack on Ubuntu 4.3.3 could not complete `renv::restore`
(`sdmTMBextra` → `tmbstan` requires R ≥ 4.5 per lockfile). Without processed training parquet,
fold fitting cannot run.

When inputs and the project R 4.5 Docker image are available locally:

```bash
python3 scripts/rebuild_adult_cps_inputs.py
python3 scripts/build_adult_cps_training_table.py
Rscript scripts/adult_sardine_spatial_block_cv.R \
  configs/models/adult_cps_sardine_encounter.yaml \
  artifacts/models/adult_sardine_encounter/spatial_block_cv_scores.json
```

Protocol requirements unchanged: **all four folds** must converge for eligible ELPD; report
per-fold log-likelihood, summed ELPD, and full out-of-fold **AUC / TSS / Boyce** (moving-window
`cbi_continuous`, never equal-width bins).

## Code changes (this branch)

- `fit_binomial_engine` / `fit_model_engine` and binomial holdout log-likelihood in `src/models/R/`.
- Encounter scoring uses logistic transform on the binomial linear predictor (with effort offset).
- Default CV script targets the encounter-only config and artifact directory.
