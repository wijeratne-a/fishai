# Market squid — CUFES egg model + CPS encounter model (readout)

Branch: `cursor/fishai-market-squid-pipeline-86df`.

## 1. CUFES egg model (priority)

**Config:** `configs/models/cufes_squid.yaml` (mirrors `cufes_anchovy.yaml`; `species.taxon: squid` → `squid_eggs` in `cufes_counts`).

**Spatial-block CV protocol:** `configs/cufes_squid_spatial_block_cv_scores.yaml` — 60 km blocks, seed **20260928**, **4** folds (same as anchovy/sardine).

### CUFES×GLORYS training table (2026-10-08, ERDDAP recovered)

Cold rebuild: `SKIP_CACHE=1 bash scripts/ci/rebuild_cufes_glorys_training_table.sh` (ERDDAP `erdCalCOFIcufes` on oceanview.pfeg.noaa.gov).

| Table | Rows |
| --- | --- |
| `cufes_events.parquet` (QC-kept) | **14,592** |
| `cufes_counts.parquet` (all taxa long) | **82,426** |
| `cufes_counts` squid taxon rows | **11,612** |
| `cufes_training_covariates.parquet` | **14,592** |
| Covariate drops | **5,640** |

### Egg CV scores

**Protocol:** `configs/cufes_squid_spatial_block_cv_scores.yaml` — 60 km blocks, seed **20260928**, 4 folds.  
**Artifact:** `prereg/cufes_squid_spatial_block_cv_scores.json` (`status: ok`).

| Run | Spec | Folds | ELPD | AUC | TSS | Boyce |
| --- | --- | --- | --- | --- | --- | --- |
| Full (smoothers + spatial on) | original | **3/4** (fold 1 non–PD) | NA | NA | NA | NA |
| **Simplified retry (playbook)** | linear `_z`; spatial/spatiotemporal **off**; **rw0** | **4/4** | **−23030.46** | **0.767** | **0.360** | **1.0** |

Retry fit rows: **8,632**; OOF **8,632**; fold log-lik: −5608.55, −6721.05, −6940.25, −3760.61 (`elpd_eligible: true`).

**24 h rolling-origin forecast (eggs):** not run in this turn (CV validated on simplified spec only).

---

## 2. CPS encounter model (second; honestly labeled)

**Not an adult model.** Specimen mirror has **weights only** (no mantle length); no defensible L50. Maturity literature (Fields 1965; spawning size ~132–152 mm ML) is cited for transparency only — **not** used as a cutoff.

**Semantics:** `squid encounter (all sizes; maturity unfiltered — no length data)` (`src/fishai/ingestion/adult/squid_encounter.py`).

**CPS catch staging:** public GCS mirror (Phase 1); **309** non–presence-only presences in pilot bbox (trawl 291 + nearshore 18).

**Training table builder:** `scripts/build_market_squid_encounter_table.py` (GLORYS join when table build is run).

**Spatial-block CV protocol:** `configs/market_squid_encounter_spatial_block_cv_scores.yaml` — 60 km blocks, seed **20260928**, **4** folds (same as adult/CUFES).

**Model config:** `configs/models/cps_market_squid_encounter.yaml` — sdmTMB **delta Poisson-link** on **binary 0/1 encounter** (encounter-only; not biomass; **not an adult model**).

**GLORYS training table:** built via `scripts/build_market_squid_encounter_table.py` (782 physics events in pilot bbox; 572 model-ready rows after covariate QC).

**Model-ready export (encounter presences, unique events):** **275** total (**270** trawl + **5** nearshore) after GLORYS QC — see `data/processed/adult_cps/model_ready/adult_cps_model_export_market_squid_encounter.json`. Pilot-bbox presences before GLORYS drops: **310** unique events (**292** trawl + **18** nearshore). The **110 + 29 = 139** figure was **not** reproduced under this mirror + export rules; if that slice is required, specify the exact QC filter.

**Encounter CV scores:** `prereg/market_squid_encounter_spatial_block_cv_scores.json`.

| Run | Spec | Folds converged | ELPD | AUC | TSS | Boyce |
| --- | --- | --- | --- | --- | --- | --- |
| Full (smoothers + spatial on) | `cps_market_squid_encounter.yaml` (original) | **0/4** (non–PD Hessian) | — | — | — | — |
| Simplified retry (playbook) | linear `_z` covariates; spatial/spatiotemporal **off**; daily **rw0** kept | **0/4** (non–PD Hessian) | — | — | — | — |

Both runs: 60 km blocks, seed **20260928**, 4 folds, 572 fit rows; `elpd_eligible: false`, `n_oof_rows: 0`. No further spec changes per retry policy. **24 h forecast:** not run (CV not validated).

---

## Next ops

1. Squid egg CV: diagnose fold 1 non–PD Hessian or apply a preregistered simplified retry if policy allows.
2. If egg CV validates (`elpd_eligible` + 4/4 folds), run temporal holdout per forecast branch `cursor/fishai-forecast-validation-a046`.
3. Encounter model: no further spec changes after linear/spatial-off retry (0/4 folds); see §2.
