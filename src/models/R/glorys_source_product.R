#' Point the Python catalogue resolver at the committed pinned catalogue.
#'
#' Production CLIs do not call this. They leave
#' ``FISHAI_GLORYS_PINNED_CATALOG_JSON`` unset and resolve against the live
#' Copernicus catalogue, fail-closed. Test and dry-run entry points call
#' this so R ``system2(python3)`` lookups do not depend on catalogue availability.
.use_glorys_catalog_fixture <- function(root = Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))) {
  fixture <- file.path(
    root,
    "src",
    "models",
    "tests",
    "fixtures",
    "glorys_pinned_catalog.json"
  )
  if (!file.exists(fixture)) {
    stop("missing GLORYS catalogue fixture at ", fixture, call. = FALSE)
  }
  Sys.setenv(FISHAI_GLORYS_PINNED_CATALOG_JSON = normalizePath(fixture, mustWork = TRUE))
  invisible(Sys.getenv("FISHAI_GLORYS_PINNED_CATALOG_JSON"))
}

#' Expected GLORYS Copernicus product ids for calendar days.
#'
#' One Python process resolves every date so the catalogue is fetched once.
#' Returns a named character vector (ISO date -> product id).
.expected_glorys_products_for_iso_dates <- function(iso_dates) {
  iso_dates <- as.character(iso_dates)
  if (!length(iso_dates)) {
    return(stats::setNames(character(), character()))
  }
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  script <- file.path(root, "scripts", "ci", "glorys_product_for_date_cli.py")
  if (!file.exists(script)) {
    stop("missing glorys_product_for_date_cli.py at ", script, call. = FALSE)
  }
  out <- suppressWarnings(
    system2(
      "python3",
      c(script, iso_dates),
      stdout = TRUE,
      stderr = TRUE
    )
  )
  status <- attr(out, "status")
  if (!is.null(status) && status != 0L) {
    stop(
      "glorys_product_for_date lookup failed: ",
      paste(out, collapse = "\n"),
      call. = FALSE
    )
  }
  prods <- trimws(out)
  prods <- prods[nzchar(prods)]
  if (length(prods) != length(iso_dates)) {
    stop(
      "glorys_product_for_date returned ",
      length(prods),
      " ids for ",
      length(iso_dates),
      " dates",
      call. = FALSE
    )
  }
  stats::setNames(prods, iso_dates)
}

#' Expected GLORYS Copernicus product id for a calendar day (via Python ``glorys_product_for_date``).
.expected_glorys_product_for_iso_date <- function(iso_date) {
  unname(.expected_glorys_products_for_iso_dates(iso_date))
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
  uniq_days <- unique(days)
  expected_by_day <- .expected_glorys_products_for_iso_dates(uniq_days)
  for (i in seq_len(nrow(events))) {
    expected <- expected_by_day[[days[[i]]]]
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
