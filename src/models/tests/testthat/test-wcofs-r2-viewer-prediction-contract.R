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
  grid <- grid[seq_len(min(8L, nrow(grid))), , drop = FALSE]
  list(cfg = cfg, artifact = artifact, grid = grid)
}

test_that("R-2 two-missed-runs viewer contract and lead_days from forecast_age_hours", {
  target <- as.Date("2026-09-28")
  r2 <- target - 2L
  r_target <- as.POSIXct("2026-09-28T03:00:00", tz = "UTC")
  r_source <- as.POSIXct(format(r2, "%Y-%m-%dT03:00:00"), tz = "UTC")
  fx <- .wcofs_predict_fixture()
  fx$cfg$prediction$hindcast_evidence <- FALSE
  fx$cfg$prediction$interval_widen_per_24h <- 0.25
  fx$cfg$prediction$interval_widen_base <- 1.0

  assert_r2_step <- function(valid_offset_h) {
    age <- valid_offset_h + 48
    valid <- r_target + as.difftime(valid_offset_h, units = "hours")
    out <- predict_engine(
      fx$artifact,
      fx$grid,
      fx$cfg,
      nsim = 25L,
      species = "sardine",
      valid_day = format(target, "%Y-%m-%d"),
      dry_run = TRUE,
      forecast_age_hours = age,
      fallback_used = TRUE,
      valid_time = format(valid, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
      source_run_time = format(r_source, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
    )
    expect_true(all(out$evidence_state == "FORECAST"))
    expect_true(all(out$fallback_used))
    expect_equal(unique(out$source_run_time), format(r_source, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"))
    expect_equal(unique(out$forecast_age_hours), age)
    expected_lead <- as.integer(min(3L, max(1L, ceiling(age / 24))))
    expect_equal(unique(out$lead_days), expected_lead)
    offset_lead <- as.integer(min(3L, max(1L, ceiling(valid_offset_h / 24))))
    if (valid_offset_h < 0L) {
      expect_false(expected_lead == offset_lead)
    }
    width <- out$p_hi90 - out$p_lo90
    expect_true(all(is.finite(width)))
    list(out = out, width = mean(width, na.rm = TRUE), age = age, offset = valid_offset_h)
  }

  low <- assert_r2_step(-21L)
  high <- assert_r2_step(24L)
  for (off in seq(-21L, 24L, by = 3L)) {
    step <- assert_r2_step(off)
    expect_equal(step$age, off + 48)
    expect_true(step$age >= 27 && step$age <= 72)
  }
  expect_gt(high$width, low$width)

  same_age <- assert_r2_step(-21L)
  fake_offset_run <- predict_engine(
    fx$artifact,
    fx$grid,
    fx$cfg,
    nsim = 25L,
    forecast_age_hours = same_age$age,
    fallback_used = TRUE,
    valid_time = format(r_target + as.difftime(24, units = "hours"), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
    source_run_time = format(r_source, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
  )
  width_fake <- mean(fake_offset_run$p_hi90 - fake_offset_run$p_lo90, na.rm = TRUE)
  expect_equal(width_fake, same_age$width, tolerance = 0.02)

  unk <- predict_engine(
    fx$artifact,
    fx$grid,
    fx$cfg,
    nsim = 5L,
    wcofs_unknown_reason = "missing_operational_cycle",
    valid_time = format(r_target + as.difftime(27, units = "hours"), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
    source_run_time = format(r_source, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
  )
  expect_true(all(unk$evidence_state == "UNKNOWN"))
  expect_equal(unique(unk$unknown_reason), "missing_operational_cycle")
  expect_equal(unique(unk$lead_days), 0L)
  unk72 <- predict_engine(
    fx$artifact,
    fx$grid,
    fx$cfg,
    nsim = 5L,
    wcofs_unknown_reason = "missing_operational_cycle",
    valid_time = format(r_target + as.difftime(72, units = "hours"), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
    source_run_time = format(r_source, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
  )
  expect_true(all(is.na(unk$p_encounter)))
})

test_that("valid_time_mismatch is UNKNOWN with reason passthrough and no fill", {
  fx <- .wcofs_predict_fixture()
  out <- predict_engine(
    fx$artifact,
    fx$grid,
    fx$cfg,
    nsim = 5L,
    wcofs_unknown_reason = "valid_time_mismatch",
    valid_time = "2026-09-28T06:00:00Z"
  )
  expect_true(all(out$evidence_state == "UNKNOWN"))
  expect_equal(unique(out$unknown_reason), "valid_time_mismatch")
  expect_true(all(is.na(out$p_encounter)))
  expect_equal(unique(out$lead_days), 0L)
})

test_that("viewer contract columns include WCOFS provenance fields", {
  fx <- .wcofs_predict_fixture()
  out <- predict_engine(
    fx$artifact,
    fx$grid,
    fx$cfg,
    nsim = 5L,
    forecast_age_hours = 27,
    fallback_used = TRUE,
    valid_time = "2026-09-27T06:00:00Z",
    source_run_time = "2026-09-26T03:00:00Z"
  )
  need <- c(
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
    "valid_time"
  )
  expect_true(all(need %in% names(out)))
})
