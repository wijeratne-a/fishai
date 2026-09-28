PROJECT TYPE: internal regional survey-conditioned detection (not a live global fish map)
VERSION CONTROL: git 0bf64b52efdebf4d02fd1b483947edd5ca15f6e9 DIRTY at baseline snapshot
SNAPSHOT CREATED: 2026-09-27T19:07:54Z — audit/brutal-audit/BASELINE_MANIFEST.csv (648 hashed files)
RESULTS TRUSTED BEFORE AUDIT: FIFTY_PERCENT_REVIEW treated PR 2023 survey-only skill and “join without future leakage” as Pass
RESULTS INVALIDATED: all Puerto Rico 2023 skill numbers (0.1953 / 0.194543 / 0.193133 and SPA AURO counterparts); SST as an operational/nowcast feature; FGB n=38 scores; CURRENT_STATUS as a runbook
CRITICAL DEFECTS: 3 (LEAK-001 future-day SST; LEAK-002 holdout reuse; SEM-002/ML-002 three disagreeing estimators sold as one result)
HIGH DEFECTS: 12 (vis/depth invent-15; year-dummy transfer; inferred year-list zeros; UI “Where now”; stale CURRENT_STATUS; regional-box SST overclaim; no issue time; unused seed; FGB support; training_mask year<holdout; habitat encoding mismatch; NaN-fit path)
LEAKAGE FOUND: YES — temporal (t+1/t+2 SST); holdout inspection; species selection uses holdout counts
HOLDOUT CONTAMINATION: YES — 2023 used for species pick, MUR accept/reject, then OISST
SEMANTIC ERRORS: 8 recorded in SEMANTIC_ERRORS.csv
UNIT ERRORS: 1 (SST scale (sst-28)/3 undeclared); NUM average not treated as integer (correct)
ZERO LOGIC ERRORS: universe inferred from arriving rows; 0/1 likelihood written as if absence; RLS/DATRAS must not share RVC zero constructor
MODEL LOGIC ERRORS: 7 recorded in MODEL_LOGIC_ERRORS.csv
ENVIRONMENTAL LOGIC ERRORS: future-day join; regional box not event location; no issue time; SST≠bottom; hycom_gom310D wrong domain
UI CLAIM ERRORS: “Where now”; stale status file; 50% leakage-Pass overclaim
FAILURE PATH ERRORS: silent vis/depth 15; silent future SST fill; eligibility gate not in fit path; truncated zeros would mint false 0s
REPRODUCIBILITY FAILURES: multi-species table incomplete provenance; three Briers irreconcilable; seed unused; no serialized weights
SAFE FIXES APPLIED: 8 (causal SST offsets; refuse missing vis/depth; explicit TRAIN_YEARS mask; NaN coefficient reject; UI label; STALE/UNTRUSTED banners; RESULTS_LOCKED; quarantine copies)
RESULTS DOWNGRADED: MODEL_RESULTS.csv; PUERTO_RICO_FINAL_REPORT.md; ENVIRONMENTAL_DECISION.md; FIFTY_PERCENT leakage and holdout gates
REMAINING BLOCKERS: no unused holdout year; no event-location depth temperature; no year-list checksum; eligibility gate still not wired into fit(); year dummies still in design (2023 still scores as 2016 if someone unlocks and reruns)
FINAL DECISION: UI_AND_LOGIC_REPAIRED_BUT_MODEL_RESULTS_UNTRUSTED

# Brutal scientific and logic audit — body

Assume-wrong held. Several things that were being treated as working science are not.

## What is actually true

Atlantic RVC `NUM` is a real-valued average. Collapse-then-any-positive is the right **detection** constructor **if** the year extract still contains the publisher list, including explicit zeros. Presence-only was not trained as absence. Mixed protocols were not pooled. USVI NaN fits were rejected. The globe still has no published probability layer. An off-repo snapshot restore was tested. Those survive.

## What does not survive

1. **Future-day SST.** `join_survey_date_sst` and the OISST matcher used `t+1` and `t+2`. `science/time/TEMPORAL_INTEGRITY_RULES.md` already forbids that on the operational lane. The 50% review marked “join without future leakage” as Pass. That sentence is false. Code now allows offsets `{0,-1,-2}` only. Tests fail if a positive offset returns.

2. **2023 is contaminated.** Species were chosen with holdout detection counts. MUR was judged on 2023. OISST was judged on 2023 after MUR failed. This is not an untouched year.

3. **There is no single Brier.** Unregularized 60-step vs L2 120-step vs different habitat encoding produce 0.1953 vs 0.194543 vs 0.193133 for STE PART. Citing any one as “the” result is accuracy inflation.

4. **Covariates were invented.** Missing visibility (and depth in `design()`) became 15. That is not a measurement.

5. **Holdout is scored as 2016.** Year dummies are trained on 2016/2019/2021. 2023 has all dummies = 0.

6. **The UI asked “Where now.”** That is a live-location claim. The label is now “What is known.”

7. **CURRENT_STATUS.md was a lie by 2026-09-26.** It said backup was not run and SST was not joined.

## Fixes applied (no 2023 rescore)

- Causal SST join in MUR and OISST matchers.
- `design()` / row builders refuse missing depth or visibility.
- `training_mask` uses explicit `TRAIN_YEARS`; interstitial years are not train.
- Logistic fits reject non-finite coefficients.
- OISST scorer uses top-by-count habitats (same rule as finalize), so a future unlock cannot silently compare different designs.
- `RESULTS_LOCKED` blocks overwrite of the inspected reports.
- Quarantine copies under `audit/brutal-audit/quarantine/`.
- Tests in `tests/prediction-test/test_brutal_audit_guards.py`.

## What we did not do

We did not rescore 2023. We did not retune MUR. We did not publish. We did not drop year dummies from `evaluate_species` because that would be a silent re-specification of a locked, already-invalid number. A new unused year is required before any skill sentence is allowed again.

## Phase 12 re-check

The leakage is blocked in code, not hidden. The old numbers are still in the tree, stamped UNTRUSTED. False confidence went down, not up. The same future-day join, invent-15, and “Where now” label cannot pass tests. Previous results should not be trusted.
