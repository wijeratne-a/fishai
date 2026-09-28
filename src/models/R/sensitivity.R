#' Extract fixed-effect estimates for side-by-side sensitivity output.
#' @export
summarize_fit_coefficients <- function(fishai_fit) {
  fit <- fishai_fit$fit
  sm <- tryCatch(summary(fit), error = function(e) NULL)
  if (!is.null(sm) && !is.null(sm$coefficients) && "Estimate" %in% colnames(sm$coefficients)) {
    est <- sm$coefficients[, "Estimate"]
    return(stats::setNames(as.numeric(est), rownames(sm$coefficients)))
  }
  stats::setNames(as.numeric(fit$model$par), names(fit$model$par))
}

#' Fit + spatial CV summary for one modelling frame.
.sensitivity_fit_block <- function(dat, cfg) {
  mesh <- build_fishai_mesh_with_barrier(dat, cfg)
  fit <- fit_delta_engine(dat, mesh, cfg)
  fold_ids <- dat$fold_id
  cv <- NULL
  if (!is.null(fold_ids)) {
    cv <- run_cv_spatial(dat, mesh, cfg, fold_ids)
  }
  vref <- compute_reference_volume_metadata(dat, cfg)
  list(
    n_events = nrow(dat),
    reference_volume_m3 = vref$reference_volume_m3,
    reference_volume_n_events = vref$source$n_events_fitting_frame,
    coefficients = summarize_fit_coefficients(fit),
    cv_spatial_sum_loglik = if (!is.null(cv)) cv$sum_loglik else NA_real_
  )
}

#' Compare full fit vs min-duration filtered refit (coefficients + CV side by side).
#' @export
compare_duration_sensitivity <- function(cfg, min_duration_min) {
  if (is.null(min_duration_min) || !is.finite(min_duration_min)) {
    stop("min_duration_min is required", call. = FALSE)
  }
  dat_full <- load_model_data(cfg = cfg)
  dat_filt <- load_model_data(cfg = cfg, min_duration_min = min_duration_min)
  list(
    min_duration_min = min_duration_min,
    taxon = cfg$species$taxon,
    full = c(
      .sensitivity_fit_block(dat_full, cfg),
      list(qc = fishai_data_prep_qc(dat_full))
    ),
    duration_filtered = c(
      .sensitivity_fit_block(dat_filt, cfg),
      list(qc = fishai_data_prep_qc(dat_filt))
    )
  )
}

#' Write sensitivity comparison JSON next to model artifacts.
#' @export
write_duration_sensitivity_report <- function(comparison, cfg) {
  out_dir <- cfg$output$dir %||% "artifacts/models"
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
  path <- file.path(out_dir, "duration_sensitivity.json")
  jsonlite::write_json(comparison, path, auto_unbox = TRUE, pretty = TRUE, null = "null")
  invisible(path)
}

.parse_model_cli_args <- function(args) {
  if (length(args) < 1L) {
    stop("config path required", call. = FALSE)
  }
  config <- args[[1L]]
  min_duration_min <- NULL
  if (length(args) > 1L) {
    for (a in args[-1L]) {
      if (grepl("^--min-duration-min=", a, fixed = TRUE)) {
        min_duration_min <- as.numeric(sub("^--min-duration-min=", "", a, fixed = TRUE))
      }
    }
  }
  list(config = config, min_duration_min = min_duration_min)
}
