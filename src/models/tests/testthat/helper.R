`%||%` <- function(x, y) if (is.null(x)) y else x

.fishai_root_from_helper <- function() {
  root_env <- Sys.getenv("FISHAI_ROOT", unset = "")
  if (nzchar(root_env)) {
    return(normalizePath(root_env, mustWork = TRUE))
  }
  normalizePath(file.path(getwd()), mustWork = TRUE)
}

FISHAI_ROOT <- .fishai_root_from_helper()

load_fishaisdm <- function(root = FISHAI_ROOT) {
  root <- normalizePath(root, mustWork = TRUE)
  lib <- file.path(root, "renv", "library")
  if (dir.exists(lib)) {
    .libPaths(c(lib, .libPaths()))
  }
  act <- file.path(root, "renv", "activate.R")
  if (file.exists(act)) {
    source(act, local = FALSE)
    if (dir.exists(lib)) {
      .libPaths(c(lib, .libPaths()))
    }
  }
  r_dir <- file.path(root, "src", "models", "R")
  for (f in sort(list.files(r_dir, pattern = "\\.[Rr]$", full.names = TRUE))) {
    source(f, local = FALSE)
  }
  invisible(root)
}

load_fishaisdm(FISHAI_ROOT)

load_sardine_test_cfg <- function(intercept_only = FALSE) {
  cfg <- load_config_yaml(file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine.yaml"))
  if (isTRUE(intercept_only)) {
    cfg$model$formula_shared <- "~ 1"
    cfg$model$spatial <- list("off", "off")
    cfg$model$spatiotemporal <- list("off", "off")
  }
  cfg
}
