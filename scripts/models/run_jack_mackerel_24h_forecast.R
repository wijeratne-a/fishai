#!/usr/bin/env Rscript
Sys.setenv(
  OMP_NUM_THREADS = "1",
  MKL_NUM_THREADS = "1",
  OPENBLAS_NUM_THREADS = "1",
  VECLIB_MAXIMUM_THREADS = "1"
)
args_all <- commandArgs(trailingOnly = FALSE)
file_arg <- args_all[grep("^--file=", args_all)]
root <- normalizePath(file.path(
  dirname(sub("^--file=", "", file_arg[1])),
  "..",
  ".."
))
setwd(root)
Sys.setenv(FISHAI_ROOT = root)
Sys.unsetenv("RENV_PATHS_ROOT")
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

flags <- commandArgs(trailingOnly = TRUE)
inventory_only <- "--inventory-only" %in% flags
report <- run_jack_mackerel_24h_forecast(root = root, inventory_only = inventory_only)
cat("jack mackerel 24h forecast status:", report$status, "\n")
if (!is.null(report$cutoffs)) {
  cat("cutoffs:", paste(report$cutoffs, collapse = ", "), "\n")
}
if (!is.null(report$scoring_windows_overlap_ncei)) {
  cat("WCOFS-era cutoffs:", paste(report$scoring_windows_overlap_ncei, collapse = ", "), "\n")
}
if (identical(report$status, "design_infeasible") || identical(report$status, "BLOCKED")) {
  cat("reason:", report$blocked_reason %||% report$cutoff_selection_reason, "\n")
  quit(status = 2)
}
