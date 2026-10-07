# Adult vs egg northern anchovy — spatial coherence readout

**Branch:** `cursor/fishai-anchovy-adult-egg-coherence-3f1e`  
**Framing (non-negotiable):** This is a **coherence check** between two independently validated encounter models — not cross-validation of either model. Adults move and spawn; eggs drift with currents. Perfect overlap is not expected, and disagreement does not invalidate either fit.

## Models compared

| Stage | Config | Observations | Validated scores (prior work) |
|---|---|---|---|
| Eggs | `configs/models/cufes_anchovy.yaml` | CalCOFI CUFES egg tows × GLORYS | Spatial-block CV: AUC 0.85, TSS 0.41, Boyce 0.99 (PR #33) |
| Adults | `configs/models/adult_cps_anchovy.yaml` | SWFSC CPS trawl + nearshore sets × GLORYS | Spatial-block CV: ELPD −1074.69, AUC 0.85, TSS 0.46, Boyce 0.60 (PR #43) |

## Methods (10 km SCB grid)

1. **Training tables:** Public ERDDAP biology + Copernicus GLORYS covariates (same covariate set as validated configs). Single **full-data** sdmTMB delta-gamma fits (Poisson-link, spatial on, barrier mesh) produce frozen artifacts — not a repeat of spatial-block CV.
2. **Common grid:** ~10 km cell centers over the SCB pilot bbox (32–35°N, 121–117°W), UTM zone 11N km coordinates (`X`, `Y`), aggregated to public-map cell ids `g{floor(X/10)}_{floor(Y/10)}` (minimum 10 km; no finer resolution).
3. **Surfaces:** Hindcast-style `predict_engine()` on climatology days with GLORYS covariates sampled from the built field store (`scripts/build_scb_coherence_grid.py`). Out-of-domain cells (`ood_level >= 2`) are **UNKNOWN** and excluded from overlap metrics.
4. **Metrics (in-domain cells only):**
   - Pearson correlation of `p_encounter` on matched `cell_id`
   - Top-decile overlap: Jaccard index and hit rate (egg top decile vs adult top decile)
   - Seasonal alignment: repeat for representative spring (egg peak) and summer days; compare mean metrics across days
5. **Figure:** Side-by-side cell maps (`artifacts/coherence/anchovy/map_egg_vs_adult_side_by_side.png`).

Orchestration: `scripts/models/run_adult_egg_coherence.R`

## Run status (2026-10-07, cloud agent)

| Step | Status | Notes |
|---|---|---|
| CUFES events/counts | **OK** | Rebuilt from committed public fixture `tests/fixtures/cufes_pilot_distances.csv` (14,592 QC-kept events; ERDDAP live pull unavailable — NOAA PFEG gateway timeouts) |
| CUFES × GLORYS covariates | **In progress** | Copernicus credentials present; cold GLORYS subset running (`data/cache/glorys_cufes/`) |
| Adult CPS ingest | **Blocked** | NOAA ERDDAP (`oceanview` / `coastwatch` PFEG) HTTP 504 / read timeouts for `FRDCPSTrawlLHHaulCatch` and nearshore tables; no committed processed adult tables in repo |
| Full-data fits + grid coherence metrics | **Blocked** | Requires adult training table + completed egg covariates |

### Metrics (pending unblock)

| Metric | Value |
|---|---:|
| Mean grid-cell Pearson *r* (egg vs adult `p_encounter`) | *pending* |
| Mean top-decile Jaccard | *pending* |
| Mean top-decile hit rate | *pending* |

When ERDDAP and the GLORYS build complete, rerun:

```bash
# After public ingest (no vault/secret tooling):
python3 scripts/build_adult_cps_training_table.py
python3 scripts/export_adult_cps_model_tables.py
Rscript scripts/models/run_adult_egg_coherence.R
```

## Product / data rules

- **Not** live tracking, **not** harvest advice, **not** validation of either model.
- Threatened-species masking and ≥10 km public-map floor apply to any published maps.
- Copernicus GLORYS used only where `COPERNICUSMARINE_*` env credentials are supplied at runtime (training/hindcast policy in `data/SOURCES.yaml`).

## Verdict (draft — complete after metrics)

*Pending adult CPS public ingest and GLORYS covariate completion.* Expect moderate positive coherence in spring nearshore spawning habitat (adults and eggs both elevated where surveys overlap), with systematic divergence offshore and in summer when adult feeding aggregations and egg drift decouple. Final numeric verdict and figure will be filled from `artifacts/coherence/anchovy/coherence_summary.json` after a successful run.
