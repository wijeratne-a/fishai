# Uncertainty propagation rules

**Status:** Rules for combining and reporting uncertainty components. Synthetic-fixture documentation only until wired to a fitted model.

## Keep components separate

1. Store every taxonomy component under its own field (`UNCERTAINTY_OUTPUT_SCHEMA.json`).
2. `collapsed_score` must be `null`. Do not invent a single confidence index for APIs or UI.
3. A predictive interval, if present, is an **additional** summary of the predictive distribution — it does not replace `aleatoric` / `epistemic_*` / support fields.

## Propagation across steps

| Step | Rule |
|---|---|
| Feature join | Carry `observation_process` and `data_coverage` from the weaker source; never drop a `UNKNOWN` by averaging with `KNOWN` |
| Model predict | Update `aleatoric` and `epistemic_parameter` from the model; leave support components to the domain mask |
| Domain mask | Map support labels into `spatial_support` / `environmental_support` / `temporal_support` qualitative levels; do not overwrite aleatoric |
| Aggregation (cells, regions) | Aggregate each component with an explicit rule (mean, max, or worst-case). Worst-case for support: any `UNSUPPORTED` child → parent support blocked |
| Time lag / forecast | Increase `temporal_support` and `epistemic_structural` severity with lead time; do not hide that in a smaller probability alone |

## Blocking rules

- If `support_label` is `UNSUPPORTED`, publication status stays non-published.
- If `observation_process.status` is `UNKNOWN` for the label frame, do not claim calibrated detection probability.
- Missing components use `status: UNKNOWN`, not zero.

## Evaluation

- Score probabilities with Brier and log loss (`evaluation/engine/metrics.py`).
- Stratify by support label (`evaluation/support/SUPPORT_METRICS.md`).
- ROC AUC remains secondary discrimination only.
- Do not report calibration slope unless implemented and tested elsewhere.
