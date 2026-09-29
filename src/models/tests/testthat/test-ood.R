.ood_reference <- function(n = 60L) {
  set.seed(11)
  x <- stats::rnorm(n)
  data.frame(
    temp_3m_z = x,
    sal_3m_z = 0.6 * x + stats::rnorm(n, sd = 0.4),
    mld_z = stats::rnorm(n)
  )
}

test_that("OOD levels follow MESS thresholds", {
  ref <- data.frame(temp_3m_z = c(-1, 0, 1), sal_3m_z = c(-1, 0, 1))
  pred <- data.frame(temp_3m_z = c(2), sal_3m_z = c(0))
  mess <- mess_scores(pred, ref)
  expect_lt(mess$mess[1], 100)
  lvl <- classify_ood_level(
    mess$mess,
    nt1 = 0,
    nt2 = 0.5,
    maha = 0,
    hull_out = FALSE,
    maha_ref = maha_distance(.ood_reference(), .ood_reference())
  )
  expect_type(lvl, "integer")
})

test_that("Mahalanobis novelty uses frozen reference distances, not the grid quantile", {
  ref <- .ood_reference()
  maha_ref <- maha_distance(ref, ref)
  thr <- maha_reference_threshold(maha_ref)
  n <- 8L
  lvl <- classify_ood_level(
    mess = rep(50, n),
    nt1 = rep(0, n),
    nt2 = rep(0.5, n),
    maha = rep(thr * 3, n),
    hull_out = rep(FALSE, n),
    maha_ref = maha_ref
  )
  expect_true(all(lvl >= 1L))
})

test_that("in-domain Mahalanobis distances are not flagged", {
  ref <- .ood_reference()
  maha_ref <- maha_distance(ref, ref)
  inside <- maha_ref <= stats::median(maha_ref)
  lvl <- classify_ood_level(
    mess = rep(50, sum(inside)),
    nt1 = rep(0, sum(inside)),
    nt2 = rep(0.5, sum(inside)),
    maha = maha_ref[inside],
    hull_out = rep(FALSE, sum(inside)),
    maha_ref = maha_ref
  )
  expect_true(all(lvl == 0L))
})

test_that("classify_ood_level refuses to run without frozen reference distances", {
  expect_error(
    classify_ood_level(mess = 50, nt1 = 0, nt2 = 0.5, maha = 1, hull_out = FALSE),
    "maha_ref"
  )
})

test_that("non-finite Mahalanobis distance is treated as novel", {
  ref <- .ood_reference()
  lvl <- classify_ood_level(
    mess = 50,
    nt1 = 0,
    nt2 = 0.5,
    maha = NA_real_,
    hull_out = FALSE,
    maha_ref = maha_distance(ref, ref)
  )
  expect_gte(lvl, 1L)
})

.ood_predict_fixture <- function() {
  cfg <- load_sardine_test_cfg(intercept_only = TRUE)
  dat <- load_model_data(cfg = cfg)
  ref_cols <- c("temp_3m_z", "sal_3m_z", "mld_z")
  mesh <- build_fishai_mesh(dat, cfg$mesh)
  fit <- fit_delta_engine(dat, mesh, cfg)
  artifact <- freeze_model(fit, cfg, tempfile(fileext = ".rds"), training_dat = dat)
  artifact$reference <- dat[, ref_cols, drop = FALSE]
  artifact$reference_cols <- ref_cols
  list(cfg = cfg, dat = dat, artifact = artifact, ref_cols = ref_cols)
}

test_that("all-novel grid is UNKNOWN and does not self-normalize", {
  fx <- .ood_predict_fixture()
  grid <- read.csv(fx$cfg$prediction$grid_table, stringsAsFactors = FALSE)
  for (col in fx$ref_cols) {
    grid[[col]] <- max(fx$dat[[col]]) + 25 + seq_len(nrow(grid)) * 0.01
  }
  out <- predict_engine(
    fx$artifact,
    grid,
    fx$cfg,
    nsim = 2L,
    species = "sardine",
    valid_day = "2020-06-01",
    dry_run = TRUE
  )
  expect_true(all(out$ood_level >= 2L))
  expect_true(all(out$evidence_state == "UNKNOWN"))
  expect_true(all(out$unknown_reason == "ood_level_ge_2"))
  expect_true(all(is.na(out$p_encounter)))
  expect_true(all(is.na(out$p_lo90)))
  expect_true(all(is.na(out$p_hi90)))
})

test_that("in-domain grid is not blanked as out of domain", {
  fx <- .ood_predict_fixture()
  grid <- read.csv(fx$cfg$prediction$grid_table, stringsAsFactors = FALSE)
  mid <- vapply(fx$ref_cols, function(col) stats::median(fx$dat[[col]]), numeric(1))
  for (col in fx$ref_cols) {
    grid[[col]] <- mid[[col]]
  }
  out <- predict_engine(
    fx$artifact,
    grid,
    fx$cfg,
    nsim = 2L,
    species = "sardine",
    valid_day = "2020-06-01",
    dry_run = TRUE
  )
  expect_true(all(out$ood_level < 2L))
  expect_false(any(out$evidence_state == "UNKNOWN"))
  expect_true(all(is.finite(out$p_encounter)))
})
