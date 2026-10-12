# Jack mackerel (all sizes) 24 h encounter forecast — thin slice

**Model:** `configs/models/jack_mackerel_encounter_all_sizes.yaml` (spatial-block CV ELPD −423.96, OOF AUC 0.762, TSS 0.412, Boyce 0.956).

**Physics:** Issued WCOFS `fields.f024` from cutoff cycle D for holdout D+1 (24 h). Sources, in order: NOAA NCEI THREDDS fileServer (`model-wcofs-files`, 2021-03-22+), then public PDS `noaa-nos-ofs-pds` (2024-07-01+). No damped proxy for this thin-slice claim — missing issued fields ⇒ BLOCKED, not scored as WCOFS.

**Baselines / pass rule:** Same as `prereg/adult_sardine_24h_forecast_design.md` (persistence + DOY climatology; strict AUC and TSS at 24 h; ≥ 6 eligible cutoffs).

**Scoring window overlap:** Cutoffs with D ≥ 2021-03-22 (NCEI archive operational start).
