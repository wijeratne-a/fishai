#!/usr/bin/env Rscript
# Jack mackerel lagged-covariate experiment: baseline vs +lags vs lagged-only (same lag frame).
Sys.setenv(
  OMP_NUM_THREADS = "1",
  MKL_NUM_THREADS = "1",
  OPENBLAS_NUM_THREADS = "1",
  VECLIB_MAXIMUM_THREADS = "1"
)
root <- normalizePath(file.path(dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])), ".."))
setwd(root)
Sys.setenv(FISHAI_ROOT = root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

.specs <- list(
  list(
    id = "baseline_lagged_frame",
    config = "configs/models/jack_mackerel_encounter_lagged_baseline.yaml",
    label = "baseline (instantaneous physics, lag-complete frame)"
  ),
  list(
    id = "plus_instant_and_lags",
    config = "configs/models/jack_mackerel_encounter_lagged_plus_instant.yaml",
    label = "baseline + 7d/14d lag terms"
  ),
  list(
    id = "lagged_physics_only",
    config = "configs/models/jack_mackerel_encounter_lagged_physics_only.yaml",
    label = "lagged physics only (no instantaneous dynamic terms)"
  )
)

.run_one_spec <- function(spec) {
  cfg_path <- file.path(root, spec$config)
  cfg <- load_config_yaml(cfg_path)
  dat <- load_model_data(cfg = cfg)
  if (is.null(dat$fold_id)) {
    stop("model frame missing fold_id for ", spec$id, call. = FALSE)
  }
  cv <- run_cv_spatial(
    dat,
    NULL,
    cfg,
    fold_ids = dat$fold_id,
    n_workers = 1L,
    checkpoint_dir = file.path(cfg$output$dir, "cv_checkpoints"),
    checkpoint_label = spec$id
  )
  oof <- cv$oof_predictions
  auc <- NA_real_
  brier <- NA_real_
  expected_folds <- sort(unique(as.integer(cv$fold_assignment$fold_id)))
  oof_complete <- isTRUE(cv$n_failed_folds == 0L) &&
    nrow(oof) == nrow(dat) &&
    setequal(unique(as.integer(oof$fold_id)), expected_folds) &&
    !anyDuplicated(as.character(oof$event_id))
  if (oof_complete && any(oof$z == 1L) && any(oof$z == 0L)) {
    auc <- auc_mw(oof$z, oof$p)
    brier <- brier_score(oof$z, oof$p)
  }
  list(
    spec_id = spec$id,
    spec_label = spec$label,
    model_config = cfg_path,
    n_fit_rows = nrow(dat),
    n_presence_rows = sum(as.integer(dat$y > 0)),
    oof_auc = auc,
    oof_brier = brier,
    n_failed_folds = cv$n_failed_folds,
    fold_failures = cv$fold_failures,
    elpd = if (isTRUE(cv$elpd_eligible)) cv$sum_loglik else NA_real_
  )
}

results <- lapply(.specs, .run_one_spec)
baseline <- results[[1L]]
gate_plus <- is.finite(baseline$oof_auc) &&
  is.finite(results[[2L]]$oof_auc) &&
  is.finite(baseline$oof_brier) &&
  is.finite(results[[2L]]$oof_brier) &&
  results[[2L]]$oof_auc > baseline$oof_auc &&
  results[[2L]]$oof_brier < baseline$oof_brier
gate_lag_only <- is.finite(baseline$oof_auc) &&
  is.finite(results[[3L]]$oof_auc) &&
  is.finite(baseline$oof_brier) &&
  is.finite(results[[3L]]$oof_brier) &&
  results[[3L]]$oof_auc > baseline$oof_auc &&
  results[[3L]]$oof_brier < baseline$oof_brier

report <- list(
  experiment = "jack_mackerel_lagged_ocean_covariates",
  product_label = "jack mackerel encounter probability (all sizes)",
  spatial_block_cv = list(n_folds = 4L, block_size_km = 60, seed = 20260928),
  specs = results,
  gate = list(
    rule = "PASS only if OOF AUC higher AND OOF Brier lower vs baseline on same frame",
    plus_instant_and_lags = if (gate_plus) "PASS" else "FAIL",
    lagged_physics_only = if (gate_lag_only) "PASS" else "FAIL",
    overall = if (gate_plus || gate_lag_only) "PASS" else "FAIL"
  ),
  generated_at = as.character(Sys.time())
)

out_path <- file.path(
  root,
  "artifacts",
  "models",
  "jack_mackerel_encounter_lagged",
  "spatial_block_cv_lagged_comparison.json"
)
dir.create(dirname(out_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(report, out_path, auto_unbox = TRUE, pretty = TRUE)
message("Wrote ", out_path)
for (r in results) {
  message(
    r$spec_id,
    " rows=", r$n_fit_rows,
    " pres=", r$n_presence_rows,
    " AUC=", round(r$oof_auc, 4),
    " Brier=", round(r$oof_brier, 4)
  )
}
