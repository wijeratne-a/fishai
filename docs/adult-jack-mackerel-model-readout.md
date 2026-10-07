# Adult Pacific jack mackerel (*Trachurus symmetricus*) — pipeline readout

Branch: `cursor/fishai-adult-jack-mackerel`. Public NOAA CPS Life History data via GCS mirror (oceanview ERDDAP 504 during ingest).

## Adult length cutoff (final)

Adult specimens were retained only if standard length >= 250 mm (jack mackerel, Trachurus symmetricus). This cutoff is the length at 50% maturity (L50) from Fitch (1956): 50% of females mature at 250 mm fork length (100% at 350 mm). The published value is in fork length; applied to standard length it is conservative, since fork length exceeds standard length for the same fish.

Implementation: specimen normalization prefers standard length fields; when only fork length is recorded, fork length >= 250 mm is used (published L50 in fork length; no FL→SL conversion).

## Training table (pilot bbox)

| Metric | Count |
|--------|------:|
| Jack mackerel model-ready rows | **325** |
| Jack mackerel encounters (presence) | **24** |
| All-species training rows kept (GLORYS join) | 1,205 |

Config: `configs/models/adult_cps_jack_mackerel.yaml` (delta hurdle) with binomial fallback `configs/models/adult_cps_jack_mackerel_binomial.yaml`.

## Spatial-block CV (60 km blocks, seed 20260928, 4 sequential folds)

1. **Delta hurdle** (Poisson-link, spatial `[on, on]`, spatiotemporal `[off, off]`, barrier mesh, rw0): all folds **non-positive-definite Hessian** (after one `[off, off]` retry per protocol).
2. **Encounter-only binomial** fallback (same covariates/mesh): all 4 folds **non-positive-definite Hessian**.

Scores: `artifacts/models/adult_jack_mackerel/spatial_block_cv_scores.json`

| ELPD eligible | OOF AUC | OOF TSS | OOF Boyce |
|---------------|---------|---------|-----------|
| **No** | NA | NA | NA |

**Verdict:** Adult encounter model **did not validate** (sparse positives: 24 presences / 307 fit rows for *T. symmetricus*). **24 h forecast check not run** (requires validated model).

## Egg (CUFES) model

Jack mackerel egg config: `configs/models/cufes_jack_mackerel.yaml` (mirrors anchovy). **Blocked:** full CalCOFI CUFES ERDDAP sync failed (HTTP 504); no local `data/processed/calcofi_cufes/` training table in this environment. Spatial-block CV and 24 h egg forecast **not executed**.

## Data rules

Public data only; no raw coordinates or secrets committed. Maps not produced (≥10 km rule N/A for this branch).
