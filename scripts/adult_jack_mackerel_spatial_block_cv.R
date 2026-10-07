#!/usr/bin/env Rscript
# Jack mackerel adult CPS: delta hurdle CV with binomial fallback (sequential folds).
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

score_oof <- function(cfg, dat, cv) {
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
    z <- oof$z
    p <- oof$p
    if (any(z == 1L) && any(z == 0L)) {
      boyce <- cbi_continuous(p, p[z == 1L])
      auc <- auc_mw(z, p)
      tss <- tss_at(z, p, 0.5)
    }
  }
  list(auc = auc, tss = tss, boyce = boyce, oof_complete = oof_complete)
}

run_one_cv <- function(cfg_path, label, checkpoint_subdir) {
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
    checkpoint_dir = file.path(root, "artifacts", "models", checkpoint_subdir, "cv_checkpoints"),
    checkpoint_label = checkpoint_subdir
  )
  oof_stats <- score_oof(cfg, dat, cv)
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

has_pd_failure <- function(res) {
  cv <- res$cv
  if (isTRUE(cv$n_failed_folds > 0L)) {
    return(TRUE)
  }
  failures <- unlist(cv$fold_failures, use.names = FALSE)
  any(grepl("non-positive-definite|non-converged", failures, ignore.case = TRUE))
}

delta_cfg <- file.path(root, "configs", "models", "adult_cps_jack_mackerel.yaml")
bin_cfg <- file.path(root, "configs", "models", "adult_cps_jack_mackerel_binomial.yaml")
scores_path <- file.path(root, "artifacts", "models", "adult_jack_mackerel", "spatial_block_cv_scores.json")

# Hurdle delta: spatial [on, on] then one [off, off] retry if non-PD.
res <- run_one_cv(delta_cfg, "delta_spatial_on_on", "adult_jack_mackerel_delta_on")
if (has_pd_failure(res)) {
  message("delta [on,on] had fold failures; retrying spatial [off, off] once")
  cfg <- load_config_yaml(delta_cfg)
  cfg$model$spatial <- list("off", "off")
  tmp <- tempfile(fileext = ".yaml")
  yaml::write_yaml(cfg, tmp)
  res_off <- run_one_cv(tmp, "delta_spatial_off_off", "adult_jack_mackerel_delta_off")
  if (!has_pd_failure(res_off)) {
    res <- res_off
  }
}

model_kind <- "delta_hurdle"
if (has_pd_failure(res)) {
  message("hurdle CV did not converge all folds; falling back to encounter-only binomial")
  res <- run_one_cv(bin_cfg, "encounter_binomial", "adult_jack_mackerel_binomial")
  model_kind <- "encounter_binomial"
}

report <- list(
  species = "Pacific jack mackerel (adult CPS encounter)",
  model_kind = model_kind,
  model_config = res$config,
  n_fit_rows = res$n_fit_rows,
  n_presence_rows = res$n_presence_rows,
  spatial_block_cv = res$cv$spatial_block_cv,
  elpd = res$elpd,
  elpd_eligible = res$elpd_eligible,
  elpd_ineligible_reason = res$cv$elpd_ineligible_reason,
  fold_loglik = as.list(res$cv$fold_loglik),
  n_failed_folds = res$cv$n_failed_folds,
  fold_failures = res$cv$fold_failures,
  oof_auc = res$oof$auc,
  oof_tss = res$oof$tss,
  oof_boyce = res$oof$boyce,
  oof_boyce_method = "cbi_continuous_moving_window",
  adult_length_cutoff_disclosure = paste(
    "Adult specimens were retained only if standard length >= 250 mm (jack mackerel, Trachurus symmetricus).",
    "This cutoff is the length at 50% maturity (L50) from Fitch (1956): 50% of females mature at 250 mm fork length (100% at 350 mm).",
    "The published value is in fork length; applied to standard length it is conservative, since fork length exceeds standard length for the same fish."
  ),
  product_label = "adult spawning encounter evidence (survey catch; not live fish tracking)"
)

dir.create(dirname(scores_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(report, scores_path, auto_unbox = TRUE, pretty = TRUE)
message("wrote ", scores_path)
