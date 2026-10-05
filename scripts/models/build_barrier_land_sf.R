#!/usr/bin/env Rscript
# Build the Bakka barrier land polygon RDS from the vendored public-domain
# Natural Earth clip.
#
# Reads data/reference/shoreline/ne_10m_land_pilot_clip.json (Natural Earth
# ne_10m_land 5.1.1, public domain, vendored in the repo), reprojects to the
# model CRS (EPSG:32611, metres) and writes
# data/reference/mesh/scb_pilot_land_sf.rds.
#
# The RDS itself is NOT committed (scripts/ci/check_no_committed_data.py
# forbids .rds); it is rebuilt deterministically whenever missing. Usable both
# as `Rscript scripts/models/build_barrier_land_sf.R` and sourced from the
# production CV pipeline, which sets FISHAI_ROOT and BARRIER_LAND_DEST.

root <- Sys.getenv("FISHAI_ROOT", unset = "")
if (!nzchar(root)) {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- sub("^--file=", "", args[grepl("^--file=", args)])
  root <- if (length(file_arg)) {
    normalizePath(file.path(dirname(file_arg[[1L]]), "..", ".."), mustWork = FALSE)
  } else {
    normalizePath(getwd(), mustWork = FALSE)
  }
}
# When sourced via sys.source() into an env carrying overrides, exists() finds
# them in the evaluation environment first.
src <- if (exists("BARRIER_LAND_SRC", inherits = TRUE)) {
  BARRIER_LAND_SRC
} else {
  file.path(root, "data", "reference", "shoreline", "ne_10m_land_pilot_clip.json")
}
dest <- if (exists("BARRIER_LAND_DEST", inherits = TRUE)) {
  BARRIER_LAND_DEST
} else {
  file.path(root, "data", "reference", "mesh", "scb_pilot_land_sf.rds")
}

if (!requireNamespace("sf", quietly = TRUE)) {
  stop("build_barrier_land_sf: package 'sf' is required", call. = FALSE)
}
if (!file.exists(src)) {
  stop("build_barrier_land_sf: vendored shoreline clip not found: ", src, call. = FALSE)
}

land <- sf::st_read(src, quiet = TRUE, stringsAsFactors = FALSE)
land <- sf::st_transform(land, crs = 32611L)
land <- sf::st_make_valid(land)
land <- land[!sf::st_is_empty(land), , drop = FALSE]
if (!nrow(land)) {
  stop("build_barrier_land_sf: no land polygons survived transform/validity", call. = FALSE)
}

dir.create(dirname(dest), recursive = TRUE, showWarnings = FALSE)
saveRDS(land, dest)
message(sprintf(
  "build_barrier_land_sf: wrote %s (%d polygons, CRS EPSG:32611)",
  dest, nrow(land)
))
invisible(dest)
