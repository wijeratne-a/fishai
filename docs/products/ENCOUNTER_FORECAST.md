# 72-hour egg-encounter forecast

Extends the nowcast pipeline (`docs/products/ENCOUNTER_NOWCAST.md`) to a **72-hour** egg / spawning-habitat forecast. Valid times are issue day + 24 h, + 48 h, and + 72 h (`lead_days` 1–3). The column contract is `configs/schemas/cufes_prediction_output.schema.json`. Public maps use `scripts/products/publish_static_maps.py` (10 km cells, Unknown when out of domain, no harvest advice, no adult tracking).

## Run

Inside the CI modeling image:

```bash
docker run --rm -v "$PWD":/work -w /work fishai-pilot \
  Rscript scripts/products/refresh_forecast.R \
  configs/models/cufes_sardine.yaml artifacts/models/sardine/fit.rds \
  configs/models/cufes_anchovy.yaml artifacts/models/anchovy/fit.rds \
  /work/forecast_grid.csv 2024-06-02 2024-06-02T00:00:00Z /work/forecast.json
```

`forecast_grid.csv` is the forecast physics fields on the same covariate columns as the GLORYS nowcast grid. A horizon other than 72 hours is rejected. Out-of-domain cells stay `UNKNOWN` with a null probability.
