#!/usr/bin/env Rscript
# Predict jack mackerel encounter probability on a GLORYS grid with issued WCOFS covariates.

args_all <- commandArgs(trailingOnly = FALSE)
file_arg <- args_all[grep("^--file=", args_all)]
root <- normalizePath(file.path(dirname(sub("^--file=", "", file_arg[1])), "..", ".."))
setwd(root)
Sys.setenv(FISHAI_ROOT = root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

flags <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  i <- match(flag, flags)
  if (is.na(i) || i >= length(flags)) default else flags[i + 1L]
}

checkpoint <- get_arg("--checkpoint")
grid_parquet <- get_arg("--grid-parquet")
cutoff <- get_arg("--cutoff")
output <- get_arg("--output")
wcofs_key <- get_arg("--wcofs-key", "")

if (any(vapply(list(checkpoint, grid_parquet, cutoff, output), is.null, logical(1L)))) {
  stop("usage: --checkpoint RDS --grid-parquet path --cutoff YYYY-MM-DD --output csv", call. = FALSE)
}

cfg <- load_config_yaml(file.path(root, "configs/models/jack_mackerel_encounter_all_sizes.yaml"))
cutoff_date <- as.Date(cutoff)
hold_day <- cutoff_date + 1L

dat <- load_model_data(cfg = cfg, min_duration_min = 2)
dat <- adult_forecast_prepare_frame(dat, cfg)
train <- dat[dat$event_day <= cutoff_date, , drop = FALSE]
hold <- dat[dat$event_day == hold_day, , drop = FALSE]
extra <- sort(unique(as.integer(hold$time_idx)))
fit_cfg <- cfg
fit_cfg$model$extra_time_slices <- extra
mesh <- build_fishai_production_mesh(train, cfg$mesh)
fit_res <- fit_encounter_binomial_engine(train, mesh, fit_cfg)
if (!is.null(.cv_fit_failure_reason(fit_res))) {
  stop("cutoff fit failed for map export", call. = FALSE)
}
fit <- fit_res$fit

if (!requireNamespace("arrow", quietly = TRUE)) {
  stop("arrow required", call. = FALSE)
}
grid <- arrow::read_parquet(grid_parquet)
grid$event_day <- hold_day
grid$y <- 0L
grid$encounter <- 0L
grid$effort_duration_min <- 60
grid$log_effort <- log(60)

if (!nrow(hold)) {
  stop("no holdout rows on D+1 for map export", call. = FALSE)
}
grid$time_idx <- as.integer(unique(hold$time_idx)[1L])
grid$X <- (grid$lon + 120) * 50
grid$Y <- (grid$lat - 32) * 50

pred <- stats::predict(fit, newdata = grid)
eta <- pred$est + grid$log_effort
p <- 1 / (1 + exp(-as.numeric(eta)))
out <- data.frame(
  lat = grid$lat,
  lon = grid$lon,
  p_encounter = p,
  cutoff = cutoff,
  holdout_day = format(hold_day),
  wcofs_s3_key = wcofs_key,
  stringsAsFactors = FALSE
)
dir.create(dirname(output), recursive = TRUE, showWarnings = FALSE)
utils::write.csv(out, output, row.names = FALSE)
