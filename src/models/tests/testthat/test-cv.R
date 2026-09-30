test_that("random CV folds are refused", {
  expect_error(run_cv_spatial(data.frame(), NULL, list(model = list()), NULL), "random")
})

test_that("spatial CV runs on synthetic folds", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  cv <- run_cv_spatial(dat, mesh, cfg, dat$fold_id)
  expect_equal(cv$n_failed_folds, 0L)
  expect_true(is.finite(cv$sum_loglik))
  expect_true(cv$elpd_eligible)
  expect_null(cv$elpd_ineligible_reason)
})

test_that("spatial CV records failed folds instead of crashing", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  cv <- run_cv_spatial(dat, mesh, cfg, dat$fold_id)
  expect_gt(cv$n_failed_folds, 0L)
  expect_true(is.na(cv$sum_loglik))
  expect_true(is.list(cv$fold_failures))
  expect_true(length(cv$fold_failures) >= 1L)
  expect_false(cv$elpd_eligible)
  expect_equal(cv$elpd_ineligible_reason, "cv_fold_nonconverged")
})

test_that("select_by_elpd ignores ineligible candidates with failed CV folds", {
  cfg_ok <- load_sardine_test_cfg(intercept_only = TRUE)
  dat_ok <- load_model_data(cfg = cfg_ok)
  mesh_ok <- build_fishai_mesh(dat_ok, cfg_ok$mesh)
  cv_ok <- run_cv_spatial(dat_ok, mesh_ok, cfg_ok, dat_ok$fold_id)

  cfg_bad <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  dat_bad <- load_model_data(cfg = cfg_bad)
  mesh_bad <- build_fishai_mesh(dat_bad, cfg_bad$mesh)
  cv_bad <- run_cv_spatial(dat_bad, mesh_bad, cfg_bad, dat_bad$fold_id)
  expect_false(cv_bad$elpd_eligible)

  sel <- select_by_elpd(list(ok = cv_ok, bad = cv_bad))
  expect_equal(as.character(sel), "ok")
})

test_that("select_by_elpd stops when every candidate is ineligible", {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml"))
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  cv <- run_cv_spatial(dat, mesh, cfg, dat$fold_id)
  expect_false(cv$elpd_eligible)
  expect_error(
    select_by_elpd(list(first = cv, second = cv)),
    "elpd_all_candidates_ineligible",
    fixed = TRUE
  )
})

test_that("spatial CV output includes fold table and block metadata", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  cv <- run_cv_spatial(dat, mesh, cfg, dat$fold_id)
  expect_true(all(c("fold_assignment", "spatial_block_cv") %in% names(cv)))
  expect_equal(nrow(cv$fold_assignment), nrow(dat))
  expect_equal(cv$fold_assignment$event_id, as.character(dat$event_id))
  expect_equal(cv$fold_assignment$fold_id, as.integer(dat$fold_id))
  expect_equal(cv$fold_assignment$block_id, as.character(dat$block_id))
  sel <- select_by_elpd(list(spatial = cv))
  expect_equal(as.character(sel), "spatial")
  expect_equal(
    attr(sel, "fold_assignment")[, c("event_id", "fold_id", "block_id")],
    cv$fold_assignment[, c("event_id", "fold_id", "block_id")]
  )
  expect_gte(cv$spatial_block_cv$block_size_km, cv$spatial_block_cv$spatial_range_km)
  expect_equal(cv$spatial_block_cv$block_size_km, max(cfg$mesh$cutoff_km, cfg$mesh$range_guess_km))
})

test_that("spatial CV shares identical folds across species on the same events", {
  ev_path <- tempfile(fileext = ".csv")
  on.exit(unlink(ev_path), add = TRUE)
  base_ev <- read.csv(
    file.path(FISHAI_ROOT, "src/models/tests/fixtures/synthetic_cufes_events.csv"),
    stringsAsFactors = FALSE
  )
  base_ev$fold_id <- NULL
  base_ev$block_id <- NULL
  utils::write.csv(base_ev, ev_path, row.names = FALSE)

  cfg_s <- load_sardine_test_cfg(intercept_only = TRUE)
  cfg_a <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "cufes_anchovy_synthetic.yaml")
  )
  cfg_a$model$formula_shared <- "~ 1"
  cfg_a$model$spatial <- list("off", "off")
  cfg_a$model$spatiotemporal <- list("off", "off")
  cfg_s$data$events_path <- ev_path
  cfg_a$data$events_path <- ev_path

  dat_s <- load_model_data(cfg = cfg_s, min_duration_min = 2)
  dat_a <- load_model_data(cfg = cfg_a, min_duration_min = 2)
  mesh_s <- build_fishai_mesh(dat_s, cfg_s$mesh)
  mesh_a <- build_fishai_mesh(dat_a, cfg_a$mesh)
  cv_s <- run_cv_spatial(dat_s, mesh_s, cfg_s, dat_s$fold_id)
  cv_a <- run_cv_spatial(dat_a, mesh_a, cfg_a, dat_a$fold_id)
  expect_identical(cv_s$fold_assignment, cv_a$fold_assignment)
})

.elpd_candidate <- function(sum_loglik, eligible = TRUE, reason = NULL, n_failed = 0L, fold_loglik = NULL, folds = NULL) {
  if (is.null(fold_loglik)) {
    fold_loglik <- c(-1, sum_loglik + 1)
  }
  if (is.null(folds)) {
    folds <- data.frame(
      event_id = c("e1", "e2"),
      fold_id = c(1L, 2L),
      block_id = c("bx0_by0", "bx1_by0"),
      stringsAsFactors = FALSE
    )
  }
  list(
    sum_loglik = sum_loglik,
    n_failed_folds = n_failed,
    fold_loglik = fold_loglik,
    elpd_eligible = eligible,
    elpd_ineligible_reason = reason,
    fold_assignment = folds
  )
}

test_that("select_by_elpd drops a failed run even when its sum_loglik is higher", {
  ok <- .elpd_candidate(-20, eligible = TRUE)
  bad <- .elpd_candidate(-1, eligible = FALSE, reason = "cv_fold_failed", n_failed = 1L, fold_loglik = c(-1, NA))
  sel <- select_by_elpd(list(bad = bad, ok = ok))
  expect_equal(as.character(sel), "ok")
})

test_that("select_by_elpd honors elpd_eligible FALSE when the stored sum is finite", {
  ok <- .elpd_candidate(-20, eligible = TRUE)
  sneaky <- .elpd_candidate(
    0,
    eligible = FALSE,
    reason = "cv_fold_failed",
    n_failed = 0L,
    fold_loglik = c(0, 0)
  )
  sel <- select_by_elpd(list(sneaky = sneaky, ok = ok))
  expect_equal(as.character(sel), "ok")
})

test_that("select_by_elpd does not rank a non-finite ELPD", {
  ok <- .elpd_candidate(-20, eligible = TRUE)
  na_cand <- .elpd_candidate(NA_real_, eligible = TRUE, n_failed = 0L, fold_loglik = c(NA_real_, -1))
  sel <- select_by_elpd(list(na = na_cand, ok = ok))
  expect_equal(as.character(sel), "ok")
  expect_error(
    select_by_elpd(list(only = na_cand)),
    "elpd_all_candidates_ineligible"
  )
})

test_that("select_by_elpd refuses eligible candidates scored on different folds", {
  ok <- .elpd_candidate(-20, eligible = TRUE)
  other <- .elpd_candidate(-10, eligible = TRUE)
  other$fold_assignment$fold_id <- c(2L, 1L)
  expect_error(
    select_by_elpd(list(a = ok, b = other)),
    "elpd_fold_assignment_mismatch",
    fixed = TRUE
  )
})

test_that("run_cv_spatial refuses fold ids that are not the assignment", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)
  bad <- as.integer(dat$fold_id)
  bad[1L] <- if (bad[1L] == 1L) 2L else 1L
  expect_error(
    run_cv_spatial(dat, NULL, cfg, bad),
    "fold_ids do not match the assigned fold_id",
    fixed = TRUE
  )
})

.capture_cv_fold_meshes <- function(cfg, dat) {
  mesh_dir <- tempfile("cv-fold-meshes-")
  dir.create(mesh_dir)
  real_fit <- get("fit_delta_engine", envir = globalenv())
  assign(
    "fit_delta_engine",
    function(dat, mesh, cfg) {
      saveRDS(mesh, tempfile(pattern = "mesh-", tmpdir = mesh_dir, fileext = ".rds"))
      real_fit(dat, mesh, cfg)
    },
    envir = globalenv()
  )
  on.exit(
    {
      assign("fit_delta_engine", real_fit, envir = globalenv())
      unlink(mesh_dir, recursive = TRUE)
    },
    add = TRUE
  )
  cv <- run_cv_spatial(dat, NULL, cfg, dat$fold_id)
  files <- list.files(mesh_dir, pattern = "\\.rds$", full.names = TRUE)
  list(cv = cv, meshes = lapply(files, readRDS))
}

test_that("spatial CV worker count is min(cores, 4) and not above the fold count", {
  expect_equal(.cv_spatial_n_workers(4L, cores = 8L), 4L)
  expect_equal(.cv_spatial_n_workers(4L, cores = 2L), 2L)
  expect_equal(.cv_spatial_n_workers(1L, cores = 8L), 1L)
  expect_equal(.cv_spatial_n_workers(3L, cores = NA_integer_), 1L)
})

test_that("spatial CV fold meshes use the production Bakka barrier and range", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  expect_true(isTRUE(cfg$mesh$barrier$enabled))
  dat <- load_model_data(cfg = cfg)
  res <- .capture_cv_fold_meshes(cfg, dat)
  expect_gt(length(res$meshes), 0L)
  for (m in res$meshes) {
    expect_gt(length(m$barrier_triangles), 0L)
    expect_equal(m$barrier_scaling[2], cfg$mesh$barrier$range_fraction)
  }
  prod_mesh <- build_fishai_production_mesh(dat, cfg$mesh)
  expect_gt(length(prod_mesh$barrier_triangles), 0L)
  expect_equal(prod_mesh$barrier_scaling, res$meshes[[1L]]$barrier_scaling)
})

test_that("spatial CV with the barrier disabled keeps plain fold meshes", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  cfg$mesh$barrier$enabled <- FALSE
  cfg$mesh$barrier$land_sf_rds <- file.path(tempdir(), "does-not-exist.rds")
  dat <- load_model_data(cfg = cfg)
  res <- .capture_cv_fold_meshes(cfg, dat)
  expect_gt(length(res$meshes), 0L)
  for (m in res$meshes) {
    expect_null(m$barrier_triangles)
  }
  expect_equal(res$cv$n_failed_folds, 0L)
})

test_that("spatial CV with the barrier enabled fails closed on unusable land input", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)

  cfg_missing <- cfg
  cfg_missing$mesh$barrier$land_sf_rds <- file.path(tempdir(), "missing-land.rds")
  expect_error(run_cv_spatial(dat, NULL, cfg_missing, dat$fold_id), "land_sf_rds not found")

  cfg_unset <- cfg
  cfg_unset$mesh$barrier$land_sf_rds <- NULL
  expect_error(run_cv_spatial(dat, NULL, cfg_unset, dat$fold_id), "land_sf_rds")

  bad_rds <- tempfile(fileext = ".rds")
  saveRDS(list(not = "sf"), bad_rds)
  cfg_bad <- cfg
  cfg_bad$mesh$barrier$land_sf_rds <- bad_rds
  expect_error(run_cv_spatial(dat, NULL, cfg_bad, dat$fold_id), "sf land polygon")
})

test_that("spatial CV with the barrier enabled fails closed on empty barrier triangles", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)
  far <- sf::st_sf(
    geometry = sf::st_sfc(
      sf::st_polygon(list(rbind(
        c(9e6, 9e6),
        c(9.1e6, 9e6),
        c(9.1e6, 9.1e6),
        c(9e6, 9.1e6),
        c(9e6, 9e6)
      ))),
      crs = 32611
    )
  )
  far_rds <- tempfile(fileext = ".rds")
  saveRDS(far, far_rds)
  cfg$mesh$barrier$land_sf_rds <- far_rds
  expect_error(run_cv_spatial(dat, NULL, cfg, dat$fold_id), "barrier")
})
