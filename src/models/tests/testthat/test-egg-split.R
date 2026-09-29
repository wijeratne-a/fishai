test_that("egg_split dates are read from config", {
  cfg <- list(
    egg_split = list(
      fit_end = "2017-12-31",
      test_start = "2018-01-01",
      test_end = "2022-04-27",
      glorys_product_boundary = "2021-06-30",
      test_score_include_post_boundary = TRUE
    )
  )
  es <- parse_egg_split(cfg)
  expect_equal(as.character(es$fit_end), "2017-12-31")
  expect_equal(as.character(es$test_end), "2022-04-27")
})

test_that("test score flag drops post-boundary events when disabled", {
  cfg <- load_sardine_test_cfg()
  cfg$egg_split <- list(
    fit_end = "2017-12-31",
    test_start = "2018-01-01",
    test_end = "2022-04-27",
    glorys_product_boundary = "2021-06-30",
    test_score_include_post_boundary = FALSE
  )
  dat <- data.frame(
    time = c("2021-06-01T00:00:00Z", "2021-07-01T00:00:00Z"),
    stringsAsFactors = FALSE
  )
  out <- filter_egg_test_period_scores(dat, cfg, include_post_boundary = FALSE)
  expect_equal(nrow(out), 1L)
  out2 <- filter_egg_test_period_scores(dat, cfg, include_post_boundary = TRUE)
  expect_equal(nrow(out2), 2L)
})
