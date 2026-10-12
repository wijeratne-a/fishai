#' Attach behavioral-regime factors (season, optional day/night) for formula interactions.
#'
#' Season uses the same meteorological buckets as [forecast_season()] (DJF, MAM, JJA, SON).
#' Day/night uses UTC civil twilight proxy: day = hour in [6, 18), else night.
#' @keywords internal
.attach_behavioral_regime_factors <- function(dat, cfg) {
  br <- cfg$model$behavioral_regime %||% cfg$data$behavioral_regime
  if (is.null(br) || identical(br, FALSE)) {
    return(dat)
  }
  if (!"time" %in% names(dat)) {
    stop("behavioral_regime requires event time column", call. = FALSE)
  }
  tt <- as.POSIXct(dat$time, tz = "UTC")
  if (any(is.na(tt))) {
    stop("could not parse event time for behavioral_regime factors", call. = FALSE)
  }
  season_mode <- br$season %||% "meteorological"
  if (!identical(season_mode, "off") && !isFALSE(season_mode)) {
    if (!identical(season_mode, "meteorological")) {
      stop("unsupported behavioral_regime.season: ", season_mode, call. = FALSE)
    }
    dat$season_met <- factor(forecast_season(as.Date(tt)), levels = c("DJF", "MAM", "JJA", "SON"))
  }
  dn_mode <- br$day_night %||% "off"
  if (!identical(dn_mode, "off") && !isFALSE(dn_mode)) {
    if (!identical(dn_mode, "civil_utc")) {
      stop("unsupported behavioral_regime.day_night: ", dn_mode, call. = FALSE)
    }
    hrs <- as.integer(format(tt, "%H", tz = "UTC"))
    dat$day_night <- factor(ifelse(hrs >= 6L & hrs < 18L, "day", "night"), levels = c("day", "night"))
  }
  dat
}
