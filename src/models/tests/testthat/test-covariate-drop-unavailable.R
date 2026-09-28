test_that("drop upwelling when all blank with no_consistent_wind_product", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  drops <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header("time_idx"),
      cufes_event_row("CUFES:T:AK:a", 10, time_idx = 1),
      cufes_event_row("CUFES:T:AK:b", 10, time_idx = 2),
      sep = "\n"
    ),
    ev
  )
  writeLines(
    "event_id,taxon,count\nCUFES:T:AK:a,sardine,1\nCUFES:T:AK:b,sardine,2",
    ct
  )
  blank_row <- function(event_id) {
    paste(
      event_id,
      "0,0,0,0,0,,20,cmems_mod_glo_phy_my_0.083deg_P1D-m,no_consistent_wind_product,FALSE",
      sep = ","
    )
  }
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      blank_row("CUFES:T:AK:a"),
      blank_row("CUFES:T:AK:b"),
      sep = "\n"
    ),
    cov
  )
  writeLines("event_id,reason,covariate,latitude,longitude", drops)
  cfg <- list(
    species = list(taxon = "sardine"),
    drop_covariates_if_unavailable = "upwelling",
    data = list(
      events_path = ev,
      counts_path = ct,
      covariates_path = cov,
      covariate_drops_path = drops
    ),
    covariates = list(
      dynamic = c("temp_3m", "sal_3m", "mld", "sst_grad", "dist_front", "upwelling"),
      static = "log_depth",
      upstream_fields = list(
        temp_3m = "T3m",
        sal_3m = "S3m",
        mld = "MLD_m",
        sst_grad = "sst_grad",
        dist_front = "front_distance_km",
        upwelling = "upwelling",
        log_depth = "bottom_depth_m"
      )
    ),
    model = list(
      formula_shared = "~ s(temp_3m_z, k = 3) + s(upwelling_z, k = 3)"
    )
  )
  dat <- load_model_data(cfg = cfg)
  cfg_fit <- apply_model_cfg_patches(cfg, dat)
  expect_equal(nrow(dat), 2L)
  expect_false("upwelling" %in% cfg_fit$covariates$dynamic)
  expect_false(grepl("upwelling_z", cfg_fit$model$formula_shared, fixed = TRUE))
  prep <- .prepare_dat_for_fit_delta(dat, cfg_fit)
  expect_length(prep$covariate_dropped, 0L)
})

test_that("partial blank upwelling fails loudly", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  drops <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header("time_idx"),
      cufes_event_row("CUFES:T:AK:a", 10, time_idx = 1),
      cufes_event_row("CUFES:T:AK:b", 10, time_idx = 2),
      sep = "\n"
    ),
    ev
  )
  writeLines(
    "event_id,taxon,count\nCUFES:T:AK:a,sardine,1\nCUFES:T:AK:b,sardine,2",
    ct
  )
  partial_row_blank <- paste(
    "CUFES:T:AK:a",
    "0,0,0,0,0,,20,cmems_mod_glo_phy_my_0.083deg_P1D-m,no_consistent_wind_product,FALSE",
    sep = ","
  )
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      partial_row_blank,
      cufes_covariate_row("CUFES:T:AK:b", values = rep(0, 6)),
      sep = "\n"
    ),
    cov
  )
  writeLines("event_id,reason,covariate,latitude,longitude", drops)
  cfg <- list(
    species = list(taxon = "sardine"),
    drop_covariates_if_unavailable = "upwelling",
    data = list(
      events_path = ev,
      counts_path = ct,
      covariates_path = cov,
      covariate_drops_path = drops
    ),
    covariates = list(
      dynamic = c("temp_3m", "sal_3m", "mld", "sst_grad", "dist_front", "upwelling"),
      static = "log_depth"
    )
  )
  expect_error(load_model_data(cfg = cfg), "partially blank")
})

test_that("present upwelling is kept in dynamic covariates", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  drops <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header("time_idx"),
      cufes_event_row("CUFES:T:AK:a", 10, time_idx = 1),
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:a,sardine,1", ct)
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:T:AK:a"),
      sep = "\n"
    ),
    cov
  )
  writeLines("event_id,reason,covariate,latitude,longitude", drops)
  cfg <- list(
    species = list(taxon = "sardine"),
    drop_covariates_if_unavailable = "upwelling",
    data = list(
      events_path = ev,
      counts_path = ct,
      covariates_path = cov,
      covariate_drops_path = drops
    ),
    covariates = list(
      dynamic = c("temp_3m", "sal_3m", "mld", "sst_grad", "dist_front", "upwelling"),
      static = "log_depth"
    )
  )
  dat <- load_model_data(cfg = cfg)
  cfg_fit <- apply_model_cfg_patches(cfg, dat)
  expect_equal(nrow(dat), 1L)
  expect_true("upwelling" %in% cfg_fit$covariates$dynamic)
  expect_true("upwelling_z" %in% names(dat))
})
