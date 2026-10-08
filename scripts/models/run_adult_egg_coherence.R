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
      grid[[zcol]] <- as.numeric(grid[[up]])
    } else if (slug %in% names(grid)) {
      grid[[zcol]] <- as.numeric(grid[[slug]])
    }
  }
  grid
}

.intersect_prediction_days <- function(egg_art, adult_art, cfg, candidates) {
  levels_e <- as.integer(egg_art$time_idx_levels)
  levels_a <- as.integer(adult_art$time_idx_levels)
  shared <- intersect(levels_e, levels_a)
  if (!length(shared)) {
    stop("no shared time_idx between egg and adult artifacts", call. = FALSE)
  }
  origin <- .time_idx_origin_date(cfg)
  shared_dates <- origin + shared - 1L
  keep <- character()
  for (day in candidates) {
    idx <- as.integer(as.Date(day) - origin) + 1L
    if (idx %in% shared) {
      keep <- c(keep, day)
    }
  }
  if (!length(keep)) {
    for (day in candidates) {
      d <- as.Date(day)
      ym <- format(d, "%Y-%m")
      in_month <- shared_dates[format(shared_dates, "%Y-%m") == ym]
      if (length(in_month)) {
        nearest <- in_month[which.min(abs(as.integer(in_month - d)))]
        keep <- c(keep, format(nearest, "%Y-%m-%d"))
      }
    }
  }
  if (!length(keep)) {
    apr <- shared_dates[format(shared_dates, "%m") == "04"]
    jul <- shared_dates[format(shared_dates, "%m") == "07"]
    mid <- function(v) {
      if (!length(v)) {
        return(NA_character_)
      }
      format(sort(v)[ceiling(length(v) / 2)], "%Y-%m-%d")
    }
    keep <- c(mid(apr), mid(jul))
    keep <- keep[!is.na(keep) & nzchar(keep)]
  }
  if (!length(keep)) {
    stop("no climatology days could be aligned to shared survey time_idx", call. = FALSE)
  }
  unique(keep)
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
  zcols <- paste0(
    c(cfg$covariates$dynamic %||% character(), cfg$covariates$static %||% character()),
    "_z"
  )
  zcols <- intersect(zcols, names(grid))
  ok <- if (length(zcols)) stats::complete.cases(grid[, zcols, drop = FALSE]) else rep(TRUE, nrow(grid))
  if (!any(ok)) {
    stop("no grid cells with complete covariates for ", day, call. = FALSE)
  }
  pred <- predict_engine(
    artifact,
    grid[ok, , drop = FALSE],
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
    # Grids store UTM kilometres, not latitude/longitude headers.
    xs <- if ("X" %in% names(df)) df$X[ok] else df$longitude[ok]
    ys <- if ("Y" %in% names(df)) df$Y[ok] else df$latitude[ok]
    plot(
      xs,
      ys,
      col = cols[ci],
      pch = 15,
      cex = 0.9,
      xlab = "",
      ylab = "",
      main = main,
      xlim = range(xs, na.rm = TRUE),
      ylim = range(ys, na.rm = TRUE)
    )
  }
  plot_surface(egg, "Egg encounter (CUFES model)")
  plot_surface(adult, "Adult encounter (CPS model)")
}

# Candidate days: spring (egg peak) and summer; filtered to shared training time_idx
climatology_candidates <- c(
  "2014-04-15", "2015-04-15", "2016-04-15", "2017-04-15",
  "2014-07-15", "2015-07-15", "2016-07-15", "2017-07-15"
)

message("loading configs...")
egg_cfg <- load_config_yaml(egg_cfg_path)
adult_cfg <- load_config_yaml(adult_cfg_path)
egg_cfg$output$dir <- file.path(root, "artifacts", "models", "anchovy_egg_coherence")
adult_cfg$output$dir <- file.path(root, "artifacts", "models", "anchovy_adult_coherence")

# Host budget: validated formula/covariates/families; barrier mesh omitted here only
# (full barrier fits exceed cloud-agent wall time on ~12k CUFES rows).
egg_cfg$mesh$barrier$enabled <- FALSE
adult_cfg$mesh$barrier$enabled <- FALSE
egg_cfg$mesh$cutoff_km <- max(egg_cfg$mesh$cutoff_km %||% 9, 15)
adult_cfg$mesh$cutoff_km <- max(adult_cfg$mesh$cutoff_km %||% 9, 15)

# freeze_model() calls egg_split_fit_end(); adult CPS YAML has no egg_split block.
adult_cfg$egg_split <- list(
  fit_end = "2025-12-31",
  test_start = "2099-01-01",
  test_end = "2099-01-01",
  test_score_include_post_boundary = TRUE
)
adult_cfg$training_end <- "2025-12-31"

message("checking training tables...")
.require_inputs(egg_cfg)
.require_inputs(adult_cfg)

message("train / load artifacts (full data, not CV)...")
egg_res <- train_if_needed(egg_cfg, "anchovy_egg")
adult_res <- train_if_needed(adult_cfg, "anchovy_adult")

climatology_days <- .intersect_prediction_days(
  egg_res$artifact,
  adult_res$artifact,
  egg_res$cfg,
  climatology_candidates
)
message("climatology days (shared time_idx): ", paste(climatology_days, collapse = ", "))

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

spring_days <- climatology_days[grepl("-04-", climatology_days)]
summer_days <- climatology_days[grepl("-07-", climatology_days)]
season_rows <- function(days, label) {
  if (!length(days)) {
    return(NULL)
  }
  sub <- agg[agg$day %in% days, , drop = FALSE]
  data.frame(
    season = label,
    n_days = nrow(sub),
    mean_pearson_r = mean(sub$pearson_r, na.rm = TRUE),
    mean_top_decile_jaccard = mean(sub$top_decile_jaccard, na.rm = TRUE),
    mean_top_decile_hit_rate = mean(sub$top_decile_hit_rate, na.rm = TRUE),
    stringsAsFactors = FALSE
  )
}
season_agg <- do.call(rbind, Filter(Negate(is.null), list(
  season_rows(spring_days, "spring_apr"),
  season_rows(summer_days, "summer_jul")
)))
if (!is.null(season_agg) && nrow(season_agg)) {
  write.csv(season_agg, file.path(out_dir, "coherence_metrics_by_season.csv"), row.names = FALSE)
}

cat(
  "\nCoherence summary (anchovy, 10 km SCB grid):\n",
  "  mean Pearson r:", mean_r, "\n",
  "  mean top-decile Jaccard:", mean_j, "\n",
  "  mean top-decile hit rate (egg->adult):", mean_hit, "\n",
  sep = ""
)
message("coherence run complete")
