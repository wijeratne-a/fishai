.refuse_random_cv <- function(fold_ids) {
  if (is.null(fold_ids)) {
    stop("random CV folds are forbidden; supply explicit spatial or LFO fold_ids.", call. = FALSE)
  }
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

#' Spatial-block cross-validation with explicit fold IDs.
#' @export
run_cv_spatial <- function(dat, mesh, cfg, fold_ids) {
  .refuse_random_cv(fold_ids)
  dat$fold_id <- fold_ids
  model <- cfg$model
  frm <- build_delta_formula(model$formula_shared %||% model$formula_encounter)
  assert_shared_delta_formula(frm)
  sdmTMB::sdmTMB_cv(
    formula = frm,
    data = dat,
    mesh = mesh,
    time = "time_idx",
    fold_ids = "fold_id",
    family = resolve_delta_family(cfg),
    offset = "log_effort",
    spatial = .as_pair(model$spatial, list("on", "on")),
    spatiotemporal = .as_pair(model$spatiotemporal, list("ar1", "iid")),
    share_range = .as_pair(model$share_range, list(TRUE, TRUE)),
    silent = TRUE
  )
}

#' Leave-future-out CV (explicit; never random folds).
#' @export
run_cv_lfo <- function(dat, mesh, cfg, lfo_forecast = 1L, lfo_validations = 3L) {
  model <- cfg$model
  frm <- build_delta_formula(model$formula_shared %||% model$formula_encounter)
  assert_shared_delta_formula(frm)
  sdmTMB::sdmTMB_cv(
    formula = frm,
    data = dat,
    mesh = mesh,
    time = "time_idx",
    lfo = TRUE,
    lfo_forecast = lfo_forecast,
    lfo_validations = lfo_validations,
    family = resolve_delta_family(cfg),
    offset = "log_effort",
    spatial = .as_pair(model$spatial, list("on", "on")),
    spatiotemporal = .as_pair(model$spatiotemporal, list("ar1", "iid")),
    share_range = .as_pair(model$share_range, list(TRUE, TRUE)),
    silent = TRUE
  )
}

#' Choose model with higher ELPD (sum_loglik).
#' @export
select_by_elpd <- function(cv_results) {
  elpd <- vapply(cv_results, function(x) x$sum_loglik, numeric(1))
  names(cv_results)[[which.max(elpd)]]
}

#' @export
refuse_random_cv <- function() {
  stop("sdmTMB_cv() defaults to random folds; always pass explicit fold_ids or lfo=TRUE.", call. = FALSE)
}
