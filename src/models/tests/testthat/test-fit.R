test_that("shared delta formula smoothers match", {
  frm <- build_delta_formula("~ s(sst_z, k = 3)")
  expect_silent(assert_shared_delta_formula(frm))
  bad <- build_delta_formula("~ s(sst_z, k = 3)")
  bad[[2]] <- stats::as.formula("y ~ s(sal_z, k = 3)")
  expect_error(assert_shared_delta_formula(bad))
})

test_that("pilot config uses poisson-link delta with log effort offset", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  expect_true(is_poisson_link_delta(cfg))
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  expect_true(fit_uses_log_effort_offset(fit))
})
