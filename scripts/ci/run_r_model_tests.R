#!/usr/bin/env Rscript
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
if (!requireNamespace("testthat", quietly = TRUE)) {
  stop("testthat not available in renv library", call. = FALSE)
}
testthat::test_dir(
  file.path(root, "src", "models", "tests", "testthat"),
  reporter = "summary"
)
