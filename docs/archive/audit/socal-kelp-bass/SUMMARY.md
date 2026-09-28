# SoCal kelp-forest bass detection test (SBC LTER) — summary

**INTERNAL — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.** Not on the globe. No coordinates in any output.

Same end-to-end discipline as `audit/florida-keys-one-species/`: freeze, then preregistration plus sha256, then a rehearsal on a training year, then score once with `SCORED_ONCE.lock`. Code: `scripts/modeling/socal_kelp_bass.py`. It imports the Florida Keys estimator, metrics, CV, bootstrap and decision rule; the Keys file is unchanged.

## Data

| Item | Value |
|---|---|
| Fish | SBC LTER Reef: Kelp Forest Community Dynamics: Fish abundance, `knb-lter-sbc.17.41`, doi:10.6073/pasta/73cb2666f95f7a4a4c2e3744f1bb5e0e, CC BY 4.0 |
| Kelp | Abundance and size of giant kelp, `knb-lter-sbc.18.30`, doi:10.6073/pasta/c05388280c63f9effa0c71bf5908be1e |
| Access | 2026-09-27 through the DataONE LTER member node. The EDI portal and PASTA API returned a login or 403 for public access, and no account was created. SHA-1 matches DataONE system metadata. |
| Manifests | `data/manifests/socal-sbc-source-manifest.csv`, `data/manifests/socal-environment-manifest.csv`, 2 rows added to `structured-program-manifest.csv` |
| Temperature | HYCOM water_temp, one experiment per year. 2001-2015 use expt_53.X; 2016 expt_57.2; 2017 expt_57.7; 2018 GLBv expt_93.0; 2022 GLBy expt_93.0/ts3z. All 166 dates were acquired; 7 used a past-day fallback and none used a future day. |

**Survey unit:** one completed standard `FISH` transect, identified by site, transect and date. Each transect is 40 m x 2 m (80 m2), 0-2 m off the bottom, surveyed once a year in late July or August. The `CRYPTIC FISH` benthic protocol is excluded.

**Detection:** any size row with COUNT > 0. A transect counts as zero only if it has explicit rows for the species and every COUNT is 0. A value of -99999, or no rows at all, is NOT_EVALUATED and is never treated as zero.

**Checks run:** EML units (COUNT = number, SIZE = cm), a zero-row coverage threshold of 99% or more, a zero COUNT carrying a size is refused, and an AREA other than 80 m2 is refused.

**Train/test years:** train 2001-2018, test 2022. 2000 was dropped because only 3 sites were surveyed and the survey was in October. 2022 has full coverage (44 transects) and is inside HYCOM coverage. The three-year gap after training avoids scoring fixed transects in the year right after training.

## Striped bass feasibility (`FEASIBILITY.json`)

*Morone saxatilis* is not on the SBC species list in any year (0 detections in 2000-2025). Verdict: **INSUFFICIENT_DETECTIONS**, so it was not modeled.

Barred sand bass (*Paralabrax nebulifer*) was run in its place. **This substitution must be confirmed by the user.**

## Results (2022, scored once)

| | Kelp bass (*P. clathratus*) | Barred sand bass (*P. nebulifer*) — substitution |
|---|---|---|
| Training rows (detected) | 708 (380) | 708 (70) |
| Temperature kept? (leave-one-site-out CV, Brier / log loss) | yes: 0.2308 / 0.6520 with temperature vs 0.2385 / 0.6700 survey-only (prevalence 0.2503 / 0.6938) | no: Brier 0.0999 with temperature vs 0.0991 without (log loss 0.4173 vs 0.4206). Survey-only was already worse than prevalence (0.0955 / 0.3712). |
| Test rows (detected) | 43 (26) | 43 (9; below the minimum of 10 after 1 row was dropped for missing visibility) |
| Brier, model vs prevalence | 0.2960 vs 0.2437 | 0.1787 vs 0.1777 |
| Log loss, model vs prevalence | 0.7949 vs 0.6805 | 0.5740 vs 0.5666 |
| AUC | 0.520 | 0.376 |
| Brier improvement (95% CI, 11-site bootstrap) | -0.052 (-0.129 to 0.027) | -0.001 (-0.005 to 0.004) |
| Mean predicted vs observed | 0.379 vs 0.605 | 0.107 vs 0.209 |
| Decision | `DID_NOT_BEAT_BASELINE_ON_TEST_YEAR` | `DID_NOT_BEAT_BASELINE_ON_TEST_YEAR` |

## Post-scoring diagnostics (these do not change any stored result)

- **Kelp bass:** the temperature effect was learned across years. Kelp bass detections rose during the 2014-2018 warm years. 2022 was cooler at site depth (mean 15.8 C vs 17.3 C in training), but detections stayed high (60%), so the model under-predicted.
  - 5 of 43 test rows, all at one site, were below the training temperature range. `score` does not refuse out-of-support rows; only `predict` does. The Keys pipeline has the same gap.
- **Barred sand bass:** the model is essentially the training prevalence (about 10%). 2022 prevalence was 21%, and the model has no skill at ranking transects.
- **Test-year exposure:** aggregate per-year detection counts for 2022 were seen before freezing (during exploration and the feasibility check). This is disclosed in each preregistration.

## Judgement calls

- **No per-transect depth:** the data has no per-transect depth. HYCOM temperature uses each site's EML depth-range midpoint. Site depth is not a model feature, because with 11 sites it would act as a site identifier.
- **Kelp covariate:** kelp is giant kelp frond density on the same transect and the same day. It is a survey-time covariate, not a forecast input.
- **Small sample:** with 11 fixed sites, both CV and bootstrap are coarse. A single test year cannot separate model skill from that year's conditions.
