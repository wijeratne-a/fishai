# Pooling restrictions (Atlantic protocol year pairs)

Source matrix: `audit/multi-species/ATLANTIC_PROTOCOL_MATRIX.csv` (read-only). This note adds year-pair classes only.

## Rules

1. **Do not pool years as if the searchable species universe is identical.** Species-list size changes by year. A code is a survey non-detection only in years that include it on the frame.
2. **List-size changes are not biological trend evidence.** Classify year pairs as `COMPARABLE_WITH_COVARIATES` (or `INSUFFICIENT_DOCUMENTATION` where the 2024 single-stage accession narrative is involved). Require an explicit list-membership / frame covariate or year-specific universe before pooling.
3. **2024 Florida single-stage narrative.** Prior accession text described a single-stage design while column structure still matches earlier extracts. That is `INSUFFICIENT_DOCUMENTATION` for claiming protocol identity — not proof that biology changed, and not a free pass to pool without covariates.
4. **Puerto Rico 2014.** Absent from the ERDDAP year list. There is no 2014 file and no 2014–2016 pair. Do not invent compatibility with a missing year.
5. **Cross-region pooling.** Not authorized by the matrix. Regions stay separate even when column names match.
6. **NUM semantics.** NUM is a real-valued average, not an integer count. Detection = any length-bin row with NUM > 0. Do not treat fractional NUM as integer abundance when pooling.
7. **Holdout years.** Latest year per region remains holdout-only for the existing baseline design; pooling restrictions still apply inside training years.

## Quick reference

| Region | Downloaded years | Absent notable years |
|---|---|---|
| Florida Keys | 2014, 2016, 2018, 2022, 2024 | 2020 (not in ERDDAP list) |
| Puerto Rico | 2016, 2019, 2021, 2023 | **2014** (not in ERDDAP list) |
| USVI | 2017, 2019, 2021, 2023 | 2013, 2015 |
| Flower Garden Banks | 2018, 2022, 2023, 2024 | 2013, 2015 |

See `YEAR_COMPATIBILITY.csv` and `PROTOCOL_CHANGE_EVENTS.csv`.
