# Retired estimator: 10 equal-width bins, half-open on the right. A strictly
# increasing predicted/expected curve on those bins has Spearman 1 even when
# the moving window still sees local drops.
fixed_bin_boyce <- function(p_avail, p_pres, n_bins = 10L) {
  edges <- seq(min(p_avail), max(p_avail), length.out = n_bins + 1L)
  fi <- numeric(n_bins)
  n_avail <- length(p_avail)
  n_pres <- length(p_pres)
  for (i in seq_len(n_bins)) {
    lo <- edges[[i]]
    hi <- edges[[i + 1L]]
    in_bin <- if (i < n_bins) {
      p_avail >= lo & p_avail < hi
    } else {
      p_avail >= lo & p_avail <= hi
    }
    in_pres <- if (i < n_bins) {
      p_pres >= lo & p_pres < hi
    } else {
      p_pres >= lo & p_pres <= hi
    }
    fi[[i]] <- (sum(in_pres) / n_pres) / (sum(in_bin) / n_avail)
  }
  stats::cor(fi, seq_len(n_bins), method = "spearman")
}

test_that("continuous Boyce uses a moving window and keeps the maximum", {
  # Presences sit only in the upper tail, so the window ratio rises throughout.
  p_tail <- seq(0, 1, length.out = 400)
  z_tail <- as.integer(p_tail >= 0.75)
  b_tail <- cbi_continuous(p_tail, p_tail[z_tail == 1L])
  expect_true(is.finite(b_tail))
  expect_gt(b_tail, 0.9)

  # Reversed ranking is negative.
  p <- c(seq(0.05, 0.9, length.out = 40), 1)
  z_rev <- c(rep(1L, 20), rep(0L, 21))
  expect_lt(cbi_continuous(p, p[z_rev == 1L]), 0)

  # A flat suitability has no Boyce.
  expect_true(is.na(cbi_continuous(rep(0.4, 10), rep(0.4, 4))))

  # Presences packed on the low side of each bin: 10-bin Spearman saturates
  # at 1 while the moving window stays below that ceiling.
  p_bins <- seq(0.001, 0.999, length.out = 200)
  z_bins <- rep(0L, 200)
  for (b in 0:9) {
    idx <- (b * 20L + 1L):((b + 1L) * 20L)
    z_bins[idx[seq_len(b + 1L)]] <- 1L
  }
  expect_equal(fixed_bin_boyce(p_bins, p_bins[z_bins == 1L]), 1)
  expect_lt(cbi_continuous(p_bins, p_bins[z_bins == 1L]), 1)
})

test_that("metrics match toy definitions", {
  z <- c(1, 1, 0, 0)
  p <- c(0.9, 0.8, 0.2, 0.1)
  expect_equal(auc_mw(z, p), 1)
  expect_equal(tss_at(z, p, 0.5), 1)
  expect_equal(brier_score(z, p), mean((p - z)^2))
  samp <- c(0, 1, 2)
  expect_equal(crps_sample(1, samp), mean(abs(samp - 1)) - 0.5 * mean(abs(outer(samp, samp, "-"))))
})
