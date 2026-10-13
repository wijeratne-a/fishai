test_that("compute_solar_elevation returns day/night at noon and midnight UTC", {
  t_noon <- as.POSIXct("2020-06-21 20:00:00", tz = "UTC")
  sol <- compute_solar_elevation(t_noon, lat_deg = 33.5, lon_deg = -120)
  expect_true(sol$solar_elevation_deg > 0)
  expect_true(sol$is_day)
  expect_false(sol$is_night)

  t_night <- as.POSIXct("2020-06-21 08:00:00", tz = "UTC")
  sol_n <- compute_solar_elevation(t_night, lat_deg = 33.5, lon_deg = -120)
  expect_true(sol_n$solar_elevation_deg <= 0)
  expect_true(sol_n$is_night)
})

test_that("catchability_detection attaches z-scored solar columns", {
  cfg <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "jack_mackerel_encounter_catchability_delta.yaml")
  )
  dat <- data.frame(
    time = as.POSIXct(c("2020-07-01 18:00:00"), tz = "UTC"),
    lat = 33.5,
    lon = -120,
    stringsAsFactors = FALSE
  )
  out <- .attach_catchability_detection_terms(dat, cfg)
  expect_true(all(c("solar_elevation_deg", "solar_elev_z", "is_day", "is_dawn_dusk") %in% names(out)))
})
