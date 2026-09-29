#!/usr/bin/env Rscript
# Staging-only spatial-block CV dry run on bot2 training table (PR #28).
# Offshore sardine and anchovy egg and spawning-habitat pilot; egg encounter target.
# All reported metrics are EVIDENCE ONLY — NOT FOR DISPLAY. Scoring at lead 0 only.

root <- normalizePath(
  file.path(
    dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])),
    "..",
    ".."
  )
)
setwd(root)
Sys.setenv(FISHAI_ROOT = root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))

.args <- commandArgs(trailingOnly = TRUE)
parse_flag <- function(flag, default = NA_character_) {
  i <- match(flag, .args)
  if (is.na(i) || i >= length(.args)) {
    return(default)
  }
  .args[[i + 1L]]
}
has_flag <- function(flag) {
  flag %in% .args
}

species_arg <- parse_flag("--species", "both")
out_root <- parse_flag("--out-dir", file.path(root, "staging", "cv-real-run", "dry-run"))
mesh_cutoff <- as.numeric(parse_flag("--mesh-cutoff-km", NA_character_))
skip_barrier <- has_flag("--skip-barrier")
counts_only <- has_flag("--counts-only")
evidence_only <- !has_flag("--allow-display-metrics")

dir.create(out_root, recursive = TRUE, showWarnings = FALSE)

.cv_staging_publish_wording <- function(evidence_only = TRUE) {
  list(
    report_title = paste(
      "Offshore sardine and anchovy egg and spawning-habitat pilot:",
      "spatial-block CV staging dry-run report",
      "(EVIDENCE ONLY — NOT FOR DISPLAY)"
    ),
    pilot_scope = "Offshore sardine and anchovy egg and spawning-habitat pilot.",
    prediction_target_label = "egg encounter",
    scoring_lead_days = 0L,
    scoring_scope_label = "Scoring at lead 0 only.",
    evidence_only_not_for_display = isTRUE(evidence_only),
    evidence_only_label = "EVIDENCE ONLY — NOT FOR DISPLAY"
  )
}

.cv_staging_publish_notes <- function(prev_gap, evidence_only = TRUE) {
  w <- .cv_staging_publish_wording(evidence_only = evidence_only)
  c(
    w$evidence_only_label,
    w$pilot_scope,
    paste0("Prediction target: ", w$prediction_target_label, " (not species-named encounter)."),
    w$scoring_scope_label,
    prev_gap
  )
}

.species_configs <- function(sp) {
  switch(
    sp,
    sardine = file.path(root, "configs", "staging", "cufes_sardine_real_cv.yaml"),
    anchovy = file.path(root, "configs", "staging", "cufes_anchovy_real_cv.yaml"),
    stop("unknown species: ", sp, call. = FALSE)
  )
}

.run_species <- function(sp) {
  config_path <- .species_configs(sp)
  cfg <- load_config_yaml(config_path)
  if (!is.na(mesh_cutoff) && is.finite(mesh_cutoff)) {
    cfg$mesh$cutoff_km <- mesh_cutoff
  }
  cfg$output$dir <- file.path(out_root, sp)

  events <- .read_model_table(cfg$data$events_path)
  events <- .normalize_cufes_events_columns(events)
  params <- spatial_block_cv_params(cfg)
  fold_all <- assign_cufes_spatial_block_folds(events, params)

  dat_fit <- load_model_data(cfg = cfg, egg_split_scope = "fit")
  dat_fit <- .apply_log_depth_from_bottom_m(dat_fit, cfg)
  .assert_covariate_finite(dat_fit, cfg)

  fold_match <- fold_all$fold_id[match(dat_fit$event_id, fold_all$event_id)]
  if (any(is.na(fold_match))) {
    stop("missing fold_id for some fit-period modelling rows", call. = FALSE)
  }
  dat_fit$fold_id <- fold_match
  dat_fit$block_id <- fold_all$block_id[match(dat_fit$event_id, fold_all$event_id)]

  domain <- .training_domain_limits(dat_fit, events)
  dat_test <- tryCatch(
    load_model_data(cfg = cfg, egg_split_scope = "test"),
    error = function(e) NULL
  )
  if (!is.null(dat_test)) {
    dat_test <- .apply_log_depth_from_bottom_m(dat_test, cfg)
    fold_test <- fold_all$fold_id[match(dat_test$event_id, fold_all$event_id)]
    if (any(is.na(fold_test))) {
      stop("missing fold_id for some test-period modelling rows", call. = FALSE)
    }
  } else {
    fold_test <- NULL
  }

  fold_ids_all <- sort(unique(as.integer(fold_match)))
  publish <- .cv_staging_publish_wording(evidence_only)
  fold_stats <- list(
    report_section = "Per-fold egg encounter event counts (EVIDENCE ONLY — NOT FOR DISPLAY)",
    evidence_only_label = publish$evidence_only_label,
    evidence_only_not_for_display = evidence_only,
    prediction_target_label = publish$prediction_target_label,
    year_1998_note = paste0(
      "1998 nearshore exclusions (trainable table): 1,171 of 2,507 excluded events; ",
      "year_1998 egg encounter count rows below are ",
      publish$evidence_only_label,
      "."
    ),
    fit = .per_fold_event_stats_by_year(dat_fit, fold_match, fold_ids_all, 1998L),
    test = .per_fold_event_stats_by_year(dat_test, fold_test, fold_ids_all, 1998L)
  )

  if (counts_only) {
    prev_gap <- .sardine_prevalence_gap_note(cfg, events)
    return(list(
      species = sp,
      config = config_path,
      publish = publish,
      evidence_only_not_for_display = evidence_only,
      counts_only = TRUE,
      training_domain = domain,
      fold_event_stats = fold_stats,
      spatial_cv = list(
        report_section = "Spatial-block CV egg encounter scores (skipped)",
        skipped = TRUE,
        reason = "--counts-only"
      ),
      elpd_sum_loglik = NA_real_,
      elpd_eligible = FALSE,
      time_holdout = list(
        report_section = "Temporal holdout egg encounter scores (skipped)",
        skipped = TRUE,
        reason = "--counts-only"
      ),
      notes = .cv_staging_publish_notes(prev_gap, evidence_only),
      fold_failures = character(0)
    ))
  }

  land_sf <- NULL
  mesh <- build_fishai_mesh(dat_fit, cfg$mesh)
  if (isTRUE(cfg$mesh$barrier$enabled) && !skip_barrier) {
    land_path <- cfg$mesh$barrier$land_sf_rds
    if (!file.exists(land_path)) {
      stop("barrier land_sf missing: ", land_path, call. = FALSE)
    }
    land_sf <- readRDS(land_path)
    if (requireNamespace("sdmTMBextra", quietly = TRUE)) {
      mesh <- add_barrier_land(mesh, land_sf, range_fraction = cfg$mesh$barrier$range_fraction %||% 0.1)
    } else {
      stop(
        "barrier mesh requires sdmTMBextra (sdmTMB::add_barrier_mesh is defunct); ",
        "install INLA + sdmTMBextra or pass --skip-barrier for non-barrier evidence-only dry run",
        call. = FALSE
      )
    }
    check_barrier(mesh, dat_fit, land_sf = land_sf)
  }

  t0 <- proc.time()
  gc()
  cv <- run_cv_spatial(dat_fit, mesh, cfg, fold_ids = fold_match)
  elapsed <- (proc.time() - t0)[["elapsed"]]
  peak_mb <- NA_real_
  if (file.exists("/proc/self/status")) {
    st <- readLines("/proc/self/status", warn = FALSE)
    vm <- grep("^VmHWM:", st, value = TRUE)
    if (length(vm)) {
      peak_mb <- as.numeric(sub("^VmHWM:\\s+", "", vm[[1L]])) / 1024
    }
  }

  fold_scores <- .score_cv_folds_in_domain(cv, dat_fit, fold_match, cfg, domain)

  test_scores <- if (is.null(dat_test)) {
    list(skipped = TRUE, reason = "no test rows after load")
  } else {
    .score_time_holdout_in_domain(dat_fit, dat_test, mesh, cfg, domain)
  }

  prev_gap <- .sardine_prevalence_gap_note(cfg, events)

  list(
    species = sp,
    config = config_path,
    publish = publish,
    evidence_only_not_for_display = evidence_only,
    wall_seconds = as.numeric(elapsed),
    peak_rss_mb = peak_mb,
    training_domain = domain,
    fold_event_stats = fold_stats,
    spatial_cv = c(
      list(
        report_section = paste0(
          "Spatial-block CV egg encounter scores (",
          publish$evidence_only_label,
          "; ",
          publish$scoring_scope_label,
          ")"
        )
      ),
      fold_scores
    ),
    elpd_sum_loglik = cv$sum_loglik,
    elpd_eligible = cv$elpd_eligible,
    time_holdout = c(
      list(
        report_section = paste0(
          "Temporal holdout egg encounter scores (",
          publish$evidence_only_label,
          "; ",
          publish$scoring_scope_label,
          ")"
        )
      ),
      test_scores
    ),
    notes = .cv_staging_publish_notes(prev_gap, evidence_only),
    fold_failures = cv$fold_failures
  )
}

.apply_log_depth_from_bottom_m <- function(dat, cfg) {
  upstream <- cfg$covariates$upstream_fields$log_depth %||% "log_depth_z"
  if (!identical(upstream, "bottom_depth_m")) {
    return(dat)
  }
  if (!"bottom_depth_m" %in% names(dat)) {
    stop("bottom_depth_m required for log_depth covariate", call. = FALSE)
  }
  bd <- as.numeric(dat$bottom_depth_m)
  if (any(!is.finite(bd) | bd <= 0)) {
    stop("depth <= 0 or non-finite bottom_depth_m in modelling frame", call. = FALSE)
  }
  dat$log_depth_z <- log(bd)
  dat
}

.assert_covariate_finite <- function(dat, cfg) {
  cols <- .model_covariate_columns(cfg)
  upstream <- cfg$covariates$upstream_fields %||% list()
  for (mc in cols) {
    slug <- sub("_z$", "", mc)
    up <- upstream[[slug]]
    if (is.null(up)) {
      up <- mc
    }
    val <- if (mc %in% names(dat)) dat[[mc]] else dat[[up]]
    if (is.null(val)) {
      stop("missing covariate column ", mc, call. = FALSE)
    }
    if (any(is.na(val) | !is.finite(as.numeric(val)))) {
      stop("NA or non-finite covariate in ", mc, call. = FALSE)
    }
  }
  invisible(TRUE)
}

.training_domain_limits <- function(trainable_mod, events) {
  ev <- events
  if (!"dist_shore_km" %in% names(ev)) {
    stop("cufes_events missing dist_shore_km for training domain", call. = FALSE)
  }
  if (!"bottom_depth_m" %in% names(trainable_mod)) {
    stop("modelling frame missing bottom_depth_m for training domain", call. = FALSE)
  }
  ds <- as.numeric(ev$dist_shore_km[match(trainable_mod$event_id, ev$event_id)])
  bd <- as.numeric(trainable_mod$bottom_depth_m)
  if (any(!is.finite(ds)) || any(!is.finite(bd))) {
    stop("non-finite dist_shore_km or bottom_depth_m on trainable rows", call. = FALSE)
  }
  list(
    bottom_depth_m_min = min(bd),
    bottom_depth_m_max = max(bd),
    dist_shore_km_min = min(ds),
    dist_shore_km_max = max(ds)
  )
}

.in_training_domain <- function(dat, events, limits) {
  ds <- as.numeric(events$dist_shore_km[match(dat$event_id, events$event_id)])
  bd <- as.numeric(dat$bottom_depth_m)
  ds >= limits$dist_shore_km_min &
    ds <= limits$dist_shore_km_max &
    bd >= limits$bottom_depth_m_min &
    bd <= limits$bottom_depth_m_max
}

.event_calendar_year <- function(dat) {
  if (is.null(dat) || !nrow(dat) || !"time" %in% names(dat)) {
    return(integer(0))
  }
  as.integer(format(as.POSIXct(dat$time, tz = "UTC"), "%Y"))
}

.per_fold_event_stats_by_year <- function(dat, fold_ids, folds, breakout_year = 1998L) {
  folds <- sort(unique(as.integer(folds)))
  n <- if (is.null(dat) || !nrow(dat)) 0L else nrow(dat)
  if (n > 0L) {
    if (is.null(fold_ids) || length(fold_ids) != n) {
      stop("fold_ids length must match modelling rows", call. = FALSE)
    }
    years <- .event_calendar_year(dat)
    y_pos <- as.integer(dat$y > 0)
    fold_ids <- as.integer(fold_ids)
  } else {
    years <- integer(0)
    y_pos <- integer(0)
    fold_ids <- integer(0)
  }
  stats::setNames(
    lapply(folds, function(f) {
      idx_fold <- if (length(fold_ids)) fold_ids == f else rep(FALSE, n)
      idx_yr <- idx_fold & years == breakout_year
      list(
        fold_id = f,
        evidence_only_not_for_display = TRUE,
        all_years = list(
          n_events = sum(idx_fold),
          n_egg_encounter_positives = if (any(idx_fold)) sum(y_pos[idx_fold] == 1L) else 0L
        ),
        year_1998 = list(
          calendar_year = breakout_year,
          n_events = sum(idx_yr),
          n_egg_encounter_positives = if (any(idx_yr)) sum(y_pos[idx_yr] == 1L) else 0L
        )
      )
    }),
    as.character(folds)
  )
}

.optimal_tss_threshold <- function(z, p) {
  if (!length(z)) {
    return(0.5)
  }
  grid <- sort(unique(stats::quantile(p, probs = seq(0.05, 0.95, 0.05), na.rm = TRUE)))
  if (!length(grid)) {
    return(0.5)
  }
  tss <- vapply(grid, function(th) tss_at(z, p, th), numeric(1))
  grid[which.max(tss)]
}

.score_egg_encounter_block <- function(z, p, thr) {
  list(
    egg_encounter_auc = auc_mw(z, p),
    egg_encounter_tss = tss_at(z, p, thr),
    egg_encounter_boyce = cbi_continuous(p, z),
    egg_encounter_prevalence = mean(z),
    scoring_lead_days = 0L
  )
}

.score_cv_folds_in_domain <- function(cv, dat, fold_ids, cfg, domain) {
  events <- .read_model_table(cfg$data$events_path)
  events <- .normalize_cufes_events_columns(events)
  folds <- sort(unique(as.character(fold_ids)))
  out <- list()
  for (fold_id in folds) {
    test <- dat[as.character(fold_ids) == fold_id, , drop = FALSE]
    in_dom <- .in_training_domain(test, events, domain)
    z <- as.integer(test$y > 0)
    if (sum(z == 1L) < 1L) {
      out[[fold_id]] <- list(
        failed = TRUE,
        reason = "zero egg encounter positives in fold",
        n_events = nrow(test),
        n_egg_encounter_positives = sum(z == 1L)
      )
      next
    }
    train <- dat[as.character(fold_ids) != fold_id, , drop = FALSE]
    train <- train[.in_training_domain(train, events, domain), , drop = FALSE]
    z_tr <- as.integer(train$y > 0)
    if (sum(z_tr == 1L) < 1L || sum(z_tr == 0L) < 1L) {
      out[[fold_id]] <- list(failed = TRUE, reason = "training fold lacks both classes in domain")
      next
    }
    train_mesh <- build_fishai_mesh(train, cfg$mesh)
    fit_res <- tryCatch(
      fit_delta_engine(train, train_mesh, cfg),
      error = function(e) list(error = conditionMessage(e))
    )
    if (!inherits(fit_res, "fishai_fit")) {
      out[[fold_id]] <- list(failed = TRUE, reason = fit_res$error %||% "fit failed")
      next
    }
    p_tr <- score_encounter_on_events(fit_res$fit, train, cfg)
    thr <- .optimal_tss_threshold(z_tr, p_tr)
    test_dom <- test[in_dom, , drop = FALSE]
    z_te <- as.integer(test_dom$y > 0)
    if (sum(z_te == 1L) < 1L) {
      out[[fold_id]] <- list(
        failed = TRUE,
        reason = "zero egg encounter positives in domain-scored holdout",
        n_scored = nrow(test_dom),
        unknown_outside = sum(!in_dom)
      )
      next
    }
    p_te <- score_encounter_on_events(fit_res$fit, test_dom, cfg)
    sc <- .score_egg_encounter_block(z_te, p_te, thr)
    ll_fold <- cv$fold_loglik[[fold_id]]
    out[[fold_id]] <- c(
      list(
        failed = FALSE,
        n_scored = nrow(test_dom),
        unknown_outside = sum(!in_dom),
        unknown_reason = "outside_training_domain",
        elpd_fold_loglik = ll_fold,
        egg_encounter_tss_threshold = thr
      ),
      sc
    )
  }
  agg <- .aggregate_fold_scores(out)
  c(list(per_fold = out), agg)
}

.aggregate_fold_scores <- function(per_fold) {
  ok <- vapply(per_fold, function(x) isFALSE(x$failed %||% TRUE), logical(1))
  if (!any(ok)) {
    return(list(
      aggregate_evidence_only_not_for_display = list(
        egg_encounter_elpd = NA_real_,
        egg_encounter_auc = NA_real_,
        egg_encounter_tss = NA_real_,
        egg_encounter_boyce = NA_real_,
        egg_encounter_prevalence = NA_real_,
        scoring_lead_days = 0L
      )
    ))
  }
  elpd <- sum(vapply(per_fold[ok], function(x) as.numeric(x$elpd_fold_loglik), numeric(1)), na.rm = TRUE)
  auc <- mean(vapply(per_fold[ok], function(x) as.numeric(x$egg_encounter_auc), numeric(1)), na.rm = TRUE)
  tss <- mean(vapply(per_fold[ok], function(x) as.numeric(x$egg_encounter_tss), numeric(1)), na.rm = TRUE)
  boyce <- mean(vapply(per_fold[ok], function(x) as.numeric(x$egg_encounter_boyce), numeric(1)), na.rm = TRUE)
  prev <- mean(vapply(per_fold[ok], function(x) as.numeric(x$egg_encounter_prevalence), numeric(1)), na.rm = TRUE)
  list(
    aggregate_evidence_only_not_for_display = list(
      egg_encounter_elpd = elpd,
      egg_encounter_auc = auc,
      egg_encounter_tss = tss,
      egg_encounter_boyce = boyce,
      egg_encounter_prevalence = prev,
      scoring_lead_days = 0L
    )
  )
}

.score_time_holdout_in_domain <- function(dat_fit, dat_test, mesh, cfg, domain) {
  events <- .read_model_table(cfg$data$events_path)
  events <- .normalize_cufes_events_columns(events)
  fit <- fit_delta_engine(dat_fit, mesh, cfg)
  in_tr <- .in_training_domain(dat_fit, events, domain)
  train_dom <- dat_fit[in_tr, , drop = FALSE]
  z_tr <- as.integer(train_dom$y > 0)
  p_tr <- score_encounter_on_events(fit$fit, train_dom, cfg)
  thr <- .optimal_tss_threshold(z_tr, p_tr)
  in_te <- .in_training_domain(dat_test, events, domain)
  test_dom <- dat_test[in_te, , drop = FALSE]
  z_te <- as.integer(test_dom$y > 0)
  p_te <- score_encounter_on_events(fit$fit, test_dom, cfg)
  sc <- .score_egg_encounter_block(z_te, p_te, thr)
  c(
    list(
      n_scored = nrow(test_dom),
      unknown_outside = sum(!in_te),
      unknown_reason = "outside_training_domain",
      egg_encounter_tss_threshold = thr
    ),
    sc
  )
}

.sardine_prevalence_gap_note <- function(cfg, events) {
  if (cfg$species$taxon != "sardine") {
    return("sardine egg encounter prevalence gap: N/A (not sardine species run)")
  }
  counts <- .read_model_table(cfg$data$counts_path)
  cov <- .read_model_table(cfg$data$covariates_path)
  taxon <- "sardine"
  ct <- counts[counts$taxon == taxon, , drop = FALSE]
  pos_ids <- as.character(ct$event_id[as.numeric(ct$count) > 0])
  ex <- .parse_excluded_logical(cov$excluded)
  kept <- !(ex %in% TRUE)
  ev_ids <- as.character(cov$event_id)
  in_kept <- ev_ids %in% ct$event_id & kept
  in_drop <- ev_ids %in% ct$event_id & !kept
  prev_kept <- if (any(in_kept)) mean(ev_ids[in_kept] %in% pos_ids) else NA_real_
  prev_drop <- if (any(in_drop)) mean(ev_ids[in_drop] %in% pos_ids) else NA_real_
  sprintf(
    "sardine egg encounter prevalence gap: kept %.1f%% vs dropped %.1f%% (trainable covariate rows vs excluded)",
    100 * prev_kept,
    100 * prev_drop
  )
}

species_list <- if (species_arg == "both") {
  c("sardine", "anchovy")
} else {
  species_arg
}

results <- lapply(species_list, .run_species)
names(results) <- species_list

publish_root <- .cv_staging_publish_wording(evidence_only)
manifest <- list(
  publish = publish_root,
  staging_branch = "wip/cv-real-run-staging",
  evidence_only_not_for_display = evidence_only,
  evidence_only_label = publish_root$evidence_only_label,
  wall_seconds_by_species = stats::setNames(
    vapply(results, function(x) x$wall_seconds %||% NA_real_, numeric(1)),
    names(results)
  ),
  results = results
)

manifest_path <- file.path(out_root, "cufes_real_spatial_cv_staging_manifest.json")
jsonlite::write_json(manifest, manifest_path, auto_unbox = TRUE, pretty = TRUE, null = "null")
cat(
  publish_root$evidence_only_label,
  "— Wrote offshore egg encounter pilot staging manifest:",
  manifest_path,
  "\n"
)
