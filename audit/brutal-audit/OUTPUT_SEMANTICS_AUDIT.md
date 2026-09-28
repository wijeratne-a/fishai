# Output semantics audit

| Output | Claimed meaning | Actual meaning |
|---|---|---|
| y=1 | detection on completed event | any length-bin NUM>0 for a list species |
| y=0 | survey non-detection | code in inferred year universe and no positive NUM |
| p | P(detection \| survey, habitat, depth, vis[, sst, year]) | logistic of those covariates; year omitted at 2023 |
| Brier | skill vs prevalence | inspected-holdout score; estimator-dependent |
| SST_ADDS_NO_VALUE | environment does not help | regional-box surface SST with future-day fallback does not beat survey-only on reused 2023 |
| PUBLISHED | public nowcast | globe gate exists; no published detection layer |
| Where now | current location | historical atlas sentence |

No output is a live location. No output is ecological absence. No output is a forecast.
