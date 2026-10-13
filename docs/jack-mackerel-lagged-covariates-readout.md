# Jack mackerel lagged ocean covariates — experiment readout

**Product label:** jack mackerel encounter probability (all sizes)  
**Branch:** `cursor/fishai-lagged-covariates`  
**Hypothesis:** 7-day and 14-day lagged GLORYS physics (SST at 3 m, SST gradient, mixed-layer depth) improve encounter prediction vs instantaneous fields alone.

## Frame and folds (apples-to-apples)

| Item | Value |
|------|------:|
| Species | *Trachurus symmetricus* (all sizes, no length gate) |
| Spatial-block CV | 4 folds, 60 km blocks, seed 20260928 |
| Shared table | `data/processed/adult_cps/adult_cps_training_table_lagged.parquet` |
| Jack fit rows / presences | **539 / 254** (same as baseline on instantaneous table) |
| Lag columns | `T3m_lag7d`, `T3m_lag14d`, `sst_grad_lag7d`, `sst_grad_lag14d`, `MLD_m_lag7d`, `MLD_m_lag14d` |

**Lag availability:** GLORYS daily fields were joined at the same tow geometry as instantaneous covariates, sampled at event mid-time minus 7 and 14 calendar days. Building the lag-augmented adult CPS table dropped **449** multi-species rows with any missing lag field (early-era or cache gaps). After species and mesh QC, **no jack mackerel rows were lost** relative to the baseline fit frame (539 / 254).

**Baseline reproduction** on the original instantaneous table (`configs/models/jack_mackerel_encounter_all_sizes.yaml`): OOF AUC **0.7624**, OOF Brier **0.1986**, 539 rows, 254 presences.

## Spatial-block CV results (lag-complete jack frame)

| Spec | OOF AUC | OOF Brier | ELPD |
|------|--------:|----------:|-----:|
| Baseline (instantaneous physics only) | **0.7624** | **0.1986** | −431.24 |
| Baseline + 7d/14d lag terms | 0.7524 | 0.2028 | −448.30 |
| Lagged physics only (no instantaneous dynamic terms) | 0.7238 | 0.2138 | −554.53 |

Artifact: `artifacts/models/jack_mackerel_encounter_lagged/spatial_block_cv_lagged_comparison.json`  
CV driver: `scripts/jack_mackerel_encounter_lagged_spatial_block_cv.R`

Configs:

- `configs/models/jack_mackerel_encounter_lagged_baseline.yaml`
- `configs/models/jack_mackerel_encounter_lagged_plus_instant.yaml`
- `configs/models/jack_mackerel_encounter_lagged_physics_only.yaml`

Lag build: `scripts/build_adult_cps_lagged_training_table.py` (library: `fishai.ingestion.physics.lagged_ocean_covariates`).

## Gate verdict

**Rule:** PASS only if a candidate beats baseline on **both** OOF AUC (higher) and OOF Brier (lower).

| Candidate | AUC vs baseline | Brier vs baseline | Verdict |
|-----------|-----------------|-------------------|---------|
| Baseline + lags | 0.7524 < 0.7624 | 0.2028 > 0.1986 | **FAIL** |
| Lagged physics only | 0.7238 < 0.7624 | 0.2138 > 0.1986 | **FAIL** |

**Overall: FAIL** — no spec escalation (per experiment protocol).

## Interpretation

Lagged 7d/14d SST, SST gradient, and MLD did **not** improve out-of-fold discrimination or calibration; adding them alongside instantaneous terms slightly **hurt** both metrics, and lagged-only physics was substantially worse than instantaneous baselines. For this jack mackerel encounter model, **recent past ocean conditions do not carry incremental predictive signal beyond same-day GLORYS physics** in the pilot domain.
