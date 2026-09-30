# Prediction map UX spike (synthetic fixture)

Internal prototype for the Southern California Bight pilot domain (**32–35°N, 121–117°W**). Cells load only from the committed synthetic fixture; every row has `dry_run: true`. This is **not** a nowcast.

## Run the map

From this directory, serve static files (any simple HTTP server):

```bash
cd prototype/prediction-map
python -m http.server 8765
```

Open `http://127.0.0.1:8765/` in a browser. No build step; ES modules load from disk.

## Fixture

- Path: `fixtures/synthetic_cufes_grid.json`
- Validates against `configs/schemas/cufes_prediction_output.schema.json` (see `tests/prototype/test_prediction_map_fixture.py`).

## Copy doctrine

User-facing strings use **egg-encounter** / **spawning-habitat** wording. The UI shows:

1. **Schema `evidence_state`** enum (data contract).
2. **README display doctrine** labels (Direct Observation, Historical Pattern, Current Nowcast, Forecast, Unknown) — see repo root `README.md` § Evidence-state vocabulary.

Those lists are not merged into a single invented scale. `UNKNOWN` cells never receive a probability fill.
