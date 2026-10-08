# Adult vs egg northern anchovy — spatial coherence readout

**Branch:** `cursor/fishai-anchovy-adult-egg-coherence-3f1e`  
**Framing (non-negotiable):** This is a **coherence check** between two independently validated encounter models — not cross-validation of either model. Adults move and spawn; eggs drift with currents. Perfect overlap is not expected, and disagreement does not invalidate either fit.

## Models compared

| Stage | Config | Observations | Validated scores (prior work) |
|---|---|---|---|
| Eggs | `configs/models/cufes_anchovy.yaml` | CalCOFI CUFES egg tows × GLORYS | Spatial-block CV: AUC 0.85, TSS 0.41, Boyce 0.99 (PR #33) |
| Adults | `configs/models/adult_cps_anchovy.yaml` | SWFSC CPS trawl + nearshore sets × GLORYS | Spatial-block CV: ELPD −1074.69, AUC 0.85, TSS 0.46, Boyce 0.60 (PR #43) |

## Methods (10 km SCB grid)

1. **Training tables:** Public ERDDAP biology (NOAA PFEG `oceanview`, 2026-10-07 recovery) + Copernicus GLORYS covariates (same covariate set as validated configs). Single **full-data** sdmTMB delta-gamma fits (Poisson-link, spatial on) produce frozen artifacts — not a repeat of spatial-block CV.
2. **Common grid:** ~10 km cell centers over the SCB pilot bbox (32–35°N, 121–117°W), UTM zone 11N km coordinates (`X`, `Y`), aggregated to public-map cell ids `g{floor(X/10)}_{floor(Y/10)}` (minimum 10 km; no finer resolution).
3. **Surfaces:** Hindcast-style `predict_engine()` on **shared survey calendar days** (dates where both models have a frozen `time_idx` in training), with GLORYS covariates from the CUFES subset cache (`scripts/build_scb_coherence_grid.py`). Out-of-domain cells (`ood_level >= 2`) and cells with incomplete physics are **UNKNOWN** and excluded from overlap metrics.
4. **Metrics (in-domain cells only):**
   - Pearson correlation of `p_encounter` on matched `cell_id`
   - Top-decile overlap: Jaccard index and hit rate (egg top decile vs adult top decile)
   - Seasonal alignment: mean metrics across representative days (spring April in this run)
5. **Figure:** Side-by-side cell maps (`artifacts/coherence/anchovy/map_egg_vs_adult_side_by_side.png`).

Orchestration: `scripts/models/run_adult_egg_coherence.R`

### Compute note (this run)

Validated YAML **formula, covariates, delta family, and spatial random fields** were used. For cloud-agent wall time, coherence **production fits** omitted the barrier land mesh and used **15 km** mesh cutoff (vs 9 km + barrier in the locked CV configs). Scores below are therefore a coherence check on slightly coarser spatial basis functions, not a reproduction of the frozen production mesh from PR #33 / #43.

## Run status (2026-10-08, cloud agent)

| Step | Status | Notes |
|---|---|---|
| CUFES × GLORYS covariates | **OK** | `cufes_training_covariates.parquet` (12,083 in-domain rows) |
| Adult CPS ERDDAP ingest | **OK** | Trawl + nearshore rebuild via `scripts/rebuild_adult_cps_inputs.py` |
| Adult CPS × GLORYS | **OK** | 400 observation rows / 706 physics events after QC (`export_adult_cps_model_tables.py`) |
| Full-data fits + grid coherence | **OK** | Artifacts under `artifacts/models/anchovy_{egg,adult}_coherence/` (local; not committed) |

### Coherence scores (10 km SCB, in-domain cells)

| Metric | Mean | By day |
|---|---:|---|
| Pearson *r* (`p_encounter`) | **0.603** | 2014-04-24: 0.533 (*n*=401); 2017-04-04: 0.674 (*n*=655) |
| Top-decile Jaccard | **0.271** | 2014-04-24: 0.414; 2017-04-04: 0.128 |
| Top-decile hit rate (egg→adult) | **0.406** | 2014-04-24: 0.585; 2017-04-04: 0.227 |

Spring (April) pooled (*n*=2 days): *r*=0.603, Jaccard=0.271, hit rate=0.406 — see `artifacts/coherence/anchovy/coherence_summary.json`.

**Climatology days used:** `2014-04-24`, `2017-04-04` (nearest shared CUFES/CPS survey dates to April mid-month; both models’ frozen `time_idx_levels`).

Reproduce:

```bash
python3 scripts/rebuild_adult_cps_inputs.py
python3 scripts/build_adult_cps_training_table.py
python3 scripts/export_adult_cps_model_tables.py
Rscript scripts/models/run_adult_egg_coherence.R
```

## Product / data rules

- **Not** live tracking, **not** harvest advice, **not** validation of either model.
- Threatened-species masking and ≥10 km public-map floor apply to any published maps.
- Copernicus GLORYS used only where `COPERNICUSMARINE_*` env credentials are supplied at runtime (training/hindcast policy in `data/SOURCES.yaml`).

## Verdict

**Moderate positive coherence** on the 10 km grid: mean Pearson *r* ≈ **0.60** across two spring survey-aligned days, with **~27%** Jaccard overlap of top-decile cells and **~41%** of egg hot-spot cells also in the adult top decile (pooled). The stronger alignment in 2014 and weaker top-decile overlap in 2017 are consistent with a coherence check (not validation): shared habitat drivers and nearshore spawning structure can align egg and adult encounter surfaces while trawl/nearshore adults and CUFES eggs sample different life stages and processes. Disagreement offshore and in years with weaker top-decile overlap does **not** invalidate either independently scored model.
