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
predict_engine <- function(artifact, grid, cfg, physics_cycle = "PASS", nsim = NULL) {
  attr_meta <- assert_prediction_attributions(
    prediction_attribution_metadata(artifact, cfg)
  )
  attr_cols <- .flatten_attributions_for_columns(attr_meta)
  vref <- assert_reference_volume(artifact)

  harmonize_bundle <- NULL
  hcfg <- NULL
  if (.inference_requires_harmonization(cfg)) {
    harmonize_bundle <- assert_harmonization_for_predict(artifact, cfg)
    hcfg <- load_harmonize_config(cfg$harmonization$config_path %||% NULL)
    grid <- harmonize_inference_grid(grid, harmonize_bundle, hcfg)
  }

  fit <- artifact$fit
  pred_cfg <- cfg$prediction %||% list()
  nsim <- nsim %||% pred_cfg$nsim %||% 500L
  seed <- pred_cfg$seed %||% 20260928L
  off <- reference_volume_offset(artifact, nrow(grid))

  cov_cols <- artifact$reference_cols
  ref <- artifact$reference
  if (!is.null(harmonize_bundle)) {
    ood_level <- harmonize_envelope_ood(grid, ref, cov_cols, cfg)
    for (col in cov_cols) {
      bad <- !is.finite(grid[[col]])
      if (any(bad)) {
        grid[[col]][bad] <- stats::median(ref[[col]], na.rm = TRUE)
      }
    }
  } else {
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
  }

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
    return(.finalize_prediction_table(
      .unknown_prediction_table(grid, ood_level),
      attr_cols,
      artifact,
      nsim,
      seed,
      vref
    ))
  }

  set.seed(seed)
  eta1_raw <- stats::predict(fit, newdata = grid, nsim = nsim, model = 1)
  eta1 <- sweep(eta1_raw, 1L, off, "+")
  set.seed(seed)
  eta2 <- stats::predict(fit, newdata = grid, nsim = nsim, model = 2, offset = off)
  p_s <- encounter_probability(eta1, cfg = cfg)
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

  .finalize_prediction_table(agg, attr_cols, artifact, nsim, seed, vref)
}

.finalize_prediction_table <- function(agg, attr_cols, artifact, nsim, seed, vref) {
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
    "p_encounter",
    "expected_density",
    "ood_level",
    "evidence_state",
    "product_label",
    "reference_volume_m3",
    "metadata_encounter_effort_basis",
    "metadata_validated_forcing",
    "metadata_training_end",
    "metadata_attribution_training",
    "metadata_attribution_inference"
  )]
}

.unknown_prediction_table <- function(grid, ood_level) {
  agg <- stats::aggregate(
    ood_level ~ cell_id,
    cbind(grid, ood_level = ood_level),
    FUN = max
  )
  agg$p_encounter <- NA_real_
  agg$expected_density <- NA_real_
  agg$evidence_state <- "Unknown"
  agg$product_label <- "egg encounter (eggs sampled near 3 m depth along ship tracks)"
  agg
}
