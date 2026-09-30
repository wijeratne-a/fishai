test_that("real-table spatial-block CV reports blockers without fabricating scores", {
  cfg <- load_sardine_test_cfg()
  cfg$data$events_path <- "data/processed/calcofi_cufes/cufes_events.parquet"
  cfg$data$counts_path <- "data/processed/calcofi_cufes/cufes_counts.parquet"
  cfg$data$covariates_path <- "data/processed/calcofi_cufes/cufes_training_covariates.parquet"
  missing <- missing_real_table_cv_inputs(cfg)
  skip_if_not(length(missing) > 0L, "real training table present in this environment")
  scores <- compute_spatial_block_cv_scores(cfg)
  expect_equal(scores$status, "blocked")
  expect_length(scores$missing_inputs, length(missing))
  expect_false(isTRUE(scores$elpd_eligible))
  expect_true(is.na(scores$elpd))
  expect_true(is.na(scores$boyce))
  expect_true(is.na(scores$auc))
  expect_true(is.na(scores$tss))
})

test_that("run_spatial_block_cv_scores writes blocked JSON when inputs are absent", {
  proto <- tempfile(fileext = ".yaml")
  out_json <- tempfile(fileext = ".json")
  fold_csv <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "spatial_block_cv_scores:",
      "  wcofs_h_artifact: data/derived/physics/wcofs_h_glorys_pilot.zarr",
      "  min_duration_min: 2",
      "  species:",
      "    - label: sardine",
      "      model_config: configs/models/cufes_sardine.yaml",
      "  output:",
      paste0("    scores_json: ", out_json),
      paste0("    fold_assignment_csv: ", fold_csv),
      sep = "\n"
    ),
    proto
  )
  report <- run_spatial_block_cv_scores(proto)
  expect_equal(report$status, "blocked")
  expect_true(file.exists(out_json))
  parsed <- jsonlite::read_json(out_json)
  expect_equal(parsed$status, "blocked")
  expect_true(length(parsed$missing_inputs) >= 1L)
})
