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
      "CUFES:T:AK:a,0,0,0,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE",
      "CUFES:T:AK:b,0,0,0,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE",
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
      "CUFES:2024:SH:1,0.1,0.2,10,0,0,0,0,cmems_mod_glo_phy_myint_0.083deg_P1D-m,FALSE",
      "CUFES:2024:SH:2,0.2,0.3,11,0,0,0,0,cmems_mod_glo_phy_myint_0.083deg_P1D-m,FALSE",
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
      "CUFES:T:AK:mid,1,1,1,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE",
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
      "CUFES:T:AK:ok,0,0,0,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE",
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
      "CUFES:T:AK:ok,0,0,0,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE",
      "CUFES:T:AK:bad,0,0,0,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE",
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
      "CUFES:T:AK:b,0,0,0,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE",
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
      "CUFES:T:AK:bot,0,0,0,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE",
      sep = "\n"
    ),
    cov
  )
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(events_path = ev, counts_path = ct, covariates_path = cov, time_idx_origin = "2019-01-01"),
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
      "CUFES:T:AK:ok,0.5,0,0,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE",
      "CUFES:T:AK:na,,0,0,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE",
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

.time_idx_scope_cfg <- function(origin = "2019-01-01") {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  times <- c(
    "2019-03-01T00:00:00Z",
    "2020-06-15T12:00:00Z",
    "2021-03-01T00:00:00Z",
    "2022-01-10T23:59:00Z"
  )
  ids <- paste0("CUFES:T:AK:t", seq_along(times))
  rows <- vapply(
    seq_along(times),
    function(i) {
      paste(
        ids[[i]], times[[i]], 33, -119, times[[i]], 33.01, -118.99, 10, 2, 5, "TRUE",
        sep = ","
      )
    },
    character(1)
  )
  writeLines(paste(c(cufes_events_csv_header(), rows), collapse = "\n"), ev)
  writeLines(
    paste(c("event_id,taxon,count", paste0(ids, ",sardine,", c(1, 0, 2, 0))), collapse = "\n"),
    ct
  )
  writeLines(
    paste(c(cufes_covariates_csv_header(), vapply(ids, cufes_covariate_row, character(1))), collapse = "\n"),
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
    egg_split = list(
      fit_end = "2020-12-31",
      test_start = "2021-01-01",
      test_end = "2022-04-27"
    )
  )
  if (!is.null(origin)) {
    cfg$data$time_idx_origin <- origin
  }
  cfg
}

test_that("time_idx uses one fixed origin identically across fit, test, and all scopes", {
  cfg <- .time_idx_scope_cfg()
  fit <- load_model_data(cfg = cfg, egg_split_scope = "fit")
  test <- load_model_data(cfg = cfg, egg_split_scope = "test")
  all <- load_model_data(cfg = cfg, egg_split_scope = "all")
  expect_equal(nrow(fit), 2L)
  expect_equal(nrow(test), 2L)
  expect_equal(nrow(all), 4L)
  idx_all <- stats::setNames(all$time_idx, all$event_id)
  expect_equal(stats::setNames(fit$time_idx, fit$event_id), idx_all[fit$event_id])
  expect_equal(stats::setNames(test$time_idx, test$event_id), idx_all[test$event_id])
  expect_equal(unname(idx_all[["CUFES:T:AK:t1"]]), 60L)
  expect_gt(min(test$time_idx), max(fit$time_idx))
  expect_false(min(test$time_idx) == 1L)
})

test_that("time_idx does not move when a different origin-free subset is loaded", {
  cfg <- .time_idx_scope_cfg()
  a <- load_model_data(cfg = cfg, egg_split_scope = "all")
  cfg_b <- cfg
  ev <- read.csv(cfg$data$events_path, stringsAsFactors = FALSE)
  ev <- ev[ev$event_id != "CUFES:T:AK:t1", , drop = FALSE]
  cov <- read.csv(cfg$data$covariates_path, stringsAsFactors = FALSE)
  cov <- cov[cov$event_id != "CUFES:T:AK:t1", , drop = FALSE]
  ev_path <- tempfile(fileext = ".csv")
  cov_path <- tempfile(fileext = ".csv")
  utils::write.csv(ev, ev_path, row.names = FALSE)
  utils::write.csv(cov, cov_path, row.names = FALSE)
  cfg_b$data$events_path <- ev_path
  cfg_b$data$covariates_path <- cov_path
  b <- load_model_data(cfg = cfg_b, egg_split_scope = "all")
  idx_a <- stats::setNames(a$time_idx, a$event_id)
  expect_equal(stats::setNames(b$time_idx, b$event_id), idx_a[b$event_id])
})

test_that("missing or invalid time_idx origin fails closed", {
  expect_error(load_model_data(cfg = .time_idx_scope_cfg(origin = NULL)), "time_idx_origin")
  expect_error(load_model_data(cfg = .time_idx_scope_cfg(origin = "")), "time_idx_origin")
  expect_error(load_model_data(cfg = .time_idx_scope_cfg(origin = "not-a-date")), "time_idx_origin")
  expect_error(load_model_data(cfg = .time_idx_scope_cfg(origin = "2019-13-40")), "time_idx_origin")
  expect_error(
    load_model_data(cfg = .time_idx_scope_cfg(origin = "2020-01-01")),
    "precedes data.time_idx_origin"
  )
})

test_that("pilot production configs fix a time_idx origin", {
  for (sp in c("sardine", "anchovy")) {
    raw <- yaml::read_yaml(file.path(FISHAI_ROOT, "configs", "models", paste0("cufes_", sp, ".yaml")))
    cfg <- raw$fishai_engine_config
    expect_false(is.na(.time_idx_origin_date(cfg)))
  }
})
