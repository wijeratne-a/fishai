This checks whether the validated adult Pacific sardine encounter model beats two simple baselines at 24 hours ahead on CPS trawl and nearshore survey tows. It is fishery-independent encounter evidence, not live tracking, not a map product, and not harvest advice.

All eight rolling-origin refits converged (no non-positive-definite Hessian). Cutoffs: 2014-04-25 (MAM, 150 train / 5 holdout), 2015-06-20 (JJA, 158/8), 2016-09-08 (SON, 174/9), 2018-09-20 (SON, 243/6), 2021-03-26 (MAM, 286/8), 2022-09-23 (SON, 346/4), 2024-07-29 (JJA, 404/6), 2026-06-25 (JJA, 448/8). DJF had no eligible day. This is not an INSUFFICIENT convergence result.

Issued WCOFS fields are coarsened onto the GLORYS grid with no bias-correction map. Of 58 holdout rows, 15 are on or after 2024-07-01 and all 15 used an issued forecast from the cutoff-day cycle: 6 ROMS `fields` files for 2024-07-29 (`f024`/`f048`/`f072`) and 9 `regulargrid` files for 2026-06-25. The other 43 rows are before the public archive and use the lead-damped anomaly proxy (NOT_ISSUED_FORECAST).

The 24 h comparison is thin. Only 5 events are on common support, and only 1 is a presence. Two of those five used issued WCOFS covariates; three used the pre-archive proxy.

Adult sardine at 24 hours: operational AUC 1.000 and TSS 0.000 do not beat both baselines (persistence AUC 0.500, TSS 0.000; climatology AUC 1.000, TSS 0.000) on those 5 events. AUC ties climatology and TSS ties both baselines, so the pre-registered strict rule fails. FAIL.

Retrospective oracle ceiling at 24 h (analysed GLORYS, not the product): AUC 1.000, TSS 0.000. 48 h had 6 common-support events and 0 presences, so AUC/TSS were not scored. 72 h had no common-support pool.
