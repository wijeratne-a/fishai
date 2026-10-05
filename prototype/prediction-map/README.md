# Prediction map UX spike (synthetic fixture)

Internal prototype for the Southern California Bight pilot domain (**32–35°N, 121–117°W**). The map renders egg-encounter rows that conform to `configs/schemas/cufes_prediction_output.schema.json`. It loads only the committed synthetic fixture; every row has `dry_run: true`. This is **not** a nowcast and is **not** wired to a prediction engine.

## Run the egg map

From this directory, serve static files (any simple HTTP server):

```bash
cd prototype/prediction-map
python -m http.server 8765
```

Open `http://127.0.0.1:8765/` in a browser. CesiumJS loads from the Cesium CDN (satellite imagery from Esri World Imagery). No install step. Drag to rotate the egg-encounter globe; scroll to zoom. Toggle sardine or anchovy egg-encounter.

Likelihood is a **dot-density** layer on a **10 km** lattice: more dots where egg-encounter probability is higher. Zero probability and out-of-domain egg conditions (`ood_level` ≥ 2, **UNKNOWN**) render **no dots**. Distant camera heights keep fewer dots so the spawning-habitat globe stays smooth. Fixture cells are about **50 km** apart.

## Fixture

- Path: `fixtures/synthetic_cufes_grid.json`
- Watermarked synthetic egg-encounter grid only. Species and domain follow the synthetic model configs `configs/models/cufes_sardine_synthetic.yaml` and `configs/models/cufes_anchovy_synthetic.yaml`. Those configs are not executed here.
- Validates against `configs/schemas/cufes_prediction_output.schema.json` (see `tests/prototype/test_prediction_map_fixture.py`).

## Copy doctrine

User-facing strings use **egg-encounter** / **spawning-habitat** wording. The UI shows:

1. **Schema `evidence_state`** enum (data contract) on every egg cell.
2. **README display doctrine** labels (Direct Observation, Historical Pattern, Current Nowcast, Forecast, Unknown) — see repo root `README.md` § Evidence-state vocabulary.

Those lists are not merged into a single invented scale. `UNKNOWN` egg cells render nothing on the globe. The page does not give harvest advice and does not describe live animals.
