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

#' Eight cutoffs when one or more meteorological seasons have no eligible days.
#'
#' CPS adult surveys cluster in spring/summer/fall; DJF is often empty. Take up
#' to two cutoffs per season that has eligible days, then fill toward K = 8 from
#' the remaining pool (farthest-apart dates first), keeping ``min_sep_days``.
#' @export
select_forecast_cutoffs_best_effort <- function(
  eligible,
  k = 8L,
  pair_gap_days = 365L,
  min_sep_days = 30L
) {
  eligible <- sort(unique(as.Date(eligible)))
  seasons <- c("DJF", "MAM", "JJA", "SON")
  notes <- character()
  chosen <- as.Date(character())
  for (season in seasons) {
    pool <- eligible[forecast_season(eligible) == season]
    if (length(pool) == 0L) {
      notes <- c(notes, paste0("season ", season, " has 0 eligible cutoff(s); skipped"))
      next
    }
    if (length(pool) == 1L) {
      chosen <- c(chosen, pool[[1L]])
      notes <- c(notes, paste0("season ", season, " contributes 1 cutoff (only one eligible day)"))
      next
    }
    gap <- as.integer(pool[length(pool)] - pool[1L])
    if (gap >= pair_gap_days) {
      pair <- c(pool[1L], pool[length(pool)])
    } else {
      pair <- c(pool[1L], pool[length(pool)])
      notes <- c(notes, sprintf("%s pair gap is %d days, under the %d-day target", season, gap, pair_gap_days))
    }
    chosen <- c(chosen, pair)
  }
  chosen <- unique(chosen)
  if (length(chosen) < k) {
    rest <- eligible[!eligible %in% chosen]
    while (length(chosen) < k && length(rest)) {
      best_i <- 1L
      best_score <- -1L
      for (i in seq_along(rest)) {
        d <- rest[[i]]
        sep <- min(abs(as.integer(d - chosen)))
        if (sep >= min_sep_days && sep > best_score) {
          best_score <- sep
          best_i <- i
        }
      }
      if (best_score < 0L) {
        break
      }
      chosen <- c(chosen, rest[[best_i]])
      rest <- rest[-best_i]
    }
  }
  if (length(chosen) < 6L) {
    return(list(
      status = "design_infeasible",
      reason = sprintf("only %d cutoff candidate(s) after season fill", length(chosen)),
      cutoffs = as.Date(character()),
      notes = notes
    ))
  }
  selected <- sort(unique(chosen))
  if (length(selected) > k) {
    selected <- selected[seq_len(k)]
  }
  guard <- 0L
  repeat {
    guard <- guard + 1L
    if (guard > 16L) {
      return(list(
        status = "design_infeasible",
        reason = "cutoff separation did not settle (best effort)",
        cutoffs = as.Date(character()),
        notes = notes
      ))
    }
    ord <- order(selected)
    selected <- selected[ord]
    conflict <- NA_integer_
    for (i in seq_len(length(selected) - 1L)) {
      if (as.integer(selected[i + 1L] - selected[i]) < min_sep_days) {
        conflict <- i
        break
      }
    }
    if (is.na(conflict)) {
      break
    }
    later <- selected[conflict + 1L]
    season <- forecast_season(later)
    pool <- eligible[forecast_season(eligible) == season]
    blocked <- selected[forecast_season(selected) != season]
    ok <- vapply(pool, function(d) {
      all(abs(as.integer(d - blocked)) >= min_sep_days) && !(d %in% selected)
    }, logical(1))
    if (!any(ok)) {
      return(list(
        status = "design_infeasible",
        reason = paste0("cannot separate ", format(later), " by ", min_sep_days, " days"),
        cutoffs = as.Date(character()),
        notes = notes
      ))
    }
    cand <- pool[ok]
    replacement <- cand[which.min(abs(as.integer(cand - later)))]
    notes <- c(notes, sprintf(
      "moved %s cutoff %s to %s to keep cutoffs %d days apart",
      season, format(later), format(replacement), min_sep_days
    ))
    selected[conflict + 1L] <- replacement
  }
  list(
    status = "ok",
    reason = NULL,
    cutoffs = selected[order(selected)],
    seasons = forecast_season(selected[order(selected)]),
    notes = notes
  )
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
  strict <- select_forecast_cutoffs(eligible)
  picked <- if (identical(strict$status, "ok")) {
    strict
  } else {
    select_forecast_cutoffs_best_effort(eligible)
  }
  egg_ref <- adult_forecast_egg_reference_cutoffs()
  calendar <- if (identical(picked$status, "ok")) {
    if (identical(strict$status, "ok")) "adult_inventory" else "adult_inventory_best_effort"
  } else {
    "unresolved"
  }
  list(
    eligible = eligible,
    shared_n = length(eligible),
    egg_reference_cutoffs = format(egg_ref),
    egg_overlap_cutoffs = format(intersect(as.Date(picked$cutoffs), egg_ref)),
    calendar = calendar,
    strict_four_season_status = strict$status,
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
    fails <- vapply(sp$cutoffs %||% list(), function(x) x$failure %||% "", character(1))
    fails <- fails[nzchar(fails)]
    conv <- sum(grepl("Hessian", fails, ignore.case = TRUE))
    detail <- if (conv > 0L) {
      sprintf(
        "None of the eight rolling-origin refits passed the spatial-CV convergence gate (%d cutoffs failed with non-positive-definite Hessian). Temporal training subsets drop spatial coverage compared with the full validated fit, so forecast metrics were not computed.",
        conv
      )
    } else {
      sprintf("Only %d of 8 cutoffs produced a usable fit.", n_el)
    }
    lines <- c(lines, sprintf(
      "Adult anchovy: %s Six eligible cutoffs are required; verdict is FAIL (INSUFFICIENT). NOT_ISSUED_FORECAST 24h proxy AUC/TSS were not compared to persistence or climatology.",
      detail
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
      forecast_fit_cutoff(dat, cfg, cutoff, extra_time_fill = "holdout_only"),
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
