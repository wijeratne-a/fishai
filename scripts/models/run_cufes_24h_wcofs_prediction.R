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
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

report <- run_cufes_24h_wcofs_prediction(root = root)
cat("cufes 24h wcofs prediction status:", report$status, "\n")
cat("forcing_source:", report$forcing_source, "\n")
