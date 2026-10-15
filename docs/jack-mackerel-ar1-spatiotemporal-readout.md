# Jack mackerel AR(1) spatiotemporal encounter model — experiment readout

**Product label:** jack mackerel encounter probability (all sizes)  
**Branch:** `cursor/fishai-ar1-spatiotemporal`  
**Config (AR(1) candidate):** `configs/models/jack_mackerel_encounter_ar1_spatiotemporal.yaml`  
**CV driver:** `scripts/jack_mackerel_encounter_ar1_spatial_block_cv.R`

## Frame and folds (same as baseline / lagged-covariate experiment)

| Item | Value |
|------|------:|
| Fit rows / presences | **539 / 254** |
| Spatial-block CV | 4 folds, **60 km** blocks, seed **20260928** |
| Baseline config | `configs/models/jack_mackerel_encounter_all_sizes.yaml` |
| Baseline linear FE | `temp_3m_z`, `sal_3m_z`, `mld_z`, `sst_grad_z`, `dist_front_z`, `log_depth_z` |

**Baseline gate (fixed):** OOF AUC **> 0.7624**, OOF Brier **< 0.1986**.

**Baseline reproduced on this rebuild** (same folds, spatial-off checkpoints): OOF AUC **0.7624**, OOF Brier **0.1986**, ELPD **−431.24** (539 rows).

## AR(1) model spec (candidate)

| Component | Setting |
|-----------|---------|
| Engine | sdmTMB binomial encounter |
| Spatial | `[on]` + Bakka barrier (land RDS rebuilt from vendored NE clip) |
| Spatiotemporal | `[ar1]` |
| Temporal intercept | Baseline uses daily `rw0` with spatial off; AR(1) candidate uses **spatiotemporal AR(1) only** (`time_varying: null`) so temporal structure is not double-counted |
| Priors | Shared PC Matérn on spatial and spatiotemporal fields (`fit_encounter_binomial_engine` extended with `matern_st`) |

## OOM mitigation ladder (order enforced)

| Step | Resolution ID | Time | Mesh | AR(1)? | Outcome on 15 GiB VM (no swap) |
|------|---------------|------|------|--------|--------------------------------|
| **a** | `a_daily_ar1_baseline_mesh` | Daily dense (`time_idx_dense_remap`) | cutoff **9 km**, ~**1161** vertices | yes | **Incomplete** — fold 1 never checkpointed after **>7 h** CPU; RSS ~**5 GB** (**no OOM**) |
| **b** | `b_daily_ar1_coarse_mesh` | Daily dense | cutoff **18 km**, ~**159** vertices | yes | **Incomplete** — fold 1 still running **>100 min** without checkpoint when stopped; **no OOM** |
| **c** | `c_weekly_ar1_baseline_mesh` | Weekly buckets + **dense remap** (66 time indices) | cutoff **9 km** | yes | **Partial** — **fold 1/4** completed (holdout log-lik **−79.82**); folds 2–4 estimated **multi-hour each** at 100% CPU |
| **d** | `d_weekly_iid_fallback` | Weekly | cutoff **9 km** | **no (IID fallback)** | **Not run** — ladder stopped after **c** still incomplete |

**Mesh specs documented**

- Baseline mesh: `cutoff_km: 9`, `range_guess_km: 60`, barrier `range_fraction: 0.1` → ~**1161** mesh vertices on the jack fit frame.
- Coarse mesh: `cutoff_km: 18`, same `range_guess_km: 60` → ~**159** vertices.

## Results table

| Spec | OOF AUC | OOF Brier | ELPD | Verdict vs gate |
|------|--------:|----------:|-----:|-----------------|
| Baseline (spatial off, rw0) | **0.7624** | **0.1986** | −431.24 | reference |
| AR(1) (any completed resolution) | *NA* | *NA* | *NA* | **not scored** — no full 4-fold AR(1) CV finished |

Artifact: `artifacts/models/jack_mackerel_encounter_ar1/spatial_block_cv_ar1_comparison.json`

## Gate verdict

**INFRASTRUCTURE BLOCKER** — No OOM was observed on resolutions **a**, **b**, or **c** (peak RSS ~5 GB ≪ 15 GB), but **no AR(1) resolution completed all four spatial-block folds** on this 15 GiB, no-swap runner within the experiment window. The strict AUC/Brier gate **cannot be evaluated** (not a performance FAIL).

**Resolutions tried:** (a) daily + 9 km mesh, (b) daily + 18 km mesh, (c) weekly + 9 km mesh (1/4 folds only).

## Engineering notes

- Barrier mesh uses **INLAspacetime** fallback when `sdmTMBextra` is unavailable (`src/models/R/mesh.R`).
- Weekly aggregation must **dense-remap** week indices; sparse calendar week indices caused sdmTMB to propose hundreds of `extra_time` slices and extreme runtimes (fixed in the CV script).
- Prior `[off,off]` baseline simplification avoided per-day GMRF blow-up; AR(1) with dense daily time (225 indices) and ~1k mesh vertices remains **compute-bound** on this VM.
