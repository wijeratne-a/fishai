#' Freeze fitted model artifact with config, renv hash, and training source attributions.
#' @export
freeze_model <- function(fit_obj, cfg, path, sources_manifest = NULL) {
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
    training_sources = training_sources,
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

#' Score frozen model exactly once on held-out data.
#' @export
score_frozen_once <- function(artifact_path, holdout, scored_flag_path) {
  if (file.exists(scored_flag_path)) {
    stop("frozen model already scored once", call. = FALSE)
  }
  artifact <- readRDS(artifact_path)
  z <- as.integer(holdout$y > 0)
  p <- stats::predict(artifact$fit, newdata = holdout)$est1
  p <- 1 / (1 + exp(-p))
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
  pert <- holdout
  for (nm in names(bias_table)) {
    if (nm %in% names(pert)) {
      pert[[nm]] <- pert[[nm]] + bias_table[[nm]]
    }
  }
  z <- as.integer(holdout$y > 0)
  p_base <- 1 / (1 + exp(-stats::predict(artifact$fit, newdata = holdout)$est1))
  p_deg <- 1 / (1 + exp(-stats::predict(artifact$fit, newdata = pert)$est1))
  list(
    auc_base = auc_mw(z, p_base),
    auc_degraded = auc_mw(z, p_deg),
    skill_drop = auc_mw(z, p_base) - auc_mw(z, p_deg)
  )
}
