# Florida Keys one-species detection model — bicolor damselfish (*Stegastes partitus*)

**INTERNAL — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED**

DECISION: `BEATS_BASELINE_BUT_MISCALIBRATED_ON_TEST_YEAR`

Probability that a completed Reef Visual Census point count with this habitat, depth, visibility records at least one bicolor damselfish. Not abundance. Not ecological absence. Not a current location.

## Design (frozen before the test year was read)

- Train 2014, 2016, 2018; test 2022 scored once (`SCORED_ONCE.lock`).
- Features: habitat, depth, vis. No year dummies. Scaler fit on training rows.
- L2 logistic (Newton), convergence enforced.
- Temperature kept only if spatial CV on training years beat survey-only: survey-only Brier 0.08115 / log loss 0.26426; with temperature 0.08145 / 0.26524; prevalence 0.10469.

## 2022 result

| Metric | Model | Prevalence baseline |
|---|---:|---:|
| Brier | 0.09537 | 0.12475 |
| Log loss | 0.31880 | 0.41736 |
| AUC | 0.8574 | 0.5 |

Brier improvement 0.02938 (95% CI 0.02104 to 0.03886, 2000 bootstrap resamples of survey sites).
Mean predicted 0.9075 vs observed 0.8549 (gap 0.0526). Calibration fit {'intercept': -0.5897, 'slope': 0.9655}.

Preregistered checks: {'beats_prevalence_brier_ci': True, 'beats_prevalence_logloss': True, 'calibrated_mean': False}.
Training prevalence 0.8820; the model ranks dives well but its overall level follows the training years, so a year with fewer detections is over-predicted.

Events: train 2500, test 648. Test rows dropped for missing temperature: 0.

Not published. Not on the globe. Survey non-detection is not ecological absence.
