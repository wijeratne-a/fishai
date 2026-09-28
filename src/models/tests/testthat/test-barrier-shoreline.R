test_that("placeholder shoreline sha256 blocks verification", {
  dummy_path <- file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml")
  expect_error(
    verify_barrier_shoreline_sha256(dummy_path, BARRIER_SHORELINE_SHA256_PLACEHOLDER),
    "placeholder"
  )
  expect_true(barrier_shoreline_is_placeholder_sha256(""))
  expect_true(barrier_shoreline_is_placeholder_sha256(BARRIER_SHORELINE_SHA256_PLACEHOLDER))
  expect_false(barrier_shoreline_is_placeholder_sha256("deadbeef"))
})

test_that("model YAML pins PR #7 shoreline path with placeholder hash", {
  cfg <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml")
  )
  sl <- cfg$mesh$barrier$shoreline
  expect_equal(
    basename(sl$path),
    "ne_10m_land_pilot_clip.json"
  )
  expect_true(barrier_shoreline_is_placeholder_sha256(sl$sha256))
})

test_that("build_fishai_mesh_with_barrier respects pinned shoreline hash", {
  cfg <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml")
  )
  dat <- load_model_data(cfg = cfg)
  if (barrier_shoreline_is_placeholder_sha256(cfg$mesh$barrier$shoreline$sha256)) {
    expect_error(build_fishai_mesh_with_barrier(dat, cfg), "placeholder")
  } else {
    mesh <- build_fishai_mesh_with_barrier(dat, cfg)
    expect_true(mesh$mesh$n > 0)
  }
})
