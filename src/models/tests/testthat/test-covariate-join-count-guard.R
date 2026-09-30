synthetic_drop_summary_json <- function(overrides = list()) {
  base <- list(
    schema_version = 1L,
    input_event_count = 48L,
    dropped_unique_total = 2L,
    unique_by_reason = list(
      missing_endpoint = 0L,
      land_mask = 1L,
      too_few_track_points = 0L,
      missing_covariate = 1L
    ),
    rows_by_reason = list(
      missing_endpoint = 0L,
      land_mask = 1L,
      too_few_track_points = 0L,
      missing_covariate = 1L
    )
  )
  if (length(overrides)) {
    for (nm in names(overrides)) {
      base[[nm]] <- overrides[[nm]]
    }
  }
  jsonlite::toJSON(base, auto_unbox = TRUE, null = "null")
}

freeze_with_event_count_guard <- function(summary_json = NULL, guard_overrides = list()) {
  td <- tempfile()
  dir.create(td)
  proto <- load_short_sample_protocol(
    file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "sensitivity_protocol_test.yaml")
  )
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  guard <- proto$event_count_guard
  if (length(guard_overrides)) {
    for (nm in names(guard_overrides)) {
      guard[[nm]] <- guard_overrides[[nm]]
    }
  }
  cfg$data$event_count_guard <- guard
  if (!is.null(summary_json)) {
    summary_path <- tempfile(fileext = ".json")
    writeLines(as.character(summary_json), summary_path)
    cfg$data$covariate_drop_summary_path <- summary_path
  }
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  list(
    cfg = cfg,
    dat = dat,
    fit = fit,
    path = file.path(td, "artifact.rds")
  )
}

test_that("freeze passes when bot2 summary matches drops, covariates, and event_count_guard", {
  fx <- freeze_with_event_count_guard()
  expect_no_error(freeze_model(fx$fit, fx$cfg, fx$path, training_dat = fx$dat))
})

test_that("freeze fails when input_event_count is raw-pull not post-QC guard", {
  fx <- freeze_with_event_count_guard(
    summary_json = synthetic_drop_summary_json(list(input_event_count = 15969L))
  )
  expect_error(
    freeze_model(fx$fit, fx$cfg, fx$path, training_dat = fx$dat),
    "input_event_count \\(15969\\) != event_count_guard n_events \\(48\\)"
  )
})

test_that("freeze fails when covariate output row count differs from event_count_guard", {
  fx <- freeze_with_event_count_guard()
  fx$cfg$data$event_count_guard$n_events <- 47L
  fx$cfg$data$covariate_drop_summary_path <- tempfile(fileext = ".json")
  writeLines(
    as.character(synthetic_drop_summary_json(list(input_event_count = 47L))),
    fx$cfg$data$covariate_drop_summary_path
  )
  expect_error(
    freeze_model(fx$fit, fx$cfg, fx$path, training_dat = fx$dat),
    "covariate output row count \\(48\\) != event_count_guard n_events \\(47\\)"
  )
})

test_that("freeze fails on unsupported covariate drop summary schema_version", {
  fx <- freeze_with_event_count_guard(
    summary_json = synthetic_drop_summary_json(list(schema_version = 2L))
  )
  expect_error(
    freeze_model(fx$fit, fx$cfg, fx$path, training_dat = fx$dat),
    "schema_version must be 1"
  )
})

test_that("freeze fails when unique_by_reason is missing a required reason key", {
  bad <- list(
    schema_version = 1L,
    input_event_count = 48L,
    dropped_unique_total = 2L,
    unique_by_reason = list(
      missing_endpoint = 0L,
      land_mask = 1L,
      too_few_track_points = 0L
    ),
    rows_by_reason = list(
      missing_endpoint = 0L,
      land_mask = 1L,
      too_few_track_points = 0L,
      missing_covariate = 1L
    )
  )
  fx <- freeze_with_event_count_guard(summary_json = jsonlite::toJSON(bad, auto_unbox = TRUE))
  expect_error(
    freeze_model(fx$fit, fx$cfg, fx$path, training_dat = fx$dat),
    "unique_by_reason must include exactly"
  )
})

test_that("freeze fails when dropped_unique_total mismatches drop table", {
  fx <- freeze_with_event_count_guard(
    summary_json = synthetic_drop_summary_json(list(dropped_unique_total = 99L))
  )
  expect_error(
    freeze_model(fx$fit, fx$cfg, fx$path, training_dat = fx$dat),
    "dropped_unique_total \\(99\\)"
  )
})

test_that("freeze fails when unique_by_reason count mismatches drop table for a reason", {
  u <- list(
    missing_endpoint = 0L,
    land_mask = 1L,
    too_few_track_points = 0L,
    missing_covariate = 99L
  )
  fx <- freeze_with_event_count_guard(
    summary_json = synthetic_drop_summary_json(list(unique_by_reason = u))
  )
  expect_error(
    freeze_model(fx$fit, fx$cfg, fx$path, training_dat = fx$dat),
    "unique_by_reason\\$missing_covariate"
  )
})
