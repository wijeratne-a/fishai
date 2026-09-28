test_that("event missing two covariates counts once in join-drop summary", {
  drops <- data.frame(
    event_id = rep("CUFES:T:AK:multi", 2),
    reason = rep("missing_covariate", 2),
    covariate = c("T3m", "S3m"),
    latitude = c(33, 33),
    longitude = c(-119, -119),
    stringsAsFactors = FALSE
  )
  eligible <- c("CUFES:T:AK:multi", "CUFES:T:AK:ok")
  pos <- "CUFES:T:AK:ok"
  rep <- summarize_covariate_join_drops(
    taxon_eligible_ids = eligible,
    taxon_positive_ids = pos,
    drops = drops
  )
  expect_equal(rep$n_join_dropped, 1L)
  expect_equal(rep$by_reason$missing_covariate$n_events, 1L)
})

test_that("event with two reasons counts once per reason and once in total", {
  drops <- data.frame(
    event_id = rep("CUFES:T:AK:both", 2),
    reason = c("missing_covariate", "land_mask"),
    covariate = c("T3m", NA),
    latitude = c(33, 33),
    longitude = c(-119, -119),
    stringsAsFactors = FALSE
  )
  eligible <- c("CUFES:T:AK:both", "CUFES:T:AK:ok")
  rep <- summarize_covariate_join_drops(
    taxon_eligible_ids = eligible,
    taxon_positive_ids = eligible,
    drops = drops
  )
  expect_equal(rep$n_join_dropped, 1L)
  expect_equal(rep$by_reason$missing_covariate$n_events, 1L)
  expect_equal(rep$by_reason$land_mask$n_events, 1L)
})

test_that("excluded flag inconsistent with drop table stops with error", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  drops <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header("time_idx"),
      cufes_event_row("CUFES:T:AK:a", 10, time_idx = 1),
      cufes_event_row("CUFES:T:AK:b", 10, time_idx = 2),
      sep = "\n"
    ),
    ev
  )
  writeLines(
    "event_id,taxon,count\nCUFES:T:AK:a,sardine,1\nCUFES:T:AK:b,sardine,1",
    ct
  )
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:T:AK:a", excluded = FALSE),
      cufes_covariate_row("CUFES:T:AK:b", excluded = TRUE),
      sep = "\n"
    ),
    cov
  )
  writeLines(
    paste(
      "event_id,reason,covariate,latitude,longitude",
      "CUFES:T:AK:a,missing_covariate,T3m,33,-119",
      sep = "\n"
    ),
    drops
  )
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(
      events_path = ev,
      counts_path = ct,
      covariates_path = cov,
      covariate_drops_path = drops
    ),
    covariates = list(
      dynamic = c("temp_3m", "sal_3m", "mld", "sst_grad", "dist_front", "upwelling"),
      static = "log_depth"
    ),
    response = list(column = "egg_count", effort_column = "volume_m3")
  )
  expect_error(load_model_data(cfg = cfg), "inconsistent with covariate drop table")
})

test_that("NaN covariate on non-excluded row stops with error", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header("time_idx"),
      cufes_event_row("CUFES:T:AK:ok", 10, time_idx = 1),
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:ok,sardine,1", ct)
  writeLines(
    paste(
      cufes_covariates_csv_header(),
      cufes_covariate_row("CUFES:T:AK:ok", values = c(NA, 0, 0, 0, 0, 0), bottom_depth_m = 20),
      sep = "\n"
    ),
    cov
  )
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(events_path = ev, counts_path = ct, covariates_path = cov),
    covariates = list(
      dynamic = c("temp_3m", "sal_3m", "mld", "sst_grad", "dist_front", "upwelling"),
      static = "log_depth"
    ),
    response = list(column = "egg_count", effort_column = "volume_m3")
  )
  expect_error(load_model_data(cfg = cfg), "never impute or silently drop")
})

test_that("covariate table without excluded column stops with error", {
  ev <- tempfile(fileext = ".csv")
  ct <- tempfile(fileext = ".csv")
  cov <- tempfile(fileext = ".csv")
  writeLines(
    paste(
      cufes_events_csv_header("time_idx"),
      cufes_event_row("CUFES:T:AK:ok", 10, time_idx = 1),
      sep = "\n"
    ),
    ev
  )
  writeLines("event_id,taxon,count\nCUFES:T:AK:ok,sardine,1", ct)
  writeLines(
    "event_id,T3m,S3m,MLD_m,sst_grad,front_distance_km,upwelling,bottom_depth_m,source_product,excluded_reason\nCUFES:T:AK:ok,0,0,0,0,0,0,20,cmems_mod_glo_phy_my_0.083deg_P1D-m,",
    cov
  )
  cfg <- list(
    species = list(taxon = "sardine"),
    data = list(events_path = ev, counts_path = ct, covariates_path = cov),
    covariates = list(dynamic = "temp_3m", static = character()),
    response = list(column = "egg_count", effort_column = "volume_m3")
  )
  expect_error(load_model_data(cfg = cfg), "missing excluded column")
})
