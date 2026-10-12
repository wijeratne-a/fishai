#!/usr/bin/env Rscript
# OOF SDM export + pooled-train grid suitability S(x, t0) for advection hindcast.
Sys.setenv(
  OMP_NUM_THREADS = "1",
  MKL_NUM_THREADS = "1",
  OPENBLAS_NUM_THREADS = "1",
  VECLIB_MAXIMUM_THREADS = "1"
)
args_all <- commandArgs(trailingOnly = FALSE)
file_arg <- args_all[grep("^--file=", args_all)]
root <- normalizePath(file.path(dirname(sub("^--file=", "", file_arg[1])), "..", ".."))
setwd(root)
Sys.setenv(FISHAI_ROOT = root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

flags <- commandArgs(trailingOnly = TRUE)
test_fold <- 4L
idx <- match("--test-fold", flags)
if (!is.na(idx) && idx < length(flags)) {
  test_fold <- as.integer(flags[[idx + 1L]])
}
grids_only <- "--grids-only" %in% flags

out_dir <- file.path(root, "artifacts", "models", "jack_mackerel_advection_sdm")
cov_dir <- file.path(out_dir, "grid_covariates")
s_dir <- file.path(out_dir, "grid_s")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(s_dir, recursive = TRUE, showWarnings = FALSE)

cfg_path <- file.path(root, "configs", "models", "jack_mackerel_encounter_all_sizes.yaml")
cfg <- load_config_yaml(cfg_path)
cfg$mesh$barrier$enabled <- FALSE

fold_csv <- cfg$data$fold_assignment_path
if (!grepl("^/", fold_csv)) {
  fold_csv <- file.path(root, fold_csv)
}
events_ref <- .read_model_table(cfg$data$events_path)
events_ref <- .normalize_cufes_events_columns(events_ref)
params <- spatial_block_cv_params(cfg)
fa <- assign_cufes_spatial_block_folds(events_ref, params)
dir.create(dirname(fold_csv), recursive = TRUE, showWarnings = FALSE)
write_fold_assignment_csv(fa, fold_csv)

dat <- load_model_data(cfg = cfg)
if (is.null(dat$fold_id)) {
  stop("model frame missing fold_id", call. = FALSE)
}

events_csv <- file.path(out_dir, "hindcast_events.csv")
if (isTRUE(grids_only) && file.exists(events_csv)) {
  events_out <- utils::read.csv(events_csv, stringsAsFactors = FALSE)
  oof <- data.frame(
    event_id = events_out$event_id,
    p = events_out$p_sdm,
    stringsAsFactors = FALSE
  )
} else {
  cv <- run_cv_spatial(
    dat,
    NULL,
    cfg,
    fold_ids = dat$fold_id,
    n_workers = 1L,
    checkpoint_dir = file.path(out_dir, "cv_checkpoints"),
    checkpoint_label = "jack_mackerel_advection"
  )
  oof <- cv$oof_predictions
  if (nrow(oof) != nrow(dat)) {
    stop("incomplete OOF predictions for advection export", call. = FALSE)
  }
}

train <- dat[as.integer(dat$fold_id) != test_fold, , drop = FALSE]
test <- dat[as.integer(dat$fold_id) == test_fold, , drop = FALSE]
mesh_train <- build_fishai_mesh(train, cfg$mesh)
pooled <- fit_encounter_binomial_engine(train, mesh_train, cfg)
fit_reason <- .cv_fit_failure_reason(pooled)
if (!is.null(fit_reason)) {
  stop("pooled train fit failed: ", fit_reason, call. = FALSE)
}
ref_log_effort <- stats::median(train$log_effort, na.rm = TRUE)

if (!isTRUE(grids_only) || !file.exists(events_csv)) {
  events_out <- data.frame(
    event_id = as.character(dat$event_id),
    fold_id = as.integer(dat$fold_id),
    z = as.integer(dat$y > 0),
    p_sdm = as.numeric(oof$p[match(as.character(dat$event_id), as.character(oof$event_id))]),
    time = format(as.POSIXct(dat$time, tz = "UTC"), "%Y-%m-%dT%H:%M:%SZ"),
    lat = as.numeric(dat$lat),
    lon = as.numeric(dat$lon),
    X = as.numeric(dat$X),
    Y = as.numeric(dat$Y),
    stringsAsFactors = FALSE
  )
  events_out$event_day <- as.character(as.Date(events_out$time))
  events_out$source_day <- as.character(as.Date(events_out$time) - 1L)
  utils::write.csv(events_out, file.path(out_dir, "hindcast_events.csv"), row.names = FALSE)
} else {
  events_out <- utils::read.csv(events_csv, stringsAsFactors = FALSE)
}

cov_cols <- c("temp_3m_z", "sal_3m_z", "mld_z", "sst_grad_z", "dist_front_z", "log_depth_z")
source_days <- sort(unique(events_out$source_day))
n_grid_days <- 0L
for (day in source_days) {
  cov_path <- file.path(cov_dir, paste0(day, ".csv"))
  s_path <- file.path(s_dir, paste0(day, ".csv"))
  if (!file.exists(cov_path)) {
    next
  }
  g <- utils::read.csv(cov_path, stringsAsFactors = FALSE)
  miss <- setdiff(c(cov_cols, "time_idx", "X", "Y", "cell_id", "latitude", "longitude"), names(g))
  if (length(miss)) {
    stop("grid covariates missing columns for ", day, ": ", paste(miss, collapse = ", "), call. = FALSE)
  }
  keep <- stats::complete.cases(g[, cov_cols, drop = FALSE])
  g <- g[keep, , drop = FALSE]
  if (nrow(g) < 20L) {
    next
  }
  allowed_t <- sort(unique(as.integer(train$time_idx)))
  tid <- as.integer(g$time_idx)
  for (i in seq_along(tid)) {
    if (!tid[[i]] %in% allowed_t) {
      tid[[i]] <- allowed_t[[which.min(abs(allowed_t - tid[[i]]))]]
    }
  }
  g$time_idx <- tid
  g$log_effort <- ref_log_effort
  pred <- stats::predict(pooled$fit, newdata = g)
  g$S <- 1 / (1 + exp(-as.numeric(pred$est + g$log_effort)))
  utils::write.csv(
    g[, c("cell_id", "X", "Y", "latitude", "longitude", "S")],
    s_path,
    row.names = FALSE
  )
  n_grid_days <- n_grid_days + 1L
}

meta <- list(
  test_fold = test_fold,
  n_events = nrow(events_out),
  n_train = nrow(train),
  n_test = nrow(test),
  n_source_days = length(source_days),
  n_grid_s_days = n_grid_days,
  ref_log_effort = ref_log_effort,
  oof_auc = if (any(events_out$z == 1L) && any(events_out$z == 0L)) auc_mw(events_out$z, events_out$p_sdm) else NA_real_
)
jsonlite::write_json(meta, file.path(out_dir, "export_meta.json"), auto_unbox = TRUE, pretty = TRUE)
message(
  "advection export complete test_fold=", test_fold,
  " events=", nrow(events_out),
  " grid_s_days=", n_grid_days
)
