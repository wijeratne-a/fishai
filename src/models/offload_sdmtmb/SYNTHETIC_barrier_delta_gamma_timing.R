#!/usr/bin/env Rscript
# SYNTHETIC — delta-gamma sdmTMB barrier fit timing (offload benchmark only).

args <- commandArgs(trailingOnly = TRUE)
out_path <- if (length(args) >= 1) args[[1]] else "SYNTHETIC_sdmtmb_barrier_delta_gamma_timing.json"

LAND_X0 <- 40
LAND_X1 <- 60
LAND_Y0 <- 40
LAND_Y1 <- 60

result <- list(
  label = "SYNTHETIC",
  benchmark = "delta_gamma_barrier_fit",
  status = "skipped",
  reason = NULL,
  barrier_triangle_count = 0L,
  timings_sec = list()
)

write_json <- function(obj, path) {
  if (!requireNamespace("jsonlite", quietly = TRUE)) {
    stop("jsonlite required to write SYNTHETIC benchmark output", call. = FALSE)
  }
  writeLines(jsonlite::toJSON(obj, auto_unbox = TRUE, pretty = TRUE), path)
}

if (!requireNamespace("jsonlite", quietly = TRUE)) {
  result$reason <- "jsonlite not installed"
  writeLines(
    '{"label":"SYNTHETIC","benchmark":"delta_gamma_barrier_fit","status":"skipped","reason":"jsonlite not installed"}',
    out_path
  )
  quit(status = 0)
}

if (!requireNamespace("sdmTMB", quietly = TRUE)) {
  result$reason <- "sdmTMB not installed"
  write_json(result, out_path)
  quit(status = 0)
}

set.seed(42)
n <- 120L
dat <- data.frame(
  X = runif(n, 0, 100),
  Y = runif(n, 0, 100),
  y = rpois(n, 2),
  log_effort = log(runif(n, 50, 200)),
  time_idx = rep(1L, n)
)
inside_land <- dat$X >= LAND_X0 & dat$X <= LAND_X1 & dat$Y >= LAND_Y0 & dat$Y <= LAND_Y1
dat <- dat[!inside_land, , drop = FALSE]
result$points_dropped_inside_land <- sum(inside_land)

t_mesh <- system.time({
  mesh <- sdmTMB::make_mesh(dat, xy_cols = c("X", "Y"), cutoff = 9)
})["elapsed"]

t_barrier <- 0
if (requireNamespace("sdmTMBextra", quietly = TRUE) && requireNamespace("sf", quietly = TRUE)) {
  land_poly <- sf::st_polygon(
    list(
      matrix(
        c(
          LAND_X0, LAND_Y0,
          LAND_X1, LAND_Y0,
          LAND_X1, LAND_Y1,
          LAND_X0, LAND_Y1,
          LAND_X0, LAND_Y0
        ),
        ncol = 2,
        byrow = TRUE
      )
    )
  )
  land <- sf::st_sf(geometry = sf::st_sfc(land_poly))
  t_barrier <- system.time({
    mesh <- sdmTMBextra::add_barrier_mesh(
      spde_obj = mesh,
      barrier_sf = land,
      range_fraction = 0.1,
      proj_scaling = 1,
      plot = FALSE
    )
  })["elapsed"]
  n_barrier <- length(mesh$barrier_triangles)
  result$barrier_triangle_count <- as.integer(n_barrier)
  if (n_barrier == 0L) {
    result$status <- "error"
    result$reason <- "zero barrier triangles flagged"
  }
} else {
  result$barrier_note <- "sdmTMBextra/sf unavailable; barrier step skipped"
}

frm <- list(stats::as.formula("y ~ 1"), stats::as.formula("y ~ 1"))

if (identical(result$status, "error")) {
  result$timings_sec <- list(
    mesh = unname(t_mesh),
    barrier = unname(t_barrier),
    delta_gamma_fit = NA_real_
  )
  write_json(result, out_path)
  quit(status = 0)
}

t_fit <- system.time({
  fit <- tryCatch(
    sdmTMB::sdmTMB(
      formula = frm,
      data = dat,
      mesh = mesh,
      family = sdmTMB::delta_gamma(type = "poisson-link"),
      spatial = "on",
      spatiotemporal = "off",
      offset = "log_effort"
    ),
    error = function(e) e
  )
})["elapsed"]

if (inherits(fit, "error")) {
  result$status <- "error"
  result$reason <- conditionMessage(fit)
} else {
  result$status <- "ok"
}

result$timings_sec <- list(
  mesh = unname(t_mesh),
  barrier = unname(t_barrier),
  delta_gamma_fit = unname(t_fit)
)
write_json(result, out_path)
