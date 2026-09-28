#' Load model-ready observation table.
#'
#' Accepts CSV or Parquet keyed by `sample_id`. Rows with missing or non-positive
#' effort are rejected (never imputed as zero catch).
#'
#' @param path File path (.csv or .parquet).
#' @param cfg Optional config list with `response` block.
#' @return Data frame with standardized columns including `y`, `log_effort`.
#' @export
load_model_data <- function(path, cfg = NULL) {
  ext <- tolower(tools::file_ext(path))
  if (ext == "csv") {
    dat <- utils::read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
  } else if (ext %in% c("parquet", "pq")) {
    if (!requireNamespace("arrow", quietly = TRUE)) {
      stop("Parquet requires arrow; use CSV in tests or add arrow to renv.", call. = FALSE)
    }
    dat <- as.data.frame(arrow::read_parquet(path))
  } else {
    stop("unsupported table format: ", ext, call. = FALSE)
  }

  id_col <- if ("sample_id" %in% names(dat)) {
    "sample_id"
  } else if ("obs_id" %in% names(dat)) {
    "obs_id"
  } else {
    stop("missing sample_id/obs_id column", call. = FALSE)
  }

  effort_col <- cfg$response$effort_column %||% "effort"
  resp_col <- cfg$response$column %||% "egg_count"

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
  dat$sample_id <- dat[[id_col]]
  dat
}

`%||%` <- function(x, y) if (is.null(x)) y else x
