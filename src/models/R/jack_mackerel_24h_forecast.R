#' Rolling-origin 24/48/72 h jack mackerel (all sizes) encounter validation.
#'
#' Operational physics: issued WCOFS fields.f024 from public PDS (2024-07-01+).

JACK_MACKEREL_FORECAST_MIN_TRAIN_ROWS <- 120L
JACK_MACKEREL_PDS_F024_INVENTORY <- "artifacts/jack_mackerel_24h_forecast/pds_f024_inventory.json"

.jack_call_wcofs_sampler <- function(root, cutoffs) {
  if (identical(Sys.getenv("FISHAI_SKIP_WCOFS_SAMPLER", unset = ""), "1")) {
    message("WCOFS sampler skipped; using existing operational covariate table")
    return(invisible(NULL))
  }
  py <- "/tmp/fishai-venv/bin/python3"
  if (!file.exists(py)) {
    py <- Sys.which("python3")
  }
  script <- file.path(root, "scripts", "models", "sample_jack_mackerel_24h_wcofs_covariates.py")
  if (!file.exists(script)) {
    stop("missing WCOFS sampler script: ", script, call. = FALSE)
  }
  cut_path <- tempfile(fileext = ".json")
  jsonlite::write_json(list(cutoffs = format(as.Date(cutoffs))), cut_path, auto_unbox = TRUE)
  out <- file.path(root, "artifacts", "jack_mackerel_24h_forecast", "wcofs_operational_covariates.csv")
  dir.create(dirname(out), recursive = TRUE, showWarnings = FALSE)
  env <- Sys.getenv("PYTHONPATH", unset = "")
  if (!grepl(root, env, fixed = TRUE)) {
    Sys.setenv(PYTHONPATH = if (nzchar(env)) paste(root, "src", env, sep = ":") else paste(root, "src", sep = ":"))
  }
  cmd <- paste(
    shQuote(py),
    shQuote(script),
    "--cutoffs-json", shQuote(cut_path),
    "--output", shQuote(out)
  )
  status <- system(cmd)
  if (!identical(status, 0L)) {
    warning("WCOFS sampler failed (exit ", status, ")", call. = FALSE)
  }
  invisible(out)
}

.jack_read_operational_covariates <- function(root) {
  path <- file.path(root, "artifacts", "jack_mackerel_24h_forecast", "wcofs_operational_covariates.csv")
  if (!file.exists(path)) {
    return(NULL)
  }
  dat <- utils::read.csv(path, stringsAsFactors = FALSE)
  dat$event_id <- as.character(dat$event_id)
  dat$cutoff <- as.character(dat$cutoff)
  dat
}

.jack_read_pds_f024_inventory <- function(root) {
  path <- file.path(root, JACK_MACKEREL_PDS_F024_INVENTORY)
  if (!file.exists(path)) {
    return(NULL)
  }
  jsonlite::fromJSON(path, simplifyVector = FALSE)
}

.jack_pds_f024_cutoffs <- function(root, cutoffs) {
  inv <- .jack_read_pds_f024_inventory(root)
  if (is.null(inv)) {
    return(as.Date(character()))
  }
  listed <- inv$cutoffs_with_f024 %||% list()
  as.Date(unlist(listed))
}

.jack_run_pds_f024_inventory <- function(root, cutoffs) {
  py <- Sys.which("python3")
  script <- file.path(root, "scripts", "models", "inventory_wcofs_pds_f024_cutoffs.py")
  out <- file.path(root, JACK_MACKEREL_PDS_F024_INVENTORY)
  dir.create(dirname(out), recursive = TRUE, showWarnings = FALSE)
  env <- Sys.getenv("PYTHONPATH", unset = "")
  if (!grepl(root, env, fixed = TRUE)) {
    Sys.setenv(PYTHONPATH = if (nzchar(env)) paste(root, "src", env, sep = ":") else paste(root, "src", sep = ":"))
  }
  cut_arg <- paste(shQuote(format(as.Date(cutoffs))), collapse = " ")
  cmd <- paste(
    shQuote(py),
    shQuote(script),
    "--cutoffs", cut_arg,
    "--output", shQuote(out)
  )
  status <- system(cmd)
  if (!identical(status, 0L)) {
    warning("PDS f024 inventory failed (exit ", status, ")", call. = FALSE)
  }
  invisible(out)
}

#' Run jack mackerel rolling-origin 24h validation (preregistered adult CPS protocol).
#' @export
run_jack_mackerel_24h_forecast <- function(
  root = NULL,
  inventory_only = FALSE,
  checkpoint_dir = NULL,
  scores_json = NULL,
  readout_md = NULL,
  min_train_rows = JACK_MACKEREL_FORECAST_MIN_TRAIN_ROWS
) {
  root <- root %||% Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  scores_json <- scores_json %||% file.path(root, "prereg", "jack_mackerel_24h_forecast_scores.json")
  readout_md <- readout_md %||% file.path(root, "prereg", "jack_mackerel_24h_forecast_readout.md")
  checkpoint_dir <- checkpoint_dir %||% file.path(root, "artifacts", "jack_mackerel_24h_forecast", "checkpoints")
  model_config <- "configs/models/jack_mackerel_encounter_all_sizes.yaml"
  cfg <- load_config_yaml(file.path(root, model_config))
  .ensure_barrier_land_rds(cfg, root)
  dat <- load_model_data(cfg = cfg, min_duration_min = 2)
  dat <- adult_forecast_prepare_frame(dat, cfg)
  test_end <- adult_forecast_test_end(dat)
  locked <- adult_forecast_lock_cutoffs(dat, test_end, min_train_rows = min_train_rows)
  all_cutoffs <- locked$selection$cutoffs %||% character()
  .jack_run_pds_f024_inventory(root, all_cutoffs)
  pds_inv <- .jack_read_pds_f024_inventory(root)
  pds_cutoffs <- .jack_pds_f024_cutoffs(root, all_cutoffs)
  scoring_cutoffs <- as.Date(all_cutoffs)[as.Date(all_cutoffs) %in% pds_cutoffs]
  manifest <- list(
    status = if (inventory_only) "cutoffs_locked" else "ok",
    claim = "24h jack mackerel encounter (all sizes) forecast skill (PDS issued f024 only)",
    wcofs_pds_bucket = "noaa-nos-ofs-pds",
    wcofs_pds_fields_start = "2024-07-01",
    pds_f024_inventory = JACK_MACKEREL_PDS_F024_INVENTORY,
    pds_f024_inventory_detail = pds_inv$cutoffs %||% list(),
    cutoffs_with_pds_f024 = as.list(format(scoring_cutoffs)),
    n_cutoffs_with_pds_f024 = length(scoring_cutoffs),
    locked_cutoffs_all = as.list(format(all_cutoffs)),
    operational_claim = FORECAST_OPERATIONAL_CLAIM,
    physics_source = FORECAST_PHYSICS_SOURCE,
    tau_days = FORECAST_TAU_DAYS,
    lane_oracle = "retrospective",
    code_sha = Sys.getenv("GITHUB_SHA", unset = NA_character_),
    design = "prereg/jack_mackerel_24h_forecast_design.md",
    pass_rule = "operational AUC and TSS at 24h strictly greater than persistence and climatology on PDS f024 windows (preregistered >=6 cutoffs when full archive exists)",
    physics_mode = "pds_f024_only",
    spatial_cv_reference = "artifacts/models/jack_mackerel_encounter_all_sizes/spatial_block_cv_scores.json",
    test_end = format(test_end),
    cutoff_calendar = locked$calendar,
    egg_reference_cutoffs = as.list(locked$egg_reference_cutoffs),
    egg_overlap_cutoffs = as.list(locked$egg_overlap_cutoffs),
    cutoff_selection_status = locked$selection$status,
    cutoff_selection_reason = locked$selection$reason,
    cutoff_notes = as.list(locked$selection$notes),
    cutoffs = format(locked$selection$cutoffs),
    cutoff_seasons = as.list(locked$selection$seasons %||% forecast_season(locked$selection$cutoffs)),
    eligible_day_count = length(locked$eligible),
    min_train_rows = as.integer(min_train_rows),
    min_train_days = ADULT_FORECAST_MIN_TRAIN_DAYS,
    species = list()
  )
  if (length(scoring_cutoffs) == 0L) {
    manifest$status <- "BLOCKED"
    manifest$blocked_reason <- "no locked cutoffs have public PDS f024 (2024-07-01+); cannot run PDS-only 24h validation"
    .forecast_write_outputs(manifest, character(), scores_json, readout_md)
    return(manifest)
  }
  if (!identical(locked$selection$status, "ok")) {
    manifest$status <- "design_infeasible"
    .forecast_write_outputs(manifest, character(), scores_json, readout_md)
    return(manifest)
  }
  if (inventory_only) {
    .forecast_write_outputs(manifest, character(), scores_json, readout_md)
    return(manifest)
  }
  .jack_call_wcofs_sampler(root, format(scoring_cutoffs))
  op_cov <- .jack_read_operational_covariates(root)
  if (!is.null(op_cov) && nrow(op_cov)) {
    h24 <- op_cov[op_cov$horizon_days == 1L, , drop = FALSE]
    manifest$n_issued_wcofs_24h_rows <- sum(h24$physics_source == FORECAST_PHYSICS_SOURCE_WCOFS)
    manifest$n_proxy_24h_rows <- sum(h24$physics_source == FORECAST_PHYSICS_SOURCE)
    if (manifest$n_issued_wcofs_24h_rows == 0L) {
      manifest$status <- "BLOCKED"
      manifest$blocked_reason <- "no issued PDS WCOFS f024 covariates for any 24h holdout row in PDS windows"
      .forecast_write_outputs(manifest, character(), scores_json, readout_md)
      return(manifest)
    }
  }
  label <- "jack_mackerel_all_sizes"
  pieces <- list()
  for (cutoff in format(scoring_cutoffs)) {
    path <- .forecast_checkpoint_path(checkpoint_dir, label, cutoff)
    if (file.exists(path)) {
      pieces[[length(pieces) + 1L]] <- readRDS(path)
      next
    }
    message("JACK_FORECAST_CUTOFF_START ", format(cutoff))
    piece <- tryCatch(
      forecast_fit_cutoff(
        dat,
        cfg,
        cutoff,
        extra_time_fill = "holdout_only",
        operational_covariates = op_cov
      ),
      error = function(e) {
        list(
          cutoff = format(as.Date(cutoff)),
          eligible = FALSE,
          failure = conditionMessage(e),
          rows = NULL
        )
      }
    )
    dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
    saveRDS(piece, path)
    pieces[[length(pieces) + 1L]] <- piece
    gc(verbose = FALSE)
  }
  sp <- .forecast_species_from_rows(
    label,
    cfg$species$taxon,
    model_config,
    locked$selection$cutoffs,
    pieces
  )
  manifest$n_eligible_cutoffs <- sp$n_eligible_cutoffs
  manifest$fit_status <- sp$fit_status
  manifest$pass_24h <- isTRUE(sp$pass_24h)
  manifest$cutoffs_detail <- sp$cutoffs
  manifest$species <- list(sp)
  readout <- sprintf(
    "Jack mackerel all-sizes 24h forecast validation. pass_24h=%s fit_status=%s n_eligible_cutoffs=%s",
    manifest$pass_24h,
    manifest$fit_status %||% "",
    manifest$n_eligible_cutoffs %||% 0L
  )
  .forecast_write_outputs(manifest, readout, scores_json, readout_md)
  manifest
}
