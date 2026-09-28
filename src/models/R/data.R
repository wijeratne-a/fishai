#' Load model-ready observation table.
#'
#' Production ingest provides ``cufes_events`` (one row per ``event_id`` with
#' start/stop positions and ``volume_m3``), ``cufes_counts`` (long counts by
#' taxon), and along-track covariates keyed by ``event_id`` only (PR #2).
#' Only events with a ``cufes_counts`` row for ``species.taxon`` enter the
#' modelling frame; absent rows are **not** zeros (see ``excluded_no_count_row``
#' in QC). Events are placed on the mesh at the track midpoint in UTM zone 11N (km).
#' Effort enters as ``log(volume_m3)`` via ``log_effort``; [fit_delta_engine()]
#' passes that column to sdmTMB as ``offset``, which applies to the **positive**
#' delta component only.
#'
#' @param path Deprecated single-table override (tests only).
#' @param cfg Config with `data`, `response`, and `covariates` blocks.
#' @param min_duration_min Optional; drop events with ``duration_min`` below this threshold.
#' @return Data frame with `event_id`, `X`, `Y`, `y`, `log_effort`, and `*_z`
#'   covariates. Attribute `fishai_data_qc` holds drop counts (never imputed).
#' @export
load_model_data <- function(path = NULL, cfg = NULL, min_duration_min = NULL) {
  if (is.null(cfg)) {
    stop("cfg is required", call. = FALSE)
  }

  qc <- list(
    dropped_missing_endpoint = 0L,
    dropped_missing_covariate = list(),
    excluded_no_count_row = 0L,
    dropped_short_duration = 0L,
    taxon = NA_character_,
    join_drop_event_ids = character()
  )

  min_duration_min <- min_duration_min %||% cfg$data$min_duration_min %||% cfg$sensitivity$min_duration_min

  effort_col <- cfg$response$effort_column %||% "volume_m3"
  resp_col <- cfg$response$column %||% "egg_count"

  taxon_eligible_ids <- character()
  taxon_positive_ids <- character()
  events_for_dist <- NULL

  if (!is.null(cfg$data$events_path) && !is.null(cfg$data$counts_path)) {
    events <- .read_model_table(cfg$data$events_path)
    events <- .normalize_cufes_events_columns(events)
    .validate_cufes_events_schema(events)
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
    .assert_unique_keys(cov$event_id, "event_id in covariates")
    cov <- cov[cov$event_id %in% dat$event_id, , drop = FALSE]
    dat <- .join_covariates_strict(dat, cov)
    drops <- .read_covariate_drop_table(cfg$data$covariate_drops_path)
    if (!is.null(drops)) {
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
  if (length(cov_prep$dropped_missing_covariate)) {
    qc$dropped_missing_covariate <- cov_prep$dropped_missing_covariate
  }
  dat <- .ensure_time_idx(dat)

  dur <- .apply_min_duration_filter(dat, min_duration_min)
  dat <- dur$dat
  if (!is.null(dur$dropped_short_duration)) {
    qc$dropped_short_duration <- dur$dropped_short_duration
  }
  if (nrow(dat) == 0L) {
    stop("no events remain after data prep filters", call. = FALSE)
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

.join_drop_event_ids <- function(drops) {
  unique(as.character(drops$event_id))
}

#' Summarize covariate-join drops for reference-volume metadata (PR #2 drop table).
#' @export
summarize_covariate_join_drops <- function(
  taxon_eligible_ids,
  taxon_positive_ids,
  join_drop_ids,
  dist_by_event_id = NULL,
  nearshore_km = 20
) {
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
  stratum_ids <- function(ids) {
    if (is.null(dist_map) || !length(dist_map)) {
      return(list(nearshore = character(), offshore = character()))
    }
    d <- dist_map[ids]
    list(
      nearshore = ids[!is.na(d) & d <= nearshore_km],
      offshore = ids[!is.na(d) & d > nearshore_km]
    )
  }
  drop_in_eligible <- intersect(eligible, drop_ids)
  .share <- function(num, den) {
    if (!den) {
      return(NA_real_)
    }
    num / den
  }
  out <- list(
    n_eligible = length(eligible),
    n_join_dropped = length(drop_in_eligible),
    share_all_events = .share(length(drop_in_eligible), length(eligible)),
    share_positive_events = .share(length(intersect(drop_in_eligible, pos_ids)), length(pos_ids)),
    nearshore_max_km = nearshore_km
  )
  for (label in c("nearshore", "offshore")) {
    ids <- stratum_ids(eligible)[[label]]
    ddrop <- intersect(ids, drop_ids)
    dpos <- intersect(ids, pos_ids)
    out[[paste0("share_all_events_", label)]] <- .share(length(ddrop), length(ids))
    out[[paste0("share_positive_events_", label)]] <- .share(length(intersect(ddrop, dpos)), length(dpos))
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

.join_covariates_strict <- function(events, cov) {
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
  events
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
  model_cols <- .model_covariate_columns(cfg)
  dropped_by_col <- list()
  if (!length(model_cols)) {
    return(list(dat = dat, dropped_missing_covariate = dropped_by_col))
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
  drop <- rep(FALSE, nrow(dat))
  for (col in model_cols) {
    if (!col %in% names(dat)) {
      next
    }
    bad <- .covariate_empty(dat[[col]])
    if (any(bad)) {
      dropped_by_col[[col]] <- as.integer(sum(bad))
      drop <- drop | bad
    }
  }
  if (any(drop)) {
    dat <- dat[!drop, , drop = FALSE]
  }
  if (nrow(dat) == 0L) {
    stop("no rows remain after dropping empty covariates", call. = FALSE)
  }
  list(dat = dat, dropped_missing_covariate = dropped_by_col)
}

.covariate_empty <- function(x) {
  if (is.character(x)) {
    return(is.na(x) | !nzchar(trimws(x)))
  }
  is.na(x)
}

.ensure_time_idx <- function(dat) {
  if ("time_idx" %in% names(dat)) {
    dat$time_idx <- as.integer(dat$time_idx)
    return(dat)
  }
  if ("time" %in% names(dat)) {
    tt <- as.POSIXct(dat$time, tz = "UTC")
    if (all(is.na(tt))) {
      stop("could not parse event time for time_idx", call. = FALSE)
    }
    origin <- min(tt, na.rm = TRUE)
    dat$time_idx <- as.integer(as.numeric(difftime(tt, origin, units = "days"))) + 1L
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
