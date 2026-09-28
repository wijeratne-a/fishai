test_that("shared delta formula smoothers match", {
  frm <- build_delta_formula("~ log_effort + s(sst_z, k = 3)")
  expect_silent(assert_shared_delta_formula(frm))
  bad <- build_delta_formula("~ log_effort + s(sst_z, k = 3)")
  bad[[2]] <- stats::as.formula("y ~ log_effort + s(sal_z, k = 3)")
  expect_error(assert_shared_delta_formula(bad))
})

test_that("offset applies to positive component only", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  expect_true(offset_applies_to_positive_only(fit))
})
