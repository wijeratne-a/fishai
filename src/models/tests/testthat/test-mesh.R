test_that("mesh cutoff enforces 9 km minimum", {
  path <- file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "synthetic_cufes.csv")
  dat <- load_model_data(path, list(response = list(column = "egg_count", effort_column = "volume_m3")))
  expect_error(build_fishai_mesh(dat, list(cutoff_km = 5)), "cutoff")
  mesh <- build_fishai_mesh(dat, list(cutoff_km = 9))
  expect_true(mesh$mesh$n > 0)
})

test_that("barrier reduces cross-land correlation proxy", {
  suppressPackageStartupMessages(require(sf))
  dat <- data.frame(X = c(10, 40), Y = c(20, 20))
  mesh <- build_fishai_mesh(dat, list(cutoff_km = 9))
  land <- sf::st_sf(
    geometry = sf::st_sfc(
      sf::st_polygon(
        list(
          rbind(
            c(15000, 15000),
            c(25000, 15000),
            c(25000, 25000),
            c(15000, 25000),
            c(15000, 15000)
          )
        )
      ),
      crs = 32610
    )
  )
  bmesh <- add_barrier_land(mesh, land, range_fraction = 0.1)
  check_barrier(bmesh, data.frame(X = 40, Y = 20), land_sf = land)
  ratio <- barrier_correlation_ratio(
    bmesh,
    pt_a = c(10, 20),
    pt_b_land = c(15, 20),
    pt_b_water = c(5, 20)
  )
  expect_lt(ratio, 1)
})
