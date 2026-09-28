# SoCal (SBC LTER) one-species detection model — kelp bass (calico bass) (*Paralabrax clathratus*)

**INTERNAL — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED**

DECISION: `DID_NOT_BEAT_BASELINE_ON_TEST_YEAR`

Probability that a completed SBC LTER annual fish transect (40 m x 2 m, late July/August, Santa Barbara Channel) with this visibility, giant kelp frond density on the transect, water temperature at the site's typical depth records at least one kelp bass (calico bass). Not abundance. Not ecological absence. Not a current location.

## Data

- Fish: SBC LTER Reef Kelp Forest Community Dynamics: Fish abundance, `knb-lter-sbc.17.41` (EDI; retrieved through the DataONE LTER member node because the EDI portal/PASTA now requires login). Standard `FISH` protocol only (40 m x 2 m transect, 0-2 m off the bottom); `CRYPTIC FISH` excluded.
- Kelp: giant kelp fronds on the same transect and day, `knb-lter-sbc.18.30`.
- Unit: one completed transect (site x transect x date). Detection = any COUNT > 0 over size rows; -99999 is missing (NOT_EVALUATED), never zero.
- 11 fixed sites resurveyed every year: CV and bootstrap group by site.

## Design (frozen before the test year was read)

- Train 2001-2018; test 2022 scored once (`SCORED_ONCE.lock`).
- Features: vis, kelp, temp. No year dummies, no site effects, no habitat dummies. Scaler fit on training rows. L2 logistic (Newton), convergence enforced.
- Temperature kept only if leave-one-site-out CV on training years beat survey-only on Brier and log loss: survey-only 0.23854 / 0.66999; with temperature 0.23079 / 0.65199; prevalence 0.25034 / 0.69384. Chosen: vis, kelp, temp.
- Test-year exposure disclosure: Before freezing, aggregate per-year counts (transects, transects with missing visibility, detected and zero transects for PCLA and PNEB) were printed for every year including 2022, during data exploration and the striped-bass feasibility check the task required. No model was fit to, evaluated on, or tuned against 2022, and no 2022 covariate values were examined.

## 2022 result

| Metric | Model | Prevalence baseline |
|---|---:|---:|
| Brier | 0.29604 | 0.24366 |
| Log loss | 0.79491 | 0.68045 |
| AUC | 0.5204 | 0.5 |

Brier improvement -0.05238 (95% CI -0.12877 to 0.02687, 2000 bootstrap resamples of 11 sites).
Mean predicted 0.3789 vs observed 0.6047 (gap 0.2257). Calibration fit {'intercept': 0.5484, 'slope': 0.2366}.

Preregistered checks: {'beats_prevalence_brier_ci': False, 'beats_prevalence_logloss': False, 'calibrated_mean': False}.
Training prevalence 0.5367 (380 of 708 transects); test 26 of 43 transects detected (minimum 10 met).
Test rows dropped: not evaluated 0, missing visibility 1, kelp join {'OK': 44}, missing temperature 0.

Small test set: one year of 11 sites, so the site bootstrap is coarse and a single year cannot separate model skill from that year's conditions.

Not published. Not on the globe. Survey non-detection is not ecological absence.
