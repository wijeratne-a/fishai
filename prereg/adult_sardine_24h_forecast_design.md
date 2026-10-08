# Adult Pacific sardine 24 h encounter forecast: rolling-origin design

**Status:** Approved for execution on branch `cursor/fishai-adult-sardine-simple-hurdle`. Scores target path: `prereg/adult_sardine_24h_forecast_scores.json`. Plain-language result: `prereg/adult_sardine_24h_forecast_readout.md`. This file does not publish a forecast or map product.

**Claim under test:** The validated adult sardine encounter model (`configs/models/adult_cps_sardine.yaml`; spatial-block CV ELPD −588.9487, OOF AUC 0.6769, TSS 0.1953, Boyce 0.7538, 458 rows, 59 presences) has skill at **future** encounter times (24/48/72 h lead), not only at held-out locations.

**Target:** Adult Pacific sardine **encounter** on SWFSC CPS trawl hauls and nearshore purse-seine sets in the Southern California Bight pilot domain. Not egg occurrence, not a track, not harvest advice.

## Model spec (unchanged from spatial CV)

Same validated adult spec as `artifacts/models/adult_sardine/spatial_block_cv_scores.json`:

- Config: `configs/models/adult_cps_sardine.yaml`
- Poisson-link delta-gamma, shared **linear** formula (no smooths): `~ temp_3m_z + sal_3m_z + mld_z + sst_grad_z + dist_front_z + log_depth_z`
- Spatial `[off, off]`, spatiotemporal `[off, off]`, `time_varying ~ 1` with type `rw0`
- Barrier mesh unchanged (cutoff 9 km, range guess 60 km, `range_fraction` 0.1)
- Effort offset `log(effort_duration_min)`

Do not edit the validated YAML fields above. Training table paths are not modified. Each cutoff builds its mesh from that cutoff's training rows only.

## K and cutoff rule

**K = 8** (two cutoffs per meteorological season when feasible).

A day **D** is an eligible cutoff only if:

1. D, D+1, D+2, and D+3 each have at least one eligible sardine-frame event (horizons 24/48/72 h).
2. Training rows are events with day ≤ D. Require ≥ **150** rows, ≥ **30** distinct days, and both presence and absence.
3. D+3 is on or before `test_end` (latest event day minus three days).

Season of a cutoff is the season of **D** (DJF, MAM, JJA, SON).

Deterministic pick before any fit:

1. Inventory eligible D from the adult sardine event table.
2. Within each season, sort eligible dates; take earliest and latest at least 365 days apart (or the farthest pair with a note).
3. Enforce at least **30 days** between selected cutoffs.
4. Record the eight locked egg cutoffs from `prereg/cufes_forecast_temporal_holdout_scores.json` as `egg_reference_cutoffs`; report overlap in `egg_overlap_cutoffs`.
5. **DJF gap:** if strict four-season selection is infeasible, use `adult_inventory_best_effort` (`select_forecast_cutoffs_best_effort`). Record `cutoff_calendar = adult_inventory_best_effort` and notes. Fewer than six cutoff candidates ⇒ `design_infeasible`.

## Time intercept

For each cutoff, fit on rows with day ≤ D only. **`extra_time` is holdout-only:** integer `time_idx` values for D+1, D+2, and D+3 only (not dense daily fill through the holdout).

## Physics (operational)

Public NOAA PDS issued WCOFS **fields** when the archive covers the lead; otherwise the lead-damped anomaly proxy for that event only.

**Issued forecast (when archive covers cutoff cycle D):**

- Holdout event on calendar day D+h (h = 1, 2, 3): use a forecast issued from the **03z cycle on cutoff day D**, lead `f024` / `f048` / `f072` (not the event-day nowcast).
- Public objects from bucket `noaa-nos-ofs-pds` only. Prefer the ROMS `fields` forecast (`wcofs.t03z.*.fields.f0HH.nc` or legacy `nos.wcofs.fields.f0HH.*.nc`). Classic NetCDF (`CDF\x02`, used in 2024) is opened with the scipy engine; HDF5/NetCDF-4 uses h5netcdf. When `fields.f0HH` is not published, use the issued `regulargrid.f0HH` forecast (standard depths, positive down) and bin it onto the GLORYS grid before the same covariate functions. The S3 key on each row records which product was used.
- Archive starts **2024-07-01**; cycles before that ⇒ proxy with `coverage_forced_proxy`. A missing object after that date is `missing_wcofs_object`, not a silent proxy.
- Coarsen onto the GLORYS grid (`coarsen_wcofs_to_glorys` for ROMS fields; equal-weight binning for `regulargrid`), then `compute_wcofs_covariates_on_glorys_grid`. Sample the event's GLORYS cell. Map to `temp_3m_z`, `sal_3m_z`, `mld_z`, `sst_grad_z`, `dist_front_z`. `log_depth_z` stays the static training value. **No** WCOFS→GLORYS bias-correction map (frozen artifact not in repo).
- Labels: `physics_source = wcofs_issued_forecast`, `operational_claim = ISSUED_FORECAST`, record S3 key and lead tag (and fallback metadata when `resolve_lead_for_offset` applies).

**Proxy (coverage or missing field):**

```
x_hat = clim + exp(-h / 3) * (x_cutoff - clim)
```

- `tau = 3` days; IDW power 2 within 120 km; climatology DOY windows 15/30/45, 60 km, min 20.
- `physics_source = damped_anomaly_proxy`, `operational_claim = NOT_ISSUED_FORECAST`, disclose reason (e.g. `coverage_forced_proxy`).

Every scored row carries `physics_source` and `operational_claim`. Pooled JSON counts `n_issued_wcofs` vs `n_proxy` among common-support 24 h rows.

## Baselines

Persistence (cutoff-day IDW encounter within 120 km) and day-of-year climatology on training presences. Common-support only.

## Oracle

Retrospective GLORYS covariates already on holdout rows (`lane_oracle = retrospective`). Not the product.

## Success rule (fixed before fitting)

**Pass at 24 h** only if operational AUC **>** persistence AUC **and** operational AUC **>** climatology AUC **and** operational TSS **>** persistence TSS **and** operational TSS **>** climatology TSS on pooled common-support events, with at least **6** of **8** eligible cutoffs (converged; non-PD Hessian is failure).

Fewer than six eligible cutoffs ⇒ `fit_status = INSUFFICIENT`, `pass_24h = false`; do not pool pass/fail metrics.

48 h and 72 h are reported for degradation only.

## What this run will not say

- No published forecast, map product, live tracking, or harvest advice.
- If every operational row is proxy, scores are **NOT_ISSUED_FORECAST** and must not be read as WCOFS verification.
