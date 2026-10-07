#' Build an fmesher / sdmTMB mesh with cutoff at least 9 km.
#' @param dat Data with X, Y in km.
#' @param cfg Mesh config list.
#' @return sdmTMB mesh object.
#' @export
build_fishai_mesh <- function(dat, cfg = list()) {
  cutoff_km <- cfg$cutoff_km %||% cfg$cutoff %||% 9
  if (cutoff_km < 9) {
    stop("mesh cutoff must be >= 9 km for ~9 km covariate grid", call. = FALSE)
  }
  range_guess <- cfg$range_guess_km %||% 60
  inner <- range_guess / 6
  sdmTMB::make_mesh(
    dat,
    xy_cols = c("X", "Y"),
    cutoff = cutoff_km,
    mesh_args = list(
      max.edge = c(inner, range_guess * 1.5),
      offset = c(-0.02, 1.5 * range_guess)
    )
  )
}

#' Add Bakka barrier mesh using land polygons (sdmTMBextra).
#' @param mesh sdmTMB mesh from [build_fishai_mesh()].
#' @param land_sf sf polygon in metres (model CRS).
#' @param range_fraction Barrier range fraction over land (default 0.1).
#' @param proj_scaling Metres per mesh km unit (default 1000).
#' @export
add_barrier_land <- function(mesh, land_sf, range_fraction = 0.1, proj_scaling = 1000) {
  if (range_fraction <= 0 || range_fraction >= 1) {
    stop("range_fraction must be in (0, 1)", call. = FALSE)
  }
  if (requireNamespace("sdmTMBextra", quietly = TRUE)) {
    return(sdmTMBextra::add_barrier_mesh(
      spde_obj = mesh,
      barrier_sf = land_sf,
      range_fraction = range_fraction,
      proj_scaling = proj_scaling,
      plot = FALSE
    ))
  }
  fishai_add_barrier_mesh(
    spde_obj = mesh,
    barrier_sf = land_sf,
    range_fraction = range_fraction,
    proj_scaling = proj_scaling,
    plot = FALSE
  )
}

#' QA barrier mesh: non-empty barrier triangles and samples not on barrier.
#' @export
check_barrier <- function(bmesh, obs, land_sf = NULL) {
  errs <- character()
  barrier_idx <- bmesh$barrier_triangles
  if (length(barrier_idx) == 0) {
    errs <- c(errs, "barrier triangle set is empty")
  }
  if (nrow(obs) > 0 && !is.null(land_sf)) {
    obs_m <- obs
    obs_m$X <- obs$X * 1000
    obs_m$Y <- obs$Y * 1000
    pts <- sf::st_as_sf(obs_m, coords = c("X", "Y"), crs = sf::st_crs(land_sf))
    inside <- lengths(sf::st_within(pts, land_sf)) > 0
    if (any(inside)) {
      errs <- c(errs, paste(sum(inside), "observations fall on land/barrier polygon"))
    }
  }
  if (length(errs)) {
    stop(paste(errs, collapse = "; "), call. = FALSE)
  }
  invisible(TRUE)
}

#' Read the configured barrier land polygon; fail closed when it is unusable.
.read_barrier_land <- function(mesh_cfg) {
  path <- mesh_cfg$barrier$land_sf_rds
  if (is.null(path) || length(path) != 1L || is.na(path) || !nzchar(path)) {
    stop("mesh.barrier.enabled requires mesh.barrier.land_sf_rds", call. = FALSE)
  }
  if (!file.exists(path)) {
    stop("mesh.barrier.land_sf_rds not found: ", path, call. = FALSE)
  }
  land_sf <- readRDS(path)
  if (!inherits(land_sf, c("sf", "sfc")) || length(sf::st_geometry(land_sf)) == 0L) {
    stop("mesh.barrier.land_sf_rds must hold a non-empty sf land polygon: ", path, call. = FALSE)
  }
  land_sf
}

#' Production mesh: plain mesh, plus Bakka land barrier and QA when enabled.
#'
#' Training and every spatial-CV fold mesh use this one path. Barrier enabled
#' requires a valid land polygon and non-empty barrier triangles
#' ([check_barrier()]); anything else is an error. Barrier disabled returns the
#' plain mesh.
#' @param dat Data with X, Y in km.
#' @param mesh_cfg ``cfg$mesh`` block.
#' @export
build_fishai_production_mesh <- function(dat, mesh_cfg) {
  mesh <- build_fishai_mesh(dat, mesh_cfg)
  if (!isTRUE(mesh_cfg$barrier$enabled)) {
    return(mesh)
  }
  land_sf <- .read_barrier_land(mesh_cfg)
  mesh <- add_barrier_land(
    mesh,
    land_sf,
    range_fraction = mesh_cfg$barrier$range_fraction %||% 0.1
  )
  check_barrier(mesh, dat, land_sf = land_sf)
  mesh
}

#' Ratio of approximate correlation across land vs through water at equal distance.
#' @export
barrier_correlation_ratio <- function(bmesh, pt_a, pt_b_land, pt_b_water) {
  d_land <- stats::dist(rbind(pt_a, pt_b_land))[1]
  d_water <- stats::dist(rbind(pt_a, pt_b_water))[1]
  if (abs(d_land - d_water) > 1e-6) {
    stop("comparison points must be equidistant from pt_a", call. = FALSE)
  }
  rf <- bmesh$barrier_scaling[2] %||% 0.1
  rw <- bmesh$barrier_scaling[1] %||% 1
  cor_land <- exp(-d_land / (20 * rf))
  cor_water <- exp(-d_water / 20)
  cor_land / cor_water
}
