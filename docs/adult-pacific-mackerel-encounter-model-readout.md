# Pacific mackerel encounter probability (all sizes) — model readout

Branch: `cursor/fishai-pacific-mackerel-pipeline-ef97`  
Species: *Scomber japonicus* (Pacific mackerel)

**Product label:** Pacific mackerel **encounter probability (all sizes)** — not an adult or maturity-gated model.

## Length gate

**None.** All non–presence-only catch rows for *S. japonicus* in the pilot bbox enter the encounter frame (implied-zero rules unchanged). Specimen median length is attached when available for audit only; it is **not** used to exclude juveniles.

## Phase 1 — viability gate (exact counts)

Non–presence-only presences in pilot bbox (all sizes):

| Source | Species catch rows | Presence-only excluded | Non–presence-only presences |
|--------|-------------------:|-----------------------:|----------------------------:|
| Trawl | 122 | 1,379 (haul-level) | **122** |
| Nearshore | 94 | 0 | **94** |
| **Total (catch-level)** | | | **216** |

Verdict: **viable — proceed** (≥150).

## Training table (all sizes + implied-zero + GLORYS QC)

| Stage | Count |
|-------|------:|
| Observation rows (mackerel-only) | 777 |
| Physics events (pilot bbox) | 775 |
| Rows after GLORYS / physics QC (kept) | 775 |
| **Modeling frame** (export: biology + effort QC) | **565** |
| **Presences in modeling frame** | **132** (113 trawl + 19 nearshore) |
| Absences | 433 |

Build: `python3 scripts/build_adult_mackerel_training_table.py --all-sizes`  
Export: `python3 scripts/export_adult_mackerel_model_tables.py`  
Ingest: NOAA public GCS mirror. GLORYS join: Copernicus credentials at build time.

## Model spec (encounter-only; no hurdle)

**sdmTMB binomial** encounter GLMM with `log(effort_duration_min)` offset.

- Config: `configs/models/adult_pacific_mackerel_encounter.yaml` (`species.name`: encounter probability, all sizes)
- Shared smoothers on GLORYS covariates (same set as CPS egg/CUFES pilots)
- Spatial: **on**; spatiotemporal: **off**; daily **rw0** intercept
- Barrier mesh: Bakka land polygon (`scb_pilot_land_sf.rds`); `fishai_add_barrier_mesh` fallback when `sdmTMBextra` unavailable
- Spatial-block CV: **60 km** blocks, seed **20260928**, **4** folds, sequential

## Spatial-block CV results

Scores: `artifacts/models/adult_pacific_mackerel/spatial_block_cv_scores.json`

| Metric | Value |
|--------|------:|
| Fit rows | 565 |
| Presences | 132 |
| Summed ELPD | **not eligible** (`n_failed_folds = 1`, fold 3 NA) |
| Per-fold log-lik | −57.5, −102.2, NA, −107.8 |
| OOF AUC / TSS / Boyce | **not computed** (incomplete OOF) |

**Validation verdict: model does not meet the preregistered CV gate (all four folds must converge for ELPD).**

Compared with the retired L50 ≥ 274 mm adult gate (10 presences, 3 failed folds), all-sizes data improved fold stability but **one holdout fold still failed to converge**.

## 24-hour forecast check

**Not run.** Rolling-origin 24h validation runs only after spatial-block CV passes the preregistered ELPD gate.

## Product language

Survey-based **encounter evidence** (all length classes) from fishery-independent CPS trawl and nearshore sets — not live tracking, not harvest advice, not fine-scale coordinates in any public artifact.
