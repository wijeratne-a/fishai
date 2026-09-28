# Calibration audit

The only calibration check that gates a result is `calibration_gap_ok` in the Puerto Rico finalize path: mean predicted probability versus empirical prevalence, max gap 0.15. That is a **mean-bias** check, not reliability.

Missing:

- No reliability diagram.
- No bin-wise ECE.
- No holdout-year-specific calibration (year dummies make 2023 a different intercept).
- Probability clip at 1e-6 / 1-1e-6 is not calibration.
- Multi-species `fit()` has **no** calibration gate.

A model can beat prevalence Brier and still be unusable as a reported probability. Brier improvement of ~0.006 on STE PART (0.2006 prevalence vs 0.1945 model) is smaller than any uncertainty we computed — we computed none.

**Verdict:** calibration is unchecked for the 16-species table. For the two locked species it is only a mean gap. Do not describe outputs as well-calibrated probabilities.
