# Pre-registration: short-sample duration sensitivity (CUFES pilot)

**Status:** Locked protocol for comparing full-effort training vs refit excluding short tows.

## Question

Do sdmTMB Poisson-link delta egg models for **Pacific sardine** and **northern anchovy** change materially when events shorter than **10 minutes** are excluded from training?

## Training frames

| Arm | Duration rule | Implementation |
| --- | --- | --- |
| **Full fit** | Upstream CUFES QC minimum only (**2 min** when start/stop timestamps have second precision; **5 min** when both are whole minutes). No 10-minute training floor. | `load_model_data()` with `full_fit_min_duration_min` from `configs/sensitivity_short_samples.yaml` (default **2**; set **5** if the pilot ingest documents minute-precision duration QC). |
| **Reduced fit** | Events with **`duration_min` ≥ 10** only. | Same loader with **`reduced_fit_min_duration_min: 10`** (CLI: `--min-duration-min 10`). |

Both arms use the same species count-row join, covariate QC, and offset contract as production (`docs/CUFES_DELTA_MODEL_SPEC.md`).

## Pass criteria

### (a) Coefficient stability

For **every fixed-effect coefficient** and for the **spatial range and variance (σ) parameters of both delta components**, the **reduced-fit point estimate** must lie inside the **full-fit 95% Wald interval**.

Wald intervals are taken from the full-fit maximum likelihood estimates and standard errors (same parameterization as `summary.sdmTMB()` / `sdmTMB::tidy(..., conf.int = TRUE)`).

### (b) Cross-validation stability

1. Fit **full** and **reduced** models once each on the training frames above.
2. Score both on **identical** spatial-block folds (`fold_id`) and leave-future-out (LFO) folds.
3. On held-out data, evaluate **only events with `duration_min` ≥ 10**, each scored with its **own `log(volume_m3)`** offset (not `V_ref`).
4. Compute per-fold **mean log score** (held-out log-likelihood contribution, higher is better) and **Boyce index** (higher is better).
5. For each metric, let `d_f = full_f − reduced_f` across folds. The **full fit passes** if  
   `mean(d) ≥ − z × SE(d)`  
   where `SE(d) = sd(d) / sqrt(n_folds)` and **`z` is read from config** (`cv_check.margin_se_fold_diff`, default **1**).

Both metrics must pass for both CV designs (spatial block and LFO).

## Fail action

If **(a)** or **(b)** fails for **either species**, the operational duration floor **reverts to 10 minutes** for that species’ production config (`data.min_duration_min: 10`). **`V_ref`** is recomputed from the resulting fitting frame after that revert.

## Outputs

The sensitivity runner writes a **pass/fail table per species**, side-by-side coefficient and CV diagnostics, and **`prereg_commit_sha`** (git object id for this file at run time). Thresholds are read only from `configs/sensitivity_short_samples.yaml` — not hard-coded in R.

## Analysis timing

This document must be committed **before** any code that executes the preregistered sensitivity fits. The recorded SHA in run metadata must match the commit containing this file text used for the decision.
