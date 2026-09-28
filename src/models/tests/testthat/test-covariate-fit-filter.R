test_that("excluded=FALSE filter summary counts by excluded_reason", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  drops <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header("time_idx"),
      cufes_event_row("CUFES:T:AK:keep", 10, time_idx = 1),
      cufes_event_row("CUFES:T:AK:drop", 10, time_idx = 2),
      sep = "\n"
    ),
    ev
  )
  writeLines(
    "event_id,taxon,count\nCUFES:T:AK:keep,sardine,1\nCUFES:T:AK:drop,sardine,2",
    ct
  )
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:T:AK:keep"),
      cufes_covariate_row(
        "CUFES:T:AK:drop",
        excluded = TRUE,
        excluded_reason = "land_mask"
      ),
      sep = "\n"
    ),
    cov
  )
  writeLines(
    paste(
      "event_id,reason,covariate,latitude,longitude",
      "CUFES:T:AK:drop,land_mask,,33,-119",
      sep = "\n"
    ),
    drops
  )
  cfg <- list(
    species = list(taxon = "sardine"),
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
    response = list(column = "egg_count", effort_column = "volume_m3"),
    mesh = list(cutoff_km = 9),
    model = list(
      formula_shared = "~ 1",
      spatial = list("off", "off"),
      spatiotemporal = list("off", "off"),
      delta_type = "poisson-link"
    )
  )
  dat <- load_model_data(cfg = cfg)
  expect_equal(nrow(dat), 1L)
  qc <- fishai_data_prep_qc(dat)
  expect_equal(qc$covariate_exclusion$n_kept, 1L)
  expect_equal(qc$covariate_exclusion$n_dropped, 1L)
  expect_equal(qc$covariate_exclusion$dropped_by_excluded_reason[["land_mask"]], 1L)

  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  expect_equal(fit$covariate_exclusion_summary$n_dropped, 1L)
  expect_equal(fit$covariate_exclusion_summary$dropped_by_excluded_reason[["land_mask"]], 1L)
  expect_equal(fit$source_product_counts$myint, 0L)
  expect_true(fit$source_product_counts$my >= 1L)
})

test_that("source_product my and myint counts appear on fit output", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  expect_type(fit$source_product_counts$my, "integer")
  expect_type(fit$source_product_counts$myint, "integer")
  expect_equal(
    fit$source_product_counts$my + fit$source_product_counts$myint,
    nrow(dat)
  )
})

test_that("missing covariate after excluded filter stops fit", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header("time_idx"),
      cufes_event_row("CUFES:T:AK:ok", 10, time_idx = 1),
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:ok,sardine,1", ct)
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:T:AK:ok", values = c(NA, 0, 0, 0, 0, 0)),
      sep = "\n"
    ),
    cov
  )
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(events_path = ev, counts_path = ct, covariates_path = cov),
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
    response = list(column = "egg_count", effort_column = "volume_m3"),
    mesh = list(cutoff_km = 9),
    model = list(
      formula_shared = "~ 1",
      spatial = list("off", "off"),
      spatiotemporal = list("off", "off"),
      delta_type = "poisson-link"
    )
  )
  expect_error(load_model_data(cfg = cfg), "kept fit row has missing value in T3m")
})
