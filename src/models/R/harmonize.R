#' Load GLORYS/WCOFS harmonization config.
#' @export
load_harmonize_config <- function(path = NULL) {
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  path <- path %||% file.path(root, "configs", "harmonize.yaml")
  if (!file.exists(path)) {
    stop("harmonize config not found: ", path, call. = FALSE)
  }
  raw <- yaml::read_yaml(path)
  cfg <- raw$glorys_wcofs_harmonization
  if (is.null(cfg)) {
    stop("missing glorys_wcofs_harmonization block in ", path, call. = FALSE)
  }
  cfg$config_path <- normalizePath(path, mustWork = TRUE)
  if (!is.null(cfg$data$pairs_table) && !grepl("^/", cfg$data$pairs_table)) {
    cfg$data$pairs_table <- normalizePath(file.path(root, cfg$data$pairs_table), mustWork = TRUE)
  }
  if (!is.null(cfg$output$maps_rds) && !grepl("^/", cfg$output$maps_rds)) {
    cfg$output$maps_rds <- file.path(root, cfg$output$maps_rds)
  }
  cfg
}

.harmonize_covariate_defs <- function(cfg) {
  defs <- cfg$covariates
  if (is.null(defs) || !length(defs)) {
    stop("harmonize config missing covariates", call. = FALSE)
  }
  defs
}

.paired_columns <- function(def) {
  gcol <- paste0(def$glorys_column, "_glorys")
  wcol <- paste0(def$wcofs_column, "_wcofs")
  list(glorys = gcol, wcofs = wcol, id = def$id, model_z = def$model_z)
}

#' @export
load_harmonize_pairs <- function(cfg) {
  path <- cfg$data$pairs_table
  if (is.null(path) || !file.exists(path)) {
    stop("harmonize pairs_table not found", call. = FALSE)
  }
  dat <- utils::read.csv(path, stringsAsFactors = FALSE)
  tcol <- cfg$data$time_column %||% "time"
  if (!tcol %in% names(dat)) {
    stop("pairs table missing time column: ", tcol, call. = FALSE)
  }
  dat$.time_ord <- as.numeric(as.POSIXct(dat[[tcol]], tz = "UTC"))
  if (any(!is.finite(dat$.time_ord))) {
    stop("could not parse harmonize pair times", call. = FALSE)
  }
  dat[order(dat$.time_ord), , drop = FALSE]
}

#' @export
split_overlap_periods <- function(pairs, cfg) {
  frac <- cfg$overlap$train_fraction %||% 0.6
  if (!is.finite(frac) || frac <= 0 || frac >= 1) {
    stop("overlap.train_fraction must be in (0, 1)", call. = FALSE)
  }
  n <- nrow(pairs)
  cut <- max(1L, floor(n * frac))
  if (cut >= n) {
    stop("overlap train_fraction leaves no holdout rows", call. = FALSE)
  }
  list(
    train = pairs[seq_len(cut), , drop = FALSE],
    holdout = pairs[seq.int(cut + 1L, n), , drop = FALSE]
  )
}

.harmonize_stratum <- function(g, w, nearshore, dist, near_km) {
  ok <- is.finite(g) & is.finite(w)
  if (!is.null(dist) && !is.null(nearshore)) {
    if (isTRUE(nearshore)) {
      ok <- ok & dist <= near_km
    } else {
      ok <- ok & dist > near_km
    }
  }
  g <- g[ok]
  w <- w[ok]
  if (length(g) < 2L) {
    return(list(
      n = length(g),
      mean_offset = NA_real_,
      sd_ratio = NA_real_,
      correlation = NA_real_
    ))
  }
  list(
    n = length(g),
    mean_offset = mean(w - g),
    sd_ratio = stats::sd(w) / stats::sd(g),
    correlation = stats::cor(g, w)
  )
}

#' Mean offset (WCOFS − GLORYS), SD ratio, and correlation by stratum.
#' @export
compute_harmonize_diagnostics <- function(pairs, cfg) {
  near_km <- cfg$nearshore_max_km %||% 20
  dcol <- cfg$data$dist_shore_column %||% "dist_shore_km"
  dist <- if (dcol %in% names(pairs)) as.numeric(pairs[[dcol]]) else NULL
  out <- list()
  for (def in .harmonize_covariate_defs(cfg)) {
    cols <- .paired_columns(def)
    g <- as.numeric(pairs[[cols$glorys]])
    w <- as.numeric(pairs[[cols$wcofs]])
    out[[def$id]] <- list(
      overall = .harmonize_stratum(g, w, NULL, NULL, near_km),
      nearshore = .harmonize_stratum(g, w, TRUE, dist, near_km),
      offshore = .harmonize_stratum(g, w, FALSE, dist, near_km)
    )
  }
  out
}

.fit_quantile_knots <- function(wcofs, glorys) {
  ok <- is.finite(wcofs) & is.finite(glorys)
  wcofs <- wcofs[ok]
  glorys <- glorys[ok]
  if (length(wcofs) < 5L) {
    return(NULL)
  }
  o <- order(wcofs)
  wcofs <- wcofs[o]
  glorys <- glorys[o]
  wu <- stats::aggregate(glorys ~ wcofs, data = data.frame(wcofs = wcofs, glorys = glorys), FUN = median)
  list(
    wcofs_knots = as.numeric(wu$wcofs),
    glorys_knots = as.numeric(wu$glorys),
    wcofs_min = min(wu$wcofs),
    wcofs_max = max(wu$wcofs),
    glorys_mu = mean(glorys),
    glorys_sd = stats::sd(glorys)
  )
}

#' Fit per-covariate, per-season empirical quantile maps on training overlap only.
#' @export
fit_season_quantile_maps <- function(train_pairs, cfg) {
  scol <- cfg$data$season_column %||% "season"
  if (!scol %in% names(train_pairs)) {
    stop("pairs table missing season column: ", scol, call. = FALSE)
  }
  seasons <- cfg$seasons
  maps <- list()
  for (def in .harmonize_covariate_defs(cfg)) {
    cols <- .paired_columns(def)
    maps[[def$id]] <- list()
    for (s in seasons) {
      sub <- train_pairs[train_pairs[[scol]] == s, , drop = FALSE]
      knots <- .fit_quantile_knots(sub[[cols$wcofs]], sub[[cols$glorys]])
      maps[[def$id]][[s]] <- knots
    }
  }
  maps
}

#' Apply quantile map without extrapolation (out-of-range -> NA + harmonize OOD).
#' @export
apply_season_quantile_map <- function(wcofs_values, map, season = NULL) {
  x <- as.numeric(wcofs_values)
  n <- length(x)
  if (is.null(map) || is.null(map$wcofs_knots) || length(map$wcofs_knots) < 2L) {
    return(list(
      glorys = rep(NA_real_, n),
      harmonize_ood = rep(3L, n)
    ))
  }
  out <- rep(NA_real_, n)
  ood <- rep(0L, n)
  in_rng <- is.finite(x) & x >= map$wcofs_min & x <= map$wcofs_max
  if (any(in_rng)) {
    out[in_rng] <- stats::approx(
      map$wcofs_knots,
      map$glorys_knots,
      xout = x[in_rng],
      rule = 1
    )$y
  }
  ood[is.finite(x) & (x < map$wcofs_min | x > map$wcofs_max)] <- 3L
  ood[!is.finite(x)] <- 3L
  list(glorys = out, harmonize_ood = ood)
}

.harmonize_skill_row <- function(obs, pred) {
  ok <- is.finite(obs) & is.finite(pred)
  obs <- obs[ok]
  pred <- pred[ok]
  if (length(obs) < 2L) {
    return(list(n = length(obs), correlation = NA_real_, rmse = NA_real_, bias = NA_real_))
  }
  list(
    n = length(obs),
    correlation = stats::cor(obs, pred),
    rmse = sqrt(mean((pred - obs)^2)),
    bias = mean(pred - obs)
  )
}

#' Score held-out overlap by season (maps must be fit on disjoint training period).
#' @export
score_harmonization_maps <- function(holdout_pairs, maps, cfg) {
  scol <- cfg$data$season_column %||% "season"
  scores <- list()
  for (def in .harmonize_covariate_defs(cfg)) {
    cols <- .paired_columns(def)
    obs <- as.numeric(holdout_pairs[[cols$glorys]])
    pred <- rep(NA_real_, length(obs))
    for (i in seq_along(pred)) {
      s <- holdout_pairs[[scol]][i]
      mp <- maps[[def$id]][[s]]
      pred[i] <- apply_season_quantile_map(holdout_pairs[[cols$wcofs]][i], mp)$glorys
    }
    by_season <- list()
    for (s in unique(holdout_pairs[[scol]])) {
      idx <- holdout_pairs[[scol]] == s
      by_season[[s]] <- .harmonize_skill_row(obs[idx], pred[idx])
    }
    scores[[def$id]] <- c(list(overall = .harmonize_skill_row(obs, pred)), by_season)
  }
  scores
}

.threshold_active <- function(thr) {
  if (is.null(thr)) {
    return(FALSE)
  }
  if (is.list(thr)) {
    vals <- unlist(thr)
    vals <- vals[!is.null(vals)]
    if (!length(vals)) {
      return(FALSE)
    }
    return(any(vapply(vals, function(v) is.finite(as.numeric(v)), logical(1L))))
  }
  is.finite(as.numeric(thr))
}

#' Drop covariates whose held-out skill fails configured thresholds (null = TODO-audit, no drop).
#' @export
drop_covariates_by_skill <- function(scores, cfg) {
  thr <- cfg$skill_thresholds %||% list()
  active <- vapply(.harmonize_covariate_defs(cfg), function(d) d$id, character(1L))
  dropped <- character()
  reasons <- list()
  for (id in active) {
    t <- thr[[id]]
    if (!.threshold_active(t)) {
      next
    }
    sc <- scores[[id]]$overall
    fail <- FALSE
    msg <- character()
    if (!is.null(t$min_correlation) && .threshold_active(t$min_correlation)) {
      if (!is.finite(sc$correlation) || sc$correlation < as.numeric(t$min_correlation)) {
        fail <- TRUE
        msg <- c(msg, "correlation below min_correlation")
      }
    }
    if (!is.null(t$max_rmse) && .threshold_active(t$max_rmse)) {
      if (!is.finite(sc$rmse) || sc$rmse > as.numeric(t$max_rmse)) {
        fail <- TRUE
        msg <- c(msg, "rmse above max_rmse")
      }
    }
    if (fail) {
      dropped <- c(dropped, id)
      reasons[[id]] <- msg
      active <- setdiff(active, id)
    }
  }
  list(active_covariates = active, dropped_covariates = dropped, drop_reasons = reasons)
}

#' @export
harmonize_maps_content_hash <- function(maps) {
  tmp <- tempfile(fileext = ".rds")
  on.exit(unlink(tmp), add = TRUE)
  saveRDS(maps, tmp)
  as.character(tools::md5sum(tmp))
}

#' Freeze fitted quantile maps with version and content hash.
#' @export
freeze_harmonize_maps <- function(
  maps,
  cfg,
  diagnostics = NULL,
  scores = NULL,
  selection = NULL,
  path = NULL
) {
  path <- path %||% cfg$output$maps_rds
  if (is.null(path)) {
    stop("harmonize output.maps_rds not set", call. = FALSE)
  }
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  payload <- list(
    version = cfg$version,
    training_forcing = cfg$training_forcing,
    inference_forcing = cfg$inference_forcing,
    maps = maps,
    diagnostics = diagnostics,
    holdout_scores = scores,
    selection = selection,
    frozen_at = format(Sys.time(), tz = "UTC", usetz = TRUE)
  )
  payload$content_hash <- harmonize_maps_content_hash(payload$maps)
  saveRDS(payload, path)
  invisible(payload)
}

#' @export
load_harmonize_maps <- function(path) {
  if (is.null(path) || !file.exists(path)) {
    stop("harmonize maps not found: ", path, call. = FALSE)
  }
  readRDS(path)
}

.harmonization_meta <- function(artifact, cfg) {
  art <- artifact$harmonization %||% list()
  pred <- cfg$harmonization %||% list()
  list(
    maps_path = art$maps_path %||% pred$maps_path,
    maps_version = art$maps_version %||% pred$maps_version,
    maps_hash = art$maps_hash %||% pred$maps_hash,
    active_covariates = art$active_covariates %||% pred$active_covariates,
    inference_forcing = cfg$prediction$inference_forcing_source_id %||% cfg$harmonization$inference_forcing
  )
}

.inference_requires_harmonization <- function(cfg) {
  inf <- cfg$prediction$inference_forcing_source_id %||% "glorys"
  train <- cfg$training$covariate_forcing_source_id %||% cfg$covariates$forcing_source_id %||% "glorys"
  tolower(inf) == "wcofs" && tolower(train) == "glorys"
}

#' Whether daily inference uses WCOFS while training used GLORYS (harmonization required).
#' @export
inference_requires_harmonization <- function(cfg) {
  .inference_requires_harmonization(cfg)
}

#' Refuse prediction when WCOFS inference requires missing or mismatched harmonization maps.
#' @export
assert_harmonization_for_predict <- function(artifact, cfg) {
  if (!.inference_requires_harmonization(cfg)) {
    return(invisible(NULL))
  }
  meta <- .harmonization_meta(artifact, cfg)
  if (is.null(meta$maps_path) || !nzchar(meta$maps_path)) {
    stop(
      "prediction requires harmonization maps (WCOFS inference vs GLORYS training)",
      call. = FALSE
    )
  }
  if (!file.exists(meta$maps_path)) {
    stop("harmonization maps file missing: ", meta$maps_path, call. = FALSE)
  }
  frozen <- load_harmonize_maps(meta$maps_path)
  exp_ver <- meta$maps_version
  if (is.null(exp_ver) || !nzchar(exp_ver) || !identical(frozen$version, exp_ver)) {
    stop(
      "harmonization maps version mismatch (artifact/config vs frozen maps)",
      call. = FALSE
    )
  }
  exp_hash <- meta$maps_hash
  if (is.null(exp_hash) || !nzchar(exp_hash) || !identical(frozen$content_hash, exp_hash)) {
    stop("harmonization maps content_hash mismatch", call. = FALSE)
  }
  invisible(frozen)
}

.standardize_glorys <- function(raw, mu, sd) {
  if (!is.finite(sd) || sd <= 0) {
    return(rep(NA_real_, length(raw)))
  }
  (raw - mu) / sd
}

#' Apply harmonization to inference grid; returns grid with model_z columns updated.
#' @export
harmonize_inference_grid <- function(grid, harmonize_bundle, cfg, season = NULL) {
  defs <- .harmonize_covariate_defs(cfg)
  active <- harmonize_bundle$selection$active_covariates
  if (is.null(active)) {
    active <- vapply(defs, function(d) d$id, character(1L))
  }
  maps <- harmonize_bundle$maps
  scol <- cfg$harmonization$season_column %||% cfg$data$season_column %||% "season"
  if (is.null(season)) {
    if (scol %in% names(grid)) {
      season <- grid[[scol]]
    } else {
      season <- rep(cfg$seasons[[1L]], nrow(grid))
    }
  }
  harmonize_ood <- rep(0L, nrow(grid))
  for (def in defs) {
    if (!(def$id %in% active)) {
      next
    }
    wraw_col <- cfg$harmonization$wcofs_raw_columns[[def$id]] %||% paste0(def$wcofs_column, "_wcofs")
    if (!wraw_col %in% names(grid)) {
      stop("inference grid missing WCOFS raw column: ", wraw_col, call. = FALSE)
    }
    zcol <- def$model_z
    if (!zcol %in% names(grid)) {
      grid[[zcol]] <- NA_real_
    }
    for (i in seq_len(nrow(grid))) {
      s <- season[i]
      mp <- maps[[def$id]][[s]]
      if (is.null(mp)) {
        mp <- maps[[def$id]][[cfg$seasons[[1L]]]]
      }
      res <- apply_season_quantile_map(grid[[wraw_col]][i], mp)
      harmonize_ood[i] <- pmax(harmonize_ood[i], res$harmonize_ood[i])
      grid[[zcol]][i] <- .standardize_glorys(res$glorys, mp$glorys_mu, mp$glorys_sd)
    }
  }
  grid$harmonize_ood <- harmonize_ood
  grid
}

#' Merge harmonization extrapolation flags with GLORYS-envelope OOD on corrected covariates.
#' @export
harmonize_envelope_ood <- function(grid, reference, reference_cols, cfg) {
  if (is.null(reference) || is.null(reference_cols)) {
    stop("GLORYS training reference required for harmonized envelope OOD", call. = FALSE)
  }
  lvl <- if ("harmonize_ood" %in% names(grid)) {
    as.integer(grid$harmonize_ood)
  } else {
    rep(0L, nrow(grid))
  }
  ok <- stats::complete.cases(grid[, reference_cols, drop = FALSE])
  if (any(ok)) {
    sub <- grid[ok, , drop = FALSE]
    mess <- mess_scores(sub[, reference_cols, drop = FALSE], reference)
    ex <- exdet_scores(sub[, reference_cols, drop = FALSE], reference)
    maha <- maha_distance(sub[, reference_cols, drop = FALSE], reference)
    hull <- convex_hull_flags(
      sub[, reference_cols, drop = FALSE],
      reference,
      pairs = cfg$ood$hull_pairs %||% list(c("temp_3m_z", "sal_3m_z"))
    )
    lvl_ok <- classify_ood_level(
      mess$mess,
      ex$nt1,
      ex$nt2,
      maha,
      hull,
      mess_mask_below = cfg$ood$mess_mask_below %||% -20
    )
    lvl[ok] <- pmax(lvl[ok], lvl_ok)
  }
  lvl[!ok] <- pmax(lvl[!ok], 3L)
  lvl
}

#' End-to-end harmonization gate on synthetic overlap (diagnostics, fit, score, freeze).
#' @export
run_harmonization_gate <- function(harmonize_cfg = NULL, path_override = NULL) {
  cfg <- load_harmonize_config(harmonize_cfg)
  pairs <- load_harmonize_pairs(cfg)
  diagnostics <- compute_harmonize_diagnostics(pairs, cfg)
  split <- split_overlap_periods(pairs, cfg)
  maps <- fit_season_quantile_maps(split$train, cfg)
  scores <- score_harmonization_maps(split$holdout, maps, cfg)
  selection <- drop_covariates_by_skill(scores, cfg)
  out_path <- path_override %||% cfg$output$maps_rds
  payload <- freeze_harmonize_maps(
    maps,
    cfg,
    diagnostics = diagnostics,
    scores = scores,
    selection = selection,
    path = out_path
  )
  if (!is.null(cfg$output$diagnostics_json)) {
    root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
    dj <- cfg$output$diagnostics_json
    if (!grepl("^/", dj)) {
      dj <- file.path(root, dj)
    }
    dir.create(dirname(dj), recursive = TRUE, showWarnings = FALSE)
    jsonlite::write_json(
      list(diagnostics = diagnostics, scores = scores, selection = selection),
      dj,
      auto_unbox = TRUE,
      pretty = TRUE,
      null = "null"
    )
  }
  c(payload, list(diagnostics = diagnostics, scores = scores, selection = selection))
}

#' Attach harmonization metadata to a model config list (for freeze_model).
#' @export
attach_harmonization_metadata <- function(cfg, maps_path, harmonize_cfg = NULL) {
  hcfg <- load_harmonize_config(harmonize_cfg)
  frozen <- load_harmonize_maps(maps_path)
  cfg$harmonization <- list(
    maps_path = normalizePath(maps_path, mustWork = TRUE),
    maps_version = frozen$version,
    maps_hash = frozen$content_hash,
    active_covariates = frozen$selection$active_covariates,
    training_forcing = hcfg$training_forcing,
    inference_forcing = hcfg$inference_forcing,
    config_path = hcfg$config_path
  )
  cfg
}
