# Scientific failure policy

**Purpose:** When a scientific path cannot produce a trustworthy value, emit a safe status token. Never invent a substitute species, probability, or location.

## Safe output tokens

| Token | Meaning |
|---|---|
| `UNKNOWN` | Evidence insufficient to label; default empty-ocean state |
| `UNAVAILABLE` | Required input or service is not available |
| `INSUFFICIENT_DATA` | Inputs exist but do not meet documented readiness for this question |
| `STALE` | Inputs are too old relative to the requested valid time |
| `UNSUPPORTED` | Query is outside model/domain support mask |
| `WITHHELD` | Result must not be shown (rights, sensitivity, or publication gate) |

These tokens are **terminal safe outputs**. They are not probabilities and must not be cast to 0 or 0.5 for display convenience.

## Hard rules

1. **No species substitution.** If model A for species X fails (non-numeric scores, validation failure, missing artifacts, runtime error), do **not** replace the answer with model B or species Y.
2. **No missing-to-absence.** Absence of a row is not a survey non-detection unless frame rules say so; otherwise use `UNKNOWN` or `INSUFFICIENT_DATA`.
3. **No silent fallback to prevalence** as a published answer when the selected model fails. Prevalence may be an internal baseline comparison only when explicitly labeled as such.
4. **Failed fit ≠ another region’s fit.** A Puerto Rico acceptance does not fill a Florida or USVI failure.
5. **Publication gate.** `INTERNAL_MODEL_OUTPUT` must not be promoted to `PUBLISHED_NOWCAST` / `PUBLISHED_FORECAST` because a failure left a hole on the globe. Prefer `UNKNOWN` / `WITHHELD`.
6. **Goliath / sensitive taxa.** Prefer `WITHHELD` or documented `no_estimate` over improvised maps.

## Mapping common failures

| Failure | Safe token |
|---|---|
| Model artifact missing | `UNAVAILABLE` |
| Non-numeric / divergent scores | `INSUFFICIENT_DATA` |
| Outside support mask | `UNSUPPORTED` |
| Rights / publication block | `WITHHELD` |
| Covariate older than allowed | `STALE` |
| Ambiguous or unevaluated label | `UNKNOWN` |

## Tests

Automated checks live in `tests/failure-recovery/test_safe_failure.py`. Audit notes in `audit/failure-recovery/`.
