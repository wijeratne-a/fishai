#!/usr/bin/env Rscript
root <- normalizePath(file.path(dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])), "..", "..", "..", ".."))
setwd(root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

parsed <- .parse_model_cli_args(commandArgs(trailingOnly = TRUE))
cfg <- load_config_yaml(parsed$config)
dat <- load_model_data(cfg = cfg)
mesh <- build_fishai_production_mesh(dat, cfg$mesh)
fit <- fit_delta_engine(dat, mesh, cfg)
out_dir <- cfg$output$dir %||% "artifacts/models"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
saveRDS(fit, file.path(out_dir, "fit.rds"))
freeze_model(fit, cfg, file.path(out_dir, "artifact.rds"), training_dat = dat)

if (!is.null(parsed$min_duration_min)) {
  cmp <- compare_duration_sensitivity(cfg, parsed$min_duration_min)
  path <- write_duration_sensitivity_report(cmp, cfg)
  message("duration sensitivity report: ", path)
}

message("train complete")
