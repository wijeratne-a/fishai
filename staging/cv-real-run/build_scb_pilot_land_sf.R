#!/usr/bin/env Rscript
# Build barrier land sf (EPSG:32611 metres) from vendored pilot shoreline GeoJSON.
# SHA-256 of ne_10m_land_pilot_clip.json must match harmonization prereg.

root <- normalizePath(file.path(dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])), "..", ".."))
setwd(root)

json_path <- file.path(root, "data", "reference", "shoreline", "ne_10m_land_pilot_clip.json")
out_path <- file.path(root, "staging", "cv-real-run", "artifacts", "scb_pilot_land_sf.rds")
dir.create(dirname(out_path), recursive = TRUE, showWarnings = FALSE)

if (!requireNamespace("sf", quietly = TRUE)) {
  stop("sf package required; run renv bootstrap first", call. = FALSE)
}

sha <- system2("sha256sum", shQuote(json_path), stdout = TRUE)
sha <- sub("\\s+.*$", "", sha[[1L]])
expected <- "2f677a16aa6c8470846d813eda6d82f2656dea2d697b1511a4c878542d20996c"
if (!identical(sha, expected)) {
  stop("shoreline hash mismatch: got ", sha, " expected ", expected, call. = FALSE)
}

land <- sf::st_read(json_path, quiet = TRUE)
land <- sf::st_transform(land, 32611)
saveRDS(land, out_path)
message("wrote ", out_path, " (shoreline sha256 ", sha, ")")
