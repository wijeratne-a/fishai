#' Predict egg encounter surfaces with coupled posterior draws.
#'
#' Aggregates to 10 km grid cells before summarizing. Outputs exclude point
#' coordinates (cell identifiers only). Labels describe **egg encounter**
#' evidence, not adult fish distribution.
#'
#' Map prediction uses ``offset = rep(log(V_ref), n)`` with ``V_ref`` from the
#' frozen artifact (median training ``volume_m3``). Refuses output when
#' ``reference_volume_m3`` or attributions are missing.
#'
#' @param forecast_age_hours Optional WCOFS valid-time minus source run time (hours).
#'   When set (with optional `fallback_used`), lead/evidence follow the WCOFS
#'   contract using **only** this field (never `lead_hours`).
#' @param fallback_used Whether the step used a prior-cycle fallback file.
#' @param lead_days_input Optional `lead_days` from input Zarr (may be NaN for nowcast).
#' @param wcofs_unknown_reason When set, row is `UNKNOWN` with this reason (failed pull / missing cycle).
#' @export
predict_engine <- function(
  artifact,
  grid,
  cfg,
  physics_cycle = "PASS",
  nsim = NULL,
  species = NA_character_,
  valid_day = NA_character_,
  dry_run = FALSE,
  forecast_age_hours = NULL,
  fallback_used = FALSE,
  lead_days_input = NULL,
  wcofs_unknown_reason = NULL,
  valid_time = NULL,
  source_run_time = NULL
) {
  attr_meta <- assert_prediction_attributions(
    prediction_attribution_metadata(artifact, cfg)
  )
  attr_cols <- .flatten_attributions_for_columns(attr_meta)
  vref <- assert_reference_volume(artifact)

  fit <- artifact$fit
  pred_cfg <- cfg$prediction %||% list()
  nsim <- nsim %||% pred_cfg$nsim %||% 500L
  seed <- pred_cfg$seed %||% 20260928L
  off <- reference_volume_offset(artifact, nrow(grid))

  grid$cell_id <- paste0(
    "g",
    floor(grid$X / 10),
    "_",
    floor(grid$Y / 10)
  )

  wcofs_step <- .prediction_from_wcofs_step(
    forecast_age_hours = forecast_age_hours,
    fallback_used = fallback_used,
    lead_days_input = lead_days_input,
    unknown_reason = wcofs_unknown_reason
  )
  wcofs_prov <- .prediction_wcofs_provenance_columns(
    forecast_age_hours = forecast_age_hours,
    fallback_used = fallback_used,
    valid_time = valid_time,
    source_run_time = source_run_time,
    wcofs_step = wcofs_step
  )
  if (!is.null(wcofs_step) && identical(wcofs_step$evidence_state, "UNKNOWN")) {
    ood_level <- rep(3L, nrow(grid))
    reason <- wcofs_step$unknown_reason %||% "missing_operational_cycle"
    return(.finalize_prediction_table(
      .unknown_prediction_table(grid, ood_level, reason = reason),
      attr_cols,
      artifact,
      nsim,
      seed,
      vref,
      species = species,
      valid_day = valid_day,
      dry_run = dry_run,
      lead_days = 0L,
      wcofs_provenance = wcofs_prov
    ))
  }

  if (toupper(physics_cycle) == "FAIL") {
    ood_level <- rep(3L, nrow(grid))
    return(.finalize_prediction_table(
      .unknown_prediction_table(grid, ood_level, reason = "physics_cycle_fail"),
      attr_cols,
      artifact,
      nsim,
      seed,
      vref,
      species = species,
      valid_day = valid_day,
      dry_run = dry_run,
      lead_days = 0L,
      wcofs_provenance = wcofs_prov
    ))
  }

  cov_cols <- artifact$reference_cols
  ref <- artifact$reference
  if (is.null(ref) || !length(cov_cols) || !all(cov_cols %in% names(ref)) || nrow(ref) < 2L) {
    stop("frozen artifact lacks the OOD reference rows and columns; refusing to predict", call. = FALSE)
  }
  if (!all(cov_cols %in% names(grid))) {
    stop("prediction grid lacks frozen reference columns: ", paste(setdiff(cov_cols, names(grid)), collapse = ", "), call. = FALSE)
  }
  mess <- mess_scores(grid[, cov_cols, drop = FALSE], ref)
  ex <- exdet_scores(grid[, cov_cols, drop = FALSE], ref)
  maha <- maha_distance(grid[, cov_cols, drop = FALSE], ref)
  hull <- convex_hull_flags(
    grid[, cov_cols, drop = FALSE],
    ref,
    pairs = cfg$ood$hull_pairs %||% list(c("temp_3m_z", "sal_3m_z"))
  )
  ood_level <- classify_ood_level(
    mess$mess,
    ex$nt1,
    ex$nt2,
    maha,
    hull,
    mess_mask_below = cfg$ood$mess_mask_below %||% -20,
    maha_ref = maha_distance(ref[, cov_cols, drop = FALSE], ref[, cov_cols, drop = FALSE])
  )

  set.seed(seed)
  eta1_raw <- stats::predict(fit, newdata = grid, nsim = nsim, model = 1)
  if (is.null(dim(eta1_raw))) {
    eta1_raw <- matrix(as.numeric(eta1_raw), ncol = 1L)
  }
  eta1 <- sweep(eta1_raw, 1L, off, "+")
  set.seed(seed)
  eta2 <- stats::predict(fit, newdata = grid, nsim = nsim, model = 2, offset = off)
  if (is.null(dim(eta2))) {
    eta2 <- matrix(as.numeric(eta2), ncol = 1L)
  }
  p_s <- if (is.matrix(eta1)) {
    if (is_poisson_link_delta(cfg)) {
      1 - exp(-exp(eta1))
    } else {
      1 / (1 + exp(-eta1))
    }
  } else {
    encounter_probability(eta1, cfg = cfg)
  }
  if (is.null(dim(p_s))) {
    p_s <- matrix(as.numeric(p_s), ncol = 1L)
  }
  mu_s <- exp(eta2)
  if (is.null(dim(mu_s))) {
    mu_s <- matrix(as.numeric(mu_s), ncol = 1L)
  }
  if (ncol(mu_s) == 1L && ncol(p_s) > 1L) {
    mu_s <- matrix(rep(mu_s[, 1L], ncol(p_s)), nrow = nrow(mu_s), ncol = ncol(p_s))
  } else if (ncol(p_s) == 1L && ncol(mu_s) > 1L) {
    p_s <- matrix(rep(p_s[, 1L], ncol(mu_s)), nrow = nrow(p_s), ncol = ncol(mu_s))
  }
  d_s <- p_s * mu_s

  grid$draw_p_mean <- rowMeans(p_s)
  grid$draw_d_mean <- rowMeans(d_s)
  grid$p_lo90 <- apply(p_s, 1, stats::quantile, probs = 0.05, na.rm = TRUE)
  grid$p_hi90 <- apply(p_s, 1, stats::quantile, probs = 0.95, na.rm = TRUE)

  agg <- stats::aggregate(
    cbind(draw_p_mean, draw_d_mean, p_lo90, p_hi90) ~ cell_id,
    data = grid,
    FUN = mean
  )

  agg$ood_level <- stats::aggregate(ood_level ~ cell_id, grid, FUN = max)$ood_level
  if (!is.null(wcofs_step)) {
    agg$evidence_state <- if (identical(wcofs_step$evidence_state, "NOWCAST")) {
      .prediction_evidence_state("PASS", cfg)
    } else if (identical(wcofs_step$evidence_state, "FORECAST")) {
      "FORECAST"
    } else {
      .prediction_evidence_state(physics_cycle, cfg)
    }
    agg$lead_days <- wcofs_step$lead_days
  } else {
    agg$evidence_state <- .prediction_evidence_state(physics_cycle, cfg)
    agg$lead_days <- .prediction_lead_days(physics_cycle, cfg)
  }
  agg$unknown_reason <- NA_character_
  agg$product_label <- "egg encounter (eggs sampled near 3 m depth along ship tracks)"
  agg$p_encounter <- agg$draw_p_mean
  agg$expected_density <- agg$draw_d_mean

  mask_ood <- agg$ood_level >= 2L
  if (any(mask_ood)) {
    agg$p_encounter[mask_ood] <- NA_real_
    agg$p_lo90[mask_ood] <- NA_real_
    agg$p_hi90[mask_ood] <- NA_real_
    agg$expected_density[mask_ood] <- NA_real_
    agg$evidence_state[mask_ood] <- "UNKNOWN"
    agg$unknown_reason[mask_ood] <- "ood_level_ge_2"
  }

  if (toupper(physics_cycle) == "DEGRADED") {
    issued <- agg$evidence_state != "UNKNOWN"
    agg$evidence_state[issued] <- "DEGRADED"
    w <- pred_cfg$interval_widen %||% 1.25
    if (length(w) != 1L || !is.finite(w) || w < 1) {
      stop("prediction.interval_widen must be a finite number >= 1", call. = FALSE)
    }
    p_mean <- agg$p_encounter
    lo <- agg$p_lo90
    hi <- agg$p_hi90
    agg$p_lo90[issued] <- pmin(lo, pmax(0, p_mean - w * (p_mean - lo)))[issued]
    agg$p_hi90[issued] <- pmax(hi, pmin(1, p_mean + w * (hi - p_mean)))[issued]
  }

  if (!is.null(wcofs_prov$forecast_age_hours) && is.finite(wcofs_prov$forecast_age_hours)) {
    wfac <- .prediction_interval_widen_from_forecast_age(wcofs_prov$forecast_age_hours, cfg)
    half <- (agg$p_hi90 - agg$p_lo90) / 2
    half <- half * wfac
    agg$p_lo90 <- pmax(0, agg$p_encounter - half)
    agg$p_hi90 <- pmin(1, agg$p_encounter + half)
  }

  .finalize_prediction_table(
    agg,
    attr_cols,
    artifact,
    nsim,
    seed,
    vref,
    species = species,
    valid_day = valid_day,
    dry_run = dry_run,
    lead_days = agg$lead_days[1L],
    wcofs_provenance = wcofs_prov
  )
}

.prediction_evidence_state <- function(physics_cycle, cfg) {
  pc <- toupper(physics_cycle)
  if (pc == "DEGRADED") {
    return("DEGRADED")
  }
  if (pc == "FORECAST") {
    return("FORECAST")
  }
  pred <- cfg$prediction %||% list()
  if (isTRUE(pred$hindcast_evidence)) {
    return("HINDCAST_GLORYS")
  }
  "NOWCAST_UNVALIDATED"
}

.prediction_lead_days <- function(physics_cycle, cfg) {
  pc <- toupper(physics_cycle)
  if (pc == "FORECAST") {
    ld <- cfg$prediction$lead_days %||% 1L
    return(as.integer(max(0L, min(3L, ld))))
  }
  0L
}

.prediction_from_wcofs_step <- function(
  forecast_age_hours = NULL,
  fallback_used = FALSE,
  lead_days_input = NULL,
  unknown_reason = NULL
) {
  if (is.null(forecast_age_hours) && (is.null(unknown_reason) || !nzchar(unknown_reason))) {
    return(NULL)
  }
  if (!is.null(unknown_reason) && nzchar(unknown_reason)) {
    return(list(
      evidence_state = "UNKNOWN",
      lead_days = 0L,
      unknown_reason = unknown_reason,
      forecast_age_hours = NA_real_
    ))
  }
  if (is.null(forecast_age_hours) || is.na(forecast_age_hours) || !is.finite(forecast_age_hours)) {
    return(list(
      evidence_state = "UNKNOWN",
      lead_days = 0L,
      unknown_reason = "missing_operational_cycle",
      forecast_age_hours = NA_real_
    ))
  }
  if (!is.null(lead_days_input) && !is.na(lead_days_input)) {
    ld_in <- suppressWarnings(as.integer(lead_days_input))
    if (is.na(ld_in) || ld_in < 0L) {
      stop(
        "invalid lead_days input ",
        lead_days_input,
        "; must be >= 0 (never -1 in prediction output)",
        call. = FALSE
      )
    }
  }
  age <- as.numeric(forecast_age_hours)
  fb <- isTRUE(fallback_used)
  if (!fb && age <= 0) {
    return(list(
      evidence_state = "NOWCAST",
      lead_days = 0L,
      unknown_reason = NA_character_,
      forecast_age_hours = age
    ))
  }
  if (fb) {
    ld <- as.integer(max(1L, ceiling(age / 24)))
  } else {
    ld <- as.integer(ceiling(age / 24))
  }
  list(
    evidence_state = "FORECAST",
    lead_days = max(0L, min(3L, ld)),
    unknown_reason = NA_character_,
    forecast_age_hours = age
  )
}

.prediction_wcofs_provenance_columns <- function(
  forecast_age_hours = NULL,
  fallback_used = FALSE,
  valid_time = NULL,
  source_run_time = NULL,
  wcofs_step = NULL
) {
  age <- forecast_age_hours
  if (!is.null(wcofs_step) && !is.null(wcofs_step$forecast_age_hours)) {
    age <- wcofs_step$forecast_age_hours
  }
  if (is.null(age)) {
    age <- NA_real_
  }
  list(
    forecast_age_hours = age,
    fallback_used = isTRUE(fallback_used),
    valid_time = valid_time %||% NA_character_,
    source_run_time = source_run_time %||% NA_character_
  )
}

.prediction_interval_widen_from_forecast_age <- function(forecast_age_hours, cfg) {
  pred <- cfg$prediction %||% list()
  per_24h <- pred$interval_widen_per_24h %||% 0.2
  base <- pred$interval_widen_base %||% 1.0
  age <- max(0, as.numeric(forecast_age_hours))
  base + per_24h * (age / 24)
}

.finalize_prediction_table <- function(
  agg,
  attr_cols,
  artifact,
  nsim,
  seed,
  vref,
  species = NA_character_,
  valid_day = NA_character_,
  dry_run = FALSE,
  lead_days = 0L,
  wcofs_provenance = list()
) {
  agg$species <- species
  agg$valid_day <- valid_day
  agg$dry_run <- isTRUE(dry_run)
  if (!"lead_days" %in% names(agg)) {
    agg$lead_days <- lead_days
  }
  agg$lead_days <- as.integer(pmax(0L, pmin(3L, agg$lead_days)))
  if (any(is.na(agg$lead_days))) {
    stop("lead_days must not be NA in prediction output", call. = FALSE)
  }
  if (!"unknown_reason" %in% names(agg)) {
    agg$unknown_reason <- NA_character_
  }
  if (!"p_lo90" %in% names(agg)) {
    agg$p_lo90 <- NA_real_
  }
  if (!"p_hi90" %in% names(agg)) {
    agg$p_hi90 <- NA_real_
  }
  prov <- wcofs_provenance %||% list()
  agg$forecast_age_hours <- prov$forecast_age_hours %||% NA_real_
  agg$fallback_used <- isTRUE(prov$fallback_used)
  agg$valid_time <- prov$valid_time %||% NA_character_
  agg$source_run_time <- prov$source_run_time %||% NA_character_
  agg$metadata_validated_forcing <- "glorys"
  agg$metadata_training_end <- artifact$training_end %||% NA_character_
  agg$metadata_nsim <- nsim
  agg$metadata_seed <- seed
  agg$reference_volume_m3 <- vref
  agg$metadata_encounter_effort_basis <- paste0(
    "egg encounter probability per ",
    format(vref, digits = 6),
    " m^3 filtered"
  )
  agg$metadata_attribution_training <- attr_cols$metadata_attribution_training
  agg$metadata_attribution_inference <- attr_cols$metadata_attribution_inference
  agg[, c(
    "cell_id",
    "species",
    "valid_day",
    "p_encounter",
    "p_lo90",
    "p_hi90",
    "expected_density",
    "ood_level",
    "evidence_state",
    "unknown_reason",
    "lead_days",
    "forecast_age_hours",
    "source_run_time",
    "fallback_used",
    "valid_time",
    "dry_run",
    "product_label",
    "reference_volume_m3",
    "metadata_encounter_effort_basis",
    "metadata_validated_forcing",
    "metadata_training_end",
    "metadata_attribution_training",
    "metadata_attribution_inference"
  )]
}

.unknown_prediction_table <- function(grid, ood_level, reason = "physics_cycle_fail") {
  agg <- stats::aggregate(
    ood_level ~ cell_id,
    cbind(grid, ood_level = ood_level),
    FUN = max
  )
  agg$p_encounter <- NA_real_
  agg$p_lo90 <- NA_real_
  agg$p_hi90 <- NA_real_
  agg$expected_density <- NA_real_
  agg$evidence_state <- "UNKNOWN"
  agg$unknown_reason <- reason
  agg$lead_days <- 0L
  agg$product_label <- "egg encounter (eggs sampled near 3 m depth along ship tracks)"
  agg
}
