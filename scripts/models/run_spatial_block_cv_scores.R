#!/usr/bin/env Rscript
Sys.setenv(
  OMP_NUM_THREADS = "1",
  MKL_NUM_THREADS = "1",
  OPENBLAS_NUM_THREADS = "1",
  VECLIB_MAXIMUM_THREADS = "1"
)
root <- normalizePath(
  file.path(
    dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])),
    "..",
    ".."
  )
)
setwd(root)
Sys.setenv(FISHAI_ROOT = root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

# Production spatial-block CV is deliberately sequential: one species at a
# time, one fold at a time, one TMB thread per fit. Each completed fold is
# checkpointed under prereg/cv_checkpoints by run_cv_spatial(), so a killed
# or restarted run resumes from the last completed fold instead of 0/4.
args <- commandArgs(trailingOnly = TRUE)
protocol_path <- if (length(args)) args[[1L]] else NULL
report <- run_spatial_block_cv_scores(protocol_path)
cat("spatial-block CV scores status:", report$status, "\n")
if (identical(report$status, "blocked")) {
  cat("missing inputs:\n")
  cat(paste0("  - ", report$missing_inputs, collapse = "\n"), "\n")
  quit(status = 2)
}
any_failed <- FALSE
for (sp in report$species) {
  cat(
    sp$label,
    " ELPD=",
    sp$elpd,
    " eligible=",
    sp$elpd_eligible,
    " Boyce=",
    sp$boyce,
    " AUC=",
    sp$auc,
    " TSS=",
    sp$tss,
    "\n",
    sep = ""
  )
  n_failed <- sp$n_failed_folds
  if (is.null(n_failed) || length(n_failed) != 1L || is.na(n_failed)) {
    n_failed <- 0L
  }
  if (as.numeric(n_failed) > 0 || !isTRUE(sp$elpd_eligible)) {
    any_failed <- TRUE
  }
}
if (any_failed) {
  quit(status = 1L)
}
