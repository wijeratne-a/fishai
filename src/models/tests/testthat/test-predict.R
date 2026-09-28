test_that("predictions mask high OOD and physics FAIL", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  artifact$reference <- dat[, ref_cols, drop = FALSE]
  artifact$reference_cols <- ref_cols
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  out <- predict_engine(artifact, grid, cfg, physics_cycle = "FAIL", nsim = 5)
  expect_true(all(out$evidence_state == "Unknown"))
  expect_true(all(is.na(out$p_encounter)))
  expect_false(any(c("X", "Y", "lon", "lat") %in% names(out)))
  expect_true(nzchar(out$metadata_attribution_inference[1]))
})
