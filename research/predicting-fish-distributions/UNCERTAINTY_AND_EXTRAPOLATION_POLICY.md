# Uncertainty and extrapolation policy

**Scope:** How FishAI should report uncertainty and refuse predictions outside support. Research policy only. No model fitting.

Every output is a probability or index plus a statement of what it is not. A number without support and uncertainty is a claim about the ocean that the data do not justify.

## 1. What must be reported with every estimate

| Quantity | Why |
|---|---|
| Point prediction (probability, rate, or index) | The scientific target named on the model card |
| Reference value | Training prevalence, climatology, or persistence |
| Proper score versus the reference, with interval | Whether the model is better than the naive rule |
| Calibration gap | Whether the average prediction matches the observed rate |
| Support mask | Whether the query is inside training habitat, depth, visibility, season, region, and covariate range |
| Observation process | Method, effort, and season the probability belongs to |
| Issue time and valid time | Required for anything called a nowcast or forecast |

If any of these is missing, the estimate is not reportable.

## 2. Uncertainty from sampling design, not from dives

Dives at the same site or primary sample unit are not independent. Resample clusters (PSU, site, or haul). Report a 95 percent interval on the improvement over the baseline, not only on the model's Brier score.

Eleven Santa Barbara sites make that interval wide. A CI that includes zero means the model did not beat the baseline. Kelp bass Brier improvement was −0.052 (−0.129 to 0.027). That is a failure, not a noisy success.

Do not treat coefficient standard errors from a logistic fit as the uncertainty of a regional map. Spatial correlation makes those errors too small (Dormann et al. 2007).

## 3. Discrimination is not calibration

A model can rank sites well and still be wrong about how often the species is recorded.

- Florida Keys bicolor damselfish ranked 2022 dives (AUC 0.86) and over-predicted the year (0.907 versus 0.855).
- A nowcast that uses an environmental anomaly to shift the whole surface can look sharp and be biased if the year's base rate moved.

Policy: both a proper score improvement and a calibration check must pass. The Keys run used a 0.05 mean-gap limit. That is a starting rule, not a universal constant. The gap and the reliability table are always published with the decision.

## 4. Extrapolation detection

Refuse or flag a prediction when the query leaves training support.

**Hard refuse (`UNSUPPORTED`)**

- Habitat code not seen in training.
- Depth, visibility, or temperature outside the training min–max.
- Region, survey method, or season other than the model card.
- Forecast lead with no archived verification.
- Species below the detection-count floors in the validation protocol.

**Soft flag (`INSIDE_RANGE_BUT_NOVEL`)**

- Combination of in-range covariates that never occurred together (for example cool water at a habitat that was only sampled in warm years). Multivariate novelty methods exist (Mahalanobis / ExDet, Mesgaran et al. 2014; area of applicability, Meyer and Pebesma 2021). FishAI has not implemented them. Until it does, report univariate range checks and the year-to-year covariate shift.

**Maps**

A probability may be drawn only on cells that have the same habitat class, depth band, and season as training events, and only if `publication_status` is `PUBLISHED`. Empty ocean is unknown, not zero.

## 5. Covariate shift between years

The most likely extrapolation FishAI will see is a later year whose environment or base rate differs from training.

- Detect it by comparing training versus test distributions of depth, visibility, temperature, and prevalence before interpreting scores.
- Measure impact by the calibration gap and by scoring a survey-only model next to the environmental model.
- Mitigation: drop the shifted covariate if it fails locked spatial CV; do not use year dummies; do not retune on the test year.
- Mitigation fails when the only warm years in the record are also the high-detection years. That is the kelp bass case. More ocean layers will not fix a confound that lives in the year axis.

Muhling et al. (2020) show species–environment models losing skill in novel climates. Treat marine heatwaves and post-heatwave cool years as novelty, not as ordinary test years.

## 6. Model uncertainty versus ocean uncertainty

| Source | How to show it | What not to do |
|---|---|---|
| Parameter uncertainty | Cluster bootstrap or posterior draws | Quote a single Brier as exact |
| Structural uncertainty | One pre-registered estimator, or an ensemble of pre-registered models scored separately | Average three disagreeing fits and cite one |
| Ocean-product uncertainty | If HYCOM and GLORYS both exist, join both on training years and test whether the decision to keep temperature changes | Switch products between train and test without a test of the switch |
| Forecast uncertainty | Ensemble ocean forecasts, skill by lead | A single deterministic grid labelled as "the" forecast |

HYCOM GOFS 3.1 analysis ends 2024-09-04. ESPC-D-V02 starts 2024-08-10 (hycom.org data server, checked 2026-09-27). A model trained on GOFS 3.1 and applied to ESPC is a product shift. It needs its own locked test.

## 7. Presence-only and fused data

Relative intensity from GBIF or OBIS has no natural probability scale. Do not attach a percent to it. If an integrated model is ever fit, each source keeps its own observation model (Isaac et al. 2020, S69). The survey-detection probability is never overwritten by a compiler pin.

## 8. Communication

Plain language on every card:

> This number is the chance that a completed [method] in [region and season] would record [species] under conditions like the training surveys. It is not the location of an individual, not a count, and not a claim about unsurveyed water.

Unknown remains the default on the globe.
