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

test_that("IDW is power 2 and exact hits ignore farther points", {
  expect_equal(forecast_idw(c(0, 10), c(1, 1)), 5)
  expect_equal(forecast_idw(c(1, 100), c(1, 2)), (1 + 100 / 4) / (1 + 1 / 4))
  expect_equal(forecast_idw(c(4, 9), c(0, 5)), 4)
  expect_true(is.na(forecast_idw(c(NA, NA), c(1, 2))))
})

test_that("local means widen the day-of-year window and refuse short support", {
  values <- rep(1, 20)
  dist <- rep(10, 20)
  doy <- rep(10, 20)
  expect_equal(forecast_local_mean(values, dist, doy), 1)
  expect_true(is.na(forecast_local_mean(values[1:19], dist[1:19], doy[1:19])))
  far_doy <- c(rep(10, 19), 40)
  expect_true(is.na(forecast_local_mean(c(values[1:19], 5), dist, far_doy, windows = 15L)))
  expect_equal(
    forecast_local_mean(c(values[1:19], 5), dist, far_doy, windows = c(15L, 45L)),
    mean(c(values[1:19], 5))
  )
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
  expect_equal(sort(unique(picked$seasons)), c("DJF", "JJA", "MAM", "SON"))
  expect_true(all(diff(as.integer(picked$cutoffs)) >= 30L))
  expect_equal(min(picked$cutoffs[picked$seasons == "DJF"]), as.Date("2005-01-15"))
  expect_equal(max(picked$cutoffs[picked$seasons == "DJF"]), as.Date("2014-01-15"))

  thin <- days[forecast_season(days) != "SON"]
  refused <- select_forecast_cutoffs(thin)
  expect_equal(refused$status, "design_infeasible")
})

test_that("eligible days require four sampled days and a large training set", {
  day <- seq(as.Date("2010-01-01"), as.Date("2010-06-01"), by = "day")
  daily <- data.frame(
    day = day,
    n = 20L,
    n_pos = 5L,
    n_neg = 15L
  )
  eligible <- forecast_eligible_days(daily, test_end = as.Date("2010-06-01"), min_rows = 2000L, min_days = 30L)
  expect_true(length(eligible) > 0L)
  expect_true(all(eligible + 3 <= as.Date("2010-06-01")))
  expect_true(all(vapply(eligible, function(d) sum(daily$n[daily$day <= d]) >= 2000, logical(1))))
  short <- forecast_eligible_days(daily, test_end = as.Date("2010-06-01"), min_rows = 100000L)
  expect_equal(length(short), 0L)
})

test_that("extra_time is the integers after the last training index through D+3", {
  expect_equal(forecast_extra_time(100L, c(101L, 102L, 103L)), 101:103)
  expect_equal(forecast_extra_time(90L, c(101L, 103L)), 91:103)
  expect_error(forecast_extra_time(103L, 103L), "strictly after")
})

test_that("the 24 h pass rule is strict and fail-closed", {
  expect_true(forecast_passes_24h(0.7, 0.6, 0.5, 0.2, 0.1, 0.05, 6))
  expect_false(forecast_passes_24h(0.7, 0.7, 0.5, 0.2, 0.1, 0.05, 6))
  expect_false(forecast_passes_24h(0.7, 0.6, 0.5, 0.2, 0.1, 0.05, 5))
  expect_false(forecast_passes_24h(NA, 0.6, 0.5, 0.2, 0.1, 0.05, 8))
})

test_that("pooled metrics keep the operational proxy labeled NOT_ISSUED_FORECAST", {
  rows <- data.frame(
    horizon_hours = rep(c(24L, 48L, 72L), each = 6L),
    z = rep(c(1L, 1L, 0L, 0L, 1L, 0L), 3L),
    p_oracle = rep(c(0.9, 0.8, 0.2, 0.1, 0.7, 0.3), 3L),
    p_operational_proxy = rep(c(0.6, 0.55, 0.4, 0.45, 0.5, 0.35), 3L),
    p_persistence = rep(c(0.8, 0.7, 0.2, 0.25, 0.75, 0.3), 3L),
    p_climatology = rep(c(0.4, 0.42, 0.38, 0.41, 0.39, 0.4), 3L),
    ll_oracle = rep(-0.2, 18L),
    ll_operational_proxy = rep(-0.4, 18L),
    ll_persistence = rep(-0.3, 18L),
    ll_climatology = rep(-0.7, 18L),
    in_common_support = TRUE
  )
  pooled <- forecast_pool_metrics(rows)
  expect_equal(pooled[["24"]]$operational_proxy$operational_claim, "NOT_ISSUED_FORECAST")
  expect_equal(pooled[["48"]]$operational_proxy$physics_source, "damped_anomaly_proxy")
  expect_equal(pooled[["72"]]$degradation_from_24h$operational_proxy$operational_claim, "NOT_ISSUED_FORECAST")
  expect_true(pooled[["24"]]$climatology$elpd_not_ranked_against_delta)
  expect_false(is.null(pooled[["24"]]$oracle$elpd))
  text <- forecast_business_readout(list(list(
    label = "sardine",
    n_eligible_cutoffs = 8L,
    pass_24h = FALSE,
    pooled = pooled
  )))
  expect_true(grepl("NOT_ISSUED_FORECAST", text, fixed = TRUE))
  expect_true(grepl("does not beat both baselines", text, fixed = TRUE))
  expect_false(grepl("adult fish are now", text, fixed = TRUE))
})
