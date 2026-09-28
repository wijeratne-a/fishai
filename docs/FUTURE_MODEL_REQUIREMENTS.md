# Future model requirements

**Status:** Requirements only. No training authorized by this file. Issued published models today: **none**.

## Label honesty

| Requirement | Rule |
|---|---|
| Zeros | Only from completed effort + taxon-in-frame (`SURVEY_NONDETECTION`) |
| Missing rows | Not absences |
| Presence-only | Not absence; cannot train as Bernoulli without a frame |
| Environmental fields | Covariates only; SST ≠ fish observation |
| Protocols | Separate likelihoods unless bridged explicitly |

## Feature honesty

- Match covariates to the event’s time precision, spatial support, and depth band.
- As-of joins on `published_at_utc`; no future leakage.
- Habitat suitability is not presence.

## Publication honesty

- `INTERNAL_MODEL_OUTPUT` stays internal until a card is `PUBLISHED`.
- Internal skill ≠ `PUBLISHED_NOWCAST` / `PUBLISHED_FORECAST`.
- No fishing guidance in any product surface.
- Public geometry: cells/units only — no raw coordinates.

## Sample-size policy

Do **not** invent minimum *n*. Any numeric threshold requires a written power analysis. Placeholder token: **`THRESHOLD_REQUIRES_POWER_ANALYSIS`**.

See also `audit/model-readiness/MODEL_INPUT_REQUIREMENTS.csv`.
