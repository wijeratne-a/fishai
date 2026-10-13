# Jack mackerel catch-data proxy scoping test

**Branch:** `cursor/fishai-catch-proxy`  
**Hypothesis:** Public commercial catch summaries carry behavioral signal about where fish are aggregated in space/time, beyond GLORYS physics.

## Public catch data found

| Source | Access | Spatial | Temporal | Species | Usable for SDM join? |
|--------|--------|---------|----------|---------|---------------------|
| **PacFIN ALL005** (CPS SAFE Portal) | Public APEX export | California **port group** (10 areas) | **Calendar year** (report name says “monthly”; export is annual totals) | Jack mackerel (`JMCK`) + other CPS | **Yes (coarse)** |
| CDFW MFDE Landings by Block | Power BI export | 10′ fishing **block** | UI defaults to single year; multi-year export not automated here | Jack mackerel | Partial (2025 snapshot only in this run) |
| CDFW / PacFIN fish tickets & logbooks | Confidential / NDA | Trip/block | Trip/day | Yes | **No** (not public) |
| SWFSC CPS trawl/nearshore ERDDAP | Public | Set/haul point | Event time | Yes | **No** (fishery-**independent** survey — already the SDM label) |

**Primary covariate file:** `data/raw/pacfin/all005_ca_2003_2025.csv` (5,132 rows, all CA species; JMCK row per year).

Attribution: Pacific Fisheries Information Network (PacFIN), CPS SAFE Portal — shoreside landings/revenue reports.

## Covariate construction

For each adult CPS survey event (same frame as `jack_mackerel_encounter_all_sizes`):

1. **Port group** — offshore lat band within the SCB pilot (32–35°N): SDA / LAA / SBA / MNA (PacFIN port-complex proxy at sea; not vessel-reported block).
2. **`comm_catch_jmck_mt`** — PacFIN JMCK landed weight (metric tons) for `(landing_year, port_group)`.
3. **`log_comm_catch_jmck`** — `log1p(comm_catch_jmck_mt)`.
4. **`comm_fleet_effort_mt`** — sum of PacFIN CPEL “WETF” species tonnage (anchovy, sardine, mackerels, squid) in the same port-year (effort / fishing-intensity proxy).
5. **`log_comm_fleet_effort`** — `log1p(comm_fleet_effort_mt)`.

Confidential/suppressed cells (`*`) treated as **0 mt** (non-confidential public table only).

Builder: `scripts/build_pacfin_catch_covariates.py` → `data/processed/commercial_catch/adult_cps_training_table_with_catch.parquet`.

## Bias correction (preferential sampling)

**Assumption:** Commercial vessels prefer areas with higher expected catch (Conn, Thorson, Johnson preferential-sampling framing). Raw landings are **not** unbiased abundance.

**Mitigation in this scoping test (minimal):**

- Include **`log_comm_fleet_effort`** (total CPS WETF tonnage in port-year) as a covariate — partial control for how much fishing pressure occurred in that port-year.
- **Do not** interpret coefficients as causal abundance; this is a predictive skill test only.
- Spatial mismatch (port-of-landing vs survey tow location) adds attenuation bias; we expect conservative effect sizes.

**Not done here:** Trip-level effort models, spatial PPML/Bayesian preferential sampling, or block-level MFDE time series (would need reliable multi-year block export).

## Model comparison

Same **4-fold spatial-block CV** (`artifacts/spatial_block_cv/adult_cps_fold_assignment.csv`), same sdmTMB spec as validated baseline (linear physics + rw0, spatial off).

| Model | Config |
|-------|--------|
| Baseline | `configs/models/jack_mackerel_encounter_all_sizes.yaml` |
| + catch | `configs/models/jack_mackerel_encounter_all_sizes_catch.yaml` |

Script: `scripts/jack_mackerel_catch_proxy_spatial_block_cv.R`  
Scores: `artifacts/models/jack_mackerel_encounter_all_sizes_catch/spatial_block_cv_comparison.json`

**PASS rule:** out-of-fold **AUC higher** and **Brier lower** vs physics-only.

## Results (this run, same folds)

Artifact: `artifacts/models/jack_mackerel_encounter_all_sizes_catch/spatial_block_cv_comparison.json`

| Model | OOF AUC | OOF Brier | OOF TSS (0.5) | Fit rows | Presences |
|-------|--------:|----------:|--------------:|---------:|----------:|
| Physics-only (refit) | 0.762 | 0.199 | 0.412 | 536 | 253 |
| Physics + PacFIN catch | 0.763 | 0.200 | 0.412 | 536 | 253 |

Δ AUC = +0.0006; Δ Brier = +0.0007 (worse).

## Verdict: **FAIL**

Catch covariates did **not** improve both AUC and Brier. AUC moved marginally up; Brier moved slightly up (worse calibration). Coarse annual port-group landings likely carry little independent signal beyond physics at survey-tow resolution.

## Validated baseline reference (prior committed run)

From `artifacts/models/jack_mackerel_encounter_all_sizes/spatial_block_cv_scores.json`: OOF **AUC 0.762**, **TSS 0.412** (536 rows, 253 presences).
