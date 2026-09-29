test_that("event_count_guard reads from config and stops on mismatch", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header(),
      "CUFES:T:AK:a,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:05:00Z,33.01,-118.99,10,2,5,FALSE",
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:a,sardine,1", ct)
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      "CUFES:T:AK:a,0,0,0,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE",
      sep = "\n"
    ),
    cov
  )
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(
      events_path = ev,
      counts_path = ct,
      covariates_path = cov,
      time_idx_origin = "2020-01-01",
      event_count_guard = list(n_events = 2L, n_short_event = 0L, n_long_event = 2L)
    ),
    covariates = list(
      dynamic = c("temp_3m", "sal_3m", "mld", "sst_grad", "dist_front", "upwelling"),
      static = "log_depth"
    ),
    response = list(column = "egg_count", effort_column = "volume_m3")
  )
  expect_error(load_model_data(cfg = cfg), "event_count_guard mismatch for taxon=sardine")
})

test_that("exclude_short_events filters on short_event column", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  all <- load_model_data(cfg = cfg)
  red <- load_model_data(cfg = cfg, exclude_short_events = TRUE)
  expect_equal(nrow(all), 46L)
  expect_equal(nrow(red), 24L)
  expect_false(any(isTRUE(.parse_short_event_logical(red$short_event))))
})

test_that("synthetic pilot guard counts match fixture events table", {
  proto <- load_short_sample_protocol(
    file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "sensitivity_protocol_test.yaml")
  )
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  cfg$data$event_count_guard <- proto$event_count_guard
  expect_no_error(load_model_data(cfg = cfg))
})
