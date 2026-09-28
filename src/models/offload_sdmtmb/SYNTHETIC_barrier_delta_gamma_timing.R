#!/usr/bin/env Rscript
# SYNTHETIC — delta-gamma sdmTMB barrier fit timing (offload benchmark only).

args <- commandArgs(trailingOnly = TRUE)
out_path <- if (length(args) >= 1) args[[1]] else "SYNTHETIC_sdmtmb_barrier_delta_gamma_timing.json"

result <- list(
  label = "SYNTHETIC",
  benchmark = "delta_gamma_barrier_fit",
  status = "skipped",
  reason = NULL,
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
n <- 80L
dat <- data.frame(
  X = runif(n, 0, 100),
  Y = runif(n, 0, 100),
  y = rpois(n, 2),
  log_effort = log(runif(n, 50, 200)),
  time_idx = rep(1L, n)
)

t_mesh <- system.time({
  mesh <- sdmTMB::make_mesh(dat, xy_cols = c("X", "Y"), cutoff = 9)
})["elapsed"]

t_barrier <- 0
if (requireNamespace("sdmTMBextra", quietly = TRUE) && requireNamespace("sf", quietly = TRUE)) {
  land <- sf::st_sf(
    geometry = sf::st_sfc(
      sf::st_polygon(
        list(
          rbind(
            c(15000, 15000),
            c(25000, 15000),
            c(25000, 25000),
            c(15000, 25000),
            c(15000, 15000)
          )
        )
      ),
      crs = 32610
    )
  )
  t_barrier <- system.time({
    mesh <- sdmTMBextra::add_barrier_mesh(
      spde_obj = mesh,
      barrier_sf = land,
      range_fraction = 0.1,
      proj_scaling = 1000,
      plot = FALSE
    )
  })["elapsed"]
} else {
  result$barrier_note <- "sdmTMBextra/sf unavailable; barrier step skipped"
}

frm <- list(stats::as.formula("y ~ 1"), stats::as.formula("y ~ 1"))

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
