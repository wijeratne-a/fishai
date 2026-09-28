#' Predict egg encounter surfaces with coupled posterior draws.
#'
#' Aggregates to 10 km grid cells before summarizing. Outputs exclude point
#' coordinates (cell identifiers only). Labels describe **egg encounter**
#' evidence, not adult fish distribution.
#'
#' @export
predict_engine <- function(artifact, grid, cfg, physics_cycle = "PASS", nsim = NULL) {
  fit <- artifact$fit
  pred_cfg <- cfg$prediction %||% list()
  nsim <- nsim %||% pred_cfg$nsim %||% 500L
  seed <- pred_cfg$seed %||% 20260928L
  ref_effort <- pred_cfg$reference_effort %||% 1
  grid$log_effort <- log(ref_effort)

  cov_cols <- artifact$reference_cols
  ref <- artifact$reference
  mess <- mess_scores(grid[, cov_cols, drop = FALSE], ref)
  ex <- exdet_scores(grid[, cov_cols, drop = FALSE], ref)
  maha <- maha_distance(grid[, cov_cols, drop = FALSE], ref)
  hull <- convex_hull_flags(
    grid[, cov_cols, drop = FALSE],
    ref,
    pairs = cfg$ood$hull_pairs %||% list(c("sst_z", "sal_z"))
  )
  ood_level <- classify_ood_level(
    mess$mess,
    ex$nt1,
    ex$nt2,
    maha,
    hull,
    mess_mask_below = cfg$ood$mess_mask_below %||% -20
  )

  if (toupper(physics_cycle) == "FAIL") {
    ood_level[] <- 3L
  }

  grid$cell_id <- paste0(
    "g",
    floor(grid$X / 10),
    "_",
    floor(grid$Y / 10)
  )

  if (toupper(physics_cycle) == "FAIL") {
    return(.unknown_prediction_table(grid, ood_level, artifact, cfg, degraded = FALSE))
  }

  set.seed(seed)
  eta1 <- stats::predict(fit, newdata = grid, nsim = nsim, model = 1)
  set.seed(seed)
  eta2 <- stats::predict(
    fit,
    newdata = grid,
    nsim = nsim,
    model = 2,
    offset = rep(log(ref_effort), nrow(grid))
  )
  p_s <- 1 / (1 + exp(-eta1))
  mu_s <- exp(eta2)
  d_s <- p_s * mu_s

  grid$draw_p_mean <- rowMeans(p_s)
  grid$draw_d_mean <- rowMeans(d_s)

  agg <- stats::aggregate(
    cbind(draw_p_mean, draw_d_mean) ~ cell_id,
    data = grid,
    FUN = mean
  )

  agg$ood_level <- stats::aggregate(ood_level ~ cell_id, grid, FUN = max)$ood_level
  agg$evidence_state <- "Current Nowcast, unvalidated under operational forcing"
  agg$product_label <- "egg encounter (eggs sampled near 3 m depth along ship tracks)"
  agg$p_encounter <- agg$draw_p_mean
  agg$expected_density <- agg$draw_d_mean

  agg$p_encounter[agg$ood_level >= 2L] <- NA_real_
  agg$expected_density[agg$ood_level >= 2L] <- NA_real_
  agg$evidence_state[agg$ood_level >= 2L] <- "Unknown"

  if (toupper(physics_cycle) == "DEGRADED") {
    agg$evidence_state <- "DEGRADED"
    w <- pred_cfg$interval_widen %||% 1.25
    agg$p_encounter <- pmin(1, agg$p_encounter * w)
  }

  agg$metadata_validated_forcing <- "glorys"
  agg$metadata_training_end <- artifact$training_end %||% NA_character_
  agg$metadata_nsim <- nsim
  agg$metadata_seed <- seed
  agg[, c(
    "cell_id",
    "p_encounter",
    "expected_density",
    "ood_level",
    "evidence_state",
    "product_label",
    "metadata_validated_forcing",
    "metadata_training_end"
  )]
}

.unknown_prediction_table <- function(grid, ood_level, artifact, cfg, degraded) {
  agg <- stats::aggregate(
    ood_level ~ cell_id,
    cbind(grid, ood_level = ood_level),
    FUN = max
  )
  agg$p_encounter <- NA_real_
  agg$expected_density <- NA_real_
  agg$evidence_state <- "Unknown"
  agg$product_label <- "egg encounter (eggs sampled near 3 m depth along ship tracks)"
  agg$metadata_validated_forcing <- "glorys"
  agg$metadata_training_end <- artifact$training_end %||% NA_character_
  agg
}
