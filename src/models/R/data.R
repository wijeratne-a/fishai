#' Load model-ready observation table.
#'
#' Production ingest provides ``cufes_events`` (one row per ``event_id`` with
#' start/stop positions and ``volume_m3``), ``cufes_counts`` (long counts by
#' taxon), and along-track covariates keyed by ``event_id`` only (PR #2).
#' Only events with a ``cufes_counts`` row for ``species.taxon`` enter the
#' modelling frame; absent rows are **not** zeros (see ``excluded_no_count_row``
#' in QC). Events are placed on the mesh at the track midpoint in UTM zone 11N (km).
#' Effort enters as ``log(volume_m3)`` via ``log_effort``; [fit_delta_engine()]
#' passes that column to sdmTMB as ``offset`` on both Poisson-link delta
#' components.
#'
#' @param path Deprecated single-table override (tests only).
#' @param cfg Config with `data`, `response`, and `covariates` blocks.
#' @param min_duration_min Optional; drop events with ``duration_min`` below this threshold.
#' @param exclude_short_events If TRUE, keep only rows with ``short_event == FALSE`` (#4 column).
#' @param egg_split_scope ``fit`` (default training frame), ``test``, or ``all`` (fit + test windows).
#' @return Data frame with `event_id`, `X`, `Y`, `y`, `log_effort`, and `*_z`
#'   covariates. Attribute `fishai_data_qc` holds drop counts (never imputed).
#' @export
load_model_data <- function(
  path = NULL,
  cfg = NULL,
  min_duration_min = NULL,
  exclude_short_events = NULL,
  egg_split_scope = "fit"
) {
  if (is.null(cfg)) {
    stop("cfg is required", call. = FALSE)
  }

  qc <- list(
    dropped_missing_endpoint = 0L,
    dropped_missing_covariate = list(),
    excluded_no_count_row = 0L,
    dropped_short_duration = 0L,
    dropped_short_event = 0L,
    dropped_unavailable_covariates = character(),
    taxon = NA_character_,
    join_drop_event_ids = character()
  )

  min_duration_min <- min_duration_min %||% cfg$data$min_duration_min %||% cfg$sensitivity$min_duration_min
  exclude_short_events <- exclude_short_events %||% cfg$data$exclude_short_events %||% FALSE

  effort_col <- cfg$response$effort_column %||% "volume_m3"
  resp_col <- cfg$response$column %||% "egg_count"

  taxon_eligible_ids <- character()
  taxon_positive_ids <- character()
  events_for_dist <- NULL

  if (!is.null(cfg$data$events_path) && !is.null(cfg$data$counts_path)) {
    events <- .read_model_table(cfg$data$events_path)
    events <- .normalize_cufes_events_columns(events)
    .validate_cufes_events_schema(events)
    events <- .attach_spatial_fold_ids(events, cfg)
    assert_no_open_review_flags(cfg)
    if (!is.null(cfg$data$event_count_guard)) {
      .assert_event_count_guard(events, cfg$data$event_count_guard, cfg$species$taxon %||% "unknown")
    }
    counts <- .read_model_table(cfg$data$counts_path)
    .validate_cufes_counts(counts)
    taxon <- cfg$species$taxon
    if (is.null(taxon) || !nzchar(taxon)) {
      stop("species.taxon is required to select rows from cufes_counts", call. = FALSE)
    }
    if (!"event_id" %in% names(events)) {
      stop("cufes_events missing event_id column", call. = FALSE)
    }
    .assert_unique_keys(events$event_id, "event_id in cufes_events")
    counts_taxon <- counts[counts$taxon == taxon, , drop = FALSE]
    .assert_unique_keys(counts_taxon$event_id, paste0("event_id in cufes_counts (taxon=", taxon, ")"))
    qc$taxon <- taxon
    events_for_dist <- events
    ev_ids <- unique(as.character(events$event_id))
    taxon_count_ids <- unique(as.character(counts_taxon$event_id))
    taxon_eligible_ids <- taxon_count_ids
    taxon_positive_ids <- as.character(counts_taxon$event_id[as.numeric(counts_taxon$count) > 0])
    qc$excluded_no_count_row <- as.integer(length(setdiff(ev_ids, taxon_count_ids)))
    dat <- merge(
      events,
      counts_taxon[, c("event_id", "count"), drop = FALSE],
      by = "event_id",
      sort = FALSE
    )
    if (nrow(dat) == 0L) {
      stop(
        "no events with a cufes_counts row for taxon=",
        taxon,
        "; missing count rows are not treated as zero",
        call. = FALSE
      )
    }
    dat[[resp_col]] <- dat$count
    dat$count <- NULL

    cov_path <- cfg$data$covariates_path
    if (is.null(cov_path) || !nzchar(cov_path)) {
      stop("data.covariates_path is required with events_path + counts_path", call. = FALSE)
    }
    cov <- .read_model_table(cov_path)
    if (!"event_id" %in% names(cov)) {
      stop("covariate table missing event_id", call. = FALSE)
    }
    if (!"excluded" %in% names(cov)) {
      stop("covariate table missing excluded column", call. = FALSE)
    }
    .assert_unique_keys(cov$event_id, "event_id in covariates")
    drops <- .read_covariate_drop_table(cfg$data$covariate_drops_path)
    .validate_covariate_drop_events(drops, events)
    .validate_excluded_vs_drop_table(cov, drops)
    cov <- cov[cov$event_id %in% dat$event_id, , drop = FALSE]
    joined <- .join_covariates_bot2(dat, cov, cfg)
    dat <- joined$dat
    cfg <- joined$cfg
    qc$dropped_unavailable_covariates <- joined$dropped_unavailable %||% character()
    if (!is.null(drops) && nrow(drops)) {
      qc$join_drop_event_ids <- .join_drop_event_ids(drops)
    }
  } else {
    table_path <- path %||% cfg$data$table_path
    if (is.null(table_path) || !nzchar(table_path)) {
      stop("set data.table_path or data.events_path + data.counts_path + data.covariates_path", call. = FALSE)
    }
    dat <- .read_model_table(table_path)
    id_col <- .resolve_event_id_column(dat)
    dat$event_id <- dat[[id_col]]
    .assert_unique_keys(dat$event_id, "event_id")
  }

  if (!effort_col %in% names(dat)) {
    stop("missing effort column: ", effort_col, call. = FALSE)
  }
  if (!resp_col %in% names(dat)) {
    stop("missing response column: ", resp_col, call. = FALSE)
  }

  bad_effort <- is.na(dat[[effort_col]]) | dat[[effort_col]] <= 0
  if (any(bad_effort)) {
    stop(
      sum(bad_effort),
      " rows with missing or non-positive effort; drop upstream (never zero-fill).",
      call. = FALSE
    )
  }

  if (any(is.na(dat[[resp_col]]))) {
    stop("missing response values are not allowed (QC failures must be dropped).", call. = FALSE)
  }

  prep <- .add_track_midpoint_xy(dat)
  dat <- prep$dat
  if (!is.null(prep$dropped_missing_endpoint)) {
    qc$dropped_missing_endpoint <- prep$dropped_missing_endpoint
  }

  cov_prep <- .map_and_drop_covariates(dat, cfg)
  dat <- cov_prep$dat
  cfg <- cov_prep$cfg
  dat <- .ensure_time_idx(dat, cfg)

  short_filt <- .apply_short_event_filter(dat, exclude_short_events)
  dat <- short_filt$dat
  if (!is.null(short_filt$dropped_short_event)) {
    qc$dropped_short_event <- short_filt$dropped_short_event
  }

  dur <- .apply_min_duration_filter(dat, min_duration_min)
  dat <- dur$dat
  if (!is.null(dur$dropped_short_duration)) {
    qc$dropped_short_duration <- dur$dropped_short_duration
  }
  if (nrow(dat) == 0L) {
    stop("no events remain after data prep filters", call. = FALSE)
  }

  if (!is.null(cfg$egg_split)) {
    dat <- filter_egg_split_scope(dat, cfg, scope = egg_split_scope)
  }

  dat$y <- dat[[resp_col]]
  dat$log_effort <- log(dat[[effort_col]])
  attr(dat, "fishai_data_qc") <- qc
  if (length(taxon_eligible_ids)) {
    attr(dat, "fishai_taxon_eligible_event_ids") <- taxon_eligible_ids
    attr(dat, "fishai_taxon_positive_event_ids") <- taxon_positive_ids
    if (!is.null(events_for_dist) && "dist_shore_km" %in% names(events_for_dist)) {
      attr(dat, "fishai_dist_shore_km_by_event") <- stats::setNames(
        as.numeric(events_for_dist$dist_shore_km),
        as.character(events_for_dist$event_id)
      )
    }
    if (!is.null(events_for_dist) && "short_event" %in% names(events_for_dist)) {
      attr(dat, "fishai_short_event_by_event") <- stats::setNames(
        .parse_short_event_logical(events_for_dist$short_event),
        as.character(events_for_dist$event_id)
      )
    }
  }
  dat
}

.cufes_events_required_columns <- function() {
  c(
    "event_id",
    "time",
    "lat",
    "lon",
    "stop_time",
    "stop_lat",
    "stop_lon",
    "volume_m3",
    "pump_readings_used",
    "duration_min",
    "short_event"
  )
}

.normalize_cufes_events_columns <- function(events) {
  out <- events
  if ("start_time" %in% names(out) && !"time" %in% names(out)) {
    out$time <- out$start_time
  }
  if ("start_latitude" %in% names(out) && !"lat" %in% names(out)) {
    out$lat <- out$start_latitude
  }
  if ("start_longitude" %in% names(out) && !"lon" %in% names(out)) {
    out$lon <- out$start_longitude
  }
  if ("stop_latitude" %in% names(out) && !"stop_lat" %in% names(out)) {
    out$stop_lat <- out$stop_latitude
  }
  if ("stop_longitude" %in% names(out) && !"stop_lon" %in% names(out)) {
    out$stop_lon <- out$stop_longitude
  }
  out
}

.validate_cufes_events_schema <- function(events) {
  req <- .cufes_events_required_columns()
  missing <- setdiff(req, names(events))
  if (length(missing)) {
    stop(
      "cufes_events missing required columns: ",
      paste(missing, collapse = ", "),
      call. = FALSE
    )
  }
  pumps <- as.integer(events$pump_readings_used)
  if (any(!pumps %in% c(1L, 2L))) {
    stop("pump_readings_used must be 1 or 2 on every cufes_events row", call. = FALSE)
  }
  invisible(TRUE)
}

.validate_cufes_counts <- function(counts) {
  if (!all(c("event_id", "taxon", "count") %in% names(counts))) {
    stop("cufes_counts must include event_id, taxon, count", call. = FALSE)
  }
  if (any(is.na(counts$count))) {
    stop(
      "cufes_counts must not contain NA counts; ERDDAP NaN means taxon not sampled (omit row)",
      call. = FALSE
    )
  }
  invisible(TRUE)
}

.read_covariate_drop_table <- function(path) {
  if (is.null(path) || !nzchar(path)) {
    return(NULL)
  }
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  if (!grepl("^/", path)) {
    path <- file.path(root, path)
  }
  if (!file.exists(path)) {
    stop("covariate_drops_path not found: ", path, call. = FALSE)
  }
  drops <- .read_model_table(path)
  need <- c("event_id", "reason", "covariate", "latitude", "longitude")
  if (!all(need %in% names(drops))) {
    stop(
      "covariate drop table must include: ",
      paste(need, collapse = ", "),
      call. = FALSE
    )
  }
  drops
}

.covariate_drop_reason_keys <- function() {
  c(
    "missing_endpoint",
    "land_mask",
    "too_few_track_points",
    "missing_covariate"
  )
}

.read_covariate_drop_summary <- function(path) {
  if (is.null(path) || !nzchar(path)) {
    return(NULL)
  }
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  if (!grepl("^/", path)) {
    path <- file.path(root, path)
  }
  if (!file.exists(path)) {
    stop("covariate_drop_summary_path not found: ", path, call. = FALSE)
  }
  raw <- jsonlite::read_json(path, simplifyVector = TRUE)
  if (is.null(raw$input_event_count)) {
    stop("covariate drop summary missing input_event_count", call. = FALSE)
  }
  raw
}

.summary_reason_value <- function(summary, block, reason) {
  obj <- summary[[block]]
  if (is.null(obj)) {
    return(NA_integer_)
  }
  if (is.list(obj) || is.vector(obj)) {
    if (!reason %in% names(obj)) {
      return(NA_integer_)
    }
    return(as.integer(obj[[reason]]))
  }
  if (is.data.frame(obj) && reason %in% names(obj)) {
    return(as.integer(obj[[reason]][[1L]]))
  }
  NA_integer_
}

.assert_covariate_drop_summary_reason_blocks <- function(summary) {
  keys <- .covariate_drop_reason_keys()
  for (block in c("unique_by_reason", "rows_by_reason")) {
    obj <- summary[[block]]
    if (is.null(obj)) {
      stop("covariate drop summary missing ", block, call. = FALSE)
    }
    got <- sort(names(obj))
    exp <- sort(keys)
    if (!identical(got, exp)) {
      stop(
        "covariate drop summary ",
        block,
        " must include exactly: ",
        paste(keys, collapse = ", "),
        call. = FALSE
      )
    }
  }
  invisible(TRUE)
}

.assert_bot2_covariate_join_counts <- function(cfg) {
  guard <- cfg$data$event_count_guard
  if (is.null(guard) || is.null(guard$n_events)) {
    return(invisible(TRUE))
  }
  expected <- as.integer(guard$n_events)
  summary_path <- cfg$data$covariate_drop_summary_path
  if (is.null(summary_path) || !nzchar(summary_path)) {
    stop(
      "event_count_guard is set but data.covariate_drop_summary_path is missing",
      call. = FALSE
    )
  }
  summary <- .read_covariate_drop_summary(summary_path)
  schema_version <- summary$schema_version
  if (is.null(schema_version) || as.integer(schema_version) != 1L) {
    stop(
      "covariate drop summary schema_version must be 1, got ",
      if (is.null(schema_version)) "NULL" else schema_version,
      call. = FALSE
    )
  }
  .assert_covariate_drop_summary_reason_blocks(summary)
  drops_path <- cfg$data$covariate_drops_path
  if (is.null(drops_path) || !nzchar(drops_path)) {
    stop(
      "data.covariate_drops_path is required to validate covariate drop summary",
      call. = FALSE
    )
  }
  drops <- .read_covariate_drop_table(drops_path)
  drop_ids <- unique(as.character(drops$event_id))
  n_unique_drop_events <- length(drop_ids)
  dropped_total <- as.integer(summary$dropped_unique_total)
  if (is.na(dropped_total)) {
    stop("covariate drop summary missing dropped_unique_total", call. = FALSE)
  }
  if (dropped_total != n_unique_drop_events) {
    stop(
      "covariate drop summary dropped_unique_total (",
      dropped_total,
      ") != unique event_id count in drop table (",
      n_unique_drop_events,
      ")",
      call. = FALSE
    )
  }
  cov_path <- cfg$data$covariates_path
  if (is.null(cov_path) || !nzchar(cov_path)) {
    stop(
      "data.covariates_path is required to validate covariate output row count",
      call. = FALSE
    )
  }
  cov <- .read_model_table(cov_path)
  if (!"event_id" %in% names(cov)) {
    stop("covariate table missing event_id column", call. = FALSE)
  }
  if (!"excluded" %in% names(cov)) {
    stop("covariate table missing excluded column", call. = FALSE)
  }
  .assert_unique_keys(cov$event_id, "event_id in covariates")
  ex <- .parse_excluded_logical(cov$excluded)
  n_excluded <- sum(ex %in% TRUE)
  if (dropped_total != n_excluded) {
    stop(
      "covariate drop summary dropped_unique_total (",
      dropped_total,
      ") != excluded=TRUE row count (",
      n_excluded,
      ")",
      call. = FALSE
    )
  }
  keys <- .covariate_drop_reason_keys()
  for (reason in keys) {
    sub <- drops[as.character(drops$reason) == reason, , drop = FALSE]
    n_unique_reason <- length(unique(as.character(sub$event_id)))
    u <- .summary_reason_value(summary, "unique_by_reason", reason)
    if (u != n_unique_reason) {
      stop(
        "covariate drop summary unique_by_reason$",
        reason,
        " (",
        u,
        ") != unique event_id count in drop table (",
        n_unique_reason,
        ")",
        call. = FALSE
      )
    }
    r <- .summary_reason_value(summary, "rows_by_reason", reason)
    if (r != nrow(sub)) {
      stop(
        "covariate drop summary rows_by_reason$",
        reason,
        " (",
        r,
        ") != drop table row count (",
        nrow(sub),
        ")",
        call. = FALSE
      )
    }
  }
  input_n <- as.integer(summary$input_event_count)
  if (input_n != expected) {
    stop(
      "covariate drop summary input_event_count (",
      input_n,
      ") != event_count_guard n_events (",
      expected,
      "); expected post-QC bot1 events fed to covariate join, not raw ERDDAP pull",
      call. = FALSE
    )
  }
  cov_n <- nrow(cov)
  if (cov_n != expected) {
    stop(
      "covariate output row count (",
      cov_n,
      ") != event_count_guard n_events (",
      expected,
      ")",
      call. = FALSE
    )
  }
  invisible(TRUE)
}

.join_drop_event_ids <- function(drops) {
  unique(as.character(drops$event_id))
}

.parse_short_event_logical <- function(x) {
  if (is.logical(x)) {
    return(x)
  }
  if (is.numeric(x)) {
    return(as.logical(x))
  }
  lx <- tolower(trimws(as.character(x)))
  out <- rep(NA, length(lx))
  out[lx %in% c("true", "t", "1", "yes")] <- TRUE
  out[lx %in% c("false", "f", "0", "no")] <- FALSE
  out
}

#' Assert bot1 event counts before covariate join (config-driven guard).
#' @export
assert_event_count_guard <- function(events, guard, species = "unknown") {
  .assert_event_count_guard(events, guard, species)
}

.assert_event_count_guard <- function(events, guard, species) {
  if (is.null(guard)) {
    return(invisible(TRUE))
  }
  n_ev <- nrow(events)
  short <- .parse_short_event_logical(events$short_event)
  n_short <- sum(short %in% TRUE, na.rm = TRUE)
  n_long <- sum(short %in% FALSE, na.rm = TRUE)
  exp_n <- as.integer(guard$n_events)
  exp_short <- as.integer(guard$n_short_event)
  exp_long <- as.integer(guard$n_long_event)
  ok <- (n_ev == exp_n) && (n_short == exp_short) && (n_long == exp_long)
  if (!ok) {
    stop(
      "event_count_guard mismatch for taxon=",
      species,
      ": observed n_events=",
      n_ev,
      " n_short_event=",
      n_short,
      " n_long_event=",
      n_long,
      "; expected n_events=",
      exp_n,
      " n_short_event=",
      exp_short,
      " n_long_event=",
      exp_long,
      call. = FALSE
    )
  }
  invisible(TRUE)
}

.apply_short_event_filter <- function(dat, exclude_short_events) {
  if (!isTRUE(exclude_short_events)) {
    return(list(dat = dat, dropped_short_event = NULL))
  }
  if (!"short_event" %in% names(dat)) {
    stop("short_event column required for exclude_short_events filter", call. = FALSE)
  }
  short <- .parse_short_event_logical(dat$short_event)
  keep <- !(short %in% TRUE)
  dropped <- as.integer(sum(!keep))
  list(dat = dat[keep, , drop = FALSE], dropped_short_event = dropped)
}

.validate_covariate_drop_events <- function(drops, events) {
  if (is.null(drops) || !nrow(drops)) {
    return(invisible(TRUE))
  }
  drop_ids <- unique(as.character(drops$event_id))
  ev_ids <- unique(as.character(events$event_id))
  missing <- setdiff(drop_ids, ev_ids)
  if (length(missing)) {
    stop(
      "covariate drop table event_id not found in cufes_events: ",
      paste(head(missing, 5), collapse = ", "),
      call. = FALSE
    )
  }
  invisible(TRUE)
}

#' Summarize covariate-join drops for reference-volume metadata (PR #2 drop table).
#' Counts and shares use unique ``event_id`` values (not drop-table row counts).
#' @export
summarize_covariate_join_drops <- function(
  taxon_eligible_ids,
  taxon_positive_ids,
  join_drop_ids = NULL,
  drops = NULL,
  dist_by_event_id = NULL,
  short_event_by_event_id = NULL,
  nearshore_km = 20
) {
  if (!is.null(drops) && nrow(drops)) {
    join_drop_ids <- unique(as.character(drops$event_id))
  }
  if (is.null(join_drop_ids) || !length(join_drop_ids)) {
    return(NULL)
  }
  drop_ids <- unique(as.character(join_drop_ids))
  eligible <- unique(as.character(taxon_eligible_ids))
  if (!length(eligible)) {
    return(NULL)
  }
  pos_ids <- unique(as.character(taxon_positive_ids))
  if (!length(pos_ids)) {
    pos_ids <- eligible
  }
  dist_map <- dist_by_event_id
  short_map <- short_event_by_event_id
  stratum_ids <- function(ids, shore = NULL, short_only = NULL) {
    out <- ids
    if (!is.null(short_only) && length(short_map)) {
      sx <- short_map[out]
      if (isTRUE(short_only)) {
        out <- out[sx %in% TRUE]
      } else if (isFALSE(short_only)) {
        out <- out[sx %in% FALSE]
      }
    }
    if (!is.null(shore) && length(dist_map)) {
      d <- dist_map[out]
      if (shore == "nearshore") {
        out <- out[!is.na(d) & d <= nearshore_km]
      } else if (shore == "offshore") {
        out <- out[!is.na(d) & d > nearshore_km]
      }
    }
    out
  }
  drop_in_eligible <- unique(intersect(eligible, drop_ids))
  .share <- function(num, den) {
    if (!den) {
      return(NA_real_)
    }
    num / den
  }
  .stratum_drop_report <- function(ids, ddrop) {
    ddrop <- unique(intersect(ids, ddrop))
    dpos <- intersect(ids, pos_ids)
    list(
      n_dropped = length(ddrop),
      share_all_events = .share(length(ddrop), length(ids)),
      share_positive_events = .share(length(intersect(ddrop, dpos)), length(dpos))
    )
  }
  out <- list(
    n_eligible = length(eligible),
    n_join_dropped = length(drop_in_eligible),
    share_all_events = .share(length(drop_in_eligible), length(eligible)),
    share_positive_events = .share(length(intersect(drop_in_eligible, pos_ids)), length(pos_ids)),
    nearshore_max_km = nearshore_km
  )
  for (shore in c("nearshore", "offshore")) {
    ids <- stratum_ids(eligible, shore = shore)
    rep <- .stratum_drop_report(ids, drop_ids)
    out[[paste0("share_all_events_", shore)]] <- rep$share_all_events
    out[[paste0("share_positive_events_", shore)]] <- rep$share_positive_events
  }
  for (dur_label in c("short", "long")) {
    short_flag <- dur_label == "short"
    ids <- stratum_ids(eligible, short_only = short_flag)
    rep <- .stratum_drop_report(ids, drop_ids)
    out[[paste0("share_all_events_", dur_label)]] <- rep$share_all_events
    out[[paste0("share_positive_events_", dur_label)]] <- rep$share_positive_events
    for (shore in c("nearshore", "offshore")) {
      ids2 <- stratum_ids(eligible, shore = shore, short_only = short_flag)
      rep2 <- .stratum_drop_report(ids2, drop_ids)
      out[[paste0("share_all_events_", shore, "_", dur_label)]] <- rep2$share_all_events
      out[[paste0("share_positive_events_", shore, "_", dur_label)]] <- rep2$share_positive_events
    }
  }
  if (!is.null(drops) && nrow(drops) && "reason" %in% names(drops)) {
    reasons <- sort(unique(as.character(drops$reason)))
    by_reason <- list()
    for (reason in reasons) {
      reason_ids <- unique(as.character(drops$event_id[drops$reason == reason]))
      dropped_reason <- unique(intersect(eligible, reason_ids))
      by_reason[[reason]] <- list(
        n_events = length(dropped_reason),
        share_all_events = .share(length(dropped_reason), length(eligible)),
        share_positive_events = .share(
          length(intersect(dropped_reason, pos_ids)),
          length(pos_ids)
        )
      )
    }
    out$by_reason <- by_reason
  }
  out
}


#' Read data-prep QC summary from [load_model_data()] result.
#' @export
fishai_data_prep_qc <- function(dat) {
  qc <- attr(dat, "fishai_data_qc")
  if (is.null(qc)) {
    stop("dat has no fishai_data_qc attribute; use load_model_data()", call. = FALSE)
  }
  qc
}

.parse_excluded_logical <- function(x) {
  .parse_short_event_logical(x)
}

.validate_excluded_vs_drop_table <- function(cov, drops) {
  ex <- .parse_excluded_logical(cov$excluded)
  ex_ids <- unique(as.character(cov$event_id[ex %in% TRUE]))
  drop_ids <- if (is.null(drops) || !nrow(drops)) {
    character()
  } else {
    unique(as.character(drops$event_id))
  }
  if (!length(drop_ids) && length(ex_ids)) {
    stop(
      "covariate table has excluded=TRUE for ",
      length(ex_ids),
      " event(s) but no covariate drop table was provided; first ids: ",
      paste(head(ex_ids, 10L), collapse = ", "),
      call. = FALSE
    )
  }
  only_ex <- setdiff(ex_ids, drop_ids)
  only_drop <- setdiff(drop_ids, ex_ids)
  if (!length(only_ex) && !length(only_drop)) {
    return(invisible(TRUE))
  }
  mismatch <- head(c(only_ex, only_drop), 10L)
  stop(
    "excluded column inconsistent with covariate drop table; mismatched event_id: ",
    paste(mismatch, collapse = ", "),
    call. = FALSE
  )
}

.planned_covariate_gap_reasons <- function() {
  c(upwelling = "no_consistent_wind_product")
}

.covariate_status_column <- function(model_slug) {
  if (identical(model_slug, "upwelling")) {
    return("upwelling_status")
  }
  paste0(model_slug, "_status")
}

.covariate_values_all_blank <- function(vals) {
  if (is.character(vals)) {
    trim <- trimws(vals)
    return(is.na(vals) | !nzchar(trim) | toupper(trim) %in% c("NA", "NAN"))
  }
  v <- suppressWarnings(as.numeric(vals))
  is.na(vals) | is.na(v) | !is.finite(v)
}

.covariate_planned_gap_on_frame <- function(dat, model_slug, upstream_col) {
  reasons <- .planned_covariate_gap_reasons()
  if (!model_slug %in% names(reasons)) {
    return(FALSE)
  }
  expected_reason <- reasons[[model_slug]]
  if (is.null(expected_reason) || !nzchar(expected_reason)) {
    return(FALSE)
  }
  status_col <- .covariate_status_column(model_slug)
  if (!status_col %in% names(dat)) {
    return(FALSE)
  }
  if (!upstream_col %in% names(dat)) {
    return(FALSE)
  }
  ex <- if ("excluded" %in% names(dat)) {
    .parse_excluded_logical(dat$excluded)
  } else {
    rep(FALSE, nrow(dat))
  }
  keep <- !(ex %in% TRUE)
  if (!any(keep)) {
    return(FALSE)
  }
  sub <- dat[keep, , drop = FALSE]
  status_vals <- trimws(as.character(sub[[status_col]]))
  if (!all(status_vals == expected_reason)) {
    return(FALSE)
  }
  all(.covariate_values_all_blank(sub[[upstream_col]]))
}

.drop_covariates_if_unavailable <- function(dat, cfg) {
  dropped <- character()
  upstream_map <- cfg$covariates$upstream_fields %||% .default_upstream_covariate_map()
  dyn <- cfg$covariates$dynamic %||% character()
  static <- cfg$covariates$static %||% character()
  if (!length(dyn) && !length(static)) {
    return(list(dat = dat, cfg = cfg, dropped_unavailable = dropped))
  }
  slugs <- c(dyn, static)
  for (slug in slugs) {
    upstream <- upstream_map[[slug]]
    if (is.null(upstream) || (length(upstream) == 1L && is.na(upstream))) {
      upstream <- slug
    }
    if (!.covariate_planned_gap_on_frame(dat, slug, upstream)) {
      next
    }
    dropped <- c(dropped, slug)
    cfg$covariates$dynamic <- setdiff(cfg$covariates$dynamic, slug)
    cfg$covariates$static <- setdiff(cfg$covariates$static, slug)
    model_col <- paste0(slug, "_z")
    if (model_col %in% names(dat)) {
      dat[[model_col]] <- NULL
    }
  }
  list(dat = dat, cfg = cfg, dropped_unavailable = dropped)
}

.join_covariates_bot2 <- function(events, cov, cfg) {
  ev_ids <- sort(unique(as.character(events$event_id)))
  cov_ids <- sort(unique(as.character(cov$event_id)))
  if (!identical(ev_ids, cov_ids)) {
    only_ev <- setdiff(ev_ids, cov_ids)
    only_cov <- setdiff(cov_ids, ev_ids)
    stop(
      "event_id set mismatch between events and covariates; ",
      "only in events: ",
      paste(head(only_ev, 5), collapse = ", "),
      "; only in covariates: ",
      paste(head(only_cov, 5), collapse = ", "),
      call. = FALSE
    )
  }
  cov <- cov[match(events$event_id, cov$event_id), , drop = FALSE]
  extra_cov_cols <- setdiff(names(cov), "event_id")
  for (col in extra_cov_cols) {
    events[[col]] <- cov[[col]]
  }
  .assert_glorys_covariate_source_product(events, cfg)
  drop_res <- .drop_covariates_if_unavailable(events, cfg)
  events <- drop_res$dat
  cfg <- drop_res$cfg
  dropped_unavailable <- drop_res$dropped_unavailable
  events <- .map_model_covariates(events, cfg)
  .assert_non_excluded_covariates_complete(events, cfg)
  ex <- .parse_excluded_logical(events$excluded)
  events <- events[!(ex %in% TRUE), , drop = FALSE]
  if (nrow(events) == 0L) {
    stop("no events remain after excluding covariate-join failures", call. = FALSE)
  }
  list(dat = events, cfg = cfg, dropped_unavailable = dropped_unavailable)
}

.map_model_covariates <- function(dat, cfg) {
  model_cols <- .model_covariate_columns(cfg)
  if (!length(model_cols)) {
    return(dat)
  }
  upstream_map <- cfg$covariates$upstream_fields %||% .default_upstream_covariate_map()
  for (model_col in model_cols) {
    slug <- sub("_z$", "", model_col)
    upstream <- upstream_map[[slug]]
    if (is.null(upstream) || (length(upstream) == 1L && is.na(upstream))) {
      upstream <- model_col
    }
    if (upstream %in% names(dat)) {
      dat[[model_col]] <- dat[[upstream]]
    } else if (!model_col %in% names(dat)) {
      stop("missing covariate column: ", upstream, " (model ", model_col, ")", call. = FALSE)
    }
  }
  dat
}

.assert_non_excluded_covariates_complete <- function(dat, cfg) {
  ex <- .parse_excluded_logical(dat$excluded)
  keep <- !(ex %in% TRUE)
  if (!any(keep)) {
    return(invisible(TRUE))
  }
  sub <- dat[keep, , drop = FALSE]
  model_cols <- .model_covariate_columns(cfg)
  upstream_map <- cfg$covariates$upstream_fields %||% .default_upstream_covariate_map()
  for (model_col in model_cols) {
    slug <- sub("_z$", "", model_col)
    upstream <- upstream_map[[slug]]
    if (is.null(upstream) || (length(upstream) == 1L && is.na(upstream))) {
      upstream <- model_col
    }
    col <- if (model_col %in% names(sub)) model_col else upstream
    if (!col %in% names(sub)) {
      stop("missing covariate column for non-excluded event: ", col, call. = FALSE)
    }
    vals <- sub[[col]]
    if (is.character(vals)) {
      bad <- is.na(vals) | !nzchar(trimws(vals))
    } else {
      bad <- is.na(vals) | !is.finite(as.numeric(vals))
    }
    if (any(bad)) {
      stop(
        "non-excluded event has missing covariate value in ",
        col,
        " (never impute or silently drop)",
        call. = FALSE
      )
    }
  }
  invisible(TRUE)
}

.map_and_assert_covariates <- function(dat, cfg) {
  if ("excluded" %in% names(dat)) {
    return(list(dat = dat))
  }
  dat <- .map_model_covariates(dat, cfg)
  .assert_non_excluded_covariates_complete(
    data.frame(excluded = FALSE, dat, stringsAsFactors = FALSE),
    cfg
  )
  list(dat = dat)
}

.add_track_midpoint_xy <- function(dat) {
  cols <- .resolve_track_endpoint_columns(names(dat))
  if (is.null(cols)) {
    if (all(c("X", "Y") %in% names(dat))) {
      return(list(dat = dat, dropped_missing_endpoint = NULL))
    }
    stop(
      "events need start/stop positions (lat/lon or start_latitude/start_longitude) or X/Y",
      call. = FALSE
    )
  }
  lat0 <- dat[[cols$start_lat]]
  lon0 <- dat[[cols$start_lon]]
  lat1 <- dat[[cols$stop_lat]]
  lon1 <- dat[[cols$stop_lon]]
  missing <- .endpoint_missing(lat0, lon0, lat1, lon1)
  dropped <- NULL
  if (any(missing)) {
    dropped <- as.integer(sum(missing))
    dat <- dat[!missing, , drop = FALSE]
  }
  if (nrow(dat) == 0L) {
    stop("no events remain after dropping missing track endpoints", call. = FALSE)
  }
  mid <- .track_midpoint_km(
    dat[[cols$start_lon]],
    dat[[cols$start_lat]],
    dat[[cols$stop_lon]],
    dat[[cols$stop_lat]]
  )
  dat$X <- mid$X
  dat$Y <- mid$Y
  list(dat = dat, dropped_missing_endpoint = dropped)
}

.endpoint_missing <- function(lat0, lon0, lat1, lon1) {
  is.na(lat0) | is.na(lon0) | is.na(lat1) | is.na(lon1)
}

.resolve_track_endpoint_columns <- function(nms) {
  start_lat <- if ("lat" %in% nms) {
    "lat"
  } else if ("start_latitude" %in% nms) {
    "start_latitude"
  } else if ("latitude" %in% nms) {
    "latitude"
  } else {
    NULL
  }
  start_lon <- if ("lon" %in% nms) {
    "lon"
  } else if ("start_longitude" %in% nms) {
    "start_longitude"
  } else if ("longitude" %in% nms) {
    "longitude"
  } else {
    NULL
  }
  stop_lat <- if ("stop_lat" %in% nms) {
    "stop_lat"
  } else if ("stop_latitude" %in% nms) {
    "stop_latitude"
  } else {
    NULL
  }
  stop_lon <- if ("stop_lon" %in% nms) {
    "stop_lon"
  } else if ("stop_longitude" %in% nms) {
    "stop_longitude"
  } else {
    NULL
  }
  if (is.null(start_lat) || is.null(start_lon) || is.null(stop_lat) || is.null(stop_lon)) {
    return(NULL)
  }
  list(
    start_lat = start_lat,
    start_lon = start_lon,
    stop_lat = stop_lat,
    stop_lon = stop_lon
  )
}

#' Track midpoint in EPSG:32611 (WGS 84 / UTM 11N), returned in km.
.track_midpoint_km <- function(start_lon, start_lat, stop_lon, stop_lat, epsg = 32611L) {
  if (!requireNamespace("sf", quietly = TRUE)) {
    stop("sf is required to project CUFES track midpoints", call. = FALSE)
  }
  start_lon <- as.numeric(start_lon)
  start_lat <- as.numeric(start_lat)
  stop_lon <- as.numeric(stop_lon)
  stop_lat <- as.numeric(stop_lat)
  n <- length(start_lon)
  x_km <- numeric(n)
  y_km <- numeric(n)
  crs_wgs <- sf::st_crs(4326)
  crs_utm <- sf::st_crs(epsg)
  for (i in seq_len(n)) {
    p1 <- sf::st_transform(
      sf::st_sfc(sf::st_point(c(start_lon[[i]], start_lat[[i]])), crs = crs_wgs),
      crs_utm
    )
    p2 <- sf::st_transform(
      sf::st_sfc(sf::st_point(c(stop_lon[[i]], stop_lat[[i]])), crs = crs_wgs),
      crs_utm
    )
    m <- (sf::st_coordinates(p1) + sf::st_coordinates(p2)) / 2
    x_km[[i]] <- m[1, "X"] / 1000
    y_km[[i]] <- m[1, "Y"] / 1000
  }
  list(X = x_km, Y = y_km)
}

.default_upstream_covariate_map <- function() {
  c(
    temp_3m = "T3m",
    sal_3m = "S3m",
    mld = "MLD_m",
    sst_grad = "sst_grad",
    dist_front = "front_distance_km",
    upwelling = "upwelling",
    log_depth = "log_depth_z"
  )
}

.model_covariate_columns <- function(cfg) {
  dyn <- cfg$covariates$dynamic %||% character()
  static <- cfg$covariates$static %||% character()
  c(paste0(dyn, "_z"), paste0(static, "_z"))
}

.map_and_drop_covariates <- function(dat, cfg) {
  if ("excluded" %in% names(dat)) {
    return(list(dat = dat, cfg = cfg))
  }
  drop_res <- .drop_covariates_if_unavailable(dat, cfg)
  dat <- drop_res$dat
  cfg <- drop_res$cfg
  dat <- .map_model_covariates(dat, cfg)
  .assert_non_excluded_covariates_complete(
    data.frame(excluded = FALSE, dat, stringsAsFactors = FALSE),
    cfg
  )
  list(dat = dat, cfg = cfg)
}

.time_idx_origin_date <- function(cfg) {
  raw <- cfg$data$time_idx_origin
  if (is.null(raw) || length(raw) != 1L || is.na(raw) || !nzchar(trimws(as.character(raw)))) {
    stop(
      "data.time_idx_origin is required to derive time_idx from event time ",
      "(one fixed ISO date shared by fit, test, and all scopes)",
      call. = FALSE
    )
  }
  txt <- trimws(as.character(raw))
  origin <- if (grepl("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", txt)) {
    as.Date(txt, format = "%Y-%m-%d")
  } else {
    as.Date(NA)
  }
  if (is.na(origin)) {
    stop("data.time_idx_origin must be a valid ISO date (YYYY-MM-DD), got: ", txt, call. = FALSE)
  }
  origin
}

.ensure_time_idx <- function(dat, cfg) {
  if ("time_idx" %in% names(dat)) {
    dat$time_idx <- as.integer(dat$time_idx)
    return(dat)
  }
  if ("time" %in% names(dat)) {
    origin <- .time_idx_origin_date(cfg)
    tt <- as.POSIXct(dat$time, tz = "UTC")
    if (any(is.na(tt))) {
      stop("could not parse event time for time_idx", call. = FALSE)
    }
    idx <- as.integer(as.Date(tt) - origin) + 1L
    if (any(idx < 1L)) {
      stop(
        "event time precedes data.time_idx_origin (",
        format(origin),
        "); time_idx must be >= 1",
        call. = FALSE
      )
    }
    dat$time_idx <- idx
    return(dat)
  }
  stop("events need time_idx or time for sdmTMB time index", call. = FALSE)
}

.apply_min_duration_filter <- function(dat, min_duration_min) {
  if (is.null(min_duration_min)) {
    return(list(dat = dat, dropped_short_duration = NULL))
  }
  if (!"duration_min" %in% names(dat)) {
    stop("duration_min column required for min-duration filter", call. = FALSE)
  }
  dur <- as.numeric(dat$duration_min)
  keep <- !is.na(dur) & dur >= min_duration_min
  dropped <- as.integer(sum(!keep))
  list(
    dat = dat[keep, , drop = FALSE],
    dropped_short_duration = dropped
  )
}

.read_model_table <- function(path) {
  ext <- tolower(tools::file_ext(path))
  if (ext == "csv") {
    return(utils::read.csv(path, stringsAsFactors = FALSE, check.names = FALSE))
  }
  if (ext %in% c("parquet", "pq")) {
    if (!requireNamespace("arrow", quietly = TRUE)) {
      stop("Parquet requires arrow; use CSV in tests or add arrow to renv.", call. = FALSE)
    }
    return(as.data.frame(arrow::read_parquet(path)))
  }
  stop("unsupported table format: ", ext, call. = FALSE)
}

.resolve_event_id_column <- function(dat) {
  if ("event_id" %in% names(dat)) {
    return("event_id")
  }
  if ("sample_id" %in% names(dat)) {
    return("sample_id")
  }
  stop("missing event_id column (sample_id accepted as alias)", call. = FALSE)
}

.assert_unique_keys <- function(keys, label = "event_id") {
  keys <- as.character(keys)
  if (any(is.na(keys)) || any(!nzchar(keys))) {
    stop("missing or empty ", label, call. = FALSE)
  }
  if (anyDuplicated(keys)) {
    dup <- unique(keys[duplicated(keys)])
    stop(
      "duplicate ",
      label,
      "; refuse ambiguous rows: ",
      paste(head(dup, 5), collapse = ", "),
      call. = FALSE
    )
  }
  invisible(TRUE)
}
