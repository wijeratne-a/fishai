# CUFES market squid egg 24 h rolling-origin forecast validation

**Status:** Preregistered before fitting. Scores: `prereg/cufes_squid_24h_forecast_scores.json`. Readout: `prereg/cufes_squid_24h_forecast_readout.md`. **This is not a forecast product** and does not publish operational nowcasts.

**Claim under test:** The validated market squid egg-encounter model (`configs/models/cufes_squid.yaml`) has skill at future times (24/48/72 h lead), not only on held-out spatial blocks. Spatial-block scores on this branch (`prereg/cufes_spatial_block_cv_scores.json`, squid 4/4 folds, AUC 0.7671, TSS 0.36) are a different claim and are not reused as forecast evidence.

**Target:** Egg encounter probability for market squid eggs in the Southern California Bight CUFES record. Not adult squid location, not a track, not harvest advice.

## Model spec (unchanged)

Same validated spec as spatial-block CV on `cursor/fishai-market-squid-pipeline-86df`:

- Config: `configs/models/cufes_squid.yaml`
- Taxon `squid`, Poisson-link delta-gamma (`delta_type: poisson-link`)
- Shared linear formula: `temp_3m_z + sal_3m_z + mld_z + sst_grad_z + dist_front_z + log_depth_z`
- Spatial `[off, off]`, spatiotemporal `[off, off]`, `time_varying ~ 1` with type `rw0`
- `egg_split.test_end`: `2022-04-27`
- Effort offset `log(volume_m3)` on holdout events

Training tables are not modified. Each cutoff builds its mesh from that cutoff's training rows only (`build_fishai_production_mesh`). Fits use `fit_delta_engine()` with `extra_time` (dense projection: holdout time indices plus any missing integers from max training `time_idx` through D+3).

## K and cutoff rule

**K = 8** (two cutoffs per meteorological season: DJF, MAM, JJA, SON).

One refit per cutoff. Physics and baselines are scored from that fit, not extra fits. Eight sequential fits, one TMB thread, checkpointed under `artifacts/forecast_temporal_holdout/`.

A day **D** is an eligible cutoff only if:

1. D, D+1, D+2, and D+3 each have at least one eligible event (horizons 24/48/72 h).
2. Training rows with day ≤ D: ≥ 2000 rows, ≥ 30 distinct days, both presence and absence.
3. D+3 ≤ `egg_split.test_end` (`2022-04-27`).

The window is the full egg record through `test_end`, not only `fit_end` (`2017-12-31`).

Deterministic cutoff pick (before any fit):

1. Inventory eligible D from the squid QC frame.
2. Within each season, earliest and latest eligible dates at least 365 days apart; if none, the two farthest dates (gap recorded).
3. If a season has fewer than two eligible dates → `design_infeasible` (do not drop seasons).
4. Selected cutoffs at least 30 days apart.

## Physics

### Oracle

Holdout rows use retrospective GLORYS covariates already on the training table. `lane = retrospective`. Not an issued forecast.

### Operational

Public NOAA WCOFS archive (`noaa-nos-ofs-pds`) does not cover this egg record. Unauthenticated checks on 2026-10-08: `wcofs/netcdf/202407/` returns HTTP 200; `wcofs/netcdf/202201/` returns HTTP 404. CUFES scoring ends 2022-04-27. No issued WCOFS fields are scored.

**Pre-declared proxy** (`physics_source = damped_anomaly_proxy`, `operational_claim = NOT_ISSUED_FORECAST`):

```
x_hat = clim + exp(-h / 3) * (x_cutoff - clim)
```

- `tau = 3` days fixed.
- `x_cutoff`: IDW (power 2) on cutoff-day training events within 120 km.
- `clim`: training-only local mean (DOY windows 15/30/45, 60 km, min 20 events else UNKNOWN).
- `log_depth_z` static from the holdout row.
- `*_z` columns are upstream copies, not re-standardized.

## Baselines

Common-support only (finite oracle, operational proxy, persistence, climatology).

1. **Persistence:** cutoff-day encounter field IDW (power 2, 120 km).
2. **Climatology:** DOY-local presence rate (same windows as operational climatology).

## Metrics and pass rule

Horizons 24/48/72 h reported; **only 24 h gates pass/fail**.

Pass at 24 h requires strictly greater operational AUC and TSS than both persistence and climatology on pooled common-support events, with ≥ 6 of 8 eligible cutoffs. Fewer than 6 eligible → `INSUFFICIENT`. Ties fail.

Convergence gate matches spatial CV: non-finite, non-converged, or non-PD Hessian → ineligible cutoff.

## What this run will not say

- No published forecast, no operational nowcast claim, no adult-fish map product.
- Proxy scores are not WCOFS verification.
- Spatial-block squid AUC 0.7671 is not a forecast score.
