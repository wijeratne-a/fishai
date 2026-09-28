test_that("positive_model_fallback refits encounter-only when sanity fails", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  cfg$mesh$barrier$enabled <- FALSE
  cfg$positive_model_fallback <- "encounter_only"
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  old <- getOption("fishai.test.force_positive_fallback")
  on.exit(options(fishai.test.force_positive_fallback = old), add = TRUE)
  options(fishai.test.force_positive_fallback = TRUE)
  fit <- fit_delta_engine(dat, mesh, cfg)
  expect_true(fit$positive_model_fallback_applied)
  expect_identical(fit$positive_model_fallback, "encounter_only")
  expect_false(fit$positive_component_fitted)
})

test_that("positive_component_sanity_ok rejects large gradients", {
  fake <- list(converged = TRUE, gradients = c(0, 0.002), tmb_obj = NULL)
  expect_false(positive_component_sanity_ok(fake))
})
