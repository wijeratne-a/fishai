#!/usr/bin/env Rscript
# Refresh egg-encounter nowcast surfaces on the latest GLORYS valid day.
# Container entrypoint (same renv image as CI). Does not fit models and does
# not rewrite the training table or mesh.
#
# Usage:
#   Rscript scripts/products/refresh_nowcast.R \
#     <sardine.yaml> <sardine.rds> <anchovy.yaml> <anchovy.rds> \
#     <grid.csv> <valid_day> <source_run_time> <out.json>
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
if (length(pos) != 8L) {
  stop(
    "usage: refresh_nowcast.R sardine.yaml sardine.rds anchovy.yaml anchovy.rds grid.csv valid_day source_run_time out.json",
    call. = FALSE
  )
}
grid <- utils::read.csv(pos[[5]], stringsAsFactors = FALSE)
valid_day <- pos[[6]]
source_run_time <- pos[[7]]
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
  run_nowcast_encounter_surface(
    art, grid, cfg, p$species, valid_day, source_run_time, dry_run = FALSE
  )
})
out <- do.call(rbind, frames)
json <- jsonlite::toJSON(out, dataframe = "rows", na = "null", auto_unbox = TRUE, pretty = TRUE)
writeLines(json, pos[[8]])
message("wrote ", nrow(out), " nowcast rows to ", pos[[8]])
