# Baseline results

**INTERNAL FEASIBILITY MODEL — NOT PUBLISHED**

Species: *Chaetodon capistratus* (`CHA CAPI`).  
Events with depth and visibility: 2,113. Detections: 1,026.  
Script: `scripts/modeling/fit_internal_baseline.py`.

Predictors were survey fields only: depth, underwater visibility, year, and habitat code. No sea-surface temperature was joined. No coordinates entered the model.

## Spatial-block cross-validation

Five subregion blocks. Pooled scores:

| Model | Brier | Log loss |
|---|---:|---:|
| Training-fold prevalence | 0.2621 | 0.7176 |
| Logistic regression | 0.2446 | 0.6822 |

The logistic model was better than prevalence on every block. The gain is small. This is not a nowcast.

## Leave-one-year-out

| Held year | Events | Positives | Model Brier | Prevalence Brier | Model AUC |
|---|---:|---:|---:|---:|---:|
| 2018 | 843 | 438 | 0.2408 | 0.2528 | 0.715 |
| 2022 | 648 | 237 | 0.2506 | 0.2618 | 0.724 |
| 2024 | 622 | 351 | 0.2389 | 0.2583 | 0.832 |

The 2024 accession page describes a single-stage design. That year is not a confirmed protocol match for 2018 and 2022. AUC is secondary. The model was not tuned to maximize it.

No reliability curve was written, because the fit is an internal screen. Calibration intercept and slope were not claimed.

The globe was not changed. The goliath card remains `NOT_PUBLISHED`.
