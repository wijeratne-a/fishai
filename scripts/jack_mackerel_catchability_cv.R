#!/usr/bin/env Rscript
# Catchability (detection) sub-model CV vs jack mackerel encounter baseline.
Sys.setenv(
  OMP_NUM_THREADS = "1",
  MKL_NUM_THREADS = "1",
  OPENBLAS_NUM_THREADS = "1",
  VECLIB_MAXIMUM_THREADS = "1"
)
root <- normalizePath(file.path(dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])), ".."))
setwd(root)
Sys.setenv(FISHAI_ROOT = root)
user_r_lib <- Sys.getenv("FISHAI_EXTRA_R_LIBS", unset = "")
if (!nzchar(user_r_lib)) {
  alt <- path.expand("~/R/library")
  if (dir.exists(alt)) {
    user_r_lib <- alt
  }
}
if (nzchar(user_r_lib) && dir.exists(user_r_lib)) {
  .libPaths(c(user_r_lib, .libPaths()))
}
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)
if (nzchar(user_r_lib) && dir.exists(user_r_lib)) {
  .libPaths(c(user_r_lib, .libPaths()))
}

land_rds <- file.path(root, "data", "reference", "mesh", "scb_pilot_land_sf.rds")
if (!file.exists(land_rds)) {
  if (nzchar(user_r_lib) && dir.exists(user_r_lib)) {
    .libPaths(c(user_r_lib, .libPaths()))
  }
  source(file.path(root, "scripts", "models", "build_barrier_land_sf.R"), local = TRUE)
}

ensure_fold_csv <- function(cfg) {
  fold_csv <- cfg$data$fold_assignment_path
  if (is.null(fold_csv) || !nzchar(fold_csv)) {
    return(invisible(NULL))
  }
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
  }
  invisible(fold_csv)
}

run_one_cv <- function(cfg_path, label, scores_rel, model_kind = "delta_hurdle") {
  cfg <- load_config_yaml(cfg_path)
  ensure_fold_csv(cfg)
  dat <- load_model_data(cfg = cfg)
  if (is.null(dat$fold_id)) {
    stop("model frame missing fold_id", call. = FALSE)
  }
  out_dir <- dirname(file.path(root, scores_rel))
  cv <- run_cv_spatial(
    dat,
    NULL,
    cfg,
    fold_ids = dat$fold_id,
    n_workers = 1L,
    checkpoint_dir = file.path(out_dir, "cv_checkpoints", label),
    checkpoint_label = label
  )
  oof <- cv$oof_predictions
  auc <- NA_real_
  tss <- NA_real_
  brier <- NA_real_
  boyce <- NA_real_
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
  elpd <- cv$sum_loglik
  eligible <- isTRUE(cv$elpd_eligible) && is.finite(as.numeric(elpd))
  if (!eligible) {
    elpd <- NA_real_
  }
  scores_path <- file.path(root, scores_rel)
  report <- list(
    species = "Pacific jack mackerel (all sizes)",
    model_kind = model_kind,
    model_config = sub(paste0("^", root, "/?"), "", cfg_path),
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
    oof_brier = brier,
    oof_tss = tss,
    oof_boyce = boyce,
    oof_boyce_method = "cbi_continuous_moving_window",
    length_gate = "none (all sizes)"
  )
  dir.create(dirname(scores_path), recursive = TRUE, showWarnings = FALSE)
  jsonlite::write_json(report, scores_path, auto_unbox = TRUE, pretty = TRUE)
  c(
    report,
    list(
      scores_path = scores_rel,
      cfg_path = cfg_path,
      oof_complete = oof_complete
    )
  )
}

baseline_path <- file.path(root, "configs", "models", "jack_mackerel_encounter_all_sizes.yaml")
baseline_scores <- file.path(root, "artifacts", "models", "jack_mackerel_encounter_all_sizes", "spatial_block_cv_scores.json")

if (!file.exists(baseline_scores)) {
  message("Running baseline encounter CV ...")
  system2("Rscript", file.path(root, "scripts", "jack_mackerel_encounter_spatial_block_cv.R"))
}
baseline <- jsonlite::read_json(baseline_scores, simplifyVector = TRUE)
baseline_auc <- as.numeric(baseline$oof_auc)
# Recompute baseline Brier from a fresh CV if missing in JSON
if (is.null(baseline$oof_brier) || !is.finite(as.numeric(baseline$oof_brier))) {
  message("Baseline JSON lacks oof_brier; scoring baseline holdout predictions ...")
  cfg_b <- load_config_yaml(baseline_path)
  ensure_fold_csv(cfg_b)
  dat_b <- load_model_data(cfg = cfg_b)
  cv_b <- run_cv_spatial(
    dat_b, NULL, cfg_b, fold_ids = dat_b$fold_id, n_workers = 1L,
    checkpoint_dir = file.path(root, "artifacts", "models", "jack_mackerel_encounter_all_sizes", "cv_checkpoints"),
    checkpoint_label = "baseline_brier"
  )
  baseline_brier <- brier_score(as.integer(cv_b$oof_predictions$z), cv_b$oof_predictions$p)
  baseline$oof_brier <- baseline_brier
  jsonlite::write_json(baseline, baseline_scores, auto_unbox = TRUE, pretty = TRUE)
} else {
  baseline_brier <- as.numeric(baseline$oof_brier)
}

candidates <- list(
  list(
    id = "catchability_delta_solar",
    cfg = file.path(root, "configs", "models", "jack_mackerel_encounter_catchability_delta.yaml"),
    scores = "artifacts/models/jack_mackerel_encounter_catchability/catchability_delta_solar_scores.json"
  ),
  list(
    id = "catchability_depth_light",
    cfg = file.path(root, "configs", "models", "jack_mackerel_encounter_catchability_depth_light.yaml"),
    scores = "artifacts/models/jack_mackerel_encounter_catchability/catchability_depth_light_scores.json"
  )
)

results <- lapply(candidates, function(cand) {
  message("CV: ", cand$id)
  run_one_cv(cand$cfg, cand$id, cand$scores, model_kind = "delta_hurdle_catchability")
})

passes_gate <- function(auc, brier) {
  is.finite(auc) && is.finite(brier) &&
    auc > baseline_auc && brier < baseline_brier
}

comparison <- list(
  baseline = list(
    model_config = "configs/models/jack_mackerel_encounter_all_sizes.yaml",
    model_kind = "encounter_binomial",
    n_fit_rows = baseline$n_fit_rows,
    n_presence_rows = baseline$n_presence_rows,
    oof_auc = baseline_auc,
    oof_brier = baseline_brier
  ),
  candidates = lapply(results, function(r) {
    list(
      model_config = sub(paste0("^", root, "/?"), "", r$cfg_path %||% r$model_config),
      model_kind = r$model_kind,
      n_fit_rows = r$n_fit_rows,
      n_presence_rows = r$n_presence_rows,
      oof_auc = r$oof_auc,
      oof_brier = r$oof_brier,
      beats_baseline_auc = isTRUE(r$oof_auc > baseline_auc),
      beats_baseline_brier = isTRUE(r$oof_brier < baseline_brier),
      passes_strict_gate = passes_gate(r$oof_auc, r$oof_brier)
    )
  }),
  strict_gate = "candidate must beat baseline on BOTH oof_auc AND oof_brier",
  any_pass = any(vapply(results, function(r) passes_gate(r$oof_auc, r$oof_brier), logical(1L))),
  verdict = if (any(vapply(results, function(r) passes_gate(r$oof_auc, r$oof_brier), logical(1L)))) "PASS" else "FAIL"
)

out_dir <- file.path(root, "artifacts", "models", "jack_mackerel_encounter_catchability")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(
  comparison,
  file.path(out_dir, "catchability_cv_comparison.json"),
  auto_unbox = TRUE,
  pretty = TRUE
)
message("Baseline AUC=", baseline_auc, " Brier=", baseline_brier)
for (r in results) {
  message(
    r$model_config, " AUC=", r$oof_auc, " Brier=", r$oof_brier,
    " gate=", passes_gate(r$oof_auc, r$oof_brier)
  )
}
message("Verdict: ", comparison$verdict)
