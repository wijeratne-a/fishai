test_that("random CV folds are refused", {
  expect_error(run_cv_spatial(data.frame(), NULL, list(model = list()), NULL), "random")
})

test_that("spatial CV runs on synthetic folds", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  dat <- load_model_data(cfg$data$table_path, cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  cv <- run_cv_spatial(dat, mesh, cfg, dat$fold_id)
  expect_true(is.finite(cv$sum_loglik))
})
