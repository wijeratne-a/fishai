# Jack mackerel (all sizes) 24 h encounter forecast — PDS f024 thin slice

**Model:** `configs/models/jack_mackerel_encounter_all_sizes.yaml` (spatial-block CV ELPD −423.96, OOF AUC 0.762, TSS 0.412, Boyce 0.956).

**Physics (this run):** Issued WCOFS **`f024`** from cutoff cycle **D** (03Z) for holdout **D+1** only. Source: public bucket **`noaa-nos-ofs-pds`** (`wcofs/netcdf/...`). Prefer ROMS `fields.f024` (`wcofs.t03z.*.fields.f024.nc` or legacy `nos.wcofs.fields.f024.*.t03z.nc`); when absent, use issued `regulargrid.f024`. Subset to SCB pilot bbox before coarsening onto the GLORYS grid. **No** NCEI THREDDS, **no** nowcast (`n024`) substitution, **no** damped-anomaly proxy.

**Cutoffs:** Lock K=8 adult CPS cutoffs as in the sardine design; **score only** cutoffs with a listed PDS `f024` object (inventory: `artifacts/jack_mackerel_24h_forecast/pds_f024_inventory.json`).

**Baselines / pass rule:** Same strict pooled 24 h rule as `prereg/adult_sardine_24h_forecast_design.md` (operational AUC and TSS strictly greater than persistence and climatology on common-support events). Full eight-cutoff claim requires ≥6 eligible cutoffs; when fewer PDS windows exist, report metrics and `fit_status = INSUFFICIENT` without inventing physics.
