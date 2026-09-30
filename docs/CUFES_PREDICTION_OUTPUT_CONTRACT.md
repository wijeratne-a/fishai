# CUFES prediction output contract (PR #5)

**Status:** Column contract for gridded egg-encounter products (not adult distribution).

Each output row is keyed by **`cell_id`**, **`species`**, and **`valid_day`** (ISO date in UTC for the forcing valid time; `null` only in legacy tests).

## Required fields

| Column | Type | Constraints | Meaning |
| --- | --- | --- | --- |
| `p_encounter` | float or null | [0, 1] when finite | Mean egg encounter probability per reference volume \(V_\text{ref}\) |
| `p_lo90` | float or null | [0, 1] when finite | Lower bound of 90% interval on `p_encounter` (5th percentile of posterior draws) |
| `p_hi90` | float or null | [0, 1] when finite | Upper bound of 90% interval (95th percentile of draws) |
| `ood_level` | int | 0–3 | Max OOD severity across points aggregated into the cell (`classify_ood_level`) |
| `evidence_state` | string | one of five labels below | Issuance / forcing tier |
| `unknown_reason` | string or null | machine token when `evidence_state = UNKNOWN` | e.g. `insufficient_model_coverage`, `physics_cycle_fail`, `ood_level_ge_2` |
| `lead_days` | int | 0–3 | WCOFS forecast lead when `evidence_state = FORECAST`; **0** for hindcast/nowcast scoring rows. Resolved from WCOFS **`forecast_age_hours`** (valid time minus source run time), never from raw `lead_hours` or **`valid_offset_h`**. Nowcast when `forecast_age_hours <= 0` and `fallback_used` is false; else `ceil(forecast_age_hours / 24)`. Input Zarr may omit or NaN `lead_days` for nowcast steps; output always uses **0**, never **-1** or NaN. |
| `forecast_age_hours` | float or null | hours | WCOFS valid time minus **source** model run time (`ocean_time` − source run). Drives `lead_days` and 90% interval widening. |
| `source_run_time` | string or null | ISO-8601 UTC | Model run time **R** of the WCOFS file used for the step (e.g. R−48h under two-missed-cycle fallback). |
| `fallback_used` | bool | | True when the step used a prior-cycle file (`cycle_date != target` or explicit fallback). |
| `valid_time` | string or null | ISO-8601 UTC | Valid time of the forcing step (from `ocean_time` / Zarr `time`). |

**Interval policy:** posterior 90% width (`p_hi90 − p_lo90`) widens with **`forecast_age_hours`**, not with timeline index **`valid_offset_h`**.

## `evidence_state` labels (exactly one)

| Label | When |
| --- | --- |
| `HINDCAST_GLORYS` | Training or held-out scoring with audited GLORYS training covariates |
| `NOWCAST_UNVALIDATED` | Operational grid with current forcing, not yet validated against Tier-1 outcomes |
| `FORECAST` | Operational grid using forecast-cycle physics (`lead_days` 1–3) |
| `DEGRADED` | Physics cycle degraded; bounds widened per config around an unchanged `p_encounter`; `UNKNOWN` cells stay `UNKNOWN` |
| `UNKNOWN` | No interpretable egg encounter probability (OOD ≥ 2, coverage blanking, or physics FAIL) |

## Dry run marking

Rows produced by `scripts/models/cufes_pipeline_dry_run.R` or integration tests must set **`dry_run: true`** and write only under a caller-supplied temp directory. **Do not commit** dry-run CSV/JSON/RDS under `artifacts/models/` or `data/provenance/`.

JSON Schema: `configs/schemas/cufes_prediction_output.schema.json`.
