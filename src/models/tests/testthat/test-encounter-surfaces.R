test_that("hindcast surface is HINDCAST_GLORYS and schema-shaped", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  artifact$reference <- dat[, ref_cols, drop = FALSE]
  artifact$reference_cols <- ref_cols
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  for (col in ref_cols) {
    grid[[col]] <- stats::median(dat[[col]])
  }
  out <- run_hindcast_encounter_surface(
    artifact,
    grid,
    cfg,
    species = "sardine",
    valid_day = "2020-06-01",
    dry_run = TRUE,
    nsim = 4L
  )
  expect_true(nrow(out) >= 1)
  expect_true(all(out$species == "sardine"))
  expect_true(all(out$evidence_state %in% c("HINDCAST_GLORYS", "UNKNOWN")))
  expect_true(all(out$dry_run))
  expect_true(all(out$lead_days == 0L))
  expect_false(any(c("X", "Y", "lon", "lat") %in% names(out)))
  unk <- out$evidence_state == "UNKNOWN"
  expect_true(all(is.na(out$p_encounter[unk])))
  issued <- !unk
  if (any(issued)) {
    expect_true(all(out$evidence_state[issued] == "HINDCAST_GLORYS"))
    expect_true(all(out$p_encounter[issued] >= 0 & out$p_encounter[issued] <= 1))
  }
  expect_true(all(grepl("^g-?[0-9]+_-?[0-9]+$", out$cell_id)))
})

test_that("nowcast surface is NOWCAST_UNVALIDATED at age 0", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  artifact$reference <- dat[, ref_cols, drop = FALSE]
  artifact$reference_cols <- ref_cols
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  for (col in ref_cols) {
    grid[[col]] <- stats::median(dat[[col]])
  }
  out <- run_nowcast_encounter_surface(
    artifact,
    grid,
    cfg,
    species = "anchovy",
    valid_day = "2099-01-01",
    source_run_time = "2099-01-01T00:00:00Z",
    dry_run = TRUE,
    nsim = 4L
  )
  issued <- out$evidence_state != "UNKNOWN"
  expect_true(any(issued))
  expect_true(all(out$evidence_state[issued] == "NOWCAST_UNVALIDATED"))
  expect_true(all(out$lead_days == 0L))
  expect_true(all(out$forecast_age_hours == 0))
  expect_false(any(out$fallback_used))
  expect_true(all(is.na(out$p_encounter[out$evidence_state == "UNKNOWN"])))
})

test_that("72-hour forecast emits lead days 1, 2, and 3", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  artifact$reference <- dat[, ref_cols, drop = FALSE]
  artifact$reference_cols <- ref_cols
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  for (col in ref_cols) {
    grid[[col]] <- stats::median(dat[[col]])
  }
  out <- run_forecast_encounter_surface(
    artifact,
    grid,
    cfg,
    species = "sardine",
    issue_day = "2099-01-01",
    source_run_time = "2099-01-01T00:00:00Z",
    horizon_hours = 72,
    dry_run = TRUE,
    nsim = 4L
  )
  expect_equal(sort(unique(out$lead_days)), c(1L, 2L, 3L))
  expect_equal(sort(unique(out$valid_day)), c("2099-01-02", "2099-01-03", "2099-01-04"))
  issued <- out$evidence_state != "UNKNOWN"
  expect_true(any(issued))
  expect_true(all(out$evidence_state[issued] == "FORECAST"))
  expect_true(all(is.na(out$p_encounter[!issued])))
  expect_error(
    run_forecast_encounter_surface(
      artifact, grid, cfg, "sardine", "2099-01-01", "2099-01-01T00:00:00Z",
      horizon_hours = 48, dry_run = TRUE, nsim = 2L
    ),
    "72"
  )
})
