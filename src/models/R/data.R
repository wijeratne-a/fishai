#' Load model-ready observation table.
#'
#' Production ingest writes ``cufes_events`` and ``cufes_counts`` Parquet tables
#' joined on ``event_id`` (``CUFES:{cruise}:{ship_code}:{sample_number}``).
#' Effort is ``volume_m3`` on events. Legacy single-table CSV fixtures may use
#' ``sample_id`` as an alias for ``event_id``.
#'
#' @param path Optional path override for a single merged table (tests).
#' @param cfg Config with `data` and `response` blocks.
#' @return Data frame with `event_id`, `y`, `log_effort`, and covariates.
#' @export
load_model_data <- function(path = NULL, cfg = NULL) {
  if (is.null(cfg)) {
    stop("cfg is required", call. = FALSE)
  }

  effort_col <- cfg$response$effort_column %||% "volume_m3"
  resp_col <- cfg$response$column %||% "egg_count"

  if (!is.null(cfg$data$events_path) && !is.null(cfg$data$counts_path)) {
    events <- .read_model_table(cfg$data$events_path)
    counts <- .read_model_table(cfg$data$counts_path)
    taxon <- cfg$species$taxon
    if (is.null(taxon) || !nzchar(taxon)) {
      stop("species.taxon is required to select rows from cufes_counts", call. = FALSE)
    }
    if (!"event_id" %in% names(events)) {
      stop("cufes_events missing event_id column", call. = FALSE)
    }
    if (!all(c("event_id", "taxon", "count") %in% names(counts))) {
      stop("cufes_counts must include event_id, taxon, count", call. = FALSE)
    }
    .assert_unique_keys(events$event_id, "event_id in cufes_events")
    counts <- counts[counts$taxon == taxon, , drop = FALSE]
    .assert_unique_keys(counts$event_id, paste0("event_id in cufes_counts (taxon=", taxon, ")"))
    dat <- merge(events, counts[, c("event_id", "count"), drop = FALSE], by = "event_id", all.x = TRUE)
    if (any(is.na(dat$count))) {
      stop("cufes_counts missing rows for some events after taxon filter", call. = FALSE)
    }
    dat[[resp_col]] <- dat$count
    dat$count <- NULL
  } else {
    table_path <- path %||% cfg$data$table_path
    if (is.null(table_path) || !nzchar(table_path)) {
      stop("set data.table_path or data.events_path + data.counts_path", call. = FALSE)
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

  dat$y <- dat[[resp_col]]
  dat$log_effort <- log(dat[[effort_col]])
  dat
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

`%||%` <- function(x, y) if (is.null(x)) y else x
