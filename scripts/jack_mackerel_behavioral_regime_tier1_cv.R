#!/usr/bin/env Rscript
# Tier-1 behavioral-regime CV: baseline (no interactions) vs season/day-night interactions.
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

run_one_cv <- function(cfg_path, label, scores_rel) {
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
    }
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
    model_config = scores_rel,
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

baseline_cfg <- file.path(root, "configs", "models", "jack_mackerel_encounter_all_sizes.yaml")
interaction_cfg <- file.path(root, "configs", "models", "jack_mackerel_encounter_behavioral_regime.yaml")

baseline <- run_one_cv(
  baseline_cfg,
  "jack_mackerel_encounter_all_sizes",
  "artifacts/models/jack_mackerel_encounter_all_sizes/spatial_block_cv_scores.json"
)
interaction <- run_one_cv(
  interaction_cfg,
  "jack_mackerel_encounter_behavioral_regime",
  "artifacts/models/jack_mackerel_encounter_behavioral_regime/spatial_block_cv_scores.json"
)

# Timestamp audit on interaction frame (document day/night availability).
int_dat <- load_model_data(cfg = load_config_yaml(interaction_cfg))
time_has_hour <- FALSE
if ("time" %in% names(int_dat)) {
  tt <- as.POSIXct(int_dat$time, tz = "UTC")
  time_has_hour <- all(!is.na(tt)) && any(as.integer(format(tt, "%M", tz = "UTC")) != 0L |
    as.integer(format(tt, "%H", tz = "UTC")) != 12L)
}
season_table <- if ("season_met" %in% names(int_dat)) {
  as.list(table(int_dat$season_met))
} else {
  list()
}
day_night_table <- if ("day_night" %in% names(int_dat)) {
  as.list(table(int_dat$day_night))
} else {
  list()
}

pass <- isTRUE(interaction$oof_complete) &&
  isTRUE(baseline$oof_complete) &&
  is.finite(interaction$oof_auc) &&
  is.finite(baseline$oof_auc) &&
  is.finite(interaction$oof_brier) &&
  is.finite(baseline$oof_brier) &&
  interaction$oof_auc > baseline$oof_auc &&
  interaction$oof_brier < baseline$oof_brier

verdict <- if (pass) "PASS" else "FAIL"

comparison <- list(
  tier = 1,
  species = "Pacific jack mackerel (all sizes)",
  length_gate = "none (all sizes)",
  verdict = verdict,
  verdict_rule = "interaction model must beat baseline OOF AUC AND OOF Brier on spatial-block CV",
  baseline = baseline,
  interaction = interaction,
  lift = list(
    delta_auc = interaction$oof_auc - baseline$oof_auc,
    delta_brier = interaction$oof_brier - baseline$oof_brier
  ),
  behavioral_regime_encoding = list(
    season = "meteorological DJF/MAM/JJA/SON via forecast_season() on event UTC date",
    day_night = "civil UTC day = hour in [6,18); night otherwise (requires event timestamps)",
    event_timestamps_present = time_has_hour,
    season_counts = season_table,
    day_night_counts = day_night_table,
    interaction_covariates = c("temp_3m_z", "sal_3m_z", "mld_z", "sst_grad_z", "dist_front_z"),
    interaction_rationale = paste(
      "Dynamic GLORYS physical drivers (SST proxy, salinity, mixed-layer depth,",
      "SST gradient, front distance) may govern habitat differently by season and",
      "diel vertical migration; log_depth_z is a static bathymetry main effect only."
    )
  )
)

out_path <- file.path(root, "artifacts", "models", "jack_mackerel_behavioral_regime", "tier1_cv_comparison.json")
dir.create(dirname(out_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(comparison, out_path, auto_unbox = TRUE, pretty = TRUE)

message(
  "verdict=", verdict,
  " baseline AUC=", baseline$oof_auc, " Brier=", baseline$oof_brier,
  " interaction AUC=", interaction$oof_auc, " Brier=", interaction$oof_brier,
  " -> ", out_path
)
