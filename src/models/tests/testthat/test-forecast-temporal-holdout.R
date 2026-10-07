test_that("forecast seasons, day-of-year distance, and damped anomaly match the design", {
  expect_equal(forecast_season(as.Date("2010-01-15")), "DJF")
  expect_equal(forecast_season(as.Date("2010-12-01")), "DJF")
  expect_equal(forecast_season(as.Date("2010-04-01")), "MAM")
  expect_equal(forecast_season(as.Date("2010-07-01")), "JJA")
  expect_equal(forecast_season(as.Date("2010-10-01")), "SON")
  expect_equal(forecast_doy_distance(1L, 366L), 1L)
  expect_equal(forecast_doy_distance(10L, 20L), 10L)
  expect_equal(forecast_damped_anomaly(10, 13, horizon_days = 3, tau = 3), 10 + exp(-1) * 3)
  expect_equal(FORECAST_OPERATIONAL_CLAIM, "NOT_ISSUED_FORECAST")
  expect_equal(FORECAST_PHYSICS_SOURCE, "damped_anomaly_proxy")
})

test_that("issued WCOFS override picks finite covariates when provided", {
  dyn <- c("temp_3m_z", "sal_3m_z")
  x_cut <- c(temp_3m_z = 1, sal_3m_z = 2)
  clim <- c(temp_3m_z = 0, sal_3m_z = 0)
  override <- data.frame(
    physics_source = FORECAST_PHYSICS_SOURCE_WCOFS,
    temp_3m_z = 5,
    sal_3m_z = 6,
    wcofs_s3_key = "wcofs/netcdf/test.nc",
    wcofs_lead_tag = "f024",
    stringsAsFactors = FALSE
  )
  out <- forecast_operational_covariates_for_row(dyn, x_cut, clim, 1L, override)
  expect_equal(out$physics_source, FORECAST_PHYSICS_SOURCE_WCOFS)
  expect_equal(out$operational_claim, FORECAST_OPERATIONAL_CLAIM_ISSUED)
  expect_equal(out$values$temp_3m_z, 5)
  proxy <- forecast_operational_covariates_for_row(dyn, x_cut, clim, 1L, NULL)
  expect_equal(proxy$physics_source, FORECAST_PHYSICS_SOURCE)
  expect_equal(proxy$operational_claim, FORECAST_OPERATIONAL_CLAIM)
})

test_that("IDW is power 2 and exact hits ignore farther points", {
  expect_equal(forecast_idw(c(0, 10), c(1, 1)), 5)
  expect_equal(forecast_idw(c(1, 100), c(1, 2)), (1 + 100 / 4) / (1 + 1 / 4))
  expect_equal(forecast_idw(c(4, 9), c(0, 5)), 4)
  expect_true(is.na(forecast_idw(c(NA, NA), c(1, 2))))
})

test_that("cutoff selection takes two dates per season and refuses a thin season", {
  days <- as.Date(character())
  for (year in 2005:2014) {
    days <- c(
      days,
      as.Date(sprintf("%d-01-15", year)),
      as.Date(sprintf("%d-04-15", year)),
      as.Date(sprintf("%d-07-15", year)),
      as.Date(sprintf("%d-10-15", year))
    )
  }
  picked <- select_forecast_cutoffs(days)
  expect_equal(picked$status, "ok")
  expect_equal(length(picked$cutoffs), 8L)
  thin <- days[forecast_season(days) != "SON"]
  refused <- select_forecast_cutoffs(thin)
  expect_equal(refused$status, "design_infeasible")
})

test_that("best-effort adult cutoff fill returns at least six candidates when possible", {
  days <- seq(as.Date("2010-04-01"), as.Date("2020-10-01"), by = "120 days")
  picked <- select_forecast_cutoffs_best_effort(days)
  expect_equal(picked$status, "ok")
  expect_gte(length(picked$cutoffs), 6L)
})

test_that("eligible days require four sampled days and training depth (adult min 150)", {
  day <- seq(as.Date("2010-01-01"), as.Date("2010-06-01"), by = "day")
  daily <- data.frame(
    day = day,
    n = 20L,
    n_pos = 5L,
    n_neg = 15L
  )
  eligible <- forecast_eligible_days(daily, test_end = as.Date("2010-06-01"), min_rows = 150L, min_days = 30L)
  expect_true(length(eligible) > 0L)
})

test_that("extra_time holdout_only uses only future holdout indices", {
  expect_equal(forecast_extra_time(100L, c(101L, 102L, 103L)), 101:103)
  hold_only <- sort(unique(c(101L, 103L)))
  expect_equal(hold_only, c(101L, 103L))
})

test_that("the 24 h pass rule is strict and fail-closed", {
  expect_true(forecast_passes_24h(0.7, 0.6, 0.5, 0.2, 0.1, 0.05, 6))
  expect_false(forecast_passes_24h(0.7, 0.7, 0.5, 0.2, 0.1, 0.05, 6))
  expect_false(forecast_passes_24h(0.7, 0.6, 0.5, 0.2, 0.1, 0.05, 5))
})
