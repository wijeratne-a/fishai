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

#' Continuous Boyce index (Spearman of moving ratios).
#' @export
cbi_continuous <- function(p_avail, p_pres, n_bins = 10L) {
  p_avail <- as.numeric(p_avail)
  p_pres <- as.numeric(p_pres)
  if (!length(p_avail) || !length(p_pres)) {
    return(NA_real_)
  }
  rng <- range(p_avail, na.rm = TRUE)
  if (diff(rng) == 0) {
    return(NA_real_)
  }
  w <- diff(rng) / n_bins
  mids <- seq(rng[1] + w / 2, rng[2] - w / 2, length.out = n_bins)
  fk <- numeric(n_bins)
  ek <- numeric(n_bins)
  for (i in seq_len(n_bins)) {
    lo <- rng[1] + (i - 1) * w
    hi <- lo + w
    in_w <- p_avail >= lo & p_avail < hi
    ek[i] <- mean(in_w)
    fk[i] <- mean(p_pres >= lo & p_pres < hi) / max(ek[i], .Machine$double.eps)
  }
  keep <- ek > 0
  if (sum(keep) < 3) {
    return(NA_real_)
  }
  stats::cor(fk[keep], mids[keep], method = "spearman")
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
