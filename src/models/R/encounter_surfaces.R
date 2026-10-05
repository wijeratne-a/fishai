#' Egg-encounter surfaces from a frozen sdmTMB artifact on a physics grid.
#'
#' Hindcast only. Nowcast and forecast modes are added by later product steps.
#' Output rows are the `predict_engine()` contract (10 km `cell_id`, no point
#' coordinates). Caller validates them against
#' `configs/schemas/cufes_prediction_output.schema.json`.

.encounter_surface_mode <- function(mode) {
  mode <- match.arg(mode, c("hindcast"))
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
