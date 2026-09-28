test_that("OOD levels follow MESS thresholds", {
  ref <- data.frame(sst_z = c(-1, 0, 1), sal_z = c(-1, 0, 1))
  pred <- data.frame(sst_z = c(2), sal_z = c(0))
  mess <- mess_scores(pred, ref)
  expect_lt(mess$mess[1], 100)
  lvl <- classify_ood_level(mess$mess, nt1 = 0, nt2 = 0.5, maha = 0, hull_out = FALSE)
  expect_type(lvl, "integer")
})
