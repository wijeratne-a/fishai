#' Egg-encounter surfaces from a frozen sdmTMB artifact on a physics grid.
#'
#' Hindcast, nowcast, and 72-hour forecast. Output rows are the
#' `predict_engine()` contract (10 km `cell_id`, no point coordinates).
#' Caller validates them against
#' `configs/schemas/cufes_prediction_output.schema.json`.

.encounter_surface_mode <- function(mode) {
  mode <- match.arg(mode, c("hindcast", "nowcast", "forecast"))
  mode
}

#' @param artifact Frozen `freeze_model()` object for one species.
#' @param grid Physics-grid table with model covariates, `X`, `Y`, `time_idx`.
#' @param cfg Model config list (YAML).
#' @param species `sardine` or `anchovy`.
#' @param valid_day ISO date (UTC) of the GLORYS valid day.
#' @param dry_run When TRUE, rows are marked dry-run and must not be published.
#' @return data.frame of prediction rows.
#' @export
run_hindcast_encounter_surface <- function(
  artifact,
  grid,
  cfg,
  species,
  valid_day,
  dry_run = FALSE,
  nsim = NULL
) {
  .encounter_surface_mode("hindcast")
  if (!species %in% c("sardine", "anchovy")) {
    stop("species must be sardine or anchovy", call. = FALSE)
  }
  cfg$prediction <- cfg$prediction %||% list()
  cfg$prediction$hindcast_evidence <- TRUE
  predict_engine(
    artifact,
    grid,
    cfg,
    physics_cycle = "PASS",
    nsim = nsim,
    species = species,
    valid_day = valid_day,
    dry_run = isTRUE(dry_run)
  )
}

#' Operational nowcast on the latest GLORYS valid day.
#'
#' Evidence state is NOWCAST_UNVALIDATED (or UNKNOWN when out of domain).
#' ``forecast_age_hours`` is 0 and ``fallback_used`` is false.
#' @export
run_nowcast_encounter_surface <- function(
  artifact,
  grid,
  cfg,
  species,
  valid_day,
  source_run_time,
  dry_run = FALSE,
  nsim = NULL
) {
  .encounter_surface_mode("nowcast")
  if (!species %in% c("sardine", "anchovy")) {
    stop("species must be sardine or anchovy", call. = FALSE)
  }
  if (is.null(source_run_time) || !nzchar(source_run_time)) {
    stop("nowcast requires source_run_time", call. = FALSE)
  }
  cfg$prediction <- cfg$prediction %||% list()
  cfg$prediction$hindcast_evidence <- FALSE
  valid_time <- paste0(as.character(as.Date(valid_day)), "T00:00:00Z")
  predict_engine(
    artifact,
    grid,
    cfg,
    physics_cycle = "PASS",
    nsim = nsim,
    species = species,
    valid_day = valid_day,
    dry_run = isTRUE(dry_run),
    forecast_age_hours = 0,
    fallback_used = FALSE,
    valid_time = valid_time,
    source_run_time = source_run_time
  )
}

#' 72-hour egg-encounter forecast from forecast physics fields.
#'
#' Three valid times at 24, 48, and 72 hours. ``lead_days`` is 1, 2, and 3.
#' Evidence state is FORECAST, or UNKNOWN when the cell is out of domain.
#' @export
run_forecast_encounter_surface <- function(
  artifact,
  grid,
  cfg,
  species,
  issue_day,
  source_run_time,
  horizon_hours = 72,
  dry_run = FALSE,
  nsim = NULL
) {
  .encounter_surface_mode("forecast")
  if (!species %in% c("sardine", "anchovy")) {
    stop("species must be sardine or anchovy", call. = FALSE)
  }
  if (!identical(as.integer(horizon_hours), 72L) && !identical(horizon_hours, 72)) {
    stop("forecast horizon must be 72 hours", call. = FALSE)
  }
  if (is.null(source_run_time) || !nzchar(source_run_time)) {
    stop("forecast requires source_run_time", call. = FALSE)
  }
  cfg$prediction <- cfg$prediction %||% list()
  cfg$prediction$hindcast_evidence <- FALSE
  issue <- as.Date(issue_day)
  parts <- lapply(c(24, 48, 72), function(age) {
    valid <- issue + (age / 24)
    predict_engine(
      artifact,
      grid,
      cfg,
      physics_cycle = "PASS",
      nsim = nsim,
      species = species,
      valid_day = as.character(valid),
      dry_run = isTRUE(dry_run),
      forecast_age_hours = age,
      fallback_used = FALSE,
      valid_time = paste0(as.character(valid), "T00:00:00Z"),
      source_run_time = source_run_time
    )
  })
  do.call(rbind, parts)
}
