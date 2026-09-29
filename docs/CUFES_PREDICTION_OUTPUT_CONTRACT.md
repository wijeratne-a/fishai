# CUFES prediction output contract (PR #5)

**Status:** Column contract for gridded egg-encounter products (not adult distribution).

Each output row is keyed by **`cell_id`**, **`species`**, and **`valid_day`** (ISO date in UTC for the forcing valid time; `null` only in legacy tests).

## Required fields

| Column | Type | Constraints | Meaning |
| --- | --- | --- | --- |
| `p_encounter` | float or null | [0, 1] when finite | Mean encounter probability per reference volume \(V_\text{ref}\) |
| `p_lo90` | float or null | [0, 1] when finite | Lower bound of 90% interval on `p_encounter` (5th percentile of posterior draws) |
| `p_hi90` | float or null | [0, 1] when finite | Upper bound of 90% interval (95th percentile of draws) |
| `ood_level` | int | 0–3 | Max OOD severity across points aggregated into the cell (`classify_ood_level`) |
| `evidence_state` | string | one of five labels below | Issuance / forcing tier |
| `unknown_reason` | string or null | machine token when `evidence_state = UNKNOWN` | e.g. `insufficient_model_coverage`, `physics_cycle_fail`, `ood_level_ge_2` |
| `lead_days` | int | 0–3 | WCOFS forecast lead when `evidence_state = FORECAST`; **0** for hindcast/nowcast scoring rows |

## `evidence_state` labels (exactly one)

| Label | When |
| --- | --- |
| `HINDCAST_GLORYS` | Training or held-out scoring with audited GLORYS training covariates |
| `NOWCAST_UNVALIDATED` | Operational grid with current forcing, not yet validated against Tier-1 outcomes |
| `FORECAST` | Operational grid using forecast-cycle physics (`lead_days` 1–3) |
| `DEGRADED` | Physics cycle degraded; intervals widened per config |
| `UNKNOWN` | No interpretable encounter probability (OOD ≥ 2, coverage blanking, or physics FAIL) |

## Dry run marking

Rows produced by `scripts/models/cufes_pipeline_dry_run.R` or integration tests must set **`dry_run: true`** and write only under a caller-supplied temp directory. **Do not commit** dry-run CSV/JSON/RDS under `artifacts/models/` or `data/provenance/`.

JSON Schema: `configs/schemas/cufes_prediction_output.schema.json`.
