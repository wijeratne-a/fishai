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

# Sardine and anchovy are the protocol species list. Score them in
# concurrent processes. Each process parallelizes its own folds.
lapply <- function(X, FUN, ...) {
  is_species <- is.list(X) &&
    length(X) > 1L &&
    is.list(X[[1L]]) &&
    is.null(X[[1L]]$status) &&
    !is.null(X[[1L]]$model_config)
  if (!is_species) {
    return(base::lapply(X, FUN, ...))
  }
  .cv_limit_tmb_threads()
  jobs <- base::lapply(X, function(sp) {
    force(sp)
    parallel::mcparallel(FUN(sp), silent = FALSE)
  })
  collected <- parallel::mccollect(jobs)
  if (length(collected) != length(X) || any(vapply(collected, is.null, logical(1L)))) {
    stop("concurrent species CV did not return one result per species", call. = FALSE)
  }
  unname(collected)
}

# Holdout predictions use the same worker cap and one TMB thread per fit.
.spatial_block_oof_predictions <- .spatial_block_oof_predictions_parallel

args <- commandArgs(trailingOnly = TRUE)
protocol_path <- if (length(args)) args[[1L]] else NULL
report <- run_spatial_block_cv_scores(protocol_path)
cat("spatial-block CV scores status:", report$status, "\n")
if (identical(report$status, "blocked")) {
  cat("missing inputs:\n")
  cat(paste0("  - ", report$missing_inputs, collapse = "\n"), "\n")
  quit(status = 2)
}
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
}
