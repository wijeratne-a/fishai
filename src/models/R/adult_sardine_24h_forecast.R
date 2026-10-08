#' Rolling-origin 24/48/72 h adult Pacific sardine encounter validation.
#'
#' Operational physics: issued WCOFS fields when the public archive covers the
#' holdout; otherwise the damped-anomaly proxy (NOT_ISSUED_FORECAST).

ADULT_FORECAST_MIN_TRAIN_ROWS <- 150L
ADULT_FORECAST_MIN_TRAIN_DAYS <- 30L

#' Calendar event days for adult CPS rolling-origin (not remapped time_idx).
#' @export
adult_forecast_prepare_frame <- function(dat, cfg) {
  if (!"time" %in% names(dat)) {
    stop("adult forecast frame missing event time", call. = FALSE)
  }
  dat$event_day <- as.Date(dat$time)
  dat$doy <- forecast_doy(dat$event_day)
  dat
}

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

#' Lock eight cutoffs on the adult CPS frame (sardine or anchovy).
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

.sardine_operational_physics_summary <- function(sp) {
  pooled <- sp$pooled
  if (is.null(pooled) || is.null(pooled[["24"]])) {
    return(list(
      operational_claim = "NOT_ISSUED_FORECAST",
      physics_source = FORECAST_PHYSICS_SOURCE,
      n_issued_wcofs = 0L,
      n_proxy = 0L
    ))
  }
  h24 <- pooled[["24"]]
  n_iss <- as.integer(h24$n_issued_wcofs %||% 0L)
  n_prx <- as.integer(h24$n_proxy %||% 0L)
  if (n_iss > 0L && n_prx > 0L) {
    claim <- "MIXED_ISSUED_AND_PROXY"
    phys <- "wcofs_issued_forecast_and_damped_anomaly_proxy"
  } else if (n_iss > 0L) {
    claim <- FORECAST_OPERATIONAL_CLAIM_ISSUED
    phys <- FORECAST_PHYSICS_SOURCE_WCOFS
  } else {
    claim <- FORECAST_OPERATIONAL_CLAIM
    phys <- FORECAST_PHYSICS_SOURCE
  }
  list(
    operational_claim = claim,
    physics_source = phys,
    n_issued_wcofs = n_iss,
    n_proxy = n_prx
  )
}

.sardine_call_wcofs_sampler <- function(root, cutoffs) {
  if (identical(Sys.getenv("FISHAI_SKIP_WCOFS_SAMPLER", unset = ""), "1")) {
    message("WCOFS sampler skipped; using existing operational covariate table")
    return(invisible(NULL))
  }
  py <- "/tmp/fishai-venv/bin/python3"
  if (!file.exists(py)) {
    py <- Sys.which("python3")
  }
  script <- file.path(root, "scripts", "models", "sample_adult_sardine_24h_wcofs_covariates.py")
  if (!file.exists(script)) {
    stop("missing WCOFS sampler script: ", script, call. = FALSE)
  }
  cut_path <- tempfile(fileext = ".json")
  jsonlite::write_json(list(cutoffs = format(as.Date(cutoffs))), cut_path, auto_unbox = TRUE)
  out <- file.path(root, "artifacts", "adult_sardine_24h_forecast", "wcofs_operational_covariates.csv")
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
    warning(
      "WCOFS operational covariate sampler failed (exit ",
      status,
      "); operational rows will use damped-anomaly proxy only",
      call. = FALSE
    )
    return(invisible(NULL))
  }
  invisible(out)
}

.sardine_read_operational_covariates <- function(root) {
  path <- file.path(root, "artifacts", "adult_sardine_24h_forecast", "wcofs_operational_covariates.csv")
  if (!file.exists(path)) {
    return(NULL)
  }
  dat <- utils::read.csv(path, stringsAsFactors = FALSE)
  dat$event_id <- as.character(dat$event_id)
  dat$cutoff <- as.character(dat$cutoff)
  dat
}

.adult_sardine_forecast_business_readout <- function(sp, physics_summary) {
  lines <- c(
    paste0(
      "This checks whether the validated adult Pacific sardine encounter model ",
      "beats two simple baselines at 24 hours ahead on CPS trawl and nearshore ",
      "survey tows. It is fishery-independent encounter evidence, not live ",
      "tracking, not a map product, and not harvest advice."
    ),
    paste0(
      "Issued WCOFS fields are coarsened onto the GLORYS grid with no ",
      "bias-correction map applied. When the public archive does not cover a ",
      "holdout day, the operational arm uses the lead-damped anomaly proxy ",
      "(NOT_ISSUED_FORECAST)."
    )
  )
  if (!is.null(physics_summary$n_issued_wcofs) || !is.null(physics_summary$n_proxy)) {
    lines <- c(lines, sprintf(
      "Among 24 h common-support events, %s used issued WCOFS covariates and %s used the coverage-forced proxy.",
      .forecast_count(physics_summary$n_issued_wcofs %||% 0L),
      .forecast_count(physics_summary$n_proxy %||% 0L)
    ))
    if ((physics_summary$n_issued_wcofs %||% 0L) == 0L) {
      lines <- c(lines, "All operational scores are NOT_ISSUED_FORECAST; do not claim WCOFS skill.")
    }
  }
  if (!is.null(sp$fit_status) && identical(sp$fit_status, "design_infeasible")) {
    return(paste(c(lines, "Adult sardine: the cutoff rule could not be met, so no forecast score is reported."), collapse = "\n\n"))
  }
  n_el <- sp$n_eligible_cutoffs %||% 0L
  pooled <- sp$pooled
  if (is.null(pooled) || is.null(pooled[["24"]])) {
    return(paste(c(lines, "Adult sardine: scores are not available."), collapse = "\n\n"))
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
      "Adult sardine: %s Six eligible cutoffs are required; verdict is FAIL (INSUFFICIENT). Rolling-origin 24 h metrics were not pooled against persistence or climatology.",
      detail
    ))
    return(paste(lines, collapse = "\n\n"))
  }
  op_label <- if ((physics_summary$n_issued_wcofs %||% 0L) > 0L) "operational" else "NOT_ISSUED_FORECAST proxy"
  verdict <- if (pass) {
    sprintf(
      "Adult sardine at 24 hours: %s AUC %s and TSS %s beat persistence (AUC %s, TSS %s) and day-of-year climatology (AUC %s, TSS %s) on %s common-support events (%s presences). PASS.",
      op_label,
      .forecast_fmt(op$auc), .forecast_fmt(op$tss),
      .forecast_fmt(per$auc), .forecast_fmt(per$tss),
      .forecast_fmt(clim$auc), .forecast_fmt(clim$tss),
      .forecast_count(h24$n_common_support), .forecast_count(op$n_presence)
    )
  } else {
    sprintf(
      "Adult sardine at 24 hours: %s AUC %s and TSS %s do not beat both baselines (persistence AUC %s, TSS %s; climatology AUC %s, TSS %s) on %s common-support events (%s presences). FAIL.",
      op_label,
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

#' Run adult sardine rolling-origin forecast validation and write prereg outputs.
#' @export
run_adult_sardine_24h_forecast <- function(
  root = NULL,
  inventory_only = FALSE,
  checkpoint_dir = NULL,
  scores_json = NULL,
  readout_md = NULL,
  min_train_rows = ADULT_FORECAST_MIN_TRAIN_ROWS
) {
  root <- root %||% Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  scores_json <- scores_json %||% file.path(root, "prereg", "adult_sardine_24h_forecast_scores.json")
  readout_md <- readout_md %||% file.path(root, "prereg", "adult_sardine_24h_forecast_readout.md")
  checkpoint_dir <- checkpoint_dir %||% file.path(root, "artifacts", "adult_sardine_24h_forecast", "checkpoints")
  model_config <- "configs/models/adult_cps_sardine.yaml"
  cfg <- load_config_yaml(file.path(root, model_config))
  .ensure_barrier_land_rds(cfg, root)
  dat <- load_model_data(cfg = cfg, min_duration_min = 2)
  dat <- adult_forecast_prepare_frame(dat, cfg)
  test_end <- adult_forecast_test_end(dat)
  locked <- adult_forecast_lock_cutoffs(dat, test_end, min_train_rows = min_train_rows)
  manifest <- list(
    status = if (inventory_only) "cutoffs_locked" else "ok",
    claim = "24h adult sardine encounter forecast skill (rolling-origin holdout)",
    operational_claim = FORECAST_OPERATIONAL_CLAIM,
    physics_source = FORECAST_PHYSICS_SOURCE,
    operational_claim_summary = FORECAST_OPERATIONAL_CLAIM,
    physics_source_summary = FORECAST_PHYSICS_SOURCE,
    tau_days = FORECAST_TAU_DAYS,
    lane_oracle = "retrospective",
    code_sha = Sys.getenv("GITHUB_SHA", unset = NA_character_),
    design = "prereg/adult_sardine_24h_forecast_design.md",
    pass_rule = "operational AUC and TSS at 24h strictly greater than persistence and climatology, with at least 6 eligible cutoffs",
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
  .sardine_call_wcofs_sampler(root, locked$selection$cutoffs)
  op_cov <- .sardine_read_operational_covariates(root)
  label <- "adult_sardine"
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
  physics_summary <- .sardine_operational_physics_summary(sp)
  manifest$operational_claim_summary <- physics_summary$operational_claim
  manifest$physics_source_summary <- physics_summary$physics_source
  manifest$n_issued_wcofs <- physics_summary$n_issued_wcofs
  manifest$n_proxy <- physics_summary$n_proxy
  manifest$n_eligible_cutoffs <- sp$n_eligible_cutoffs
  manifest$fit_status <- sp$fit_status
  manifest$pass_24h <- isTRUE(sp$pass_24h)
  manifest$cutoffs_detail <- sp$cutoffs
  readout <- .adult_sardine_forecast_business_readout(sp, physics_summary)
  manifest$species <- list(sp)
  .forecast_write_outputs(manifest, readout, scores_json, readout_md)
  manifest
}
