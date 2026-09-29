test_that("shared delta formula smoothers match", {
  frm <- build_delta_formula("~ s(sst_z, k = 3)")
  expect_silent(assert_shared_delta_formula(frm))
  bad <- build_delta_formula("~ s(sst_z, k = 3)")
  bad[[2]] <- stats::as.formula("y ~ s(sal_z, k = 3)")
  expect_error(assert_shared_delta_formula(bad))
})

test_that("pilot config uses poisson-link delta with log effort offset", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  expect_true(is_poisson_link_delta(cfg))
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  expect_true(fit_uses_log_effort_offset(fit))
  expect_true("mesh_spatial_scale" %in% names(fit))
  ms <- fit$mesh_spatial_scale
  expect_true(all(c(
    "fitted_spatial_range_km",
    "water_triangle_edge_km",
    "barrier_triangle_edge_km"
  ) %in% names(ms)))
  expect_true(is.finite(ms$water_triangle_edge_km$min_km))
  expect_true(is.finite(ms$fitted_spatial_range_km))
})
