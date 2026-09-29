#!/usr/bin/env Rscript
# DRY RUN ONLY — not for interpretation. Writes only under --out-dir (must be temp).
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

.args <- commandArgs(trailingOnly = TRUE)
parse_flag <- function(flag) {
  i <- match(flag, .args)
  if (is.na(i) || i >= length(.args)) {
    return(NA_character_)
  }
  .args[[i + 1L]]
}
out_dir <- parse_flag("--out-dir")
if (is.na(out_dir) || !nzchar(out_dir)) {
  stop("--out-dir is required (use tempdir(); never repo artifacts/)", call. = FALSE)
}
out_dir <- normalizePath(out_dir, mustWork = FALSE)
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
if (grepl("^/workspace/data/provenance", out_dir) || grepl("data/provenance", out_dir, fixed = TRUE)) {
  stop("refusing to write dry run under data/provenance", call. = FALSE)
}

events_path <- parse_flag("--events")
counts_path <- parse_flag("--counts")
cov_path <- parse_flag("--covariates")
species <- parse_flag("--species")
if (is.na(species)) {
  species <- "sardine"
}
config_path <- parse_flag("--config")
if (is.na(config_path)) {
  config_path <- if (species == "anchovy") {
    file.path(root, "configs", "models", "cufes_anchovy_synthetic.yaml")
  } else {
    file.path(root, "configs", "models", "cufes_sardine_synthetic.yaml")
  }
}

cfg <- load_config_yaml(config_path)
cfg$output$dir <- file.path(out_dir, species)
cfg$dry_run <- TRUE
cfg$prediction$hindcast_evidence <- TRUE
cfg$prediction$nsim <- 15L
cfg$model$formula_shared <- "~ 1"
cfg$model$spatial <- list("off", "off")
cfg$model$spatiotemporal <- list("off", "off")
if (is.null(cfg$covariates$upstream_fields)) {
  cfg$covariates$upstream_fields <- list()
}
if (is.null(cfg$covariates$upstream_fields$temp_3m)) {
  defaults <- .default_upstream_covariate_map()
  for (nm in names(defaults)) {
    if (is.null(cfg$covariates$upstream_fields[[nm]])) {
      cfg$covariates$upstream_fields[[nm]] <- defaults[[nm]]
    }
  }
}
cfg$covariates$upstream_fields$log_depth <- "bottom_depth_m"
if (!is.na(events_path)) {
  cfg$data$events_path <- events_path
}
if (!is.na(counts_path)) {
  cfg$data$counts_path <- counts_path
}
if (!is.na(cov_path)) {
  cfg$data$covariates_path <- cov_path
}
if (is.null(cfg$data$covariate_drops_path) || !nzchar(cfg$data$covariate_drops_path)) {
  drops_empty <- file.path(out_dir, paste0(species, "_empty_drops.csv"))
  drops_src <- file.path(root, "src", "models", "tests", "fixtures", "synthetic_covariate_drops.csv")
  if (file.exists(drops_src)) {
    file.copy(drops_src, drops_empty, overwrite = TRUE)
  } else {
    writeLines("event_id,reason,covariate,latitude,longitude", drops_empty)
  }
  cfg$data$covariate_drops_path <- drops_empty
}
cfg$data$covariate_drop_summary_path <- NULL
cfg$data$event_count_guard <- NULL

stages <- list()
record_stage <- function(name, expr) {
  t0 <- proc.time()
  ok <- TRUE
  err <- NA_character_
  out <- NULL
  tryCatch(
    {
      out <- force(expr)
    },
    error = function(e) {
      ok <<- FALSE
      err <<- conditionMessage(e)
    }
  )
  elapsed <- (proc.time() - t0)[["elapsed"]]
  stages[[length(stages) + 1L]] <<- list(
    stage = name,
    ok = ok,
    error = err,
    seconds = as.numeric(elapsed)
  )
  if (!ok) {
    stop("dry run failed at stage ", name, ": ", err, call. = FALSE)
  }
  out
}

dat <- record_stage("load_model_data", load_model_data(cfg = cfg, min_duration_min = 2L, egg_split_scope = "all"))
qc_load <- attr(dat, "fishai_data_qc")
if (length(qc_load$dropped_unavailable_covariates)) {
  cfg$covariates$dynamic <- setdiff(
    cfg$covariates$dynamic %||% character(),
    qc_load$dropped_unavailable_covariates
  )
  cfg$covariates$static <- setdiff(
    cfg$covariates$static %||% character(),
    qc_load$dropped_unavailable_covariates
  )
}

bot2_branch_ref <- "origin/cursor/cufes-glorys-training-covariates-faff"
pr15_pin_ref <- Sys.getenv("PR15_PIN_REF", unset = "794261bfb0cd86ce72145190a1b564ea85202865")
pr15_pin_short <- substr(pr15_pin_ref, 1L, 7L)
branch_existed <- system2(
  "git",
  c("rev-parse", "--verify", bot2_branch_ref),
  stdout = FALSE,
  stderr = FALSE
) == 0
schema_mode_env <- Sys.getenv("BOT2_SCHEMA_MODE", unset = "auto")
schema_mode <- if (identical(schema_mode_env, "auto")) {
  if (branch_existed) "git" else "expected"
} else {
  schema_mode_env
}

record_stage(
  "bottom_depth_qc",
  {
    cols <- intersect(c("bottom_depth_m", "log_depth_z", "depth_at_model_floor"), names(dat))
    if (!length(cols)) {
      stop("no bottom depth columns on loaded frame")
    }
    list(columns = cols, n = nrow(dat))
  }
)

mesh <- record_stage("barrier_mesh", {
  m <- build_fishai_mesh(dat, cfg$mesh)
  land_path <- cfg$mesh$barrier$land_sf_rds
  if (isTRUE(cfg$mesh$barrier$enabled) && !is.null(land_path) && file.exists(land_path)) {
    land_sf <- readRDS(land_path)
    m <- add_barrier_land(m, land_sf, range_fraction = cfg$mesh$barrier$range_fraction %||% 0.1)
    check_barrier(m, dat, land_sf = land_sf)
  } else if (isTRUE(cfg$mesh$barrier$enabled)) {
    message("DRY RUN: barrier land_sf missing at ", land_path, "; skipping add_barrier_land")
  }
  m
})

record_stage("spatial_block_folds", {
  params <- spatial_block_cv_params(cfg)
  folds <- assign_cufes_spatial_block_folds(dat, params)
  write_fold_assignment_csv(folds, file.path(out_dir, paste0(species, "_fold_assignment.csv")))
  folds
})

record_stage("time_forward_scope", {
  if (is.null(cfg$egg_split)) {
    return(list(scope = "none"))
  }
  fit_rows <- filter_egg_split_scope(dat, cfg, scope = "fit")
  test_rows <- tryCatch(
    filter_egg_split_scope(dat, cfg, scope = "test"),
    error = function(e) data.frame()
  )
  list(n_fit = nrow(fit_rows), n_test = nrow(test_rows))
})

fit <- record_stage("fit_delta", fit_delta_engine(dat, mesh, cfg))

artifact_path <- file.path(out_dir, paste0(species, "_artifact.rds"))
artifact <- record_stage(
  "freeze_artifact",
  freeze_model(fit, cfg, artifact_path, training_dat = dat)
)

record_stage("spatial_cv_metrics", {
  params <- spatial_block_cv_params(cfg)
  folds <- assign_cufes_spatial_block_folds(dat, params)
  fit_dat <- tryCatch(filter_egg_split_scope(dat, cfg, scope = "fit"), error = function(e) dat)
  fold_match <- folds$fold_id[match(fit_dat$event_id, folds$event_id)]
  cv <- tryCatch(
    run_cv_spatial(fit_dat, mesh, cfg, fold_ids = fold_match),
    error = function(e) list(elpd = NA_real_, fold_loglik = list(), error = conditionMessage(e))
  )
  list(elpd = cv$elpd, n_folds = length(cv$fold_loglik), note = cv$error %||% NA_character_)
})

grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
ref_cols <- grep("_z$", names(dat), value = TRUE)
if (!length(ref_cols)) {
  stop("no *_z covariate columns for OOD reference", call. = FALSE)
}
artifact$reference <- dat[, ref_cols, drop = FALSE]
artifact$reference_cols <- ref_cols
pred <- record_stage(
  "predict_grid",
  predict_engine(
    artifact,
    grid,
    cfg,
    physics_cycle = "FAIL",
    nsim = 1L,
    species = species,
    valid_day = "2020-06-01",
    dry_run = TRUE
  )
)

record_stage("holdout_metrics", {
  z <- as.integer(dat$y > 0)
  p <- score_encounter_on_events(fit$fit, dat, cfg)
  list(
    auc = auc_mw(z, p),
    boyce = cbi_continuous(p, z),
    tss = tss_at(z, p, 0.5)
  )
})

grid_out <- file.path(out_dir, paste0(species, "_prediction_grid_DRY_RUN.csv"))
write.csv(
  cbind(pred, note = "DRY RUN / NOT FOR INTERPRETATION"),
  grid_out,
  row.names = FALSE
)

manifest <- list(
  dry_run = TRUE,
  not_for_interpretation = TRUE,
  species = species,
  out_dir = out_dir,
  config = config_path,
  bot2_branch_ref = "cursor/cufes-glorys-training-covariates-faff",
  pr15_pull = "https://github.com/wijeratne-a/fishai/pull/15",
  pr15_pin_ref = pr15_pin_ref,
  pr15_pin_short = pr15_pin_short,
  branch_existed = branch_existed,
  mode = schema_mode,
  dropped_unavailable_covariates = as.list(qc_load$dropped_unavailable_covariates %||% character()),
  stages = stages,
  prediction_grid = grid_out
)
manifest_path <- file.path(out_dir, "cufes_pipeline_dry_run_manifest.json")
jsonlite::write_json(manifest, manifest_path, auto_unbox = TRUE, pretty = TRUE, null = "null")
cat("DRY RUN manifest:", manifest_path, "\n")
