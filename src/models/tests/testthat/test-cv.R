test_that("random CV folds are refused", {
  expect_error(run_cv_spatial(data.frame(), NULL, list(model = list()), NULL), "random")
})

test_that("spatial CV runs on synthetic folds", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  cfg$model$formula_shared <- "~ 1"
  cfg$model$spatial <- list("off", "off")
  cfg$model$spatiotemporal <- list("off", "off")
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  cv <- run_cv_spatial(dat, mesh, cfg, dat$fold_id)
  expect_equal(cv$n_failed_folds, 0L)
  expect_true(is.finite(cv$sum_loglik))
})

test_that("spatial CV records failed folds instead of crashing", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  cv <- run_cv_spatial(dat, mesh, cfg, dat$fold_id)
  expect_gt(cv$n_failed_folds, 0L)
  expect_true(is.na(cv$sum_loglik))
  expect_true(is.list(cv$fold_failures))
  expect_true(length(cv$fold_failures) >= 1L)
})
