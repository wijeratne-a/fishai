test_that("encounter probability rises with volume under poisson-link offset", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  cfg$model$formula_shared <- "~ 1"
  cfg$model$spatial <- list("off", "off")
  cfg$model$spatiotemporal <- list("off", "off")
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)

  base <- dat[1, , drop = FALSE]
  vols <- c(20, 80, 320)
  nd <- do.call(rbind, lapply(vols, function(v) {
    x <- base
    x$volume_m3 <- v
    x$log_effort <- log(v)
    x$y <- 0L
    x
  }))

  p <- score_encounter_on_events(fit$fit, nd, cfg)
  expect_equal(length(p), 3L)
  expect_true(all(diff(p) > 0))
  expect_true(all(p > 0 & p < 1))
})

test_that("freeze stores median reference_volume_m3 from training QC data", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  cfg$model$formula_shared <- "~ 1"
  cfg$model$spatial <- list("off", "off")
  cfg$model$spatiotemporal <- list("off", "off")
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  art <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  expect_equal(
    art$config$prediction$reference_volume_m3,
    unname(stats::median(dat$volume_m3))
  )
  expect_equal(art$reference_volume$source$n_events_fitting_frame, nrow(dat))
  expect_false(art$config$prediction$reference_volume_m3 == 1)
})

test_that("map prediction uses log V_ref offset; events use log(volume_m3)", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  cfg$model$formula_shared <- "~ 1"
  cfg$model$spatial <- list("off", "off")
  cfg$model$spatiotemporal <- list("off", "off")
  dat <- load_model_data(cfg = cfg)
  dat <- dat[seq_len(min(18L, nrow(dat))), ]
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  art <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  art$reference <- dat[, c("temp_3m_z", "sal_3m_z", "mld_z"), drop = FALSE]
  art$reference_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")

  hold <- dat[1:3, , drop = FALSE]
  p_event <- score_encounter_on_events(art$fit, hold, cfg)

  grid <- hold
  p_map <- predict_encounter_on_grid(art$fit, grid, art, cfg)
  expect_false(isTRUE(all.equal(p_event, p_map)))

  vref <- art$config$prediction$reference_volume_m3
  hold$log_effort <- log(vref)
  p_at_vref <- score_encounter_on_events(art$fit, hold, cfg)
  expect_equal(p_map, p_at_vref, tolerance = 1e-6)
})

test_that("predict_engine refuses without reference_volume_m3", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  cfg$model$formula_shared <- "~ 1"
  cfg$model$spatial <- list("off", "off")
  cfg$model$spatiotemporal <- list("off", "off")
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  art <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  art$reference <- dat[, c("temp_3m_z", "sal_3m_z"), drop = FALSE]
  art$reference_cols <- c("temp_3m_z", "sal_3m_z")
  art$config$prediction$reference_volume_m3 <- NULL
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  expect_error(
    predict_engine(art, grid, cfg, physics_cycle = "FAIL", nsim = 3),
    "reference_volume_m3"
  )
})

test_that("predict output records reference volume basis", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  cfg$model$formula_shared <- "~ 1"
  cfg$model$spatial <- list("off", "off")
  cfg$model$spatiotemporal <- list("off", "off")
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  art <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  art$reference <- dat[, ref_cols, drop = FALSE]
  art$reference_cols <- ref_cols
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  out <- predict_engine(art, grid, cfg, physics_cycle = "FAIL", nsim = 3)
  expect_true(all(out$reference_volume_m3 == art$config$prediction$reference_volume_m3))
  expect_match(out$metadata_encounter_effort_basis[1], "encounter probability per")
  expect_match(out$metadata_encounter_effort_basis[1], "m\\^3 filtered")
})
