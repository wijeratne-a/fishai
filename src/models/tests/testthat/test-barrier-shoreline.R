FROZEN_PILOT_SHORELINE_SHA256 <- "2f677a16aa6c8470846d813eda6d82f2656dea2d697b1511a4c878542d20996c"

test_that("placeholder shoreline sha256 blocks verification", {
  dummy_path <- file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml")
  expect_error(
    verify_barrier_shoreline_sha256(dummy_path, BARRIER_SHORELINE_SHA256_PLACEHOLDER),
    "placeholder"
  )
  expect_true(barrier_shoreline_is_placeholder_sha256(""))
  expect_true(barrier_shoreline_is_placeholder_sha256(BARRIER_SHORELINE_SHA256_PLACEHOLDER))
  expect_false(barrier_shoreline_is_placeholder_sha256(FROZEN_PILOT_SHORELINE_SHA256))
})

test_that("model YAML pins PR #7 shoreline path and frozen hash", {
  cfg <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml")
  )
  sl <- cfg$mesh$barrier$shoreline
  expect_equal(basename(sl$path), "ne_10m_land_pilot_clip.json")
  expect_equal(tolower(trimws(sl$sha256)), FROZEN_PILOT_SHORELINE_SHA256)
})

test_that("verify_barrier_shoreline_sha256 fails on hash mismatch when file exists", {
  cfg_path <- file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml")
  expect_error(
    verify_barrier_shoreline_sha256(cfg_path, paste0("a", substr(FROZEN_PILOT_SHORELINE_SHA256, 2, 64))),
    "sha256 mismatch"
  )
})

test_that("build_fishai_mesh_with_barrier uses frozen PR #7 shoreline", {
  cfg <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml")
  )
  sl_path <- cfg$mesh$barrier$shoreline$path
  if (!file.exists(sl_path)) {
    skip(paste0(
      "frozen shoreline file missing (vendored on PR #7 branch only): ",
      sl_path
    ))
  }
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_mesh_with_barrier(dat, cfg)
  expect_true(mesh$mesh$n > 0)
})
