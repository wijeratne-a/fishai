# Storage and retention plan

**Agent:** GEOSPATIAL_DATA_ENGINEER_AGENT  
**Date:** 2026-09-18  
**Constraint:** `DATA_STORAGE_REGION` is UNRESOLVED. Until the founder sets it, v1 stays **local disk**. Pilot cloud uses **one** U.S. region chosen after wedge lock (us-west-2 if WA/CA/OR; us-east-1 if GOM). No multi-region lake.

---

## 1. Recommended MVP stack

| Layer | Local (now) | First partner (pilot) | Monthly cost (order of magnitude) |
|---|---|---|---|
| Object store | `~/fishai-data/` or MinIO in Docker | Cloudflare R2 **or** AWS S3 Standard, one bucket, versioning on | $0 local; R2 ~$1.50/100 GB-mo + cheap egress; S3 ~$2.30/100 GB-mo + request/egress |
| Warehouse | SQLite `fishai.sqlite` | Postgres 16 + PostGIS (Neon / RDS / a VM) | $0; managed PG ~$15–50 |
| Query | DuckDB over parquet | Same | $0 |
| Compute | Laptop | 2 vCPU VPS or GitHub Actions | $0–20 |
| Secrets / TLS | OS user + disk encryption | Bucket SSE + PG TLS | included |
| Backup | Encrypted Time Machine / restic to a second disk | Nightly `pg_dump` + S3 versioning; 30-day restic offsite | $0–10 |

**Pilot total: about $30–80 / month**, not a warehouse contract. Stay here until a paid pilot exists.

Swap SQLite → Postgres when the first PRIVATE partner table needs row-level grants or a second operator machine. Do not introduce a cloud warehouse “because analytics.”

---

## 2. What lives where

| Data | Store | Format | Why |
|---|---|---|---|
| Immutable raw pulls | Object store L0 | native bytes + JSON sidecar | Replay, checksum, license audit |
| Observations, catch, outcomes | Object store L1/L4 | GeoParquet / Parquet | Columnar, typed geometry, cheap |
| SST/chl/waves native grids | Object store | NetCDF or Zarr subset; COG if we publish a raster | Keep native multidimensional structure |
| Habitat / growing areas / stat areas | Object store + warehouse | GeoParquet + small PostGIS copy | Official units queried with forecasts |
| Source/partner/agreement/health/forecast index | Warehouse | SQLite/Postgres tables | Point lookups, RLS, product queries |
| Feature snapshots | Object store L2 | Parquet named by `feature_snapshot_id` | Immutable as-of |
| Predictions | Object store L3 + warehouse index | Parquet + `forecast` table | Append-only; briefs join the index |
| Tiny GeoJSON briefs | Object store L5 / email payload | GeoJSON | Interchange only, coarsened cells |
| WoRMS cache | Warehouse | JSON per AphiaID used | Not a copy of the full register |

Warehouse is **not** the system of record for rasters or bulk observations.

---

## 3. Volume envelope (one wedge, not global)

These are planning bounds, not ingest targets.

| Wedge | 12-month object store | Notes |
|---|---|---|
| WA oyster ops | 10–40 GB | Coastal SST/waves subset + farm outcomes (tiny) + growing-area GIS |
| CA/OR Chinook charter | 20–80 GB | Regional satellite/model subset + trip forms |
| GOM lobster CPUE | 20–80 GB | Same pattern; NERACOOS/NEFSC products |

If a connector would pull >20 GB for a single global product, the job is mis-scoped: subset or refuse.

---

## 4. Partitioning, indexing, clustering

**Object store keys:** see `ingestion_pipeline_spec.md` §4. Hive-style `year=/month=` on `observed_at_utc` (UTC). Additional partition: `privacy_tier` so PUBLIC jobs cannot list PRIVATE prefixes.

**Parquet:** sort by `official_unit_id`, `spatial_cell_id`, `observed_at_utc`. Dictionary-encode `source_id`, `privacy_tier`, taxon ids.

**SQLite/Postgres indexes:**

```text
source_metadata(source_id) PK
ingestion_run(ingestion_run_id) PK
forecast(forecast_id) PK
forecast(issued_at_utc)
forecast(wedge_id, forecast_window_start_utc)
feature_snapshot(feature_snapshot_id) PK
sensitive_location_rule(rule_id)
data_use_agreement(partner_id, version)
source_health(source_id, checked_at_utc)
```

PostGIS: GIST on official-unit geometries only (small). Do not GIST every catch point in a public schema.

---

## 5. Retention

| Class | Retain | Delete / tombstone |
|---|---|---|
| L0 raw (rights allow) | Life of project + 1 year after last forecast that used it | If license forbids retention: sidecar only |
| L1 normalized | All versions used in any issued forecast; otherwise current + previous `transformation_version` | Rebuildable from L0 |
| L2 feature snapshots | **Forever** for issued forecasts | Never delete a snapshot referenced by L3 |
| L3 predictions | Forever (append-only) | Supercede, do not UPDATE |
| L4 partner outcomes | Agreement `retention_days`; default 3 years or until revocation | Cryptographic delete + warehouse tombstone; keep `event_id` for audit (“record removed”) |
| L5 briefs | 2 years or match marketing/compliance later | Rebuildable from L3 |
| Logs / health | 2 years | |
| WoRMS cache | Refresh 90 days; keep the Aphia JSON used at transform time next to `transform_hash` | Do not dump full WoRMS |
| Quarantine | 90 days after resolution | |

Revocation: partner DUA wins. After revoke, PRIVATE objects are deleted or re-encrypted with a destroyed key; forecasts already delivered stay in L3 but must not re-export partner GPS or performance.

---

## 6. Backup and restore

**Local:** encrypted restic or Time Machine; test restore once before first partner file.

**Pilot:**

1. S3/R2 versioning + MFA-delete off until two operators exist (avoid lockout).
2. Nightly `pg_dump` to `s3://.../backups/postgres/YYYYMMDD.dump`.
3. Monthly restore drill: spin SQLite/PG from backup, run `explain forecast` on one fixture id.
4. Bucket default encryption (SSE-S3 or SSE-C for PRIVATE prefix).
5. Separate backup credentials from ingest credentials.

Do not back up PRIVATE catch GPS into a founder laptop Photos/iCloud folder.

---

## 7. Lifecycle and cost controls

- Object lifecycle: `raw/` after 90 days → Infrequent Access if on S3; stay Standard on R2 (pricing is flat).
- Abort incomplete multipart uploads after 7 days.
- Requester-pays and public-read: **off**. PUBLIC product files are still in a private bucket and copied out through a job that strips secrets.
- CloudTrail / R2 logs on the PRIVATE prefix.
- Alert if monthly storage exceeds 100 GB (means a connector went global).

---

## 8. Region and residency

Until `DATA_STORAGE_REGION` is set:

- Default **local only** for PRIVATE data.
- Public fixture parquet may sit in-repo only if it contains **no** real coordinates or partner names (the JSON schema examples are the pattern).

After lock, put compute in the same region as the bucket. No EU/US dual-write.

---

## 9. What not to provision yet

Managed Kafka, Snowflake, a second “cold lake” account, GPU object cache, ElasticSearch/OpenSearch for observations, a vector database, CDN in front of parquet, multi-AZ Postgres HA. All of that is later-company infrastructure, not a one-wedge MVP.
