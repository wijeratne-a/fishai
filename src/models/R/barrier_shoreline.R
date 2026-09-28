#' Frozen pilot shoreline for Bakka barrier meshes (same artifact as PR #7 coverage).
#'
#' Polygons are read from ``mesh.barrier.shoreline.path``; ``mesh.barrier.shoreline.sha256``
#' must match the file bytes before any barrier mesh is built.

BARRIER_SHORELINE_SHA256_PLACEHOLDER <- "TO_BE_SET_FROM_PR7"

#' @export
barrier_shoreline_is_placeholder_sha256 <- function(expected) {
  val <- tolower(trimws(as.character(expected %||% "")))
  ph <- tolower(BARRIER_SHORELINE_SHA256_PLACEHOLDER)
  !nzchar(val) || identical(val, ph)
}

.barrier_shoreline_cfg <- function(cfg) {
  barrier <- cfg$mesh$barrier
  if (is.null(barrier) || !isTRUE(barrier$enabled)) {
    stop("mesh.barrier.enabled must be TRUE to load barrier shoreline", call. = FALSE)
  }
  sl <- barrier$shoreline
  if (is.null(sl) || is.null(sl$path) || !nzchar(as.character(sl$path))) {
    stop("mesh.barrier.shoreline.path is required", call. = FALSE)
  }
  if (is.null(sl$sha256)) {
    stop("mesh.barrier.shoreline.sha256 is required", call. = FALSE)
  }
  list(
    path = as.character(sl$path),
    expected_sha256 = tolower(trimws(as.character(sl$sha256)))
  )
}

#' @export
verify_barrier_shoreline_sha256 <- function(path, expected_sha256) {
  expected_sha256 <- tolower(trimws(as.character(expected_sha256)))
  if (barrier_shoreline_is_placeholder_sha256(expected_sha256)) {
    stop(
      "mesh.barrier.shoreline.sha256 is still placeholder; pin PR #7 frozen shoreline hash before building barrier mesh",
      call. = FALSE
    )
  }
  if (!file.exists(path)) {
    stop("barrier shoreline file not found: ", path, call. = FALSE)
  }
  actual <- file_sha256(path)
  if (!identical(actual, expected_sha256)) {
    stop(
      "barrier shoreline sha256 mismatch; expected ",
      expected_sha256,
      " got ",
      actual,
      call. = FALSE
    )
  }
  invisible(actual)
}

#' Load barrier land ``sf`` in EPSG:32611 metres (mesh km units × 1000 at barrier call).
#' @export
load_barrier_land_sf <- function(cfg) {
  if (!requireNamespace("sf", quietly = TRUE)) {
    stop("sf is required to load barrier shoreline", call. = FALSE)
  }
  meta <- .barrier_shoreline_cfg(cfg)
  path <- meta$path
  verify_barrier_shoreline_sha256(path, meta$expected_sha256)
  land <- sf::st_read(path, quiet = TRUE)
  if (is.na(sf::st_crs(land))) {
    sf::st_crs(land) <- 4326
  }
  land <- sf::st_transform(land, 32611)
  land <- sf::st_make_valid(land)
  land
}

#' Build mesh and optional barrier using verified frozen shoreline.
#' @export
build_fishai_mesh_with_barrier <- function(dat, cfg) {
  mesh_cfg <- cfg$mesh %||% list()
  mesh <- build_fishai_mesh(dat, mesh_cfg)
  if (!isTRUE(mesh_cfg$barrier$enabled)) {
    return(mesh)
  }
  land_sf <- load_barrier_land_sf(cfg)
  rf <- mesh_cfg$barrier$range_fraction %||% 0.1
  bmesh <- add_barrier_land(mesh, land_sf, range_fraction = rf)
  check_barrier(bmesh, dat, land_sf = land_sf)
  bmesh
}
