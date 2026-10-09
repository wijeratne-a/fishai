#' 24 h WCOFS-forced rolling-origin validation (extends forecast_temporal_holdout).
#'
#' Operational arm prefers issued WCOFS ``fields.f024`` covariates when reachable;
#' otherwise falls back to the pre-declared damped-anomaly proxy (GLORYS training units).

WCOFS_FORCING_WCOFS <- "wcofs_forecast"
WCOFS_FORCING_PROXY <- "proxy_fallback"
WCOFS_24H_LEAD_TAG <- "f024"

.forecast_apply_slug_covariates <- function(hold_row, slug_values, dyn_cols) {
  for (col in dyn_cols) {
    slug <- sub("_z$", "", col)
    if (slug %in% names(slug_values) && is.finite(slug_values[[slug]])) {
      hold_row[[col]] <- slug_values[[slug]]
    }
  }
  if ("log_depth_z" %in% dyn_cols || "log_depth_z" %in% names(hold_row)) {
    if ("log_depth" %in% names(slug_values) && is.finite(slug_values[["log_depth"]])) {
      hold_row[["log_depth_z"]] <- slug_values[["log_depth"]]
    }
  }
  hold_row
}

.forecast_wcofs_forcing_path <- function(root, label, cutoff) {
  file.path(
    root,
    "artifacts",
    "cufes_24h_wcofs_prediction",
    "forcing",
    label,
    paste0(format(as.Date(cutoff)), ".parquet")
  )
}

#' Score holdout rows with WCOFS-first operational forcing.
#'
#' When ``wcofs_forcing`` is supplied (event_id keyed), rows with
#' ``forcing_source == wcofs_forecast`` use those covariates; others use the
#' damped-anomaly proxy from the approved design.
#' @export
forecast_score_rows_wcofs <- function(
  fit,
  train,
  hold,
  cfg,
  cutoff_date,
  extra_time,
  wcofs_forcing = NULL
) {
  dyn_cols <- .forecast_dynamic_columns(cfg)
  missing_cols <- setdiff(dyn_cols, names(hold))
  if (length(missing_cols)) {
    stop("holdout frame missing covariate columns: ", paste(missing_cols, collapse = ", "), call. = FALSE)
  }
  cutoff_rows <- train[train$event_day == cutoff_date, , drop = FALSE]
  if (!nrow(cutoff_rows)) {
    stop("cutoff day has no training rows", call. = FALSE)
  }
  p_cut <- as.numeric(score_encounter_on_events(fit, cutoff_rows, cfg))
  mu_cut <- .forecast_positive_mu(fit, cutoff_rows)
  shape <- .forecast_shape(fit)
  future_idx <- sort(unique(as.integer(hold$time_idx)))
  if (!all(future_idx %in% as.integer(extra_time))) {
    stop("holdout time_idx was not projected with extra_time", call. = FALSE)
  }

  wcofs_by_id <- list()
  if (!is.null(wcofs_forcing) && nrow(wcofs_forcing)) {
    ids <- as.character(wcofs_forcing$event_id)
    wcofs_by_id <- stats::setNames(split(wcofs_forcing, ids), ids)
  }

  n <- nrow(hold)
  p_per <- rep(NA_real_, n)
  p_clim <- rep(NA_real_, n)
  ll_per <- rep(NA_real_, n)
  ll_clim <- rep(NA_real_, n)
  unknown <- rep("", n)
  forcing_used <- rep(WCOFS_FORCING_PROXY, n)
  op_new <- hold

  for (i in seq_len(n)) {
    h_days <- as.integer(hold$event_day[i] - cutoff_date)
    reasons <- character()
    d_cut <- forecast_dist_km(hold$X[i], hold$Y[i], cutoff_rows$X, cutoff_rows$Y)
    near_cut <- is.finite(d_cut) & d_cut <= 120
    if (!any(near_cut)) {
      reasons <- c(reasons, "no_cutoff_track_within_120km")
    } else {
      p_per[i] <- forecast_idw(p_cut[near_cut], d_cut[near_cut])
      mu_i <- forecast_idw(mu_cut[near_cut], d_cut[near_cut])
      if (is.finite(p_per[i]) && is.finite(mu_i) && mu_i > 0) {
        ll_per[i] <- .forecast_event_delta_ll(p_per[i], hold$y[i], mu_i, shape)
      } else {
        p_per[i] <- NA_real_
        reasons <- c(reasons, "persistence_mean_not_finite")
      }
    }
    d_train <- forecast_dist_km(hold$X[i], hold$Y[i], train$X, train$Y)
    doy_d <- forecast_doy_distance(train$doy, hold$doy[i])
    p_clim[i] <- forecast_local_mean(as.numeric(train$y > 0), d_train, doy_d)
    if (!is.finite(p_clim[i])) {
      reasons <- c(reasons, "climatology_support")
    } else {
      ll_clim[i] <- .forecast_bernoulli_ll(p_clim[i], hold$y[i])
    }

    wcofs_row <- wcofs_by_id[[as.character(hold$event_id[i])]]
    wcofs_ok <- FALSE
    if (!is.null(wcofs_row) && length(wcofs_row)) {
      wcofs_row <- wcofs_row[[1L]]
      if (identical(as.character(wcofs_row$forcing_source[[1L]]), WCOFS_FORCING_WCOFS) && h_days == 1L) {
        slug_vals <- as.list(wcofs_row)
        op_row <- hold[i, , drop = FALSE]
        op_row <- .forecast_apply_slug_covariates(op_row, slug_vals, dyn_cols)
        miss <- vapply(dyn_cols, function(col) !is.finite(op_row[[col]][1L]), logical(1))
        if (!any(miss)) {
          op_new[i, dyn_cols] <- op_row[, dyn_cols, drop = FALSE]
          wcofs_ok <- TRUE
          forcing_used[i] <- WCOFS_FORCING_WCOFS
        } else {
          reasons <- c(reasons, "wcofs_covariate_incomplete")
        }
      }
    }

    if (!wcofs_ok) {
      op_ok <- any(near_cut)
      x_cut <- stats::setNames(rep(NA_real_, length(dyn_cols)), dyn_cols)
      clim <- x_cut
      for (col in dyn_cols) {
        if (any(near_cut)) {
          x_cut[[col]] <- forecast_idw(cutoff_rows[[col]][near_cut], d_cut[near_cut])
        }
        clim[[col]] <- forecast_local_mean(train[[col]], d_train, doy_d)
        if (!is.finite(x_cut[[col]]) || !is.finite(clim[[col]])) {
          op_ok <- FALSE
        }
      }
      if (!op_ok) {
        reasons <- c(reasons, "operational_proxy_support")
      } else {
        for (col in dyn_cols) {
          op_new[[col]][i] <- forecast_damped_anomaly(clim[[col]], x_cut[[col]], h_days)
        }
        forcing_used[i] <- WCOFS_FORCING_PROXY
      }
    }
    unknown[i] <- paste(unique(reasons), collapse = ";")
  }

  p_oracle <- as.numeric(score_encounter_on_events(fit, hold, cfg))
  mu_oracle <- .forecast_positive_mu(fit, hold)
  ll_oracle <- .forecast_event_delta_ll(p_oracle, hold$y, mu_oracle, shape)

  op_rows <- !grepl("operational_proxy_support|wcofs_covariate_incomplete", unknown) &
    forcing_used %in% c(WCOFS_FORCING_WCOFS, WCOFS_FORCING_PROXY)
  p_op <- rep(NA_real_, n)
  ll_op <- rep(NA_real_, n)
  if (any(op_rows)) {
    op_sub <- op_new[op_rows, , drop = FALSE]
    p_op[op_rows] <- as.numeric(score_encounter_on_events(fit, op_sub, cfg))
    mu_op <- .forecast_positive_mu(fit, op_sub)
    ll_op[op_rows] <- .forecast_event_delta_ll(p_op[op_rows], op_sub$y, mu_op, shape)
  }

  common <- is.finite(p_oracle) & is.finite(ll_oracle) &
    is.finite(p_op) & is.finite(ll_op) &
    is.finite(p_per) & is.finite(ll_per) &
    is.finite(p_clim) & is.finite(ll_clim)

  data.frame(
    cutoff = format(as.Date(cutoff_date)),
    horizon_hours = as.integer(hold$event_day - cutoff_date) * 24L,
    z = as.integer(hold$y > 0),
    forcing_source = forcing_used,
    p_oracle = p_oracle,
    p_operational = p_op,
    p_persistence = p_per,
    p_climatology = p_clim,
    ll_oracle = ll_oracle,
    ll_operational = ll_op,
    ll_persistence = ll_per,
    ll_climatology = ll_clim,
    in_common_support = common,
    unknown_reason = ifelse(common, "", unknown),
    stringsAsFactors = FALSE
  )
}

.forecast_pool_metrics_wcofs <- function(rows) {
  sources <- c("oracle", "operational", "persistence", "climatology")
  kinds <- c(oracle = "delta", operational = "delta", persistence = "delta", climatology = "bernoulli")
  horizons <- c(24L)
  out <- list()
  for (h in horizons) {
    sub <- rows[rows$in_common_support %in% TRUE & rows$horizon_hours == h, , drop = FALSE]
    slot <- list(horizon_hours = h, n_common_support = nrow(sub))
    for (src in sources) {
      block <- .forecast_metric_block(
        sub$z,
        sub[[paste0("p_", src)]],
        sub[[paste0("ll_", src)]],
        kinds[[src]]
      )
      if (identical(src, "operational")) {
        n_wcofs <- sum(sub$forcing_source == WCOFS_FORCING_WCOFS)
        n_proxy <- sum(sub$forcing_source == WCOFS_FORCING_PROXY)
        block$forcing_mix <- list(
          wcofs_forecast = n_wcofs,
          proxy_fallback = n_proxy
        )
      }
      slot[[src]] <- block
    }
    out[[as.character(h)]] <- slot
  }
  out
}

.forecast_species_wcofs_from_rows <- function(label, taxon, model_config, cutoffs, pieces, forcing_label) {
  eligible <- vapply(pieces, function(x) isTRUE(x$eligible), logical(1))
  rows <- do.call(rbind, lapply(pieces[eligible], function(x) x$rows))
  pooled <- if (!is.null(rows) && nrow(rows)) .forecast_pool_metrics_wcofs(rows) else NULL
  h24 <- if (!is.null(pooled)) pooled[["24"]] else NULL
  pass <- FALSE
  if (!is.null(h24)) {
    pass <- forecast_passes_24h(
      h24$operational$auc,
      h24$persistence$auc,
      h24$climatology$auc,
      h24$operational$tss,
      h24$persistence$tss,
      h24$climatology$tss,
      sum(eligible)
    )
  }
  list(
    label = label,
    taxon = taxon,
    model_config = model_config,
    forcing_source = forcing_label,
    n_cutoffs = length(cutoffs),
    n_eligible_cutoffs = sum(eligible),
    fit_status = if (sum(eligible) >= 6L) "scored" else "INSUFFICIENT",
    pass_24h = pass,
    pass_rule = paste0(
      "operational (WCOFS or proxy_fallback) AUC and TSS at 24h strictly greater ",
      "than persistence and climatology, with at least 6 eligible cutoffs"
    ),
    pooled = pooled,
    cutoffs = pieces
  )
}

#' Run 24 h WCOFS-first holdout and write ``prereg/cufes_24h_wcofs_prediction_scores.json``.
#' @export
run_cufes_24h_wcofs_prediction <- function(
  root = NULL,
  scores_json = NULL,
  readout_md = NULL,
  checkpoint_dir = NULL
) {
  root <- root %||% Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  scores_json <- scores_json %||% file.path(root, "prereg", "cufes_24h_wcofs_prediction_scores.json")
  readout_md <- readout_md %||% file.path(root, "prereg", "cufes_24h_wcofs_prediction_readout.md")
  checkpoint_dir <- checkpoint_dir %||% file.path(root, "artifacts", "cufes_24h_wcofs_prediction", "checkpoints")
  species_specs <- list(
    list(label = "sardine", config = "configs/models/cufes_sardine.yaml"),
    list(label = "anchovy", config = "configs/models/cufes_anchovy.yaml")
  )
  frames <- list()
  cfgs <- list()
  for (sp in species_specs) {
    cfg <- load_config_yaml(file.path(root, sp$config))
    .ensure_barrier_land_rds(cfg, root)
    dat <- load_model_data(cfg = cfg, min_duration_min = 2, egg_split_scope = "all")
    dat <- .forecast_prepare_frame(dat, cfg)
    frames[[sp$label]] <- dat
    cfgs[[sp$label]] <- cfg
  }
  test_end <- as.Date(cfgs[[1]]$egg_split$test_end)
  locked <- forecast_lock_cutoffs(frames, test_end)
  forcing_label <- WCOFS_FORCING_PROXY
  if (identical(locked$selection$status, "ok")) {
    cutoffs <- locked$selection$cutoffs
    all_wcofs <- all(vapply(
      cutoffs,
      function(d) {
        d <- as.Date(d)
        as.Date(d) + 1L <= test_end &&
          as.Date(d) >= as.Date("2024-07-01") &&
          file.exists(.forecast_wcofs_forcing_path(root, "sardine", d))
      },
      logical(1)
    ))
    if (all_wcofs) {
      forcing_label <- WCOFS_FORCING_WCOFS
    }
  }
  manifest <- list(
    status = if (identical(locked$selection$status, "ok")) "ok" else "design_infeasible",
    claim = "24h egg-encounter forecast with WCOFS-first forcing",
    forcing_source = forcing_label,
    wcofs_lead_tag = WCOFS_24H_LEAD_TAG,
    proxy_physics_source = FORECAST_PHYSICS_SOURCE,
    design = "prereg/cufes_forecast_temporal_holdout_design.md",
    test_end = format(test_end),
    cutoffs = format(locked$selection$cutoffs),
    species = list()
  )
  if (!identical(locked$selection$status, "ok")) {
    jsonlite::write_json(manifest, scores_json, auto_unbox = TRUE, pretty = TRUE, null = "null")
    return(manifest)
  }
  species_out <- list()
  for (sp in species_specs) {
    pieces <- list()
    for (cutoff in locked$selection$cutoffs) {
      path <- file.path(checkpoint_dir, sp$label, paste0(format(as.Date(cutoff)), ".rds"))
      if (file.exists(path)) {
        pieces[[length(pieces) + 1L]] <- readRDS(path)
        next
      }
      piece <- forecast_fit_cutoff_wcofs(
        frames[[sp$label]],
        cfgs[[sp$label]],
        cutoff,
        root = root,
        label = sp$label
      )
      dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
      saveRDS(piece, path)
      pieces[[length(pieces) + 1L]] <- piece
    }
    species_out[[length(species_out) + 1L]] <- .forecast_species_wcofs_from_rows(
      sp$label,
      cfgs[[sp$label]]$species$taxon,
      sp$config,
      locked$selection$cutoffs,
      pieces,
      forcing_label
    )
  }
  manifest$species <- species_out
  manifest$pass_24h <- lapply(species_out, function(x) x$pass_24h)
  readout <- wcofs_24h_business_readout(manifest)
  jsonlite::write_json(manifest, scores_json, auto_unbox = TRUE, pretty = TRUE, null = "null")
  writeLines(readout, readout_md)
  manifest
}

#' Fit/score one cutoff using WCOFS-first operational forcing.
#' @export
forecast_fit_cutoff_wcofs <- function(dat, cfg, cutoff_date, root, label) {
  .cv_limit_tmb_threads()
  cutoff_date <- as.Date(cutoff_date)
  train <- dat[dat$event_day <= cutoff_date, , drop = FALSE]
  hold <- dat[dat$event_day %in% (cutoff_date + 1), , drop = FALSE]
  if (!nrow(train) || !nrow(hold)) {
    stop("cutoff is missing training or 24h holdout rows", call. = FALSE)
  }
  max_train <- max(as.integer(train$time_idx))
  extra <- forecast_extra_time(max_train, hold$time_idx)
  fit_cfg <- cfg
  fit_cfg$model$extra_time_slices <- extra
  mesh <- build_fishai_production_mesh(train, cfg$mesh)
  fit_res <- fit_delta_engine(train, mesh, fit_cfg)
  reason <- .cv_fit_failure_reason(fit_res)
  if (!is.null(reason)) {
    return(list(
      cutoff = format(cutoff_date),
      eligible = FALSE,
      failure = reason,
      rows = NULL
    ))
  }
  wcofs_path <- .forecast_wcofs_forcing_path(root, label, cutoff_date)
  wcofs_forcing <- NULL
  if (file.exists(wcofs_path)) {
    if (!requireNamespace("arrow", quietly = TRUE)) {
      stop("arrow package required to read WCOFS forcing parquet", call. = FALSE)
    }
    wcofs_forcing <- arrow::read_parquet(wcofs_path)
  }
  rows <- forecast_score_rows_wcofs(
    fit_res$fit,
    train,
    hold,
    cfg,
    cutoff_date,
    extra,
    wcofs_forcing = wcofs_forcing
  )
  list(
    cutoff = format(cutoff_date),
    eligible = TRUE,
    failure = NULL,
    n_train = nrow(train),
    n_holdout = nrow(hold),
    n_common_support = sum(rows$in_common_support),
    rows = rows
  )
}

#' Plain-language readout for WCOFS-first 24 h validation.
#' @export
wcofs_24h_business_readout <- function(manifest) {
  lines <- c(
    "This checks whether 24-hour-ahead egg-encounter maps beat persistence and day-of-year climatology.",
    "It is about eggs in the water, not adult fish locations, and it is not harvest advice.",
    sprintf(
      "Operational ocean forcing label for this run: %s (WCOFS lead %s when reachable; otherwise GLORYS-based damped-anomaly proxy).",
      manifest$forcing_source %||% "unknown",
      manifest$wcofs_lead_tag %||% WCOFS_24H_LEAD_TAG
    )
  )
  for (sp in manifest$species %||% list()) {
    name <- sp$label %||% "species"
    pooled <- sp$pooled
    h24 <- if (!is.null(pooled)) pooled[["24"]] else NULL
    if (is.null(h24)) {
      lines <- c(lines, sprintf("%s: no pooled 24 h scores.", name))
      next
    }
    op <- h24$operational
    per <- h24$persistence
    clim <- h24$climatology
    pass_txt <- if (isTRUE(sp$pass_24h)) "PASS" else "FAIL"
    lines <- c(
      lines,
      sprintf(
        paste0(
          "%s 24 h verdict: %s. AUC operational %s vs persistence %s vs climatology %s; ",
          "TSS operational %s vs persistence %s vs climatology %s ",
          "(n=%s common-support tows, %s with eggs)."
        ),
        name,
        pass_txt,
        .forecast_fmt(op$auc),
        .forecast_fmt(per$auc),
        .forecast_fmt(clim$auc),
        .forecast_fmt(op$tss),
        .forecast_fmt(per$tss),
        .forecast_fmt(clim$tss),
        .forecast_count(h24$n_common_support),
        .forecast_count(op$n_presence)
      )
    )
    if (!isTRUE(sp$pass_24h)) {
      lines <- c(
        lines,
        sprintf(
          "%s: maps are a pipeline demonstration only until validation passes; do not treat as a validated prediction product.",
          name
        )
      )
    }
  }
  paste(lines, collapse = "\n\n")
}
