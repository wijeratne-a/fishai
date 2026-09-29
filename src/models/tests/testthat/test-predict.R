test_that("predictions mask high OOD and physics FAIL", {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  artifact$reference <- dat[, ref_cols, drop = FALSE]
  artifact$reference_cols <- ref_cols
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  out <- predict_engine(
    artifact,
    grid,
    cfg,
    physics_cycle = "FAIL",
    nsim = 5,
    species = "sardine",
    valid_day = "2020-06-01",
    dry_run = TRUE
  )
  expect_true(all(out$evidence_state == "UNKNOWN"))
  expect_true(all(is.na(out$p_encounter)))
  expect_true(all(out$dry_run))
  expect_equal(out$lead_days, rep(0L, nrow(out)))
  expect_false(any(c("X", "Y", "lon", "lat") %in% names(out)))
  expect_true(nzchar(out$metadata_attribution_inference[1]))
})

.degraded_predict <- function(physics_cycle, widen = 1.5, ood_rows = NULL) {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  cfg$prediction$hindcast_evidence <- TRUE
  cfg$prediction$interval_widen <- widen
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  artifact$reference <- dat[, ref_cols, drop = FALSE]
  artifact$reference_cols <- ref_cols
  grid <- read.csv(cfg$prediction$grid_table, stringsAsFactors = FALSE)
  for (col in ref_cols) {
    grid[[col]] <- stats::median(dat[[col]])
  }
  if (!is.null(ood_rows)) {
    grid$cell_key <- paste0(floor(grid$X / 10), "_", floor(grid$Y / 10))
    novel_cells <- sort(unique(grid$cell_key))[ood_rows]
    novel <- grid$cell_key %in% novel_cells
    for (col in ref_cols) {
      grid[[col]][novel] <- max(dat[[col]]) + 25
    }
    grid$cell_key <- NULL
  }
  predict_engine(
    artifact,
    grid,
    cfg,
    physics_cycle = physics_cycle,
    nsim = 5L,
    species = "sardine",
    valid_day = "2020-06-01",
    dry_run = TRUE
  )
}

test_that("DEGRADED keeps UNKNOWN cells and reasons and marks the rest DEGRADED", {
  base <- .degraded_predict("PASS", ood_rows = 1:2)
  deg <- .degraded_predict("DEGRADED", ood_rows = 1:2)
  expect_equal(deg$cell_id, base$cell_id)
  was_unknown <- base$evidence_state == "UNKNOWN"
  expect_true(any(was_unknown))
  expect_true(any(!was_unknown))
  expect_true(all(deg$evidence_state[was_unknown] == "UNKNOWN"))
  expect_equal(deg$unknown_reason[was_unknown], base$unknown_reason[was_unknown])
  expect_true(all(is.na(deg$p_encounter[was_unknown])))
  expect_true(all(is.na(deg$p_lo90[was_unknown])))
  expect_true(all(is.na(deg$p_hi90[was_unknown])))
  expect_true(all(deg$evidence_state[!was_unknown] == "DEGRADED"))
})

test_that("DEGRADED never changes p_encounter and only widens bounds around it", {
  base <- .degraded_predict("PASS", widen = 1.5)
  deg <- .degraded_predict("DEGRADED", widen = 1.5)
  expect_equal(deg$p_encounter, base$p_encounter)
  expect_true(all(deg$p_lo90 <= base$p_lo90 + 1e-12))
  expect_true(all(deg$p_hi90 >= base$p_hi90 - 1e-12))
  expect_true(all(deg$p_lo90 >= 0 & deg$p_hi90 <= 1))
  expect_true(all(deg$p_lo90 <= deg$p_encounter + 1e-12))
  expect_true(all(deg$p_hi90 >= deg$p_encounter - 1e-12))
  expect_true(any(deg$p_hi90 - deg$p_lo90 > base$p_hi90 - base$p_lo90))
})

test_that("DEGRADED refuses an interval_widen that would narrow bounds", {
  expect_error(.degraded_predict("DEGRADED", widen = 0.5), "interval_widen")
})
