# Test priority rules

Rules for ordering hypothesis tests in this repo. No fits in phase `GLOBAL_DATA_ACQUISITION`.

## Hard gates

1. **Phase gate:** Do not fit or refit models while the active phase is global data acquisition. Document candidates only.
2. **Frame gate:** Prefer Atlantic zero-bearing RVC regions (Florida Keys, Puerto Rico, USVI, Flower Garden Banks). Pacific positive-count tables are presence layers only; do not invent non-detections.
3. **Join gate:** External ocean fields must be matched as-of survey time and location in protected storage before any environmental model claim. Snippets and unjoined boxes do not count.
4. **ID gate:** Only use dataset IDs already verified in manifests (e.g. `jplMURSST41`). Do not invent IDs for bottom temperature, oxygen, chlorophyll, currents, or substrate.
5. **Publication gate:** Passing an internal holdout does not authorize a globe layer, nowcast, or species card publication.

## Priority order (when fitting is allowed again)

1. **Historical environmental match for the two Puerto Rico baselines that already passed 2023 holdout** (bicolor damselfish *Stegastes partitus*; redband parrotfish *Sparisoma aurofrenatum*). Test whether joined historical predictors beat the survey-only baseline on the same untouched holdout. Keep results off the globe. Do not expand the species suite first.
2. **Reef visibility and hard-bottom (`H_REEF_VIS_HARD`)** using survey `HABITAT_CD`, visibility, and depth already on the dive—before remote maps.
3. **SST as shallow-guild candidate (`H_SST_PROXY_CAUTION`)** only after historical `jplMURSST41` join; report as guild-scoped, not universal.
4. **Demersal bottom temperature (`H_DEMERSAL_BOTTOM_TEMP`)** only if a depth-resolved product is verified and acquired; otherwise leave untested.
5. **Pelagic fronts (`H_PELAGIC_FRONTS`)** only with verified chlorophyll and/or currents plus an appropriate pelagic observation frame.
6. **Larval current transport (`H_LARVAL_CURRENT_TRANSPORT`)** last among these: needs currents, life-stage labels, and lag design; not a substitute for adult reef detection models.

## Deprioritize / refuse

- Refitting Florida, USVI, or Flower Garden Banks suites before environmental coverage improves.
- Treating GEBCO or bathymetry as reef-presence evidence.
- Stacking OBIS presence into RVC detection likelihoods.
- Forecast or current-field tests before historical join and as-of rules are proven.
- Sample-size or DOI claims not present in repo artifacts.
