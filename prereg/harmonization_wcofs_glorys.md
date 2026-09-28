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

The **daily nowcast path** must call **`coarsen_wcofs_to_glorys`** and **`compute_wcofs_covariates_on_glorys_grid`** in `fishai.ingestion.physics.wcofs_glorys_grid` — the same shared functions as overlap/holdout scoring. **Native ~4 km WCOFS** is scored only as a **diagnostic** row and is **never** passed through the harmonization map.

Correction models for mapped WCOFS are fit on the fit window only; reported holdout scores use the **test** window only.

## Fields and grids

Seven harmonized variables: **T3m**, **S3m**, **MLD_m**, **sst_grad**, **front_distance_km**, and surface **u** and **v**. WCOFS is coarsened to the GLORYS horizontal grid with **area-weighted** regridding (WCOFS cell weight `1/(pm*pn)`, half-open GLORYS boxes, `wet_fraction` with `min_wet_fraction: 0.5` matching `data/config/wcofs_glorys_overlap.yaml` when present). SST/T3m/S3m use depth below the **moving surface** (`zeta - z_rho`); SST at **0.494 m** below surface (GLORYS top level). Reference GLORYS product: **`cmems_mod_glo_phy_myint_0.083deg_P1D-m`** for all fit and test dates.

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

Nearshore (bot2 PR #7 @ cc26ab4): `Natural Earth ne_10m_land` v**5.1.1**, public domain, clip lat 31–36 / lon −122 to −116 (Channel Islands), path `data/reference/shoreline/ne_10m_land_pilot_clip.json`, **cutoff_km 20**, geodesic distance on WGS84 from GLORYS cell centre to nearest shoreline. **Scoring strata:** buoys and HF radar cells use the **matched GLORYS cell’s** nearshore flag (same for all four model rows, including native WCOFS). `shoreline_sha256` and `shoreline_simplification_check` remain `TO_BE_SET_BEFORE_SCORING`. auditbot1 cutoffs unchanged.

## Timing

Commit this YAML and markdown **before** generating test-split pairings or score outputs. Downstream tests (e.g. bot2 #7) should read `fit_start`, `fit_end`, `test_start`, and `test_end` from this file rather than hard-coding dates.
