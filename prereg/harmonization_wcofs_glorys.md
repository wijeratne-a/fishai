# Pre-registration: WCOFS / GLORYS harmonization holdout

**Status:** Locked protocol for comparing WCOFS inference fields to GLORYS training fields and to independent observations during the pilot overlap window.

## Purpose

Before any test-split observational pairing or score tables are produced, this document and `prereg/harmonization_wcofs_glorys.yaml` define splits, variables, models, observation matching, independence rules, metrics, nowcast-forcing grade gates, and known limitations. Machine-readable gate thresholds live in `nowcast_forcing_grading` and related YAML blocks below.

## Temporal split (machine-readable)

| Field | Value |
| --- | --- |
| `overlap_start` / `overlap_end` | 2024-09-01 … 2026-06-23 |
| `fit_start` / `fit_end` | 2024-09-01 … **2025-08-31** |
| `test_start` / `test_end` | **2025-09-01** … 2026-06-23 |

**Resolution (exact string in YAML):** `WCOFS coarsened to GLORYS grid, area-weighted, wet-masked`

The **daily nowcast path** must call **`coarsen_wcofs_to_glorys`** and **`compute_wcofs_covariates_on_glorys_grid`** in `fishai.ingestion.physics.wcofs_glorys_grid` — the same shared functions as overlap/holdout scoring. **Native ~4 km WCOFS** is scored only as a **diagnostic** row and is **never** passed through the harmonization map.

Correction models for mapped WCOFS are fit on the fit window only; reported holdout scores use the **test** window only.

## Graded nowcast row

Only **`wcofs_coarsened_mapped`** receives PASS/DEGRADED/FAIL **nowcast-forcing** gates. Native WCOFS, coarsened-only WCOFS, and GLORYS remain diagnostic/report rows for harmonization tables. **SCCOOS HF radar** is assimilated by WCOFS and is **report-only** for forcing gates.

## Fields and grids

**Five graded inputs:** **T3m**, **S3m**, **MLD_m**, **sst_grad**, **front_distance_km**. Each stratum passes when RMSE ≤ 0.5× GLORYS spatial SD, is DEGRADED up to 1.0×, and FAILs above; a failed input makes the stratum **UNKNOWN**. **`upwelling`** stays in `variables` as **`shared_forcing`** (reported, never graded). **`u_surf`** and **`v_surf`** are report-only. The graded-input gate refuses to run if any of the five graded names is missing from `variables`. If no single wind product covers both CUFES training years and daily nowcasts, **`upwelling`** is blank with reason `no_consistent_wind_product`, dropped from the pilot model, and no events are excluded.

WCOFS is coarsened to the GLORYS horizontal grid with **area-weighted** regridding (WCOFS cell weight `1/(pm*pn)`, half-open GLORYS boxes, `wet_fraction` with `min_wet_fraction: 0.5` matching `data/config/wcofs_glorys_overlap.yaml` when present). SST/T3m/S3m use depth below the **moving surface** (`zeta - z_rho`); SST at **0.494 m** below surface (GLORYS top level). **GLORYS product choice is date-based** (same rule as the `source_product` column): **`cmems_mod_glo_phy_my_0.083deg_P1D-m`** through **2021-06-30**, **`cmems_mod_glo_phy_myint_0.083deg_P1D-m`** from **2021-07-01** onward (the pilot harmonization window uses interim only).

## Models compared (harmonization holdout)

1. Native WCOFS (diagnostic only; no harmonization map)  
2. WCOFS coarsened to the GLORYS grid  
3. Coarsened WCOFS plus a correction fit on the fit split only (**graded for forcing**)  
4. GLORYS  

## Frozen mapping artifact (bot3, later PR)

The WCOFS-to-GLORYS map is fit by **bot3** on the **fit split only**, then frozen under `artifacts/harmonization/wcofs_to_glorys_map/v1/` with a sidecar **`manifest.json`** recording: fitting commit SHA, SHA-256 of the fit-split Parquet, this pre-registration file’s commit SHA, variables mapped, and the fit date range (`fit_start`–`fit_end`). **Scoring and the nowcast path load only this frozen map and never refit it.**

## Observations and forcing gates

- **NDBC** hull water temperature at **0.494 m** below the moving surface (graded vs **`wcofs_coarsened_mapped`** only). NDBC is **not** assimilated by WCOFS (NOAA Tech Report CO-OPS 097, p.17; auditor accepted). Strata: **pooled**, **nearshore**, **offshore** — each needs ≥100 matched daily values from ≥3 buoys or is not gradable. **PASS:** RMSE ratio to GLORYS ≤1.2 with bootstrap upper ≤1.5; |bias| ≤0.5 °C; Pearson r no more than 0.10 below GLORYS r. **DEGRADED:** ratio in (1.2, 1.5] or bias in (0.5, 1.0] °C. Worse → **UNKNOWN** with reason `nowcast_forcing_failed_holdout`. Harmonization holdout still compares all four model rows at 0.494 m via bot2’s shared depth function.
- **SCCOOS HF radar** u/v: daily cell means, masked when **hdop > 1.25** or **fewer than 2** sites — **report-only** for forcing.
- **Scripps Spray gliders** `binnedCUGN80` and `binnedCUGN90` (free to use/redistribute; independent of WCOFS per CO-OPS 097). Grade **`wcofs_coarsened_mapped`** only, never GLORYS. Variables: **MLD_m**, **T and S at 10 m** (stand-in for 3 m), model values interpolated from s-levels at profile time/position; **doxy** report-only. ≥100 matched profiles from ≥3 missions per stratum or not gradable. Same RMSE-ratio-to-GLORYS rule as buoys (GLORYS may assimilate gliders — conservative). Absolute bias limits: T10 0.5 °C, S10 0.1, MLD 10 m (auditor judgment); 1–2× limit DEGRADED, >2× FAIL. Pearson r as buoys. MLD via `fishai.ingestion.physics.vertical.mld` (10 m reference, 0.2 °C drop, interpolated); profiles not reaching the drop are null with `mld_not_reached` and excluded from MLD grading.

## Combination rules

Per stratum, take the **worst** verdict in order **UNKNOWN → FAIL → DEGRADED → PASS**. No gradable independent check caps at **DEGRADED** (`no_independent_obs_check`). No independent source at all → every stratum **UNKNOWN** (`no_independent_validation`).

## Upwelling lags (if `upwelling` survives)

Trailing means over **0, 7, 14, and 28** days ending the day before the event (no other lags). Selected by time-forward CV on the fit split through **2017-12-31** by mean out-of-fold log-likelihood; frozen before **2018-01-01** and never re-selected for the **2018-01-01–2022-04-27** test (auditor accepted).

## Independence

Scores use `config/assimilated_sources.yaml` (versioned, cited). Unknown assimilation status is reported separately and never pooled.

## Metrics

Per variable: **bias**, **RMSE**, **Pearson r**, by season (DJF/MAM/JJA/SON), nearshore/offshore, and pooled, each with **n** and a **7-day block bootstrap 95% CI**. **Common-support scoring:** all four harmonization model rows use only buoy/HF matches where **every row has a value**; drops because any row is blanked are reported as **`insufficient_model_coverage`** (nearshore/offshore). **Map labels:** **`egg encounter likelihood`** only — not spawning habitat, spawning locations, or adult distribution.

## Shoreline (bot2 PR #7)

**Frozen shoreline** (`frozen_shoreline_reference` in YAML): path `data/reference/shoreline/ne_10m_land_pilot_clip.json`, SHA-256 frozen at PR #7 commit **8d4bfae** (import **`FROZEN_PILOT_SHORELINE_REFERENCE_SHA256`** from `fishai.evaluation.harmonization_prereg` for scoring). **`shoreline_simplification_check`:** method **`none_bbox_clip_only`** (Natural Earth `ne_10m_land` v**5.1.1**, pilot bbox clip, not simplified); **0** nearshore-flag mismatches vs full resolution; rejected trial was ~400-vertex simplification (**211** mismatches). `file_sha256` aliases the frozen reference. **cutoff_km 20**, geodesic WGS84 from GLORYS cell centre. Scoring strata inherit the matched GLORYS cell nearshore flag.

## Timing

Commit this YAML and markdown **before** generating test-split pairings or score outputs. Downstream tests (e.g. bot2 #7) should read `fit_start`, `fit_end`, `test_start`, and `test_end` from this file rather than hard-coding dates.

**Wet-fraction (coarsened WCOFS only):** bot2 writes read-only `artifacts/harmonization/wcofs_glorys_overlap/coverage_report.json` — GLORYS-ocean cells blanked by the 0.5 rule (nearshore/offshore, surface and each covariate level) and CUFES events in those cells by `event_id` vs **14,592** / **13,326** long events. **Does not exclude training rows** (CUFES ocean comes from GLORYS). Rows with **missing own ocean data** stay `excluded = TRUE` with their reason, never zeros. **Nowcast:** blanked coarsened-WCOFS cells → `evidence_state = UNKNOWN`, reason `insufficient_model_coverage` (test in bot2/nowcast).
