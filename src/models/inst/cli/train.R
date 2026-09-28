#!/usr/bin/env Rscript
root <- normalizePath(file.path(dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])), "..", "..", "..", ".."))
setwd(root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) stop("usage: train.R <config.yaml>", call. = FALSE)
cfg <- load_config_yaml(args[[1]])
dat <- load_model_data(cfg$data$table_path, cfg)
mesh <- build_fishai_mesh(dat, cfg$mesh)
if (isTRUE(cfg$mesh$barrier$enabled)) {
  land_sf <- readRDS(cfg$mesh$barrier$land_sf_rds)
  mesh <- add_barrier_land(mesh, land_sf, range_fraction = cfg$mesh$barrier$range_fraction %||% 0.1)
  check_barrier(mesh, dat, land_sf = land_sf)
}
fit <- fit_delta_engine(dat, mesh, cfg)
out_dir <- cfg$output$dir %||% "artifacts/models"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
saveRDS(fit, file.path(out_dir, "fit.rds"))
message("train complete")
