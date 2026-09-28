#' Build identical delta formulas for both sdmTMB components.
#' @param formula_rhs Character RHS starting with ~ (shared smoothers required).
#' @return list of two formulas.
#' @export
build_delta_formula <- function(formula_rhs) {
  if (!grepl("^~", formula_rhs)) {
    formula_rhs <- paste("~", formula_rhs)
  }
  f <- stats::as.formula(paste("y", formula_rhs))
  list(f, f)
}

#' Assert delta formulas share the same smoother structure (sdmTMB requirement).
#' @export
assert_shared_delta_formula <- function(formula_list) {
  if (length(formula_list) != 2) {
    stop("delta formula must be length-2 list", call. = FALSE)
  }
  sm1 <- .extract_smooth_terms(formula_list[[1]])
  sm2 <- .extract_smooth_terms(formula_list[[2]])
  if (!identical(sm1, sm2)) {
    stop("delta smoothers must match between components: ", call. = FALSE)
  }
  invisible(TRUE)
}

.extract_smooth_terms <- function(f) {
  txt <- paste(deparse(f), collapse = " ")
  regmatches(txt, gregexpr("s\\([^\\)]+\\)", txt, perl = TRUE))[[1]]
}

.positive_component_sanity_ok <- function(fit) {
  if (isTRUE(getOption("fishai.test.force_positive_fallback", FALSE))) {
    return(FALSE)
  }
  if (!isTRUE(fit$converged)) {
    return(FALSE)
  }
  g <- fit$gradients
  if (length(g) && is.finite(max(abs(g), na.rm = TRUE))) {
    if (max(abs(g), na.rm = TRUE) > 0.001) {
      return(FALSE)
    }
  }
  ok <- tryCatch(
    {
      TMB::sdreport(fit$tmb_obj, getJointPrecision = TRUE)
      TRUE
    },
    error = function(e) FALSE
  )
  isTRUE(ok)
}

.positive_model_fallback_mode <- function(cfg) {
  cfg$model$positive_model_fallback %||% cfg$positive_model_fallback
}

#' @export
positive_component_sanity_ok <- function(fit) {
  .positive_component_sanity_ok(fit)
}

#' Fit delta GLMM with FishAI defaults (Poisson-link pilot).
#'
#' Effort is ``log(volume_m3)`` via ``offset = \"log_effort\"``. For
#' ``delta_* (type = \"poisson-link\")``, the offset enters **both** delta
#' linear predictors; encounter probability is ``1 - exp(-exp(eta))``. See
#' ``docs/CUFES_DELTA_MODEL_SPEC.md``.
#'
#' @export
fit_delta_engine <- function(dat, mesh, cfg) {
  .assert_training_covariate_table_from_cfg(cfg)
  cfg <- apply_model_cfg_patches(cfg, dat)
  prep <- .prepare_dat_for_fit_delta(dat, cfg)
  dat <- prep$data
  model <- cfg$model
  family <- resolve_delta_family(cfg)

  rhs <- model$formula_shared %||% model$formula_encounter
  frm <- build_delta_formula(rhs)
  assert_shared_delta_formula(frm)

  pc <- model$priors$pc_matern %||% list()
  range_gt <- (pc$range_gt_mult_max_edge %||% 2) * (cfg$mesh$cutoff_km %||% 9)
  pri <- sdmTMB::sdmTMBpriors(
    matern_s = sdmTMB::pc_matern(
      range_gt = range_gt,
      sigma_lt = pc$sigma_lt %||% 2
    ),
    matern_st = sdmTMB::pc_matern(
      range_gt = range_gt,
      sigma_lt = pc$sigma_lt %||% 2
    )
  )

  extra <- NULL
  if (!is.null(cfg$model$extra_time_slices)) {
    extra <- cfg$model$extra_time_slices
  }

  .as_pair <- function(x, default) {
    if (is.null(x)) {
      return(default)
    }
    if (is.list(x)) {
      return(x)
    }
    as.list(x)
  }

  fit <- sdmTMB::sdmTMB(
    formula = frm,
    data = dat,
    mesh = mesh,
    time = "time_idx",
    family = family,
    offset = "log_effort",
    spatial = .as_pair(model$spatial, list("on", "on")),
    spatiotemporal = .as_pair(model$spatiotemporal, list("ar1", "iid")),
    share_range = .as_pair(model$share_range, list(TRUE, TRUE)),
    time_varying = stats::as.formula(model$time_varying$formula %||% "~ 1"),
    time_varying_type = model$time_varying$type %||% "rw0",
    extra_time = extra,
    priors = pri,
    control = do.call(
      sdmTMB::sdmTMBcontrol,
      c(list(newton_loops = 1L, multiphase = TRUE), model$control %||% list())
    ),
    silent = TRUE
  )

  positive_fitted <- TRUE
  fallback_applied <- FALSE
  fallback_mode <- .positive_model_fallback_mode(cfg)
  if (
    identical(fallback_mode, "encounter_only") &&
      !.positive_component_sanity_ok(fit)
  ) {
    sp <- .as_pair(model$spatial, list("on", "on"))
    st <- .as_pair(model$spatiotemporal, list("ar1", "iid"))
    fit <- sdmTMB::sdmTMB(
      formula = frm,
      data = dat,
      mesh = mesh,
      time = "time_idx",
      family = family,
      offset = "log_effort",
      spatial = list(sp[[1L]], "off"),
      spatiotemporal = list(st[[1L]], "off"),
      share_range = .as_pair(model$share_range, list(TRUE, TRUE)),
      time_varying = stats::as.formula(model$time_varying$formula %||% "~ 1"),
      time_varying_type = model$time_varying$type %||% "rw0",
      extra_time = extra,
      priors = pri,
      control = do.call(
        sdmTMB::sdmTMBcontrol,
        c(list(newton_loops = 1L, multiphase = TRUE), model$control %||% list())
      ),
      silent = TRUE
    )
    positive_fitted <- FALSE
    fallback_applied <- TRUE
  }

  structure(
    list(
      fit = fit,
      delta_type = cfg$model$delta_type %||% "poisson-link",
      covariate_exclusion_summary = prep$exclusion_summary,
      covariate_dropped = prep$covariate_dropped %||% list(),
      source_product_counts = prep$source_product_counts,
      positive_component_fitted = positive_fitted,
      positive_model_fallback_applied = fallback_applied,
      positive_model_fallback = if (fallback_applied) fallback_mode else NULL
    ),
    class = "fishai_fit"
  )
}

#' @export
fit_uses_log_effort_offset <- function(fit_obj) {
  fit <- fit_obj$fit
  identical(as.character(fit$call$offset), "log_effort")
}
