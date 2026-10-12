# Jack mackerel DVM (depth × diel) hypothesis test — readout

**Product:** jack mackerel encounter probability (all sizes).  
**Branch:** `cursor/fishai-dvm-test`  
**Baseline config:** `configs/models/jack_mackerel_encounter_all_sizes.yaml`  
**DVM config:** `configs/models/jack_mackerel_encounter_dvm.yaml`  
**CV script:** `scripts/jack_mackerel_dvm_cv.R`

## Hypothesis (mechanistic DVM)

Trawl/set encounter probability at a depth stratum should follow diel vertical migration: **higher shallow-water encounter at night**, **lower by day**, holding physics covariates fixed.

This is **not** the Tier-1 behavioral-regime test (season/day-night × physics interactions). Here we add **two** terms only: `log_depth_z × tod_sin` and `log_depth_z × tod_cos`, where `tod_*` come from **local solar hour** (UTC + longitude/15) on event timestamps merged from `adult_cps_events.parquet`.

## Data and CV (same frame as baseline)

| Item | Value |
|------|------:|
| Fit rows | 539 |
| Presences | 254 |
| Spatial blocks | 60 km |
| Folds | 4 |
| Fold assignment | `artifacts/spatial_block_cv/adult_cps_fold_assignment.csv` (regenerated for current `adult_cps_events.parquet`, 778 physics events; jack fit frame matches prior Tier-1 counts) |

Training table rebuilt locally from public SWFSC GCS mirrors + Copernicus GLORYS (`scripts/build_adult_cps_training_table.py`).

## Gate

**PASS** only if DVM beats baseline on **both** OOF **AUC** (higher) and OOF **Brier** (lower), all folds converged. No spec escalation on FAIL.

## Results

| Model | OOF AUC | OOF Brier | OOF TSS | ELPD |
|-------|--------:|----------:|--------:|-----:|
| Baseline (no diel×depth) | **0.7624** | **0.1986** | 0.407 | −431.24 |
| DVM (`log_depth_z` × cyclic tod) | 0.7499 | 0.2043 | 0.397 | −418.67 |

**Verdict: FAIL** — DVM did not beat baseline on AUC or Brier (`pass_auc=false`, `pass_brier=false`). ELPD improved for DVM but is not the preregistered gate.

Artifact: `artifacts/models/jack_mackerel_encounter_dvm/dvm_cv_comparison.json`.

## Fitted diel pattern (full-data refit, diagnostic)

Plot: `artifacts/models/jack_mackerel_encounter_dvm/dvm_hour_depth_pattern.png`

Hold other covariates at training medians; compare predicted encounter vs **local solar hour** at shallow (Q1) vs deep (Q3) `log_depth_z`:

| Diagnostic | Value |
|------------|------:|
| Shallow-stratum peak hour | ~13.5 (midday) |
| Shallow-stratum minimum hour | ~1.5 (night) |
| Shallow night − midday Δ*p* | −0.045 |

**DVM-consistent? No.** The fitted shallow stratum peaks **midday** and is **lower at night**, the opposite of a classic DVM encounter pattern (shallow night peak ~00–04h, midday minimum). Metrics and biology align on FAIL: the depth×diel interaction does not recover plausible DVM structure.

## Implementation notes

- R helpers: `src/models/R/diel_vertical_migration.R`; attached in `load_model_data()` when `model.diel_vertical_migration.enabled: true`.
- Unit tests: `src/models/tests/testthat/test-diel-vertical-migration.R`.
