test_that("spatial block params are read from committed model config fields", {
  cfg <- load_sardine_test_cfg()
  p <- spatial_block_cv_params(cfg)
  expect_equal(p$block_size_km, cfg$mesh$cutoff_km)
  expect_equal(p$seed, as.integer(cfg$prediction$seed))
  expect_equal(p$n_folds, cfg$data$spatial_block_cv$n_folds)
  expect_equal(p$block_size_source, "mesh.cutoff_km")
})

test_that("spatial block assignment is deterministic", {
  cfg <- load_sardine_test_cfg()
  ev <- read.csv(
    file.path(FISHAI_ROOT, "src/models/tests/fixtures/synthetic_cufes_events.csv"),
    stringsAsFactors = FALSE
  )
  ev$fold_id <- NULL
  params <- spatial_block_cv_params(cfg)
  a1 <- assign_cufes_spatial_block_folds(ev, params)
  a2 <- assign_cufes_spatial_block_folds(ev, params)
  expect_identical(a1, a2)
})

test_that("each event receives exactly one fold", {
  cfg <- load_sardine_test_cfg()
  ev <- read.csv(
    file.path(FISHAI_ROOT, "src/models/tests/fixtures/synthetic_cufes_events.csv"),
    stringsAsFactors = FALSE
  )
  ev$fold_id <- NULL
  params <- spatial_block_cv_params(cfg)
  fa <- assign_cufes_spatial_block_folds(ev, params)
  expect_equal(nrow(fa), nrow(ev))
  expect_equal(length(unique(fa$event_id)), nrow(fa))
  expect_true(all(fa$fold_id >= 1L & fa$fold_id <= params$n_folds))
  expect_true(all(nzchar(fa$block_id)))
})

test_that("fold assignment is identical across species (events-only)", {
  ev <- read.csv(
    file.path(FISHAI_ROOT, "src/models/tests/fixtures/synthetic_cufes_events.csv"),
    stringsAsFactors = FALSE
  )
  ev$fold_id <- NULL
  cfg_s <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml")
  )
  cfg_a <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "cufes_anchovy_synthetic.yaml")
  )
  fa_s <- assign_cufes_spatial_block_folds(ev, spatial_block_cv_params(cfg_s))
  fa_a <- assign_cufes_spatial_block_folds(ev, spatial_block_cv_params(cfg_a))
  expect_identical(fa_s, fa_a)
})

test_that("load_model_data attaches identical folds for sardine and anchovy", {
  ev_path <- tempfile(fileext = ".csv")
  on.exit(unlink(ev_path), add = TRUE)
  base_ev <- read.csv(
    file.path(FISHAI_ROOT, "src/models/tests/fixtures/synthetic_cufes_events.csv"),
    stringsAsFactors = FALSE
  )
  base_ev$fold_id <- NULL
  utils::write.csv(base_ev, ev_path, row.names = FALSE)

  cfg_s <- load_sardine_test_cfg()
  cfg_a <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "cufes_anchovy_synthetic.yaml")
  )
  cfg_s$data$events_path <- ev_path
  cfg_a$data$events_path <- ev_path

  d_s <- load_model_data(cfg = cfg_s, min_duration_min = 2)
  d_a <- load_model_data(cfg = cfg_a, min_duration_min = 2)
  merged <- merge(
    d_s[, c("event_id", "fold_id")],
    d_a[, c("event_id", "fold_id")],
    by = "event_id",
    suffixes = c("_s", "_a")
  )
  expect_equal(merged$fold_id_s, merged$fold_id_a)
})
