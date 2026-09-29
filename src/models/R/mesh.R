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
  sdmTMBextra::add_barrier_mesh(
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

.summarize_edge_lengths_km <- function(x) {
  if (!length(x)) {
    return(list(min_km = NA_real_, median_km = NA_real_, max_km = NA_real_, n = 0L))
  }
  list(
    min_km = min(x),
    median_km = stats::median(x),
    max_km = max(x),
    n = length(x)
  )
}

.triangle_edge_lengths_km <- function(mesh_obj, triangle_idx = NULL) {
  fm <- mesh_obj$mesh
  tv <- fm$graph$tv
  loc <- fm$loc[, 1:2, drop = FALSE]
  if (is.null(triangle_idx)) {
    triangle_idx <- seq_len(nrow(tv))
  }
  triangle_idx <- as.integer(triangle_idx)
  triangle_idx <- triangle_idx[triangle_idx >= 1L & triangle_idx <= nrow(tv)]
  if (!length(triangle_idx)) {
    return(numeric())
  }
  lengths_km <- vapply(
    triangle_idx,
    function(tri) {
      v <- as.integer(tv[tri, ])
      p <- loc[v, , drop = FALSE]
      sqrt(rowSums((p[c(2L, 3L, 1L), , drop = FALSE] - p)^2))
    },
    numeric(3)
  )
  as.numeric(lengths_km)
}

.fitted_spatial_range_km <- function(fishai_fit) {
  if (is.null(fishai_fit)) {
    return(NA_real_)
  }
  fit <- fishai_fit$fit
  spatial <- fit$spatial
  if (is.null(spatial) || all(spatial == "off")) {
    return(NA_real_)
  }
  tp <- tryCatch(
    sdmTMB::tidy(fit, effects = "ran_pars"),
    error = function(e) NULL
  )
  if (is.null(tp) || !"term" %in% names(tp)) {
    return(NA_real_)
  }
  idx <- tp$term == "range" & is.finite(tp$estimate)
  if (!any(idx)) {
    return(NA_real_)
  }
  as.numeric(tp$estimate[which(idx)[1L]])
}

#' Mesh triangle edge-length summary (km) with fitted Matérn range when available.
#'
#' Water vs barrier triangles are split using ``barrier_triangles`` when present.
#' @param mesh sdmTMB mesh (optionally with barrier).
#' @param fishai_fit Optional [fit_delta_engine()] result for fitted range (km).
#' @export
mesh_spatial_scale_report <- function(mesh, fishai_fit = NULL) {
  if (is.null(mesh) || is.null(mesh$mesh) || is.null(mesh$mesh$graph$tv)) {
    stop("mesh must be an sdmTMB mesh with triangle graph", call. = FALSE)
  }
  n_tri <- nrow(mesh$mesh$graph$tv)
  barrier_idx <- mesh$barrier_triangles
  if (is.null(barrier_idx) || !length(barrier_idx)) {
    water_idx <- seq_len(n_tri)
    barrier_idx <- integer()
  } else {
    barrier_idx <- unique(as.integer(barrier_idx))
    barrier_idx <- barrier_idx[barrier_idx >= 1L & barrier_idx <= n_tri]
    water_idx <- setdiff(seq_len(n_tri), barrier_idx)
  }
  list(
    fitted_spatial_range_km = .fitted_spatial_range_km(fishai_fit),
    water_triangle_edge_km = .summarize_edge_lengths_km(
      .triangle_edge_lengths_km(mesh, water_idx)
    ),
    barrier_triangle_edge_km = .summarize_edge_lengths_km(
      .triangle_edge_lengths_km(mesh, barrier_idx)
    )
  )
}
