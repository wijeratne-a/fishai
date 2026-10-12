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

.cv_binomial_holdout_loglik <- function(fishai_fit, test, cfg) {
  p <- score_encounter_binomial_on_events(fishai_fit$fit, test, cfg)
  z <- as.integer(test$y > 0)
  ll <- 0
  if (any(!z)) {
    ll <- ll + sum(log(pmax(1 - p[!z], .Machine$double.eps)))
  }
  if (any(z)) {
    ll <- ll + sum(log(pmax(p[z], .Machine$double.eps)))
  }
  ll
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

.cv_flag_any_not_true <- function(x) {
  if (is.null(x) || !is.atomic(x)) {
    return(FALSE)
  }
  x <- as.logical(x)
  length(x) > 0L && any(!x %in% TRUE)
}

#' Reason code when a CV result may not enter ELPD selection.
#' Failed, non-converged, non-PD, or non-finite runs are ineligible even when
#' ``sum_loglik`` is finite (a partial sum must not win ``which.max``).
#' @export
cv_elpd_ineligible_reason <- function(cv_obj) {
  if (is.null(cv_obj)) {
    return("cv_missing")
  }
  if (isFALSE(cv_obj$elpd_eligible)) {
    reason <- cv_obj$elpd_ineligible_reason
    if (is.null(reason) || !nzchar(as.character(reason)[1L])) {
      return("cv_fold_failed")
    }
    return(as.character(reason)[1L])
  }
  n_failed <- cv_obj$n_failed_folds %||% 0L
  if (n_failed > 0L) {
    failures <- unlist(cv_obj$fold_failures, use.names = FALSE)
    if (length(failures) && any(grepl("non-converged|non-positive-definite|gradient", failures, ignore.case = TRUE))) {
      return("cv_fold_nonconverged")
    }
    return("cv_fold_failed")
  }
  if (.cv_flag_any_not_true(cv_obj$converged) || .cv_flag_any_not_true(cv_obj$pdHess)) {
    return("cv_fold_nonconverged")
  }
  ll <- cv_obj$sum_loglik
  if (is.null(ll) || length(ll) != 1L || !is.finite(as.numeric(ll))) {
    return("cv_fold_failed")
  }
  fold_ll <- cv_obj$fold_loglik
  if (!is.null(fold_ll) && any(!is.finite(as.numeric(fold_ll)))) {
    return("cv_fold_failed")
  }
  NULL
}

.fold_assignment_key <- function(tab) {
  req <- c("event_id", "fold_id", "block_id")
  if (is.null(tab) || !all(req %in% names(tab))) {
    return(NA_character_)
  }
  tab <- data.frame(
    event_id = as.character(tab$event_id),
    fold_id = as.integer(tab$fold_id),
    block_id = as.character(tab$block_id),
    stringsAsFactors = FALSE
  )
  tab <- tab[order(tab$event_id, tab$block_id), , drop = FALSE]
  paste(tab$event_id, tab$fold_id, tab$block_id, sep = "\t", collapse = "\n")
}

#' One TMB/OpenMP thread per fit so forked fold workers do not share a pool.
.cv_limit_tmb_threads <- function() {
  Sys.setenv(
    OMP_NUM_THREADS = "1",
    MKL_NUM_THREADS = "1",
    OPENBLAS_NUM_THREADS = "1",
    VECLIB_MAXIMUM_THREADS = "1"
  )
  if (requireNamespace("TMB", quietly = TRUE)) {
    tryCatch(TMB::openmp(n = 1L), error = function(e) NULL)
  }
  if (requireNamespace("RhpcBLASctl", quietly = TRUE)) {
    tryCatch(RhpcBLASctl::blas_set_num_threads(1L), error = function(e) NULL)
    tryCatch(RhpcBLASctl::omp_set_num_threads(1L), error = function(e) NULL)
  }
  invisible(1L)
}

#' Fold-worker count: min(cores, 4), and never more workers than folds.
.cv_spatial_n_workers <- function(n_tasks, cores = parallel::detectCores(logical = TRUE)) {
  if (length(cores) != 1L || is.na(cores) || cores < 1L) {
    cores <- 1L
  }
  n_tasks <- max(1L, as.integer(n_tasks)[1L])
  as.integer(min(as.integer(cores), 4L, n_tasks))
}

.cv_empty_oof_predictions <- function() {
  data.frame(
    event_id = character(),
    fold_id = integer(),
    z = integer(),
    p = numeric(),
    stringsAsFactors = FALSE
  )
}

.cv_valid_oof_predictions <- function(oof, fold_id = NULL) {
  if (is.null(oof) || !is.data.frame(oof)) {
    return(FALSE)
  }
  if (!all(c("event_id", "fold_id", "z", "p") %in% names(oof))) {
    return(FALSE)
  }
  if (!nrow(oof)) {
    return(TRUE)
  }
  p <- suppressWarnings(as.numeric(oof$p))
  if (length(p) != nrow(oof) || any(!is.finite(p)) || any(p < 0) || any(p > 1)) {
    return(FALSE)
  }
  if (!is.null(fold_id) && any(as.character(oof$fold_id) != as.character(fold_id))) {
    return(FALSE)
  }
  TRUE
}

#' A fold result is usable only when it is the structured list produced by
#' .cv_spatial_one_fold(). Forked workers killed by the OOM killer can hand
#' back atomic or otherwise malformed values; dereferencing fields on those
#' values used to crash the collector with "$ operator is invalid for atomic
#' vectors" and lose every completed fold.
.cv_valid_fold_result <- function(res, fold_id) {
  if (is.null(res) || !is.list(res) || inherits(res, "try-error")) {
    return(FALSE)
  }
  if (!all(c("fold_id", "failure", "loglik", "barrier_stop") %in% names(res))) {
    return(FALSE)
  }
  if (!identical(as.character(res$fold_id)[1L], as.character(fold_id)[1L])) {
    return(FALSE)
  }
  if (!is.null(res$barrier_stop)) {
    return(TRUE)
  }
  if (!is.null(res$failure)) {
    return(length(res$loglik) == 1L && is.na(res$loglik))
  }
  length(res$loglik) == 1L &&
    is.finite(suppressWarnings(as.numeric(res$loglik))) &&
    (is.null(res$oof) || .cv_valid_oof_predictions(res$oof, fold_id))
}

.cv_sanitize_checkpoint_label <- function(label) {
  label <- as.character(label %||% "species")[1L]
  if (is.na(label) || !nzchar(label)) {
    label <- "species"
  }
  gsub("[^A-Za-z0-9_-]+", "_", label)
}

.cv_fold_checkpoint_path <- function(checkpoint_dir, label, fold_id) {
  file.path(
    checkpoint_dir,
    sprintf(
      "%s_fold_%s.rds",
      .cv_sanitize_checkpoint_label(label),
      gsub("[^A-Za-z0-9_-]+", "_", as.character(fold_id)[1L])
    )
  )
}

.cv_save_fold_checkpoint <- function(path, res) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  tmp <- tempfile(pattern = ".cv-fold-", tmpdir = dirname(path), fileext = ".tmp")
  on.exit(unlink(tmp), add = TRUE)
  saveRDS(res, tmp)
  if (!file.rename(tmp, path)) {
    stop("could not write CV fold checkpoint: ", path, call. = FALSE)
  }
  invisible(path)
}

.cv_read_fold_checkpoint <- function(path, fold_id) {
  res <- tryCatch(readRDS(path), error = function(e) e)
  if (inherits(res, "error") || !.cv_valid_fold_result(res, fold_id) || !is.null(res$failure) || !is.null(res$barrier_stop)) {
    stop(
      sprintf("CV_WORKER_INVALID fold=%s: invalid checkpoint %s", as.character(fold_id)[1L], path),
      call. = FALSE
    )
  }
  res
}

.cv_spatial_one_fold <- function(fold_id, dat, cfg) {
  .cv_limit_tmb_threads()
  train <- dat[as.character(dat$fold_id) != fold_id, , drop = FALSE]
  test <- dat[as.character(dat$fold_id) == fold_id, , drop = FALSE]
  pre <- .cv_spatial_preflight(train, test, fold_id)
  if (!is.null(pre)) {
    return(list(
      fold_id = fold_id,
      failure = pre,
      loglik = NA_real_,
      barrier_stop = NULL,
      oof = .cv_empty_oof_predictions()
    ))
  }
  train_mesh <- tryCatch(
    build_fishai_production_mesh(train, cfg$mesh),
    error = function(e) {
      structure(
        list(message = paste0("CV fold ", fold_id, " barrier mesh: ", conditionMessage(e))),
        class = "cv_barrier_stop"
      )
    }
  )
  if (inherits(train_mesh, "cv_barrier_stop")) {
    return(list(
      fold_id = fold_id,
      failure = NULL,
      loglik = NA_real_,
      barrier_stop = train_mesh$message,
      oof = .cv_empty_oof_predictions()
    ))
  }
  # Holdout days absent from this fold's training rows are new time levels.
  # sdmTMB scores them only when those levels were supplied as extra_time.
  fold_cfg <- cfg
  fold_cfg$model$extra_time_slices <- sort(unique(test$time_idx))
  fit_fn <- if (identical(cfg$response$type %||% "", "encounter_binomial")) {
    fit_encounter_binomial_engine
  } else {
    fit_delta_engine
  }
  fit_res <- tryCatch(
    fit_fn(train, train_mesh, fold_cfg),
    error = function(e) {
      structure(list(message = conditionMessage(e)), class = "cv_fold_error")
    }
  )
  if (inherits(fit_res, "cv_fold_error")) {
    return(list(
      fold_id = fold_id,
      failure = fit_res$message,
      loglik = NA_real_,
      barrier_stop = NULL,
      oof = .cv_empty_oof_predictions()
    ))
  }
  fit_reason <- .cv_fit_failure_reason(fit_res)
  if (!is.null(fit_reason)) {
    return(list(
      fold_id = fold_id,
      failure = fit_reason,
      loglik = NA_real_,
      barrier_stop = NULL,
      oof = .cv_empty_oof_predictions()
    ))
  }
  ll <- tryCatch(
    if (identical(cfg$response$type %||% "", "encounter_binomial")) {
      .cv_binomial_holdout_loglik(fit_res, test, cfg)
    } else {
      .cv_delta_holdout_loglik(fit_res, test, cfg)
    },
    error = function(e) conditionMessage(e)
  )
  if (is.character(ll) && length(ll) == 1L) {
    return(list(
      fold_id = fold_id,
      failure = ll,
      loglik = NA_real_,
      barrier_stop = NULL,
      oof = .cv_empty_oof_predictions()
    ))
  }
  if (!is.finite(ll)) {
    return(list(
      fold_id = fold_id,
      failure = "non-finite fold log-likelihood",
      loglik = NA_real_,
      barrier_stop = NULL,
      oof = .cv_empty_oof_predictions()
    ))
  }
  score_fn <- if (identical(cfg$response$type %||% "", "encounter_binomial")) {
    function(fit, test, cfg) score_encounter_binomial_on_events(fit, test, cfg)
  } else {
    function(fit, test, cfg) score_encounter_on_events(fit, test, cfg)
  }
  p <- tryCatch(
    score_fn(fit_res$fit, test, cfg),
    error = function(e) conditionMessage(e)
  )
  if (is.character(p) && length(p) == 1L) {
    return(list(
      fold_id = fold_id,
      failure = p,
      loglik = NA_real_,
      barrier_stop = NULL,
      oof = .cv_empty_oof_predictions()
    ))
  }
  p <- suppressWarnings(as.numeric(p))
  if (length(p) != nrow(test) || any(!is.finite(p)) || any(p < 0) || any(p > 1)) {
    return(list(
      fold_id = fold_id,
      failure = "invalid out-of-fold encounter probabilities",
      loglik = NA_real_,
      barrier_stop = NULL,
      oof = .cv_empty_oof_predictions()
    ))
  }
  oof <- data.frame(
    event_id = as.character(test$event_id),
    fold_id = as.integer(test$fold_id),
    z = as.integer(test$y > 0),
    p = p,
    stringsAsFactors = FALSE
  )
  list(fold_id = fold_id, failure = NULL, loglik = ll, barrier_stop = NULL, oof = oof)
}

#' Out-of-fold encounter probabilities. Same folds and skips as the serial
#' scorer; successful holdouts are bound in fold-id order. Worker count is
#' explicit so production callers can force the memory-safe sequential path.
.spatial_block_oof_predictions_parallel <- function(dat, cfg, fold_ids, n_workers = NULL) {
  .cv_limit_tmb_threads()
  fold_assignment <- .assert_supplied_folds_match_assignment(dat, fold_ids, cfg)
  dat$fold_id <- fold_assignment$fold_id
  dat$block_id <- fold_assignment$block_id
  .assert_cv_fold_assignment_contract(dat, fold_assignment$fold_id, cfg)
  folds <- sort(unique(as.character(fold_assignment$fold_id)))
  one <- function(fold_id) {
    .cv_limit_tmb_threads()
    train <- dat[as.character(dat$fold_id) != fold_id, , drop = FALSE]
    test <- dat[as.character(dat$fold_id) == fold_id, , drop = FALSE]
    pre <- .cv_spatial_preflight(train, test, fold_id)
    if (!is.null(pre)) {
      return(NULL)
    }
    fit_res <- tryCatch(
      {
        mesh_fold <- build_fishai_mesh(train, cfg$mesh)
        if (isTRUE(cfg$mesh$barrier$enabled)) {
          land_path <- cfg$mesh$barrier$land_sf_rds
          if (!is.null(land_path) && nzchar(land_path) && file.exists(land_path)) {
            land_sf <- readRDS(land_path)
            mesh_fold <- add_barrier_land(
              mesh_fold,
              land_sf,
              range_fraction = cfg$mesh$barrier$range_fraction %||% 0.1
            )
          }
        }
        fit_fn <- if (identical(cfg$response$type %||% "", "encounter_binomial")) {
          fit_encounter_binomial_engine
        } else {
          fit_delta_engine
        }
        fit_fn(train, mesh_fold, cfg)
      },
      error = function(e) {
        structure(list(message = conditionMessage(e)), class = "cv_fold_error")
      }
    )
    if (inherits(fit_res, "cv_fold_error")) {
      return(NULL)
    }
    fit_reason <- .cv_fit_failure_reason(fit_res)
    if (!is.null(fit_reason)) {
      return(NULL)
    }
    score_fn <- if (identical(cfg$response$type %||% "", "encounter_binomial")) {
      function(fit, test, cfg) score_encounter_binomial_on_events(fit, test, cfg)
    } else {
      function(fit, test, cfg) score_encounter_on_events(fit, test, cfg)
    }
    p <- tryCatch(score_fn(fit_res$fit, test, cfg), error = function(e) NULL)
    if (is.null(p)) {
      return(NULL)
    }
    data.frame(
      event_id = as.character(test$event_id),
      fold_id = as.integer(test$fold_id),
      z = as.integer(test$y > 0),
      p = as.numeric(p),
      stringsAsFactors = FALSE
    )
  }
  n_workers <- if (is.null(n_workers)) {
    .cv_spatial_n_workers(length(folds))
  } else {
    max(1L, min(as.integer(n_workers)[1L], length(folds)))
  }
  pred_chunks <- if (n_workers <= 1L) {
    lapply(folds, one)
  } else {
    parallel::mclapply(
      folds,
      one,
      mc.cores = n_workers,
      mc.preschedule = FALSE,
      mc.allow.recursive = TRUE
    )
  }
  for (idx in seq_along(pred_chunks)) {
    chunk <- pred_chunks[[idx]]
    if (inherits(chunk, "try-error") || (!is.null(chunk) && !.cv_valid_oof_predictions(chunk, folds[[idx]]))) {
      stop(
        sprintf("CV_WORKER_INVALID fold=%s: invalid out-of-fold prediction result", folds[[idx]]),
        call. = FALSE
      )
    }
  }
  pred_chunks <- pred_chunks[!vapply(pred_chunks, is.null, logical(1))]
  if (!length(pred_chunks)) {
    return(data.frame(
      event_id = character(),
      fold_id = integer(),
      z = integer(),
      p = numeric(),
      stringsAsFactors = FALSE
    ))
  }
  out <- do.call(rbind, pred_chunks)
  rownames(out) <- NULL
  out
}

#' Spatial-block cross-validation with explicit fold IDs.
#' Failed folds are recorded (not fatal); see ``n_failed_folds`` and ``fold_failures``.
#' By default folds may run with ``min(cores, 4)`` workers and one TMB thread
#' each. Production callers can force ``n_workers = 1`` and supply
#' ``checkpoint_dir`` so each completed fold is persisted immediately and a
#' restarted run skips folds whose checkpoints validate.
#' @export
run_cv_spatial <- function(
  dat,
  mesh,
  cfg,
  fold_ids,
  n_workers = NULL,
  checkpoint_dir = NULL,
  checkpoint_label = NULL
) {
  .refuse_random_cv(fold_ids)
  fold_assignment <- .assert_supplied_folds_match_assignment(dat, fold_ids, cfg)
  dat$fold_id <- fold_assignment$fold_id
  dat$block_id <- fold_assignment$block_id
  .assert_cv_fold_assignment_contract(dat, fold_assignment$fold_id, cfg)
  spatial_meta <- spatial_block_cv_params(cfg)
  folds <- sort(unique(as.character(fold_assignment$fold_id)))
  fold_loglik <- stats::setNames(rep(NA_real_, length(folds)), folds)
  fold_failures <- list()
  oof_chunks <- list()
  if (isTRUE(cfg$mesh$barrier$enabled)) {
    .read_barrier_land(cfg$mesh)
  }

  .cv_limit_tmb_threads()
  checkpoint_label <- checkpoint_label %||% cfg$species$taxon %||% "species"
  n_workers <- if (!is.null(checkpoint_dir)) {
    1L
  } else if (is.null(n_workers)) {
    .cv_spatial_n_workers(length(folds))
  } else {
    max(1L, min(as.integer(n_workers)[1L], length(folds)))
  }

  run_one_fold <- function(fold_id) {
    if (!is.null(checkpoint_dir)) {
      checkpoint_path <- .cv_fold_checkpoint_path(checkpoint_dir, checkpoint_label, fold_id)
      if (file.exists(checkpoint_path)) {
        res <- .cv_read_fold_checkpoint(checkpoint_path, fold_id)
        message(sprintf(
          "CV_FOLD_SKIPPED species=%s fold=%s checkpoint=%s",
          .cv_sanitize_checkpoint_label(checkpoint_label),
          fold_id,
          checkpoint_path
        ))
        return(res)
      }
    }
    res <- .cv_spatial_one_fold(fold_id, dat, cfg)
    if (!.cv_valid_fold_result(res, fold_id)) {
      stop(
        sprintf("CV_WORKER_INVALID fold=%s: invalid fold result", fold_id),
        call. = FALSE
      )
    }
    if (!is.null(checkpoint_dir) && is.null(res$failure) && is.null(res$barrier_stop)) {
      checkpoint_path <- .cv_fold_checkpoint_path(checkpoint_dir, checkpoint_label, fold_id)
      .cv_save_fold_checkpoint(checkpoint_path, res)
      message(sprintf(
        "CV_FOLD_DONE species=%s fold=%s loglik=%.6f checkpoint=%s",
        .cv_sanitize_checkpoint_label(checkpoint_label),
        fold_id,
        as.numeric(res$loglik),
        checkpoint_path
      ))
    }
    # Release the fold's fit/mesh/data copies back to the OS before the next
    # fold. On RAM-constrained runners the peak of one fold must not bleed
    # into the next.
    gc(verbose = FALSE)
    res
  }

  results <- if (n_workers <= 1L) {
    lapply(folds, run_one_fold)
  } else {
    parallel::mclapply(
      folds,
      run_one_fold,
      mc.cores = n_workers,
      mc.preschedule = FALSE,
      mc.allow.recursive = TRUE
    )
  }
  for (idx in seq_along(results)) {
    res <- results[[idx]]
    fold_id <- folds[[idx]]
    if (!.cv_valid_fold_result(res, fold_id)) {
      stop(
        sprintf("CV_WORKER_INVALID fold=%s: invalid fold result", fold_id),
        call. = FALSE
      )
    }
    if (!is.null(res$barrier_stop)) {
      stop(res$barrier_stop, call. = FALSE)
    }
    if (!is.null(res$failure)) {
      fold_failures[[res$fold_id]] <- res$failure
      message("CV fold ", res$fold_id, " failed: ", res$failure)
    } else {
      fold_loglik[[res$fold_id]] <- res$loglik
      if (!is.null(res$oof) && nrow(res$oof)) {
        oof_chunks[[res$fold_id]] <- res$oof
      }
    }
  }
  oof_predictions <- if (length(oof_chunks)) {
    out <- do.call(rbind, oof_chunks)
    rownames(out) <- NULL
    out
  } else {
    .cv_empty_oof_predictions()
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
      oof_predictions = oof_predictions,
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
#'
#' Eligible candidates must share one fold assignment. That table is the
#' assignment used to score them and the table reported on the selection.
#' Non-finite ELPD never enters ``which.max``.
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
  if (any(!is.finite(elpd))) {
    stop(
      "elpd_nonfinite_eligible_candidate: refusing to rank a non-finite ELPD",
      call. = FALSE
    )
  }
  tabs <- lapply(cv_results[eligible], function(x) x$fold_assignment)
  keys <- vapply(tabs, .fold_assignment_key, character(1))
  if (any(is.na(keys))) {
    stop(
      "elpd_fold_assignment_missing: eligible candidate has no fold assignment",
      call. = FALSE
    )
  }
  if (length(unique(keys)) != 1L) {
    stop(
      "elpd_fold_assignment_mismatch: folds used in ELPD selection are not the same assignment",
      call. = FALSE
    )
  }
  best <- names(cv_results)[eligible][which.max(elpd)]
  structure(
    best,
    elpd_report = report,
    fold_assignment = cv_results[[best]]$fold_assignment,
    class = "fishai_elpd_selection"
  )
}

#' @export
refuse_random_cv <- function() {
  stop("sdmTMB_cv() defaults to random folds; always pass explicit fold_ids or lfo=TRUE.", call. = FALSE)
}
