test_that("binomial config is detected", {
  cfg <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "adult_cps_sardine_encounter.yaml")
  )
  expect_true(is_binomial_model(cfg))
  expect_false(is_poisson_link_delta(cfg))
})

test_that("encounter scoring uses logistic link for binomial fits", {
  skip_if_not_installed("sdmTMB")
  cfg <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml")
  )
  cfg$model$family <- "binomial"
  cfg$model$delta_type <- NULL
  cfg$response$column <- "egg_count"
  dat <- load_model_data(cfg = cfg)
  dat$y <- as.integer(dat$y > 0)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_binomial_engine(dat, mesh, cfg)
  p <- score_encounter_on_events(fit$fit, dat, cfg)
  expect_true(all(p >= 0 & p <= 1))
})
