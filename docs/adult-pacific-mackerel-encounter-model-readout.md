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
- **CV-fit spec (one remediation retry):** linear GLORYS effects (`temp_3m_z` … `log_depth_z`); **spatial off**; spatiotemporal **off**; daily **rw0** intercept; barrier mesh **disabled** (sardine off-off playbook + linear terms for identifiability at ~132 presences).
- Spatial-block CV: **60 km** blocks, seed **20260928**, **4** folds, sequential

### Fold 3 failure (full spatial + smoothers)

Holdout fold 3 is well posed (**221** rows, **67** presences, **154** absences). The failure was on **training** when fold 3 is held out: **344** rows, **65** presences, **279** absences — sdmTMB returned **non-positive-definite Hessian** (barrier spatial random field + six `k=3` smoothers + rw0 time effects vs sparse presences). Folds 1, 2, and 4 converged under the full spec.

## Spatial-block CV results (remediated spec)

Scores: `artifacts/models/adult_pacific_mackerel/spatial_block_cv_scores.json`

| Metric | Value |
|--------|------:|
| Fit rows | 565 |
| Presences | 132 |
| Summed ELPD | **−674.14** (`elpd_eligible`: true) |
| Per-fold log-lik | −69.6, −116.9, −325.5, −162.2 |
| OOF AUC | 0.569 |
| OOF TSS (0.5) | 0.052 |
| OOF Boyce | 0.467 |

**Validation verdict: preregistered CV gate met (all four folds converged).** Discrimination is modest (AUC ≈ 0.57).

## 24-hour forecast check

**Not run in this turn** (CV gate now passes; forecast script remains on the forecast-validation branch for CPS/mackerel wiring).

## Product language

Survey-based **encounter evidence** (all length classes) from fishery-independent CPS trawl and nearshore sets — not live tracking, not harvest advice, not fine-scale coordinates in any public artifact.
