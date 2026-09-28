test_that("cufes_events field report documents no planned/adaptive flag", {
  rep <- cufes_events_sampling_mode_field_report()
  expect_false(rep$planned_transect_flag_on_processed_table)
  expect_false(rep$adaptive_infill_flag_on_processed_table)
  expect_true("cruise" %in% rep$erddap_erdCalCOFIcufes_fields_fetched)
  expect_false("line" %in% rep$erddap_erdCalCOFIcufes_fields_fetched)
})

test_that("planned_line_only test filter requires reference path", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  cfg$egg_split$test_event_filter <- list(mode = "planned_line_only")
  dat <- data.frame(event_id = "CUFES:TEST:AK:s001", stringsAsFactors = FALSE)
  expect_error(filter_test_events_by_sampling_mode(dat, cfg), "planned_line_reference_path")
})

test_that("planned_line_only filter keeps reference event_ids", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  ref <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id",
      "CUFES:TEST:AK:s001",
      sep = "\n"
    ),
    ref
  )
  cfg$egg_split$test_event_filter <- list(
    mode = "planned_line_only",
    planned_line_reference_path = ref
  )
  dat <- data.frame(
    event_id = c("CUFES:TEST:AK:s001", "CUFES:TEST:AK:s002"),
    stringsAsFactors = FALSE
  )
  out <- filter_test_events_by_sampling_mode(dat, cfg)
  expect_equal(nrow(out), 1L)
  expect_equal(out$event_id[[1]], "CUFES:TEST:AK:s001")
})
