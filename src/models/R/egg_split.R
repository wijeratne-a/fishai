#' Egg-model temporal split (fit vs test holdout window).
#'
#' Keys live under ``egg_split`` in model YAML; no hard-coded pilot dates in R.

#' @export
parse_egg_split <- function(cfg) {
  es <- cfg$egg_split
  if (is.null(es)) {
    stop("egg_split block is required in model config", call. = FALSE)
  }
  req <- c("fit_end", "test_start", "test_end")
  miss <- req[!req %in% names(es)]
  if (length(miss)) {
    stop("egg_split missing: ", paste(miss, collapse = ", "), call. = FALSE)
  }
  fit_end <- as.Date(es$fit_end)
  test_start <- as.Date(es$test_start)
  test_end <- as.Date(es$test_end)
  if (any(is.na(c(fit_end, test_start, test_end)))) {
    stop("egg_split dates must be valid ISO dates (YYYY-MM-DD)", call. = FALSE)
  }
  if (test_start <= fit_end) {
    stop("egg_split.test_start must be after egg_split.fit_end", call. = FALSE)
  }
  if (test_end < test_start) {
    stop("egg_split.test_end must be on or after egg_split.test_start", call. = FALSE)
  }
  boundary <- es$glorys_product_boundary
  if (is.null(boundary) || !nzchar(as.character(boundary))) {
    boundary <- "2021-06-30"
  }
  glorys_boundary <- as.Date(boundary)
  if (is.na(glorys_boundary)) {
    stop("egg_split.glorys_product_boundary must be a valid date", call. = FALSE)
  }
  include_post <- es$test_score_include_post_boundary
  if (is.null(include_post)) {
    include_post <- TRUE
  }
  list(
    fit_end = fit_end,
    test_start = test_start,
    test_end = test_end,
    glorys_product_boundary = glorys_boundary,
    test_score_include_post_boundary = isTRUE(include_post)
  )
}

#' @export
egg_split_fit_end <- function(cfg) {
  parse_egg_split(cfg)$fit_end
}

.event_date_utc <- function(dat) {
  if (!"time" %in% names(dat)) {
    stop("events need time column for egg_split filtering", call. = FALSE)
  }
  as.Date(as.POSIXct(dat$time, tz = "UTC"))
}

#' @export
tag_egg_split_period <- function(dat, cfg) {
  es <- parse_egg_split(cfg)
  d <- .event_date_utc(dat)
  period <- ifelse(
    d <= es$fit_end,
    "fit",
    ifelse(d >= es$test_start & d <= es$test_end, "test", "out_of_scope")
  )
  dat$egg_split_period <- period
  dat
}

#' @export
filter_egg_split_scope <- function(dat, cfg, scope = c("fit", "test", "all")) {
  scope <- match.arg(scope)
  es <- parse_egg_split(cfg)
  d <- .event_date_utc(dat)
  keep <- switch(
    scope,
    fit = d <= es$fit_end,
    test = d >= es$test_start & d <= es$test_end,
    all = (d <= es$fit_end) | (d >= es$test_start & d <= es$test_end)
  )
  if (!any(keep)) {
    stop("no events remain for egg_split scope=", scope, call. = FALSE)
  }
  out <- dat[keep, , drop = FALSE]
  if (scope == "test") {
    out <- filter_test_events_by_sampling_mode(out, cfg)
    if (nrow(out) == 0L) {
      stop("no test events remain after test_event_filter", call. = FALSE)
    }
  }
  if (!"egg_split_period" %in% names(out)) {
    out <- tag_egg_split_period(out, cfg)
  }
  out
}

#' Subset test-period rows for scoring; optional drop of post-GLORYS-my events.
#'
#' @param include_post_boundary If NULL, uses ``egg_split.test_score_include_post_boundary``.
#' @export
filter_egg_test_period_scores <- function(dat, cfg, include_post_boundary = NULL) {
  es <- parse_egg_split(cfg)
  d <- .event_date_utc(dat)
  keep <- d >= es$test_start & d <= es$test_end
  if (is.null(include_post_boundary)) {
    include_post_boundary <- es$test_score_include_post_boundary
  }
  if (!isTRUE(include_post_boundary)) {
    keep <- keep & (d <= es$glorys_product_boundary)
  }
  out <- dat[keep, , drop = FALSE]
  out <- filter_test_events_by_sampling_mode(out, cfg)
  out
}

.filter_events_table_to_fit_end <- function(events, cfg) {
  es <- parse_egg_split(cfg)
  d <- .event_date_utc(events)
  events[d <= es$fit_end, , drop = FALSE]
}
