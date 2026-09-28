# Holdout contamination

Puerto Rico **2023 is not an unused year.** It has been the development, selection, and marketing holdout for:

1. The 16-species regional suite (`audit/multi-species/MODEL_RESULTS.csv`) — species chosen by training prevalence filters, then scored on 2023.
2. The finalize path that compared survey-only vs MUR SST on the same 2023 events (`PUERTO_RICO_FINAL_REPORT.md`).
3. The OISST robustness score, again on 2023 (`ENVIRONMENTAL_DECISION.md`), after the team already knew MUR failed on that year.

The experiment schema says `holdout_year` must not appear in `tuning_years`. Species selection, SST product choice, and “which two species passed” **used 2023 outcomes**. That is holdout-as-tuning.

## Score disagreement on the same claimed experiment

| Artifact | STE PART survey Brier | SPA AURO survey Brier |
|---|---:|---:|
| multi-species MODEL_RESULTS | 0.1953 | 0.2324 |
| PUERTO_RICO_FINAL_REPORT | 0.194543 | 0.233136 |
| OISST robustness table | 0.193133 | 0.238669 |

Three numbers, one story. Causes that are in the code:

- Multi-species `fit()`: 60 steps, **no L2**.
- Finalize `fit_l2_logistic()`: 120 steps, **L2 = 0.05**.
- OISST script: habitats = `sorted({habitat})[:6]` instead of top-by-count.

These are not rounding error. They are different models scored on a reused year.

## Verdict

2023 cannot be cited as an independent confirmation of skill. Treat every “beats prevalence on 2023” sentence as **inspected-holdout performance**, not generalization.
