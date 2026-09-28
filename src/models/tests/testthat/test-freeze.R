test_that("frozen model scores once", {
  td <- tempfile()
  dir.create(td)
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  path <- file.path(td, "artifact.rds")
  freeze_model(fit, cfg, path, training_dat = dat)
  hold <- dat[1:10, ]
  flag <- file.path(td, "scored.flag")
  s1 <- score_frozen_once(path, hold, flag)
  expect_true(is.finite(s1$auc))
  expect_error(score_frozen_once(path, hold, flag), "already scored")
})

test_that("freeze records covariate join drop shares when drop table configured", {
  td <- tempfile()
  dir.create(td)
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  cfg$data$covariate_drops_path <- file.path(
    FISHAI_ROOT,
    "src",
    "models",
    "tests",
    "fixtures",
    "synthetic_covariate_drops.csv"
  )
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  path <- file.path(td, "artifact.rds")
  art <- freeze_model(fit, cfg, path, training_dat = dat)
  drops <- art$reference_volume$source$covariate_join_drops
  expect_true(is.list(drops))
  expect_gt(drops$n_join_dropped, 0L)
  expect_true(is.finite(drops$share_all_events))
  expect_true(is.finite(drops$share_all_events_nearshore))
  expect_true(is.finite(drops$share_all_events_short))
  expect_true(is.finite(drops$share_positive_events_long))
})

test_that("covariate drop table must reference known cufes_events ids", {
  td <- tempfile()
  dir.create(td)
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  cfg$data$covariate_drops_path <- file.path(
    FISHAI_ROOT,
    "src",
    "models",
    "tests",
    "fixtures",
    "synthetic_covariate_drops.csv"
  )
  bad <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,reason,covariate,latitude,longitude",
      "CUFES:MISSING:XX:999,missing_covariate,T3m,33,-119",
      sep = "\n"
    ),
    bad
  )
  cfg$data$covariate_drops_path <- bad
  expect_error(load_model_data(cfg = cfg), "not found in cufes_events")
})
