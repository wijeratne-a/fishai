# Temporal integrity rules

**Status:** Binding validation contract for feature timing and forecast clocks.  
**Schema:** `science/time/FORECAST_TIME_SCHEMA.json`  
**Related:** `docs/TEMPORAL_STANDARDIZATION.md`

## Clocks (must stay distinct)

| Field | Meaning |
|---|---|
| `event_time_utc` | When the survey or observation occurred (to declared precision) |
| `feature_valid_time_utc` | Instant or window the covariate describes |
| `feature_available_at_utc` | Earliest time the covariate value could have been known / published |
| `issue_time_utc` | When a forecast or analysis product was issued |
| `valid_time_utc` | Instant the forecast claims to describe |
| `lead_time` | `valid_time_utc − issue_time_utc` (must be explicit when they differ in role) |

## Hard prohibitions

1. **Post-event features** — A training or scoring feature for an event at time *t* must not use values with `feature_available_at_utc > event_time_utc` (or `feature_valid_time_utc > event_time_utc` when availability is unknown and the field is treated as known-at-valid-time). Post-event analysed fields entering operational features fail.

2. **Centered windows as operational lags** — A symmetric / centered temporal window around *t* (e.g. ±N days) must not be labeled or used as an operational lag / as-of feature. Operational lags use only data available at or before *t*.

3. **Forecast without lead** — If a record is a forecast (`product_kind=forecast`), `valid_time_utc` must not equal `issue_time_utc` unless an explicit `lead_time` of zero is declared and justified (nowcast lane). Equality without a declared lead fails.

4. **Fabricated timestamps** — Date-only source records (`time_precision=DAY`) must not receive an invented hour, minute, or second. Keep day precision; do not fabricate `T12:00:00Z` (or any clock) to satisfy a schema.

5. **Locked holdout for feature choice** — A covariate definition (product, offset, scaling, missingness rule) must be frozen on training / tuning years. The locked holdout year must not be used to choose or retune the feature.

6. **Run manifest** — Every modeling run writes checksums, seed, train years, holdout year, code version, and `publish_status=NOT_PUBLISHED`. A run without a manifest is invalid.

## Allowed patterns

- Retrospective research lanes may use post-event analyses only when marked `lane=retrospective` and never claimed as operational nowcast/forecast features.
- Day-only surveys use `time_precision=DAY` and date strings without fabricated clock components.
- Forecasts declare both `issue_time_utc` and `valid_time_utc`, plus `lead_time` (ISO-8601 duration or hours).

## Synthetic validation

`tests/time/test_temporal_integrity.py` fails the prohibited patterns above using synthetic timestamps only.
