# Temporal leakage tests

## Confirmed leak: future calendar days in SST join

`join_survey_date_sst` in `scripts/modeling/run_puerto_rico_prediction_test.py` and the OISST matcher try offsets `0, ±1, ±2` days. The `+` side is **after** the survey date.

MUR/OISST daily analyses are typically available after the valid day, so even same-day `analysed_sst` is not an operational as-of feature. Using **t+1 / t+2** is worse: it is post-event information entering a feature that is later discussed as if it could support a nowcast.

`science/time/TEMPORAL_INTEGRITY_RULES.md` already forbids post-event features on the operational lane and forbids centered windows as operational lags. The join code violates both unless every join is labeled `lane=retrospective` **and** never used to argue nowcast readiness.

## Other temporal issues

- Year dummies are fit on 2016/2019/2021. Holdout 2023 has all year dummies = 0, i.e. it is scored as **the 2016 reference year**. That is not future leakage; it is a broken temporal transfer.
- `training_mask` is `year < holdout`, not `year in TRAIN_YEARS`. An accidental extra file with year 2022 would enter training.
- SST scale `(sst - 28) / 3` is a global constant, not fit on all rows (no leakage). It is still an unvalidated unit transform.

## Required tests (added this audit)

- Future-day SST offset must be rejected.
- Holdout year must not appear as a dummy column.
- Visibility/depth must not be invented as 15.0.
