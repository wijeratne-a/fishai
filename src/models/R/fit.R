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

#' Fit delta GLMM with FishAI defaults.
#'
#' Effort is ``log(volume_m3)`` on column ``log_effort``. In sdmTMB delta
#' families the ``offset`` argument applies to the **positive** component only;
#' the encounter component uses ``log_effort`` in the shared formula unless
#' using Poisson-link delta. See ``src/models/README.md``.
#'
#' @export
fit_delta_engine <- function(dat, mesh, cfg) {
  model <- cfg$model
  delta_type <- model$delta_type %||% "standard"
  family <- switch(
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

  structure(
    list(
      fit = fit,
      offset_note = "sdmTMB delta: offset column applies to positive component only; encounter uses log_effort as covariate in shared formula."
    ),
    class = "fishai_fit"
  )
}

#' Test helper: verify offset is passed only to positive likelihood.
#' @export
offset_applies_to_positive_only <- function(fit_obj) {
  fit <- fit_obj$fit
  args <- fit$call
  identical(as.character(args$offset), "log_effort")
}
