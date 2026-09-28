# Baseline comparison audit

The only baseline is **constant training prevalence**. That is the correct null for a probability. It is not a habitat-stratified null, not a last-year persistence null, and not a spatial-smoothed null.

On the finalize path, STE PART holdout Brier 0.194543 vs prevalence 0.2006-class (report says beats prevalence). The delta is about 0.006. No bootstrap, no standard error, no paired test. A 0.006 Brier move on 248 events can be noise.

OISST vs survey deltas are ~0.0003. Those are smaller than any rounding story and were used to say “SST adds no value.” Directionally they are “not better.” They are not a precise measurement of environmental worth, because SST is a regional box with future-day fallback.

Did any accepted model beat the correct simple baseline? **Numerically, on an inspected holdout, two Puerto Rico species beat prevalence.** That is not independent confirmation. FGB and Florida Keys mostly did not. USVI did not produce numbers.

No model decision should have been made by comparing 0.194543 vs 0.1953 vs 0.193133 as if they were the same experiment.
