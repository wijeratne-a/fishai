#' Load short-sample pre-registration protocol from YAML (thresholds only).
#' @export
load_short_sample_protocol <- function(path = NULL) {
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  path <- path %||% file.path(root, "configs", "sensitivity_short_samples.yaml")
  if (!file.exists(path)) {
    stop("sensitivity protocol not found: ", path, call. = FALSE)
  }
  raw <- yaml::read_yaml(path)
  proto <- raw$short_sample_sensitivity
  if (is.null(proto)) {
    stop("missing short_sample_sensitivity block in ", path, call. = FALSE)
  }
  proto$config_path <- normalizePath(path, mustWork = TRUE)
  proto
}

#' Git object name for the prereg markdown at HEAD (recorded in run metadata).
#' @export
prereg_commit_sha <- function(git_path, repo_root = NULL) {
  for (env_nm in c("PREREG_COMMIT_SHA", "GIT_SHA", "GITHUB_SHA")) {
    sha <- trimws(Sys.getenv(env_nm, unset = ""))
    if (nzchar(sha) && grepl("^[0-9a-fA-F]{5,40}$", sha)) {
      return(tolower(sha))
    }
  }
  repo_root <- repo_root %||% Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  git_path <- gsub("^\\./", "", git_path)
  git_dir <- file.path(repo_root, ".git")
  if (!dir.exists(git_dir)) {
    stop(
      "could not resolve prereg_commit_sha for ",
      git_path,
      "; set PREREG_COMMIT_SHA or GIT_SHA (CI should pass github.sha into docker-r)",
      call. = FALSE
    )
  }
  cmd <- paste("git", "-C", shQuote(repo_root), "rev-parse", shQuote(paste0("HEAD:", git_path)))
  sha <- tryCatch(trimws(system(cmd, intern = TRUE, ignore.stderr = TRUE)), error = function(e) character())
  if (length(sha) != 1L || !nzchar(sha) || grepl("fatal", sha)) {
    stop(
      "could not resolve prereg_commit_sha for ",
      git_path,
      "; set PREREG_COMMIT_SHA or GIT_SHA when git rev-parse is unavailable",
      call. = FALSE
    )
  }
  sha
}

.revert_duration_minutes <- function(protocol) {
  ro <- protocol$revert_on_fail
  val <- ro$duration_minutes %||% ro$duration_min_minutes
  if (is.null(val) || !is.finite(as.numeric(val))) {
    stop("revert_on_fail.duration_minutes missing from sensitivity protocol", call. = FALSE)
  }
  as.numeric(val)
}

.prepare_cv_holdout_for_predict <- function(train, test) {
  if (!"time_idx" %in% names(train) || !"time_idx" %in% names(test) || !nrow(test)) {
    return(test)
  }
  max_train <- max(as.integer(train$time_idx), na.rm = TRUE)
  out <- test
  out$time_idx <- pmin(as.integer(out$time_idx), max_train)
  out
}

.extract_wald_table <- function(fishai_fit, conf_level) {
  fit <- fishai_fit$fit
  pieces <- list()
  tf <- tryCatch(
    sdmTMB::tidy(fit, conf.int = TRUE, conf.level = conf_level, effects = "fixed"),
    error = function(e) NULL
  )
  if (!is.null(tf) && nrow(tf) > 0) {
    tf$param_id <- paste0("fixed:", tf$term)
    if ("model" %in% names(tf)) {
      tf$param_id <- paste0(tf$param_id, ":m", tf$model)
    }
    pieces[[length(pieces) + 1L]] <- tf[, c("param_id", "estimate", "conf.low", "conf.high")]
  }
  for (m in c(1L, 2L)) {
    tr <- tryCatch(
      sdmTMB::tidy(
        fit,
        conf.int = TRUE,
        conf.level = conf_level,
        effects = "ran_pars",
        model = m
      ),
      error = function(e) NULL
    )
    if (is.null(tr) || !nrow(tr)) {
      next
    }
    if (!tr$term %in% c("range", "sigma_O", "sigma_E", "sigma", "phi")) {
      tr <- tr[tr$term %in% c("range", "sigma_O", "sigma_E", "sigma", "phi"), , drop = FALSE]
    }
    if (!nrow(tr)) {
      next
    }
    tr$param_id <- paste0("ran:", tr$term, ":m", m)
    pieces[[length(pieces) + 1L]] <- tr[, c("param_id", "estimate", "conf.low", "conf.high")]
  }
  if (!length(pieces)) {
    stop("no Wald parameters extracted for coefficient check", call. = FALSE)
  }
  out <- do.call(rbind, pieces)
  rownames(out) <- NULL
  out
}

#' @export
check_coefficient_wald_pass <- function(full_fit, reduced_fit, conf_level = 0.95) {
  full <- .extract_wald_table(full_fit, conf_level)
  red <- .extract_wald_table(reduced_fit, conf_level)
  merged <- merge(full, red, by = "param_id", suffixes = c("_full", "_red"), all = FALSE)
  if (!nrow(merged)) {
    stop("no overlapping parameters between full and reduced fits", call. = FALSE)
  }
  ok <- !is.na(merged$estimate_red) &
    !is.na(merged$conf.low_full) &
    !is.na(merged$conf.high_full) &
    merged$estimate_red >= merged$conf.low_full &
    merged$estimate_red <= merged$conf.high_full
  list(
    pass = all(ok),
    details = merged,
    failures = merged$param_id[!ok]
  )
}

.fold_metric_vectors <- function(dat, cfg, eval_min_duration, fold_col = "fold_id") {
  if (!fold_col %in% names(dat)) {
    stop("missing fold column: ", fold_col, call. = FALSE)
  }
  folds <- sort(unique(dat[[fold_col]]))
  fold_names <- as.character(folds)
  mean_log_score <- stats::setNames(rep(NA_real_, length(folds)), fold_names)
  boyce <- stats::setNames(rep(NA_real_, length(folds)), fold_names)
  for (k in folds) {
    kn <- as.character(k)
    train <- dat[dat[[fold_col]] != k, , drop = FALSE]
    test <- dat[dat[[fold_col]] == k, , drop = FALSE]
    test <- .cv_holdout_rows(test, eval_min_duration)
    if (nrow(train) < 5L || nrow(test) < 2L) {
      next
    }
    mesh <- build_fishai_mesh(train, cfg$mesh)
    fit <- tryCatch(fit_delta_engine(train, mesh, cfg), error = function(e) NULL)
    if (is.null(fit)) {
      next
    }
    test_pred <- .prepare_cv_holdout_for_predict(train, test)
    p <- tryCatch(score_encounter_on_events(fit$fit, test_pred, cfg), error = function(e) NULL)
    if (is.null(p)) {
      next
    }
    z <- as.integer(test$y > 0)
    if (sum(z == 1L) < 1L || sum(z == 0L) < 1L) {
      boyce[[kn]] <- NA_real_
    } else {
      boyce[[kn]] <- cbi_continuous(p, p[z == 1L])
    }
    ll <- sum(z * log(pmax(p, 1e-15)) + (1L - z) * log(pmax(1 - p, 1e-15)))
    mean_log_score[[kn]] <- ll / nrow(test)
  }
  list(mean_log_score = mean_log_score, boyce_index = boyce, fold_id = folds)
}

.lfo_fold_metric_vectors <- function(dat, cfg, eval_min_duration, n_validations = 3L) {
  es <- parse_egg_split(cfg)
  d <- .event_date_utc(dat)
  train <- dat[d <= es$fit_end, , drop = FALSE]
  test_dates <- sort(unique(d[d >= es$test_start & d <= es$test_end]))
  if (length(test_dates) < 1L) {
    return(list(mean_log_score = numeric(), boyce_index = numeric()))
  }
  n_val <- min(n_validations, length(test_dates))
  hold_dates <- test_dates[seq(from = length(test_dates) - n_val + 1L, to = length(test_dates))]
  mean_log_score <- numeric()
  boyce <- numeric()
  for (hd in hold_dates) {
    test <- dat[d == hd, , drop = FALSE]
    test <- .cv_holdout_rows(test, eval_min_duration)
    if (nrow(train) < 5L || nrow(test) < 2L) {
      next
    }
    mesh <- build_fishai_mesh(train, cfg$mesh)
    fit <- tryCatch(fit_delta_engine(train, mesh, cfg), error = function(e) NULL)
    if (is.null(fit)) {
      next
    }
    test_pred <- .prepare_cv_holdout_for_predict(train, test)
    p <- tryCatch(score_encounter_on_events(fit$fit, test_pred, cfg), error = function(e) NULL)
    if (is.null(p)) {
      next
    }
    z <- as.integer(test$y > 0)
    if (sum(z == 1L) < 1L || sum(z == 0L) < 1L) {
      boyce <- c(boyce, NA_real_)
    } else {
      boyce <- c(boyce, cbi_continuous(p, p[z == 1L]))
    }
    ll <- sum(z * log(pmax(p, 1e-15)) + (1L - z) * log(pmax(1 - p, 1e-15)))
    mean_log_score <- c(mean_log_score, ll / nrow(test))
  }
  list(mean_log_score = mean_log_score, boyce_index = boyce)
}

#' @export
check_cv_metric_pass <- function(full_vals, reduced_vals, margin_se) {
  fn <- names(full_vals)
  rn <- names(reduced_vals)
  if (!is.null(fn) || !is.null(rn)) {
    if (is.null(fn) || is.null(rn) || !setequal(fn, rn)) {
      return(list(
        pass = FALSE,
        mean_diff = NA_real_,
        se_diff = NA_real_,
        n_folds = 0L,
        fold_ids = character()
      ))
    }
    reduced_vals <- reduced_vals[fn]
  }
  full_vals <- as.numeric(full_vals)
  reduced_vals <- as.numeric(reduced_vals)
  if (length(full_vals) != length(reduced_vals) || length(full_vals) < 2L) {
    return(list(
      pass = FALSE,
      mean_diff = NA_real_,
      se_diff = NA_real_,
      n_folds = length(full_vals),
      fold_ids = fn %||% character()
    ))
  }
  ok <- is.finite(full_vals) & is.finite(reduced_vals)
  compared <- if (!is.null(fn)) fn[ok] else character()
  full_vals <- full_vals[ok]
  reduced_vals <- reduced_vals[ok]
  if (length(full_vals) < 2L) {
    return(list(
      pass = FALSE,
      mean_diff = NA_real_,
      se_diff = NA_real_,
      n_folds = length(full_vals),
      fold_ids = compared
    ))
  }
  d <- full_vals - reduced_vals
  se <- stats::sd(d) / sqrt(length(d))
  mean_d <- mean(d)
  pass <- is.finite(se) && (se == 0 || mean_d >= -margin_se * se)
  list(
    pass = pass,
    mean_diff = mean_d,
    se_diff = se,
    n_folds = length(d),
    fold_ids = compared
  )
}

#' @export
check_cv_design_pass <- function(full_metrics, reduced_metrics, margin_se, metrics) {
  out <- list()
  all_pass <- TRUE
  for (m in metrics) {
    res <- check_cv_metric_pass(full_metrics[[m]], reduced_metrics[[m]], margin_se)
    out[[m]] <- res
    all_pass <- all_pass && isTRUE(res$pass)
  }
  c(out, list(pass = all_pass))
}

.cv_holdout_rows <- function(test, eval_min_duration) {
  if ("short_event" %in% names(test)) {
    short <- .parse_short_event_logical(test$short_event)
    return(test[short %in% FALSE, , drop = FALSE])
  }
  if (!is.null(eval_min_duration) && "duration_min" %in% names(test)) {
    dur <- as.numeric(test$duration_min)
    return(test[!is.na(dur) & dur >= eval_min_duration, , drop = FALSE])
  }
  test
}

#' Run pre-registered short-sample sensitivity for one species.
#' @export
run_short_sample_species <- function(protocol, species_entry) {
  cfg <- load_config_yaml(species_entry$model_config)
  if (!is.null(protocol$fold_assignment_path)) {
    cfg$data$fold_assignment_path <- protocol$fold_assignment_path
  }
  if (!is.null(protocol$event_count_guard)) {
    cfg$data$event_count_guard <- protocol$event_count_guard
  }
  conf_level <- protocol$coefficient_check$wald_confidence
  margin_se <- protocol$cv_check$margin_se_fold_diff
  metrics <- unlist(protocol$cv_check$metrics)
  eval_min <- protocol$cv_eval_min_duration_min
  full_min <- protocol$full_fit_min_duration_min
  prereg_reduced <- isTRUE(protocol$reduced_fit_exclude_short_events %||% TRUE)

  dat_full <- load_model_data(cfg = cfg, min_duration_min = full_min, egg_split_scope = "fit")
  dat_all <- load_model_data(cfg = cfg, min_duration_min = full_min, egg_split_scope = "all")
  dat_red <- if (prereg_reduced) {
    load_model_data(cfg = cfg, exclude_short_events = TRUE, egg_split_scope = "fit")
  } else {
    load_model_data(cfg = cfg, min_duration_min = protocol$reduced_fit_min_duration_min, egg_split_scope = "fit")
  }
  mesh_full <- build_fishai_mesh(dat_full, cfg$mesh)
  mesh_red <- build_fishai_mesh(dat_red, cfg$mesh)
  fit_full <- fit_delta_engine(dat_full, mesh_full, cfg)
  fit_red <- fit_delta_engine(dat_red, mesh_red, cfg)

  coef <- check_coefficient_wald_pass(fit_full, fit_red, conf_level = conf_level)

  cv_sp_full <- .fold_metric_vectors(dat_full, cfg, eval_min, "fold_id")
  cv_sp_red <- .fold_metric_vectors(dat_red, cfg, eval_min, "fold_id")
  cv_sp <- check_cv_design_pass(cv_sp_full, cv_sp_red, margin_se, metrics)

  cv_lfo_full <- .lfo_fold_metric_vectors(dat_all, cfg, eval_min)
  cv_lfo_red <- .lfo_fold_metric_vectors(
    if (prereg_reduced) {
      load_model_data(cfg = cfg, exclude_short_events = TRUE, egg_split_scope = "all")
    } else {
      load_model_data(
        cfg = cfg,
        min_duration_min = protocol$reduced_fit_min_duration_min,
        egg_split_scope = "all"
      )
    },
    cfg,
    eval_min
  )
  cv_lfo <- check_cv_design_pass(cv_lfo_full, cv_lfo_red, margin_se, metrics)

  overall_pass <- isTRUE(coef$pass) && isTRUE(cv_sp$pass) && isTRUE(cv_lfo$pass)
  revert_min <- .revert_duration_minutes(protocol)
  use_short_revert <- !overall_pass && prereg_reduced
  dat_action <- if (overall_pass) {
    load_model_data(cfg = cfg, min_duration_min = full_min)
  } else if (use_short_revert) {
    load_model_data(cfg = cfg, exclude_short_events = TRUE, min_duration_min = full_min)
  } else {
    load_model_data(cfg = cfg, min_duration_min = revert_min)
  }
  action_min <- if (overall_pass) full_min else revert_min
  if (nrow(dat_action) == 0L) {
    stop(
      "no events remain after short-sample action frame for ",
      species_entry$label,
      "; cannot recompute V_ref",
      call. = FALSE
    )
  }
  vref <- compute_reference_volume_metadata(dat_action, cfg)

  list(
    label = species_entry$label,
    taxon = cfg$species$taxon,
    coefficient_pass = isTRUE(coef$pass),
    cv_spatial_pass = isTRUE(cv_sp$pass),
    cv_lfo_pass = isTRUE(cv_lfo$pass),
    overall_pass = overall_pass,
    action_min_duration_min = action_min,
    action_exclude_short_events = use_short_revert,
    reduced_fit_exclude_short_events = prereg_reduced,
    reference_volume_m3 = vref$reference_volume_m3,
    reference_volume_n_events = vref$source$n_events_fitting_frame,
    n_events_full = nrow(dat_full),
    n_events_reduced = nrow(dat_red),
    coefficient_check = coef,
    cv_spatial = cv_sp,
    cv_lfo = cv_lfo
  )
}

#' Execute full protocol for all species; write pass/fail table and JSON report.
#' @export
run_short_sample_sensitivity <- function(protocol_path = NULL, output_override = NULL) {
  protocol <- load_short_sample_protocol(protocol_path)
  if (!is.null(output_override)) {
    protocol$output <- utils::modifyList(protocol$output, output_override)
  }
  git_path <- protocol$prereg_doc_git_path
  sha <- prereg_commit_sha(git_path)
  species <- protocol$species

  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  cfg_ref <- load_config_yaml(species[[1L]]$model_config)
  events_ref <- .read_model_table(cfg_ref$data$events_path)
  events_ref <- .normalize_cufes_events_columns(events_ref)
  .validate_cufes_events_schema(events_ref)
  spatial_params <- spatial_block_cv_params(cfg_ref)
  fold_assignment <- assign_cufes_spatial_block_folds(events_ref, spatial_params)
  fold_csv <- protocol$output$fold_assignment_csv
  if (is.null(fold_csv) || !nzchar(fold_csv)) {
    stop("protocol output.fold_assignment_csv is required", call. = FALSE)
  }
  if (!grepl("^/", fold_csv)) {
    fold_csv <- file.path(root, fold_csv)
  }
  write_fold_assignment_csv(fold_assignment, fold_csv)
  fold_assignment_sha256 <- file_sha256(fold_csv)
  protocol$fold_assignment_path <- fold_csv
  protocol$spatial_block_cv <- spatial_params
  protocol$fold_assignment_sha256 <- fold_assignment_sha256

  results <- lapply(species, function(sp) run_short_sample_species(protocol, sp))

  pass_fail <- do.call(
    rbind,
    lapply(results, function(r) {
      data.frame(
        species = r$label,
        taxon = r$taxon,
        coefficient_pass = r$coefficient_pass,
        cv_spatial_pass = r$cv_spatial_pass,
        cv_lfo_pass = r$cv_lfo_pass,
        overall_pass = r$overall_pass,
        action_min_duration_min = r$action_min_duration_min,
        reference_volume_m3 = r$reference_volume_m3,
        reference_volume_n_events = r$reference_volume_n_events,
        stringsAsFactors = FALSE
      )
    })
  )

  out_json <- protocol$output$report_json
  out_csv <- protocol$output$pass_fail_csv
  if (!grepl("^/", out_json)) {
    out_json <- file.path(root, out_json)
  }
  if (!grepl("^/", out_csv)) {
    out_csv <- file.path(root, out_csv)
  }
  dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
  dir.create(dirname(out_csv), recursive = TRUE, showWarnings = FALSE)

  report <- list(
    prereg_commit_sha = sha,
    prereg_doc = protocol$prereg_doc,
    protocol_config = protocol$config_path,
    spatial_block_cv = protocol$spatial_block_cv,
    fold_assignment_csv = fold_csv,
    fold_assignment_sha256 = protocol$fold_assignment_sha256,
    thresholds = list(
      full_fit_min_duration_min = protocol$full_fit_min_duration_min,
      reduced_fit_exclude_short_events = protocol$reduced_fit_exclude_short_events %||% TRUE,
      reduced_fit_min_duration_min = protocol$reduced_fit_min_duration_min,
      cv_eval_min_duration_min = protocol$cv_eval_min_duration_min,
      wald_confidence = protocol$coefficient_check$wald_confidence,
      cv_margin_se_fold_diff = protocol$cv_check$margin_se_fold_diff,
      revert_duration_min = .revert_duration_minutes(protocol)
    ),
    pass_fail = pass_fail,
    species_results = results
  )

  utils::write.csv(pass_fail, out_csv, row.names = FALSE)
  jsonlite::write_json(report, out_json, auto_unbox = TRUE, pretty = TRUE, null = "null")

  invisible(report)
}
