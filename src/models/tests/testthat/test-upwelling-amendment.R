.production_cfg <- function(species) {
  raw <- yaml::read_yaml(
    file.path(FISHAI_ROOT, "configs", "models", paste0("cufes_", species, ".yaml"))
  )
  raw$fishai_engine_config
}

.formula_vars <- function(cfg) {
  frm <- build_delta_formula(cfg$model$formula_shared)[[1]]
  setdiff(all.vars(frm), "y")
}

test_that("pilot production configs carry no upwelling covariate or formula term", {
  for (sp in c("sardine", "anchovy")) {
    cfg <- .production_cfg(sp)
    expect_false("upwelling" %in% c(cfg$covariates$dynamic, cfg$covariates$static))
    expect_false("upwelling" %in% names(cfg$covariates$upstream_fields))
    expect_false(grepl("upwelling", cfg$model$formula_shared, fixed = TRUE))
    expect_false("upwelling_z" %in% .formula_vars(cfg))
    expect_true(all(.formula_vars(cfg) %in% .model_covariate_columns(cfg)))
  }
})

test_that("all-null upwelling table loads and fits under the production model formula", {
  for (sp in c("sardine", "anchovy")) {
    cfg <- .production_cfg(sp)
    cfg$species$taxon <- "sardine"
    cfg$training <- NULL
    cfg$covariates$forcing_source_id <- NULL
    cfg$egg_split <- NULL
    cfg$data$fold_assignment_path <- NULL
    cfg$data$spatial_block_cv <- NULL
    cfg$data$covariate_drops_path <- NULL
    cfg$data$covariate_drop_summary_path <- NULL
    cfg$data$event_count_guard <- NULL
    cfg$mesh$barrier$enabled <- FALSE
    cfg$mesh$cutoff_km <- 18
    cfg$model$spatial <- list("off", "off")
    cfg$model$spatiotemporal <- list("off", "off")
    cfg$model$share_range <- list(FALSE, FALSE)
    cfg$model$time_varying <- NULL

    ev <- tempfile(fileext = ".csv")
    ct <- tempfile(fileext = ".csv")
    cov <- tempfile(fileext = ".csv")
    n <- 30L
    ids <- sprintf("CUFES:U:AK:%03d", seq_len(n))
    set.seed(3)
    ev_tab <- data.frame(
      event_id = ids,
      time = "2020-06-01T12:00:00Z",
      lat = 33 + stats::runif(n, -0.5, 0.5),
      lon = -119 + stats::runif(n, -0.5, 0.5),
      stop_time = "2020-06-01T12:08:00Z",
      volume_m3 = stats::runif(n, 50, 150),
      pump_readings_used = 2L,
      duration_min = 8,
      short_event = FALSE,
      time_idx = rep(1:3, length.out = n),
      stringsAsFactors = FALSE
    )
    ev_tab$stop_lat <- ev_tab$lat + 0.01
    ev_tab$stop_lon <- ev_tab$lon + 0.01
    utils::write.csv(ev_tab, ev, row.names = FALSE)
    utils::write.csv(
      data.frame(event_id = ids, taxon = "sardine", count = rep(c(0, 3, 1), length.out = n)),
      ct,
      row.names = FALSE
    )
    cov_tab <- data.frame(
      event_id = ids,
      T3m = stats::rnorm(n),
      S3m = stats::rnorm(n),
      MLD_m = stats::rnorm(n),
      sst_grad = stats::rnorm(n),
      front_distance_km = stats::rnorm(n),
      upwelling = NA_real_,
      upwelling_status = "no_consistent_wind_product",
      log_depth_z = stats::rnorm(n),
      source_product = "cmems_mod_glo_phy_my_0.083deg_P1D-m",
      excluded = FALSE,
      stringsAsFactors = FALSE
    )
    utils::write.csv(cov_tab, cov, row.names = FALSE)
    cfg$data$events_path <- ev
    cfg$data$counts_path <- ct
    cfg$data$covariates_path <- cov

    dat <- load_model_data(cfg = cfg)
    expect_equal(nrow(dat), n)
    expect_false("upwelling_z" %in% names(dat))
    expect_true(all(.formula_vars(cfg) %in% names(dat)))
    qc <- attr(dat, "fishai_data_qc")
    expect_length(qc$dropped_unavailable_covariates, 0L)

    mesh <- build_fishai_mesh(dat, cfg$mesh)
    fit <- suppressWarnings(fit_delta_engine(dat, mesh, cfg))
    expect_s3_class(fit, "fishai_fit")
  }
})
