# Preprocessing leakage tests

| Operation | Fitted on | Leak? |
|---|---|---|
| SST scale (sst-28)/3 | constant | no |
| Habitat dummies | training counts (finalize) | no for finalize |
| Habitat dummies | `sorted(set)[:6]` (OISST scorer) | not holdout leak; **different feature set** than locked survey model |
| Visibility impute 15 | constant | not leak; **fabrication** |
| Depth impute 15 | constant | fabrication |
| Species selection | train prevalence **and** holdout detection count ≥ 8 | **yes** — holdout support used to choose who is scored |
| SST product choice | 2023 MUR then 2023 OISST | **yes** — sequential peek |
| Normalization of features | none beyond fixed scales | no |

`rank_and_fit` requires `hold_d < 8` skip. That uses the holdout year to decide which species appear in MODEL_RESULTS. Species that would have failed on 2023 never enter the table. The two “passed” species were selected with knowledge of 2023 detection counts.

That is selection leakage. The 16-row table is not a pre-registered species list scored blindly.
