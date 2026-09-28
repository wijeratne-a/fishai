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
  expect_equal(
    sort(as.integer(cv$fold_assignment$fold_id)),
    sort(as.integer(dat$fold_id))
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
