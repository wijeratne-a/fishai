test_that("harmonize config loads covariates and TODO-audit thresholds", {
  cfg <- load_harmonize_config(file.path(FISHAI_ROOT, "configs", "harmonize.yaml"))
  expect_equal(length(cfg$covariates), 6L)
  expect_null(cfg$skill_thresholds$temp_3m$min_correlation)
  expect_equal(cfg$nearshore_max_km, 20)
})

test_that("overlap train and holdout periods are disjoint by time", {
  cfg <- load_harmonize_config(file.path(FISHAI_ROOT, "configs", "harmonize.yaml"))
  pairs <- load_harmonize_pairs(cfg)
  split <- split_overlap_periods(pairs, cfg)
  expect_gt(max(split$train$.time_ord), 0)
  expect_true(all(split$train$.time_ord < min(split$holdout$.time_ord)))
})

test_that("diagnostics report offset, sd ratio, and correlation by stratum", {
  cfg <- load_harmonize_config(file.path(FISHAI_ROOT, "configs", "harmonize.yaml"))
  pairs <- load_harmonize_pairs(cfg)
  diag <- compute_harmonize_diagnostics(pairs, cfg)
  d <- diag$temp_3m
  expect_true(is.finite(d$overall$mean_offset))
  expect_true(is.finite(d$overall$correlation))
  expect_gt(d$nearshore$n, 0L)
  expect_gt(d$offshore$n, 0L)
})

test_that("quantile map does not extrapolate — high WCOFS is harmonize OOD level 3", {
  cfg <- load_harmonize_config(file.path(FISHAI_ROOT, "configs", "harmonize.yaml"))
  pairs <- load_harmonize_pairs(cfg)
  split <- split_overlap_periods(pairs, cfg)
  maps <- fit_season_quantile_maps(split$train, cfg)
  mp <- maps$temp_3m$DJF
  hi <- mp$wcofs_max + 5
  res <- apply_season_quantile_map(hi, mp)
  expect_true(is.na(res$glorys))
  expect_equal(res$harmonize_ood, 3L)
})

test_that("held-out scoring uses maps fit only on earlier overlap", {
  cfg <- load_harmonize_config(file.path(FISHAI_ROOT, "configs", "harmonize.yaml"))
  pairs <- load_harmonize_pairs(cfg)
  split <- split_overlap_periods(pairs, cfg)
  maps <- fit_season_quantile_maps(split$train, cfg)
  scores <- score_harmonization_maps(split$holdout, maps, cfg)
  expect_true(is.finite(scores$temp_3m$overall$correlation))
  sel <- drop_covariates_by_skill(scores, cfg)
  expect_length(sel$active_covariates, 6L)
})

test_that("frozen maps carry version and content hash", {
  cfg <- load_harmonize_config(file.path(FISHAI_ROOT, "configs", "harmonize.yaml"))
  maps_path <- tempfile(fileext = ".rds")
  gate <- run_harmonization_gate(
    file.path(FISHAI_ROOT, "configs", "harmonize.yaml"),
    path_override = maps_path
  )
  expect_true(file.exists(maps_path))
  expect_equal(gate$version, cfg$version)
  expect_true(nzchar(gate$content_hash))
})

test_that("predict refuses WCOFS inference without harmonization maps", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  cfg$prediction$inference_forcing_source_id <- "wcofs"
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  artifact$reference <- dat[, ref_cols, drop = FALSE]
  artifact$reference_cols <- ref_cols
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  expect_error(predict_engine(artifact, grid, cfg, nsim = 3), "harmonization maps")
})

test_that("predict applies harmonized WCOFS and envelope OOD on corrected grid", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  cfg$prediction$inference_forcing_source_id <- "wcofs"
  hcfg <- load_harmonize_config(file.path(FISHAI_ROOT, "configs", "harmonize.yaml"))
  maps_path <- tempfile(fileext = ".rds")
  run_harmonization_gate(hcfg$config_path, path_override = maps_path)
  cfg <- attach_harmonization_metadata(cfg, maps_path, hcfg$config_path)

  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  artifact$harmonization <- cfg$harmonization
  artifact$reference <- dat[, ref_cols, drop = FALSE]
  artifact$reference_cols <- ref_cols

  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  grid$season <- "JJA"
  frozen_maps <- readRDS(maps_path)
  for (def in hcfg$covariates) {
    mp <- frozen_maps$maps[[def$id]]$JJA
    mid <- (mp$wcofs_min + mp$wcofs_max) / 2
    grid[[paste0(def$wcofs_column, "_wcofs")]] <- mid
  }
  mp <- frozen_maps$maps$temp_3m$JJA
  grid$T3m_wcofs[1] <- mp$wcofs_max + 10

  hgrid <- harmonize_inference_grid(grid, frozen_maps, hcfg)
  expect_equal(hgrid$harmonize_ood[1], 3L)
  lvl <- harmonize_envelope_ood(hgrid, artifact$reference, ref_cols, cfg)
  expect_true(any(lvl == 3L))
})
