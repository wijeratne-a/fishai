# Jack mackerel encounter probability (all sizes) — model readout

**Product label (use everywhere):** jack mackerel encounter probability (all sizes).  
**Not** an adult-length model; no L50 / 250 mm gate.

Date: 2026-10-07. Branch: `cursor/fishai-adult-jack-mackerel`.  
Config: `configs/models/jack_mackerel_encounter_all_sizes.yaml`.  
CV script: `scripts/jack_mackerel_encounter_spatial_block_cv.R`.

## Data

| Stage | Jack mackerel (*Trachurus symmetricus*) encounters |
|--------|-----------------------------------------------------:|
| GCS mirror viability (pilot bbox, non–presence-only) | **305** (269 trawl + 36 nearshore) |
| sdmTMB fit frame after mesh / covariate / duration QC | **253** presences / **536** rows |

Length gate: **none** (`ENCOUNTER_ALL_SIZES_SPECIES` in ingestion).

## Model (validated CV spec)

After the full spec (GAM smooths + spatial `[on]`) failed **fold 4** (non-PD Hessian; folds 1–3 OK), one **sardine-playbook** retry was applied:

- **Linear** covariates (`temp_3m_z`, `sal_3m_z`, `mld_z`, `sst_grad_z`, `dist_front_z`, `log_depth_z`)
- **Spatial off** (`spatial: [off]`)
- rw0 intercept time random walk retained (same as adult CPS family)

Spatial-block CV: **60 km** blocks, **4** folds, seed **20260928**.

## Spatial-block CV scores

Artifact: `artifacts/models/jack_mackerel_encounter_all_sizes/spatial_block_cv_scores.json`.

| Metric | Value |
|--------|------:|
| **ELPD** (sum fold log-lik) | **−423.96** |
| `elpd_eligible` | **true** |
| Fold log-lik | −91.95, −87.94, −150.33, −93.73 |
| **OOF AUC** | **0.762** |
| **OOF TSS** (thr 0.5) | **0.412** |
| **OOF Boyce** | **0.956** |

## Verdict

**Validated** under FishAI ELPD rules (all four folds converged with PD Hessian).

**24 h forecast check:** not run for this CPS encounter product (rolling-origin 24 h in-repo is CUFES egg–only). CUFES jack egg remains blocked on ERDDAP 504 in this environment.

## Diagnosis (fold 4, original spec)

Holdout **fold 4** removed a spatially coherent block of nearshore / 2024–2025 events (60 holdout time indices not in training). Training retained **202** presences on **380** rows but the **spatial Matérn field + tensor-product smooths** were not identifiable on the remaining geometry (full-data and fold 4 **without** rw0 still failed with spatial+smooths on). Linear + spatial-off removed that failure mode without changing folds, seed, or covariate set.
