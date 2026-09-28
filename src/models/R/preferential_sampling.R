#' Pre-fit preferential-sampling diagnostic (covariate-only GLMs, no spatial field).
#'
#' Per cruise, event counts in 10 km EPSG:32611 cells define sampling intensity.
#' Spearman correlation with mean combined GLM residuals; cell-block bootstrap CI.

#' @export
cufes_cruise_from_event_id <- function(event_id) {
  eid <- as.character(event_id)
  vapply(
    strsplit(eid, ":", fixed = TRUE),
    function(parts) {
      if (length(parts) < 4L) {
        return(NA_character_)
      }
      parts[[2L]]
    },
    character(1L)
  )
}

#' @export
ten_km_cell_id_utm <- function(x_km, y_km, cell_size_km = 10) {
  bx <- floor(as.numeric(x_km) / cell_size_km)
  by <- floor(as.numeric(y_km) / cell_size_km)
  paste0("bx", bx, "_by", by)
}

.covariate_only_glm_rhs <- function(dat, cfg) {
  cols <- .model_covariate_columns(cfg)
  present <- cols[cols %in% names(dat)]
  if (!length(present)) {
    return(~1)
  }
  stats::as.formula(paste("~", paste(present, collapse = " + ")))
}

.combined_glm_pearson_residuals <- function(dat, cfg) {
  if (!all(c("y", "log_effort") %in% names(dat))) {
    stop("dat needs y and log_effort for preferential-sampling GLMs", call. = FALSE)
  }
  rhs <- .covariate_only_glm_rhs(dat, cfg)
  dat$y_pos <- as.integer(dat$y > 0)
  enc_f <- stats::update.formula(rhs, y_pos ~ .)
  enc <- stats::glm(
    enc_f,
    data = dat,
    family = stats::binomial(),
    offset = log_effort
  )
  enc_res <- stats::residuals(enc, type = "pearson")
  out <- enc_res
  pos_idx <- which(dat$y > 0)
  if (length(pos_idx)) {
    pos_dat <- dat[pos_idx, , drop = FALSE]
    pos_f <- stats::update.formula(rhs, y ~ .)
    pos <- stats::glm(
      pos_f,
      data = pos_dat,
      family = stats::Gamma(link = "log"),
      offset = log_effort
    )
    pos_res <- stats::residuals(pos, type = "pearson")
    out[pos_idx] <- enc_res[pos_idx] + pos_res
  }
  out
}

.spearman_block_bootstrap_ci <- function(x, y, n_boot, seed) {
  if (length(x) < 3L) {
    return(list(rho = NA_real_, ci_low = NA_real_, ci_high = NA_real_))
  }
  rho <- stats::cor(x, y, method = "spearman", use = "complete.obs")
  if (!is.finite(rho)) {
    return(list(rho = NA_real_, ci_low = NA_real_, ci_high = NA_real_))
  }
  n <- length(x)
  set.seed(seed)
  boots <- numeric(n_boot)
  for (b in seq_len(n_boot)) {
    idx <- sample.int(n, n, replace = TRUE)
    boots[[b]] <- stats::cor(x[idx], y[idx], method = "spearman", use = "complete.obs")
  }
  qs <- stats::quantile(boots, probs = c(0.025, 0.975), na.rm = TRUE, names = FALSE)
  list(rho = rho, ci_low = qs[[1L]], ci_high = qs[[2L]])
}

#' @export
run_preferential_sampling_diagnostic <- function(cfg, dat = NULL) {
  block <- cfg$diagnostics$preferential_sampling
  if (is.null(block)) {
    stop("diagnostics.preferential_sampling block is required", call. = FALSE)
  }
  cell_km <- block$cell_size_km %||% 10
  n_boot <- as.integer(block$bootstrap_replicates %||% 500L)
  seed <- cfg$prediction$seed %||% 1L
  if (is.null(dat)) {
    dat <- load_model_data(cfg = cfg)
  }
  if (!all(c("X", "Y", "event_id") %in% names(dat))) {
    stop("dat needs X, Y, event_id (EPSG:32611 km)", call. = FALSE)
  }
  taxon <- cfg$species$taxon %||% cfg$species$code %||% "unknown"
  dat$cruise <- cufes_cruise_from_event_id(dat$event_id)
  dat$cell_10km <- ten_km_cell_id_utm(dat$X, dat$Y, cell_size_km = cell_km)
  dat$resid <- .combined_glm_pearson_residuals(dat, cfg)
  agg <- stats::aggregate(
    list(mean_residual = dat$resid),
    by = list(cruise = dat$cruise, cell_10km = dat$cell_10km),
    FUN = mean,
    na.rm = TRUE
  )
  counts <- stats::aggregate(
    list(sampling_intensity = dat$event_id),
    by = list(cruise = dat$cruise, cell_10km = dat$cell_10km),
    FUN = length
  )
  merged <- merge(agg, counts, by = c("cruise", "cell_10km"), all = TRUE)
  merged <- merged[is.finite(merged$mean_residual) & is.finite(merged$sampling_intensity), , drop = FALSE]
  boot <- .spearman_block_bootstrap_ci(
    merged$sampling_intensity,
    merged$mean_residual,
    n_boot = n_boot,
    seed = as.integer(seed)
  )
  flag <- is.finite(boot$ci_low) && is.finite(boot$ci_high) &&
    (boot$ci_low > 0 || boot$ci_high < 0)
  list(
    species_taxon = taxon,
    cell_size_km = cell_km,
    epsg = 32611L,
    spearman_rho = boot$rho,
    bootstrap_ci_95 = c(boot$ci_low, boot$ci_high),
    flag_preferential = isTRUE(flag),
    n_cruise_cell_units = nrow(merged),
    n_events = nrow(dat)
  )
}

#' @export
write_preferential_sampling_json <- function(result, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  jsonlite::write_json(result, path, auto_unbox = TRUE, pretty = TRUE)
  invisible(path)
}
