.production_freeze_fixture <- function(species = "sardine") {
  raw <- yaml::read_yaml(
    file.path(FISHAI_ROOT, "configs", "models", paste0("cufes_", species, ".yaml"))
  )
  cfg <- raw$fishai_engine_config
  cfg$data$fold_assignment_path <- NULL
  cfg$data$covariate_drops_path <- NULL
  cfg$data$covariate_drop_summary_path <- NULL
  cfg$data$event_count_guard <- NULL
  cfg$mesh$barrier$enabled <- FALSE
  cfg$mesh$cutoff_km <- 18
  cfg$model$spatial <- list("off", "off")
  cfg$model$spatiotemporal <- list("off", "off")
  cfg$model$share_range <- list(FALSE, FALSE)
  cfg$model$time_varying <- NULL
  cfg$prediction$hindcast_evidence <- TRUE

  n <- 240L
  ids <- sprintf("CUFES:P:AK:%03d", seq_len(n))
  set.seed(5)
  day <- as.Date("2015-06-01") + rep(0:3, length.out = n)
  ev <- data.frame(
    event_id = ids,
    time = paste0(format(day), "T12:00:00Z"),
    lat = 33 + stats::runif(n, -0.5, 0.5),
    lon = -119 + stats::runif(n, -0.5, 0.5),
    stop_time = paste0(format(day), "T12:08:00Z"),
    volume_m3 = stats::runif(n, 50, 150),
    pump_readings_used = 2L,
    duration_min = 8,
    short_event = FALSE,
    stringsAsFactors = FALSE
  )
  ev$stop_lat <- ev$lat + 0.01
  ev$stop_lon <- ev$lon + 0.01
  cov <- data.frame(
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
  ct <- data.frame(event_id = ids, taxon = "sardine", count = rep(c(0, 3, 1), length.out = n))
  paths <- vapply(c("ev", "ct", "cov"), function(x) tempfile(fileext = ".csv"), character(1))
  utils::write.csv(ev, paths[["ev"]], row.names = FALSE)
  utils::write.csv(ct, paths[["ct"]], row.names = FALSE)
  utils::write.csv(cov, paths[["cov"]], row.names = FALSE)
  cfg$species$taxon <- "sardine"
  cfg$data$events_path <- paths[["ev"]]
  cfg$data$counts_path <- paths[["ct"]]
  cfg$data$covariates_path <- paths[["cov"]]

  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_production_mesh(dat, cfg$mesh)
  fit <- suppressWarnings(fit_delta_engine(dat, mesh, cfg))
  artifact_path <- tempfile(fileext = ".rds")
  frozen <- freeze_model(fit, cfg, artifact_path, training_dat = dat)
  grid <- read.csv(file.path(FISHAI_ROOT, cfg$prediction$grid_table), stringsAsFactors = FALSE)
  grid$time_idx <- dat$time_idx[[1L]]
  list(cfg = cfg, dat = dat, frozen = frozen, artifact_path = artifact_path, grid = grid)
}

test_that("production-config freeze stores the OOD reference and predict needs no injection", {
  for (sp in c("sardine", "anchovy")) {
    fx <- .production_freeze_fixture(sp)
    artifact <- readRDS(fx$artifact_path)
    expected_cols <- .model_covariate_columns(fx$cfg)
    expect_null(fx$cfg$reference)
    expect_false("upwelling_z" %in% artifact$reference_cols)
    expect_equal(artifact$reference_cols, setdiff(expected_cols, "upwelling_z"))
    expect_equal(nrow(artifact$reference), nrow(fx$dat))
    expect_equal(
      as.matrix(artifact$reference),
      as.matrix(fx$dat[, artifact$reference_cols, drop = FALSE]),
      ignore_attr = TRUE
    )
    expect_equal(artifact$time_idx_origin, "1990-01-01")

    novel <- fx$grid
    for (col in artifact$reference_cols) {
      novel[[col]] <- max(fx$dat[[col]]) + 25 + seq_len(nrow(novel)) * 0.01
    }
    out <- predict_engine(
      artifact,
      novel,
      fx$cfg,
      nsim = 2L,
      species = sp,
      valid_day = "2015-06-01",
      dry_run = TRUE
    )
    expect_true(all(out$ood_level >= 2L))
    expect_true(all(out$evidence_state == "UNKNOWN"))
    expect_true(all(out$unknown_reason == "ood_level_ge_2"))
    expect_true(all(is.na(out$p_encounter) & is.na(out$p_lo90) & is.na(out$p_hi90)))
    expect_true(all(is.na(out$expected_density)))

    inside <- fx$grid
    for (col in artifact$reference_cols) {
      inside[[col]] <- stats::median(fx$dat[[col]])
    }
    ok <- predict_engine(
      artifact,
      inside,
      fx$cfg,
      nsim = 2L,
      species = sp,
      valid_day = "2015-06-01",
      dry_run = TRUE
    )
    expect_true(all(ok$ood_level < 2L))
    expect_false(any(ok$evidence_state == "UNKNOWN"))
    expect_true(all(is.finite(ok$p_encounter)))
  }
})

test_that("predict refuses an artifact without a frozen OOD reference", {
  fx <- .production_freeze_fixture("sardine")
  artifact <- readRDS(fx$artifact_path)
  artifact$reference <- NULL
  expect_error(
    predict_engine(artifact, fx$grid, fx$cfg, nsim = 2L, species = "sardine", valid_day = "2015-06-01"),
    "OOD reference"
  )
})
