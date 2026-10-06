#' Rolling-origin 24/48/72 h egg-encounter validation.
#'
#' Implements prereg/cufes_forecast_temporal_holdout_design.md.
#' The operational arm is a damped-anomaly proxy, never an issued forecast.
#' Every operational record carries operational_claim NOT_ISSUED_FORECAST.

FORECAST_OPERATIONAL_CLAIM <- "NOT_ISSUED_FORECAST"
FORECAST_PHYSICS_SOURCE <- "damped_anomaly_proxy"
FORECAST_TAU_DAYS <- 3
FORECAST_HORIZONS <- c(24L, 48L, 72L)

#' Meteorological season of a cutoff date (DJF, MAM, JJA, SON).
#' @export
forecast_season <- function(date) {
  m <- as.integer(format(as.Date(date), "%m"))
  ifelse(
    m %in% c(12L, 1L, 2L),
    "DJF",
    ifelse(m %in% 3:5, "MAM", ifelse(m %in% 6:8, "JJA", "SON"))
  )
}

#' Circular day-of-year distance on a 366-day circle.
#' @export
forecast_doy_distance <- function(doy_a, doy_b) {
  d <- abs(as.integer(doy_a) - as.integer(doy_b))
  pmin(d, 366L - d)
}

#' Day-of-year (1-366) for Date or ISO strings.
#' @export
forecast_doy <- function(date) {
  as.integer(format(as.Date(date), "%j"))
}

#' Inverse-distance weights, power 2. Exact hits (distance 0) take equal weight
#' and everyone else is ignored. Distances above max_km are already dropped.
#' @export
forecast_idw <- function(values, dist_km) {
  values <- as.numeric(values)
  dist_km <- as.numeric(dist_km)
  ok <- is.finite(values) & is.finite(dist_km) & dist_km >= 0
  if (!any(ok)) {
    return(NA_real_)
  }
  values <- values[ok]
  dist_km <- dist_km[ok]
  hit <- dist_km == 0
  if (any(hit)) {
    return(mean(values[hit]))
  }
  w <- dist_km^(-2)
  sum(w * values) / sum(w)
}

#' Lead-damped anomaly. tau is fixed at 3 days by the approved design.
#' @export
forecast_damped_anomaly <- function(clim, x_cutoff, horizon_days, tau = FORECAST_TAU_DAYS) {
  as.numeric(clim) + exp(-as.numeric(horizon_days) / tau) * (as.numeric(x_cutoff) - as.numeric(clim))
}

#' Integer time indices to project after the last training index, through D+3.
#' @export
forecast_extra_time <- function(max_train_time_idx, future_time_idx) {
  lo <- as.integer(max_train_time_idx) + 1L
  hi <- max(as.integer(future_time_idx))
  if (!is.finite(lo) || !is.finite(hi) || hi < lo) {
    stop("future time_idx must be strictly after the last training time_idx", call. = FALSE)
  }
  seq.int(lo, hi)
}

#' Euclidean km distance from one point to many, X/Y already in km.
forecast_dist_km <- function(x0, y0, x, y) {
  sqrt((as.numeric(x) - x0)^2 + (as.numeric(y) - y0)^2)
}

#' Pick two cutoffs per season from eligible dates.
#'
#' Within a season, take the earliest and latest dates at least `pair_gap_days`
#' apart. If none are that far apart, take the two farthest and record the gap.
#' Then enforce `min_sep_days` across the selected set by moving the later date
#' of a close pair to the nearest eligible date in its season that restores the
#' gap. If that cannot be done, status is design_infeasible.
#' @param eligible Date vector.
#' @export
select_forecast_cutoffs <- function(eligible, pair_gap_days = 365L, min_sep_days = 30L) {
  eligible <- sort(unique(as.Date(eligible)))
  seasons <- c("DJF", "MAM", "JJA", "SON")
  notes <- character()
  chosen <- list()
  for (season in seasons) {
    pool <- eligible[forecast_season(eligible) == season]
    if (length(pool) < 2L) {
      return(list(
        status = "design_infeasible",
        reason = paste0("season ", season, " has ", length(pool), " eligible cutoff(s)"),
        cutoffs = as.Date(character()),
        notes = notes
      ))
    }
    gap <- as.integer(pool[length(pool)] - pool[1L])
    if (gap >= pair_gap_days) {
      pair <- c(pool[1L], pool[length(pool)])
    } else {
      best_i <- 1L
      best_j <- 2L
      best_gap <- as.integer(pool[2L] - pool[1L])
      for (i in seq_len(length(pool) - 1L)) {
        for (j in (i + 1L):length(pool)) {
          g <- as.integer(pool[j] - pool[i])
          if (g > best_gap) {
            best_gap <- g
            best_i <- i
            best_j <- j
          }
        }
      }
      pair <- c(pool[best_i], pool[best_j])
      notes <- c(notes, sprintf(
        "%s pair gap is %d days, under the %d-day target",
        season, best_gap, pair_gap_days
      ))
    }
    chosen[[season]] <- pair
  }
  selected <- as.Date(do.call(c, chosen))
  names(selected) <- rep(names(chosen), each = 2L)
  guard <- 0L

  repeat {
    guard <- guard + 1L
    if (guard > 16L) {
      return(list(
        status = "design_infeasible",
        reason = "cutoff separation did not settle",
        cutoffs = as.Date(character()),
        notes = notes
      ))
    }
    ord <- order(selected)
    selected <- selected[ord]
    conflict <- NA_integer_
    for (i in seq_len(length(selected) - 1L)) {
      if (as.integer(selected[i + 1L] - selected[i]) < min_sep_days) {
        conflict <- i
        break
      }
    }
    if (is.na(conflict)) {
      break
    }
    later <- selected[conflict + 1L]
    season <- forecast_season(later)
    partner <- selected[names(selected) == season & selected != later]
    pool <- eligible[forecast_season(eligible) == season]
    blocked <- selected[names(selected) != season]
    ok <- vapply(seq_along(pool), function(i) {
      d <- pool[[i]]
      if (length(partner) && as.integer(abs(d - partner[[1L]])) < 1L) {
        return(FALSE)
      }
      sep_ok <- all(abs(as.integer(d - blocked)) >= min_sep_days)
      pair_ok <- TRUE
      if (length(partner)) {
        pair_ok <- as.integer(abs(d - partner[[1L]])) >= 1L
      }
      # Keep a pair that already clears pair_gap_days from collapsing.
      season_pair <- selected[names(selected) == season]
      if (length(season_pair) == 2L && as.integer(abs(season_pair[[1L]] - season_pair[[2L]])) >= pair_gap_days) {
        pair_ok <- as.integer(abs(d - partner[[1L]])) >= pair_gap_days
      }
      sep_ok && pair_ok && !(d %in% selected)
    }, logical(1))
    if (!any(ok)) {
      return(list(
        status = "design_infeasible",
        reason = paste0(
          "cannot separate ", format(later),
          " from another cutoff by ", min_sep_days, " days"
        ),
        cutoffs = as.Date(character()),
        notes = notes
      ))
    }
    cand <- pool[ok]
    replacement <- cand[which.min(abs(as.integer(cand - later)))]
    notes <- c(notes, sprintf(
      "moved %s cutoff %s to %s to keep cutoffs %d days apart",
      season, format(later), format(replacement), min_sep_days
    ))
    selected[conflict + 1L] <- replacement
  }
  selected <- selected[order(selected)]
  list(
    status = "ok",
    reason = NULL,
    cutoffs = unname(selected),
    seasons = unname(forecast_season(selected)),
    notes = notes
  )
}

#' Days that satisfy the approved eligibility rule for one species frame.
#' @param daily data.frame with day, n, n_pos, n_neg.
#' @export
forecast_eligible_days <- function(
  daily,
  test_end,
  min_rows = 2000L,
  min_days = 30L
) {
  daily <- daily[order(daily$day), , drop = FALSE]
  days <- as.Date(daily$day)
  n_by <- stats::setNames(as.numeric(daily$n), as.character(days))
  out <- as.Date(character())
  for (i in seq_along(days)) {
    D <- days[[i]]
    horizon <- D + 1:3
    if (horizon[3L] > as.Date(test_end)) {
      next
    }
    key <- as.character(horizon)
    if (!all(key %in% names(n_by)) || any(n_by[key] < 1)) {
      next
    }
    sub <- daily[days <= D, , drop = FALSE]
    if (sum(sub$n) < min_rows || nrow(sub) < min_days) {
      next
    }
    if (sum(sub$n_pos) < 1 || sum(sub$n_neg) < 1) {
      next
    }
    out <- c(out, D)
  }
  as.Date(out, origin = "1970-01-01")
}

#' Local climatology support: mean of `values` within max_km and a doy window.
#' Widens the window through 15, 30, 45. Returns NA when fewer than min_n.
#' @export
forecast_local_mean <- function(values, dist_km, doy_dist, windows = c(15L, 30L, 45L), max_km = 60, min_n = 20L) {
  values <- as.numeric(values)
  dist_km <- as.numeric(dist_km)
  doy_dist <- as.numeric(doy_dist)
  for (w in windows) {
    keep <- is.finite(values) & is.finite(dist_km) & dist_km <= max_km & doy_dist <= w
    if (sum(keep) >= min_n) {
      return(mean(values[keep]))
    }
  }
  NA_real_
}

#' 24 h pass rule. Strictly greater AUC and TSS than both baselines.
#' @export
forecast_passes_24h <- function(op_auc, per_auc, clim_auc, op_tss, per_tss, clim_tss, n_eligible, min_eligible = 6L) {
  nums <- c(op_auc, per_auc, clim_auc, op_tss, per_tss, clim_tss)
  if (length(nums) != 6L || any(!is.finite(nums))) {
    return(FALSE)
  }
  if (!is.finite(n_eligible) || n_eligible < min_eligible) {
    return(FALSE)
  }
  op_auc > per_auc && op_auc > clim_auc && op_tss > per_tss && op_tss > clim_tss
}

.forecast_round <- function(x, digits = 6) {
  if (is.null(x) || !length(x) || all(is.na(x))) {
    return(NA_real_)
  }
  round(as.numeric(x), digits)
}

.forecast_metric_block <- function(z, p, ll, elpd_kind) {
  z <- as.integer(z)
  p <- as.numeric(p)
  ll <- as.numeric(ll)
  ok <- is.finite(p) & (z %in% c(0L, 1L))
  z <- z[ok]
  p <- p[ok]
  ll <- ll[ok]
  n <- length(z)
  auc <- if (n && any(z == 1L) && any(z == 0L)) auc_mw(z, p) else NA_real_
  tss <- if (n && any(z == 1L) && any(z == 0L)) tss_at(z, p, 0.5) else NA_real_
  boyce <- if (n && any(z == 1L)) cbi_continuous(p, p[z == 1L]) else NA_real_
  elpd <- if (n && all(is.finite(ll))) sum(ll) else NA_real_
  block <- list(
    n = n,
    n_presence = sum(z == 1L),
    auc = .forecast_round(auc),
    tss = .forecast_round(tss),
    boyce = .forecast_round(boyce),
    elpd_per_event = if (is.finite(elpd) && n > 0) .forecast_round(elpd / n) else NULL
  )
  if (identical(elpd_kind, "delta")) {
    block$elpd <- .forecast_round(elpd)
    block$elpd_kind <- "delta_encounter_plus_gamma"
  } else {
    block$elpd_encounter_bernoulli <- .forecast_round(elpd)
    block$elpd_kind <- "encounter_bernoulli_only"
    block$elpd_not_ranked_against_delta <- TRUE
  }
  block
}

#' Pool common-support rows into horizon metrics.
#' @param rows data.frame with horizon_hours, z, p_*, ll_*, in_common_support
#' @export
forecast_pool_metrics <- function(rows) {
  sources <- c("oracle", "operational_proxy", "persistence", "climatology")
  kinds <- c(oracle = "delta", operational_proxy = "delta", persistence = "delta", climatology = "bernoulli")
  horizons <- FORECAST_HORIZONS
  out <- list()
  for (h in horizons) {
    sub <- rows[rows$in_common_support %in% TRUE & rows$horizon_hours == h, , drop = FALSE]
    slot <- list(horizon_hours = h, n_common_support = nrow(sub))
    for (src in sources) {
      block <- .forecast_metric_block(
        sub$z,
        sub[[paste0("p_", src)]],
        sub[[paste0("ll_", src)]],
        kinds[[src]]
      )
      if (identical(src, "operational_proxy")) {
        block$operational_claim <- FORECAST_OPERATIONAL_CLAIM
        block$physics_source <- FORECAST_PHYSICS_SOURCE
      }
      slot[[src]] <- block
    }
    if (nrow(sub)) {
      slot$degradation_from_24h <- NULL
    }
    out[[as.character(h)]] <- slot
  }
  h24 <- out[["24"]]
  for (h in c(48L, 72L)) {
    slot <- out[[as.character(h)]]
    deg <- list()
    for (src in sources) {
      deg[[src]] <- list(
        auc = .forecast_round(slot[[src]]$auc - h24[[src]]$auc),
        tss = .forecast_round(slot[[src]]$tss - h24[[src]]$tss)
      )
      if (identical(src, "operational_proxy")) {
        deg[[src]]$operational_claim <- FORECAST_OPERATIONAL_CLAIM
      }
    }
    out[[as.character(h)]]$degradation_from_24h <- deg
  }
  out
}

.forecast_event_delta_ll <- function(p, y, mu, shape) {
  y <- as.numeric(y)
  p <- as.numeric(p)
  z <- y > 0
  ll <- ifelse(z, log(pmax(p, .Machine$double.eps)), log(pmax(1 - p, .Machine$double.eps)))
  if (any(z)) {
    scale <- as.numeric(mu[z]) / shape
    ll[z] <- ll[z] + stats::dgamma(y[z], shape = shape, scale = scale, log = TRUE)
  }
  ll
}

.forecast_bernoulli_ll <- function(p, y) {
  y <- as.numeric(y)
  p <- as.numeric(p)
  z <- y > 0
  ifelse(z, log(pmax(p, .Machine$double.eps)), log(pmax(1 - p, .Machine$double.eps)))
}

.forecast_fmt <- function(x) {
  if (is.null(x) || length(x) != 1L || !is.finite(x)) {
    return("not available")
  }
  sprintf("%.3f", x)
}

.forecast_delta_fmt <- function(later, earlier) {
  if (is.null(later) || is.null(earlier) || !is.finite(later) || !is.finite(earlier)) {
    return("not available")
  }
  sprintf("%+.3f", later - earlier)
}

#' Plain-language readout. Does not claim an issued forecast.
#' @export
forecast_business_readout <- function(species_results) {
  lines <- c(
    "This checks whether a 72-hour map of sardine and anchovy egg encounter beats two simple baselines. It is about eggs in the water, not where adult fish are, and it is not harvest advice.",
    "The operational numbers do not use an issued ocean forecast. No archived issued forecast overlaps these egg surveys, so those scores use a stand-in ocean field and are labeled NOT_ISSUED_FORECAST everywhere."
  )
  for (sp in species_results) {
    name <- sp$label %||% "species"
    if (!is.null(sp$fit_status) && identical(sp$fit_status, "design_infeasible")) {
      lines <- c(lines, paste0(name, ": the cutoff rule could not be met, so no forecast score is reported."))
      next
    }
    n_el <- sp$n_eligible_cutoffs %||% 0L
    pooled <- sp$pooled
    if (is.null(pooled) || is.null(pooled[["24"]])) {
      lines <- c(lines, paste0(name, ": scores are not available."))
      next
    }
    h24 <- pooled[["24"]]
    op <- h24$operational_proxy
    per <- h24$persistence
    clim <- h24$climatology
    ora <- h24$oracle
    pass <- isTRUE(sp$pass_24h)
    if (n_el < 6L) {
      lines <- c(lines, sprintf(
        "%s: only %d of 8 cutoffs produced a usable fit. Six are required, so this is not a result. The 72-hour forecast does not beat the baselines.",
        name, n_el
      ))
      next
    }
    verdict <- if (pass) {
      sprintf(
        "%s at 24 hours: the NOT_ISSUED_FORECAST proxy beats both baselines. That comparison uses %s tows, %s of them with eggs. AUC %s versus persistence %s and climatology %s (higher is better). TSS %s versus persistence %s and climatology %s.",
        name,
        .forecast_count(h24$n_common_support), .forecast_count(op$n_presence),
        .forecast_fmt(op$auc), .forecast_fmt(per$auc), .forecast_fmt(clim$auc),
        .forecast_fmt(op$tss), .forecast_fmt(per$tss), .forecast_fmt(clim$tss)
      )
    } else {
      sprintf(
        "%s at 24 hours: the NOT_ISSUED_FORECAST proxy does not beat both baselines. That comparison uses %s tows, %s of them with eggs. AUC %s versus persistence %s and climatology %s. TSS %s versus persistence %s and climatology %s.",
        name,
        .forecast_count(h24$n_common_support), .forecast_count(op$n_presence),
        .forecast_fmt(op$auc), .forecast_fmt(per$auc), .forecast_fmt(clim$auc),
        .forecast_fmt(op$tss), .forecast_fmt(per$tss), .forecast_fmt(clim$tss)
      )
    }
    h48s <- pooled[["48"]]
    h72s <- pooled[["72"]]
    h48 <- h48s$operational_proxy
    h72 <- h72s$operational_proxy
    deg <- sprintf(
      "At 48 hours (%s tows, %s with eggs) the NOT_ISSUED_FORECAST proxy AUC is %s, a change of %s from 24 hours, and TSS is %s, a change of %s. At 72 hours (%s tows, %s with eggs) the proxy AUC is %s, a change of %s, and TSS is %s, a change of %s.",
      .forecast_count(h48s$n_common_support), .forecast_count(h48$n_presence),
      .forecast_fmt(h48$auc), .forecast_delta_fmt(h48$auc, op$auc),
      .forecast_fmt(h48$tss), .forecast_delta_fmt(h48$tss, op$tss),
      .forecast_count(h72s$n_common_support), .forecast_count(h72$n_presence),
      .forecast_fmt(h72$auc), .forecast_delta_fmt(h72$auc, op$auc),
      .forecast_fmt(h72$tss), .forecast_delta_fmt(h72$tss, op$tss)
    )
    oracle_line <- sprintf(
      "If the analysed ocean state is treated as known (a retrospective ceiling, not the product), 24-hour AUC is %s and TSS is %s. That ceiling is not the 72-hour product.",
      .forecast_fmt(ora$auc), .forecast_fmt(ora$tss)
    )
    lines <- c(lines, verdict, deg, oracle_line)
  }
  paste(lines, collapse = "\n\n")
}

.forecast_count <- function(x) {
  if (is.null(x) || length(x) != 1L || !is.finite(as.numeric(x))) {
    return("an unknown number of")
  }
  as.character(as.integer(x))
}

.forecast_daily_summary <- function(dat) {
  day <- as.Date(dat$event_day)
  y <- as.numeric(dat$y)
  spl <- split(seq_len(nrow(dat)), day)
  data.frame(
    day = as.Date(names(spl)),
    n = vapply(spl, length, integer(1)),
    n_pos = vapply(spl, function(i) sum(y[i] > 0), integer(1)),
    n_neg = vapply(spl, function(i) sum(y[i] == 0), integer(1)),
    stringsAsFactors = FALSE
  )
}

.forecast_prepare_frame <- function(dat, cfg) {
  origin <- .time_idx_origin_date(cfg)
  dat$event_day <- origin + (as.integer(dat$time_idx) - 1L)
  dat$doy <- forecast_doy(dat$event_day)
  dat
}

#' Lock cutoff dates from loaded species frames. No fits.
#' @export
forecast_lock_cutoffs <- function(frames, test_end) {
  eligible <- lapply(frames, function(dat) {
    forecast_eligible_days(.forecast_daily_summary(dat), test_end = test_end)
  })
  shared <- Reduce(intersect, eligible)
  picked <- select_forecast_cutoffs(shared)
  list(
    eligible = eligible,
    shared_n = length(shared),
    calendar = if (identical(picked$status, "ok")) "shared" else "unresolved",
    selection = picked
  )
}

.forecast_dynamic_columns <- function(cfg) {
  dyn <- cfg$covariates$dynamic %||% character()
  paste0(dyn, "_z")
}

.forecast_shape <- function(fit) {
  ln_phi <- fit$par$ln_phi
  if (is.null(ln_phi)) {
    stop("missing ln_phi for positive-component log-likelihood", call. = FALSE)
  }
  shape <- exp(as.numeric(ln_phi)[1L])
  if (!is.finite(shape) || shape <= 0) {
    stop("invalid ln_phi for positive-component log-likelihood", call. = FALSE)
  }
  shape
}

.forecast_positive_mu <- function(fit, newdata) {
  pr <- stats::predict(fit, newdata = newdata, model = 2L, offset = newdata$log_effort)
  exp(as.numeric(pr$est2))
}

.forecast_score_rows <- function(fit, train, hold, cfg, cutoff_date, extra_time) {
  dyn_cols <- .forecast_dynamic_columns(cfg)
  missing_cols <- setdiff(dyn_cols, names(hold))
  if (length(missing_cols)) {
    stop("holdout frame missing covariate columns: ", paste(missing_cols, collapse = ", "), call. = FALSE)
  }
  cutoff_rows <- train[train$event_day == cutoff_date, , drop = FALSE]
  if (!nrow(cutoff_rows)) {
    stop("cutoff day has no training rows", call. = FALSE)
  }
  p_cut <- as.numeric(score_encounter_on_events(fit, cutoff_rows, cfg))
  mu_cut <- .forecast_positive_mu(fit, cutoff_rows)
  shape <- .forecast_shape(fit)
  future_idx <- sort(unique(as.integer(hold$time_idx)))
  if (!all(future_idx %in% as.integer(extra_time))) {
    stop("holdout time_idx was not projected with extra_time", call. = FALSE)
  }

  n <- nrow(hold)
  p_per <- rep(NA_real_, n)
  p_clim <- rep(NA_real_, n)
  ll_per <- rep(NA_real_, n)
  ll_clim <- rep(NA_real_, n)
  unknown <- rep("", n)
  op_new <- hold

  for (i in seq_len(n)) {
    h_days <- as.integer(hold$event_day[i] - cutoff_date)
    reasons <- character()
    d_cut <- forecast_dist_km(hold$X[i], hold$Y[i], cutoff_rows$X, cutoff_rows$Y)
    near_cut <- is.finite(d_cut) & d_cut <= 120
    if (!any(near_cut)) {
      reasons <- c(reasons, "no_cutoff_track_within_120km")
    } else {
      p_per[i] <- forecast_idw(p_cut[near_cut], d_cut[near_cut])
      mu_i <- forecast_idw(mu_cut[near_cut], d_cut[near_cut])
      if (is.finite(p_per[i]) && is.finite(mu_i) && mu_i > 0) {
        ll_per[i] <- .forecast_event_delta_ll(p_per[i], hold$y[i], mu_i, shape)
      } else {
        p_per[i] <- NA_real_
        reasons <- c(reasons, "persistence_mean_not_finite")
      }
    }
    d_train <- forecast_dist_km(hold$X[i], hold$Y[i], train$X, train$Y)
    doy_d <- forecast_doy_distance(train$doy, hold$doy[i])
    p_clim[i] <- forecast_local_mean(as.numeric(train$y > 0), d_train, doy_d)
    if (!is.finite(p_clim[i])) {
      reasons <- c(reasons, "climatology_support")
    } else {
      ll_clim[i] <- .forecast_bernoulli_ll(p_clim[i], hold$y[i])
    }
    op_ok <- any(near_cut)
    x_cut <- stats::setNames(rep(NA_real_, length(dyn_cols)), dyn_cols)
    clim <- x_cut
    for (col in dyn_cols) {
      if (any(near_cut)) {
        x_cut[[col]] <- forecast_idw(cutoff_rows[[col]][near_cut], d_cut[near_cut])
      }
      clim[[col]] <- forecast_local_mean(train[[col]], d_train, doy_d)
      if (!is.finite(x_cut[[col]]) || !is.finite(clim[[col]])) {
        op_ok <- FALSE
      }
    }
    if (!op_ok) {
      reasons <- c(reasons, "operational_proxy_support")
    } else {
      for (col in dyn_cols) {
        op_new[[col]][i] <- forecast_damped_anomaly(clim[[col]], x_cut[[col]], h_days)
      }
    }
    unknown[i] <- paste(unique(reasons), collapse = ";")
  }

  p_oracle <- as.numeric(score_encounter_on_events(fit, hold, cfg))
  mu_oracle <- .forecast_positive_mu(fit, hold)
  ll_oracle <- .forecast_event_delta_ll(p_oracle, hold$y, mu_oracle, shape)

  op_rows <- !grepl("operational_proxy_support", unknown)
  p_op <- rep(NA_real_, n)
  ll_op <- rep(NA_real_, n)
  if (any(op_rows)) {
    op_sub <- op_new[op_rows, , drop = FALSE]
    p_op[op_rows] <- as.numeric(score_encounter_on_events(fit, op_sub, cfg))
    mu_op <- .forecast_positive_mu(fit, op_sub)
    ll_op[op_rows] <- .forecast_event_delta_ll(p_op[op_rows], op_sub$y, mu_op, shape)
  }

  common <- is.finite(p_oracle) & is.finite(ll_oracle) &
    is.finite(p_op) & is.finite(ll_op) &
    is.finite(p_per) & is.finite(ll_per) &
    is.finite(p_clim) & is.finite(ll_clim)

  data.frame(
    cutoff = format(as.Date(cutoff_date)),
    horizon_hours = as.integer(hold$event_day - cutoff_date) * 24L,
    z = as.integer(hold$y > 0),
    p_oracle = p_oracle,
    p_operational_proxy = p_op,
    p_persistence = p_per,
    p_climatology = p_clim,
    ll_oracle = ll_oracle,
    ll_operational_proxy = ll_op,
    ll_persistence = ll_per,
    ll_climatology = ll_clim,
    in_common_support = common,
    unknown_reason = ifelse(common, "", unknown),
    stringsAsFactors = FALSE
  )
}

#' Fit one cutoff and score 24/48/72 h. Projects the daily intercept with extra_time.
#' @export
forecast_fit_cutoff <- function(dat, cfg, cutoff_date) {
  .cv_limit_tmb_threads()
  cutoff_date <- as.Date(cutoff_date)
  train <- dat[dat$event_day <= cutoff_date, , drop = FALSE]
  hold <- dat[dat$event_day %in% (cutoff_date + 1:3), , drop = FALSE]
  if (!nrow(train) || !nrow(hold)) {
    stop("cutoff is missing training or holdout rows", call. = FALSE)
  }
  if (!any(train$event_day == cutoff_date)) {
    stop("cutoff day is not inside the training rows", call. = FALSE)
  }
  max_train <- max(as.integer(train$time_idx))
  extra <- forecast_extra_time(max_train, hold$time_idx)
  fit_cfg <- cfg
  fit_cfg$model$extra_time_slices <- extra
  mesh <- build_fishai_production_mesh(train, cfg$mesh)
  fit_res <- fit_delta_engine(train, mesh, fit_cfg)
  reason <- .cv_fit_failure_reason(fit_res)
  if (!is.null(reason)) {
    return(list(
      cutoff = format(cutoff_date),
      eligible = FALSE,
      failure = reason,
      rows = NULL
    ))
  }
  rows <- .forecast_score_rows(fit_res$fit, train, hold, cfg, cutoff_date, extra)
  list(
    cutoff = format(cutoff_date),
    eligible = TRUE,
    failure = NULL,
    n_train = nrow(train),
    n_holdout = nrow(hold),
    n_common_support = sum(rows$in_common_support),
    extra_time = extra,
    rows = rows
  )
}

.forecast_checkpoint_path <- function(dir, label, cutoff) {
  file.path(dir, .cv_sanitize_checkpoint_label(label), paste0(format(as.Date(cutoff)), ".rds"))
}

.forecast_species_from_rows <- function(label, taxon, model_config, cutoffs, pieces) {
  eligible <- vapply(pieces, function(x) isTRUE(x$eligible), logical(1))
  rows <- do.call(rbind, lapply(pieces[eligible], function(x) x$rows))
  pooled <- if (!is.null(rows) && nrow(rows)) forecast_pool_metrics(rows) else NULL
  h24 <- if (!is.null(pooled)) pooled[["24"]] else NULL
  pass <- FALSE
  if (!is.null(h24)) {
    pass <- forecast_passes_24h(
      h24$operational_proxy$auc,
      h24$persistence$auc,
      h24$climatology$auc,
      h24$operational_proxy$tss,
      h24$persistence$tss,
      h24$climatology$tss,
      sum(eligible)
    )
  }
  per_cutoff <- lapply(pieces, function(x) {
    base <- list(
      cutoff = x$cutoff,
      eligible = isTRUE(x$eligible),
      failure = x$failure,
      n_train = x$n_train %||% NULL,
      n_holdout = x$n_holdout %||% NULL,
      n_common_support = x$n_common_support %||% 0L
    )
    if (isTRUE(x$eligible) && !is.null(x$rows)) {
      base$horizons <- forecast_pool_metrics(x$rows)
    }
    base
  })
  list(
    label = label,
    taxon = taxon,
    model_config = model_config,
    operational_claim = FORECAST_OPERATIONAL_CLAIM,
    physics_source = FORECAST_PHYSICS_SOURCE,
    n_cutoffs = length(cutoffs),
    n_eligible_cutoffs = sum(eligible),
    fit_status = if (sum(eligible) >= 6L) "scored" else "INSUFFICIENT",
    pass_24h = pass,
    pass_rule = "operational_proxy AUC and TSS at 24h strictly greater than persistence and climatology, with at least 6 eligible cutoffs",
    pooled = pooled,
    cutoffs = per_cutoff
  )
}

#' Run the approved rolling-origin validation and write JSON plus the readout.
#' @export
run_forecast_temporal_holdout <- function(
  root = NULL,
  inventory_only = FALSE,
  checkpoint_dir = NULL,
  scores_json = NULL,
  readout_md = NULL
) {
  root <- root %||% Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  scores_json <- scores_json %||% file.path(root, "prereg", "cufes_forecast_temporal_holdout_scores.json")
  readout_md <- readout_md %||% file.path(root, "prereg", "cufes_forecast_temporal_holdout_readout.md")
  checkpoint_dir <- checkpoint_dir %||% file.path(root, "artifacts", "forecast_temporal_holdout", "checkpoints")
  species_specs <- list(
    list(label = "sardine", config = "configs/models/cufes_sardine.yaml"),
    list(label = "anchovy", config = "configs/models/cufes_anchovy.yaml")
  )
  frames <- list()
  cfgs <- list()
  for (sp in species_specs) {
    cfg <- load_config_yaml(file.path(root, sp$config))
    .ensure_barrier_land_rds(cfg, root)
    dat <- load_model_data(cfg = cfg, min_duration_min = 2, egg_split_scope = "all")
    dat <- .forecast_prepare_frame(dat, cfg)
    frames[[sp$label]] <- dat
    cfgs[[sp$label]] <- cfg
  }
  test_end <- as.Date(cfgs[[1]]$egg_split$test_end)
  locked <- forecast_lock_cutoffs(frames, test_end)
  manifest <- list(
    status = if (inventory_only) "cutoffs_locked" else "ok",
    claim = "72h egg-encounter forecast skill",
    operational_claim = FORECAST_OPERATIONAL_CLAIM,
    physics_source = FORECAST_PHYSICS_SOURCE,
    tau_days = FORECAST_TAU_DAYS,
    lane_oracle = "retrospective",
    code_sha = Sys.getenv("GITHUB_SHA", unset = NA_character_),
    design = "prereg/cufes_forecast_temporal_holdout_design.md",
    test_end = format(test_end),
    cutoff_calendar = locked$calendar,
    cutoff_selection_status = locked$selection$status,
    cutoff_selection_reason = locked$selection$reason,
    cutoff_notes = as.list(locked$selection$notes),
    cutoffs = format(locked$selection$cutoffs),
    cutoff_seasons = as.list(locked$selection$seasons %||% forecast_season(locked$selection$cutoffs)),
    eligible_counts = lapply(locked$eligible, length),
    min_train_rows = 2000L,
    min_train_days = 30L,
    species = list()
  )
  if (!identical(locked$selection$status, "ok")) {
    manifest$status <- "design_infeasible"
    .forecast_write_outputs(manifest, character(), scores_json, readout_md)
    return(manifest)
  }
  if (inventory_only) {
    .forecast_write_outputs(manifest, character(), scores_json, readout_md)
    return(manifest)
  }
  species_out <- list()
  for (sp in species_specs) {
    pieces <- list()
    for (cutoff in locked$selection$cutoffs) {
      path <- .forecast_checkpoint_path(checkpoint_dir, sp$label, cutoff)
      if (file.exists(path)) {
        pieces[[length(pieces) + 1L]] <- readRDS(path)
        message("FORECAST_CUTOFF_SKIPPED ", sp$label, " ", format(cutoff))
        next
      }
      message("FORECAST_CUTOFF_START ", sp$label, " ", format(cutoff))
      piece <- tryCatch(
        forecast_fit_cutoff(frames[[sp$label]], cfgs[[sp$label]], cutoff),
        error = function(e) {
          list(
            cutoff = format(as.Date(cutoff)),
            eligible = FALSE,
            failure = conditionMessage(e),
            rows = NULL
          )
        }
      )
      dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
      saveRDS(piece, path)
      pieces[[length(pieces) + 1L]] <- piece
      gc(verbose = FALSE)
    }
    species_out[[length(species_out) + 1L]] <- .forecast_species_from_rows(
      sp$label,
      cfgs[[sp$label]]$species$taxon,
      sp$config,
      locked$selection$cutoffs,
      pieces
    )
  }
  readout <- forecast_business_readout(species_out)
  manifest$species <- species_out
  manifest$pass_24h <- lapply(species_out, function(x) x$pass_24h)
  .forecast_write_outputs(manifest, readout, scores_json, readout_md)
  manifest
}

.forecast_write_outputs <- function(manifest, readout, scores_json, readout_md) {
  dir.create(dirname(scores_json), recursive = TRUE, showWarnings = FALSE)
  jsonlite::write_json(manifest, scores_json, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null")
  if (length(readout) && nzchar(readout)) {
    writeLines(readout, readout_md)
  }
  invisible(TRUE)
}
