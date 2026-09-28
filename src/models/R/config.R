#' Load and validate a FishAI model YAML config.
#' @param path Path to YAML file.
#' @return Named list (fishai_engine_config root if present).
#' @export
load_config_yaml <- function(path) {
  if (!file.exists(path)) {
    stop("config not found: ", path, call. = FALSE)
  }
  cfg <- yaml::read_yaml(path)
  if (!is.null(cfg$fishai_engine_config)) {
    cfg <- cfg$fishai_engine_config
  }
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  .abs <- function(p) {
    if (is.null(p) || grepl("^/", p)) {
      return(p)
    }
    normalizePath(file.path(root, p), mustWork = TRUE)
  }
  if (!is.null(cfg$data$table_path)) {
    cfg$data$table_path <- .abs(cfg$data$table_path)
  }
  if (!is.null(cfg$data$events_path)) {
    cfg$data$events_path <- .abs(cfg$data$events_path)
  }
  if (!is.null(cfg$data$counts_path)) {
    cfg$data$counts_path <- .abs(cfg$data$counts_path)
  }
  if (!is.null(cfg$data$covariates_path)) {
    cfg$data$covariates_path <- .abs(cfg$data$covariates_path)
  }
  if (!is.null(cfg$data$fold_assignment_path)) {
    cfg$data$fold_assignment_path <- .abs(cfg$data$fold_assignment_path)
  }
  if (!is.null(cfg$prediction$grid_table)) {
    cfg$prediction$grid_table <- .abs(cfg$prediction$grid_table)
  }
  if (!is.null(cfg$mesh$barrier$shoreline$path)) {
    p <- cfg$mesh$barrier$shoreline$path
    if (!grepl("^/", p)) {
      p <- file.path(root, p)
    }
    cfg$mesh$barrier$shoreline$path <- normalizePath(p, mustWork = FALSE)
  }
  cfg
}
