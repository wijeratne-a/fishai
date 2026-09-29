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
#' @export
predict_engine <- function(
  artifact,
  grid,
  cfg,
  physics_cycle = "PASS",
  nsim = NULL,
  species = NA_character_,
  valid_day = NA_character_,
  dry_run = FALSE
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
      lead_days = 0L
    ))
  }

  cov_cols <- artifact$reference_cols
  ref <- artifact$reference
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
    mess_mask_below = cfg$ood$mess_mask_below %||% -20
  )

  if (toupper(physics_cycle) == "DEGRADED") {
    # keep computed ood_level; handled after aggregation
  }

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
  p_s <- encounter_probability(eta1, cfg = cfg)
  if (is.null(dim(p_s))) {
    p_s <- matrix(as.numeric(p_s), ncol = 1L)
  }
  mu_s <- exp(eta2)
  if (ncol(mu_s) == 1L && ncol(p_s) > 1L) {
    mu_s <- matrix(rep(mu_s[, 1L], ncol(p_s)), nrow = nrow(mu_s), ncol = ncol(p_s))
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
  agg$evidence_state <- .prediction_evidence_state(physics_cycle, cfg)
  agg$unknown_reason <- NA_character_
  agg$lead_days <- .prediction_lead_days(physics_cycle, cfg)
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
    agg$evidence_state <- "DEGRADED"
    w <- pred_cfg$interval_widen %||% 1.25
    agg$p_encounter <- pmin(1, agg$p_encounter * w)
    agg$p_lo90 <- pmin(1, agg$p_lo90 * w)
    agg$p_hi90 <- pmin(1, agg$p_hi90 * w)
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
    lead_days = agg$lead_days[1L]
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
  lead_days = 0L
) {
  agg$species <- species
  agg$valid_day <- valid_day
  agg$dry_run <- isTRUE(dry_run)
  if (!"lead_days" %in% names(agg)) {
    agg$lead_days <- lead_days
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
  agg$metadata_validated_forcing <- "glorys"
  agg$metadata_training_end <- artifact$training_end %||% NA_character_
  agg$metadata_nsim <- nsim
  agg$metadata_seed <- seed
  agg$reference_volume_m3 <- vref
  agg$metadata_encounter_effort_basis <- paste0(
    "encounter probability per ",
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
