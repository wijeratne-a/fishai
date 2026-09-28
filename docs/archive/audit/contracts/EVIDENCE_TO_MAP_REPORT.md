# Evidence-to-map report

**Scope:** Synthetic honesty checks only. No live globe writes. No coordinates printed.  
**Tests:** `tests/contracts/evidence-to-map/test_evidence_labels.py`

## Rejected materializations

| Case | Reject reason | Correct treatment |
|---|---|---|
| SST / analysed sea-surface temperature as a fish sighting | `sst_is_not_a_fish_sighting` | `ENVIRONMENTAL_CONDITION` measurement only |
| OBIS presence as current location | `obis_presence_is_not_current_location` | `HISTORICAL_OCCURRENCE` or presence evidence — not “here now” |
| Survey zero as regional ecological absence | `survey_zero_is_not_regional_ecological_absence` | `SURVEY_NONDETECTION` with `is_ecological_absence_claim=false` |
| Internal baseline as published nowcast | `internal_baseline_is_not_published_nowcast` | `INTERNAL_MODEL_OUTPUT` / `NOT_PUBLISHED` |
| Forecast without issue and valid times | `forecast_requires_*` | Require `issued_at_utc`, `valid_from_utc`, `valid_to_utc` |
| `NOT_PUBLISHED` producing a probability layer | `not_published_cannot_produce_probability_layer` | Keep off the public probability map |

## Allowed examples (synthetic)

- SST with `evidence_label=ENVIRONMENTAL_CONDITION` and no fish-sighting claim.
- Forecast with issue time and a closed valid window when `publish_status=PUBLISHED`.

## Product alignment

Matches `docs/GLOBE_DATA_CONTRACT.md` and `schemas/globe-evidence.schema.json` / `schemas/globe-model-output.schema.json`. Empty ocean + `UNKNOWN` remains a valid cold-load state.
