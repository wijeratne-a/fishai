# Missing provenance for existing multi-species results

**Sources read (only):** `audit/multi-species/MODEL_RESULTS.csv`, `audit/multi-species/EXECUTION_REPORT.md`  
**Action:** Document gaps. Do **not** rerun models. Do **not** change scores.

## What is recorded

- Sixteen species × region rows with Brier / log-loss / AUC fields and pass/fail `status`.
- Narrative: 17 Atlantic frames validated; holdout scored once; training years = compatible years before holdout; OBIS not used for training; USVI logistic scores non-numeric and rejected; final decision `MORE_ENVIRONMENTAL_COVERAGE_REQUIRED`.
- Commands named in the execution report (validators / fit script / watch script).

## Missing items (all sixteen fits)

| Provenance field | Status in existing artifacts | Notes |
|---|---|---|
| Git commit of the fit | **MISSING** | Neither CSV nor execution report records the commit SHA that produced MODEL_RESULTS. |
| Random seed | **MISSING** | No seed documented for folds, logistic init, or any stochastic step. |
| Environment lock | **MISSING** | No `requirements.lock`, `conda-lock`, or pinned Python/package hash tied to the run. |
| Artifact hash | **MISSING** | No SHA-256 (or equivalent) of model binaries, prediction tables, or the results CSV at write time. |

## Partial narrative only (not a substitute)

EXECUTION_REPORT states process facts (holdout once, no env models, Pacific positive-only) but does not pin code or environment. Those facts do not replace commit / seed / lock / hash.

## Minimum run manifest

See `reproducibility/MINIMUM_RUN_MANIFEST.json` for the required fields on any future recorded run. Existing results remain `provenance_status=INCOMPLETE` in `EXISTING_RESULTS.csv`.
