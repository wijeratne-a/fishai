# Model readiness blockers (no fitting)

**As of:** 2026-09-25  
**Policy:** Readiness only. Do not refit. Do not rescore. Do not rank taxa by holdout scores.

## Hard blockers

| ID | Blocker | Applies to | Effect |
|---|---|---|---|
| B-001 | `ZERO_SEMANTICS_REQUIRED` | Pacific COUNT regions (Hawaii, American Samoa, CNMI/Guam, PRIAs) | `PRESENCE_ONLY`. Missing taxa must not become absences. Detection models blocked. |
| B-002 | Insufficient detection events (8 total) | Goliath grouper `EPI ITAJ` (Florida Keys) | `NOT_MODEL_READY`. Events: 1 in 2018, 1 in 2022, 6 in 2024. |
| B-003 | Historical SST not matched to survey dates/places | Puerto Rico accepted baselines (*S. partitus*, *S. aurofrenatum*) | Internal baseline only; not nowcast-research-ready. |
| B-004 | Year-specific species lists | All Atlantic RVC frames | Non-detection only when code is on that year’s list; pooling needs covariates. |
| B-005 | Publication / rights gates | Globe products; goliath | No species `PUBLISHED`; goliath remains `no_estimate` / `NOT_PUBLISHED`. |

## Not blockers for frame existence

Florida Keys, Puerto Rico, USVI, and Flower Garden Banks frames are **detection-capable with restrictions** (zeros present, one list per year). Capability ≠ accepted model ≠ published nowcast.

## Explicit non-actions

- No ranking by holdout Brier / AUC in this directory.
- `MODEL_INPUT_REQUIREMENTS.csv` left unchanged.
- Multi-species score CSVs left unchanged.
