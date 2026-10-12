# Jack mackerel all-sizes — 24 h forecast validation (thin slice)

**Verdict: FAIL** (preregistered pooled 24 h rule). **Issued-WCOFS coverage: BLOCKED** for a full eight-cutoff, proxy-free claim.

## 1. Scoring windows vs NCEI archive (2021-03-22+)

Rolling-origin cutoffs (adult CPS protocol, K=8, min 120 training rows):  
`2013-04-26`, `2013-06-10`, `2016-09-08`, `2018-09-20`, `2021-04-02`, `2022-09-23`, `2024-07-29`, `2026-06-25`.

**Overlap with WCOFS NCEI era (D ≥ 2021-03-22):** 4 cutoffs — `2021-04-02`, `2022-09-23`, `2024-07-29`, `2026-06-25`.  
Task 1 is satisfied (windows exist); validation is not stopped here.

## 2. Issued WCOFS fields (no proxy)

- **NCEI THREDDS** (`model-wcofs-files`): `fields.n024` / `2ds.n024` present from 2021-03-22; **no `fields.f024` (or any `fields.f*`)** in monthly catalogs checked (2021-03, 2022-09, 2024-07).
- **24 h product** for holdout D+1 requires **`fields.f024`** from cycle D (03Z). That lead is on **public PDS** from **2024-07-01+** (e.g. `wcofs/netcdf/202407/nos.wcofs.fields.f024.20240729.t03z.nc`).
- **2021–2023 cutoffs:** no `fields.f024` on NCEI (404 on fileServer) or PDS — cannot populate issued forecast physics without proxy.
- **Sampler result (24 h rows):** 7 `ISSUED_FORECAST` + 17 `NOT_ISSUED_FORECAST` (missing object / before archive).

## 3. Encounter maps (24 h ahead)

Operational map product for cutoff **2024-07-29** (issued `f024` on SCB grid) is supported by the same covariate pipeline as adult sardine; grid export is not committed in this thin-slice run. Event-level scores and WCOFS keys are in `artifacts/jack_mackerel_24h_forecast/wcofs_operational_covariates.csv`.

## 4. Scores vs persistence & climatology (24 h, pooled common support)

| Lane | AUC | TSS | n (common support) | n presence |
|------|-----|-----|-------------------|------------|
| Operational (mixed issued + proxy) | 0.500 | −0.250 | 5 | 4 |
| Persistence | 1.000 | 0.500 | 5 | 4 |
| Climatology | 1.000 | 0.500 | 5 | 4 |
| Oracle (retrospective GLORYS) | 0.750 | 0.500 | 5 | 4 |

- **Eligible cutoffs (converged fits):** 8 / 8  
- **Issued WCOFS 24 h rows in pool:** 3  
- **`pass_24h`:** false (operational does not strictly beat both baselines on AUC and TSS)

**Issued-WCOFS-only** common-support rows (n=3, 2 presences): operational AUC 1.0, TSS 0.0 vs persistence/climatology AUC 1.0, TSS 0.5 — still fails strict TSS rule; sample too small for a standalone claim.

## 5. Reference

Spatial-block CV (PR #53): ELPD −423.96, OOF AUC 0.762, TSS 0.412, Boyce 0.956.  
Full JSON: `prereg/jack_mackerel_24h_forecast_scores.json`.
