test_that("protocol thresholds load from YAML not hard-coded defaults in checks", {
  proto <- load_short_sample_protocol(
    file.path(FISHAI_ROOT, "configs", "sensitivity_short_samples.yaml")
  )
  expect_equal(proto$reduced_fit_min_duration_min, 10)
  expect_equal(proto$full_fit_min_duration_min, 2)
  expect_equal(proto$cv_eval_min_duration_min, 10)
  expect_equal(proto$cv_check$margin_se_fold_diff, 1)
  expect_equal(proto$coefficient_check$wald_confidence, 0.95)
  expect_equal(proto$revert_on_fail$duration_minutes, 10)
})

test_that("prereg_commit_sha resolves for prereg markdown", {
  sha <- prereg_commit_sha("docs/prereg/short_sample_refit.md")
  expect_true(nzchar(sha))
  expect_match(sha, "^[0-9a-f]{5,40}$")
})

test_that("prereg_commit_sha uses env when git checkout is unavailable", {
  old <- Sys.getenv("PREREG_COMMIT_SHA", unset = NA_character_)
  on.exit({
    if (is.na(old)) {
      Sys.unsetenv("PREREG_COMMIT_SHA")
    } else {
      Sys.setenv(PREREG_COMMIT_SHA = old)
    }
  }, add = TRUE)
  Sys.setenv(PREREG_COMMIT_SHA = "abc123def4567890abcd")
  nogit <- tempfile()
  dir.create(nogit)
  sha <- prereg_commit_sha("docs/prereg/short_sample_refit.md", repo_root = nogit)
  expect_equal(sha, "abc123def4567890abcd")
})

test_that("missing count row species framing excludes taxon without zero imputation", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  eid <- "CUFES:T:AK:mixed"
  writeLines(
    paste(
      "event_id,time,lat,lon,stop_time,stop_lat,stop_lon,volume_m3,pump_readings_used,duration_min,short_event",
      paste0(eid, ",2020-01-01T00:00:00Z,33,-119,2020-01-01T00:12:00Z,33.01,-118.99,100,1,12"),
      sep = "\n"
    ),
    ev
  )
  writeLines(paste0("event_id,taxon,count\n", eid, ",sardine,2"), ct)
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      paste0(eid, ",0,0,0,0,0,0,0,cmems_mod_glo_phy_my_0.083deg_P1D-m,FALSE"),
      sep = "\n"
    ),
    cov
  )
  mk_cfg <- function(taxon) {
    list(
      species = list(taxon = taxon),
      data = list(events_path = ev, counts_path = ct, covariates_path = cov, time_idx_origin = "2020-01-01"),
      covariates = list(
        dynamic = c("temp_3m", "sal_3m", "mld", "sst_grad", "dist_front", "upwelling"),
        static = "log_depth"
      ),
      response = list(column = "egg_count", effort_column = "volume_m3")
    )
  }
  sard <- load_model_data(cfg = mk_cfg("sardine"))
  expect_equal(sard$event_id, eid)
  expect_error(load_model_data(cfg = mk_cfg("hake")), "no events with a cufes_counts row")
})

test_that("check_cv_metric_pass aligns named folds and does not shift past a failed fold", {
  full <- c("1" = 0.5, "2" = NA_real_, "3" = 0.5)
  red <- c("3" = 0.5, "1" = 0.5, "2" = 0.9)
  res <- check_cv_metric_pass(full, red, margin_se = 1)
  expect_true(res$pass)
  expect_equal(res$fold_ids, c("1", "3"))
  shifted <- c("1" = 0.5, "2" = 0.5, "4" = 0.5)
  expect_false(check_cv_metric_pass(full, shifted, margin_se = 1)$pass)
})

test_that("check_cv_metric_pass uses margin from protocol scale", {
  margin <- 1.0
  full <- c(0.5, 0.6, 0.55)
  red <- c(0.52, 0.58, 0.54)
  expect_true(check_cv_metric_pass(full, red, margin_se = margin)$pass)
  bad_red <- c(0.9, 0.92, 0.91)
  expect_false(check_cv_metric_pass(full, bad_red, margin_se = margin)$pass)
})

test_that("run_short_sample_species returns structured pass_fail fields", {
  proto <- load_short_sample_protocol(
    file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "sensitivity_protocol_test.yaml")
  )
  cfg_sard <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml")
  )
  cfg_sard$model$formula_shared <- "~ 1"
  cfg_sard$model$spatial <- list("off", "off")
  cfg_sard$model$spatiotemporal <- list("off", "off")
  tmp_cfg <- tempfile(fileext = ".yaml")
  yaml::write_yaml(list(fishai_engine_config = cfg_sard), tmp_cfg)
  proto$species[[1]]$model_config <- tmp_cfg
  res <- run_short_sample_species(proto, proto$species[[1]])
  expect_true(is.logical(res$overall_pass))
  expect_true(is.logical(res$coefficient_pass))
  expect_true(is.finite(res$reference_volume_m3))
  expect_gt(res$reference_volume_n_events, 0L)
  expect_equal(res$n_events_reduced, 24L)
})
