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

#' Fail closed unless the frozen OOD reference supports a Mahalanobis calibration.
#'
#' Requires finite numeric columns with non-zero variance, full column rank after
#' centering (no collinear columns), strictly more rows than columns + 1 (so the
#' covariance can have full rank), a positive-definite well-conditioned
#' covariance, and finite reference distances.
#' @export
assert_usable_ood_reference <- function(reference, cols = NULL, min_rcond = 1e-10) {
  fail <- function(...) stop("unusable OOD reference: ", ..., call. = FALSE)
  if (is.null(reference)) {
    fail("reference is missing")
  }
  cols <- cols %||% colnames(reference)
  if (!length(cols) || anyNA(cols) || anyDuplicated(cols) || !all(cols %in% colnames(reference))) {
    fail("reference columns are missing or duplicated")
  }
  ref_df <- as.data.frame(reference)[, cols, drop = FALSE]
  if (!all(vapply(ref_df, is.numeric, logical(1)))) {
    fail("reference columns must be numeric")
  }
  x <- as.matrix(ref_df)
  if (any(!is.finite(x))) {
    fail("reference contains non-finite values")
  }
  n <- nrow(x)
  p <- ncol(x)
  if (n < p + 2L) {
    fail(sprintf("%d rows cannot calibrate %d columns (need at least %d)", n, p, p + 2L))
  }
  sds <- apply(x, 2L, stats::sd)
  scale_ref <- pmax(1, abs(colMeans(x)))
  flat <- !is.finite(sds) | sds <= 1e-8 * scale_ref
  if (any(flat)) {
    fail("zero-variance column(s): ", paste(cols[flat], collapse = ", "))
  }
  z <- scale(x)
  rank <- qr(z, tol = 1e-7)$rank
  if (rank < p) {
    fail(sprintf("collinear columns (rank %d of %d)", rank, p))
  }
  s_mat <- stats::cov(x)
  ok_chol <- tryCatch({
    chol(s_mat)
    TRUE
  }, error = function(e) FALSE)
  rc <- tryCatch(rcond(stats::cor(x)), error = function(e) 0)
  if (!ok_chol || !is.finite(rc) || rc < min_rcond) {
    fail("covariance is singular or not positive definite")
  }
  d <- tryCatch(maha_distance(x, x), error = function(e) NULL, warning = function(w) NULL)
  if (is.null(d) || any(!is.finite(d))) {
    fail("reference Mahalanobis distances are not finite")
  }
  invisible(TRUE)
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

#' Frozen Mahalanobis novelty threshold from reference (training) distances.
#'
#' The threshold is the 0.99 quantile of the reference rows' own distances to
#' the reference mean and covariance. It never depends on the prediction grid.
#' @export
maha_reference_threshold <- function(maha_ref, prob = 0.99) {
  maha_ref <- as.numeric(maha_ref)
  if (!length(maha_ref) || any(!is.finite(maha_ref))) {
    stop("frozen reference Mahalanobis distances must be non-empty and finite", call. = FALSE)
  }
  unname(stats::quantile(maha_ref, probs = prob, names = FALSE))
}

#' Classify OOD level 0-3 per spec defaults.
#'
#' Mahalanobis novelty is judged against ``maha_ref``: distances of the frozen
#' training/reference rows, never the prediction grid's own distribution.
#' Non-finite grid distances count as novel.
#' @param maha_ref Frozen reference distances (see [maha_distance()] on the reference).
#' @export
classify_ood_level <- function(
  mess,
  nt1,
  nt2,
  maha,
  hull_out,
  mess_mask_below = -20,
  maha_ref = NULL
) {
  if (is.null(maha_ref)) {
    stop("maha_ref (frozen reference Mahalanobis distances) is required", call. = FALSE)
  }
  maha_threshold <- maha_reference_threshold(maha_ref)
  lvl <- rep(0L, length(mess))
  lvl[mess < 0 & mess >= mess_mask_below] <- 2L
  lvl[mess < mess_mask_below] <- 3L
  lvl[nt1 < 0] <- pmax(lvl[nt1 < 0], 2L)
  maha_novel <- !is.finite(maha) | (maha > maha_threshold) %in% TRUE
  caution <- (nt2 > 1) %in% TRUE | hull_out %in% TRUE | maha_novel
  lvl[caution & lvl < 2L] <- 1L
  lvl
}
