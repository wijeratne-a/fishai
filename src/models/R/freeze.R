#' Median training volume and provenance for map reference offset.
#' @export
compute_reference_volume_metadata <- function(training_dat, cfg) {
  col <- cfg$response$effort_column %||% "volume_m3"
  if (!col %in% names(training_dat)) {
    stop("training data missing effort column: ", col, call. = FALSE)
  }
  vol <- as.numeric(training_dat[[col]])
  vol <- vol[is.finite(vol) & vol > 0]
  if (!length(vol)) {
    stop("no positive training volumes to define reference_volume_m3", call. = FALSE)
  }
  qs <- stats::quantile(vol, probs = c(0.1, 0.5, 0.9), na.rm = TRUE, names = FALSE)
  n_ev <- length(vol)
  list(
    reference_volume_m3 = unname(stats::median(vol, na.rm = TRUE)),
    source = list(
      n_events_fitting_frame = n_ev,
      n_events = n_ev,
      taxon = cfg$species$taxon %||% NA_character_,
      training_end = cfg$training_end %||% NA_character_,
      volume_m3_quantiles = stats::setNames(
        as.list(as.numeric(qs)),
        c("p10", "p50", "p90")
      )
    )
  )
}

#' Freeze fitted model artifact with config, renv hash, training source attributions, and V_ref.
#' @param training_dat Model-ready training table after [load_model_data()] QC.
#' @export
freeze_model <- function(fit_obj, cfg, path, training_dat = NULL, sources_manifest = NULL) {
  if (is.null(training_dat)) {
    stop("training_dat is required to compute reference_volume_m3", call. = FALSE)
  }
  ref_vol <- compute_reference_volume_metadata(training_dat, cfg)
  cfg <- cfg
  cfg$prediction <- cfg$prediction %||% list()
  cfg$prediction$reference_volume_m3 <- ref_vol$reference_volume_m3
  cfg$prediction$reference_volume_source <- ref_vol$source

  lock_hash <- digest_renv_lock()
  manifest <- sources_manifest %||% load_sources_manifest()
  training_sources <- training_sources_metadata(cfg, manifest = manifest)
  artifact <- list(
    fit = fit_obj$fit,
    config = cfg,
    renv_hash = lock_hash,
    training_end = cfg$training_end %||% NA_character_,
    reference = cfg$reference %||% NULL,
    reference_cols = cfg$reference_cols %||% NULL,
    harmonization = cfg$harmonization %||% NULL,
    training_sources = training_sources,
    reference_volume = ref_vol,
    frozen_at = format(Sys.time(), tz = "UTC", usetz = TRUE)
  )
  saveRDS(artifact, path)
  invisible(artifact)
}

digest_renv_lock <- function() {
  lock <- "renv.lock"
  if (!file.exists(lock)) {
    return(NA_character_)
  }
  as.character(tools::md5sum(lock))
}

#' Score frozen model exactly once on held-out data (per-event effort offsets).
#' @export
score_frozen_once <- function(artifact_path, holdout, scored_flag_path) {
  if (file.exists(scored_flag_path)) {
    stop("frozen model already scored once", call. = FALSE)
  }
  artifact <- readRDS(artifact_path)
  cfg <- artifact$config
  z <- as.integer(holdout$y > 0)
  p <- score_encounter_on_events(artifact$fit, holdout, cfg)
  out <- list(
    auc = auc_mw(z, p),
    brier = brier_score(z, p),
    n = nrow(holdout)
  )
  writeLines(as.character(Sys.time()), scored_flag_path)
  out
}

#' Re-score frozen model under perturbed covariates (degraded forcing harness).
#' @export
degraded_forcing_rescore <- function(artifact_path, holdout, bias_table) {
  artifact <- readRDS(artifact_path)
  cfg <- artifact$config
  pert <- holdout
  for (nm in names(bias_table)) {
    if (nm %in% names(pert)) {
      pert[[nm]] <- pert[[nm]] + bias_table[[nm]]
    }
  }
  z <- as.integer(holdout$y > 0)
  p_base <- score_encounter_on_events(artifact$fit, holdout, cfg)
  p_deg <- score_encounter_on_events(artifact$fit, pert, cfg)
  list(
    auc_base = auc_mw(z, p_base),
    auc_degraded = auc_mw(z, p_deg),
    skill_drop = auc_mw(z, p_base) - auc_mw(z, p_deg)
  )
}
