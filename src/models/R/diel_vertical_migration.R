#' Decimal hour-of-day in [0, 24) from POSIXct (UTC clock).
#' @param tt POSIXct vector (UTC).
#' @return numeric vector of fractional hours.
#' @keywords internal
.utc_decimal_hour <- function(tt) {
  tt <- as.POSIXct(tt, tz = "UTC")
  as.numeric(format(tt, "%H", tz = "UTC")) +
    as.numeric(format(tt, "%M", tz = "UTC")) / 60 +
    as.numeric(format(tt, "%S", tz = "UTC")) / 3600
}

#' Approximate local solar hour from UTC time and longitude (deg E; W negative).
#'
#' Ignores equation of time and DST; adequate for a smooth diel cycle on trawl times.
#' @keywords internal
.solar_local_decimal_hour <- function(time_utc, lon_deg) {
  utc_h <- .utc_decimal_hour(as.POSIXct(time_utc, tz = "UTC"))
  lon_deg <- as.numeric(lon_deg)
  if (length(lon_deg) != length(utc_h)) {
    if (length(lon_deg) == 1L) {
      lon_deg <- rep(lon_deg, length(utc_h))
    } else {
      stop("lon length must match time for solar_local hour", call. = FALSE)
    }
  }
  local <- utc_h + lon_deg / 15
  local <- local %% 24
  local
}

#' Sin/cos pair for a smooth 24 h cycle (peak alignment follows the hour input).
#' @keywords internal
.tod_harmonic_terms <- function(hour_decimal) {
  ang <- 2 * pi * as.numeric(hour_decimal) / 24
  list(sin = sin(ang), cos = cos(ang))
}

#' Attach diel vertical migration (DVM) cyclic time-of-day columns for formula terms.
#'
#' Config block ``model$diel_vertical_migration`` (or ``data$diel_vertical_migration``):
#' \describe{
#'   \item{enabled}{Must be true to attach columns (default false when absent).}
#'   \item{time_reference}{``solar_local`` (default) or ``utc`` for hour-of-day.}
#' }
#' Adds ``tod_sin`` and ``tod_cos`` to ``dat``; requires ``time`` and ``lon`` for solar_local.
#' @keywords internal
.attach_diel_vertical_migration_terms <- function(dat, cfg) {
  dvm <- cfg$model$diel_vertical_migration %||% cfg$data$diel_vertical_migration
  if (is.null(dvm) || identical(dvm, FALSE) || !isTRUE(dvm$enabled)) {
    return(dat)
  }
  if (!"time" %in% names(dat)) {
    stop("diel_vertical_migration requires event time column", call. = FALSE)
  }
  ref <- dvm$time_reference %||% "solar_local"
  if (identical(ref, "utc")) {
    hour <- .utc_decimal_hour(dat$time)
  } else if (identical(ref, "solar_local")) {
    if (!"lon" %in% names(dat)) {
      stop("diel_vertical_migration solar_local requires lon on the model frame", call. = FALSE)
    }
    hour <- .solar_local_decimal_hour(dat$time, dat$lon)
  } else {
    stop("unsupported diel_vertical_migration.time_reference: ", ref, call. = FALSE)
  }
  harm <- .tod_harmonic_terms(hour)
  dat$tod_sin <- harm$sin
  dat$tod_cos <- harm$cos
  dat
}
