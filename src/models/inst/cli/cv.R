#!/usr/bin/env Rscript
root <- normalizePath(file.path(dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])), "..", "..", "..", ".."))
setwd(root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

parsed <- .parse_model_cli_args(commandArgs(trailingOnly = TRUE))
cfg <- load_config_yaml(parsed$config)
dat <- load_model_data(cfg = cfg)
mesh <- build_fishai_mesh(dat, cfg$mesh)
fold_ids <- dat$fold_id
if (is.null(fold_ids)) stop("config data must include fold_id for spatial CV", call. = FALSE)
cv_sp <- run_cv_spatial(dat, mesh, cfg, fold_ids)
cv_lfo <- run_cv_lfo(dat, mesh, cfg, lfo_forecast = 1L, lfo_validations = min(3L, length(unique(dat$time_idx)) - 1L))
out_dir <- cfg$output$dir %||% "artifacts/models"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
saveRDS(list(spatial = cv_sp, lfo = cv_lfo, selected = select_by_elpd(list(spatial = cv_sp, lfo = cv_lfo))), file.path(out_dir, "cv.rds"))
message("cv complete; ELPD spatial=", cv_sp$sum_loglik, " lfo=", cv_lfo$sum_loglik)

if (!is.null(parsed$min_duration_min)) {
  cmp <- compare_duration_sensitivity(cfg, parsed$min_duration_min)
  path <- write_duration_sensitivity_report(cmp, cfg)
  message("duration sensitivity report: ", path)
}
