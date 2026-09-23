# Ingestion pipeline spec

**Agent:** GEOSPATIAL_DATA_ENGINEER_AGENT  
**Date:** 2026-09-18  
**Status:** Design + empty stub only. **Do not ingest production datasets** until (1) founder locks a wedge, (2) DATA_RIGHTS_AND_PRIVACY_AGENT marks the source an approved class, (3) a human confirms commercial-use basis.

Stub: `pipeline_stub/ingest.py` — illustrates the loop, raises on real sources.

---

## 1. v1 shape (small team)

One Python package, one scheduler, one object-store prefix, one warehouse.

| Piece | v1 choice | Not yet |
|---|---|---|
| Runtime | Python 3.12, `pandas` / `geopandas` / `pyarrow` / `h3` / `pandera` | Spark, Beam |
| Scheduler | `cron` on a laptop or a $12/mo VM; GitHub Actions for public-source pulls if robots/TOS allow | Airflow, Dagster, Prefect Cloud |
| Transfer | Official HTTPS/API/bulk files only | Scraping, parallel unofficial harvest |
| Local object store | Filesystem `data/raw/` or MinIO | Multi-account data lake |
| Pilot object store | Cloudflare R2 or AWS S3, **one region** | Cross-region replication |
| Warehouse | SQLite (`fishai.sqlite`) until first partner; then Postgres 16 + PostGIS | Snowflake, BigQuery, Databricks |
| Analytics engine | DuckDB reading parquet | dbt Cloud, Flink |
| Secrets | env files / OS keychain; never in git | Vault cluster |

Jobs are CLI entry points:

```text
python -m fishai_ingest acquire  --source-id ... --wedge-id ...
python -m fishai_ingest profile  --ingestion-run-id ...
python -m fishai_ingest normalize --ingestion-run-id ...
python -m fishai_ingest validate --ingestion-run-id ...
python -m fishai_ingest promote  --ingestion-run-id ...
python -m fishai_ingest snapshot-features --issued-at ...   # later, after baseline exists
```

Until the package lives under `ingestion_pipeline/` at repo root (owned after this design is accepted), the stub in this folder is the contract.

---

## 2. Gates before `acquire`

All must be true:

1. `SourceMetadata.data_rights_status` ∈ {`APPROVED_OPEN_COMMERCIAL`, `APPROVED_WITH_ATTRIBUTION`, `APPROVED_INTERNAL_ONLY`, `APPROVED_PARTNER_CONSENT`} **or** a human recorded an exception in `legal_review_queue`.
2. `SourceMetadata.robots_and_tos_ok = true` with URL + access date.
3. `wedge_id` is set **or** the job is `mode=fixture` (synthetic rows only).
4. AOI GeoJSON exists for the active wedge; public jobs clip to it.
5. Rate-limit budget remaining (`max_requests_per_hour` on the source row).
6. Partner rows have a live `data_use_agreement_id` that includes the purpose (`model_training`, `product_delivery`, etc.).

If any gate fails: write a `ingestion_run` row with `status=blocked`, do not contact the source.

---

## 3. The six-step loop

Matches the platform spec. Every source, every run.

### Step 1 — Acquire

- Use the official documented API or file URL from `SourceMetadata`.
- Send a descriptive User-Agent (`FishAI-research/0.1 (+contact email UNRESOLVED)`).
- Respect `Retry-After`, 429, and published rate limits. No parallel workers against a source that forbids it.
- Write **immutable** L0:
  - object: `raw/{source_id}/{ingestion_run_id}/{filename}`
  - sidecar JSON: request URL, params, headers (redact auth), HTTP status, bytes, SHA-256, clock times.
- If the license **forbids raw retention**: store only the sidecar + checksum + retrieval instructions; set `raw_payload_reference` to `policy:no_retain`.
- Never log access tokens.

### Step 2 — Profile

Inspect without rewriting L0: schema, units, CRS, timezone, null rates, duplicates, geographic bounds vs AOI, range, taxonomy strings, latency vs `published_at`, update frequency, collection method, missingness.

Write `profile/{source_id}/{ingestion_run_id}.json` and a `source_quality` warehouse row.

### Step 3 — Normalize

- Map to the observation kernel (`canonical_data_model.md`).
- UTC + preserve source-local time.
- SI units + native pair.
- WoRMS accepted name via cached Aphia lookup (attribution required; no full DB redistrib).
- Point → H3 at the wedge feature res; also parent public cell.
- Point-in-polygon → `official_unit_id`.
- Attach `privacy_tier` from source default **and** `SensitiveLocationRule` (stricter wins).
- Strip lat/lon/geometry when writing PUBLIC/COARSENED files (separate materialization).
- Compute `transform_hash` (code + params) and `record_hash`.

### Step 4 — Validate

`pandera` (or equivalent) tests:

| Class | Examples |
|---|---|
| Schema / types | required kernel fields present |
| CRS | lon ∈ [-180,180], lat ∈ [-90,90]; AOI contains point or cell centroid |
| Time | `observed_at_utc ≤ published_at_utc` unless flagged; tz present or `TIME_TZ_UNKNOWN` |
| Range | SST, salinity, wave height physical bounds; catch ≥ 0 |
| Biology | taxon resolved or `TAXONOMY_UNRESOLVED`; life stage optional |
| Spatial | H3 valid; `h3_res` matches id; private GPS not in public file |
| Temporal continuity | expected cadence vs gaps → `STALE` / source_health |
| Duplicates | natural key |
| Units | mapped or `UNIT_UNMAPPED` |
| Freshness | `now - published_at` vs SLO |
| Rights | production L1 cannot contain `RIGHTS_BLOCKED` |
| Replay | `published_at` not null |

Failures **quarantine** the row (`quality_flags`, `layer=quarantine`). Do not drop.

### Step 5 — Document

Update (or emit patches for the owning agents): source catalog fields, lineage (`ingestion_run`), quality report, health report, fallback plan pointer, coverage counts by official unit. This agent does not overwrite DATA_DISCOVERY or DATA_RIGHTS files; it writes geospatial run logs here and warehouse rows.

### Step 6 — Decide

| Result | Action |
|---|---|
| Rights + QC pass | Promote to L1 `normalized/` |
| Useful but limited | Promote with flags + `observation_confidence=low` |
| Rights or hard QC fail | Remain in quarantine; `status=rejected` |
| Critical variable missing | Do not silently interpolate. Open a source-gap task |

Promotion is a copy to a new prefix + warehouse pointer, not an in-place edit of L0.

---

## 4. Partitioning and file layout

```text
s3://{bucket}/
  raw/{source_id}/{ingestion_run_id}/...
  quarantine/{entity}/{source_id}/year=YYYY/month=MM/*.parquet
  normalized/{privacy_tier}/{entity}/{source_id}/year=YYYY/month=MM/*.parquet
  raster/{source_id}/{product_version}/...   # COG / NetCDF / Zarr
  features/{wedge_id}/{model_version}/{feature_snapshot_id}.parquet
  predictions/{wedge_id}/year=YYYY/month=MM/*.parquet
  outcomes/{privacy_tier}/{entity}/{partner_id}/year=YYYY/*.parquet
  product/{wedge_id}/{delivery_date}/brief.json
```

GeoParquet 1.1 for vector L1 ([spec](https://geoparquet.org/releases/v1.1.0/)): lon/lat WGS84, `geometry` column, file bbox metadata. Snappy compression. Row-group size ~50–200 MB when data exists; v1 will be tiny.

---

## 5. Connector families (implement only after wedge lock)

Implement **one family at a time**, the one the locked wedge needs.

| Family | Typical sources | Format in | v1 connector notes |
|---|---|---|---|
| Raster env | Copernicus Marine, NOAA CoastWatch/ERDDAP | NetCDF / Zarr | Clip to AOI bbox **on request** if the API supports subset; do not pull global cubes |
| In-situ | NDBC, CO-OPS, NANOOS, NERACOOS | CSV/ERDDAP | Station allowlist inside AOI |
| Official polygons | WA DOH growing areas, NEFSC stat areas, LMA, PFMC area defs | shapefile/GeoJSON | Edition-versioned HabitatSpatialLayer |
| Advisories | WA DOH closures, state/NMFS season notices | GIS or HTML/API if official | `last_verified_at`; stale ≠ open |
| Taxonomy | WoRMS REST | JSON | Cache Aphia records used; CC-BY citation |
| Partner CSV/xlsx | farm log, trip form | tabular | DUA required; PRIVATE |
| Outcome form | web/email parse | JSON | 30-second schema |

Do **not** build AIS/VMS, social scrape, or global OBIS harvest in v1.

---

## 6. Idempotency and retries

- `ingestion_run_id` is the idempotency key for L0.
- Re-acquire of the same URL after change → new run (new raw object). Same checksum → mark `status=unchanged`, skip normalize.
- HTTP retries: exponential backoff, cap 5, honor `Retry-After`.
- Partial file writes use `.part` then atomic rename.

---

## 7. Quality tests as code (contract)

`pipeline_stub/checks.py` lists the test names. Implementation comes after wedge lock. A source cannot be `promoted` if:

- any row lacks kernel required fields
- public parquet contains lat/lon for privacy_tier PRIVATE/NEVER_PUBLISH sources
- `data_rights_status` is not an approved production class
- H3 id is invalid
- `published_at_utc` is null (cannot replay)

---

## 8. Scheduling sketch (after lock)

| Job | Cadence (typical) |
|---|---|
| Tides / NDBC / NWS | 1–6 h |
| SST / chl subset | 12–24 h |
| Wave forecast | 6–12 h |
| Official closures | 6 h + on-demand before a brief |
| Partner outcome pull | daily or on form submit |
| Feature snapshot + baseline brief | match decision frequency (daily or per trip) |
| Source health | every job |

No 24×7 streaming.

---

## 9. Fixture mode (allowed now)

```bash
python pipeline_stub/ingest.py --mode fixture --entity CatchEffortObservation
```

Writes **zero** network calls. Emits one synthetic row conforming to the JSON schema. Used to prove partition names and pandera hooks. Not a model training set.
