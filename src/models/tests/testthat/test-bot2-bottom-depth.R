test_that("bot2 bottom_depth_m maps to log_depth_z for modeling", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header("time_idx"),
      cufes_event_row("CUFES:T:AK:d1", 10, time_idx = 1),
      sep = "\n"
    ),
    ev
  )
  writeLines(
    paste(
      "event_id,taxon,count",
      "CUFES:T:AK:d1,sardine,2",
      sep = "\n"
    ),
    ct
  )
  writeLines(
    paste(
      bot2_covariates_csv_header(),
      paste(
        c(
          "CUFES:T:AK:d1",
          0, 0, 0, 0, 0,
          "",
          "no_consistent_wind_product",
          200,
          "FALSE",
          "glorys",
          "SYNTHETIC",
          "FALSE",
          "cmems_mod_glo_phy_my_0.083deg_P1D-m",
          ""
        ),
        collapse = ","
      ),
      sep = "\n"
    ),
    cov
  )
  cfg <- list(
    species = list(taxon = "sardine"),
    training = list(covariate_forcing_source_id = "glorys"),
    data = list(events_path = ev, counts_path = ct, covariates_path = cov),
    covariates = list(
      dynamic = character(),
      static = "log_depth",
      upstream_fields = list(log_depth = "bottom_depth_m")
    ),
    response = list(column = "egg_count", effort_column = "volume_m3"),
    model = list(formula_shared = "~ 1", spatial = list("off", "off"), spatiotemporal = list("off", "off")),
    mesh = list(cutoff = 50, max_edge = c(80, 120), offset = c(20, 40), barrier = list(enabled = FALSE))
  )
  dat <- load_model_data(cfg = cfg, min_duration_min = 2L)
  expect_true("log_depth_z" %in% names(dat))
  expect_false(any(is.na(dat$log_depth_z)))
})
