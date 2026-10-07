# Market squid — CUFES egg model + CPS encounter model (readout)

Branch: `cursor/fishai-market-squid-pipeline-86df`.

## 1. CUFES egg model (priority)

**Config:** `configs/models/cufes_squid.yaml` (mirrors `cufes_anchovy.yaml`; `species.taxon: squid` → `squid_eggs` in `cufes_counts`).

**Spatial-block CV protocol:** `configs/cufes_squid_spatial_block_cv_scores.yaml` — 60 km blocks, seed **20260928**, **4** folds (same as anchovy/sardine).

### Egg CV scores (this environment)

**Status: blocked** — no ELPD / AUC / TSS produced.

| Metric | Value |
| --- | --- |
| ELPD | — (not computed) |
| ELPD eligible | **false** |
| AUC / TSS / Boyce | — |
| Failed folds | — |

**Reason:** The shared CUFES×GLORYS training table could not be materialized:

- NOAA ERDDAP (`erdCalCOFIcufes` on oceanview/coastwatch) failed with **504**, read timeouts, and **SSL EOF** on all fetch strategies tried (yearly, half-year, single-cruise).
- Public GHCR cache `cufes-glorys-rebuild:612cb155…` is **not published** (`docker pull`: not found).
- `COPERNICUSMARINE_*` credentials **are** present locally; the blocker is **ERDDAP CUFES ingest**, not Copernicus.

Artifact: `prereg/cufes_squid_spatial_block_cv_scores.json` (`status: blocked`).

**24 h rolling-origin forecast (eggs):** not run — requires a validated egg CV fit first (`prereg/cufes_forecast_temporal_holdout_design.md`).

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

**Encounter CV scores:** `prereg/market_squid_encounter_spatial_block_cv_scores.json` — **blocked / incomplete** in this run (CV started but sequential fits did not finish in time). Re-run:

`Rscript scripts/models/run_spatial_block_cv_scores.R configs/market_squid_encounter_spatial_block_cv_scores.yaml`

**24 h forecast:** not run (encounter CV not validated).

---

## Next unblock (ops)

1. Rebuild CUFES×GLORYS where ERDDAP is healthy (or publish GHCR `cufes-glorys-rebuild` cache tar for key `612cb155…`).
2. Re-run: `Rscript scripts/models/run_spatial_block_cv_scores.R configs/cufes_squid_spatial_block_cv_scores.yaml`
3. If egg CV validates (`elpd_eligible` + 4/4 folds), run temporal holdout per forecast branch `cursor/fishai-forecast-validation-a046`.
4. Encounter CV: build table → `configs/models/cps_market_squid_encounter.yaml` (to add) → adult-style spatial-block CV.
