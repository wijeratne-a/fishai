#!/usr/bin/env Rscript
# Bootstrap renv and install pilot modeling packages (requires network).
# Run inside the repo Docker image; refreshes renv.lock at repo root.

root <- normalizePath(file.path(
  dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])),
  "..",
  ".."
))
setwd(root)

.lib <- file.path(root, "renv", "library")
dir.create(.lib, recursive = TRUE, showWarnings = FALSE)
Sys.setenv(RENV_PATHS_LIBRARY = .lib)
.libPaths(c(.lib, .libPaths()))

if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv", repos = "https://cloud.r-project.org", lib = .lib)
}
library(renv, lib.loc = .lib)

if (!file.exists("renv.lock")) {
  renv::init(bare = TRUE, restart = FALSE)
}

# Pinned GitHub commit for add_barrier_mesh() (sdmTMBextra companion package).
SDMTMBEXTRA_COMMIT <- "eaa57bcc748fa462fb3069f18ff507407d99f023"

cran_pkgs <- c(
  "remotes",
  "TMB",
  "fmesher",
  "sdmTMB",
  "sf",
  "INLAspacetime",
  "tmbstan",
  "testthat",
  "yaml",
  "jsonlite",
  "withr"
)

renv::install(cran_pkgs)

if (!requireNamespace("remotes", quietly = TRUE)) {
  install.packages("remotes", repos = "https://cloud.r-project.org", lib = .lib)
}

remotes::install_github(
  paste0("pbs-assess/sdmTMBextra@", SDMTMBEXTRA_COMMIT),
  lib = .lib,
  upgrade = "never"
)

renv::snapshot(prompt = FALSE)
message("renv bootstrap complete; sdmTMBextra commit=", SDMTMBEXTRA_COMMIT)
