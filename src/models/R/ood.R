#' Multivariate similarity (MESS-style) scores.
#' @export
mess_scores <- function(pred, reference) {
  pred <- as.matrix(pred)
  reference <- as.matrix(reference)
  n_ref <- nrow(reference)
  mess <- numeric(nrow(pred))
  mod <- character(nrow(pred))
  for (i in seq_len(nrow(pred))) {
    x <- pred[i, ]
    s_j <- numeric(ncol(pred))
    for (j in seq_len(ncol(pred))) {
      r <- sort(reference[, j])
      mn <- r[1]
      mx <- r[n_ref]
      rng <- mx - mn
      if (rng <= 0) {
        s_j[j] <- 100
        next
      }
      f <- 100 * sum(reference[, j] < x[j]) / n_ref
      s_j[j] <- if (f == 0) {
        100 * (x[j] - mn) / rng
      } else if (f <= 50) {
        2 * f
      } else if (f < 100) {
        2 * (100 - f)
      } else {
        100 * (mx - x[j]) / rng
      }
    }
    mess[i] <- min(s_j)
    mod[i] <- colnames(pred)[which.min(s_j)]
  }
  data.frame(mess = mess, mod = mod, stringsAsFactors = FALSE)
}

#' ExDet NT1 / NT2 scores.
#' @export
exdet_scores <- function(pred, reference) {
  pred <- as.matrix(pred)
  reference <- as.matrix(reference)
  mn <- apply(reference, 2, min)
  mx <- apply(reference, 2, max)
  rng <- pmax(mx - mn, .Machine$double.eps)
  lo <- sweep(pred, 2, mn, "-")
  hi <- sweep(-pred, 2, -mx, "-")
  ud <- pmin(lo, hi, 0)
  ud <- sweep(ud, 2, rng, "/")
  nt1 <- rowSums(ud)
  mu <- colMeans(reference)
  S <- stats::cov(reference)
  d_pred <- sqrt(mahalanobis(pred, mu, S))
  d_ref <- sqrt(mahalanobis(reference, mu, S))
  nt2 <- d_pred / max(d_ref)
  nt2[nt1 < 0] <- NA_real_
  data.frame(nt1 = nt1, nt2 = nt2)
}

#' Mahalanobis distance for each prediction row.
#' @export
maha_distance <- function(pred, reference) {
  pred <- as.matrix(pred)
  reference <- as.matrix(reference)
  mu <- colMeans(reference)
  S <- stats::cov(reference)
  sqrt(mahalanobis(pred, mu, S))
}

#' Pairwise convex hull membership flags.
#' @export
convex_hull_flags <- function(pred, reference, pairs = list(c("sst_z", "sal_z"))) {
  flags <- rep(FALSE, nrow(pred))
  .inside <- function(x, y, poly_x, poly_y) {
    n <- length(poly_x)
    inside <- FALSE
    j <- n
    for (i in seq_len(n)) {
      if (((poly_y[i] > y) != (poly_y[j] > y)) &&
        (x < (poly_x[j] - poly_x[i]) * (y - poly_y[i]) / (poly_y[j] - poly_y[i] + 1e-12) + poly_x[i])) {
        inside <- !inside
      }
      j <- i
    }
    inside
  }
  for (pair in pairs) {
    if (!all(pair %in% colnames(pred))) {
      next
    }
    ref_ch <- grDevices::chull(reference[, pair[1]], reference[, pair[2]])
    ref_xy <- reference[ref_ch, pair, drop = FALSE]
    inside <- apply(pred, 1, function(row) {
      .inside(row[pair[1]], row[pair[2]], ref_xy[, 1], ref_xy[, 2])
    })
    flags <- flags | !inside
  }
  flags
}

#' Classify OOD level 0-3 per spec defaults.
#' @export
classify_ood_level <- function(mess, nt1, nt2, maha, hull_out, mess_mask_below = -20) {
  lvl <- rep(0L, length(mess))
  lvl[mess < 0 & mess >= mess_mask_below] <- 2L
  lvl[mess < mess_mask_below] <- 3L
  lvl[nt1 < 0] <- pmax(lvl[nt1 < 0], 2L)
  caution <- (nt2 > 1) | hull_out | (maha > stats::quantile(maha, 0.99, na.rm = TRUE))
  lvl[caution & lvl < 2L] <- 1L
  lvl
}
