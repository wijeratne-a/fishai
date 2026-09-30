GLORYS_REQUIRED_CMEMS <- "Generated using E.U. Copernicus Marine Service Information"
GLORYS_REQUIRED_DOI <- "10.48670/moi-00021"

#' Load data/SOURCES.yaml (or override path).
#' @export
load_sources_manifest <- function(path = NULL) {
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  path <- path %||% file.path(root, "data", "SOURCES.yaml")
  if (!file.exists(path)) {
    stop("SOURCES manifest not found: ", path, call. = FALSE)
  }
  yaml::read_yaml(path)
}

#' Resolve source records by id from the manifest.
#' @export
sources_records <- function(source_ids, manifest = NULL) {
  manifest <- manifest %||% load_sources_manifest()
  src <- manifest$sources
  if (is.null(src)) {
    stop("SOURCES.yaml has no sources block", call. = FALSE)
  }
  out <- list()
  for (sid in source_ids) {
    rec <- src[[sid]]
    if (is.null(rec)) {
      stop("unknown source id in SOURCES.yaml: ", sid, call. = FALSE)
    }
    attr_txt <- rec$attribution
    if (is.null(attr_txt) || !nzchar(trimws(attr_txt))) {
      stop("missing attribution for source: ", sid, call. = FALSE)
    }
    if (identical(sid, "glorys")) {
      validate_glorys_attribution(attr_txt)
    }
    out[[length(out) + 1L]] <- list(
      source_id = sid,
      attribution = trimws(attr_txt)
    )
  }
  out
}

#' @export
validate_glorys_attribution <- function(attribution) {
  if (!grepl(GLORYS_REQUIRED_CMEMS, attribution, fixed = TRUE)) {
    stop(
      "GLORYS attribution must include: ",
      GLORYS_REQUIRED_CMEMS,
      call. = FALSE
    )
  }
  if (!grepl(GLORYS_REQUIRED_DOI, attribution, fixed = TRUE)) {
    stop(
      "GLORYS attribution must include DOI ",
      GLORYS_REQUIRED_DOI,
      call. = FALSE
    )
  }
  invisible(TRUE)
}

#' Build training-source metadata for a frozen artifact from config + manifest.
#' @export
training_sources_metadata <- function(cfg, manifest = NULL) {
  obs_id <- cfg$training$observation_source_id %||% cfg$data$source_id
  force_id <- cfg$training$covariate_forcing_source_id %||% cfg$covariates$forcing_source_id
  if (is.null(obs_id) || is.null(force_id)) {
    stop(
      "config must set training.observation_source_id and training.covariate_forcing_source_id",
      call. = FALSE
    )
  }
  sources_records(c(obs_id, force_id), manifest = manifest)
}

#' Full attribution block for prediction outputs.
#' @export
prediction_attribution_metadata <- function(artifact, cfg, manifest = NULL) {
  train <- artifact$training_sources
  if (is.null(train) || !length(train)) {
    stop("artifact missing training_sources; refreeze with freeze_model()", call. = FALSE)
  }
  infer_id <- cfg$prediction$inference_forcing_source_id
  if (is.null(infer_id) || !nzchar(infer_id)) {
    stop("config prediction.inference_forcing_source_id is required", call. = FALSE)
  }
  infer <- sources_records(infer_id, manifest = manifest)[[1L]]
  list(
    training_sources = train,
    inference_forcing = infer
  )
}

#' Stop if any attribution string is missing (fail closed before writing outputs).
#' @export
assert_prediction_attributions <- function(meta) {
  if (is.null(meta$training_sources) || !length(meta$training_sources)) {
    stop("missing training source attributions", call. = FALSE)
  }
  for (rec in meta$training_sources) {
    if (is.null(rec$attribution) || !nzchar(trimws(rec$attribution))) {
      stop("missing attribution for training source: ", rec$source_id %||% "?", call. = FALSE)
    }
  }
  infer <- meta$inference_forcing
  if (is.null(infer) || is.null(infer$attribution) || !nzchar(trimws(infer$attribution))) {
    stop("missing inference forcing attribution", call. = FALSE)
  }
  if (identical(infer$source_id, "glorys")) {
    validate_glorys_attribution(infer$attribution)
  }
  invisible(meta)
}

.flatten_attributions_for_columns <- function(meta) {
  train_txt <- vapply(
    meta$training_sources,
    function(r) paste0(r$source_id, ": ", r$attribution),
    character(1)
  )
  list(
    metadata_attribution_training = paste(train_txt, collapse = " | "),
    metadata_attribution_inference = paste0(
      meta$inference_forcing$source_id,
      ": ",
      meta$inference_forcing$attribution
    )
  )
}
