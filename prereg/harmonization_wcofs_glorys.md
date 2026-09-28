# Pre-registration: WCOFS / GLORYS harmonization holdout

**Status:** Locked protocol for comparing WCOFS inference fields to GLORYS training fields and to independent observations during the pilot overlap window.

## Purpose

Before any test-split observational pairing or score tables are produced, this document and `prereg/harmonization_wcofs_glorys.yaml` define splits, variables, models, observation matching, independence rules, metrics, and known limitations. Pass/degraded numeric cutoffs are **not** set here; they remain placeholders owned by **auditbot1** until explicitly filled.

## Temporal split (machine-readable)

| Field | Value |
| --- | --- |
| `overlap_start` / `overlap_end` | 2024-09-01 … 2026-06-23 |
| `fit_start` / `fit_end` | 2024-09-01 … **2025-08-31** |
| `test_start` / `test_end` | **2025-09-01** … 2026-06-23 |

**Resolution (exact string in YAML):** `WCOFS coarsened to GLORYS grid, area-weighted, wet-masked`

The **daily nowcast path** must call the **same single coarsening function** as the overlap/holdout path so features are built identically. **Native ~4 km WCOFS** is scored only as a **diagnostic** row and is **never** passed through the harmonization map.

Correction models for mapped WCOFS are fit on the fit window only; reported holdout scores use the **test** window only.

## Fields and grids

Seven harmonized variables: **T3m**, **S3m**, **MLD_m**, **sst_grad**, **front_distance_km**, and surface **u** and **v**. WCOFS is coarsened to the GLORYS horizontal grid with area weights and a wet mask before front features; both models share a **0–200 m, 1 m** vertical grid before T3m, S3m, and MLD are derived.

## Models compared

1. Native WCOFS (diagnostic only; no harmonization map)  
2. WCOFS coarsened to the GLORYS grid  
3. Coarsened WCOFS plus a correction fit on the fit split only  
4. GLORYS  

## Frozen mapping artifact (bot3, later PR)

The WCOFS-to-GLORYS map is fit by **bot3** on the **fit split only**, then frozen under `artifacts/harmonization/wcofs_to_glorys_map/v1/` with a sidecar **`manifest.json`** recording: fitting commit SHA, SHA-256 of the fit-split Parquet, this pre-registration file’s commit SHA, variables mapped, and the fit date range (`fit_start`–`fit_end`). **Scoring and the nowcast path load only this frozen map and never refit it.**

## Observations

- **NDBC** hull water temperature: stations from `docs/archive/legacy_data/globe_fixtures/stations.json`, nearest cell, same-day daily mean; GLORYS at **0.49 m**, WCOFS nearest level to **1 m**.  
- **SCCOOS HF radar** u/v: daily cell means, masked when **hdop > 1.25** or **fewer than 2** sites.  
- **Gliders:** excluded while the IOOS feed is pending/disabled.

## Independence

Scores use `config/assimilated_sources.yaml` (versioned, cited). Unknown assimilation status is reported separately and never pooled. HF radar is **presumed assimilated by WCOFS** unless the registry documents otherwise.

## Metrics

Per variable: **bias**, **RMSE**, **Pearson r**, by season (DJF/MAM/JJA/SON), nearshore/offshore, and pooled, each with **n** and a **7-day block bootstrap 95% CI**. **Front-detail loss** is mean coarsened-WCOFS **sst_grad** divided by native WCOFS on the same days. Test-split **JJA** is **1–23 June only** (`test_split_jja_partial`).

Nearshore (bot2): **Natural Earth** `ne_10m_land` (public domain, Channel Islands included), clipped to lat 31–36°N and lon 122–116°W; **20 km** geodesic cutoff from each GLORYS cell centre to the nearest mainland or island shoreline (`nearshore_rule` in YAML). `shoreline_version` and `shoreline_sha256` stay `TO_BE_SET_BEFORE_SCORING` until bot2 posts the exact version and hash; scoring **must refuse** while those two fields are unset. auditbot1 pass/degraded cutoffs remain placeholders.

## Timing

Commit this YAML and markdown **before** generating test-split pairings or score outputs. Downstream tests (e.g. bot2 #7) should read `fit_start`, `fit_end`, `test_start`, and `test_end` from this file rather than hard-coding dates.
