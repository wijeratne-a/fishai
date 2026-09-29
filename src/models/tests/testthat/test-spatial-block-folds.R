test_that("spatial block params are read from committed model config fields", {
  cfg <- load_sardine_test_cfg()
  p <- spatial_block_cv_params(cfg)
  expect_equal(p$block_size_km, max(cfg$mesh$cutoff_km, cfg$mesh$range_guess_km))
  expect_equal(p$spatial_range_km, cfg$mesh$range_guess_km)
  expect_equal(p$seed, as.integer(cfg$prediction$seed))
  expect_equal(p$n_folds, cfg$data$spatial_block_cv$n_folds)
  expect_equal(p$block_size_source, "max(mesh.cutoff_km, mesh.range_guess_km)")
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

test_that("spatial blocks are contiguous and at least the pre-registered range", {
  cfg <- load_sardine_test_cfg()
  ev <- read.csv(
    file.path(FISHAI_ROOT, "src/models/tests/fixtures/synthetic_cufes_events.csv"),
    stringsAsFactors = FALSE
  )
  ev$fold_id <- NULL
  params <- spatial_block_cv_params(cfg)
  fa <- assign_cufes_spatial_block_folds(ev, params)
  expect_gte(params$block_size_km, params$spatial_range_km)
  expect_true(verify_spatial_block_contiguity(fa, ev, params))
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
  base_ev$block_id <- NULL
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
    d_s[, c("event_id", "fold_id", "block_id")],
    d_a[, c("event_id", "fold_id", "block_id")],
    by = "event_id",
    suffixes = c("_s", "_a")
  )
  expect_equal(merged$fold_id_s, merged$fold_id_a)
  expect_equal(merged$block_id_s, merged$block_id_a)
})

test_that("fold assignment CSV may cover all events while fit scope is a subset", {
  ev_path <- tempfile(fileext = ".csv")
  fold_path <- tempfile(fileext = ".csv")
  on.exit(unlink(c(ev_path, fold_path)), add = TRUE)
  base_ev <- read.csv(
    file.path(FISHAI_ROOT, "src/models/tests/fixtures/synthetic_cufes_events.csv"),
    stringsAsFactors = FALSE
  )
  base_ev$fold_id <- NULL
  base_ev$block_id <- NULL
  utils::write.csv(base_ev, ev_path, row.names = FALSE)

  cfg <- load_sardine_test_cfg()
  cfg$data$events_path <- ev_path
  cfg$data$fold_assignment_path <- fold_path
  fa <- assign_cufes_spatial_block_folds(base_ev, spatial_block_cv_params(cfg))
  write_fold_assignment_csv(fa, fold_path)

  dat_fit <- load_model_data(cfg = cfg, min_duration_min = 2, egg_split_scope = "fit")
  expect_true(all(dat_fit$event_id %in% fa$event_id))
  expect_false(any(is.na(dat_fit$fold_id)))
  keyed <- merge(
    dat_fit[, c("event_id", "fold_id", "block_id")],
    fa,
    by = "event_id",
    suffixes = c("_used", "_assigned")
  )
  expect_equal(keyed$fold_id_used, keyed$fold_id_assigned)
  expect_equal(keyed$block_id_used, keyed$block_id_assigned)
})

test_that("load_model_data assigns contiguous EPSG:32611 blocks, one fold per block", {
  cfg <- load_sardine_test_cfg()
  ev <- read.csv(
    file.path(FISHAI_ROOT, "src/models/tests/fixtures/synthetic_cufes_events.csv"),
    stringsAsFactors = FALSE
  )
  expect_false("fold_id" %in% names(ev))
  params <- spatial_block_cv_params(cfg)
  expect_equal(params$epsg, 32611L)
  fa <- assign_cufes_spatial_block_folds(ev, params)
  expect_true(verify_spatial_block_contiguity(fa, ev, params))
  dat <- load_model_data(cfg = cfg, min_duration_min = 2)
  keyed <- merge(
    dat[, c("event_id", "fold_id", "block_id")],
    fa,
    by = "event_id",
    suffixes = c("_used", "_assigned")
  )
  expect_equal(nrow(keyed), nrow(dat))
  expect_equal(keyed$fold_id_used, keyed$fold_id_assigned)
  expect_equal(keyed$block_id_used, keyed$block_id_assigned)
  splits <- split(keyed$fold_id_used, keyed$block_id_used)
  expect_true(all(vapply(splits, function(x) length(unique(x)) == 1L, logical(1))))
})

test_that("a stale fold_id column that disagrees with the spatial assignment is refused", {
  ev_path <- tempfile(fileext = ".csv")
  on.exit(unlink(ev_path), add = TRUE)
  ev <- read.csv(
    file.path(FISHAI_ROOT, "src/models/tests/fixtures/synthetic_cufes_events.csv"),
    stringsAsFactors = FALSE
  )
  ev$fold_id <- 1L
  utils::write.csv(ev, ev_path, row.names = FALSE)
  cfg <- load_sardine_test_cfg()
  cfg$data$events_path <- ev_path
  expect_error(
    load_model_data(cfg = cfg, min_duration_min = 2),
    "fold_id disagrees with the spatial-block fold assignment",
    fixed = TRUE
  )
})
