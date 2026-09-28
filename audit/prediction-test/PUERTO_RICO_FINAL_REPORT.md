> **BRUTAL AUDIT 2026-09-27 — UNTRUSTED_AS_GENERALIZATION.**
> 2023 is an inspected holdout. Survey-only Brier disagrees with `audit/multi-species/MODEL_RESULTS.csv` (0.1953 / 0.2324) and with the OISST robustness table (0.193133 / 0.238669) because those are different estimators. SST join allowed future calendar days. Depth/visibility were imputed to 15 when missing. Year dummies score 2023 as the 2016 reference year. Do not cite these numbers as independent skill. Original copy: `audit/brutal-audit/quarantine/PUERTO_RICO_FINAL_REPORT.md`.

FINAL STATUS:
SPECIES: STE PART (Stegastes partitus); SPA AURO (Sparisoma aurofrenatum)
TRAIN YEARS: 2016, 2019, 2021
HOLDOUT YEAR: 2023
SURVEY-ONLY HOLDOUT BRIER: STE PART 0.194543; SPA AURO 0.233136
SST MODEL HOLDOUT BRIER: STE PART 0.194778; SPA AURO 0.233344
MODEL RETAINED: STE PART survey_only; SPA AURO survey_only
SST MISSING FRACTION: 0.000000
BEATS PREVALENCE: STE PART YES; SPA AURO YES
PUBLICATION: NOT_PUBLISHED
ON THE GLOBE: NO
COORDINATES IN REPORT: NO
BLOCKERS: NONE

Label: INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.

# Puerto Rico internal prediction finalize — report

**INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.**

Survey-only L2 logistic versus constant training prevalence, plus optional survey-date MUR `analysed_sst` (`jplMURSST41`) joined via a coarse Puerto Rico regional box cached under `data/restricted/`. Train years 2016/2019/2021 only; 2023 scored once per model. SST retained only if holdout Brier and log loss are ≤ survey-only and mean predicted probability is within 0.15 of holdout prevalence.

SST join: missing_fraction=0.0; distinct_dates=174; cache=data/restricted/environmental/jplMURSST41/by-date.

| Species | Survey Brier | SST Brier | Retained | Beats prevalence | SST skip |
|---|---:|---:|---|---|---|
| STE PART | 0.194543 | 0.194778 | survey_only | yes | sst_did_not_earn_a_place |
| SPA AURO | 0.233136 | 0.233344 | survey_only | yes | sst_did_not_earn_a_place |

SST did not earn a place for at least one species under the acceptance rule; survey-only model retained where SST was not accepted.

**INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.**
