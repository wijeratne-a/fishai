# Support metrics

How to score models once each point has a support label from `mask.label_support_point`.

## Primary (probability quality)

- **Brier score** — mean squared error of predicted probabilities vs binary outcomes.
- **Log loss** — mean Bernoulli negative log-likelihood with probability clipping.

These are the primary comparison metrics for detection-style Bernoulli targets. Implement and test them in `evaluation/engine/metrics.py`.

## Secondary

- **ROC AUC** — discrimination only. Report when both classes exist in a slice; never treat as sufficient alone.
- Do **not** claim calibration slope, ECE, or reliability diagrams unless those functions are implemented and unit-tested.

## Required slices

For any holdout or block evaluation, report Brier and log loss for:

1. All points with a defined label
2. `SUPPORTED` only
3. `WEAK_SUPPORT` only
4. Each extrapolation label present in the slice
5. `UNSUPPORTED` count (and metrics only if n > 0 and both classes exist where needed)

## Skill vs prevalence

When comparing to a global prevalence baseline, compute skill on the **same support slice**. A model that looks good only by scoring `UNSUPPORTED` points is not accepted.

## Honesty constraints

- Support rate (`SUPPORTED` / n) is a coverage statistic, not model skill.
- Do not collapse support + uncertainty + probability into one “confidence” number.
- Synthetic fixtures are valid for unit tests; real survey fits are out of scope for this package’s tests.
