#' Resolve sdmTMB delta family from config (CUFES default: poisson-link).
#' @export
resolve_delta_family <- function(cfg) {
  model <- cfg$model
  delta_type <- model$delta_type %||% "poisson-link"
  switch(
    model$family %||% "delta_gamma",
    delta_gamma = if (delta_type == "poisson-link") {
      sdmTMB::delta_gamma(type = "poisson-link")
    } else {
      sdmTMB::delta_gamma()
    },
    delta_lognormal = if (delta_type == "poisson-link") {
      sdmTMB::delta_lognormal(type = "poisson-link")
    } else {
      sdmTMB::delta_lognormal()
    },
    stop("unsupported family: ", model$family, call. = FALSE)
  )
}

#' @export
is_poisson_link_delta <- function(cfg) {
  identical(cfg$model$delta_type %||% "poisson-link", "poisson-link")
}

#' Encounter probability from delta component-1 linear predictor.
#'
#' Poisson-link (Thorson): \eqn{p = 1 - \exp(-\exp(\eta))} with \eqn{\eta} including
#' \eqn{\log(V)} offset. Standard delta uses logistic on \eqn{\eta}.
#' @export
encounter_probability <- function(eta, cfg = NULL, poisson_link = NULL) {
  pl <- poisson_link
  if (is.null(pl) && !is.null(cfg)) {
    pl <- is_poisson_link_delta(cfg)
  }
  if (is.null(pl)) {
    pl <- TRUE
  }
  eta <- as.numeric(eta)
  if (pl) {
    return(1 - exp(-exp(eta)))
  }
  1 / (1 + exp(-eta))
}

#' Log offset vector for map prediction from frozen artifact config.
#' @export
reference_volume_offset <- function(artifact, n) {
  vref <- artifact$config$prediction$reference_volume_m3
  if (is.null(vref) || !is.finite(vref) || vref <= 0) {
    stop("frozen artifact missing prediction.reference_volume_m3", call. = FALSE)
  }
  rep(log(vref), n)
}

#' @export
assert_reference_volume <- function(artifact) {
  vref <- artifact$config$prediction$reference_volume_m3
  if (is.null(vref) || !is.finite(vref) || vref <= 0) {
    stop("reference_volume_m3 missing from frozen config; refreeze with training data", call. = FALSE)
  }
  invisible(vref)
}
