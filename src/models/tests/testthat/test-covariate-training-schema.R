test_that("training covariate table schema lists every missing column", {
  cfg <- load_sardine_test_cfg()
  cov_path <- cfg$data$covariates_path
  cov <- utils::read.csv(cov_path, stringsAsFactors = FALSE, check.names = FALSE)
  bad <- cov
  bad$source_product <- NULL
  bad$excluded_reason <- NULL
  bad$bottom_depth_m <- NULL
  expect_error(
    assert_training_covariate_table_schema(bad, cfg),
    "missing columns"
  )
})

test_that("bottom_depth_m <= 0 fails with event_id in message", {
  cfg <- load_sardine_test_cfg()
  cov <- utils::read.csv(
    cfg$data$covariates_path,
    stringsAsFactors = FALSE,
    check.names = FALSE
  )
  cov$bottom_depth_m[cov$event_id == "CUFES:TEST:AK:s002"] <- 0
  tmp <- tempfile(fileext = ".csv")
  utils::write.csv(cov, tmp, row.names = FALSE)
  cfg$data$covariates_path <- tmp
  expect_error(load_model_data(cfg = cfg), "bottom_depth_m must be > 0")
})

test_that("fit_delta_engine validates covariate table before fitting", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  tmp <- tempfile(fileext = ".csv")
  bad <- utils::read.csv(
    cfg$data$covariates_path,
    stringsAsFactors = FALSE,
    check.names = FALSE
  )
  bad$MLD_m <- NULL
  utils::write.csv(bad, tmp, row.names = FALSE)
  cfg$data$covariates_path <- tmp
  expect_error(
    fit_delta_engine(dat, mesh, cfg),
    "missing columns: MLD_m"
  )
})

test_that("log_depth_z is derived from bottom_depth_m on load", {
  cfg <- load_sardine_test_cfg()
  dat <- load_model_data(cfg = cfg)
  expect_true("log_depth_z" %in% names(dat))
  expect_true(all(is.finite(dat$log_depth_z)))
})
