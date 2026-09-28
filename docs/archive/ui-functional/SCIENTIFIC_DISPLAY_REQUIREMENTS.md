# Scientific display requirements

**Owner:** `ui-functional/` (spec only).  
**Does not wire or restyle** `globe/prototype`.

## Product honesty (must remain true)

1. **Publish gates.** A current estimate may appear only when a model card is `PUBLISHED` and `hasCurrentEstimate` is true. A forecast may appear only when a card is `PUBLISHED` and `hasForecast` is true. Relative abundance and movement follow the same publish rule.
2. **Goliath.** Atlantic goliath grouper remains `no_estimate`: no issued location, no forecast, not assessed for confidence as a published nowcast.
3. **Unknown default.** When no published now/soon layer applies, scientific status is Unknown (not absence, not empty ocean as a biological claim).
4. **Label separation.** Observed presence, occurrence probability, relative abundance, movement, habitat suitability, and unknown stay separate. Habitat is favorable conditions, not confirmed presence.
5. **Output class.** Internal research scores must be labeled `INTERNAL` / `INTERNAL_MODEL_OUTPUT`, never `PUBLISHED_NOWCAST` or `PUBLISHED_FORECAST`, until a card is actually published.
6. **No public lat/lon fields** on scientific output payloads intended for the globe contract (`spatial_cell_id` only).

## Required display fields (future UI)

When a scientific estimate or evidence object is shown, the UI must expose:

| Field | Requirement |
|---|---|
| Species | Named taxon (common + scientific). |
| Output type | Exactly one: observation, survey non-detection, historical pattern, internal model, published nowcast, published forecast, unknown, etc. |
| Probability | If issued; otherwise explicit “none issued.” |
| Uncertainty | How sure / confidence category with reasons when available. |
| Valid time | Phenomenon or prediction valid interval (not only wall-clock “as of”). |
| Model version | Stable id when a model output is shown. |
| Support | In-support vs out-of-range / unsupported covariate or cell. |
| Sources | Provenance / licenses. |
| Limitations | Known limitations and what is not claimed. |

## Live UI status of honesty gaps

Until implemented against a published card path, treat these as **NOT_IMPLEMENTED** in the live globe:

- Valid time
- Model version (as a scientific species-output chip)
- Extrapolation
- Sensitivity withheld (structured)
- Environmental latency

See `UI_FUNCTIONAL_AUDIT.md` for the read-only gate findings.

## Evidence inspector

`evidence-inspector/README.md` defines inspector fields and states that the inspector is a **spec with mock data only**, not wired to the globe.
