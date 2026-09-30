#!/usr/bin/env Rscript
root <- normalizePath(file.path(dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])), "..", "..", "..", ".."))
setwd(root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

args <- commandArgs(trailingOnly = TRUE)
protocol_path <- if (length(args) >= 1L) args[[1L]] else file.path(root, "configs", "sensitivity_short_samples.yaml")
report <- run_short_sample_sensitivity(protocol_path)
message(
  "short-sample sensitivity complete; prereg_commit_sha=",
  report$prereg_commit_sha
)
