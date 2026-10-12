#' Mann–Whitney AUC for binary presence.
#' @export
auc_mw <- function(z, p) {
  z <- as.integer(z)
  p <- as.numeric(p)
  n1 <- sum(z == 1L)
  n0 <- sum(z == 0L)
  if (n1 == 0 || n0 == 0) {
    return(NA_real_)
  }
  r <- rank(p)
  (sum(r[z == 1L]) - n1 * (n1 + 1) / 2) / (n1 * n0)
}

#' Continuous Boyce index (Hirzel et al. 2006).
#'
#' Spearman correlation between window midpoints and the predicted/expected
#' ratio inside a moving window. The default window is one tenth of the
#' suitability range, evaluated at `n_windows` positions. Both ends of each
#' window are closed, so the maximum suitability is included. Windows with no
#' availability, and successive duplicate ratios, are dropped.
#' @param p_avail Predicted suitability at evaluation locations.
#' @param p_pres Predicted suitability at presence locations.
#' @param n_windows Number of window positions along the suitability range.
#' @export
cbi_continuous <- function(p_avail, p_pres, n_windows = 100L) {
  p_avail <- as.numeric(p_avail)
  p_pres <- as.numeric(p_pres)
  p_avail <- p_avail[is.finite(p_avail)]
  p_pres <- p_pres[is.finite(p_pres)]
  if (!length(p_avail) || !length(p_pres)) {
    return(NA_real_)
  }
  mini <- min(p_avail)
  maxi <- max(p_avail)
  if (maxi == mini) {
    return(NA_real_)
  }
  n_windows <- as.integer(n_windows)[1L]
  if (!is.finite(n_windows) || n_windows < 3L) {
    return(NA_real_)
  }
  window_w <- (maxi - mini) / 10
  starts <- seq(mini, maxi - window_w, length.out = n_windows)
  fi <- numeric(n_windows)
  mids <- numeric(n_windows)
  n_avail <- length(p_avail)
  n_pres <- length(p_pres)
  for (i in seq_len(n_windows)) {
    lo <- starts[[i]]
    hi <- lo + window_w
    if (i == n_windows) {
      hi <- maxi
    }
    n_f <- sum(p_avail >= lo & p_avail <= hi)
    n_o <- sum(p_pres >= lo & p_pres <= hi)
    mids[[i]] <- (lo + hi) / 2
    fi[[i]] <- if (n_f > 0L) (n_o / n_pres) / (n_f / n_avail) else NA_real_
  }
  ok <- is.finite(fi)
  if (sum(ok) < 2L) {
    return(NA_real_)
  }
  vals <- fi[ok]
  keep_dup <- vals != c(vals[-1], TRUE)
  keep_dup[length(keep_dup)] <- TRUE
  idx <- which(ok)[keep_dup]
  if (length(idx) < 3L) {
    return(NA_real_)
  }
  stats::cor(fi[idx], mids[idx], method = "spearman")
}

#' True skill statistic at threshold.
#' @export
tss_at <- function(z, p, thr) {
  z <- as.integer(z)
  pr <- p >= thr
  mean(pr[z == 1L]) + mean(!pr[z == 0L]) - 1
}

#' Brier score.
#' @export
brier_score <- function(z, p) {
  mean((p - as.numeric(z))^2)
}

#' Egg encounter probability on observed events using each row's ``log(volume_m3)`` offset.
#' @export
score_encounter_binomial_on_events <- function(fit, newdata, cfg) {
  if (!"log_effort" %in% names(newdata)) {
    stop("holdout data missing log_effort for per-event offsets", call. = FALSE)
  }
  pred <- stats::predict(fit, newdata = newdata)
  eta <- pred$est + newdata$log_effort
  1 / (1 + exp(-as.numeric(eta)))
}

score_encounter_on_events <- function(fit, newdata, cfg) {
  if (!"log_effort" %in% names(newdata)) {
    stop("holdout data missing log_effort for per-event offsets", call. = FALSE)
  }
  pred <- stats::predict(fit, newdata = newdata, model = 1L)
  eta <- pred$est1 + newdata$log_effort
  encounter_probability(eta, cfg = cfg)
}

#' Map-scale egg encounter draws using ``log(V_ref)`` offset (never fitted offsets).
#' @export
predict_encounter_on_grid <- function(fit, newdata, artifact, cfg, nsim = 1L) {
  assert_reference_volume(artifact)
  off <- reference_volume_offset(artifact, nrow(newdata))
  if (nsim > 1L) {
    eta_raw <- stats::predict(fit, newdata = newdata, nsim = nsim, model = 1L)
    eta <- sweep(eta_raw, 1L, off, "+")
    return(encounter_probability(eta, cfg = cfg))
  }
  pred <- stats::predict(fit, newdata = newdata, model = 1L)
  encounter_probability(pred$est1 + off, cfg = cfg)
}

#' Positive-component mean on grid with ``log(V_ref)`` offset.
#' @export
predict_positive_mean_on_grid <- function(fit, newdata, artifact, nsim = 1L) {
  assert_reference_volume(artifact)
  off <- reference_volume_offset(artifact, nrow(newdata))
  if (nsim > 1L) {
    eta <- stats::predict(fit, newdata = newdata, nsim = nsim, model = 2L, offset = off)
    return(exp(eta))
  }
  pred <- stats::predict(fit, newdata = newdata, model = 2L, offset = off)
  exp(pred$est2)
}

#' Sample-based CRPS.
#' @export
crps_sample <- function(y, samples) {
  samples <- as.numeric(samples)
  y <- as.numeric(y)
  mean(abs(samples - y)) - 0.5 * mean(abs(outer(samples, samples, "-")))
}
