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
  cfg <- load_config_yaml(
    file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml")
  )
  if (isTRUE(intercept_only)) {
    # Honest spatial blocks can drop a time index from a training fold.
    # A random-walk time intercept then has a non-PD Hessian. This control
    # is an intercept-only delta: no spatial field and no time walk.
    cfg$model$formula_shared <- "~ 1"
    cfg$model$spatial <- list("off", "off")
    cfg$model$spatiotemporal <- list("off", "off")
    cfg$model$share_range <- list(FALSE, FALSE)
    cfg$model$time_varying <- NULL
  }
  cfg
}

synthetic_land_barrier_path <- function() {
  file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "synthetic_land_barrier.rds")
}

# Land polygon in EPSG:32611 metres: a wide frame with a hole around every
# synthetic track midpoint, so no fixture observation sits on land and any
# spatial-CV fold mesh still has barrier triangles.
synthetic_land_barrier_sf <- function() {
  ev <- utils::read.csv(
    file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "synthetic_cufes_events.csv"),
    stringsAsFactors = FALSE
  )
  mid <- .track_midpoint_km(ev$lon, ev$lat, ev$stop_lon, ev$stop_lat)
  pts <- sf::st_as_sf(
    data.frame(x = mid$X * 1000, y = mid$Y * 1000),
    coords = c("x", "y"),
    crs = 32611
  )
  water <- sf::st_buffer(sf::st_convex_hull(sf::st_union(pts)), 3000)
  bb <- sf::st_bbox(water)
  pad <- 400000
  frame <- sf::st_as_sfc(
    sf::st_bbox(
      c(xmin = bb[["xmin"]] - pad, ymin = bb[["ymin"]] - pad, xmax = bb[["xmax"]] + pad, ymax = bb[["ymax"]] + pad),
      crs = sf::st_crs(32611)
    )
  )
  sf::st_sf(geometry = sf::st_difference(frame, water))
}

write_synthetic_land_barrier <- function(path = synthetic_land_barrier_path()) {
  saveRDS(synthetic_land_barrier_sf(), path)
  invisible(path)
}
