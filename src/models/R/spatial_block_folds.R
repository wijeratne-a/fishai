#' Spatial-block CV fold assignment for CUFES events (modeling-side).
#'
#' Block size and seed come from the species model config; fold count from
#' ``data.spatial_block_cv.n_folds``. See ``docs/CUFES_DELTA_MODEL_SPEC.md``.

#' Pre-registered spatial range (km) used to enforce minimum block size.
.spatial_range_km_from_cfg <- function(cfg) {
  rg <- cfg$mesh$range_guess_km
  if (is.null(rg) || length(rg) != 1L || !is.finite(as.numeric(rg))) {
    stop("mesh.range_guess_km is required for spatial-block fold assignment", call. = FALSE)
  }
  as.numeric(rg)
}

#' Read spatial-block CV parameters from a model config (no invented defaults).
#' @export
spatial_block_cv_params <- function(cfg) {
  cutoff <- cfg$mesh$cutoff_km
  range_km <- .spatial_range_km_from_cfg(cfg)
  seed <- cfg$prediction$seed
  n_folds <- cfg$data$spatial_block_cv$n_folds
  if (is.null(cutoff) || length(cutoff) != 1L || !is.finite(as.numeric(cutoff))) {
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
  cutoff <- as.numeric(cutoff)
  block_size_km <- max(cutoff, range_km)
  block_size_source <- if (block_size_km > cutoff) {
    "max(mesh.cutoff_km, mesh.range_guess_km)"
  } else {
    "mesh.cutoff_km"
  }
  list(
    block_size_km = block_size_km,
    mesh_cutoff_km = cutoff,
    spatial_range_km = range_km,
    seed = as.integer(seed),
    n_folds = n_folds,
    epsg = 32611L,
    block_size_source = block_size_source,
    spatial_range_source = "mesh.range_guess_km",
    seed_source = "prediction.seed",
    n_folds_source = "data.spatial_block_cv.n_folds"
  )
}

.block_table_from_events <- function(events, params) {
  cols <- .resolve_track_endpoint_columns(names(events))
  lat0 <- events[[cols$start_lat]]
  lon0 <- events[[cols$start_lon]]
  lat1 <- events[[cols$stop_lat]]
  lon1 <- events[[cols$stop_lon]]
  mid <- .track_midpoint_km(lon0, lat0, lon1, lat1, epsg = params$epsg %||% 32611L)
  bx <- floor(mid$X / params$block_size_km)
  by <- floor(mid$Y / params$block_size_km)
  block_id <- paste0("bx", bx, "_by", by)
  data.frame(
    event_id = as.character(events$event_id),
    block_id = block_id,
    bx = bx,
    by = by,
    X = mid$X,
    Y = mid$Y,
    stringsAsFactors = FALSE
  )
}

.md5_hex <- function(x) {
  f <- tempfile()
  on.exit(unlink(f), add = TRUE)
  writeLines(x, f, useBytes = TRUE)
  unname(tools::md5sum(f))
}

.block_sort_order <- function(uniq, seed) {
  tie <- vapply(
    uniq$block_id,
    function(b) {
      strtoi(substr(.md5_hex(paste0(seed, ":", b)), 1L, 8L), base = 16L)
    },
    integer(1L)
  )
  order(uniq$by, uniq$bx, uniq$Y, uniq$X, tie, uniq$block_id)
}

.assign_folds_to_blocks_contiguous <- function(block_df, n_folds, seed) {
  uniq <- unique(block_df[, c("block_id", "bx", "by"), drop = FALSE])
  cx <- stats::aggregate(
    cbind(X = block_df$X, Y = block_df$Y),
    by = list(block_id = block_df$block_id),
    FUN = mean
  )
  uniq <- merge(uniq, cx, by = "block_id", sort = FALSE)
  ord <- .block_sort_order(uniq, seed)
  uniq <- uniq[ord, , drop = FALSE]
  n_blk <- nrow(uniq)
  if (n_blk < n_folds) {
    stop(
      "fewer spatial blocks (",
      n_blk,
      ") than CV folds (",
      n_folds,
      "); widen domain or reduce n_folds",
      call. = FALSE
    )
  }
  edges <- floor(seq(0, n_blk, length.out = n_folds + 1L))
  fold_id <- integer(n_blk)
  for (k in seq_len(n_folds)) {
    i0 <- edges[[k]] + 1L
    i1 <- edges[[k + 1L]]
    if (i0 <= i1) {
      fold_id[i0:i1] <- k
    }
  }
  if (any(fold_id < 1L)) {
    stop("contiguous fold assignment left unassigned blocks", call. = FALSE)
  }
  stats::setNames(fold_id, uniq$block_id)
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
  block_df <- .block_table_from_events(events, params)
  block_fold <- .assign_folds_to_blocks_contiguous(
    block_df,
    params$n_folds,
    params$seed
  )
  fold_id <- as.integer(block_fold[block_df$block_id])
  out <- data.frame(
    event_id = block_df$event_id,
    fold_id = fold_id,
    block_id = block_df$block_id,
    stringsAsFactors = FALSE
  )
  out <- out[order(out$event_id), , drop = FALSE]
  rownames(out) <- NULL
  out
}

#' Verify contiguous block groups per fold (EPSG:32611 blocking geometry).
#' @export
verify_spatial_block_contiguity <- function(assignment, events, params) {
  req <- c("event_id", "fold_id", "block_id")
  if (!all(req %in% names(assignment))) {
    stop("assignment missing columns for contiguity check", call. = FALSE)
  }
  block_df <- .block_table_from_events(events, params)
  uniq <- unique(block_df[, c("block_id", "bx", "by"), drop = FALSE])
  cx <- stats::aggregate(
    cbind(X = block_df$X, Y = block_df$Y),
    by = list(block_id = block_df$block_id),
    FUN = mean
  )
  uniq <- merge(uniq, cx, by = "block_id", sort = FALSE)
  ord <- .block_sort_order(uniq, params$seed)
  uniq <- uniq[ord, , drop = FALSE]
  idx_by_block <- stats::setNames(seq_len(nrow(uniq)), uniq$block_id)
  block_fold <- assignment[
    match(uniq$block_id, assignment$block_id),
    c("block_id", "fold_id"),
    drop = FALSE
  ]
  block_fold <- block_fold[!is.na(block_fold$block_id), , drop = FALSE]
  block_fold <- block_fold[order(idx_by_block[block_fold$block_id]), , drop = FALSE]
  folds <- sort(unique(block_fold$fold_id))
  for (f in folds) {
    pos <- which(block_fold$fold_id == f)
    if (!length(pos)) {
      next
    }
    if (max(pos) - min(pos) + 1L != length(pos)) {
      return(FALSE)
    }
  }
  TRUE
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

.assert_cv_fold_assignment_contract <- function(dat, fold_ids, cfg) {
  if (length(fold_ids) != nrow(dat)) {
    stop("fold_id length must match modelling rows", call. = FALSE)
  }
  if (any(is.na(fold_ids))) {
    stop("fold_id contains NA", call. = FALSE)
  }
  if (anyDuplicated(dat$event_id)) {
    stop("duplicate event_id in CV frame", call. = FALSE)
  }
  folds <- sort(unique(as.character(fold_ids)))
  for (fold_id in folds) {
    train_ids <- dat$event_id[as.character(fold_ids) != fold_id]
    test_ids <- dat$event_id[as.character(fold_ids) == fold_id]
    if (length(intersect(train_ids, test_ids))) {
      stop("CV fold ", fold_id, ": event appears in both train and test", call. = FALSE)
    }
    if ("block_id" %in% names(dat)) {
      train_blocks <- unique(dat$block_id[as.character(fold_ids) != fold_id])
      test_blocks <- unique(dat$block_id[as.character(fold_ids) == fold_id])
      overlap <- intersect(train_blocks, test_blocks)
      if (length(overlap)) {
        stop(
          "CV fold ",
          fold_id,
          ": spatial block(s) appear in both train and test",
          call. = FALSE
        )
      }
    }
  }
  params <- spatial_block_cv_params(cfg)
  if (params$block_size_km < params$spatial_range_km) {
    stop("spatial block size is below pre-registered spatial range", call. = FALSE)
  }
  invisible(TRUE)
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
  missing <- setdiff(ev_ids, fa_ids)
  if (length(missing)) {
    stop(
      length(missing),
      " event_id(s) in cufes_events missing from fold assignment",
      call. = FALSE
    )
  }
  idx <- match(ev_ids, fa$event_id)
  events$fold_id <- fa$fold_id[idx]
  events$block_id <- fa$block_id[idx]
  events
}
