#' Audit bot1 ``cufes_events`` for planned-transect vs adaptive-infill discrimination.

#' @export
cufes_events_sampling_mode_field_report <- function() {
  list(
    processed_cufes_events_columns_from_pr4 = c(
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
      "short_event",
      "implied_speed_kn",
      "speed_review_flag",
      "qc_flags",
      "track_wkt"
    ),
    erddap_erdCalCOFIcufes_fields_fetched = c(
      "cruise",
      "ship_code",
      "sample_number",
      "time",
      "latitude",
      "longitude",
      "start_pump_speed",
      "stop_time",
      "stop_latitude",
      "stop_longitude",
      "stop_pump_speed",
      "sardine_eggs",
      "anchovy_eggs",
      "jack_mackerel_eggs",
      "hake_eggs",
      "squid_eggs",
      "other_fish_eggs"
    ),
    planned_transect_flag_on_processed_table = FALSE,
    adaptive_infill_flag_on_processed_table = FALSE,
    calcofi_line_station_on_processed_table = FALSE,
    discrimination_note = paste(
      "Processed cufes_events retains cruise/ship/sample only inside event_id",
      "(CUFES:cruise:ship_code:sample_number). No CalCOFI line/station column is",
      "written to the parquet. Matching standard CalCOFI positions requires an",
      "external reference table; FishAI does not invent a planned/adaptive flag."
    ),
    optional_test_filter = list(
      config_path = "egg_split.test_event_filter.mode",
      modes = c("all", "planned_line_only"),
      planned_line_reference_path = "egg_split.test_event_filter.planned_line_reference_path"
    )
  )
}

.planned_line_event_ids <- function(reference_path, root = Sys.getenv("FISHAI_ROOT", getwd())) {
  path <- reference_path
  if (!grepl("^/", path)) {
    path <- file.path(root, path)
  }
  if (!file.exists(path)) {
    stop("planned_line_reference_path not found: ", path, call. = FALSE)
  }
  ref <- utils::read.csv(path, stringsAsFactors = FALSE)
  if ("event_id" %in% names(ref)) {
    return(unique(as.character(ref$event_id)))
  }
  req <- c("cruise", "ship_code", "sample_number")
  if (!all(req %in% names(ref))) {
    stop(
      "planned line reference needs event_id or columns: ",
      paste(req, collapse = ", "),
      call. = FALSE
    )
  }
  paste(
    "CUFES",
    ref$cruise,
    ref$ship_code,
    ref$sample_number,
    sep = ":"
  )
}

#' @export
filter_test_events_by_sampling_mode <- function(dat, cfg) {
  filt <- cfg$egg_split$test_event_filter
  if (is.null(filt)) {
    return(dat)
  }
  mode <- filt$mode %||% "all"
  if (identical(mode, "all")) {
    return(dat)
  }
  if (!identical(mode, "planned_line_only")) {
    stop("egg_split.test_event_filter.mode must be 'all' or 'planned_line_only'", call. = FALSE)
  }
  ref_path <- filt$planned_line_reference_path
  if (is.null(ref_path) || !nzchar(as.character(ref_path))) {
    stop(
      "egg_split.test_event_filter.planned_line_reference_path is required when mode is planned_line_only",
      call. = FALSE
    )
  }
  keep_ids <- .planned_line_event_ids(ref_path)
  dat[dat$event_id %in% keep_ids, , drop = FALSE]
}
