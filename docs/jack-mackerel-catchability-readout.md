# Jack mackerel catchability (detection) sub-model — readout

**Branch:** `cursor/fishai-catchability-model`  
**Date:** 2026-10-13  
**Hypothesis:** Daylight trawl catchability bias (visual net avoidance) was conflated with absence in prior DVM-style specs. This test adds explicit **detection** terms on the **encounter (hurdle) component** only, with **habitat** physics unchanged from the validated encounter baseline.

## Data and CV protocol

| Item | Value |
|------|------:|
| Config (baseline) | `configs/models/jack_mackerel_encounter_all_sizes.yaml` |
| Fit rows (jack mackerel, all sizes) | **536** |
| Presences | **253** |
| Spatial blocks | **60 km**, EPSG:32611 |
| Folds | **4**, seed **20260928** |
| Fold assignment | `artifacts/spatial_block_cv/adult_cps_fold_assignment.csv` (regenerated from `adult_cps_events.parquet` when missing) |

Row counts are **536 / 253** on this rebuild (public GCS CPS mirror + GLORYS join), versus **539 / 254** cited in the task brief; the spec, folds, and covariate set match the validated encounter pipeline.

## Solar / diel covariates

Implemented in `src/models/R/catchability_solar.R` and attached when `model.catchability_detection.enabled: true`:

- **`solar_elevation_deg`** — NOAA-style apparent solar elevation from UTC `time` + `lat` / `lon`
- **`is_day`**, **`is_night`**, **`is_dawn_dusk`** — day (elev > 0°), night, civil twilight band (−6° < elev ≤ 6°)
- **`solar_elev_z`** — z-scored elevation for modeling

## Baseline (encounter binomial)

Same as `docs/jack-mackerel-encounter-all-sizes-readout.md`: linear GLORYS habitat covariates, spatial off, daily `rw0` intercept.

| Metric | Value |
|--------|------:|
| **OOF AUC** | **0.7622** |
| **OOF Brier** | **0.1989** |
| ELPD | −423.96 (eligible) |

Artifact: `artifacts/models/jack_mackerel_encounter_all_sizes/spatial_block_cv_scores.json`

## Candidate specs (detection vs habitat)

Both use **Poisson-link delta-gamma** (`density_delta` on `weight_kg`) so component 1 is encounter probability and component 2 is positive catch given encounter. **Spatial off** on both components (same as baseline).

### (a) Delta + solar detection — `jack_mackerel_encounter_catchability_delta.yaml`

| Layer | Terms |
|-------|--------|
| **Ecological (habitat)** — both components | `temp_3m_z`, `sal_3m_z`, `mld_z`, `sst_grad_z`, `dist_front_z`, `log_depth_z` |
| **Detection** — encounter component only | `solar_elev_z`, `is_dawn_dusk` |

### (b) Delta + depth × light — `jack_mackerel_encounter_catchability_depth_light.yaml`

| Layer | Terms |
|-------|--------|
| **Ecological (habitat)** — positive component | same six habitat terms |
| **Detection** — encounter component only | habitat six + **`log_depth_z:solar_elev_z`** |

CV script: `scripts/jack_mackerel_catchability_cv.R`

## Spatial-block CV results

Scores directory: `artifacts/models/jack_mackerel_encounter_catchability/`

| Model | OOF AUC | OOF Brier | CV status |
|-------|--------:|----------:|-----------|
| Baseline binomial | **0.7622** | **0.1989** | 4/4 folds OK |
| (a) Delta + solar | — | — | **Incomplete OOF** — fold 2 non-PD Hessian (`n_failed_folds=1`) |
| (b) Depth × light | — | — | **Incomplete OOF** — folds 1–3 non-PD Hessian (`n_failed_folds=3`) |

Comparison gate JSON: `artifacts/models/jack_mackerel_encounter_catchability/catchability_cv_comparison.json`

**Strict gate:** beat baseline on **both** AUC and Brier.

## Verdict

**FAIL** — Neither delta catchability candidate produced complete out-of-fold scores. The hurdle extension (extra detection parameters + positive component + `rw0`) did not remain numerically stable under the same 4-fold spatial blocks as the validated binomial baseline. Per task rules, **no further spec escalation** was attempted.

## Interpretation

- Separating detection onto the encounter component is the right structural test, but **this delta parameterization is not CV-valid** at current sample size.
- A lighter-weight test (encounter-only binomial with detection covariates) would not separate the observation process from habitat; it was **not** run, to respect the two-spec cap and hurdle-style requirement.

## Reproduce

```bash
python3 scripts/fetch_odp_adult_cps_bulk.py
python3 scripts/ingest_cps_from_gcs_mirror.py
python3 scripts/build_adult_cps_training_table.py
Rscript scripts/jack_mackerel_catchability_cv.R
```

Requires R **sdmTMB** stack (see `src/models/DESCRIPTION`). On hosts where project `renv` is incomplete, `~/R/library` is prepended via `FISHAI_EXTRA_R_LIBS` / `helper.R`.
