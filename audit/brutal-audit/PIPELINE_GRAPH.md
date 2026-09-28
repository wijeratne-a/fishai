# Pipeline graph

```mermaid
flowchart TD
  raw[data/raw biological gitignored]
  val[validate_atlantic_frames / gate_model_eligible]
  events[event collapse NUM any-positive]
  env[MUR / OISST regional-box join]
  fit1[fit_regional_detection_models]
  fit2[run_puerto_rico_prediction_test]
  fit3[score_new_environmental_variable]
  reports[audit reports]
  globe[globe prototype historical atlas]
  raw --> val --> events
  events --> fit1 --> reports
  events --> env --> fit2 --> reports
  env --> fit3 --> reports
  globe -.->|must not consume unpublished scores| reports
```

Gates that are **not** wired into the live fit path: `gate_model_eligible.py` is a CLI/test only. `fit_regional_detection_models.py` does not call it.

Environmental join is a **regional daily mean**, not an event-location extract. All dives on a calendar date share one SST number.
