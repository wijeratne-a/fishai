# SoCal (SBC LTER) one-species detection model — barred sand bass (*Paralabrax nebulifer*)

**INTERNAL — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED**

> **SUBSTITUTION — USER MUST CONFIRM: the request said 'striped bass'. True striped bass (Morone saxatilis) is not on the SBC LTER fish list, so it cannot be modeled here. Barred sand bass is the likely intended fish; this model says nothing about Morone saxatilis.**

DECISION: `DID_NOT_BEAT_BASELINE_ON_TEST_YEAR`

Probability that a completed SBC LTER annual fish transect (40 m x 2 m, late July/August, Santa Barbara Channel) with this visibility, giant kelp frond density on the transect records at least one barred sand bass. Not abundance. Not ecological absence. Not a current location.

## Data

- Fish: SBC LTER Reef Kelp Forest Community Dynamics: Fish abundance, `knb-lter-sbc.17.41` (EDI; retrieved through the DataONE LTER member node because the EDI portal/PASTA now requires login). Standard `FISH` protocol only (40 m x 2 m transect, 0-2 m off the bottom); `CRYPTIC FISH` excluded.
- Kelp: giant kelp fronds on the same transect and day, `knb-lter-sbc.18.30`.
- Unit: one completed transect (site x transect x date). Detection = any COUNT > 0 over size rows; -99999 is missing (NOT_EVALUATED), never zero.
- 11 fixed sites resurveyed every year: CV and bootstrap group by site.

## Design (frozen before the test year was read)

- Train 2001-2018; test 2022 scored once (`SCORED_ONCE.lock`).
- Features: vis, kelp. No year dummies, no site effects, no habitat dummies. Scaler fit on training rows. L2 logistic (Newton), convergence enforced.
- Temperature kept only if leave-one-site-out CV on training years beat survey-only on Brier and log loss: survey-only 0.09910 / 0.42064; with temperature 0.09987 / 0.41726; prevalence 0.09547 / 0.37125. Chosen: vis, kelp.
- Test-year exposure disclosure: Before freezing, aggregate per-year counts (transects, transects with missing visibility, detected and zero transects for PCLA and PNEB) were printed for every year including 2022, during data exploration and the striped-bass feasibility check the task required. No model was fit to, evaluated on, or tuned against 2022, and no 2022 covariate values were examined.

## 2022 result

| Metric | Model | Prevalence baseline |
|---|---:|---:|
| Brier | 0.17866 | 0.17769 |
| Log loss | 0.57399 | 0.56663 |
| AUC | 0.3758 | 0.5 |

Brier improvement -0.00097 (95% CI -0.00485 to 0.00374, 2000 bootstrap resamples of 11 sites).
Mean predicted 0.1070 vs observed 0.2093 (gap 0.1023). Calibration fit {'intercept': -11.8224, 'slope': -4.8747}.

Preregistered checks: {'beats_prevalence_brier_ci': False, 'beats_prevalence_logloss': False, 'calibrated_mean': False}.
Training prevalence 0.0989 (70 of 708 transects); test 9 of 43 transects detected (minimum 10 NOT met).
Test rows dropped: not evaluated 0, missing visibility 1, kelp join {'OK': 44}, missing temperature 0.

Small test set: one year of 11 sites, so the site bootstrap is coarse and a single year cannot separate model skill from that year's conditions.

Not published. Not on the globe. Survey non-detection is not ecological absence.
