#' Drop configured covariates when entirely unavailable (fit time only).
#'
#' Pilot: ``upwelling`` may be blank for all kept rows with
#' ``excluded_reason == no_consistent_wind_product`` without ``excluded == TRUE``.
#' @keywords internal
.no_consistent_wind_product_reason <- function() {
  "no_consistent_wind_product"
}

.drop_covariates_if_unavailable_slugs <- function(cfg) {
  slugs <- cfg$drop_covariates_if_unavailable %||%
    cfg$model$drop_covariates_if_unavailable %||%
    character()
  unique(as.character(slugs))
}

.covariate_upstream_column <- function(slug, cfg) {
  upstream_map <- cfg$covariates$upstream_fields %||% .default_upstream_covariate_map()
  col <- upstream_map[[slug]]
  if (is.null(col) || !nzchar(col)) {
    stop("unknown drop_covariates_if_unavailable slug: ", slug, call. = FALSE)
  }
  unname(col)
}

.covariate_values_blank <- function(vals) {
  if (is.character(vals)) {
    return(is.na(vals) | !nzchar(trimws(vals)))
  }
  num <- suppressWarnings(as.numeric(vals))
  is.na(vals) | !is.finite(num)
}

.strip_covariate_smoother_from_formula <- function(rhs, slug) {
  if (is.null(rhs) || !nzchar(rhs)) {
    return(rhs)
  }
  pat <- paste0("\\+?\\s*s\\(", slug, "_z[^\\)]*\\)")
  new_rhs <- gsub(pat, "", rhs, perl = TRUE)
  new_rhs <- gsub("\\+\\s*\\+", "+", new_rhs, perl = TRUE)
  new_rhs <- gsub("~\\s*\\+", "~ ", new_rhs, perl = TRUE)
  trimws(new_rhs)
}

.patch_cfg_drop_covariate_slug <- function(cfg, slug, reason) {
  cfg_out <- cfg
  cov <- cfg$covariates
  cov$dynamic <- setdiff(cov$dynamic %||% character(), slug)
  dropped <- cov$dropped_if_unavailable %||% list()
  dropped[[length(dropped) + 1L]] <- list(covariate = slug, reason = reason)
  cov$dropped_if_unavailable <- dropped
  cfg_out$covariates <- cov
  model <- cfg$model %||% list()
  for (field in c("formula_shared", "formula_encounter")) {
    if (!is.null(model[[field]])) {
      model[[field]] <- .strip_covariate_smoother_from_formula(model[[field]], slug)
    }
  }
  cfg_out$model <- model
  cfg_out
}

#' Resolve ``drop_covariates_if_unavailable`` against kept fit rows.
#'
#' Returns an updated config copy; callers must merge via [sync_cfg_covariate_drop_state()].
#' @export
apply_drop_covariates_if_unavailable <- function(dat, cfg) {
  slugs <- .drop_covariates_if_unavailable_slugs(cfg)
  if (!length(slugs)) {
    return(list(data = dat, cfg = cfg, dropped = list()))
  }
  cfg_out <- cfg
  dyn <- cfg_out$covariates$dynamic %||% character()
  dropped <- list()
  for (slug in slugs) {
    if (!slug %in% dyn) {
      next
    }
    if (!identical(slug, "upwelling")) {
      stop(
        "drop_covariates_if_unavailable only implements upwelling; got: ",
        slug,
        call. = FALSE
      )
    }
    col <- .covariate_upstream_column(slug, cfg_out)
    if (!col %in% names(dat)) {
      stop(
        "drop_covariates_if_unavailable requires column ",
        col,
        " on fit rows",
        call. = FALSE
      )
    }
    vals <- dat[[col]]
    blank <- .covariate_values_blank(vals)
    if (!any(blank)) {
      next
    }
    if (!all(blank)) {
      ids <- as.character(dat$event_id[blank])
      stop(
        "partially blank ",
        col,
        " (never impute or drop rows); blank event_id: ",
        paste(head(ids, 10L), collapse = ", "),
        if (sum(blank) > 10L) " ..." else "",
        call. = FALSE
      )
    }
    reason_col <- "excluded_reason"
    if (!reason_col %in% names(dat)) {
      stop(
        "all ",
        col,
        " blank but excluded_reason column missing",
        call. = FALSE
      )
    }
    reasons <- trimws(as.character(dat[[reason_col]]))
    want <- .no_consistent_wind_product_reason()
    bad_reason <- is.na(reasons) | !nzchar(reasons) | reasons != want
    if (any(bad_reason)) {
      stop(
        "all ",
        col,
        " blank requires excluded_reason=",
        want,
        " on every kept row (never impute or drop rows)",
        call. = FALSE
      )
    }
    cfg_out <- .patch_cfg_drop_covariate_slug(cfg_out, slug, want)
    dyn <- cfg_out$covariates$dynamic
    dropped[[length(dropped) + 1L]] <- list(covariate = slug, reason = want)
    message("covariate_dropped: ", slug, ", reason: ", want)
  }
  list(data = dat, cfg = cfg_out, dropped = dropped)
}

#' Merge covariate-drop patches from [apply_drop_covariates_if_unavailable()] into live config.
#' @export
sync_cfg_covariate_drop_state <- function(cfg, resolved_cfg) {
  if (length(resolved_cfg$covariates$dropped_if_unavailable %||% list())) {
    cfg$covariates <- resolved_cfg$covariates
    cfg$model <- resolved_cfg$model
  }
  invisible(cfg)
}

.sync_cfg_covariate_drop_state <- sync_cfg_covariate_drop_state

#' Apply ``fishai_cfg_patches`` from [load_model_data()] onto a model config copy for fit.
#' @export
apply_model_cfg_patches <- function(cfg, dat) {
  patches <- attr(dat, "fishai_cfg_patches")
  if (is.null(patches)) {
    return(cfg)
  }
  cfg$covariates <- patches$covariates
  cfg$model <- patches$model
  cfg
}
