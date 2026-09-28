# Pre-registration: WCOFS / GLORYS harmonization holdout

**Status:** Locked protocol for comparing WCOFS inference fields to GLORYS training fields and to independent observations during the pilot overlap window.

## Purpose

Before any test-split observational pairing or score tables are produced, this document and `prereg/harmonization_wcofs_glorys.yaml` define splits, variables, models, observation matching, independence rules, metrics, and known limitations. Pass/degraded numeric cutoffs are **not** set here; they remain placeholders owned by **auditbot1** until explicitly filled.

## Temporal split

| Window | Dates |
| --- | --- |
| Overlap (data available for both models) | 2024-09-01 through 2026-06-23 |
| **Fit** (correction maps only) | 2024-09-01 through **2025-08-31** |
| **Test** (all reported holdout scores) | **2025-09-01** through 2026-06-23 |

Correction models for mapped WCOFS are fit on the fit window only; all candidate model scores listed in the YAML are evaluated on the **test** window only.

## Fields and grids

Seven harmonized variables: **T3m**, **S3m**, **MLD_m**, **sst_grad**, **front_distance_km**, and surface **u** and **v**. WCOFS is coarsened to the GLORYS horizontal grid with area weights and a wet mask before front features; both models share a **0–200 m, 1 m** vertical grid before T3m, S3m, and MLD are derived.

## Models compared

1. Native WCOFS  
2. WCOFS coarsened to the GLORYS grid  
3. Coarsened WCOFS plus a correction fit on the fit split only  
4. GLORYS  

## Observations

- **NDBC** hull water temperature: stations from `docs/archive/legacy_data/globe_fixtures/stations.json`, nearest cell, same-day daily mean; GLORYS at **0.49 m**, WCOFS nearest level to **1 m**.  
- **SCCOOS HF radar** u/v: daily cell means, masked when **hdop > 1.25** or **fewer than 2** sites.  
- **Gliders:** excluded while the IOOS feed is pending/disabled.

## Independence

Scores use `config/assimilated_sources.yaml` (versioned, cited). Unknown assimilation status is reported separately and never pooled. HF radar is **presumed assimilated by WCOFS** unless the registry documents otherwise.

## Metrics

Per variable: **bias**, **RMSE**, **Pearson r**, by season (DJF/MAM/JJA/SON), nearshore/offshore, and pooled, each with **n** and a **7-day block bootstrap 95% CI**. **Front-detail loss** is mean coarsened-WCOFS **sst_grad** divided by native WCOFS on the same days. Test-split **JJA** is **1–23 June only** (`test_split_jja_partial`).

Nearshore uses `shoreline_source` and `nearshore_cutoff_km` from bot2; both are `TO_BE_SET_BEFORE_SCORING` until supplied. Scoring code **must refuse** while placeholders remain.

## Timing

Commit this YAML and markdown **before** generating test-split pairings or score outputs. Record the git object id of this file in run metadata when scoring is eventually enabled.
