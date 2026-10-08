#!/usr/bin/env Rscript
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

cfg_path <- file.path(root, "configs", "models", "cufes_jack_mackerel.yaml")
scores_path <- file.path(root, "artifacts", "models", "jack_mackerel_eggs", "spatial_block_cv_scores.json")
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
  checkpoint_dir = file.path(root, "artifacts", "models", "jack_mackerel_eggs", "cv_checkpoints"),
  checkpoint_label = "jack_mackerel_eggs"
)
oof <- cv$oof_predictions
boyce <- NA_real_
auc <- NA_real_
tss <- NA_real_
expected_folds <- sort(unique(as.integer(cv$fold_assignment$fold_id)))
oof_complete <- isTRUE(cv$n_failed_folds == 0L) &&
  nrow(oof) == nrow(dat) &&
  setequal(unique(as.integer(oof$fold_id)), expected_folds) &&
  !anyDuplicated(as.character(oof$event_id))
if (oof_complete && any(oof$z == 1L) && any(oof$z == 0L)) {
  boyce <- cbi_continuous(oof$p, oof$p[oof$z == 1L])
  auc <- auc_mw(oof$z, oof$p)
  tss <- tss_at(oof$z, oof$p, 0.5)
}
elpd <- cv$sum_loglik
eligible <- isTRUE(cv$elpd_eligible) && is.finite(as.numeric(elpd))
if (!eligible) {
  elpd <- NA_real_
}
report <- list(
  species = "Pacific jack mackerel (CUFES egg encounter)",
  model_config = cfg_path,
  n_fit_rows = nrow(dat),
  n_presence_rows = sum(as.integer(dat$y > 0)),
  spatial_block_cv = cv$spatial_block_cv,
  elpd = elpd,
  elpd_eligible = eligible,
  elpd_ineligible_reason = cv$elpd_ineligible_reason,
  fold_loglik = as.list(cv$fold_loglik),
  n_failed_folds = cv$n_failed_folds,
  fold_failures = cv$fold_failures,
  oof_auc = auc,
  oof_tss = tss,
  oof_boyce = boyce,
  oof_boyce_method = "cbi_continuous_moving_window",
  product_label = "egg encounter (eggs sampled near 3 m depth along ship tracks)"
)
dir.create(dirname(scores_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(report, scores_path, auto_unbox = TRUE, pretty = TRUE)
message("wrote ", scores_path)
