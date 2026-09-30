#' Resolve required on-disk inputs for real-table spatial-block CV.
#' @keywords internal
.real_table_input_paths <- function(cfg, wcofs_artifact_rel = "data/derived/physics/wcofs_h_glorys_pilot.zarr") {
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  abs_path <- function(p) {
    if (is.null(p) || !nzchar(p)) {
      return(NA_character_)
    }
    if (grepl("^/", p)) {
      return(normalizePath(p, mustWork = FALSE))
    }
    normalizePath(file.path(root, p), mustWork = FALSE)
  }
  list(
    events_path = abs_path(cfg$data$events_path),
    counts_path = abs_path(cfg$data$counts_path),
    covariates_path = abs_path(cfg$data$covariates_path),
    covariate_drops_path = abs_path(cfg$data$covariate_drops_path),
    covariate_drop_summary_path = abs_path(cfg$data$covariate_drop_summary_path),
    wcofs_h_artifact = abs_path(wcofs_artifact_rel)
  )
}

#' List missing files required before real-table spatial-block CV may run.
#' @export
missing_real_table_cv_inputs <- function(cfg, wcofs_artifact_rel = "data/derived/physics/wcofs_h_glorys_pilot.zarr") {
  paths <- .real_table_input_paths(cfg, wcofs_artifact_rel)
  missing <- character()
  for (nm in c(
    "events_path",
    "counts_path",
    "covariates_path",
    "covariate_drops_path",
    "covariate_drop_summary_path"
  )) {
    p <- paths[[nm]]
    if (is.na(p) || !nzchar(p) || !file.exists(p)) {
      missing <- c(missing, if (is.na(p) || !nzchar(p)) nm else p)
    }
  }
  wcofs <- paths$wcofs_h_artifact
  if (is.na(wcofs) || !nzchar(wcofs) || !dir.exists(wcofs)) {
    missing <- c(missing, if (is.na(wcofs) || !nzchar(wcofs)) "wcofs_h_artifact" else wcofs)
  }
  missing
}

.spatial_block_oof_predictions <- function(dat, cfg, fold_ids) {
  fold_assignment <- .assert_supplied_folds_match_assignment(dat, fold_ids, cfg)
  dat$fold_id <- fold_assignment$fold_id
  dat$block_id <- fold_assignment$block_id
  .assert_cv_fold_assignment_contract(dat, fold_assignment$fold_id, cfg)
  folds <- sort(unique(as.character(fold_assignment$fold_id)))
  pred_chunks <- list()
  for (fold_id in folds) {
    train <- dat[as.character(dat$fold_id) != fold_id, , drop = FALSE]
    test <- dat[as.character(dat$fold_id) == fold_id, , drop = FALSE]
    pre <- .cv_spatial_preflight(train, test, fold_id)
    if (!is.null(pre)) {
      next
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
        fit_delta_engine(train, mesh_fold, cfg)
      },
      error = function(e) {
        structure(list(message = conditionMessage(e)), class = "cv_fold_error")
      }
    )
    if (inherits(fit_res, "cv_fold_error")) {
      next
    }
    fit_reason <- .cv_fit_failure_reason(fit_res)
    if (!is.null(fit_reason)) {
      next
    }
    p <- tryCatch(score_encounter_on_events(fit_res$fit, test, cfg), error = function(e) NULL)
    if (is.null(p)) {
      next
    }
    pred_chunks[[fold_id]] <- data.frame(
      event_id = as.character(test$event_id),
      fold_id = as.integer(test$fold_id),
      z = as.integer(test$y > 0),
      p = as.numeric(p),
      stringsAsFactors = FALSE
    )
  }
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

#' Spatial-block CV scores on the production CUFES × GLORYS training table.
#'
#' Uses [run_cv_spatial()] for ELPD (sum of fold log-likelihoods) and the same
#' fold assignment as modeling. Discrimination metrics (Boyce, AUC, TSS) use
#' out-of-fold encounter probabilities from successful holdout folds only.
#' @export
compute_spatial_block_cv_scores <- function(
  cfg,
  min_duration_min = 2L,
  wcofs_artifact_rel = "data/derived/physics/wcofs_h_glorys_pilot.zarr"
) {
  missing <- missing_real_table_cv_inputs(cfg, wcofs_artifact_rel)
  if (length(missing)) {
    return(list(
      status = "blocked",
      missing_inputs = missing,
      elpd = NA_real_,
      elpd_eligible = FALSE,
      elpd_ineligible_reason = "missing_real_table_inputs",
      boyce = NA_real_,
      auc = NA_real_,
      tss = NA_real_
    ))
  }

  dat <- load_model_data(cfg = cfg, min_duration_min = min_duration_min, egg_split_scope = "fit")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  if (isTRUE(cfg$mesh$barrier$enabled)) {
    land_path <- cfg$mesh$barrier$land_sf_rds
    if (!is.null(land_path) && nzchar(land_path) && file.exists(land_path)) {
      land_sf <- readRDS(land_path)
      mesh <- add_barrier_land(mesh, land_sf, range_fraction = cfg$mesh$barrier$range_fraction %||% 0.1)
    }
  }
  cv <- run_cv_spatial(dat, mesh, cfg, fold_ids = dat$fold_id)
  oof <- .spatial_block_oof_predictions(dat, cfg, dat$fold_id)

  boyce <- NA_real_
  auc <- NA_real_
  tss <- NA_real_
  if (nrow(oof)) {
    z <- oof$z
    p <- oof$p
    if (any(z == 1L) && any(z == 0L)) {
      boyce <- cbi_continuous(p, p[z == 1L])
      auc <- auc_mw(z, p)
      tss <- tss_at(z, p, 0.5)
    }
  }

  elpd <- cv$sum_loglik
  eligible <- isTRUE(cv$elpd_eligible) && is.finite(as.numeric(elpd))
  if (!eligible) {
    elpd <- NA_real_
  }

  list(
    status = "ok",
    missing_inputs = character(),
    n_fit_rows = nrow(dat),
    elpd = elpd,
    elpd_eligible = eligible,
    elpd_ineligible_reason = cv$elpd_ineligible_reason,
    n_failed_folds = cv$n_failed_folds,
    fold_loglik = cv$fold_loglik,
    n_oof_rows = nrow(oof),
    boyce = boyce,
    auc = auc,
    tss = tss,
    fold_assignment = cv$fold_assignment,
    spatial_block_cv = cv$spatial_block_cv
  )
}

#' Load spatial-block CV score protocol YAML.
#' @export
load_spatial_block_cv_scores_protocol <- function(path = NULL) {
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  path <- path %||% file.path(root, "configs", "spatial_block_cv_scores.yaml")
  if (!file.exists(path)) {
    stop("spatial-block CV scores protocol not found: ", path, call. = FALSE)
  }
  raw <- yaml::read_yaml(path)
  proto <- raw$spatial_block_cv_scores
  if (is.null(proto)) {
    stop("missing spatial_block_cv_scores block in ", path, call. = FALSE)
  }
  proto$config_path <- normalizePath(path, mustWork = TRUE)
  proto
}

#' Run spatial-block CV for all configured species; write JSON report.
#' @export
run_spatial_block_cv_scores <- function(protocol_path = NULL, output_override = NULL) {
  protocol <- load_spatial_block_cv_scores_protocol(protocol_path)
  if (!is.null(output_override)) {
    protocol$output <- utils::modifyList(protocol$output, output_override)
  }
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  wcofs_rel <- protocol$wcofs_h_artifact %||% "data/derived/physics/wcofs_h_glorys_pilot.zarr"
  min_dur <- protocol$min_duration_min %||% 2L

  cfg_ref <- load_config_yaml(protocol$species[[1L]]$model_config)
  missing_global <- missing_real_table_cv_inputs(cfg_ref, wcofs_rel)
  fold_csv <- protocol$output$fold_assignment_csv
  if (is.null(fold_csv) || !nzchar(fold_csv)) {
    stop("protocol output.fold_assignment_csv is required", call. = FALSE)
  }
  if (!grepl("^/", fold_csv)) {
    fold_csv <- file.path(root, fold_csv)
  }
  spatial_params <- NULL
  fold_sha <- NA_character_
  if (!length(missing_global)) {
    events_ref <- .read_model_table(cfg_ref$data$events_path)
    events_ref <- .normalize_cufes_events_columns(events_ref)
    .validate_cufes_events_schema(events_ref)
    if (!is.null(protocol$event_count_guard)) {
      .assert_event_count_guard(events_ref, protocol$event_count_guard, "reference")
    }
    spatial_params <- spatial_block_cv_params(cfg_ref)
    fold_assignment <- assign_cufes_spatial_block_folds(events_ref, spatial_params)
    dir.create(dirname(fold_csv), recursive = TRUE, showWarnings = FALSE)
    write_fold_assignment_csv(fold_assignment, fold_csv)
    fold_sha <- file_sha256(fold_csv)
  }

  species_out <- lapply(protocol$species, function(sp) {
    cfg <- load_config_yaml(sp$model_config)
    if (!length(missing_global)) {
      cfg$data$fold_assignment_path <- fold_csv
    }
    if (!is.null(protocol$event_count_guard)) {
      cfg$data$event_count_guard <- protocol$event_count_guard
    }
    scores <- compute_spatial_block_cv_scores(cfg, min_duration_min = min_dur, wcofs_artifact_rel = wcofs_rel)
    c(
      list(
        label = sp$label %||% sp$taxon,
        taxon = cfg$species$taxon,
        model_config = sp$model_config
      ),
      scores
    )
  })

  blocked <- any(vapply(species_out, function(x) identical(x$status, "blocked"), logical(1)))
  out_json <- protocol$output$scores_json
  if (!grepl("^/", out_json)) {
    out_json <- file.path(root, out_json)
  }
  dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)

  manifest <- list(
    status = if (blocked) "blocked" else "ok",
    code_sha = Sys.getenv("GITHUB_SHA", unset = NA_character_),
    evidence_manifest = protocol$evidence_manifest,
    training_table_builder_code_sha = "88083dedb099482d2f149d264a1e12f0f337f13e",
    protocol_config = protocol$config_path,
    spatial_block_cv = spatial_params,
    fold_assignment_csv = fold_csv,
    fold_assignment_sha256 = fold_sha,
    min_duration_min = min_dur,
    wcofs_h_artifact = wcofs_rel,
    species = species_out
  )
  if (blocked) {
    manifest$missing_inputs <- unique(unlist(lapply(species_out, `[[`, "missing_inputs")))
  }

  jsonlite::write_json(manifest, out_json, auto_unbox = TRUE, pretty = TRUE, null = "null")
  invisible(manifest)
}
