test_that("source_product matches glorys_product_for_date on load", {
  cfg <- load_sardine_test_cfg()
  dat <- load_model_data(cfg = cfg, min_duration_min = 2)
  expect_gt(nrow(dat), 0L)
})

test_that("load_model_data rejects source_product disagreeing with glorys_product_for_date", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  on.exit(unlink(c(ev, ct, cov)), add = TRUE)
  eid <- "CUFES:T:AK:badprod"
  writeLines(
    paste(
      cufes_events_csv_header("fold_id"),
      paste0(eid, ",2021-07-01T00:00:00Z,33,-119,2021-07-01T00:08:00Z,33.01,-118.99,100,1,12,FALSE,1"),
      sep = "\n"
    ),
    ev
  )
  writeLines(paste0("event_id,taxon,count\n", eid, ",sardine,1"), ct)
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      paste(
        eid,
        paste(
          c(rep(0, 7), "cmems_mod_glo_phy_my_0.083deg_P1D-m", "FALSE"),
          collapse = ","
        ),
        sep = ","
      ),
      sep = "\n"
    ),
    cov
  )
  cfg <- load_sardine_test_cfg()
  cfg$data$events_path <- ev
  cfg$data$counts_path <- ct
  cfg$data$covariates_path <- cov
  drops_path <- tempfile(fileext = ".csv")
  writeLines("event_id,reason,covariate,latitude,longitude", drops_path)
  cfg$data$covariate_drops_path <- drops_path
  cfg$data$covariate_drop_summary_path <- NULL
  expect_error(
    load_model_data(cfg = cfg),
    "source_product mismatch"
  )
})
