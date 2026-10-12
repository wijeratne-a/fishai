# Jack mackerel behavioral-regime SDM — Tier 1 readout

**Product:** jack mackerel encounter probability (all sizes).  
**Branch:** `cursor/fishai-behavioral-regime-d830`  
**Baseline config:** `configs/models/jack_mackerel_encounter_all_sizes.yaml` (PR #53 merged spec).  
**Interaction config:** `configs/models/jack_mackerel_encounter_behavioral_regime.yaml`.  
**CV script:** `scripts/jack_mackerel_behavioral_regime_tier1_cv.R`.

## Design

Behavioral regime is encoded as **formula interactions**, not data splits or length gates.

| Factor | Encoding |
|--------|----------|
| Season | Meteorological **DJF / MAM / JJA / SON** via `forecast_season()` on event UTC date (same buckets as CUFES temporal-holdout prereg). |
| Day/night | **Civil UTC:** day if hour ∈ [6, 18), else night, from trawl/set `time` timestamps merged from `adult_cps_events.parquet`. |

**Interaction covariates (dynamic physics only):** `temp_3m_z`, `sal_3m_z`, `mld_z`, `sst_grad_z`, `dist_front_z`.  
**Main effect only:** `log_depth_z` (static bathymetry; not season-split).

Spatial-block CV: **60 km** blocks, **4** folds, same fold assignment CSV as baseline (`artifacts/spatial_block_cv/adult_cps_fold_assignment.csv`).

## Verdict rule (Tier 1)

**PASS** only if the interaction model beats baseline on **both** out-of-fold **AUC** and **Brier** with all folds converged. Otherwise **FAIL** (no mixture / larger spec escalation).

Results artifact: `artifacts/models/jack_mackerel_behavioral_regime/tier1_cv_comparison.json`.
