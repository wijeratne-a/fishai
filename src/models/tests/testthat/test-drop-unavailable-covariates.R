bot2_covariates_csv_header <- function() {
  paste(
    c(
      "event_id",
      "T3m",
      "S3m",
      "MLD_m",
      "sst_grad",
      "front_distance_km",
      "upwelling",
      "upwelling_status",
      "bottom_depth_m",
      "depth_at_model_floor",
      "source",
      "provenance",
      "excluded",
      "source_product",
      "excluded_reason"
    ),
    collapse = ","
  )
}

bot2_covariate_row <- function(
  event_id,
  excluded = FALSE,
  upwelling = "",
  upwelling_status = "no_consistent_wind_product",
  source_product = "cmems_mod_glo_phy_my_0.083deg_P1D-m",
  bottom_depth_m = 120
) {
  paste(
    c(
      event_id,
      0,
      0,
      0,
      0,
      0,
      upwelling,
      upwelling_status,
      bottom_depth_m,
      "FALSE",
      "glorys",
      "SYNTHETIC_expected_contract",
      if (isTRUE(excluded)) "TRUE" else "FALSE",
      source_product,
      ""
    ),
    collapse = ","
  )
}

test_that("planned blank upwelling drops covariate and fit still runs", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header("time_idx"),
      cufes_event_row("CUFES:T:AK:u1", 10, time_idx = 1),
      cufes_event_row("CUFES:T:AK:u2", 12, time_idx = 2),
      sep = "\n"
    ),
    ev
  )
  writeLines(
    paste(
      "event_id,taxon,count",
      "CUFES:T:AK:u1,sardine,1",
      "CUFES:T:AK:u2,sardine,0",
      sep = "\n"
    ),
    ct
  )
  writeLines(
    paste(
      bot2_covariates_csv_header(),
      bot2_covariate_row("CUFES:T:AK:u1"),
      bot2_covariate_row("CUFES:T:AK:u2"),
      sep = "\n"
    ),
    cov
  )
  cfg <- list(
    species = list(taxon = "sardine"),
    training = list(covariate_forcing_source_id = "glorys"),
    data = list(events_path = ev, counts_path = ct, covariates_path = cov),
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
        log_depth = "bottom_depth_m"
      )
    ),
    response = list(column = "egg_count", effort_column = "volume_m3"),
    model = list(
      formula_shared = "~ 1",
      spatial = list("off", "off"),
      spatiotemporal = list("off", "off")
    ),
    mesh = list(
      cutoff = 50,
      max_edge = c(80, 120),
      offset = c(20, 40),
      barrier = list(enabled = FALSE)
    )
  )
  dat <- load_model_data(cfg = cfg, min_duration_min = 2L)
  qc <- attr(dat, "fishai_data_qc")
  expect_equal(qc$dropped_unavailable_covariates, "upwelling")
  expect_false("upwelling_z" %in% names(dat))
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  cfg$covariates$dynamic <- setdiff(cfg$covariates$dynamic, "upwelling")
  expect_no_error(suppressWarnings(fit_delta_engine(dat, mesh, cfg)))
})
