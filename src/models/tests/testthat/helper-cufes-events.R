cufes_covariates_csv_header <- function() {
  paste(
    c(
      "event_id",
      "T3m",
      "S3m",
      "MLD_m",
      "sst_grad",
      "front_distance_km",
      "upwelling",
      "log_depth_z",
      "excluded"
    ),
    collapse = ","
  )
}

cufes_covariate_row <- function(event_id, values = rep(0, 7), excluded = FALSE) {
  vals <- paste(c(as.character(values), if (isTRUE(excluded)) "TRUE" else "FALSE"), collapse = ",")
  paste(event_id, vals, sep = ",")
}

cufes_events_csv_header <- function(extra_cols = character()) {
  base <- paste(
    c(
      "event_id",
      "time",
      "lat",
      "lon",
      "stop_time",
      "stop_lat",
      "stop_lon",
      "volume_m3",
      "pump_readings_used",
      "duration_min",
      "short_event"
    ),
    collapse = ","
  )
  if (length(extra_cols)) {
    base <- paste(base, paste(extra_cols, collapse = ","), sep = ",")
  }
  base
}

cufes_event_row <- function(
  event_id,
  volume_m3,
  time_idx = NULL,
  duration_min = 5,
  pump_readings_used = 2,
  short_event = duration_min < 10,
  lat = 33,
  lon = -119,
  extra_after_short = character()
) {
  core <- paste(
    event_id,
    "2020-01-01T00:00:00Z",
    lat,
    lon,
    "2020-01-01T00:05:00Z",
    lat + 0.01,
    lon + 0.01,
    volume_m3,
    pump_readings_used,
    duration_min,
    if (isTRUE(short_event)) "TRUE" else "FALSE",
    sep = ","
  )
  if (!is.null(time_idx)) {
    core <- paste(core, time_idx, sep = ",")
  }
  if (length(extra_after_short)) {
    core <- paste(core, paste(extra_after_short, collapse = ","), sep = ",")
  }
  core
}
