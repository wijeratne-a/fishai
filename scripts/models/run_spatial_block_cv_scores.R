#!/usr/bin/env Rscript
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
