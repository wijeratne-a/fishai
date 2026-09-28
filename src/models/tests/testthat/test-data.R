test_that("load_model_data rejects missing effort", {
  path <- file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "synthetic_cufes.csv")
  dat <- load_model_data(path, list(response = list(column = "egg_count", effort_column = "volume_m3")))
  expect_true(all(dat$volume_m3 > 0))
  expect_equal(nrow(dat), 48)
})

test_that("missing effort rows are refused", {
  td <- tempfile(fileext = ".csv")
  writeLines(
    "sample_id,egg_count,volume_m3\na,1,NA\nb,2,10",
    td
  )
  expect_error(load_model_data(td, list(response = list(column = "egg_count", effort_column = "volume_m3"))))
})
