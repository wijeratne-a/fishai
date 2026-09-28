TEST STATUS: PASSED (both species beat prevalence on spatial blocks and untouched 2023 holdout)
SPECIES: STE PART (Stegastes partitus); SPA AURO (Sparisoma aurofrenatum)
TRAIN YEARS: 2016, 2019, 2021
HOLDOUT YEAR: 2023
HOLDOUT BRIER MODEL: STE PART 0.194543; SPA AURO 0.233136
HOLDOUT BRIER BASELINE: STE PART 0.204564; SPA AURO 0.248376
BEATS BASELINE: YES (both)
PUBLICATION: NOT_PUBLISHED
COORDINATES IN REPORT: NO
NEXT ACTION: Join historical analysed SST to Puerto Rico survey dates in protected storage; re-score only these two species on the same 2023 holdout once. Keep off the globe.

# Puerto Rico internal prediction test — report

**INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.**

Survey-only L2 logistic versus constant training prevalence. Predictors: depth, underwater visibility, year, habitat code. No SST. No OBIS. Spatial leave-one-subregion-out on training years only; 2023 scored once and not used for tuning. Other regional species were not refit. Outputs: `RESULTS.json`, `RUN_MANIFEST.json`. Manifest records gzip sha256, seed `20260926`, zero rule, commit `0bf64b52efdebf4d02fd1b483947edd5ca15f6e9`, `DIRTY_TREE`.

| Species | Spatial Brier model | Spatial Brier baseline | Holdout Brier model | Holdout Brier baseline | Beats baseline |
|---|---:|---:|---:|---:|---|
| STE PART | 0.190713 | 0.200782 | 0.194543 | 0.204564 | yes |
| SPA AURO | 0.205438 | 0.216314 | 0.233136 | 0.248376 | yes |

**INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.**

Unittest: `python3 -m unittest tests.prediction-test.test_puerto_rico_prediction_rules -v` → 3 ok.
