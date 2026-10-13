#!/usr/bin/env Rscript
# Compare physics-only vs physics + PacFIN commercial catch covariates (same spatial-block folds).
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

score_oof <- function(dat, cv) {
  oof <- cv$oof_predictions
  boyce <- NA_real_
  auc <- NA_real_
  tss <- NA_real_
  brier <- NA_real_
  expected_folds <- sort(unique(as.integer(cv$fold_assignment$fold_id)))
  oof_complete <- isTRUE(cv$n_failed_folds == 0L) &&
    nrow(oof) == nrow(dat) &&
    setequal(unique(as.integer(oof$fold_id)), expected_folds) &&
    !anyDuplicated(as.character(oof$event_id))
  if (oof_complete && any(oof$z == 1L) && any(oof$z == 0L)) {
    boyce <- cbi_continuous(oof$p, oof$p[oof$z == 1L])
    auc <- auc_mw(oof$z, oof$p)
    tss <- tss_at(oof$z, oof$p, 0.5)
    brier <- brier_score(oof$z, oof$p)
  }
  list(
    auc = auc,
    tss = tss,
    brier = brier,
    boyce = boyce,
    oof_complete = oof_complete
  )
}

run_one_cv <- function(cfg_path, label, checkpoint_subdir) {
  cfg <- load_config_yaml(cfg_path)
  dat <- load_model_data(cfg = cfg)
  if (is.null(dat$fold_id)) {
    stop("model frame missing fold_id", call. = FALSE)
  }
  cv <- run_cv_spatial(
    dat,
    NULL,
    cfg,
    fold_ids = dat$fold_id,
    n_workers = 1L,
    checkpoint_dir = file.path(root, "artifacts", "models", checkpoint_subdir, "cv_checkpoints"),
    checkpoint_label = checkpoint_subdir
  )
  oof_stats <- score_oof(dat, cv)
  elpd <- cv$sum_loglik
  eligible <- isTRUE(cv$elpd_eligible) && is.finite(as.numeric(elpd))
  if (!eligible) {
    elpd <- NA_real_
  }
  list(
    label = label,
    config = cfg_path,
    n_fit_rows = nrow(dat),
    n_presence_rows = sum(as.integer(dat$y > 0)),
    cv = cv,
    elpd = elpd,
    elpd_eligible = eligible,
    oof = oof_stats
  )
}

baseline_cfg <- file.path(root, "configs", "models", "jack_mackerel_encounter_all_sizes.yaml")
catch_cfg <- file.path(root, "configs", "models", "jack_mackerel_encounter_all_sizes_catch.yaml")
scores_path <- file.path(
  root,
  "artifacts",
  "models",
  "jack_mackerel_encounter_all_sizes_catch",
  "spatial_block_cv_comparison.json"
)

baseline <- run_one_cv(
  baseline_cfg,
  "physics_only",
  "jack_mackerel_encounter_all_sizes_baseline_refit"
)
catch <- run_one_cv(
  catch_cfg,
  "physics_plus_catch",
  "jack_mackerel_encounter_all_sizes_catch"
)

pass_auc <- is.finite(baseline$oof$auc) &&
  is.finite(catch$oof$auc) &&
  catch$oof$auc > baseline$oof$auc
pass_brier <- is.finite(baseline$oof$brier) &&
  is.finite(catch$oof$brier) &&
  catch$oof$brier < baseline$oof$brier
verdict <- if (isTRUE(pass_auc && pass_brier)) "PASS" else "FAIL"

report <- list(
  test = "jack_mackerel_commercial_catch_proxy",
  catch_data_source = "PacFIN ALL005 CPS shoreside (California, 2003-2025, port-group x year)",
  spatial_temporal_match = "Annual port-group landings joined to survey events by calendar year and lat-derived port group (see docs/jack-mackerel-catch-proxy-readout.md)",
  bias_correction = "log1p(total CPEL WETF port-year tonnage) as fleet effort proxy; preferential sampling acknowledged",
  verdict = verdict,
  pass_rule = "catch model beats baseline on both OOF AUC and OOF Brier (lower)",
  baseline = list(
    config = baseline$config,
    oof_auc = baseline$oof$auc,
    oof_brier = baseline$oof$brier,
    oof_tss = baseline$oof$tss,
    oof_boyce = baseline$oof$boyce,
    n_fit_rows = baseline$n_fit_rows,
    n_presence_rows = baseline$n_presence_rows,
    elpd = baseline$elpd
  ),
  catch_model = list(
    config = catch$config,
    oof_auc = catch$oof$auc,
    oof_brier = catch$oof$brier,
    oof_tss = catch$oof$tss,
    oof_boyce = catch$oof$boyce,
    n_fit_rows = catch$n_fit_rows,
    n_presence_rows = catch$n_presence_rows,
    elpd = catch$elpd
  ),
  delta = list(
    auc = catch$oof$auc - baseline$oof$auc,
    brier = catch$oof$brier - baseline$oof$brier
  )
)

dir.create(dirname(scores_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(report, scores_path, auto_unbox = TRUE, pretty = TRUE)
message(
  "verdict=", verdict,
  " baseline AUC=", baseline$oof$auc, " Brier=", baseline$oof$brier,
  " catch AUC=", catch$oof$auc, " Brier=", catch$oof$brier,
  " -> ", scores_path
)
