#!/usr/bin/env Rscript
# Jack mackerel AR(1) spatiotemporal encounter CV with OOM-resolution ladder.
Sys.setenv(
  OMP_NUM_THREADS = "1",
  MKL_NUM_THREADS = "1",
  OPENBLAS_NUM_THREADS = "1",
  VECLIB_MAXIMUM_THREADS = "1",
  RENV_CONFIG_AUTOLOADER_ENABLED = "FALSE"
)

args <- commandArgs(trailingOnly = TRUE)
.resolution_arg <- function() {
  idx <- match("--resolution", args)
  if (is.na(idx) || idx >= length(args)) {
    return(NULL)
  }
  args[[idx + 1L]]
}
.mode_arg <- function() {
  idx <- match("--mode", args)
  if (is.na(idx) || idx >= length(args)) {
    return("orchestrate")
  }
  args[[idx + 1L]]
}

root <- normalizePath(
  file.path(dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])), "..")
)
setwd(root)
Sys.setenv(FISHAI_ROOT = root)

.lib_extra <- Sys.getenv("FISHAI_R_LIBS", unset = "")
if (nzchar(.lib_extra)) {
  .libPaths(c(unlist(strsplit(.lib_extra, ":", fixed = TRUE)), .libPaths()))
}

source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)
if (nzchar(.lib_extra)) {
  .libPaths(c(unlist(strsplit(.lib_extra, ":", fixed = TRUE)), .libPaths()))
}

.baseline_gate <- list(oof_auc = 0.7624, oof_brier = 0.1986)

.resolution_catalog <- function() {
  list(
    list(
      id = "a_daily_ar1_baseline_mesh",
      label = "Daily time (dense remap); AR(1) spatiotemporal; mesh cutoff 9 km / range guess 60 km",
      time_aggregate = "daily",
      spatiotemporal = list("ar1"),
      cutoff_km = 9,
      range_guess_km = 60,
      ar1_candidate = TRUE
    ),
    list(
      id = "b_daily_ar1_coarse_mesh",
      label = "Daily time; AR(1); coarsened mesh cutoff 18 km / range guess 60 km",
      time_aggregate = "daily",
      spatiotemporal = list("ar1"),
      cutoff_km = 18,
      range_guess_km = 60,
      ar1_candidate = TRUE
    ),
    list(
      id = "c_weekly_ar1_baseline_mesh",
      label = "Weekly time aggregation; AR(1); mesh cutoff 9 km / range guess 60 km",
      time_aggregate = "weekly",
      spatiotemporal = list("ar1"),
      cutoff_km = 9,
      range_guess_km = 60,
      ar1_candidate = TRUE
    ),
    list(
      id = "d_weekly_iid_fallback",
      label = "Weekly time; IID spatiotemporal (OOM fallback — not AR(1))",
      time_aggregate = "weekly",
      spatiotemporal = list("iid"),
      cutoff_km = 9,
      range_guess_km = 60,
      ar1_candidate = FALSE
    )
  )
}

.ensure_barrier_land <- function() {
  land_rds <- file.path(root, "data", "reference", "mesh", "scb_pilot_land_sf.rds")
  if (file.exists(land_rds)) {
    return(invisible(land_rds))
  }
  sys.source(
    file.path(root, "scripts", "models", "build_barrier_land_sf.R"),
    envir = new.env(parent = globalenv())
  )
  land_rds
}

.remap_time_weekly <- function(dat, cfg) {
  if (!"time" %in% names(dat)) {
    stop("weekly aggregation requires event time column", call. = FALSE)
  }
  origin <- as.Date(cfg$data$time_idx_origin %||% "1990-01-01")
  tt <- as.POSIXct(dat$time, tz = "UTC")
  days <- as.integer(as.Date(tt) - origin)
  week_raw <- as.integer(floor(days / 7L)) + 1L
  ord <- sort(unique(week_raw))
  dat$time_idx <- match(week_raw, ord)
  dat
}

.apply_resolution <- function(cfg, res) {
  cfg$model$spatiotemporal <- res$spatiotemporal
  cfg$mesh$cutoff_km <- res$cutoff_km
  cfg$mesh$range_guess_km <- res$range_guess_km
  cfg
}

.is_oom_failure <- function(cv, status = 0L) {
  if (!identical(status, 0L)) {
    return(TRUE)
  }
  fails <- cv$fold_failures %||% list()
  txt <- paste(unlist(fails), collapse = " ")
  grepl("Killed|killed|cannot allocate|memory|OOM|non-zero exit", txt, ignore.case = TRUE)
}

.score_cv <- function(dat, cv) {
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
    oof_auc = auc,
    oof_brier = brier,
    oof_complete = oof_complete,
    elpd = if (isTRUE(cv$elpd_eligible)) cv$sum_loglik else NA_real_,
    fold_loglik = as.list(cv$fold_loglik),
    n_failed_folds = cv$n_failed_folds,
    fold_failures = cv$fold_failures
  )
}

.run_baseline_off <- function(cfg_path) {
  cfg <- load_config_yaml(cfg_path)
  dat <- load_model_data(cfg = cfg)
  cv <- run_cv_spatial(
    dat,
    NULL,
    cfg,
    fold_ids = dat$fold_id,
    n_workers = 1L,
    checkpoint_dir = file.path(cfg$output$dir, "cv_checkpoints_baseline"),
    checkpoint_label = "baseline_spatial_off"
  )
  c(.score_cv(dat, cv), list(n_fit_rows = nrow(dat), n_presence_rows = sum(as.integer(dat$y > 0))))
}

.run_one_resolution <- function(res, cfg_path) {
  .ensure_barrier_land()
  cfg <- load_config_yaml(cfg_path)
  cfg <- .apply_resolution(cfg, res)
  dat <- load_model_data(cfg = cfg)
  if (identical(res$time_aggregate, "weekly")) {
    dat <- .remap_time_weekly(dat, cfg)
  }
  if (is.null(dat$fold_id)) {
    stop("model frame missing fold_id", call. = FALSE)
  }
  ckpt <- file.path(
    cfg$output$dir,
    "cv_checkpoints",
    paste0("ar1_", res$id)
  )
  cv <- run_cv_spatial(
    dat,
    NULL,
    cfg,
    fold_ids = dat$fold_id,
    n_workers = 1L,
    checkpoint_dir = ckpt,
    checkpoint_label = res$id
  )
  scores <- .score_cv(dat, cv)
  c(
    scores,
    list(
      resolution_id = res$id,
      resolution_label = res$label,
      mesh = list(cutoff_km = res$cutoff_km, range_guess_km = res$range_guess_km),
      time_aggregate = res$time_aggregate,
      spatiotemporal = as.character(unlist(res$spatiotemporal)),
      ar1_candidate = isTRUE(res$ar1_candidate),
      n_fit_rows = nrow(dat),
      n_presence_rows = sum(as.integer(dat$y > 0)),
      n_time_indices = length(unique(dat$time_idx)),
      oom_suspected = .is_oom_failure(cv, 0L)
    )
  )
}

.run_resolution_child <- function(res, cfg_path) {
  script <- file.path(root, "scripts", "jack_mackerel_encounter_ar1_spatial_block_cv.R")
  lib <- paste(.libPaths(), collapse = ":")
  out_rds <- file.path(
    root,
    "artifacts",
    "models",
    "jack_mackerel_encounter_ar1",
    paste0("resolution_", res$id, ".rds")
  )
  dir.create(dirname(out_rds), recursive = TRUE, showWarnings = FALSE)
  cmd <- sprintf(
    "%s --vanilla %s --mode run --resolution %s",
    shQuote(file.path(Sys.which("Rscript"))),
    shQuote(script),
    shQuote(res$id)
  )
  env <- c(sprintf("FISHAI_ROOT=%s", root), sprintf("FISHAI_R_LIBS=%s", lib))
  status <- system2("/bin/bash", c("-lc", shQuote(paste(c(env, cmd), collapse = " "))))
  if (!file.exists(out_rds)) {
    return(list(
      resolution_id = res$id,
      resolution_label = res$label,
      status = status,
      oom_suspected = !identical(status, 0L),
      oof_auc = NA_real_,
      oof_brier = NA_real_
    ))
  }
  res_obj <- readRDS(out_rds)
  res_obj$status <- status
  res_obj
}

mode <- .mode_arg()
cfg_path <- file.path(root, "configs", "models", "jack_mackerel_encounter_ar1_spatiotemporal.yaml")
catalog <- .resolution_catalog()

if (identical(mode, "run")) {
  res_id <- .resolution_arg()
  if (is.null(res_id)) {
    stop("--mode run requires --resolution", call. = FALSE)
  }
  res <- catalog[[match(res_id, vapply(catalog, `[[`, "", "id"))]]
  if (is.null(res)) {
    stop("unknown resolution id: ", res_id, call. = FALSE)
  }
  result <- .run_one_resolution(res, cfg_path)
  out_rds <- file.path(
    root,
    "artifacts",
    "models",
    "jack_mackerel_encounter_ar1",
    paste0("resolution_", res$id, ".rds")
  )
  dir.create(dirname(out_rds), recursive = TRUE, showWarnings = FALSE)
  saveRDS(result, out_rds)
  message(
    res$id,
    " rows=", result$n_fit_rows,
    " times=", result$n_time_indices,
    " AUC=", round(result$oof_auc, 4),
    " Brier=", round(result$oof_brier, 4),
    " failed=", result$n_failed_folds
  )
  quit(status = if (isTRUE(result$oom_suspected) || result$n_failed_folds > 0L) 1L else 0L)
}

# --- orchestrate ---
baseline_cfg <- file.path(root, "configs", "models", "jack_mackerel_encounter_all_sizes.yaml")
baseline_scores <- .run_baseline_off(baseline_cfg)

attempts <- list()
ar1_fit <- NULL
chosen <- NULL
for (res in catalog) {
  if (!isTRUE(res$ar1_candidate) && !is.null(ar1_fit)) {
    next
  }
  if (!isTRUE(res$ar1_candidate) && is.null(ar1_fit)) {
    message("Trying OOM fallback (non-AR1): ", res$id)
  } else {
    message("Trying resolution: ", res$id)
  }
  attempt <- .run_resolution_child(res, cfg_path)
  attempts[[length(attempts) + 1L]] <- attempt
  fit_ok <- identical(attempt$status, 0L) &&
    isTRUE(attempt$n_failed_folds == 0L) &&
    !isTRUE(attempt$oom_suspected) &&
    is.finite(attempt$oof_auc)
  if (fit_ok && isTRUE(res$ar1_candidate)) {
    ar1_fit <- attempt
    chosen <- attempt
    break
  }
  if (fit_ok && !isTRUE(res$ar1_candidate)) {
    chosen <- attempt
  }
}

gate_pass <- isFALSE(is.null(ar1_fit)) &&
  is.finite(ar1_fit$oof_auc) &&
  is.finite(ar1_fit$oof_brier) &&
  ar1_fit$oof_auc > .baseline_gate$oof_auc &&
  ar1_fit$oof_brier < .baseline_gate$oof_brier

verdict <- if (is.null(ar1_fit)) {
  "INFRASTRUCTURE BLOCKER: OOM at all tried resolutions"
} else if (gate_pass) {
  "PASS"
} else {
  "FAIL"
}

report <- list(
  experiment = "jack_mackerel_ar1_spatiotemporal",
  product_label = "jack mackerel encounter probability (all sizes)",
  spatial_block_cv = list(n_folds = 4L, block_size_km = 60, seed = 20260928),
  baseline_gate = .baseline_gate,
  baseline_reproduced = baseline_scores,
  resolution_attempts = attempts,
  ar1_resolution_fit = ar1_fit,
  chosen_resolution = chosen,
  gate = list(
    rule = "PASS only if AR(1) spec OOF AUC > baseline AND OOF Brier < baseline",
    pass = gate_pass,
    verdict = verdict
  ),
  generated_at = as.character(Sys.time())
)

out_json <- file.path(
  root,
  "artifacts",
  "models",
  "jack_mackerel_encounter_ar1",
  "spatial_block_cv_ar1_comparison.json"
)
dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(report, out_json, auto_unbox = TRUE, pretty = TRUE)
message("Wrote ", out_json)
message("VERDICT=", verdict)
