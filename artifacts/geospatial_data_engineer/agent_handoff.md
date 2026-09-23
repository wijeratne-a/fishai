# Agent handoff — GEOSPATIAL_DATA_ENGINEER_AGENT

**Date:** 2026-09-18  
**Agent id:** GEOSPATIAL_DATA_ENGINEER_AGENT  
**Project:** Ocean Intelligence Builder / FishAI  
**State:** Wedge UNRESOLVED. Design only. No production ingest. No model training.

---

## 1. Executive finding

Build **one** canonical observation model (WGS84 lon/lat exchange, UTC + source-local time, WoRMS AphiaIDs, H3 cells + official polygons, privacy-tiered files) and bind it later to a single wedge with an AOI clip. Do not fork three platforms.

**Recommended MVP:** local (then one-region) object store for immutable raw + GeoParquet/NetCDF, SQLite then Postgres+PostGIS for catalogs/forecasts, DuckDB for joins, Python cron jobs, pandera checks. Pilot cost on the order of **$30–80/month** after the first partner; **$0** while local. Partner outcomes are the labels; public rasters are covariates.

**Grid:** H3, with official units overlay (WA DOH growing areas; one PFMC salmon area; NEFSC statistical areas / LMAs). Feature defaults: res **8** (oyster), res **6** (Chinook/lobster). Public coarsen to parent res **5** or the official polygon. Area-normalize with `cell_area` when needed; H3 is not perfectly equal-area.

**Replay:** lock `feature_snapshot_id` + `source_data_cutoff_utc` + model/code hashes; join `published_at_utc <= cutoff`; never overwrite forecasts; corrected revisions only in an explicit `retrospective_corrected` eval lane. “Why was forecast X issued on date Y?” reads the snapshot, not live tables.

**Do not build yet:** global lake, Kafka/Spark/Airflow/K8s, feature store, Snowflake, AIS firehose, hardware, public spot maps, vector DB of locations, multi-region, training pipeline, or any bulk ingest before rights + wedge lock.

---

## 2. Evidence table

| Finding | Evidence | Confidence | Relevance |
|---|---|---|---|
| Three wedges share one kernel if privacy + official units are first-class | Platform spec §§9–12; operator units differ (growing area vs PFMC area vs NEFSC stat area) but all are polygons + points + rasters | High | Avoids overbuild |
| H3 res 6 ≈ “10 km cell” language; res 8 for farms | [H3 restable](https://h3geo.org/docs/core-library/restable/): res 6 ≈ 36.13 km², res 5 ≈ 252.90, res 8 ≈ 0.737 (accessed 2026-09-18) | High | Grid choice |
| WoRMS is the taxonomy authority; oyster accepted name is *Magallana gigas* 836033 | [836033](https://www.marinespecies.org/aphia.php?p=taxdetails&id=836033), synonym [140656](https://www.marinespecies.org/aphia.php?p=taxdetails&id=140656); Chinook [158075](https://marinespecies.org/aphia.php?p=taxdetails&id=158075); lobster [156134](https://www.marinespecies.org/aphia.php?p=taxdetails&id=156134); [terms](https://marinespecies.org/about.php) | High | Kernel taxon fields |
| WA ops geography is DOH growing areas, not H3 | [DOH growing areas](https://doh.wa.gov/community-and-environment/shellfish/growing-areas), [GIS](https://doh.wa.gov/data-and-statistical-reports/data-systems/geographic-information-system/downloadable-data-sets) | High | `official_unit_id` |
| Chinook charter geography should lock to one PFMC ocean salmon area | [Salmon FMP](https://www.pcouncil.org/documents/2022/12/pacific-coast-salmon-fmp.pdf/); KMZ/Fort Bragg/etc. in PFMC review docs | High | AOI clip |
| Lobster CPUE reporting geography is NEFSC statistical areas; regulation uses LMAs | [InPort 26262](https://www.fisheries.noaa.gov/inport/item/26262); [LMA map](https://www.fisheries.noaa.gov/resource/map/lobster-management-areas) | High | Overlay, not replace H3 |
| GeoParquet 1.1 lon/lat WGS84 (OGC:CRS84) | [geoparquet.org v1.1.0](https://geoparquet.org/releases/v1.1.0/) | High | Exchange format |
| Full WoRMS DB must not be redistributed | WoRMS about/terms (accessed 2026-09-18) | High | Cache lookups only |
| No founder storage region | `DATA_STORAGE_REGION` UNRESOLVED in project config (requirements agent) | High | Stay local until lock |
| HiveClaw threat model: don’t fake multi-tenant auth | `/Users/wijeratne/dev/HiveClaw/docs/research/threat-model.md` | Medium (analog) | SQLite now, RLS later |

---

## 3. Source / license table

This agent **did not ingest** sources. Status for engineering planning only; DATA_RIGHTS_AND_PRIVACY_AGENT owns the register.

| Source | Owner | URL | Accessed | License / restriction (as published; verify) | Use in this design |
|---|---|---|---|---|---|
| H3 resolution table | Uber H3 project | https://h3geo.org/docs/core-library/restable/ | 2026-09-18 | Apache-2.0 library; docs used as reference | Grid areas |
| GeoParquet 1.1 | GeoParquet community / OGC SWG | https://geoparquet.org/releases/v1.1.0/ | 2026-09-18 | Spec CC; format Apache Parquet | L1 vector |
| WoRMS | VLIZ / editors | https://marinespecies.org/about.php | 2026-09-18 | Cite CC-BY for content used; **no full DB redistrib** without agreement | Taxonomy cache |
| WA DOH growing areas / GIS | Washington State Department of Health | https://doh.wa.gov/community-and-environment/shellfish/growing-areas | 2026-09-18 | State GIS; commercial reuse = HUMAN LEGAL REVIEW | Official units, closures |
| PFMC Salmon FMP / NMFS WCR ocean salmon | PFMC / NOAA | https://www.pcouncil.org/documents/2022/12/pacific-coast-salmon-fmp.pdf/ ; https://www.fisheries.noaa.gov/west-coast/sustainable-fisheries/ocean-salmon-fisheries-west-coast | 2026-09-18 | U.S. Gov works generally public; confirm each file | Chinook AOI |
| NEFSC Statistical Areas | NOAA NEFSC | https://www.fisheries.noaa.gov/inport/item/26262 | 2026-09-18 | InPort metadata; GIS use constraints on dataset | Lobster AOI |
| GARFO Lobster Management Areas | NOAA GARFO | https://www.fisheries.noaa.gov/resource/map/lobster-management-areas | 2026-09-18 | Not a legal substitute for the CFR | Regulatory overlay |
| Copernicus Marine / NDBC / CO-OPS / NANOOS / NERACOOS | various | linked in `source_resilience_plan.md` | 2026-09-18 | **UNKNOWN / CONDITIONAL** until rights agent | Planned env connectors only |

Partner CSV/logbooks: `APPROVED_PARTNER_CONSENT` only after a signed DUA. No fixture row is real PII.

---

## 4. Confidence and limitations

| Item | Confidence | Limitation |
|---|---|---|
| Canonical kernel + five layers | High | Unproven in code beyond a fixture stub |
| H3 + official overlay | High | H3 area distortion; must use `cell_area` for densities |
| MVP stack cost | Medium | Cloud bills depend on failed subsetting (global pull) |
| Fallback tables | Medium | Primary/secondary URLs not license-cleared |
| Postgres RLS sketch | Medium | Not implemented; local SQLite has OS-user trust only |
| Chinook AphiaID 158075 | High (WoRMS 2026-09-18) | Other databases may show different IDs; WoRMS wins |
| No ingest | High | Coverage/latency numbers are not measured |

We did **not** verify Copernicus or NOAA product licenses for commercial forecast resale. Treat env connectors as blocked until the rights agent approves.

---

## 5. Recommended decision

1. **Accept this architecture** as the data foundation for whichever wedge the founder picks.
2. **Stay local + fixture-only** until wedge lock + approved sources.
3. After lock, implement **one** connector family (official polygons + one env subset + partner outcome form) — not the full catalog.
4. Prefer **R2 or S3 + Postgres** only when the first PRIVATE partner file cannot live on one encrypted laptop.
5. Quality/validation agent should assume as-of joins on `published_at_utc` and two eval lanes.
6. Product agent should assume briefs read **COARSENED/PUBLIC** files only.

---

## 6. Rejected alternatives

| Alternative | Why rejected |
|---|---|
| Three separate schemas/databases per wedge | Same kernel; binding is AOI + `wedge_id` |
| S2 or custom 10 km equal-area tile | More ops, weaker parent/child privacy coarsening |
| Snowflake / Databricks / Kafka / Airflow / K8s | Cost and complexity before a customer |
| Feature store (Feast) | Feature definitions are not stable |
| Global CMEMS/OBIS lake | Violates minimum-sufficient-data; budget risk |
| AIS as CPUE/abundance | Spec forbids; privacy and proxy misuse |
| Query-time-only privacy | Leak-prone; write-time materializations required |
| Hardware sensors | Partner exports and public buoys first |
| Iceberg/Delta time-travel | Immutable parquet snapshots suffice for v1 |
| Multi-tenant SaaS auth | No product yet; would need a real redesign |

---

## 7. Follow-up questions

1. Which wedge is locked (oyster WA / Chinook CA-OR / lobster GOM)?
2. `DATA_STORAGE_REGION` and whether PRIVATE data may leave the founder laptop?
3. Named design partners and DUA status?
4. Who is on-call for `source_health` alerts?
5. Rights status for WA DOH GIS, CMEMS, and NOAA raster commercial use?
6. For Chinook: which **one** PFMC management area?
7. For lobster: which statistical area(s) (511/512/513/514…)?
8. For oyster: which growing area(s) and whether lease polygons will ever be shared?

---

## 8. Artifacts generated

All under `/Users/wijeratne/dev/fishai/artifacts/geospatial_data_engineer/`:

| File | Role |
|---|---|
| `canonical_data_model.md` | Kernel, entities, H3 policy, WoRMS ids |
| `architecture_diagram.mmd` | Mermaid v1 flow |
| `ingestion_pipeline_spec.md` | Six-step loop, gates, layout |
| `storage_and_retention_plan.md` | Stack, cost, retention |
| `security_and_access_model.md` | Tiers, write-time coarsen, RLS |
| `as_of_replay_design.md` | Cutoff joins, explain command |
| `source_resilience_plan.md` | A/B/C, fallbacks, outage behavior |
| `agent_handoff.md` | This document |
| `schemas/_ObservationKernel.schema.json` | Shared JSON Schema |
| `schemas/CatchEffortObservation.schema.json` | Stub + fixture |
| `schemas/FarmOperationalOutcome.schema.json` | Stub + fixture |
| `schemas/ModelPrediction.schema.json` | Stub + fixture |
| `pipeline_stub/ingest.py` | Empty pipeline; fixture-only |

Did not write outside this folder. Did not ingest bulk data. Did not train models.

---

## 9. Should this work be red-teamed?

**Yes — targeted, not a full scientific red team of a model (there is no model).**

Priority leak checks for SCIENTIFIC_RED_TEAM / QUALITY:

- Temporal leakage via `published_at` vs `observed_at` on forecast rasters
- Public parquet accidentally containing lat/lon
- Explanations/embeddings reconstructing PRIVATE cells
- Evaluating historical briefs with later SST/closure revisions
- Treating AIS or chl as abundance
- Food-safety language on farm outcomes
- k-anonymity: publishing H3 cells with one partner

---

## 10. Suggested next experiment

**Smallest high-value experiment (after founder wedge lock, or using fixtures if still paused):**

Run `pipeline_stub/ingest.py --mode fixture` for the outcome entity of the likely wedge; add a pandera test that **fails** if `latitude` is present on a PUBLIC materialization; store one synthetic `ModelPrediction` + `feature_snapshot` and implement `explain --forecast-id` against that fixture.

Do **not** download CMEMS/NOAA cubes as the next step. The binding uncertainty and privacy tests are cheaper and more decision-relevant.

If the founder remains UNRESOLVED: keep this design frozen; do not specialize connectors.
