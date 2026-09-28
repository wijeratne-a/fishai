# As-of / replay design

**Agent:** GEOSPATIAL_DATA_ENGINEER_AGENT  
**Date:** 2026-09-18  
**Goal:** The platform is a time machine. “Explain exactly why forecast X was issued on date Y” must be answerable from stored snapshots, not from live revised tables.

---

## 1. Time fields (every observation)

| Field | Meaning | Join role |
|---|---|---|
| `observed_at_utc` | When the ocean/farm/trip event happened | Label time, physics time |
| `published_at_utc` | When the source made **this version** available to us in principle | **As-of availability** |
| `ingested_at_utc` | When FishAI actually stored L0 | Operations; may be later than published |
| `revised_at_utc` | Source’s revision clock | Version lineage |
| `source_data_cutoff_utc` | Max `published_at_utc` allowed into a snapshot | Locked on the forecast |
| `valid_from_utc` / `valid_to_utc` | For regulations and habitat editions | Point-in-time polygon state |

Clock rule: internal UTC. `observed_at_source_local` is display/ops only.

**As-of predicate (default, prospective and honest retrospective):**

```text
row.published_at_utc <= snapshot.source_data_cutoff_utc
AND (row.revised_at_utc IS NULL OR row.revised_at_utc <= snapshot.source_data_cutoff_utc)
AND row.is_retrospective_revision = false
```

Plus: the row’s `ingested_at_utc` may be after cutoff only if we still would have had the **published** bytes by cutoff (rare). v1 is stricter:

```text
row.ingested_at_utc <= snapshot.source_data_cutoff_utc
```

so we never pretend we had a file we had not pulled. If a source was late, the snapshot records it in `known_missing_inputs`.

---

## 2. What gets locked at issuance

When a forecast is issued, write **one** `ModelFeatureSnapshot` and **one** `ModelPrediction` (or a batch sharing one snapshot). Persist:

- `forecast_id` (new UUID, never reused)
- `issued_at_utc`
- `forecast_window_*`
- `feature_snapshot_id` → parquet of feature values
- `model_version` + git commit / `transform_hash` / environment lock (`pip freeze` or `uv.lock` hash)
- `training_data_cutoff_utc`
- `source_data_cutoff_utc` (usually `issued_at_utc` minus a small safety margin)
- `feature_freshness_summary` (per `source_id`: last `published_at`)
- `known_missing_inputs`
- `privacy_policy_applied`
- `regulatory_context_snapshot` (closure/season rows as of cutoff)
- `user_visible_*` text **as delivered** (immutable)

**Never UPDATE** a prediction row. Corrections = new `forecast_id` with `supersedes_forecast_id`.

---

## 3. Two evaluation lanes (do not mix)

| Lane | `ForecastEvaluation.split_name` | Data allowed | Use |
|---|---|---|---|
| Honest as-of | `retrospective_asof` or `prospective_pilot` | `published_at <= issued_at` | “Did the product, as issued, beat baseline?” |
| Corrected-data research | `retrospective_corrected` | Later revisions allowed | Science only; **cannot** claim product skill |

Any metric used in a go/no-go or customer claim must come from the honest lane. Mixing lanes is a red-team blocker.

---

## 4. Replay command

Interface (CLI, later):

```text
python -m fishai_replay explain --forecast-id <uuid>
python -m fishai_replay rebuild-features --forecast-id <uuid> --verify-hash
```

**Explain path (no recompute):**

1. Load warehouse `forecast` by id.
2. Load L3 parquet row (the delivered payload).
3. Load L2 snapshot parquet.
4. Load `model_version` record (code hash, feature schema version, parameters).
5. Load `regulatory_context_snapshot`.
6. Emit a structured explanation:
   - target definition and contract category (C or D)
   - window
   - cells/official units (public ids only in user-facing text)
   - feature values and freshness
   - missing inputs
   - which fallbacks were active (`SOURCE_OUTAGE_FALLBACK`)
   - limitations text as originally delivered

**Rebuild path (integrity):**

1. From L0 + `transformation_version`, rebuild L1 at cutoff.
2. Rebuild features with the locked feature code.
3. Compare `record_hash` / snapshot hash. Mismatch → `REPLAY_DIVERGENCE` alert; do not silently patch L3.

v1 implements **explain** first (store enough). **Rebuild** is required before claiming fully reproducible science; it can wait until the first baseline exists.

---

## 5. Feature construction without leakage

- Features for time `t` may use observations with `published_at_utc <= t`.
- Rasters labeled “forecast issued at t for t+48h” are allowed as **inputs** if that forecast product was available at `t` (store its `published_at`). Do not use the verifying analysis from t+48h.
- Outcomes (`CatchEffortObservation`, `FarmOperationalOutcome`) with `observed_at` inside the forecast window are labels, never features for that issuance.
- Do not random-split neighboring cells into train/test (validation agent owns splits); the snapshot still records `split_name` when used in eval.

`leakage_check_passed` on the snapshot is a required boolean. The check is a unit test: max feature `published_at` ≤ cutoff.

---

## 6. Late data and revisions

| Event | Behavior |
|---|---|
| Source revises yesterday’s SST | New L1 row with new `revised_at`; old row remains. Snapshots keep pointing at the old version via cutoff. |
| Partner edits a trip form | New event version; evaluations already computed stay; optional re-eval as `retrospective_corrected` |
| We ingest a file two days late | `source_health` miss; forecasts issued in between listed the source as missing; we do **not** rewrite them |
| Official closure back-dated | Store both; product must show `last_verified_at` and not pretend earlier briefs contained it |

---

## 7. “Why was forecast X issued on date Y?” — payload

Minimum JSON (also stored next to L3):

```json
{
  "forecast_id": "...",
  "issued_at_utc": "2026-09-18T12:00:00Z",
  "source_data_cutoff_utc": "2026-09-18T11:00:00Z",
  "model_version": "baseline.seasonal.v0",
  "feature_snapshot_id": "...",
  "inputs_used": [
    {"source_id": "ndbc.46029", "published_at_utc": "2026-09-18T10:50:00Z", "role": "primary"}
  ],
  "inputs_missing": ["partner_outcomes_not_yet_collected"],
  "fallbacks_active": [],
  "privacy_policy_applied": "public_h3_parent_res5",
  "user_visible_explanation": "...",
  "is_retrospective": false
}
```

No exact private coordinates in this file if it can be delivered to a user or dropped into a ticket.

---

## 8. Warehouse tables (v1)

```text
forecast(forecast_id, wedge_id, issued_at_utc, window_start, window_end,
         model_version, feature_snapshot_id, source_data_cutoff_utc,
         privacy_policy_applied, delivery_channel, delivered_at_utc,
         supersedes_forecast_id, is_retrospective, object_uri)

feature_snapshot(feature_snapshot_id, issued_at_utc, schema_version,
                 object_uri, sha256, leakage_check_passed)

forecast_evaluation(evaluation_id, forecast_id, split_name, metric_name,
                    metric_value, evaluated_at_utc)
```

SQLite is enough until concurrent writers exist.

---

## 9. Explicit non-goals for v1

- Full lakehouse time-travel (Delta/Iceberg). Parquet + immutable keys is enough.
- Re-simulating vendor forecast models.
- Auto-rewriting customer emails when data revises.
- Using future closures to score past operational advice without the corrected-data flag.
