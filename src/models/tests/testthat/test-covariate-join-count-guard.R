test_that("freeze passes when bot2 input_event_count matches event_count_guard and cov rows", {
  td <- tempfile()
  dir.create(td)
  proto <- load_short_sample_protocol(
    file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "sensitivity_protocol_test.yaml")
  )
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  cfg$data$event_count_guard <- proto$event_count_guard
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  path <- file.path(td, "artifact.rds")
  expect_no_error(freeze_model(fit, cfg, path, training_dat = dat))
})

test_that("freeze fails when bot2 input_event_count is raw-pull not post-QC guard", {
  td <- tempfile()
  dir.create(td)
  bad_summary <- tempfile(fileext = ".json")
  writeLines(
    paste(
      '{"drop_summary":{"input_event_count":15969,"dropped_unique_total":0}}',
      sep = ""
    ),
    bad_summary
  )
  proto <- load_short_sample_protocol(
    file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "sensitivity_protocol_test.yaml")
  )
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  cfg$data$event_count_guard <- proto$event_count_guard
  cfg$data$covariate_drop_summary_path <- bad_summary
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  path <- file.path(td, "artifact.rds")
  expect_error(
    freeze_model(fit, cfg, path, training_dat = dat),
    "input_event_count \\(15969\\) != event_count_guard n_events \\(48\\)"
  )
})

test_that("freeze fails when covariate output row count differs from event_count_guard", {
  td <- tempfile()
  dir.create(td)
  proto <- load_short_sample_protocol(
    file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "sensitivity_protocol_test.yaml")
  )
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  cfg$data$event_count_guard <- proto$event_count_guard
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  cfg$data$event_count_guard$n_events <- 47L
  bad_summary <- tempfile(fileext = ".json")
  writeLines('{"drop_summary":{"input_event_count":47,"dropped_unique_total":2}}', bad_summary)
  cfg$data$covariate_drop_summary_path <- bad_summary
  path <- file.path(td, "artifact.rds")
  expect_error(
    freeze_model(fit, cfg, path, training_dat = dat),
    "covariate output row count \\(48\\) != event_count_guard n_events \\(47\\)"
  )
})
