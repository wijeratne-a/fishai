test_that("solar local hour shifts with longitude", {
  tt <- as.POSIXct("2020-07-01 12:00:00", tz = "UTC")
  utc_h <- .utc_decimal_hour(tt)
  expect_equal(utc_h, 12)
  local <- .solar_local_decimal_hour(tt, -120)
  expect_equal(local, 4, tolerance = 1e-6)
})

test_that("DVM terms attach when enabled", {
  cfg <- list(
    model = list(
      diel_vertical_migration = list(enabled = TRUE, time_reference = "utc")
    )
  )
  dat <- data.frame(
    time = as.POSIXct(c("2020-01-01 06:00:00", "2020-01-01 18:00:00"), tz = "UTC"),
    lon = c(-120, -120),
    stringsAsFactors = FALSE
  )
  out <- .attach_diel_vertical_migration_terms(dat, cfg)
  expect_true(all(c("tod_sin", "tod_cos") %in% names(out)))
  expect_equal(out$tod_sin[1], sin(2 * pi * 6 / 24), tolerance = 1e-8)
})
