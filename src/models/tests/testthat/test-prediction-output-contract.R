test_that("predict_engine emits prediction output contract columns", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  cfg$prediction$hindcast_evidence <- TRUE
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  artifact$reference <- dat[, ref_cols, drop = FALSE]
  artifact$reference_cols <- ref_cols
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  out <- predict_engine(
    artifact,
    grid,
    cfg,
    nsim = 1L,
    species = "sardine",
    valid_day = "2020-06-01",
    dry_run = TRUE
  )
  need <- c(
    "cell_id",
    "species",
    "valid_day",
    "p_encounter",
    "p_lo90",
    "p_hi90",
    "ood_level",
    "evidence_state",
    "unknown_reason",
    "lead_days",
    "forecast_age_hours",
    "source_run_time",
    "fallback_used",
    "valid_time",
    "dry_run"
  )
  expect_true(all(need %in% names(out)))
  expect_true(all(out$evidence_state %in% c(
    "HINDCAST_GLORYS",
    "NOWCAST_UNVALIDATED",
    "FORECAST",
    "DEGRADED",
    "UNKNOWN"
  )))
  expect_true(all(out$lead_days >= 0L & out$lead_days <= 3L))
})
