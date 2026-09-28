test_that("load_model_data rejects missing effort", {
  path <- file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "synthetic_cufes.csv")
  dat <- load_model_data(path, list(response = list(column = "egg_count", effort_column = "volume_m3")))
  expect_true(all(dat$volume_m3 > 0))
  expect_equal(nrow(dat), 48)
})

test_that("missing effort rows are refused", {
  td <- tempfile(fileext = ".csv")
  writeLines(
    "event_id,egg_count,volume_m3\nCUFES:T:AK:a,1,NA\nCUFES:T:AK:b,2,10",
    td
  )
  expect_error(load_model_data(td, list(response = list(column = "egg_count", effort_column = "volume_m3"))))
})

test_that("duplicate event_id is refused", {
  td <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,egg_count,volume_m3",
      "CUFES:T:AK:1,1,10",
      "CUFES:T:AK:1,2,10",
      sep = "\n"
    ),
    td
  )
  expect_error(
    load_model_data(td, list(response = list(column = "egg_count", effort_column = "volume_m3"))),
    "duplicate event_id"
  )
})

test_that("sample_id is accepted as event_id alias", {
  td <- tempfile(fileext = ".csv")
  writeLines(
    "sample_id,egg_count,volume_m3\nCUFES:T:AK:x,3,5",
    td
  )
  dat <- load_model_data(td, list(response = list(column = "egg_count", effort_column = "volume_m3")))
  expect_equal(dat$event_id, "CUFES:T:AK:x")
})

test_that("cufes_events and cufes_counts join on event_id", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      "event_id,volume_m3,temp_3m_z",
      "CUFES:2024:SH:1,100,0.1",
      "CUFES:2024:SH:2,200,0.2",
      sep = "\n"
    ),
    ev
  )
  writeLines(
    paste(
      "event_id,taxon,count",
      "CUFES:2024:SH:1,sardine,5",
      "CUFES:2024:SH:2,sardine,0",
      sep = "\n"
    ),
    ct
  )
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(events_path = ev, counts_path = ct),
    response = list(column = "egg_count", effort_column = "volume_m3")
  )
  dat <- load_model_data(cfg = cfg)
  expect_equal(nrow(dat), 2L)
  expect_equal(dat$event_id, c("CUFES:2024:SH:1", "CUFES:2024:SH:2"))
  expect_equal(dat$egg_count, c(5, 0))
})
