test_that("load_model_data rejects missing effort", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  dat <- load_model_data(cfg = cfg)
  expect_true(all(dat$volume_m3 > 0))
  expect_equal(nrow(dat), 46)
  expect_true(all(is.finite(dat$X)))
})

test_that("missing effort rows are refused", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event,time_idx",
      "CUFES:T:AK:a,2020-01-01T00:00:00Z,33, -119,2020-01-01T00:05:00Z,33.01,-118.99,NA,1,FALSE",
      "CUFES:T:AK:b,2020-01-01T00:00:00Z,33, -119,2020-01-01T00:05:00Z,33.01,-118.99,10,1,FALSE",
      sep = "\n"
    ),
    ev
  )
  writeLines(
    "event_id,taxon,count\nCUFES:T:AK:a,sardine,1\nCUFES:T:AK:b,sardine,2",
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
  expect_error(load_model_data(cfg = cfg), "effort")
})

test_that("duplicate event_id is refused", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event",
      "CUFES:T:AK:1,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:05:00Z,33.01,-118.99,10,2,5,FALSE",
      "CUFES:T:AK:1,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:05:00Z,33.01,-118.99,10,2,5,FALSE",
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:1,sardine,1", ct)
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(events_path = ev, counts_path = ct, covariates_path = ct),
    response = list(column = "egg_count", effort_column = "volume_m3")
  )
  expect_error(load_model_data(cfg = cfg), "duplicate event_id")
})

test_that("sample_id is accepted as event_id alias in legacy table", {
  td <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "sample_id,egg_count,volume_m3,lat,lon,stop_lat,stop_lon,time_idx,temp_3m_z,sal_3m_z,mld_z,sst_grad_z,dist_front_z,upwelling_z,log_depth_z",
      "CUFES:T:AK:x,3,5,33,-119,33.01,-118.99,1,0,0,0,0,0,0,0",
      sep = "\n"
    ),
    td
  )
  cfg <- list(
    data = list(table_path = td),
    covariates = list(
      dynamic = c("temp_3m", "sal_3m", "mld", "sst_grad", "dist_front", "upwelling"),
      static = "log_depth"
    ),
    response = list(column = "egg_count", effort_column = "volume_m3")
  )
  dat <- load_model_data(cfg = cfg)
  expect_equal(dat$event_id, "CUFES:T:AK:x")
})

test_that("cufes_events counts and covariates join on event_id", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event,time_idx",
      "CUFES:2024:SH:1,2020-01-01T00:00:00Z,33.0,-120.0,2020-01-01T00:08:00Z,33.02,-119.98,100,1,FALSE",
      "CUFES:2024:SH:2,2020-01-01T00:00:00Z,33.1,-120.1,2020-01-01T00:08:00Z,33.12,-119.88,200,1,FALSE",
      sep = "\n"
    ),
    ev
  )
  writeLines(
    paste(
      "event_id,taxon,count",
      "CUFES:2024:SH:1,sardine,5",
      "CUFES:2024:SH:2,sardine,0",
      sep = "\n"
    ),
    ct
  )
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:2024:SH:1", values = c(0.1, 0.2, 10, 0, 0, 0)),
      cufes_covariate_row("CUFES:2024:SH:2", values = c(0.2, 0.3, 11, 0, 0, 0)),
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
  expect_equal(nrow(dat), 2L)
  expect_equal(dat$event_id, c("CUFES:2024:SH:1", "CUFES:2024:SH:2"))
  expect_equal(dat$egg_count, c(5, 0))
})

test_that("mesh X/Y are UTM 11N track midpoints", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  lat0 <- 33.5
  lon0 <- -119.25
  lat1 <- 33.52
  lon1 <- -119.23
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event,time_idx",
      sprintf(
        "CUFES:T:AK:mid,2020-01-01T00:00:00Z,%s,%s,2020-01-01T00:10:00Z,%s,%s,50,1,FALSE",
        lat0, lon0, lat1, lon1
      ),
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:mid,sardine,2", ct)
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:T:AK:mid", values = rep(1, 6)),
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
  mid <- .track_midpoint_km(lon0, lat0, lon1, lat1)
  expect_equal(dat$X[[1]], mid$X[[1]], tolerance = 1e-6)
  expect_equal(dat$Y[[1]], mid$Y[[1]], tolerance = 1e-6)
})

test_that("covariate event_id mismatch is refused when covariates omit an event", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event,time_idx",
      "CUFES:T:AK:ok,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:05:00Z,33.01,-118.99,10,1,FALSE",
      "CUFES:T:AK:bad,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:05:00Z,NA,-118.99,10,1,FALSE",
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:ok,sardine,1\nCUFES:T:AK:bad,sardine,1", ct)
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:T:AK:ok"),
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
  expect_error(load_model_data(cfg = cfg), "event_id set mismatch")
})

test_that("missing endpoint dropped with aligned covariate ids", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event,time_idx",
      "CUFES:T:AK:ok,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:05:00Z,33.01,-118.99,10,1,FALSE",
      "CUFES:T:AK:bad,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:05:00Z,NA,-118.99,10,1,FALSE",
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:ok,sardine,1\nCUFES:T:AK:bad,sardine,1", ct)
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:T:AK:ok"),
      cufes_covariate_row("CUFES:T:AK:bad"),
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
  expect_equal(qc$dropped_missing_endpoint, 1L)
})

test_that("covariate event_id mismatch is refused", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event,time_idx",
      "CUFES:T:AK:a,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:05:00Z,33.01,-118.99,10,1,FALSE",
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:a,sardine,1", ct)
  writeLines(
    paste(
      cufes_covariates_csv_header(),
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
  expect_error(load_model_data(cfg = cfg), "event_id set mismatch")
})

test_that("load_model_data rejects NA counts in cufes_counts", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header(),
      cufes_event_row("CUFES:T:AK:na", 10),
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:na,sardine,NA", ct)
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(events_path = ev, counts_path = ct, covariates_path = ct),
    response = list(column = "egg_count", effort_column = "volume_m3")
  )
  expect_error(load_model_data(cfg = cfg), "must not contain NA counts")
})

test_that("cufes_events schema requires pump_readings_used and short_event", {
  ev <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,duration_min",
      "CUFES:T:AK:x,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:05:00Z,33.01,-118.99,10,5,FALSE",
      sep = "\n"
    ),
    ev
  )
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(events_path = ev, counts_path = ev, covariates_path = ev),
    response = list(column = "egg_count", effort_column = "volume_m3")
  )
  expect_error(load_model_data(cfg = cfg), "missing required columns")
})

test_that("bot1 start_latitude columns are accepted on cufes_events", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,start_time,start_latitude,start_longitude,stop_time,stop_latitude,stop_longitude,volume_m3,pump_readings_used,duration_min,short_event",
      "CUFES:T:AK:bot,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:05:00Z,33.01,-118.99,10,2,5,FALSE",
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:bot,sardine,1", ct)
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:T:AK:bot"),
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
  expect_equal(dat$pump_readings_used, 2L)
})

test_that("empty covariate on non-excluded row stops with error", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event,time_idx",
      "CUFES:T:AK:ok,2020-01-01T00:00:00Z,33,-119,2020-01-01T00:05:00Z,33.01,-118.99,10,2,5,FALSE,1",
      "CUFES:T:AK:na,2020-01-01T00:00:00Z,33.1,-119.1,2020-01-01T00:05:00Z,33.11,-119.09,10,2,5,FALSE,1",
      sep = "\n"
    ),
    ev
  )
  writeLines(
    "event_id,taxon,count\nCUFES:T:AK:ok,sardine,1\nCUFES:T:AK:na,sardine,1",
    ct
  )
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:T:AK:ok", values = c(0.5, 0, 0, 0, 0, 0)),
      cufes_covariate_row("CUFES:T:AK:na", values = c(NA, 0, 0, 0, 0, 0)),
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
  expect_error(load_model_data(cfg = cfg), "never impute or silently drop")
})
