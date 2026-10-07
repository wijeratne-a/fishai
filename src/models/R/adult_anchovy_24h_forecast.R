#' Rolling-origin 24/48/72 h adult northern anchovy encounter validation.
#'
#' Adapted from prereg/cufes_forecast_temporal_holdout_design.md and the egg
#' execution on branch cursor/fishai-forecast-validation-a046. Operational arm
#' is the same damped-anomaly proxy (NOT_ISSUED_FORECAST).

ADULT_FORECAST_MIN_TRAIN_ROWS <- 150L
ADULT_FORECAST_MIN_TRAIN_DAYS <- 30L

#' Egg-protocol reference cutoffs (locked in egg scores JSON) for overlap reporting.
#' @export
adult_forecast_egg_reference_cutoffs <- function() {
  as.Date(c(
    "1998-02-26", "1998-04-07", "1998-06-13", "2012-09-03",
    "2017-08-05", "2018-09-20", "2021-01-22", "2022-04-12"
  ))
}

#' Last calendar day that may serve as cutoff D (requires D+1..D+3 in frame).
#' @export
adult_forecast_test_end <- function(dat) {
  daily <- .forecast_daily_summary(dat)
  days <- as.Date(daily$day)
  if (!length(days)) {
    stop("empty adult forecast frame", call. = FALSE)
  }
  max(days) - 3L
}

#' Lock eight cutoffs on the adult anchovy frame.
#' @export
adult_forecast_lock_cutoffs <- function(dat, test_end, min_train_rows = ADULT_FORECAST_MIN_TRAIN_ROWS) {
  eligible <- forecast_eligible_days(
    .forecast_daily_summary(dat),
    test_end = test_end,
    min_rows = min_train_rows,
    min_days = ADULT_FORECAST_MIN_TRAIN_DAYS
  )
  picked <- select_forecast_cutoffs(eligible)
  egg_ref <- adult_forecast_egg_reference_cutoffs()
  list(
    eligible = eligible,
    shared_n = length(eligible),
    egg_reference_cutoffs = format(egg_ref),
    egg_overlap_cutoffs = format(intersect(as.Date(picked$cutoffs), egg_ref)),
    calendar = if (identical(picked$status, "ok")) "adult_inventory" else "unresolved",
    selection = picked
  )
}

.adult_forecast_business_readout <- function(sp) {
  lines <- c(
    paste0(
      "This checks whether the validated adult northern anchovy encounter model ",
      "beats two simple baselines at 24 hours ahead on CPS trawl and nearshore ",
      "survey tows. It is fishery-independent encounter evidence, not live ",
      "tracking, not a map product, and not harvest advice."
    ),
    paste0(
      "The operational numbers use the same lead-damped ocean anomaly proxy as ",
      "the egg forecast validation (NOT_ISSUED_FORECAST). They are not an ",
      "issued WCOFS or CMEMS forecast and must not be read as one."
    )
  )
  if (!is.null(sp$fit_status) && identical(sp$fit_status, "design_infeasible")) {
    return(paste(c(lines, "Adult anchovy: the cutoff rule could not be met, so no forecast score is reported."), collapse = "\n\n"))
  }
  n_el <- sp$n_eligible_cutoffs %||% 0L
  pooled <- sp$pooled
  if (is.null(pooled) || is.null(pooled[["24"]])) {
    return(paste(c(lines, "Adult anchovy: scores are not available."), collapse = "\n\n"))
  }
  h24 <- pooled[["24"]]
  op <- h24$operational_proxy
  per <- h24$persistence
  clim <- h24$climatology
  ora <- h24$oracle
  pass <- isTRUE(sp$pass_24h)
  if (n_el < 6L) {
    lines <- c(lines, sprintf(
      "Adult anchovy: only %d of 8 cutoffs produced a usable fit. Six are required, so this is INSUFFICIENT for a pass/fail product claim.",
      n_el
    ))
    return(paste(lines, collapse = "\n\n"))
  }
  verdict <- if (pass) {
    sprintf(
      "Adult anchovy at 24 hours: NOT_ISSUED_FORECAST proxy AUC %s and TSS %s beat persistence (AUC %s, TSS %s) and day-of-year climatology (AUC %s, TSS %s) on %s common-support events (%s presences). PASS.",
      .forecast_fmt(op$auc), .forecast_fmt(op$tss),
      .forecast_fmt(per$auc), .forecast_fmt(per$tss),
      .forecast_fmt(clim$auc), .forecast_fmt(clim$tss),
      .forecast_count(h24$n_common_support), .forecast_count(op$n_presence)
    )
  } else {
    sprintf(
      "Adult anchovy at 24 hours: NOT_ISSUED_FORECAST proxy AUC %s and TSS %s do not beat both baselines (persistence AUC %s, TSS %s; climatology AUC %s, TSS %s) on %s common-support events (%s presences). FAIL.",
      .forecast_fmt(op$auc), .forecast_fmt(op$tss),
      .forecast_fmt(per$auc), .forecast_fmt(per$tss),
      .forecast_fmt(clim$auc), .forecast_fmt(clim$tss),
      .forecast_count(h24$n_common_support), .forecast_count(op$n_presence)
    )
  }
  lines <- c(
    lines,
    verdict,
    sprintf(
      "Retrospective oracle ceiling at 24 h (analysed GLORYS, not the product): AUC %s, TSS %s.",
      .forecast_fmt(ora$auc), .forecast_fmt(ora$tss)
    )
  )
  paste(lines, collapse = "\n\n")
}

#' Run adult anchovy rolling-origin forecast validation and write prereg outputs.
#' @export
run_adult_anchovy_24h_forecast <- function(
  root = NULL,
  inventory_only = FALSE,
  checkpoint_dir = NULL,
  scores_json = NULL,
  readout_md = NULL,
  min_train_rows = ADULT_FORECAST_MIN_TRAIN_ROWS
) {
  root <- root %||% Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  scores_json <- scores_json %||% file.path(root, "prereg", "adult_anchovy_24h_forecast_scores.json")
  readout_md <- readout_md %||% file.path(root, "prereg", "adult_anchovy_24h_forecast_readout.md")
  checkpoint_dir <- checkpoint_dir %||% file.path(root, "artifacts", "adult_anchovy_24h_forecast", "checkpoints")
  model_config <- "configs/models/adult_cps_anchovy.yaml"
  cfg <- load_config_yaml(file.path(root, model_config))
  .ensure_barrier_land_rds(cfg, root)
  dat <- load_model_data(cfg = cfg, min_duration_min = 2)
  dat <- .forecast_prepare_frame(dat, cfg)
  test_end <- adult_forecast_test_end(dat)
  locked <- adult_forecast_lock_cutoffs(dat, test_end, min_train_rows = min_train_rows)
  manifest <- list(
    status = if (inventory_only) "cutoffs_locked" else "ok",
    claim = "24h adult anchovy encounter forecast skill (rolling-origin holdout)",
    operational_claim = FORECAST_OPERATIONAL_CLAIM,
    physics_source = FORECAST_PHYSICS_SOURCE,
    tau_days = FORECAST_TAU_DAYS,
    lane_oracle = "retrospective",
    code_sha = Sys.getenv("GITHUB_SHA", unset = NA_character_),
    design = "prereg/adult_anchovy_24h_forecast_design.md",
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
  if (!identical(locked$selection$status, "ok")) {
    manifest$status <- "design_infeasible"
    .forecast_write_outputs(manifest, character(), scores_json, readout_md)
    return(manifest)
  }
  if (inventory_only) {
    .forecast_write_outputs(manifest, character(), scores_json, readout_md)
    return(manifest)
  }
  label <- "adult_anchovy"
  pieces <- list()
  for (cutoff in locked$selection$cutoffs) {
    path <- .forecast_checkpoint_path(checkpoint_dir, label, cutoff)
    if (file.exists(path)) {
      pieces[[length(pieces) + 1L]] <- readRDS(path)
      message("ADULT_FORECAST_CUTOFF_SKIPPED ", format(cutoff))
      next
    }
    message("ADULT_FORECAST_CUTOFF_START ", format(cutoff))
    piece <- tryCatch(
      forecast_fit_cutoff(dat, cfg, cutoff),
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
  readout <- .adult_forecast_business_readout(sp)
  manifest$species <- list(sp)
  manifest$pass_24h <- list(adult_anchovy = sp$pass_24h)
  .forecast_write_outputs(manifest, readout, scores_json, readout_md)
  manifest
}
