test_that("preferential sampling diagnostic runs on synthetic data and writes JSON", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  cfg$mesh$barrier$enabled <- FALSE
  cfg$positive_model_fallback <- "encounter_only"
  cfg$diagnostics <- list(
    preferential_sampling = list(
      cell_size_km = 10,
      bootstrap_replicates = 100L
    )
  )
  dat <- load_model_data(cfg = cfg)
  res <- run_preferential_sampling_diagnostic(cfg, dat = dat)
  expect_equal(res$cell_size_km, 10)
  expect_equal(res$epsg, 32611L)
  expect_true(is.finite(res$spearman_rho) || is.na(res$spearman_rho))
  expect_length(res$bootstrap_ci_95, 2L)
  expect_type(res$flag_preferential, "logical")
  expect_gt(res$n_events, 10L)
  out <- tempfile(fileext = ".json")
  write_preferential_sampling_json(res, out)
  parsed <- jsonlite::fromJSON(out)
  expect_equal(parsed$species_taxon, "sardine")
  expect_true("flag_preferential" %in% names(parsed))
})

test_that("cruise and 10 km cell ids derive from event_id and UTM km", {
  expect_equal(cufes_cruise_from_event_id("CUFES:2204RS:AF:123"), "2204RS")
  expect_equal(ten_km_cell_id_utm(c(5, 15), c(8, 22), cell_size_km = 10), c("bx0_by0", "bx1_by2"))
})
