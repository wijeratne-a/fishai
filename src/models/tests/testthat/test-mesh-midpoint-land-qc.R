test_that("qc_drop_mesh_midpoint_on_barrier_land drops only midpoints inside the polygon", {
  dat <- data.frame(
    event_id = c("on-land", "at-sea"),
    X = c(10, 40),
    Y = c(10, 40),
    stringsAsFactors = FALSE
  )
  land <- sf::st_sf(
    geometry = sf::st_sfc(
      sf::st_polygon(list(rbind(
        c(0, 0), c(20000, 0), c(20000, 20000), c(0, 20000), c(0, 0)
      ))),
      crs = 32611
    )
  )
  out <- qc_drop_mesh_midpoint_on_barrier_land(dat, land)
  expect_equal(out$dropped_event_ids, "on-land")
  expect_equal(out$dat$event_id, "at-sea")
})

test_that("load_model_data applies the barrier-land midpoint rule", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  land_path <- tempfile(fileext = ".rds")
  writeLines(
    paste(
      cufes_events_csv_header(),
      "on-land,2020-01-01T00:00:00Z,33.70,-118.40,2020-01-01T01:00:00Z,33.80,-118.50,10,2,60,FALSE",
      "at-sea,2020-01-01T00:00:00Z,33.20,-119.20,2020-01-01T01:00:00Z,33.21,-119.21,10,2,60,FALSE",
      sep = "\n"
    ),
    ev
  )
  writeLines(
    paste(
      "event_id,taxon,count",
      "on-land,sardine,0",
      "at-sea,sardine,1",
      sep = "\n"
    ),
    ct
  )
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("on-land"),
      cufes_covariate_row("at-sea"),
      sep = "\n"
    ),
    cov
  )
  raw <- utils::read.csv(ev, stringsAsFactors = FALSE)
  mid <- .track_midpoint_km(raw$lon, raw$lat, raw$stop_lon, raw$stop_lat)
  land_row <- raw$event_id == "on-land"
  cx <- mid$X[land_row] * 1000
  cy <- mid$Y[land_row] * 1000
  land <- sf::st_sf(
    geometry = sf::st_sfc(
      sf::st_polygon(list(rbind(
        c(cx - 500, cy - 500),
        c(cx + 500, cy - 500),
        c(cx + 500, cy + 500),
        c(cx - 500, cy + 500),
        c(cx - 500, cy - 500)
      ))),
      crs = 32611
    )
  )
  saveRDS(land, land_path)
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(
      events_path = ev,
      counts_path = ct,
      covariates_path = cov,
      time_idx_origin = "1990-01-01"
    ),
    covariates = list(
      dynamic = c("temp_3m", "sal_3m", "mld", "sst_grad", "dist_front", "upwelling"),
      static = "log_depth",
      upstream_fields = list(
        temp_3m = "T3m",
        sal_3m = "S3m",
        mld = "MLD_m",
        sst_grad = "sst_grad",
        dist_front = "front_distance_km",
        upwelling = "upwelling",
        log_depth = "log_depth_z"
      )
    ),
    response = list(column = "egg_count", effort_column = "volume_m3"),
    mesh = list(
      barrier = list(enabled = TRUE, land_sf_rds = land_path)
    )
  )
  dat <- load_model_data(cfg = cfg)
  expect_equal(dat$event_id, "at-sea")
  expect_equal(
    attr(dat, "fishai_data_qc")$dropped_mesh_midpoint_on_barrier_land,
    "on-land"
  )
})

test_that("current kept training table drops only the two on-land midpoints", {
  root <- FISHAI_ROOT
  events_path <- file.path(root, "data", "processed", "calcofi_cufes", "cufes_events.parquet")
  cov_path <- file.path(root, "data", "processed", "calcofi_cufes", "cufes_training_covariates.parquet")
  land_path <- file.path(root, "data", "reference", "mesh", "scb_pilot_land_sf.rds")
  skip_if_not(
    file.exists(events_path) && file.exists(cov_path) && file.exists(land_path),
    "real training table or barrier land RDS is not in this environment"
  )
  skip_if_not(requireNamespace("arrow", quietly = TRUE), "arrow is required to read the training table")
  events <- .read_model_table(events_path)
  cov <- .read_model_table(cov_path)
  kept_ids <- as.character(cov$event_id)[!.parse_excluded_logical(cov$excluded) %in% TRUE]
  ev <- events[as.character(events$event_id) %in% kept_ids, , drop = FALSE]
  mid <- .track_midpoint_km(ev$lon, ev$lat, ev$stop_lon, ev$stop_lat)
  ev$X <- mid$X
  ev$Y <- mid$Y
  out <- qc_drop_mesh_midpoint_on_barrier_land(ev, readRDS(land_path))
  expect_setequal(
    out$dropped_event_ids,
    c("CUFES:201307:SH:97", "CUFES:201501:NH:160")
  )
})
