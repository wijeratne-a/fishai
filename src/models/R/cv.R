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

.cv_spatial_reason_keys <- function() {
  c(
    "missing_endpoint",
    "land_mask",
    "too_few_track_points",
    "missing_covariate"
  )
}

.cv_spatial_preflight <- function(train, test, fold_id) {
  if (nrow(train) < 10L) {
    return(paste0("fold ", fold_id, ": training fold too small (n=", nrow(train), ")"))
  }
  if (nrow(test) < 2L) {
    return(paste0("fold ", fold_id, ": holdout fold too small (n=", nrow(test), ")"))
  }
  z_train <- as.integer(train$y > 0)
  z_test <- as.integer(test$y > 0)
  if (sum(z_train == 0L) < 1L || sum(z_train == 1L) < 1L) {
    return(paste0("fold ", fold_id, ": training fold lacks both zeros and positives"))
  }
  if (sum(z_test == 0L) < 1L || sum(z_test == 1L) < 1L) {
    return(paste0("fold ", fold_id, ": holdout fold lacks both zeros and positives"))
  }
  NULL
}

.cv_fit_failure_reason <- function(fishai_fit) {
  fit <- fishai_fit$fit
  obj <- fit$model$objective
  if (is.null(obj) || length(obj) != 1L || !is.finite(as.numeric(obj))) {
    return("non-finite objective")
  }
  if (isFALSE(fit$converged)) {
    return("non-converged")
  }
  if (isFALSE(fit$pos_def_hessian)) {
    return("non-positive-definite Hessian")
  }
  NULL
}

.cv_delta_holdout_loglik <- function(fishai_fit, test, cfg) {
  fit <- fishai_fit$fit
  if (!"log_effort" %in% names(test)) {
    stop("holdout data missing log_effort", call. = FALSE)
  }
  p <- score_encounter_on_events(fit, test, cfg)
  y <- as.numeric(test$y)
  z <- y > 0
  ll <- 0
  if (any(!z)) {
    ll <- ll + sum(log(pmax(1 - p[!z], .Machine$double.eps)))
  }
  if (any(z)) {
    ll <- ll + sum(log(pmax(p[z], .Machine$double.eps)))
    pos <- test[z, , drop = FALSE]
    pr <- stats::predict(fit, newdata = pos, model = 2L, offset = pos$log_effort)
    mu <- exp(as.numeric(pr$est2))
    ln_phi <- fit$par$ln_phi
    if (is.null(ln_phi)) {
      stop("missing ln_phi for positive-component log-likelihood", call. = FALSE)
    }
    shape <- exp(as.numeric(ln_phi)[1L])
    if (!is.finite(shape) || shape <= 0) {
      stop("invalid ln_phi for positive-component log-likelihood", call. = FALSE)
    }
    scale <- mu / shape
    ll <- ll + sum(stats::dgamma(pos$y, shape = shape, scale = scale, log = TRUE))
  }
  ll
}

.cv_fold_assignment_table <- function(dat, fold_ids) {
  block_id <- if ("block_id" %in% names(dat)) {
    as.character(dat$block_id)
  } else {
    rep(NA_character_, nrow(dat))
  }
  data.frame(
    event_id = as.character(dat$event_id),
    fold_id = as.integer(fold_ids),
    block_id = block_id,
    stringsAsFactors = FALSE
  )
}

#' Reason code when a spatial CV result may not enter ELPD selection.
#' @export
cv_elpd_ineligible_reason <- function(cv_obj) {
  if (is.null(cv_obj)) {
    return("cv_missing")
  }
  n_failed <- cv_obj$n_failed_folds %||% 0L
  if (n_failed > 0L) {
    failures <- unlist(cv_obj$fold_failures, use.names = FALSE)
    if (length(failures) && any(grepl("non-converged|non-positive-definite|gradient", failures, ignore.case = TRUE))) {
      return("cv_fold_nonconverged")
    }
    return("cv_fold_failed")
  }
  ll <- cv_obj$sum_loglik
  if (is.null(ll) || length(ll) != 1L || !is.finite(as.numeric(ll))) {
    return("cv_fold_failed")
  }
  fold_ll <- cv_obj$fold_loglik
  if (!is.null(fold_ll) && any(!is.finite(fold_ll))) {
    return("cv_fold_failed")
  }
  NULL
}

#' Spatial-block cross-validation with explicit fold IDs.
#' Failed folds are recorded (not fatal); see ``n_failed_folds`` and ``fold_failures``.
#' @export
run_cv_spatial <- function(dat, mesh, cfg, fold_ids) {
  .refuse_random_cv(fold_ids)
  dat$fold_id <- fold_ids
  .assert_cv_fold_assignment_contract(dat, fold_ids, cfg)
  spatial_meta <- spatial_block_cv_params(cfg)
  fold_assignment <- .cv_fold_assignment_table(dat, fold_ids)
  folds <- sort(unique(as.character(fold_ids)))
  fold_loglik <- stats::setNames(rep(NA_real_, length(folds)), folds)
  fold_failures <- list()

  for (fold_id in folds) {
    train <- dat[as.character(dat$fold_id) != fold_id, , drop = FALSE]
    test <- dat[as.character(dat$fold_id) == fold_id, , drop = FALSE]
    pre <- .cv_spatial_preflight(train, test, fold_id)
    if (!is.null(pre)) {
      fold_failures[[fold_id]] <- pre
      message("CV fold ", fold_id, " failed: ", pre)
      next
    }
    train_mesh <- build_fishai_mesh(train, cfg$mesh)
    fit_res <- tryCatch(
      fit_delta_engine(train, train_mesh, cfg),
      error = function(e) {
        structure(list(message = conditionMessage(e)), class = "cv_fold_error")
      }
    )
    if (inherits(fit_res, "cv_fold_error")) {
      reason <- fit_res$message
      fold_failures[[fold_id]] <- reason
      message("CV fold ", fold_id, " failed: ", reason)
      next
    }
    fit_reason <- .cv_fit_failure_reason(fit_res)
    if (!is.null(fit_reason)) {
      fold_failures[[fold_id]] <- fit_reason
      message("CV fold ", fold_id, " failed: ", fit_reason)
      next
    }
    ll <- tryCatch(
      .cv_delta_holdout_loglik(fit_res, test, cfg),
      error = function(e) conditionMessage(e)
    )
    if (is.character(ll) && length(ll) == 1L) {
      fold_failures[[fold_id]] <- ll
      message("CV fold ", fold_id, " failed: ", ll)
      next
    }
    if (!is.finite(ll)) {
      reason <- "non-finite fold log-likelihood"
      fold_failures[[fold_id]] <- reason
      message("CV fold ", fold_id, " failed: ", reason)
      next
    }
    fold_loglik[[fold_id]] <- ll
  }

  n_failed <- length(fold_failures)
  sum_ll <- if (n_failed > 0L) NA_real_ else sum(fold_loglik)
  inel <- cv_elpd_ineligible_reason(
    list(
      n_failed_folds = n_failed,
      fold_failures = fold_failures,
      sum_loglik = sum_ll,
      fold_loglik = as.numeric(fold_loglik)
    )
  )

  structure(
    list(
      data = dat,
      fold_loglik = as.numeric(fold_loglik),
      sum_loglik = sum_ll,
      n_failed_folds = n_failed,
      fold_failures = fold_failures,
      fold_assignment = fold_assignment,
      spatial_block_cv = spatial_meta,
      elpd_eligible = is.null(inel),
      elpd_ineligible_reason = inel
    ),
    class = "fishai_cv_spatial"
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

#' Choose model with higher ELPD (sum_loglik) among eligible candidates only.
#' @export
select_by_elpd <- function(cv_results) {
  if (is.null(names(cv_results)) || !nzchar(names(cv_results)[1L])) {
    names(cv_results) <- paste0("candidate_", seq_along(cv_results))
  }
  report <- lapply(names(cv_results), function(nm) {
    x <- cv_results[[nm]]
    inel <- cv_elpd_ineligible_reason(x)
    list(
      candidate = nm,
      sum_loglik = x$sum_loglik %||% NA_real_,
      elpd_eligible = is.null(inel),
      elpd_ineligible_reason = inel
    )
  })
  eligible <- vapply(cv_results, function(x) is.null(cv_elpd_ineligible_reason(x)), logical(1))
  if (!any(eligible)) {
    stop(
      "elpd_all_candidates_ineligible: no candidate completed spatial CV without failed folds",
      call. = FALSE
    )
  }
  elpd <- vapply(cv_results[eligible], function(x) as.numeric(x$sum_loglik), numeric(1))
  best <- names(cv_results)[eligible][which.max(elpd)]
  structure(
    best,
    elpd_report = report,
    class = "fishai_elpd_selection"
  )
}

#' @export
refuse_random_cv <- function() {
  stop("sdmTMB_cv() defaults to random folds; always pass explicit fold_ids or lfo=TRUE.", call. = FALSE)
}
