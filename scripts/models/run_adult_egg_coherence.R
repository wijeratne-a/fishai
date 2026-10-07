#!/usr/bin/env Rscript
# Adult vs egg anchovy encounter coherence (10 km SCB grid). Coherence check only — not validation.
root <- normalizePath(
  file.path(
    dirname(sub("^--file=", "", commandArgs()[grep("^--file=", commandArgs())][1])),
    "..",
    ".."
  )
)
setwd(root)
Sys.setenv(FISHAI_ROOT = root)
source(file.path(root, "src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm(root)

args <- commandArgs(trailingOnly = TRUE)
out_dir <- file.path(root, "artifacts", "coherence", "anchovy")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

egg_cfg_path <- file.path(root, "configs", "models", "cufes_anchovy.yaml")
adult_cfg_path <- file.path(root, "configs", "models", "adult_cps_anchovy.yaml")

.require_inputs <- function(cfg) {
  missing <- missing_real_table_cv_inputs(cfg)
  if (length(missing)) {
    stop(
      "missing model inputs (public ingest blocked or not built): ",
      paste(missing, collapse = ", "),
      call. = FALSE
    )
  }
}

train_if_needed <- function(cfg, label) {
  artifact_path <- file.path(cfg$output$dir %||% file.path("artifacts", "models", label), "artifact.rds")
  if (file.exists(artifact_path)) {
    return(list(cfg = cfg, artifact = readRDS(artifact_path), artifact_path = artifact_path))
  }
  dat <- load_model_data(cfg = cfg)
  mesh <- build_fishai_production_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  dir.create(dirname(artifact_path), recursive = TRUE, showWarnings = FALSE)
  freeze_model(fit, cfg, artifact_path, training_dat = dat)
  list(cfg = cfg, artifact = readRDS(artifact_path), artifact_path = artifact_path)
}

.map_grid_covariates <- function(grid, cfg) {
  upstream <- cfg$covariates$upstream_fields %||% list()
  dyn <- cfg$covariates$dynamic %||% character()
  static <- cfg$covariates$static %||% character()
  for (slug in c(dyn, static)) {
    up <- upstream[[slug]] %||% slug
    zcol <- paste0(slug, "_z")
    if (up %in% names(grid)) {
      grid[[zcol]] <- grid[[up]]
    }
  }
  grid
}

.day_to_time_idx <- function(day, cfg) {
  origin <- .time_idx_origin_date(cfg)
  d <- as.Date(day)
  as.integer(d - origin) + 1L
}

build_grid_for_day <- function(day, cfg) {
  py <- Sys.which("python3")
  if (!nzchar(py)) {
    stop("python3 required to build SCB 10 km grid covariates", call. = FALSE)
  }
  grid_csv <- file.path(out_dir, paste0("scb_10km_", day, ".csv"))
  cmd <- c(
    file.path(root, "scripts", "build_scb_coherence_grid.py"),
    "--day", day,
    "--output", grid_csv
  )
  status <- system2(py, cmd, stdout = TRUE, stderr = TRUE)
  if (!file.exists(grid_csv)) {
    stop("grid build failed: ", paste(status, collapse = "\n"), call. = FALSE)
  }
  grid <- read.csv(grid_csv, stringsAsFactors = FALSE)
  grid$time_idx <- .day_to_time_idx(day, cfg)
  .map_grid_covariates(grid, cfg)
}

predict_surface <- function(artifact, cfg, day, label) {
  cfg$prediction$hindcast_evidence <- TRUE
  grid <- build_grid_for_day(day, cfg)
  pred <- predict_engine(
    artifact,
    grid,
    cfg,
    physics_cycle = "PASS",
    species = "anchovy",
    valid_day = day,
    dry_run = FALSE
  )
  pred$surface_day <- day
  pred$life_stage <- label
  pred
}

coherence_metrics <- function(egg, adult) {
  merged <- merge(
    egg[, c("cell_id", "p_encounter", "ood_level")],
    adult[, c("cell_id", "p_encounter", "ood_level")],
    by = "cell_id",
    suffixes = c("_egg", "_adult")
  )
  ok <- merged$ood_level_egg < 2L & merged$ood_level_adult < 2L &
    is.finite(merged$p_encounter_egg) & is.finite(merged$p_encounter_adult)
  sub <- merged[ok, , drop = FALSE]
  if (nrow(sub) < 10L) {
    return(list(
      n_cells = nrow(sub),
      pearson_r = NA_real_,
      top_decile_jaccard = NA_real_,
      top_decile_hit_rate = NA_real_
    ))
  }
  r <- stats::cor(sub$p_encounter_egg, sub$p_encounter_adult, method = "pearson")
  q90_e <- stats::quantile(sub$p_encounter_egg, 0.9, na.rm = TRUE)
  q90_a <- stats::quantile(sub$p_encounter_adult, 0.9, na.rm = TRUE)
  top_e <- sub$p_encounter_egg >= q90_e
  top_a <- sub$p_encounter_adult >= q90_a
  inter <- sum(top_e & top_a)
  union <- sum(top_e | top_a)
  jacc <- if (union > 0) inter / union else NA_real_
  hit <- if (sum(top_e) > 0) inter / sum(top_e) else NA_real_
  list(
    n_cells = nrow(sub),
    pearson_r = unname(r),
    top_decile_jaccard = unname(jacc),
    top_decile_hit_rate = unname(hit)
  )
}

write_side_by_side_map <- function(egg, adult, path) {
  png(path, width = 1200, height = 500, res = 120)
  on.exit(dev.off(), add = TRUE)
  par(mfrow = c(1, 2), mar = c(2, 2, 3, 1))
  plot_surface <- function(df, main) {
    ok <- df$ood_level < 2L & is.finite(df$p_encounter)
    cols <- grDevices::colorRampPalette(c("#2166ac", "#f7f7f7", "#b2182b"))(100)
    z <- df$p_encounter[ok]
    if (!length(z)) {
      plot.new()
      title(main)
      return()
    }
    br <- seq(min(z, na.rm = TRUE), max(z, na.rm = TRUE), length.out = 101)
    ci <- pmin(100L, pmax(1L, as.integer(cut(z, breaks = br, include.lowest = TRUE))))
    plot(
      df$longitude[ok],
      df$latitude[ok],
      col = cols[ci],
      pch = 15,
      cex = 0.9,
      xlab = "",
      ylab = "",
      main = main,
      xlim = c(-121, -117),
      ylim = c(32, 35)
    )
  }
  plot_surface(egg, "Egg encounter (CUFES model)")
  plot_surface(adult, "Adult encounter (CPS model)")
}

# Representative days: peak egg (Apr) and broad summer adult coverage
climatology_days <- c("2016-04-15", "2017-04-15", "2018-04-15", "2019-07-15", "2020-07-15")

message("loading configs...")
egg_cfg <- load_config_yaml(egg_cfg_path)
adult_cfg <- load_config_yaml(adult_cfg_path)
egg_cfg$output$dir <- file.path(root, "artifacts", "models", "anchovy_egg_coherence")
adult_cfg$output$dir <- file.path(root, "artifacts", "models", "anchovy_adult_coherence")

message("checking training tables...")
.require_inputs(egg_cfg)
.require_inputs(adult_cfg)

message("train / load artifacts (full data, not CV)...")
egg_res <- train_if_needed(egg_cfg, "anchovy_egg")
adult_res <- train_if_needed(adult_cfg, "anchovy_adult")

surfaces <- list()
metrics_by_day <- list()
for (day in climatology_days) {
  message("predict surfaces for ", day)
  egg_s <- predict_surface(egg_res$artifact, egg_res$cfg, day, "egg")
  adult_s <- predict_surface(adult_res$artifact, adult_res$cfg, day, "adult")
  surfaces[[day]] <- list(egg = egg_s, adult = adult_s)
  metrics_by_day[[day]] <- coherence_metrics(egg_s, adult_s)
}

agg <- do.call(rbind, lapply(names(metrics_by_day), function(d) {
  cbind(data.frame(day = d, stringsAsFactors = FALSE), as.data.frame(metrics_by_day[[d]], stringsAsFactors = FALSE))
}))

mean_r <- mean(agg$pearson_r, na.rm = TRUE)
mean_j <- mean(agg$top_decile_jaccard, na.rm = TRUE)
mean_hit <- mean(agg$top_decile_hit_rate, na.rm = TRUE)

write.csv(agg, file.path(out_dir, "coherence_metrics_by_day.csv"), row.names = FALSE)
summary_json <- list(
  life_stage = "anchovy",
  grid_spacing_km = 10,
  climatology_days = climatology_days,
  mean_pearson_r = mean_r,
  mean_top_decile_jaccard = mean_j,
  mean_top_decile_hit_rate = mean_hit,
  framing = "coherence_check_not_validation"
)
jsonlite::write_json(summary_json, file.path(out_dir, "coherence_summary.json"), auto_unbox = TRUE, pretty = TRUE)

ref_day <- climatology_days[[1]]
write_side_by_side_map(
  surfaces[[ref_day]]$egg,
  surfaces[[ref_day]]$adult,
  file.path(out_dir, "map_egg_vs_adult_side_by_side.png")
)

cat(
  "\nCoherence summary (anchovy, 10 km SCB grid):\n",
  "  mean Pearson r:", mean_r, "\n",
  "  mean top-decile Jaccard:", mean_j, "\n",
  "  mean top-decile hit rate (egg->adult):", mean_hit, "\n",
  sep = ""
)
message("coherence run complete")
