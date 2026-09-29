#' Expected GLORYS Copernicus product id for a calendar day (via Python ``glorys_product_for_date``).
.expected_glorys_product_for_iso_date <- function(iso_date) {
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  script <- file.path(root, "scripts", "ci", "glorys_product_for_date_cli.py")
  if (!file.exists(script)) {
    stop("missing glorys_product_for_date_cli.py at ", script, call. = FALSE)
  }
  out <- suppressWarnings(
    system2(
      "python3",
      c(script, iso_date),
      stdout = TRUE,
      stderr = TRUE
    )
  )
  status <- attr(out, "status")
  if (!is.null(status) && status != 0L) {
    stop(
      "glorys_product_for_date lookup failed for ",
      iso_date,
      ": ",
      paste(out, collapse = "\n"),
      call. = FALSE
    )
  }
  prod <- trimws(out[[length(out)]])
  if (!nzchar(prod)) {
    stop("empty glorys_product_for_date result for ", iso_date, call. = FALSE)
  }
  prod
}

.assert_glorys_covariate_source_product <- function(events, cfg) {
  forcing <- cfg$training$covariate_forcing_source_id %||% cfg$covariates$forcing_source_id
  if (!identical(forcing, "glorys")) {
    return(invisible(TRUE))
  }
  if (!"source_product" %in% names(events)) {
    stop(
      "GLORYS covariate forcing requires source_product on covariate rows",
      call. = FALSE
    )
  }
  if (!"time" %in% names(events)) {
    stop("events missing time column for source_product validation", call. = FALSE)
  }
  tt <- as.POSIXct(events$time, tz = "UTC")
  if (any(is.na(tt))) {
    stop("could not parse event time for source_product validation", call. = FALSE)
  }
  days <- format(tt, "%Y-%m-%d")
  got <- trimws(as.character(events$source_product))
  for (i in seq_len(nrow(events))) {
    expected <- .expected_glorys_product_for_iso_date(days[[i]])
    if (!identical(got[[i]], expected)) {
      stop(
        "source_product mismatch for event_id=",
        events$event_id[[i]],
        " date=",
        days[[i]],
        ": got ",
        got[[i]],
        ", expected ",
        expected,
        " (glorys_product_for_date)",
        call. = FALSE
      )
    }
  }
  invisible(TRUE)
}
