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

**Spatial-block CV / 24 h forecast:** pending successful GLORYS training-table build + R `sdmTMB` stack (local `renv::restore` incomplete: `tmbstan` / `sdmTMB` install failure in this VM).

---

## Next unblock (ops)

1. Rebuild CUFES×GLORYS where ERDDAP is healthy (or publish GHCR `cufes-glorys-rebuild` cache tar for key `612cb155…`).
2. Re-run: `Rscript scripts/models/run_spatial_block_cv_scores.R configs/cufes_squid_spatial_block_cv_scores.yaml`
3. If egg CV validates (`elpd_eligible` + 4/4 folds), run temporal holdout per forecast branch `cursor/fishai-forecast-validation-a046`.
4. Encounter CV: build table → `configs/models/cps_market_squid_encounter.yaml` (to add) → adult-style spatial-block CV.
