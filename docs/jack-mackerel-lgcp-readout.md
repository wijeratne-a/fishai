# Jack mackerel encounter LGCP — readout

**Product:** jack mackerel encounter probability (all sizes), static habitat suitability only (no advection / taxis / 24 h forecast).

**Branch:** `cursor/fishai-lgcp-habitat`  
**LGCP config:** `configs/models/jack_mackerel_encounter_all_sizes_lgcp.yaml`  
**LGCP CV script:** `scripts/jack_mackerel_encounter_lgcp_spatial_block_cv.R`  
**Baseline config:** `configs/models/jack_mackerel_encounter_all_sizes.yaml` (sdmTMB binomial, linear covariates, spatial off, rw0 time)

## Methods

### Data and coordinates

- Same adult CPS training pipeline as the baseline: `data/processed/adult_cps/adult_cps_training_table.parquet` + `adult_cps_events.parquet`, species `Trachurus symmetricus`.
- After the same FishAI QC as sdmTMB (`load_model_data()`): **536** trawl/nearshore rows, **253** presences (exact event `lat` / `lon`, not grid aggregation).
- Environmental covariates match the baseline YAML: `temp_3m_z`, `sal_3m_z`, `mld_z`, `sst_grad_z`, `dist_front_z`, `log_depth_z` (GLORYS forcing).

### Spatial-block CV

- **4** folds, **60 km** blocks, seed **20260928**, EPSG:32611 — same parameters as `spatial_block_cv_params()` on the baseline config.
- Fold assignment CSV was extended to cover newly built physics events; **707/707** overlapping `event_id`s retained identical `fold_id` vs the committed assignment.

### LGCP (inlabru + INLA SPDE)

- **Likelihood:** log-Gaussian Cox process (`family = "cp"`) with presence points at exact coordinates and **effort-weighted samplers** at all trawl locations (`weight = effort_duration_min`).
- **Intensity:** \(\lambda(s,t) = \exp(\beta^\top X + \omega(s,t))\) with \(\omega\) a latent **spatiotemporal** Matérn field (SPDE on space × AR(1) in time).
- **Implementation:** `inlabru::lgcp()` + `INLA::inla.spde2.pcmatern()`; holdout encounter probability from Poisson exposure: \(p = 1 - \exp(-\lambda \cdot \text{effort})\).
- **Mesh / time (VM constraint):** A 9 km SPDE mesh with daily `time_idx` (~947 × 223 latent nodes) exceeded the **15 GB** cloud VM and was killed during INLA. The fitted spec uses a **coarser 18 km** triangle mesh and **monthly** `time_slice` (37 levels) for the AR(1) time dimension — documented simplification, not a change to folds or covariates.

## Metrics (out-of-fold, 4 folds)

| Model | OOF AUC | OOF Brier | Gate |
|--------|--------:|----------:|:----:|
| **Baseline sdmTMB** (linear, spatial off) | **0.7624** | **0.1986** | reference |
| **LGCP (inlabru ST-SPDE)** | **0.6516** | **0.2436** | **FAIL** |

Artifact: `artifacts/models/jack_mackerel_encounter_all_sizes_lgcp/spatial_block_cv_scores.json`.

**Gate rule:** LGCP must beat baseline on **both** AUC (higher) and Brier (lower).  
**Verdict: FAIL** — LGCP loses on AUC (−0.11) and Brier (+0.045).

Baseline AUC **0.7622** is also recorded in `artifacts/models/jack_mackerel_encounter_all_sizes/spatial_block_cv_scores.json` (prior run); Brier **0.1986** is the preregistered comparison value from the FishAI task (baseline JSON predates Brier in that artifact).

## Interpretation

- Moving from gridded-midpoint sdmTMB (spatial off) to a continuous-space LGCP with an explicit ST random field **did not** improve out-of-sample discrimination or calibration on these SWFSC trawl points.
- Possible contributors: (1) monthly time mesh vs baseline rw0 on dense daily `time_idx`; (2) coarser 18 km spatial mesh vs 9 km pilot mesh; (3) Poisson-exposure scoring vs binomial logit offset — the gate still uses the LGCP-native holdout probabilities.
- Per task rules, **no further model escalation** (finer mesh, extra smooths, alternate links) after this single LGCP spec failed the gate.

## Reproduce

```bash
# Data (public GCS CPS + Copernicus GLORYS credentials)
python3 scripts/ingest_cps_from_gcs_mirror.py
python3 scripts/build_adult_cps_training_table.py

# R deps: INLA + inlabru (see renv.lock); arrow for parquet
Rscript scripts/jack_mackerel_encounter_lgcp_spatial_block_cv.R
```
