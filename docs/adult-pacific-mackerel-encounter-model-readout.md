# Adult Pacific mackerel encounter model readout

Branch: `cursor/fishai-adult-pacific-mackerel`  
Species: *Scomber japonicus* (Pacific mackerel)

## Maturity cutoff (L50)

Adult specimens were retained only if standard length ≥ 274 mm (Pacific mackerel, *Scomber japonicus*). This cutoff is the length at 50% maturity (L50 = 274 mm fork length) from the 2023 Pacific mackerel benchmark stock assessment life-history report (histological staging, n = 911 females, SWFSC trawl surveys 2010–2021). The published value is in fork length; applied to standard length it is conservative.

## Phase 1 — viability gate (exact counts)

Non–presence-only presences in pilot bbox (before L50 gate):

| Source | Species catch rows | Presence-only excluded | Non–presence-only presences |
|--------|-------------------:|-----------------------:|----------------------------:|
| Trawl | 122 | 0 | **122** |
| Nearshore | 94 | 0 | **94** |
| **Total** | | | **216** |

Verdict: **viable — proceed** (≥150).

## Training table (after L50 ≥ 274 mm + implied-zero rules)

| Stage | Count |
|-------|------:|
| Observation rows (mackerel-only pilot species) | 572 |
| Adult presence rows (trawl + nearshore) | 11 (6 trawl + 5 nearshore) |
| Physics events (pilot bbox) | 570 |
| Training rows after GLORYS QC (kept) | 443 |
| **Adult presences in modeling frame** | **10** |
| Absences (implied-zero + catch zero) | 433 |

Ingest: NOAA public GCS mirror (ERDDAP 504 on pilot-bbox haul subsets). GLORYS join: Copernicus env credentials present at build time.

## Model spec (encounter-only; no hurdle)

Per species redirect: **sdmTMB binomial** encounter GLMM with `log(effort_duration_min)` offset — **not** delta-gamma / Poisson-link hurdle (juvenile-dominated catch at L50).

- Config: `configs/models/adult_pacific_mackerel_encounter.yaml`
- Shared smoothers on GLORYS covariates (same set as adult CPS egg/CUFES pilots)
- Spatial: **on**; spatiotemporal: **off**; daily **rw0** intercept
- Barrier mesh: Bakka land polygon (`scb_pilot_land_sf.rds`); `fishai_add_barrier_mesh` fallback when `sdmTMBextra` unavailable
- Spatial-block CV: **60 km** blocks, seed **20260928**, **4** folds, sequential

## Spatial-block CV results

Scores: `artifacts/models/adult_pacific_mackerel/spatial_block_cv_scores.json`

| Metric | Value |
|--------|------:|
| Fit rows | 443 |
| Presences | 10 |
| Summed ELPD | **not eligible** (`n_failed_folds = 3`) |
| Fold log-lik | NA, −11.0, NA, NA |
| OOF AUC / TSS / Boyce | **not computed** (incomplete OOF) |

Fold failures: holdout folds without both zeros and positives (sparse adults); fold 3 non-PD Hessian.

**Validation verdict: model does not meet the preregistered CV gate (all four folds must converge for ELPD).**

## 24-hour forecast check

**Not run.** Operational 24h rolling-origin validation applies only after a model passes spatial-block CV; with 10 adult presences and failed folds, forecast skill testing would not be interpretable.

## Product language

Survey-based adult **encounter evidence** from fishery-independent CPS trawl and nearshore sets — not live tracking, not harvest advice, not fine-scale coordinates in any public artifact.
