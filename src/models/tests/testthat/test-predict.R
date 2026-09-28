test_that("predictions mask high OOD and physics FAIL", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  dat <- load_model_data(cfg$data$table_path, cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- list(
    fit = fit$fit,
    reference = dat[, c("sst_z", "sal_z")],
    reference_cols = c("sst_z", "sal_z"),
    training_end = "2021-12-31"
  )
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  out <- predict_engine(artifact, grid, cfg, physics_cycle = "FAIL", nsim = 5)
  expect_true(all(out$evidence_state == "Unknown"))
  expect_true(all(is.na(out$p_encounter)))
  expect_false(any(c("X", "Y", "lon", "lat") %in% names(out)))
})
