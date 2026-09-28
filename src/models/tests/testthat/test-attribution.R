test_that("freeze records training source attributions from SOURCES.yaml", {
  td <- tempfile()
  dir.create(td)
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  path <- file.path(td, "artifact.rds")
  art <- freeze_model(fit, cfg, path)
  expect_length(art$training_sources, 2)
  ids <- vapply(art$training_sources, function(x) x$source_id, character(1))
  expect_true(all(c("calcofi_cufes", "glorys") %in% ids))
  expect_true(all(nzchar(vapply(art$training_sources, function(x) x$attribution, character(1)))))
  manifest <- load_sources_manifest()
  calcofi_attr <- art$training_sources[[which(ids == "calcofi_cufes")]]$attribution
  expect_equal(calcofi_attr, trimws(manifest$sources$calcofi_cufes$attribution))
  expect_false(grepl("Creative Commons|CC-BY", calcofi_attr, ignore.case = TRUE))
  glorys_attr <- art$training_sources[[which(ids == "glorys")]]$attribution
  expect_match(glorys_attr, "Generated using E\\.U\\. Copernicus Marine Service Information")
  expect_match(glorys_attr, "10\\.48670/moi-00021")
})

test_that("predict propagates training and inference attributions", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c(
    "temp_3m_z", "sal_3m_z", "mld_z", "sst_grad_z",
    "dist_front_z", "upwelling_z", "log_depth_z"
  )
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  art <- freeze_model(fit, cfg, tempfile(fileext = ".rds"))
  art$reference <- dat[, ref_cols, drop = FALSE]
  art$reference_cols <- ref_cols
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  out <- predict_engine(art, grid, cfg, physics_cycle = "FAIL", nsim = 5)
  expect_true(grepl("calcofi_cufes", out$metadata_attribution_training[1], fixed = TRUE))
  expect_true(grepl("glorys", out$metadata_attribution_training[1], fixed = TRUE))
  expect_true(grepl("Generated using E\\.U\\. Copernicus Marine Service Information", out$metadata_attribution_inference[1]))
  expect_true(grepl("10\\.48670/moi-00021", out$metadata_attribution_inference[1]))
})

test_that("predict refuses output when attributions are incomplete", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  bad_art <- list(
    fit = fit$fit,
    training_end = "2021-12-31",
    reference = dat[, c("temp_3m_z", "sal_3m_z")],
    reference_cols = c("temp_3m_z", "sal_3m_z")
  )
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  expect_error(
    predict_engine(bad_art, grid, cfg, nsim = 3),
    "training_sources"
  )
  cfg_bad <- cfg
  cfg_bad$prediction$inference_forcing_source_id <- NULL
  good_art <- freeze_model(fit, cfg, tempfile(fileext = ".rds"))
  good_art$reference <- dat[, c("temp_3m_z", "sal_3m_z")]
  good_art$reference_cols <- c("temp_3m_z", "sal_3m_z")
  expect_error(
    predict_engine(good_art, grid, cfg_bad, nsim = 3),
    "inference_forcing_source_id"
  )
})
