# CUFES 72 h egg-encounter holdout: result

The rolling-origin design in `cufes_forecast_temporal_holdout_design.md` was run as approved. Numbers below match `cufes_forecast_temporal_holdout_scores.json`. The sentences for a non-scientist are in `cufes_forecast_temporal_holdout_readout.md`.

This is egg encounter in the water. It is not adult location, not a track, and not harvest advice. No issued ocean forecast overlaps the egg record, so the operational arm is the pre-declared damped-anomaly proxy (`tau` = 3 days). Every operational block is `operational_claim = NOT_ISSUED_FORECAST` and `physics_source = damped_anomaly_proxy`. That proxy is not WCOFS and not an issued forecast.

## Cutoffs

One shared calendar, eight dates, two per meteorological season. The approved separation repair moved the early MAM cutoff from 1998-03-01 to 1998-04-07.

| Cutoff | Season |
| --- | --- |
| 1998-02-26 | DJF |
| 1998-04-07 | MAM |
| 1998-06-13 | JJA |
| 2012-09-03 | SON |
| 2017-08-05 | JJA |
| 2018-09-20 | SON |
| 2021-01-22 | DJF |
| 2022-04-12 | MAM |

Each date was a full refit on rows through that day. The daily intercept for days after the cutoff was projected with `extra_time` (the three lead days, plus any missing integers from the last training index through day +3). It was not refit on the held-out days. Oracle covariates are the analysed GLORYS values already on those rows. Persistence and the proxy use the cutoff-day surveyed track, not a full-domain grid.

## Pass rule

At 24 hours the NOT_ISSUED_FORECAST proxy must beat both persistence and climatology on AUC and on TSS, strictly, on the pooled common-support tows, with at least 6 of 8 cutoffs eligible. Ties fail. Fewer than 6 eligible cutoffs is `INSUFFICIENT`, not a pass.

## Sardine

7 of 8 cutoffs were eligible. 2022-04-12 was ineligible (non-positive-definite Hessian) and was not scored.

The 24-hour comparison has 120 common-support tows and **1** tow with eggs. The NOT_ISSUED_FORECAST proxy does not beat both baselines.

| 24 h | AUC | TSS | ELPD (delta, except climatology) |
| --- | ---: | ---: | ---: |
| NOT_ISSUED_FORECAST proxy | 0.824 | -0.008 | -19.575 |
| Persistence | 0.597 | 0.000 | -16.194 |
| Climatology | 0.983 | 0.891 | -24.970 (Bernoulli only; not ranked against delta ELPD) |
| Oracle (analysed GLORYS, not the product) | 0.807 | -0.034 | -24.172 |

The proxy AUC is above persistence and below climatology. The proxy TSS is below both. The oracle ceiling also loses to climatology on AUC and TSS. Giving the model the analysed ocean state does not create a 24-hour win on this holdout.

At 48 hours there are 103 tows and 1 with eggs. Proxy AUC is 1.000 (change +0.176 from 24 hours) and TSS is 0.980 (change +0.989). At 72 hours there are 74 tows and 4 with eggs. Proxy AUC is 0.779 (change -0.045) and TSS is -0.086 (change -0.077). Those lead-time differences are not a pass. The pass rule is the 24-hour comparison, and 48-hour AUC of 1.0 is one egg tow.

## Anchovy

4 of 8 cutoffs were eligible. 2012-09-03, 2017-08-05, 2018-09-20, and 2022-04-12 were ineligible (non-positive-definite Hessian). Four usable fits are below the required six, so the species is `INSUFFICIENT`. No pass is claimed.

On the four usable fits, the 24-hour common-support pool has 81 tows and 6 with eggs. The NOT_ISSUED_FORECAST proxy AUC is 0.962, persistence 0.991, climatology 0.989. TSS is 0 for the proxy, persistence, and climatology at the pre-declared 0.5 threshold. At 72 hours those four fits have 48 tows and 0 with eggs, so AUC and TSS are not available. That is not a 72-hour win.

## Result

Neither species meets the approved 24-hour rule. The 72-hour egg-encounter forecast, including the NOT_ISSUED_FORECAST proxy that stands in for an issued ocean forecast, does not beat persistence and climatology.
