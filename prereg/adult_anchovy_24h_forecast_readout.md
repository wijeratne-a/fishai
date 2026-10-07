This checks whether the validated adult northern anchovy encounter model beats two simple baselines at 24 hours ahead on CPS trawl and nearshore survey tows. It is fishery-independent encounter evidence, not live tracking, not a map product, and not harvest advice.

The operational numbers use the same lead-damped ocean anomaly proxy as the egg forecast validation (NOT_ISSUED_FORECAST). They are not an issued WCOFS or CMEMS forecast and must not be read as one.

Adult anchovy: None of the eight rolling-origin refits passed the spatial-block CV convergence gate (non-positive-definite Hessian on every cutoff). Temporal training subsets drop spatial and temporal coverage relative to the full 402-row validated fit, so pooled 24h NOT_ISSUED_FORECAST proxy AUC/TSS versus persistence and day-of-year climatology were not computed. With zero eligible cutoffs (need at least six), the verdict is **FAIL (INSUFFICIENT)**. This is not evidence that the proxy beats climatology; it is evidence that the preregistered rolling-origin test could not be scored under the fixed convergence rule on this public rebuild.

Cutoffs locked (best-effort calendar; no DJF eligible days): 2015-06-22, 2016-09-08, 2017-03-22, 2018-09-13, 2019-08-26, 2021-04-02, 2022-09-23, 2025-06-17. Egg-protocol reference cutoffs overlapped none of these (adult CPS coverage starts after 2003; surveys are spring–fall).
