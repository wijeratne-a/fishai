# Jack mackerel all-sizes — 24 h PDS `f024` validation

**Verdict: FAIL** (preregistered strict 24 h rule; **INSUFFICIENT** cutoffs for the full eight-window claim).

## 1. PDS `f024` coverage (bucket `noaa-nos-ofs-pds`)

Inventory: `artifacts/jack_mackerel_24h_forecast/pds_f024_inventory.json`.

| Cutoff (cycle D, 03Z) | PDS `f024` |
|---|---|
| 2013-04-26 | none |
| 2013-06-10 | none |
| 2016-09-08 | none |
| 2018-09-20 | none |
| 2021-04-02 | none |
| 2022-09-23 | none |
| **2024-07-29** | **`wcofs/netcdf/202407/nos.wcofs.fields.f024.20240729.t03z.nc`** (ROMS `fields`) |
| **2026-06-25** | **`wcofs/netcdf/2026/06/25/wcofs.t03z.20260625.regulargrid.f024.nc`** (issued `regulargrid`) |

Only **two** of eight locked cutoffs have real issued `f024` on PDS. All pre-2024-07 cutoffs were excluded (no NCEI/`n024` proxy).

## 2. Issued physics pull (SCB bbox)

- Sampler: `scripts/models/sample_jack_mackerel_24h_wcofs_covariates.py` (`--pds-only`).
- Output: `artifacts/jack_mackerel_24h_forecast/wcofs_operational_covariates.csv`
- **24 h rows:** 7 issued WCOFS, **0** proxy.

## 3. Encounter probability maps (24 h ahead, issued `f024`)

Grids (GLORYS-class SCB cells, model refit at each cutoff):

- `artifacts/jack_mackerel_24h_forecast/maps/p_encounter_2024-07-29.csv` (1196 cells)
- `artifacts/jack_mackerel_24h_forecast/maps/p_encounter_2026-06-25.csv` (1196 cells)

## 4. Scores vs persistence & climatology (pooled 24 h, common support)

**Scoring windows used:** cutoffs **2024-07-29** and **2026-06-25** only (`n_eligible_cutoffs = 2` ⇒ `fit_status = INSUFFICIENT` vs the preregistered ≥6 cutoff gate).

| Lane | AUC | TSS | n (common support) | n presence |
|------|-----|-----|-------------------:|---:|
| Operational (issued PDS `f024`) | 1.000 | 0.000 | 3 | 2 |
| Persistence | 1.000 | 0.500 | 3 | 2 |
| Climatology | 1.000 | 0.500 | 3 | 2 |
| Oracle (retrospective GLORYS) | 1.000 | 0.500 | 3 | 2 |

- **`pass_24h`:** false — operational TSS does **not** strictly exceed persistence and climatology (0.0 vs 0.5).
- Full JSON: `prereg/jack_mackerel_24h_forecast_scores.json`.

## 5. Interpretation

PDS **does** deliver genuine `f024` for late-era cutoffs, so a thin-slice issued-forecast test is **feasible** (unlike NCEI-only). With only two windows and three pooled 24 h common-support events, the preregistered pass rule fails on both **sample size** and **TSS vs baselines**. Spatial-block CV reference (PR #53): ELPD −423.96, OOF AUC 0.762, TSS 0.412, Boyce 0.956.
