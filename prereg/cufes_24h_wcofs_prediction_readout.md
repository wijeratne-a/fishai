# CUFES 24 h WCOFS-first prediction — readout

Egg-encounter validation only (not adult fish, not harvest advice).

**Forcing label (pooled):** `proxy_fallback` (WCOFS lead `f024` when reachable).

Public WCOFS `fields.*` archives begin 2024-07; CUFES egg scoring ends 2022-04-27. Historical cutoffs cannot use issued WCOFS; operational scores use the pre-declared GLORYS-based damped-anomaly proxy.

## Example 24 h WCOFS forcing map (pipeline demo)

Live public WCOFS `fields.f024` for cycle **2024-09-05**, coarsened and sampled on the **10 km** pilot grid (egg-forcing covariate field, not a validated egg-encounter product):

- `artifacts/cufes_24h_wcofs_prediction/maps/wcofs_24h_t3m_10km.png`
- Metadata: `artifacts/cufes_24h_wcofs_prediction/maps/map_metadata.json`

## sardine

- **24 h verdict:** FAIL
- AUC: operational 0.8235 vs persistence 0.5966 vs climatology 0.9832
- TSS: operational -0.0084 vs persistence 0 vs climatology 0.8908

Maps from this pipeline are a **demonstration only** until validation passes; they are not a validated prediction product.

## anchovy

- **24 h verdict:** FAIL
- AUC: operational 0.9622 vs persistence 0.9911 vs climatology 0.9889
- TSS: operational 0 vs persistence 0 vs climatology 0

Maps from this pipeline are a **demonstration only** until validation passes; they are not a validated prediction product.

