.wcofs_predict_fixture <- function() {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  cfg$prediction$hindcast_evidence <- FALSE
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  artifact$reference <- dat[, ref_cols, drop = FALSE]
  artifact$reference_cols <- ref_cols
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  list(cfg = cfg, artifact = artifact, grid = grid)
}

test_that("WCOFS forecast_age -3h and 0h yield nowcast lead_days 0", {
  fx <- .wcofs_predict_fixture()
  for (age in c(-3, 0)) {
    out <- predict_engine(
      fx$artifact,
      fx$grid,
      fx$cfg,
      nsim = 1L,
      forecast_age_hours = age,
      fallback_used = FALSE
    )
    expect_equal(unique(out$lead_days), 0L)
    expect_true(all(out$evidence_state == "NOWCAST_UNVALIDATED"))
  }
})

test_that("WCOFS age 24h with fallback yields forecast lead_days 1", {
  fx <- .wcofs_predict_fixture()
  out <- predict_engine(
    fx$artifact,
    fx$grid,
    fx$cfg,
    nsim = 1L,
    forecast_age_hours = 24,
    fallback_used = TRUE
  )
  expect_equal(unique(out$lead_days), 1L)
  expect_true(all(out$evidence_state == "FORECAST"))
})

test_that("nowcast with missing lead_days input still outputs lead_days 0", {
  fx <- .wcofs_predict_fixture()
  out <- predict_engine(
    fx$artifact,
    fx$grid,
    fx$cfg,
    nsim = 1L,
    forecast_age_hours = -3,
    fallback_used = FALSE,
    lead_days_input = NA_real_
  )
  expect_equal(unique(out$lead_days), 0L)
})

test_that("invalid lead_days input -1 stops before output", {
  fx <- .wcofs_predict_fixture()
  expect_error(
    predict_engine(
      fx$artifact,
      fx$grid,
      fx$cfg,
      nsim = 1L,
      forecast_age_hours = 0,
      fallback_used = FALSE,
      lead_days_input = -1L
    ),
    "invalid lead_days input"
  )
})

test_that("missing cycle yields UNKNOWN with upstream reason", {
  fx <- .wcofs_predict_fixture()
  out <- predict_engine(
    fx$artifact,
    fx$grid,
    fx$cfg,
    nsim = 1L,
    wcofs_unknown_reason = "missing_operational_cycle"
  )
  expect_true(all(out$evidence_state == "UNKNOWN"))
  expect_equal(unique(out$unknown_reason), "missing_operational_cycle")
  expect_equal(unique(out$lead_days), 0L)
})
