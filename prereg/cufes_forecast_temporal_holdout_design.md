# CUFES 72 h forecast skill: rolling-origin design

**Status:** Approved and executed. Scores are in `prereg/cufes_forecast_temporal_holdout_scores.json`. The plain-language result is in `prereg/cufes_forecast_temporal_holdout_readout.md`. The technical note is `prereg/cufes_forecast_temporal_holdout_report.md`. Neither species passed. This file does not publish a forecast.

**Claim under test:** The sardine and anchovy egg-encounter models have skill at future times (24/48/72 h), not only on held-out areas. Spatial-block skill (PR #33; `prereg/cufes_spatial_block_cv_scores.json`) is a different claim and is not reused as evidence here.

**Target:** Egg encounter probability for Pacific sardine and northern anchovy eggs in the Southern California Bight CUFES record. Not adult location, not a track, not harvest advice.

## Model spec (unchanged)

Same validated pilot spec as the spatial scores:

- Configs: `configs/models/cufes_sardine.yaml`, `configs/models/cufes_anchovy.yaml`
- Poisson-link delta-gamma, shared smooths on `temp_3m_z`, `sal_3m_z`, `mld_z`, `sst_grad_z`, `dist_front_z`, `log_depth_z`
- Spatial on, spatiotemporal off, `time_varying ~ 1` with type `rw0`
- Barrier mesh, cutoff 9 km, range guess 60 km, `range_fraction` 0.1
- `time_idx` origin `1990-01-01`
- Effort offset `log(volume_m3)` on holdout events (not `V_ref`)

Training table and mesh files are not modified. Each cutoff builds its mesh from that cutoff's training rows only (`build_fishai_production_mesh`).

`predict_engine()` rejects a `time_idx` outside frozen training levels. Scoring does not go through that guard. Fits use `fit_delta_engine()` with `extra_time`. That guard stays as it is.

## K and cutoff rule

**K = 8** (two cutoffs in each meteorological season).

Cost: one refit per cutoff per species. Physics variants and baselines are predictions from that fit, not extra fits. 8 × 2 = **16** sequential fits, one TMB thread, checkpointed. That is about twice the spatial-block CV (2 species × 4 folds). K = 6 cannot place two cutoffs in each season. K = 10 adds four fits for a third replicate and is not worth it until these eight exist.

A day **D** is an eligible cutoff only if all of the following hold on the same QC frame the spatial scores used (count-row join, covariate complete, duration, barrier-land midpoint drop):

1. D, D+1, D+2, and D+3 each have at least one eligible event (horizons 24/48/72 h).
2. Training rows are events with day ≤ D. Require ≥ 2000 rows, ≥ 30 distinct days, and both presence and absence.
3. D+3 is on or before `egg_split.test_end` (`2022-04-27`).

The time window is the full egg record through that end date, not only `egg_split.fit_end` (`2017-12-31`). A rolling origin that never leaves the spatial-training era would not test later years. Rows with day > D are not used to fit, scale, or build climatology.

Season of a cutoff is the season of **D** (DJF, MAM, JJA, SON).

Deterministic pick, before any fit, with no look at scores:

1. Inventory eligible D from the event table (read-only).
2. Within each season, sort eligible dates. Take the earliest and the latest that are at least 365 days apart.
3. If a season has no such pair, take the two farthest dates and record the gap. If a season has fewer than two eligible dates, stop with `design_infeasible`. Do not drop a season silently.
4. Holdout windows are cutoff+1..+3. Selected cutoffs must be at least 30 days apart so those windows do not overlap.

Exact ISO dates are locked by that inventory and written into the metrics JSON before the refits. They are not invented here. The event table is not in this checkout.

## Physics

### Oracle

Future-day covariates on the holdout event rows (observed GLORYS already joined in the training table). Isolates the egg model given the analysed ocean state. `lane = retrospective`. Not an issued forecast.

### Operational

Archived issued forecast fields do **not** overlap this egg record. Public `noaa-nos-ofs-pds` WCOFS prefixes start at `wcofs/netcdf/202407/`. List/HEAD checks for forecast objects in 2016, 2018, 2021, 2022, 2023, and 2024-06 returned no object. CUFES scoring ends 2022-04-27. There is no WCOFS (or other) issued-forecast archive to score.

**Proxy, pre-declared, not tuned on holdout:** lead-damped anomaly toward a training-only climatology. For each dynamic covariate column the model actually sees, at a holdout event on day D+h (h = 1, 2, 3):

```
x_hat = clim + exp(-h / 3) * (x_cutoff - clim)
```

- `tau = 3` days, fixed. Matches the 72 h product horizon. Not fit to these scores.
- `x_cutoff`: inverse-distance weighted mean (power 2) of that column on **cutoff-day training events** within 120 km of the holdout point. Cutoff-day rows are inside the training set.
- `clim`: mean of the same column on training events with day ≤ D, circular day-of-year distance ≤ 15, and distance ≤ 60 km. If fewer than 20 such events, widen the day-of-year window to 30, then 45. If still fewer than 20, the row is `UNKNOWN` for the operational arm (not imputed).
- `log_depth_z` is static and is taken from the holdout row (bathymetry, not a forecast field).
- Weights use the same EPSG:32611 km coordinates as the mesh.

This is `physics_source = damped_anomaly_proxy`. It is not a WCOFS field and must not be described as one. Every operational metric carries `operational_claim = NOT_ISSUED_FORECAST`.

No second standardization. `load_model_data` copies upstream columns onto the `*_z` model columns. The proxy is applied in those units.

## Time intercept

For each cutoff:

- Fit on rows with day ≤ D only.
- `extra_time` is the integer `time_idx` of D+1, D+2, and D+3, plus any missing integers from `max(training time_idx)` through D+3. Because D is sampled and included in training, that is three steps.
- Holdout rows are not in the fit. The random walk is projected. It is not clamped to the last training index (that clamp is `.prepare_cv_holdout_for_predict`, and this track does not use it).
- Mean of an `rw0` projection is the last training intercept. AUC, TSS, and Boyce use that mean encounter probability, so horizon change in those three metrics comes from the covariates. ELPD uses the holdout log-likelihood and can move because predictive variance grows with lead. Both facts are reported. The intercept is not given a fake seasonal drift.

## Baselines

Scored on the same holdout events as the models. An event enters the comparison only when oracle, operational proxy, persistence, and climatology all return a finite probability. Counts of `UNKNOWN` exclusions are reported. No fill-in.

1. **Persistence.** Cutoff-day egg-encounter field carried forward. In-sample encounter probability on cutoff-day training events, then inverse-distance weighted (power 2) to the holdout location, max distance 120 km. If no cutoff-day event is inside 120 km, the row is `UNKNOWN`. This is the surveyed track's cutoff-day field, not a full-domain grid.
2. **Climatology.** Day-of-year mean field of observed egg presence (y > 0), training rows only: circular day-of-year distance ≤ 15 and distance ≤ 60 km, mean of at least 20 events. Widen day-of-year to 30, then 45, with the same minimum. If still short, `UNKNOWN`. Not a model prediction and not a constant prevalence (a constant would force AUC to 0.5).

## Metrics

Same family as the spatial scores, per species, per horizon (24/48/72 h), per source (`oracle`, `operational_proxy`, `persistence`, `climatology`):

| Metric | Definition |
|---|---|
| ELPD | Sum of `.cv_delta_holdout_loglik` (encounter plus gamma positive) for oracle, operational proxy, and persistence. Persistence uses the Bernoulli log score of the carried probability plus the gamma log-likelihood from the cutoff-day positive mean carried by the same IDW rule. Climatology has no positive component; its column is `elpd_encounter_bernoulli` and is not ranked against delta ELPD. Also store `elpd_per_event` because horizons differ in n. |
| AUC | `auc_mw` on egg presence |
| TSS | `tss_at(..., 0.5)`, same threshold as `spatial_block_cv_scores.R` |
| Boyce | `cbi_continuous` |

Primary numbers pool events across the K cutoffs. Per-cutoff values are stored so one cruise cannot hide. A cutoff whose fit fails the spatial-CV convergence rule (non-finite, non-converged, non-positive-definite Hessian) is ineligible, listed, and not scored. If fewer than 6 of 8 cutoffs are eligible for a species, that species is `INSUFFICIENT`, not a pass.

## Success rule (fixed before fitting)

The product claim is the **operational proxy**, not the oracle.

For a species, a pass at 24 h requires all of:

- operational AUC > persistence AUC and operational AUC > climatology AUC
- operational TSS > persistence TSS and operational TSS > climatology TSS

on the pooled common-support events, with at least 6 eligible cutoffs.

Oracle is reported beside it. If only the oracle passes, the egg model has skill given analysed GLORYS, and the 72 h product path does not.

Horizons 48 h and 72 h are reported as differences from 24 h (AUC and TSS). Monotone decay is not required. The table is the degradation record. A failure to beat the baselines is reported as a failure.

## What this run will not say

- No `PUBLISHED` forecast, no nowcast skill claim, no live or adult-fish location.
- No harvest, fishery, or survey-design advice.
- Operational numbers are a proxy evaluation, not a verification of issued WCOFS forcing.
- Spatial AUC 0.7658 / 0.8489 is not a forecast score.
