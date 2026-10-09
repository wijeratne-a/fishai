# Adult northern anchovy 24 h encounter forecast: rolling-origin design

**Status:** Approved for execution on branch `cursor/fishai-adult-anchovy-24h-forecast-e867`. Scores target path: `prereg/adult_anchovy_24h_forecast_scores.json`. Plain-language result: `prereg/adult_anchovy_24h_forecast_readout.md`. This file does not publish a forecast.

**Claim under test:** The validated adult anchovy encounter model (`configs/models/adult_cps_anchovy.yaml`; spatial-block CV on branch `cursor/fishai-adult-anchovy-fit-cv-79f5`) has skill at **future** encounter times (24/48/72 h lead), not only at held-out locations. Spatial-block skill is a different claim and is not reused here.

**Target:** Adult/juvenile northern anchovy **encounter** on SWFSC CPS trawl hauls and nearshore purse-seine sets in the Southern California Bight pilot domain. Not egg occurrence, not a track, not harvest advice.

## Model spec (unchanged from spatial CV)

Same validated adult spec as `prereg/adult_anchovy_spatial_block_cv_scores.json`:

- Config: `configs/models/adult_cps_anchovy.yaml`
- Poisson-link delta-gamma, shared smooths on `temp_3m_z`, `sal_3m_z`, `mld_z`, `sst_grad_z`, `dist_front_z`, `log_depth_z`
- Spatial on, spatiotemporal off, `time_varying ~ 1` with type `rw0`
- Barrier mesh, cutoff 9 km, range guess 60 km, `range_fraction` 0.1
- Effort offset `log(effort_duration_min)` (nearshore reference effort per export script)

Training table paths are not modified. Each cutoff builds its mesh from that cutoff's training rows only.

## K and cutoff rule

**K = 8** (two cutoffs in each meteorological season), same selection machinery as `prereg/cufes_forecast_temporal_holdout_design.md`.

A day **D** is an eligible cutoff only if:

1. D, D+1, D+2, and D+3 each have at least one eligible event (horizons 24/48/72 h).
2. Training rows are events with day ≤ D. Require ≥ **150** rows, ≥ **30** distinct days, and both presence and absence. (The egg protocol uses 2000 rows because the CUFES egg frame is an order of magnitude larger; the adult CPS anchovy modeling frame is ~400 rows after QC — 2000 would make every cutoff ineligible.)
3. D+3 is on or before `test_end`, computed as the latest event day in the adult frame minus three days.

Season of a cutoff is the season of **D** (DJF, MAM, JJA, SON).

Deterministic pick before any fit:

1. Inventory eligible D from the adult event table.
2. Within each season, sort eligible dates; take earliest and latest at least 365 days apart (or the farthest pair with a note).
3. Enforce at least **30 days** between selected cutoffs so holdout windows do not overlap.
4. **Egg calendar reference:** the eight locked egg cutoffs from `prereg/cufes_forecast_temporal_holdout_scores.json` are recorded as `egg_reference_cutoffs`; overlap with the adult-selected set is reported in `egg_overlap_cutoffs`. Adult CPS coverage begins in 2003, so pre-2003 egg dates cannot be shared.
5. **DJF gap:** fishery-independent adult CPS tows in this frame rarely fall in DJF with enough training depth for the eligibility rule. If strict four-season selection is infeasible, cutoffs are chosen with `adult_inventory_best_effort` (up to two dates per season that has eligible days, then fill to eight with 30-day separation). This is recorded in `cutoff_calendar` and `cutoff_notes`.

## Time intercept

For each cutoff, fit on rows with day ≤ D only. **`extra_time` is holdout-only:** the integer `time_idx` values for D+1, D+2, and D+3 only. CPS adult surveys are sparse (multi-day cruises separated by months or years), so filling every missing daily `time_idx` between the last training day and D+3 — as in the dense CUFES egg record — makes the random-walk projection unstable (non-PD Hessian). The egg protocol uses dense daily fill; this adult protocol does not.

## Physics (operational proxy)

Identical to the egg validation:

```
x_hat = clim + exp(-h / 3) * (x_cutoff - clim)
```

- `tau = 3` days fixed; `physics_source = damped_anomaly_proxy`
- `operational_claim = NOT_ISSUED_FORECAST` on every operational metric
- IDW/climatology support rules match the egg design (120 km cutoff track; 60 km / DOY windows for climatology)

## Baselines

Persistence (cutoff-day IDW encounter field) and day-of-year climatology on training presences, same rules as eggs. Common-support only; `UNKNOWN` rows excluded from pooled metrics.

## Success rule (fixed before fitting)

For adult anchovy, **pass at 24 h** requires:

- operational proxy AUC **>** persistence AUC **and** operational proxy AUC **>** climatology AUC
- operational proxy TSS **>** persistence TSS **and** operational proxy TSS **>** climatology TSS

on pooled common-support events, with at least **6** of **8** eligible cutoffs.

Horizons 48 h and 72 h are reported for degradation; only 24 h gates pass/fail.

## What this run will not say

- No published forecast, no live location, no harvest advice.
- Operational numbers are proxy evaluation, not verification of issued WCOFS forcing.
- Spatial-block AUC 0.85 is not a forecast score.
