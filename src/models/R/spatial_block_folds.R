#' Spatial-block CV fold assignment for CUFES events (modeling-side).
#'
#' Block size and seed come from the species model config; fold count from
#' ``data.spatial_block_cv.n_folds``. See ``docs/CUFES_DELTA_MODEL_SPEC.md``.

#' Read spatial-block CV parameters from a model config (no invented defaults).
#' @export
spatial_block_cv_params <- function(cfg) {
  block <- cfg$mesh$cutoff_km
  seed <- cfg$prediction$seed
  n_folds <- cfg$data$spatial_block_cv$n_folds
  if (is.null(block) || length(block) != 1L || !is.finite(as.numeric(block))) {
    stop("mesh.cutoff_km is required for spatial-block fold assignment", call. = FALSE)
  }
  if (is.null(seed) || length(seed) != 1L || !is.finite(as.numeric(seed))) {
    stop("prediction.seed is required for spatial-block fold assignment", call. = FALSE)
  }
  if (is.null(n_folds) || length(n_folds) != 1L || !is.finite(as.numeric(n_folds))) {
    stop(
      "data.spatial_block_cv.n_folds is required for spatial-block fold assignment",
      call. = FALSE
    )
  }
  n_folds <- as.integer(n_folds)
  if (n_folds < 2L) {
    stop("data.spatial_block_cv.n_folds must be at least 2", call. = FALSE)
  }
  list(
    block_size_km = as.numeric(block),
    seed = as.integer(seed),
    n_folds = n_folds,
    epsg = 32611L,
    block_size_source = "mesh.cutoff_km",
    seed_source = "prediction.seed",
    n_folds_source = "data.spatial_block_cv.n_folds"
  )
}

.md5_hex <- function(x) {
  f <- tempfile()
  on.exit(unlink(f), add = TRUE)
  writeLines(x, f, useBytes = TRUE)
  unname(tools::md5sum(f))
}

.fold_id_from_block <- function(block_id, seed, n_folds) {
  raw <- paste0(seed, ":", block_id)
  h <- .md5_hex(raw)
  val <- strtoi(substr(h, 1L, 7L), base = 16L)
  (val %% n_folds) + 1L
}

#' Deterministic fold table from bot1 ``cufes_events`` rows (species-agnostic).
#' @export
assign_cufes_spatial_block_folds <- function(events, params) {
  if (!"event_id" %in% names(events)) {
    stop("events missing event_id", call. = FALSE)
  }
  .assert_unique_keys(events$event_id, "event_id in cufes_events")
  cols <- .resolve_track_endpoint_columns(names(events))
  if (is.null(cols)) {
    stop("events need start/stop lat/lon for spatial-block assignment", call. = FALSE)
  }
  lat0 <- events[[cols$start_lat]]
  lon0 <- events[[cols$start_lon]]
  lat1 <- events[[cols$stop_lat]]
  lon1 <- events[[cols$stop_lon]]
  missing <- .endpoint_missing(lat0, lon0, lat1, lon1)
  if (any(missing)) {
    stop(
      sum(missing),
      " event(s) missing track endpoints; cannot assign spatial folds",
      call. = FALSE
    )
  }
  mid <- .track_midpoint_km(lon0, lat0, lon1, lat1, epsg = params$epsg %||% 32611L)
  bx <- floor(mid$X / params$block_size_km)
  by <- floor(mid$Y / params$block_size_km)
  block_id <- paste0("bx", bx, "_by", by)
  fold_id <- vapply(
    block_id,
    function(b) .fold_id_from_block(b, params$seed, params$n_folds),
    integer(1L)
  )
  out <- data.frame(
    event_id = as.character(events$event_id),
    fold_id = fold_id,
    block_id = block_id,
    stringsAsFactors = FALSE
  )
  out <- out[order(out$event_id), , drop = FALSE]
  rownames(out) <- NULL
  out
}

#' @export
write_fold_assignment_csv <- function(assignment, path) {
  path <- as.character(path)
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  req <- c("event_id", "fold_id", "block_id")
  if (!all(req %in% names(assignment))) {
    stop("fold assignment missing columns: ", paste(setdiff(req, names(assignment)), collapse = ", "), call. = FALSE)
  }
  tab <- assignment[, req, drop = FALSE]
  tab <- tab[order(tab$event_id), , drop = FALSE]
  utils::write.csv(tab, path, row.names = FALSE)
  invisible(path)
}

#' @export
file_sha256 <- function(path) {
  out <- suppressWarnings(
    system2("sha256sum", shQuote(path), stdout = TRUE, stderr = FALSE)
  )
  if (length(out) < 1L || !nzchar(out[[1L]])) {
    stop("could not compute sha256 for ", path, call. = FALSE)
  }
  sub("\\s+.*$", "", out[[1L]])
}

.read_fold_assignment_csv <- function(path) {
  if (!file.exists(path)) {
    stop("fold assignment file not found: ", path, call. = FALSE)
  }
  tab <- utils::read.csv(path, stringsAsFactors = FALSE)
  req <- c("event_id", "fold_id", "block_id")
  miss <- setdiff(req, names(tab))
  if (length(miss)) {
    stop("fold assignment CSV missing columns: ", paste(miss, collapse = ", "), call. = FALSE)
  }
  tab$event_id <- as.character(tab$event_id)
  tab$fold_id <- as.integer(tab$fold_id)
  tab$block_id <- as.character(tab$block_id)
  .assert_unique_keys(tab$event_id, "event_id in fold assignment")
  tab[order(tab$event_id), , drop = FALSE]
}

.attach_spatial_fold_ids <- function(events, cfg) {
  if ("fold_id" %in% names(events)) {
    events$fold_id <- as.integer(events$fold_id)
    .assert_unique_keys(events$event_id, "event_id in cufes_events")
    return(events)
  }
  path <- cfg$data$fold_assignment_path
  if (!is.null(path) && nzchar(path) && file.exists(path)) {
    fa <- .read_fold_assignment_csv(path)
  } else if (
    !is.null(cfg$data$spatial_block_cv$n_folds) &&
      !is.null(cfg$mesh$cutoff_km) &&
      !is.null(cfg$prediction$seed)
  ) {
    params <- spatial_block_cv_params(cfg)
    fa <- assign_cufes_spatial_block_folds(events, params)
  } else {
    return(events)
  }
  ev_ids <- as.character(events$event_id)
  fa_ids <- as.character(fa$event_id)
  if (!identical(sort(ev_ids), sort(fa_ids))) {
    stop("fold assignment event_id set must match cufes_events", call. = FALSE)
  }
  idx <- match(ev_ids, fa$event_id)
  events$fold_id <- fa$fold_id[idx]
  events$block_id <- fa$block_id[idx]
  events
}
