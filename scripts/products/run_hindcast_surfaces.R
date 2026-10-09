#!/usr/bin/env Rscript
# Hindcast egg-encounter surfaces on a GLORYS covariate grid.
# Run inside the CI modeling image (renv restore), never with host-built R libs.
#
# Usage:
#   Rscript scripts/products/run_hindcast_surfaces.R \
#     <sardine.yaml> <sardine_artifact.rds> \
#     <anchovy.yaml> <anchovy_artifact.rds> \
#     <grid.csv> <valid_day> <out.json>
args <- commandArgs(trailingOnly = FALSE)
file_arg <- args[grep("^--file=", args)]
root <- if (length(file_arg)) {
  normalizePath(file.path(dirname(sub("^--file=", "", file_arg[[1]])), "..", ".."))
} else {
  normalizePath(getwd())
}
setwd(root)
Sys.setenv(FISHAI_ROOT = root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))

pos <- commandArgs(trailingOnly = TRUE)
if (length(pos) != 7L) {
  stop(
    "usage: run_hindcast_surfaces.R sardine.yaml sardine.rds anchovy.yaml anchovy.rds grid.csv valid_day out.json",
    call. = FALSE
  )
}
grid <- utils::read.csv(pos[[5]], stringsAsFactors = FALSE)
valid_day <- pos[[6]]
parts <- list(
  list(cfg = pos[[1]], art = pos[[2]], species = "sardine"),
  list(cfg = pos[[3]], art = pos[[4]], species = "anchovy")
)
frames <- lapply(parts, function(p) {
  if (!file.exists(p$art)) {
    stop("missing frozen artifact: ", p$art, call. = FALSE)
  }
  cfg <- load_config_yaml(p$cfg)
  art <- readRDS(p$art)
  run_hindcast_encounter_surface(art, grid, cfg, p$species, valid_day, dry_run = FALSE)
})
out <- do.call(rbind, frames)
json <- jsonlite::toJSON(out, dataframe = "rows", na = "null", auto_unbox = TRUE, pretty = TRUE)
writeLines(json, pos[[7]])
message("wrote ", nrow(out), " hindcast rows to ", pos[[7]])
