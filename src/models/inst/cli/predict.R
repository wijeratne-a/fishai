#!/usr/bin/env Rscript
root <- normalizePath(file.path(dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])), "..", "..", "..", ".."))
setwd(root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) stop("usage: predict.R <config.yaml> <artifact.rds>", call. = FALSE)
cfg <- load_config_yaml(args[[1]])
artifact <- readRDS(args[[2]])
grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
physics <- cfg$prediction$physics_cycle %||% "PASS"
out <- predict_engine(artifact, grid, cfg, physics_cycle = physics)
out_dir <- cfg$output$dir %||% "artifacts/models"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
utils::write.csv(out, file.path(out_dir, "predictions.csv"), row.names = FALSE)
message("predict complete")
