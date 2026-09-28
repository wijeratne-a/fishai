# Temporal standardization

## Clocks

| Field | Role |
|---|---|
| `observed_at_utc` | When the phenomenon occurred (or window start) |
| `observed_at_source_local` + `source_timezone` | Preserved source wall time (IANA tz) |
| `published_at_utc` | When the source released this version (**as-of join key**) |
| `ingested_at_utc` | When FishAI stored raw bytes |
| `valid_from_utc` / `valid_to_utc` | Validity window for products and regulations |

Internal storage uses UTC ISO-8601 with `Z`.

## Time precision (required)

Every event, observation, measurement, and globe product must set:

`SECOND` | `MINUTE` | `HOUR` | `DAY` | `MONTH` | `YEAR` | `UNKNOWN`

Do not invent finer precision than the publisher. Day-only surveys use `DAY`, not `SECOND`.

## Leakage

- Labels at time *t* may use only covariates with `published_at_utc ≤ t` (or an explicit retrospective lane).
- Internal research fits are not published nowcasts.
- Forecast validity windows must be stated; a forecast is not a current observation.
