#' Fit spatiotemporal LGCP for trawl encounter (presence points + effort-weighted samplers).
#' @param train Training frame from [load_model_data()] with lat, lon, time_idx, y, log_effort, covariates.
#' @param cfg Model config (see jack_mackerel_encounter_all_sizes_lgcp.yaml).
#' @export
fit_encounter_lgcp <- function(train, cfg) {
  if (!requireNamespace("inlabru", quietly = TRUE)) {
    stop("inlabru is required for LGCP fitting", call. = FALSE)
  }
  if (!requireNamespace("INLA", quietly = TRUE)) {
    stop("INLA is required for LGCP fitting", call. = FALSE)
  }
  req <- c("lat", "lon", "time_idx", "y", "log_effort")
  miss <- setdiff(req, names(train))
  if (length(miss)) {
    stop("LGCP training frame missing: ", paste(miss, collapse = ", "), call. = FALSE)
  }
  cov_rhs <- cfg$model$formula_covariates
  if (is.null(cov_rhs) || !nzchar(cov_rhs)) {
    stop("model$formula_covariates is required", call. = FALSE)
  }
  cov_terms <- trimws(unlist(strsplit(cov_rhs, "+", fixed = TRUE)))
  miss_cov <- setdiff(cov_terms, names(train))
  if (length(miss_cov)) {
    stop("LGCP covariates missing from training frame: ", paste(miss_cov, collapse = ", "), call. = FALSE)
  }

  mesh_cfg <- cfg$model$mesh %||% cfg$mesh %||% list()
  # Coarser than sdmTMB 9 km mesh: full ST SPDE on dense daily time_idx OOMs on ~15 GB VMs.
  max_edge_km <- as.numeric(mesh_cfg$max_edge_km %||% 18)
  cutoff_km <- as.numeric(mesh_cfg$cutoff_km %||% max_edge_km)
  range_km <- as.numeric(mesh_cfg$range_prior_km %||% 60)

  if (!"time" %in% names(train)) {
    stop("LGCP training frame missing time for spatiotemporal mesh", call. = FALSE)
  }
  train$time_slice <- as.integer(format(as.POSIXct(train$time, tz = "UTC"), "%Y%m"))

  train_sf <- sf::st_as_sf(train, coords = c("lon", "lat"), crs = 4326, remove = FALSE)
  train_sf$time_slice <- train$time_slice
  train_sf$weight <- exp(as.numeric(train$log_effort))
  pres_sf <- train_sf[as.integer(train$y) == 1L, , drop = FALSE]
  pres_sf$time_slice <- train$time_slice[as.integer(train$y) == 1L]
  if (nrow(pres_sf) < 5L) {
    stop("too few presence points for LGCP (n=", nrow(pres_sf), ")", call. = FALSE)
  }

  train_utm <- sf::st_transform(train_sf, 32611)
  loc <- sf::st_coordinates(train_utm)
  mesh <- fmesher::fm_mesh_2d_inla(
    loc = loc,
    max.edge = c(max_edge_km * 1000, max_edge_km * 5000),
    cutoff = cutoff_km * 1000
  )
  spde <- INLA::inla.spde2.pcmatern(
    mesh,
    alpha = 2,
    prior.range = c(range_km * 1000, 0.5),
    prior.sigma = c(1, 0.01)
  )

  cov_expr <- paste(cov_terms, collapse = " + ")
  cmp <- stats::as.formula(
    paste0(
      "~ field(geometry, model = spde, group = time_slice, ",
      "control.group = list(model = 'ar1')) + ",
      "Intercept(1) + ", cov_expr
    ),
    env = environment()
  )
  form <- stats::as.formula(
    paste0("geometry + time_slice ~ field + Intercept + ", cov_expr),
    env = environment()
  )

  time_vals <- sort(unique(as.integer(train$time_slice)))
  time_mesh <- fmesher::fm_mesh_1d(time_vals, boundary = "free")
  fit <- inlabru::lgcp(
    components = cmp,
    formula = form,
    data = pres_sf,
    samplers = train_sf,
    domain = list(geometry = mesh, time_slice = time_mesh),
    options = list(
      control.inla = list(int.strategy = "eb"),
      bru_verbose = FALSE,
      bru_max_iter = 2L
    )
  )
  structure(
    list(
      fit = fit,
      mesh = mesh,
      spde = spde,
      cov_terms = cov_terms
    ),
    class = "fishai_lgcp_fit"
  )
}

#' Encounter probability on holdout trawl points from LGCP intensity (Poisson exposure link).
#' @export
score_encounter_lgcp_on_events <- function(fit_obj, newdata, cfg) {
  fit <- fit_obj$fit
  cov_terms <- fit_obj$cov_terms
  need <- c("lat", "lon", "time", "log_effort", cov_terms)
  miss <- setdiff(need, names(newdata))
  if (length(miss)) {
    stop("holdout data missing columns: ", paste(miss, collapse = ", "), call. = FALSE)
  }
  nd <- newdata
  nd$time_slice <- as.integer(format(as.POSIXct(nd$time, tz = "UTC"), "%Y%m"))
  nd <- sf::st_as_sf(nd, coords = c("lon", "lat"), crs = 4326, remove = FALSE)
  pred <- inlabru::predict(
    fit,
    nd,
    as.formula(paste("~ exp(field + Intercept +", paste(cov_terms, collapse = " + "), ")"))
  )
  lam <- as.numeric(pred$mean)
  effort <- exp(as.numeric(newdata$log_effort))
  p <- 1 - exp(-lam * effort)
  pmax(pmin(p, 1), 0)
}
