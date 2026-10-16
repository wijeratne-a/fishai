# Egg-encounter nowcast

Refreshes sardine and anchovy **egg / spawning-habitat** surfaces on the latest GLORYS valid day. This is not adult-fish tracking and not harvest advice.

## Inputs

- Frozen artifacts from `freeze_model()` (not rebuilt here).
- A GLORYS covariate grid CSV with the model columns, `X`, `Y` (km, EPSG:32611), and `time_idx`.
- A local day index JSON (array of `YYYY-MM-DD`). The newest day is the nowcast valid day. An empty index fails closed.

## Run

Use the CI modeling image so R packages come from `renv`, not the host:

```bash
docker build --build-arg R_BASE_IMAGE=<r-env tag> -t fishai-pilot .
docker run --rm -v "$PWD":/work -w /work fishai-pilot \
  Rscript scripts/products/refresh_nowcast.R \
  configs/models/cufes_sardine.yaml artifacts/models/sardine/fit.rds \
  configs/models/cufes_anchovy.yaml artifacts/models/anchovy/fit.rds \
  /work/glorys_grid.csv 2024-06-01 2024-06-01T00:00:00Z /work/nowcast.json
```

Python selects the day before that call:

```bash
python -c "from pathlib import Path; from fishai.products.nowcast import latest_glorys_valid_day; print(latest_glorys_valid_day(Path('glorys_days.json')))"
```

Rows validate against `configs/schemas/cufes_prediction_output.schema.json`. Issued cells are `NOWCAST_UNVALIDATED` with `lead_days` 0. Out-of-domain cells are `UNKNOWN` with a null probability. Publish with `scripts/products/publish_static_maps.py`.
