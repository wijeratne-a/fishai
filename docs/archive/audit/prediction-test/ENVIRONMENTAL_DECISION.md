> **BRUTAL AUDIT 2026-09-27 — UNTRUSTED_AS_LOCKED_SCORE.**
> This table is not the locked finalize estimator (habitats were `sorted(set)[:6]`, not top-by-count). 2023 was already used for MUR. OISST join allowed future days. `SST_ADDS_NO_VALUE` remains the conservative product decision; it is not a proof that environment is useless. Original copy: `audit/brutal-audit/quarantine/ENVIRONMENTAL_DECISION.md`.

ENVIRONMENTAL DECISION:
DECISION: SST_ADDS_NO_VALUE
MUR RESCORED: NO
SCORED NEW VARIABLE: YES
VARIABLE: ncdcOisst21Agg_LonPM180.sst (robustness only)
FROZEN ON: 2016, 2019, 2021
HOLDOUT SCORED ONCE: 2023
DEPTH TEMPERATURE: dataset_id=hycom_gom310D; not joined; SST was not used as bottom temperature.
PUBLICATION: NOT_PUBLISHED
ON THE GLOBE: NO
NOWCAST MILESTONE: CLOSED
NOWCAST STATUS: NEEDS_MORE_ENVIRONMENTAL_COVERAGE

# Environmental decision

**INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.**

Decision: `SST_ADDS_NO_VALUE`. MUR SST was not rescored. OISST was eligible only after the join rule was frozen on 2016–2021.

| Species | Survey Brier | OISST Brier | Survey log loss | OISST log loss | Calibration gap | Accepted |
|---|---:|---:|---:|---:|---:|---|
| STE PART | 0.193133 | 0.193441 | 0.571291 | 0.571894 | 0.018727 | no |
| SPA AURO | 0.238669 | 0.238745 | 0.670624 | 0.670747 | 0.077729 | no |

Locked Puerto Rico survey-only scores remain in `PUERTO_RICO_FINAL_REPORT.md` and were not replaced. The table above is the OISST robustness comparison only.

No public globe layer was written.

