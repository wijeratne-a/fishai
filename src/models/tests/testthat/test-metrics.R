test_that("metrics match toy definitions", {
  z <- c(1, 1, 0, 0)
  p <- c(0.9, 0.8, 0.2, 0.1)
  expect_equal(auc_mw(z, p), 1)
  expect_equal(tss_at(z, p, 0.5), 1)
  expect_equal(brier_score(z, p), mean((p - z)^2))
  samp <- c(0, 1, 2)
  expect_equal(crps_sample(1, samp), mean(abs(samp - 1)) - 0.5 * mean(abs(outer(samp, samp, "-"))))
})
