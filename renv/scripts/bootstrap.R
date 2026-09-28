#!/usr/bin/env Rscript
# Bootstrap renv and install pilot modeling packages (requires network).
# After success, run renv::snapshot() locally to refresh renv.lock.

if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv", repos = "https://cloud.r-project.org")
}

root <- normalizePath(file.path(dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])), "..", ".."))
setwd(root)

if (!file.exists("renv.lock")) {
  renv::init(bare = TRUE, restart = FALSE)
}

pkgs <- c("sdmTMB", "fmesher", "sdmTMBextra")
renv::install(pkgs)
renv::snapshot(prompt = FALSE)

message("renv bootstrap complete")
