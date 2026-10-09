#!/usr/bin/env Rscript
lib <- Sys.getenv("FISHAI_RENV_LIB", unset = file.path("renv", "library", "R-4.3", "x86_64-pc-linux-gnu"))
dir.create(lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(normalizePath(lib), .libPaths()))

need_cran <- c("remotes", "jsonlite", "yaml", "withr", "sf")
for (pkg in need_cran) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, lib = lib, repos = "https://cloud.r-project.org")
  }
}

library(remotes, lib.loc = lib)
install_github(
  c("kaskr/tmbstan", "pbs-assess/fmesher", "pbs-assess/sdmTMB", "pbs-assess/sdmTMBextra"),
  lib = lib,
  upgrade = "never"
)

for (pkg in c("sdmTMB", "sdmTMBextra", "tmbstan", "fmesher", "sf")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop("missing package after install: ", pkg, call. = FALSE)
  }
}
cat("model R stack OK in", lib, "\n")
