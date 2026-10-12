#!/usr/bin/env Rscript
# DVM hypothesis CV: baseline vs depth × local-solar time-of-day interactions.
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

land_rds <- file.path(root, "data", "reference", "mesh", "scb_pilot_land_sf.rds")
if (!file.exists(land_rds)) {
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

run_one_cv <- function(cfg_path, label, scores_rel) {
  cfg <- load_config_yaml(cfg_path)
  ensure_fold_csv(cfg)
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
    checkpoint_dir = file.path(root, "artifacts", "models", label, "cv_checkpoints"),
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
    model_kind = "encounter_binomial",
    model_config = scores_rel,
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

  list(
    label = label,
    model_config = cfg_path,
    dat = dat,
    cfg = cfg,
    n_fit_rows = nrow(dat),
    n_presence_rows = sum(as.integer(dat$y > 0)),
    n_folds = length(expected_folds),
    spatial_block_cv = cv$spatial_block_cv,
    n_failed_folds = cv$n_failed_folds,
    fold_failures = cv$fold_failures,
    elpd = elpd,
    elpd_eligible = eligible,
    oof_auc = auc,
    oof_brier = brier,
    oof_tss = tss,
    oof_boyce = boyce,
    oof_complete = oof_complete,
    scores_path = scores_rel
  )
}

plot_dvm_pattern <- function(dvm_res, out_png) {
  dat <- dvm_res$dat
  cfg <- dvm_res$cfg
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  if (isTRUE(cfg$mesh$barrier$enabled)) {
    land_path <- cfg$mesh$barrier$land_sf_rds
    if (!is.null(land_path) && nzchar(land_path) && file.exists(land_path)) {
      mesh <- add_barrier_land(
        mesh,
        readRDS(land_path),
        range_fraction = cfg$mesh$barrier$range_fraction %||% 0.1
      )
    }
  }
  fit <- fit_encounter_binomial_engine(dat, mesh, cfg)$fit
  shallow <- stats::quantile(dat$log_depth_z, 0.25, na.rm = TRUE)
  deep <- stats::quantile(dat$log_depth_z, 0.75, na.rm = TRUE)
  ref_lon <- stats::median(dat$lon, na.rm = TRUE)
  ref_lat <- stats::median(dat$lat, na.rm = TRUE)
  ref_time <- stats::median(as.POSIXct(dat$time, tz = "UTC"), na.rm = TRUE)
  ref_date <- as.Date(ref_time, tz = "UTC")

  cov_cols <- c("temp_3m_z", "sal_3m_z", "mld_z", "sst_grad_z", "dist_front_z")
  ref_row <- dat[1, , drop = FALSE]
  for (col in cov_cols) {
    ref_row[[col]] <- stats::median(dat[[col]], na.rm = TRUE)
  }
  ref_row$lat <- ref_lat
  ref_row$lon <- ref_lon
  ref_row$y <- 0L
  ref_row$log_effort <- stats::median(dat$log_effort, na.rm = TRUE)
  ref_row$time_idx <- dat$time_idx[which.min(abs(as.numeric(dat$time) - as.numeric(ref_time)))]

  hours <- seq(0, 23.5, by = 0.5)
  pred_shallow <- numeric(length(hours))
  pred_deep <- numeric(length(hours))
  for (i in seq_along(hours)) {
    h <- hours[i]
    utc_h <- (h - ref_lon / 15) %% 24
    tt <- as.POSIXct(
      paste(ref_date, sprintf("%02d:%02d:00", floor(utc_h), round((utc_h %% 1) * 60))),
      tz = "UTC"
    )
    row_s <- ref_row
    row_d <- ref_row
    row_s$time <- tt
    row_d$time <- tt
    row_s$log_depth_z <- shallow
    row_d$log_depth_z <- deep
    row_s <- .attach_diel_vertical_migration_terms(row_s, cfg)
    row_d <- .attach_diel_vertical_migration_terms(row_d, cfg)
    pred_shallow[i] <- score_encounter_binomial_on_events(fit, row_s, cfg)
    pred_deep[i] <- score_encounter_binomial_on_events(fit, row_d, cfg)
  }

  dir.create(dirname(out_png), recursive = TRUE, showWarnings = FALSE)
  png(out_png, width = 720, height = 480, res = 96)
  on.exit(dev.off(), add = TRUE)
  ylim <- range(c(pred_shallow, pred_deep), na.rm = TRUE)
  ylim <- ylim + c(-0.02, 0.02) * diff(ylim)
  plot(
    hours, pred_shallow, type = "l", col = "#0072B2", lwd = 2,
    xlab = "Local solar hour of day",
    ylab = "Predicted encounter probability",
    ylim = ylim,
    main = "DVM diagnostic: shallow (Q1) vs deep (Q3) log_depth_z"
  )
  lines(hours, pred_deep, col = "#D55E00", lwd = 2)
  abline(v = c(0, 12), lty = 3, col = "gray60")
  legend(
    "topright",
    legend = c(
      sprintf("Shallow log_depth_z = %.2f", shallow),
      sprintf("Deep log_depth_z = %.2f", deep)
    ),
    col = c("#0072B2", "#D55E00"),
    lwd = 2,
    bty = "n"
  )

  shallow_peak <- hours[which.max(pred_shallow)]
  shallow_min <- hours[which.min(pred_shallow)]
  list(
    shallow_peak_hour = shallow_peak,
    shallow_min_hour = shallow_min,
    shallow_night_day_delta = pred_shallow[hours >= 22 | hours <= 4][1] - pred_shallow[hours >= 10 & hours <= 14][1]
  )
}

baseline_cfg <- file.path(root, "configs", "models", "jack_mackerel_encounter_all_sizes.yaml")
dvm_cfg <- file.path(root, "configs", "models", "jack_mackerel_encounter_dvm.yaml")

baseline <- run_one_cv(
  baseline_cfg,
  "jack_mackerel_encounter_all_sizes",
  "artifacts/models/jack_mackerel_encounter_all_sizes/spatial_block_cv_scores.json"
)
dvm <- run_one_cv(
  dvm_cfg,
  "jack_mackerel_encounter_dvm",
  "artifacts/models/jack_mackerel_encounter_dvm/spatial_block_cv_scores.json"
)

pass_auc <- is.finite(dvm$oof_auc) && is.finite(baseline$oof_auc) && dvm$oof_auc > baseline$oof_auc
pass_brier <- is.finite(dvm$oof_brier) && is.finite(baseline$oof_brier) && dvm$oof_brier < baseline$oof_brier
verdict <- if (isTRUE(pass_auc && pass_brier && dvm$n_failed_folds == 0L)) "PASS" else "FAIL"

pattern_png <- file.path(root, "artifacts", "models", "jack_mackerel_encounter_dvm", "dvm_hour_depth_pattern.png")
pattern_diag <- tryCatch(
  plot_dvm_pattern(dvm, pattern_png),
  error = function(e) {
    message("DVM pattern plot failed: ", conditionMessage(e))
    list(error = conditionMessage(e))
  }
)

comparison <- list(
  verdict = verdict,
  gate = "DVM beats baseline on both OOF AUC (higher) and OOF Brier (lower); all folds converged",
  baseline = baseline[c(
    "label", "model_config", "n_fit_rows", "n_presence_rows", "n_folds",
    "elpd", "elpd_eligible", "oof_auc", "oof_brier", "oof_tss", "n_failed_folds"
  )],
  dvm = dvm[c(
    "label", "model_config", "n_fit_rows", "n_presence_rows", "n_folds",
    "elpd", "elpd_eligible", "oof_auc", "oof_brier", "oof_tss", "n_failed_folds"
  )],
  pass_auc = pass_auc,
  pass_brier = pass_brier,
  dvm_pattern_plot = sub(paste0("^", root, "/?"), "", pattern_png),
  dvm_pattern_diagnostic = pattern_diag
)
comparison$baseline$model_config <- sub(paste0("^", root, "/?"), "", baseline$model_config)
comparison$dvm$model_config <- sub(paste0("^", root, "/?"), "", dvm$model_config)

out_json <- file.path(root, "artifacts", "models", "jack_mackerel_encounter_dvm", "dvm_cv_comparison.json")
dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(comparison, out_json, auto_unbox = TRUE, pretty = TRUE)

message(
  "DVM CV verdict=", verdict,
  " baseline AUC=", baseline$oof_auc, " Brier=", baseline$oof_brier,
  " ELPD=", baseline$elpd,
  " | dvm AUC=", dvm$oof_auc, " Brier=", dvm$oof_brier,
  " ELPD=", dvm$elpd,
  " -> ", out_json
)
