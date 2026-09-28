test_that("min_duration_min drops short events and logs QC", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event,time_idx",
      "CUFES:T:AK:long,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:10:00Z,33.01,-118.99,10,1,10,FALSE",
      "CUFES:T:AK:short,2020-01-01T00:00:00Z,33.1,-119.1,2020-01-01T00:10:00Z,33.11,-119.09,10,1,3,FALSE",
      sep = "\n"
    ),
    ev
  )
  writeLines(
    "event_id,taxon,count\nCUFES:T:AK:long,sardine,1\nCUFES:T:AK:short,sardine,0",
    ct
  )
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      "CUFES:T:AK:long,0,0,0,0,0,0,0,FALSE",
      "CUFES:T:AK:short,0,0,0,0,0,0,0,FALSE",
      sep = "\n"
    ),
    cov
  )
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(events_path = ev, counts_path = ct, covariates_path = cov),
    covariates = list(
      dynamic = c("temp_3m", "sal_3m", "mld", "sst_grad", "dist_front", "upwelling"),
      static = "log_depth"
    ),
    response = list(column = "egg_count", effort_column = "volume_m3"),
    mesh = list(cutoff_km = 9),
    model = list(
      family = "delta_gamma",
      delta_type = "poisson-link",
      formula_shared = "~ 1",
      spatial = list("off", "off"),
      spatiotemporal = list("off", "off")
    )
  )
  dat <- load_model_data(cfg = cfg, min_duration_min = 5)
  expect_equal(nrow(dat), 1L)
  expect_equal(dat$event_id[[1]], "CUFES:T:AK:long")
  qc <- fishai_data_prep_qc(dat)
  expect_equal(qc$dropped_short_duration, 1L)
})

test_that("compare_duration_sensitivity returns full and filtered blocks", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  cfg$model$formula_shared <- "~ 1"
  cfg$model$spatial <- list("off", "off")
  cfg$model$spatiotemporal <- list("off", "off")
  cmp <- compare_duration_sensitivity(cfg, min_duration_min = 5)
  expect_true(cmp$full$n_events >= cmp$duration_filtered$n_events)
  expect_true(is.finite(cmp$full$reference_volume_m3))
  expect_equal(
    cmp$full$reference_volume_n_events,
    cmp$full$n_events
  )
  expect_type(cmp$full$coefficients, "double")
  expect_true(length(cmp$full$coefficients) >= 1L)
})
