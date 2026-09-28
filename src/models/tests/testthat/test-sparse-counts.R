test_that("missing cufes_counts row is not a zero for another taxon", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  eid <- "CUFES:T:AK:only-sardine"
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event,time_idx",
      paste0(
        eid,
        ",2020-01-01T00:00:00Z,33,-119,2020-01-01T00:10:00Z,33.01,-118.99,100,1,10"
      ),
      sep = "\n"
    ),
    ev
  )
  writeLines(
    paste0("event_id,taxon,count\n", eid, ",sardine,3"),
    ct
  )
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row(eid, values = c(0.1, 0.2, 10, 0, 0, 0)),
      sep = "\n"
    ),
    cov
  )
  base_cfg <- function(taxon) {
    list(
      species = list(taxon = taxon),
      data = list(events_path = ev, counts_path = ct, covariates_path = cov),
      covariates = list(
        dynamic = c("temp_3m", "sal_3m", "mld", "sst_grad", "dist_front", "upwelling"),
        static = "log_depth"
      ),
      response = list(column = "egg_count", effort_column = "volume_m3")
    )
  }

  sard <- load_model_data(cfg = base_cfg("sardine"))
  expect_equal(nrow(sard), 1L)
  expect_equal(sard$event_id[[1]], eid)
  expect_equal(sard$egg_count[[1]], 3)
  qc_s <- fishai_data_prep_qc(sard)
  expect_equal(qc_s$excluded_no_count_row, 0L)

  expect_error(load_model_data(cfg = base_cfg("hake")), "no events with a cufes_counts row")
})

test_that("excluded_no_count_row counts events without taxon row", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event,time_idx",
      "CUFES:T:AK:a,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:10:00Z,33.01,-118.99,10,1,10,FALSE",
      "CUFES:T:AK:b,2020-01-01T00:00:00Z,33.1,-119.1,2020-01-01T00:10:00Z,33.11,-119.09,10,1,10,FALSE",
      sep = "\n"
    ),
    ev
  )
  writeLines(
    "event_id,taxon,count\nCUFES:T:AK:a,sardine,1",
    ct
  )
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:T:AK:a"),
      cufes_covariate_row("CUFES:T:AK:b"),
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
    response = list(column = "egg_count", effort_column = "volume_m3")
  )
  dat <- load_model_data(cfg = cfg)
  expect_equal(nrow(dat), 1L)
  qc <- fishai_data_prep_qc(dat)
  expect_equal(qc$excluded_no_count_row, 1L)
})
