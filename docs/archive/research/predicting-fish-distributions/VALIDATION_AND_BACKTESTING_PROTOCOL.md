# Validation and backtesting protocol

**Scope:** Research protocol only. Do not fit models, rescore locked holdouts, or publish. Source ids: `SOURCE_INDEX.csv`.

A prediction is valid only when it beats a named reference on data that did not influence any modelling decision. FishAI already has this discipline for one species. Most failures in the project, and in the wider literature, come from skipping a step.

## 1. Freeze first

Before any test-period observation is used as a label:

1. Name the question (one of the nine in `CORE_PROBLEM_DEFINITION.md`).
2. Name the survey process, species, region, season, and life stage.
3. Name training years and exactly one test year or test window.
4. Name features, estimator, missing-data rule, and baseline.
5. Write a hashed preregistration. Refuse to score if the hash does not match.
6. Write a one-time lock before loading the test labels.

Do not use the test year to pick species, keep or drop a covariate, or choose among estimators. Puerto Rico 2023 was used for all three. Those scores are untrusted.

## 2. Required baselines

Every model is scored against at least one reference that a constant or naive rule can produce.

| Question | Required reference | Optional second reference |
|---|---|---|
| Survey detection | Training prevalence | Survey-only model, if an environmental model is being tested |
| Population distribution | Spatial prevalence or intercept-only spatial field | Habitat-only model |
| Relative abundance | Mean training catch rate or design-based stratum mean | Previous year's index |
| Nowcast | Climatology of the same survey window | Persistence of the last comparable survey |
| Forecast | Climatology and persistence, by lead time | Damped anomaly persistence |
| Climate redistribution | Historical climatology; no-change range | Multi-model climate ensemble spread |

A model that loses to its reference has failed, even if AUC looks high.

## 3. Scores

Use proper scoring rules. Report them with resampling uncertainty at the cluster that matches the sampling design (primary sample unit, site, or haul).

**Required for binary detection and occurrence**

- Brier score versus the prevalence baseline.
- Log loss versus the same baseline.
- Calibration: mean predicted versus observed; reliability bins; optionally intercept and slope of a calibration logistic.
- Discrimination (AUC) as a secondary number only.

**Required for counts or rates**

- Mean squared or mean absolute error on the training scale.
- Continuous ranked probability score if a predictive distribution is produced.

**Do not use as the primary decision**

- Accuracy or "80 percent correct." For a common fish, always saying present looks strong. For a rare fish, always saying absent looks perfect.
- AUC alone. A model can rank dives well and still be miscalibrated, as in Florida Keys bicolor damselfish (AUC 0.86, mean predicted 0.907 versus observed 0.855).
- Boyce index. It is a presence-only evaluation (Hirzel et al. 2006). FishAI's Atlantic frames have real zeros. Use Brier and log loss.

Gneiting and Raftery (2007) is the standard argument for proper scores. A score is proper when the true distribution is the unique best report.

## 4. Blocking

Randomly splitting dives leaks spatial and temporal dependence.

- **Time.** Train on earlier years. Score a later year once. Interstitial years are not training data unless listed.
- **Space.** For covariate selection, leave out sites or subregions inside the training years only. Santa Barbara kelp bass passed leave-one-site-out and then failed 2022. Spatial CV is not a substitute for a later year.
- **Environment.** Report whether the test year is inside the training range of each covariate. Five Santa Barbara 2022 rows were colder than any training temperature. Scoring them is allowed only if the report says they are out of support. `predict` must refuse them.

Roberts et al. (2017) and Valavi et al. (2019) document why spatial and environmental blocking changes apparent skill. Yates et al. (2018) review transferability: models often fail when climate or habitat is novel.

## 5. Leakage checklist

Refuse a run if any item is true.

- Covariates from future calendar days relative to the survey (`t+1`, `t+2`).
- Ocean forecast fields used as if they were analyses, or analyses used as if they were forecasts.
- Test-year detection counts used to choose species or features.
- Multiple estimators reported as one number.
- Missing depth or visibility filled with a constant (for example 15).
- Year dummies in a temporal-transfer design (the test year scores as the reference year).
- Presence-only records treated as survey zeros.
- Scaling, habitat encoding, or random-field hyperparameters fit including the test year.

## 6. Backtesting nowcasts and forecasts

A nowcast or forecast cannot be tested on biennial reef surveys alone.

**Nowcast (question 7)**

1. Freeze a model whose environmental term already beat survey-only on a locked later survey year.
2. Apply it to analyzed ocean fields available at issue time, same day or past only.
3. Score against independent observations collected after the freeze, in the same survey window, with the same method or a pre-declared second method.
4. Compare to climatology of that window.

Without contemporaneous observations, a nowcast is an untested projection. FishAI does not have those observations. Analogue: EPA NowCast requires two of the last three hours (P328); biennial RVC is not a nowcast.

**Forecast (question 8)**

1. Archive ocean forecasts with issue time and valid time. Never overwrite.
2. Score predictions by lead time against later observations.
3. Report skill versus climatology and persistence at each lead.
4. Stop issuing leads where skill is not better than both references.

Weather verification practice (Jolliffe and Stephenson; Wilks) is the analogue: no skill score without a reference, no claim at a lead that was not tested.

## 7. Sample-size floors

Do not score a species if training detections are below 50 completed events or the test year has fewer than 10 usable detections after dropping missing covariates. Barred sand bass had 9 usable 2022 detections and lost to prevalence. Goliath grouper had 8 Keys detections across three years and cannot be modeled.

## 8. Reporting

Every scored run writes:

- git commit and tree state;
- input file hashes;
- train years, test year, estimator, features, offsets, missing-data policy;
- `holdout_inspected_before`;
- `publication_status` (default `NOT_PUBLISHED`);
- decision label from the preregistered rule, not from a later narrative.

If a label is wrong after scoring, recompute it from stored metrics. Do not rescore.

## 9. What this protocol does not allow

- Rescoring Puerto Rico 2023.
- Rescoring Florida Keys 2022 bicolor damselfish or Santa Barbara 2022 bass.
- Using 2024 Keys as a "new" holdout for species already tested there in the old suite without disclosing it as burned.
- Calling a spatial CV win a nowcast.
