#!/usr/bin/env Rscript
# Pacific mackerel encounter binomial GLMM: spatial-block CV (sequential folds).
root <- normalizePath(file.path(dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])), ".."))
setwd(root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

args <- commandArgs(trailingOnly = TRUE)
cfg_path <- if (length(args) >= 1L && nzchar(args[1L])) {
  args[1L]
} else {
  file.path(root, "configs", "models", "adult_pacific_mackerel_encounter.yaml")
}
scores_path <- if (length(args) >= 2L && nzchar(args[2L])) {
  args[2L]
} else {
  file.path(root, "artifacts", "models", "adult_pacific_mackerel", "spatial_block_cv_scores.json")
}

cfg <- load_config_yaml(cfg_path)
dat <- load_model_data(cfg = cfg)
if (is.null(dat$fold_id)) {
  stop("model frame missing fold_id", call. = FALSE)
}

fold_csv <- cfg$data$fold_assignment_path
if (!is.null(fold_csv) && nzchar(fold_csv)) {
  if (!grepl("^/", fold_csv)) {
    fold_csv <- file.path(root, fold_csv)
  }
  if (!file.exists(fold_csv)) {
    events_ref <- .read_model_table(cfg$data$events_path)
    events_ref <- .normalize_cufes_events_columns(events_ref)
    params <- spatial_block_cv_params(cfg)
    fa <- assign_cufes_spatial_block_folds(events_ref, params)
    dir.create(dirname(fold_csv), recursive = TRUE, showWarnings = FALSE)
    write_fold_assignment_csv(fa, fold_csv)
    message("wrote fold assignment: ", fold_csv)
  }
}

cv <- run_cv_spatial(
  dat,
  NULL,
  cfg,
  fold_ids = dat$fold_id,
  n_workers = 1L,
  checkpoint_dir = file.path(root, "artifacts", "models", "adult_pacific_mackerel", "cv_checkpoints"),
  checkpoint_label = "adult_pacific_mackerel"
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
if (oof_complete) {
  z <- as.integer(oof$z)
  p <- oof$p
  if (any(z == 1L) && any(z == 0L)) {
    boyce <- cbi_continuous(p, p[z == 1L])
    auc <- auc_mw(z, p)
    tss <- tss_at(z, p, 0.5)
  }
}

elpd <- cv$sum_loglik
eligible <- isTRUE(cv$elpd_eligible) && is.finite(as.numeric(elpd))
if (!eligible) {
  elpd <- NA_real_
}

report <- list(
  species = "Pacific mackerel encounter probability (all sizes)",
  model_config = cfg_path,
  n_fit_rows = nrow(dat),
  n_presences = sum(as.integer(dat$y) > 0L),
  n_absences = sum(as.integer(dat$y) == 0L),
  adult_length_cutoff_mm = NA,
  length_gate = "none (all sizes)",
  model_spec_note = "spatial off; linear covariates (CV remediation)",
  elpd = elpd,
  elpd_eligible = eligible,
  fold_loglik = as.list(cv$fold_loglik),
  n_failed_folds = cv$n_failed_folds,
  auc = auc,
  tss = tss,
  boyce = boyce,
  oof_complete = oof_complete,
  fold_assignment_path = cfg$data$fold_assignment_path
)

dir.create(dirname(scores_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(report, scores_path, auto_unbox = TRUE, pretty = TRUE)
cat("wrote scores:", scores_path, "\n")
if (!eligible) {
  message("ELPD not eligible; scores written for audit.")
  quit(status = 0L)
}
