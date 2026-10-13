#!/usr/bin/env Rscript
# Jack mackerel all-sizes encounter LGCP (inlabru / SPDE) spatial-block CV.
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

cfg_path <- file.path(root, "configs", "models", "jack_mackerel_encounter_all_sizes_lgcp.yaml")
baseline_cfg_path <- file.path(root, "configs", "models", "jack_mackerel_encounter_all_sizes.yaml")
scores_path <- file.path(root, "artifacts", "models", "jack_mackerel_encounter_all_sizes_lgcp", "spatial_block_cv_scores.json")
baseline_scores_path <- file.path(root, "artifacts", "models", "jack_mackerel_encounter_all_sizes", "spatial_block_cv_scores.json")

cfg <- load_config_yaml(cfg_path)
dat <- load_model_data(cfg = cfg)
if (is.null(dat$fold_id)) {
  stop("model frame missing fold_id", call. = FALSE)
}

fold_ids <- sort(unique(as.integer(dat$fold_id)))
oof_list <- vector("list", length(fold_ids))
names(oof_list) <- as.character(fold_ids)
failures <- character(0)

for (fid in fold_ids) {
  message("LGCP fold ", fid, " ...")
  train <- dat[as.integer(dat$fold_id) != fid, , drop = FALSE]
  test <- dat[as.integer(dat$fold_id) == fid, , drop = FALSE]
  fold_res <- tryCatch(
    {
      fit_obj <- fit_encounter_lgcp(train, cfg)
      p <- score_encounter_lgcp_on_events(fit_obj, test, cfg)
      list(p = p, failure = NULL)
    },
    error = function(e) {
      list(p = NULL, failure = conditionMessage(e))
    }
  )
  if (!is.null(fold_res$failure)) {
    failures <- c(failures, paste0("fold_", fid, ": ", fold_res$failure))
    next
  }
  oof_list[[as.character(fid)]] <- data.frame(
    event_id = as.character(test$event_id),
    fold_id = fid,
    z = as.integer(test$y),
    p = as.numeric(fold_res$p),
    stringsAsFactors = FALSE
  )
}

oof <- do.call(rbind, oof_list)
auc <- NA_real_
brier <- NA_real_
if (nrow(oof) == nrow(dat) && any(oof$z == 1L) && any(oof$z == 0L)) {
  auc <- auc_mw(oof$z, oof$p)
  brier <- brier_score(oof$z, oof$p)
}

baseline_auc <- 0.7624
baseline_brier <- 0.1986
if (file.exists(baseline_scores_path)) {
  base_json <- jsonlite::read_json(baseline_scores_path, simplifyVector = TRUE)
  if (!is.null(base_json$oof_auc)) {
    baseline_auc <- as.numeric(base_json$oof_auc)
  }
}

gate_pass <- is.finite(auc) && is.finite(brier) &&
  auc > baseline_auc && brier < baseline_brier

report <- list(
  species = "Pacific jack mackerel (all sizes)",
  model_kind = "encounter_lgcp_spatiotemporal",
  model_config = cfg_path,
  n_fit_rows = nrow(dat),
  n_presence_rows = sum(as.integer(dat$y > 0)),
  coordinate_mode = "exact_trawl_lat_lon",
  spatial_block_cv = spatial_block_cv_params(cfg),
  oof_auc = auc,
  oof_brier = brier,
  baseline_config = baseline_cfg_path,
  baseline_oof_auc = baseline_auc,
  baseline_oof_brier = baseline_brier,
  gate_pass = gate_pass,
  n_failed_folds = length(failures),
  fold_failures = failures,
  model_spec = "inlabru_lgcp_spde_ar1_time_linear_covariates"
)

dir.create(dirname(scores_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(report, scores_path, auto_unbox = TRUE, pretty = TRUE)
message(
  "LGCP OOF AUC=", auc,
  " Brier=", brier,
  " gate=", gate_pass,
  " -> ", scores_path
)
