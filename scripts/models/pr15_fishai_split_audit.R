#!/usr/bin/env Rscript
# Read-only audit: #5 load_model_data + egg_split on PR #15 table @ pin ref.
# Writes JSON to path given by --out (default stdout).
root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(file.path("..", "..")))
setwd(root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))

.args <- commandArgs(trailingOnly = TRUE)
parse_flag <- function(flag) {
  i <- match(flag, .args)
  if (is.na(i) || i >= length(.args)) {
    return(NA_character_)
  }
  .args[[i + 1L]]
}
cov_path <- parse_flag("--covariates")
drops_path <- parse_flag("--drops")
out_path <- parse_flag("--out")
head_sha <- parse_flag("--head-sha")
if (is.na(cov_path) || !nzchar(cov_path)) {
  stop("--covariates required", call. = FALSE)
}
if (is.na(drops_path) || !nzchar(drops_path)) {
  stop("--drops required", call. = FALSE)
}
if (is.na(head_sha) || !nzchar(head_sha)) {
  head_sha <- system2("git", c("rev-parse", "HEAD"), stdout = TRUE)
}

spring_years_with_positives <- function(dat) {
  if (!nrow(dat)) {
    return(0L)
  }
  t <- as.POSIXct(dat$time, tz = "UTC")
  pos <- dat$y > 0
  mo <- as.integer(format(t, "%m"))
  spring <- pos & mo >= 3L & mo <= 6L
  if (!any(spring)) {
    return(0L)
  }
  yrs <- as.integer(format(t[spring], "%Y"))
  length(unique(yrs))
}

audit_species <- function(taxon) {
  cfg <- load_config_yaml(file.path(root, "configs", "models", "cufes_sardine.yaml"))
  cfg$species$taxon <- taxon
  cfg$data$covariates_path <- cov_path
  cfg$data$covariate_drops_path <- drops_path
  cfg$data$covariate_drop_summary_path <- NULL
  cfg$data$fold_assignment_path <- NULL
  cfg$covariates$upstream_fields$log_depth <- "bottom_depth_m"
  cfg$mesh$barrier$enabled <- FALSE
  dat_all <- load_model_data(cfg = cfg, min_duration_min = 2L, egg_split_scope = "all")
  qc <- attr(dat_all, "fishai_data_qc")
  fit <- filter_egg_split_scope(dat_all, cfg, scope = "fit")
  test <- filter_egg_split_scope(dat_all, cfg, scope = "test")
  list(
    taxon = taxon,
    n_model_events = nrow(dat_all),
    n_fit = nrow(fit),
    n_test = nrow(test),
    n_fit_positives = as.integer(sum(fit$y > 0, na.rm = TRUE)),
    n_test_positives = as.integer(sum(test$y > 0, na.rm = TRUE)),
    test_springs_with_positive = spring_years_with_positives(test),
    dropped_unavailable_covariates = as.list(qc$dropped_unavailable_covariates %||% character())
  )
}

drops <- if (requireNamespace("arrow", quietly = TRUE)) {
  as.data.frame(arrow::read_parquet(drops_path))
} else {
  utils::read.csv(drops_path, stringsAsFactors = FALSE)
}
drops_by_reason <- as.list(table(drops$reason))

report <- list(
  fishai_head_sha = head_sha,
  pr15_pin = Sys.getenv("PR15_PIN_REF", unset = "794261bfb0cd86ce72145190a1b564ea85202865"),
  pr15_pull = "https://github.com/wijeratne-a/fishai/pull/15",
  n_kept_events = 14592L,
  drops_by_reason = drops_by_reason,
  ignore_upwelling_at_794261b = TRUE,
  species = list(
    sardine = audit_species("sardine"),
    anchovy = audit_species("anchovy")
  )
)

json <- jsonlite::toJSON(report, auto_unbox = TRUE, pretty = TRUE, null = "null")
if (!is.na(out_path) && nzchar(out_path)) {
  writeLines(json, out_path)
} else {
  cat(json, "\n")
}
