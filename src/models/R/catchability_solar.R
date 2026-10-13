#' Solar position and catchability (detection) covariates for trawl encounter models.
#'
#' Uses a standard apparent-solar-position approximation (NOAA-style, ~0.5 deg)
#' from UTC timestamp and WGS84 lat/lon. Not for sub-minute ephemeris work.

#' Julian day (UTC) from POSIXct.
#' @param tt POSIXct vector (UTC).
#' @keywords internal
.solar_julian_day_utc <- function(tt) {
  tt <- as.POSIXct(tt, tz = "UTC")
  as.numeric(
    difftime(
      as.Date(tt, tz = "UTC"),
      as.Date("2000-01-01", tz = "UTC"),
      units = "days"
    )
  ) + 2451545
}

#' Solar elevation (degrees) and related diel indicators.
#'
#' @param time_utc Event time (POSIXct, UTC).
#' @param lat_deg Latitude (degrees N).
#' @param lon_deg Longitude (degrees E; W negative).
#' @return list with solar_elevation_deg, is_day, is_night, is_dawn_dusk (civil twilight band).
#' @export
compute_solar_elevation <- function(time_utc, lat_deg, lon_deg) {
  time_utc <- as.POSIXct(time_utc, tz = "UTC")
  lat_deg <- as.numeric(lat_deg)
  lon_deg <- as.numeric(lon_deg)
  if (length(lat_deg) == 1L && length(lon_deg) == 1L) {
    lat_deg <- rep(lat_deg, length(time_utc))
    lon_deg <- rep(lon_deg, length(time_utc))
  }
  if (length(lat_deg) != length(time_utc) || length(lon_deg) != length(time_utc)) {
    stop("lat/lon must match time length for solar elevation", call. = FALSE)
  }

  jd <- .solar_julian_day_utc(time_utc)
  jc <- jd - 2451545
  g <- 357.529 + 0.98560028 * jc
  g_rad <- g * pi / 180
  q <- 280.459 + 0.98564736 * jc
  l <- q + 1.915 * sin(g_rad) + 0.02 * sin(2 * g_rad)
  l_rad <- l * pi / 180
  e <- 23.439 - 0.00000036 * jc
  e_rad <- e * pi / 180
  ra <- atan2(cos(e_rad) * sin(l_rad), cos(l_rad)) * 180 / pi
  ra <- (ra + 360) %% 360
  dec <- asin(sin(e_rad) * sin(l_rad)) * 180 / pi

  utc_h <- as.numeric(format(time_utc, "%H", tz = "UTC")) +
    as.numeric(format(time_utc, "%M", tz = "UTC")) / 60 +
    as.numeric(format(time_utc, "%S", tz = "UTC")) / 3600
  lst <- utc_h + lon_deg / 15
  ha <- (lst * 15 - ra) * pi / 180

  lat_rad <- lat_deg * pi / 180
  dec_rad <- dec * pi / 180
  sin_elev <- sin(lat_rad) * sin(dec_rad) + cos(lat_rad) * cos(dec_rad) * cos(ha)
  sin_elev <- pmax(pmin(sin_elev, 1), -1)
  elev <- asin(sin_elev) * 180 / pi

  twilight <- 6
  list(
    solar_elevation_deg = elev,
    is_day = elev > 0,
    is_night = elev <= 0,
    is_dawn_dusk = elev > -twilight & elev <= twilight
  )
}

.zscore_column <- function(x, name_z) {
  mu <- mean(x, na.rm = TRUE)
  sdv <- stats::sd(x, na.rm = TRUE)
  if (!is.finite(sdv) || sdv <= 0) {
    stop("cannot z-score ", name_z, ": zero or missing variance", call. = FALSE)
  }
  stats::setNames((x - mu) / sdv, name_z)
}

#' Attach catchability / solar detection columns when enabled in config.
#'
#' Config block ``model$catchability_detection`` or ``data$catchability_detection``:
#' \describe{
#'   \item{enabled}{Must be true to attach columns.}
#' }
#' Adds ``solar_elevation_deg``, ``is_day``, ``is_night``, ``is_dawn_dusk``,
#' ``solar_elev_z``, ``solar_elev_sin_z``, ``solar_elev_cos_z`` (detection helpers).
#' @keywords internal
.attach_catchability_detection_terms <- function(dat, cfg) {
  block <- cfg$model$catchability_detection %||% cfg$data$catchability_detection
  if (is.null(block) || identical(block, FALSE) || !isTRUE(block$enabled)) {
    return(dat)
  }
  if (!"time" %in% names(dat) || !"lat" %in% names(dat) || !"lon" %in% names(dat)) {
    stop("catchability_detection requires time, lat, lon on the model frame", call. = FALSE)
  }
  sol <- compute_solar_elevation(dat$time, dat$lat, dat$lon)
  dat$solar_elevation_deg <- sol$solar_elevation_deg
  dat$is_day <- as.integer(sol$is_day)
  dat$is_night <- as.integer(sol$is_night)
  dat$is_dawn_dusk <- as.integer(sol$is_dawn_dusk)
  dat$solar_elev_z <- .zscore_column(dat$solar_elevation_deg, "solar_elev_z")
  ang <- 2 * pi * dat$solar_elevation_deg / 90
  dat$solar_elev_sin_z <- .zscore_column(sin(ang), "solar_elev_sin_z")
  dat$solar_elev_cos_z <- .zscore_column(cos(ang), "solar_elev_cos_z")
  dat
}
