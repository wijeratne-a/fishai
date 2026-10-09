#!/usr/bin/env Rscript
# 72-hour egg-encounter forecast from forecast physics on the GLORYS grid.
# Same schema and public doctrine as the nowcast. Container / renv only.
#
# Usage:
#   Rscript scripts/products/refresh_forecast.R \
#     <sardine.yaml> <sardine.rds> <anchovy.yaml> <anchovy.rds> \
#     <grid.csv> <issue_day> <source_run_time> <out.json>
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
    "usage: refresh_forecast.R sardine.yaml sardine.rds anchovy.yaml anchovy.rds grid.csv issue_day source_run_time out.json",
    call. = FALSE
  )
}
grid <- utils::read.csv(pos[[5]], stringsAsFactors = FALSE)
issue_day <- pos[[6]]
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
  run_forecast_encounter_surface(
    art, grid, cfg, p$species, issue_day, source_run_time,
    horizon_hours = 72, dry_run = FALSE
  )
})
out <- do.call(rbind, frames)
json <- jsonlite::toJSON(out, dataframe = "rows", na = "null", auto_unbox = TRUE, pretty = TRUE)
writeLines(json, pos[[8]])
message("wrote ", nrow(out), " forecast rows to ", pos[[8]])
