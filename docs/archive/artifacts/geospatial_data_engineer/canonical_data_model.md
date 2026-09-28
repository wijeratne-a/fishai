# Canonical data model

**Agent:** GEOSPATIAL_DATA_ENGINEER_AGENT  
**Date:** 2026-09-18  
**Project:** Ocean Intelligence Builder / FishAI  
**Status:** Design only. No production ingest. Wedge UNRESOLVED.  
**Binding rule:** One schema family for all three candidate wedges. Bind later by `wedge_id` + AOI clip + privacy policy, not by forking tables.

This document is the spatiotemporal observation contract. Storage, ingestion, security, and replay documents implement it.

---

## 1. Design principles

1. **One observation kernel, many typed payloads.** Every fact is an event with identity, time, space, taxon (if biological), measurement, effort, quality, rights, and lineage. Entity types add fields; they do not replace the kernel.
2. **Minimum sufficient data.** Add a source only if it improves prediction quality, lead time, actionability, coverage of a real risk, defensibility, credibility, or resilience. Do not ingest a global ocean lake.
3. **Partner-first.** Public rasters and official polygons are covariates. Ground truth is partner catch/effort, farm outcomes, or official survey indices — never inferred from AIS, chlorophyll, or habitat scores.
4. **Claims cannot exceed evidence.** Store `prediction_contract_category` A–E (direct count, survey index, effort-normalized catch, relative likelihood, unverified indicator). Public products default to C or D.
5. **Privacy is a write-time property.** Exact private locations never enter public tables, explanations, embeddings, or exports. Coarsen before those surfaces exist.
6. **Time machine.** Four timestamps plus versions. Historical evaluation uses only data published at issuance unless explicitly marked retrospective.
7. **Official geography is first-class.** H3 is the analytical index. WA growing areas, PFMC salmon areas, and NEFSC statistical areas remain the operational/regulatory units.

---

## 2. Conventions

| Topic | Canonical rule |
|---|---|
| Horizontal CRS (exchange) | WGS84 geographic, **lon/lat axis order**. GeoParquet default CRS is OGC:CRS84. Record `crs_epsg = 4326` in metadata. Do not rely on EPSG:4326 lat-first axis order. Spec: [GeoParquet 1.1.0](https://geoparquet.org/releases/v1.1.0/) (accessed 2026-09-18). |
| Local analysis CRS | Allowed only for distance/area jobs (e.g. EPSG:32610 WGS 84 / UTM 10N for WA/CA/OR; EPSG:32619 UTM 19N for GOM). Always convert back to 4326 for storage/exchange. |
| Time internal | UTC, ISO-8601 with `Z`. |
| Time preserved | `observed_at_source_local` + `source_timezone` (IANA, e.g. `America/Los_Angeles`, `America/New_York`). |
| Depth | Meters, positive downward from sea surface. Preserve native vertical datum in `notes` / `measurement_method`. |
| Taxonomy authority | **WoRMS AphiaID**. REST: [https://www.marinespecies.org/rest/](https://www.marinespecies.org/rest/). About/terms: [https://marinespecies.org/about.php](https://marinespecies.org/about.php) (accessed 2026-09-18). Cache lookups; **do not redistribute the entire WoRMS database**. |
| Spatial index | **H3** (see §3). Official polygons stored separately and joined. |
| Units | SI in canonical fields. Native value/unit preserved. |
| Identifiers | `event_id` UUIDv7 (time-sortable). `source_id` stable slug. `source_record_id` source-native, never rewritten. |
| Layers | `raw` → `normalized` → `feature` → `prediction` → `outcome` (plus `product` views). Version every layer. |

### 2.1 Candidate taxon seeds (not a locked wedge)

Store source names as-is. Normalize to accepted WoRMS names.

| Candidate | Source names likely | Accepted scientific name | AphiaID | URL |
|---|---|---|---|---|
| WA oyster farm ops | Pacific oyster, *Crassostrea gigas* | *Magallana gigas* | 836033 | [taxdetails 836033](https://www.marinespecies.org/aphia.php?p=taxdetails&id=836033) |
| synonym row | *Crassostrea gigas* | unaccepted → 836033 | 140656 | [taxdetails 140656](https://www.marinespecies.org/aphia.php?p=taxdetails&id=140656) |
| Chinook charter | Chinook, king salmon | *Oncorhynchus tshawytscha* | 158075 | [taxdetails 158075](https://marinespecies.org/aphia.php?p=taxdetails&id=158075) |
| GOM lobster | American lobster | *Homarus americanus* | 156134 | [taxdetails 156134](https://www.marinespecies.org/aphia.php?p=taxdetails&id=156134) |

Citation when using WoRMS: WoRMS Editorial Board (2026). World Register of Marine Species. Available from https://www.marinespecies.org at VLIZ. Accessed 2026-09-18. doi:10.14284/170.

---

## 3. Grid choice: H3 with official-polygon overlay

**Decision:** H3 as the single analytical grid. Documented area statistics: [H3 resolution table](https://h3geo.org/docs/core-library/restable/) (accessed 2026-09-18).

H3 is **not perfectly equal-area**. Cell area varies with position on the icosahedron. For mid-latitude U.S. coasts this is acceptable for ranking/relative products. For any rate that depends on area (density, CPUE per km²), compute `h3.cell_area(cell, unit="km^2")` per cell. Do not assume every cell at a resolution has the table-average area.

### 3.1 Why H3 (not S2, not a custom equal-area grid)

| Option | Verdict |
|---|---|
| **H3** | Hierarchical parent/child = privacy coarsening without a second index. Compact cell IDs. Python (`h3`) is one dependency. Average areas documented. |
| S2 | Weaker equal-area properties; less common in ecological ML; no win for a three-person team. |
| Custom equal-area (e.g. 10 km Lambert) | More honest area, but requires a private tiling registry, coastline clipping, and no parent/child. Defer. |
| Native raster only | Necessary for SST/chl/waves, but cannot unify catch, farms, and surveys. Sample rasters **onto** H3 at feature time. |

### 3.2 Resolution policy (one system, wedge-specific defaults)

Average hexagon area (km²): res 5 = 252.90; res 6 = 36.13; res 7 = 5.16; res 8 = 0.737; res 9 = 0.105.

The product language “broad 10 km cell” is closest to **H3 res 6** (mean spacing ~5.6 km, area ~36 km²). A 10×10 km square (~100 km²) sits between res 5 and 6. v1 uses res 6 for fish encounter features and res 5 for public coarsening when privacy requires it.

| Use | H3 res | Role |
|---|---|---|
| Internal env/feature join (fish encounter / CPUE) | **6** | Default feature `spatial_cell_id` for Chinook and lobster models |
| Internal env/feature join (estuary/farm) | **8** | Oyster growing-area / lease-adjacent cells |
| Public fish product | **6** or parent **5** | Never finer than the partner agreement |
| Public farm product | Growing-area polygon or res **7** | Never lease GPS |
| Sensitive / NEVER_PUBLISH | native GPS in PRIVATE store only | No public cell at any res that reconstitutes the point |

Always persist:

- `spatial_cell_id` (H3 index string at the row’s `h3_res`)
- `h3_res` (int)
- `spatial_cell_id_public` (parent at the public policy res, or null if NEVER_PUBLISH)
- `official_unit_id` + `official_unit_type` (see §3.3)

### 3.3 Official operational geographies (not replaced by H3)

H3 does not replace the units operators and regulators already use. Store these as `HabitatSpatialLayer` / `RegulatoryRestriction` polygons and attach `official_unit_id` on observations.

| Wedge candidate | Official unit | Authority / dataset | URL (accessed 2026-09-18) |
|---|---|---|---|
| Oyster × WA farms | Commercial shellfish **growing area** polygons; biotoxin closure zones | WA DOH | [Growing areas](https://doh.wa.gov/community-and-environment/shellfish/growing-areas); [GIS downloads](https://doh.wa.gov/data-and-statistical-reports/data-systems/geographic-information-system/downloadable-data-sets); [geo.wa.gov dataset](https://geo.wa.gov/datasets/WADOH::commercial-shellfish-growing-areas); [map viewer](https://fortress.wa.gov/doh/oswpviewer/index.html) |
| Chinook × CA/OR charter | PFMC ocean salmon management areas (e.g. KMZ Humbug Mountain–40°10′N; Fort Bragg 40°10′N–Point Arena; San Francisco; Monterey). **Lock one area when the wedge is chosen.** | PFMC / NMFS WCR | [Salmon FMP](https://www.pcouncil.org/documents/2022/12/pacific-coast-salmon-fmp.pdf/); [Ocean salmon fisheries](https://www.fisheries.noaa.gov/west-coast/sustainable-fisheries/ocean-salmon-fisheries-west-coast) |
| Lobster × GOM | NEFSC **statistical areas** (GOM examples 511, 512, 513, 514) for catch/CPUE reporting; **Lobster Management Areas** (LMA 1, etc.) for regulation | NEFSC / GARFO / ASMFC | [NEFSC Statistical Areas InPort 26262](https://www.fisheries.noaa.gov/inport/item/26262); [Lobster Management Areas](https://www.fisheries.noaa.gov/resource/map/lobster-management-areas) |

`official_unit_id` examples: `WA_DOH_GROWING_AREA:Samish Bay`, `PFMC_SALMON:KMZ_CA`, `NEFSC_STAT_AREA:513`, `LMA:1`.

---

## 4. Observation kernel (required on every raw/normalized observation)

Applies to environmental samples, in-situ sensors, occurrences, catch, farm outcomes, and similar event-like rows. Slowly changing layers (habitat polygons, agreements) use the same identity/lineage/rights fields with `valid_from_utc` / `valid_to_utc` instead of a single `observed_at_utc` when needed.

| Field | Type | Rule |
|---|---|---|
| `event_id` | UUIDv7 | Surrogate PK. Never reused. |
| `entity_type` | enum | One of the canonical types in §6. |
| `source_id` | string | FK to `SourceMetadata`. |
| `source_record_id` | string | Source-native id; required when the source has one. |
| `source_dataset_version` | string | Product/cycle/edition as published. |
| `source_owner` | string | Legal owner, not the portal. |
| `ingestion_run_id` | UUIDv7 | FK to ingestion run. |
| `observed_at_utc` | timestamptz | When the phenomenon occurred (or window start). |
| `observed_at_source_local` | string | Local wall time as reported. |
| `source_timezone` | string | IANA tz. |
| `published_at_utc` | timestamptz | When the source made this version available. **As-of join key.** |
| `ingested_at_utc` | timestamptz | When FishAI stored the raw bytes. |
| `revised_at_utc` | timestamptz | Source revision time; equals `published_at_utc` if first version. |
| `valid_from_utc` / `valid_to_utc` | timestamptz | For regulations, closures, agreements, habitat editions. |
| `latitude` / `longitude` | float | WGS84. Null if geometry-only (polygon layer) or stripped for PUBLIC rows. |
| `geometry` | WKB/WKT | Point, line, or polygon. Null on PUBLIC rows that only expose a cell. |
| `geometry_precision` | enum | `exact`, `rounded_0.01deg`, `cell`, `official_unit`, `unknown`. |
| `geographic_uncertainty_meters` | float | Null if unknown; never invent. |
| `depth_meters` | float | Positive down. |
| `spatial_cell_id` | string | H3 index. |
| `h3_res` | int | Resolution of `spatial_cell_id`. |
| `spatial_cell_id_public` | string | Coarsened parent or null. |
| `spatial_resolution` | string | Human/source resolution (e.g. `0.05deg`, `growing_area`). |
| `official_unit_id` / `official_unit_type` | string | §3.3. |
| `temporal_bin` | string | Optional (`hour`, `tide_cycle`, `calendar_day_local`). |
| `species_taxon_id` | string | `urn:lsid:marinespecies.org:taxname:{AphiaID}` or null. |
| `scientific_name_at_source` | string | Unmodified. |
| `accepted_scientific_name` | string | WoRMS accepted. |
| `taxonomic_authority` | string | Default `WoRMS`. |
| `life_stage` | string | As source; normalize later if a dossier requires it. |
| `measurement_type` | string | Controlled vocabulary per entity. |
| `measurement_value` | float | Canonical unit. |
| `measurement_unit` | string | UCUM-like (`Cel`, `m`, `1`, `{catch}/{trap.haul}`). |
| `measurement_value_native` / `measurement_unit_native` | string | Preserved. |
| `measurement_method` | string | Protocol / instrument / model name. |
| `sampling_effort_type` / `_value` / `_unit` | mixed | Required for catch/survey. |
| `detection_probability_if_known` | float | 0–1. |
| `observation_confidence` | enum | `high`, `medium`, `low`, `unknown`. |
| `quality_flags` | string[] | See §8. Never delete a flagged row silently. |
| `evidence_tier` | enum | `T1_direct`, `T2_operational`, `T3_remote_or_modeled`, `T4_unverified`. |
| `prediction_contract_category` | enum | `A`–`E` when the row is used as a label or published claim. |
| `provenance_URL` | string | Landing page or API URL used. |
| `license` | string | SPDX or source license name. |
| `attribution_text` | string | Required when license/source demands it. |
| `privacy_tier` | enum | `PUBLIC`, `COARSENED`, `RESTRICTED`, `PRIVATE`, `NEVER_PUBLISH`. |
| `data_rights_status` | enum | From DATA_RIGHTS_AND_PRIVACY_AGENT. Production ingest only if approved class. |
| `partner_id` | string | Null for public sources. |
| `data_use_agreement_id` | string | Required if partner or restricted. |
| `raw_payload_reference` | URI | Object-store key of immutable raw. |
| `transformation_version` | string | Semver of the normalizer. |
| `transform_hash` | string | SHA-256 of transform code + params. |
| `source_checksum` | string | SHA-256 of raw bytes (or declared source hash). |
| `record_hash` | string | SHA-256 of canonical normalized bytes. |
| `is_retrospective_revision` | bool | True if this row is a later correction. |
| `notes` | string | Free text; no secrets. |

Public/COARSENED materializations **drop** `latitude`, `longitude`, `geometry`, `raw_payload_reference` (if it would reveal a private file), and any partner-identifying fields.

---

## 5. Layer model

```
L0 raw          immutable bytes + request metadata     object store
L1 normalized   kernel + typed payload                 GeoParquet / Parquet
L2 feature      leak-safe, as-of aligned vectors       Parquet (partitioned by issued_at)
L3 prediction   append-only forecasts                  Parquet + warehouse index
L4 outcome      partner/user labels                    Parquet, PRIVATE by default
L5 product      coarsened briefs / GeoJSON / tables    warehouse views only
```

Rules:

- L0 is never overwritten. Re-pull = new `ingestion_run_id`.
- L1 is rebuilt from L0 with a new `transformation_version`; old L1 retained.
- L2 is immutable per `feature_snapshot_id`.
- L3 is append-only. A correction is a new `forecast_id` with `supersedes_forecast_id`.
- L4 cannot back-label an already issued L3 row except as evaluation.
- L5 is derived. If L5 disagrees with L3, L3 wins for audit.

Warehouse (SQLite → Postgres) holds catalogs, agreements, source health, forecast index, and small L5 tables — not raster cubes.

---

## 6. Canonical entity types

All share the kernel unless noted. Extra fields below are additive.

### 6.1 EnvironmentalRasterObservation

Gridded physics/biogeochemistry sampled to a cell or stored as a native grid file.

Extra: `variable_name`, `standard_name` (CF if available), `native_grid_id`, `native_x_y`, `forecast_horizon_hours` (0 = analysis), `product_type` (`observation`, `analysis`, `reanalysis`, `forecast`), `vertical_level`, `file_format` (`netcdf`, `zarr`, `cog`).

Native cubes stay NetCDF/Zarr/COG in L0/L1-raster. The observation table stores **cell samples used for features**, not every global pixel.

### 6.2 InSituMeasurement

Buoys, tide gauges, farm sondes (if permissioned), NWS/NDBC, NANOOS/NERACOOS stations.

Extra: `station_id`, `platform_type`, `qc_source_flag`, `sensor_id`, `calibration_ref`.

### 6.3 SpeciesOccurrence

Darwin Core-compatible occurrence (OBIS/GBIF/agency). **Not abundance.**

Extra: `occurrence_status` (`present`, `absent`), `basis_of_record`, `dataset_key`, `individual_count` (only if source provides a count with protocol), `dwc_event_id`.

Do not promote occurrences to CPUE or farm risk labels.

### 6.4 SurveyAbundanceIndex

Standardized survey or stock-assessment index (category B).

Extra: `survey_name`, `stratum_id`, `index_type`, `cv_or_se`, `method_citation`, `assessment_year`, `cannot_extrapolate_beyond` (text).

### 6.5 CatchEffortObservation

Charter encounter and lobster CPUE labels (category C). JSON Schema stub: `schemas/CatchEffortObservation.schema.json`.

Extra: `vessel_trip_id`, `gear_type`, `target_taxon_id`, `catch_count`, `catch_weight_kg`, `kept_count`, `released_count`, `cpue_value`, `cpue_unit`, `absence_reported` (bool), `reporting_channel`, `selection_bias_notes`.

Exact set/trap locations default `PRIVATE`. Public research uses `spatial_cell_id_public` only.

### 6.6 VesselTripObservation

Trip header: vessel/partner identity, port, trip start/end, intended area, weather constraint as reported.

Extra: `trip_id`, `partner_id`, `vessel_id_internal` (opaque), `dep_port`, `ret_port`, `intended_official_unit_id`, `public_track` (never a GPS track; optional coarsened cell sequence).

No AIS/VMS firehose in v1. Optional later as RESTRICTED partner data, never as abundance.

### 6.7 FarmOperationalOutcome

Oyster ops labels. JSON Schema stub: `schemas/FarmOperationalOutcome.schema.json`.

Extra: `farm_id`, `lease_id_internal`, `growing_area_id`, `outcome_type` (`stress_event`, `mortality_band`, `work_window_disruption`, `gear_loss`, `fouling`, `growth_observation`, `harvest_timing`, `other`), `severity` (`none`, `low`, `medium`, `high`), `action_taken`, `related_sensor_event_ids`.

**Not** a food-safety or legal-harvest field. Official closures live in `OfficialClosureOrAdvisory`.

### 6.8 AquacultureSensorObservation

Permissioned farm sensors. Subtype of in-situ with `farm_id`, `lease_id_internal`, `parameter`. Default `PRIVATE`.

No FishAI hardware in v1. Ingest vendor/partner exports only if rights-approved.

### 6.9 RegulatoryRestriction

Seasons, gear, size, MPA, quota-like constraints.

Extra: `jurisdiction`, `authority_name`, `regulation_id`, `restriction_type`, `species_scope`, `geometry` (official polygon), `legal_source_url`, `is_authoritative_copy` (always false — we cache for context; operator must follow the agency).

### 6.10 OfficialClosureOrAdvisory

Shellfish biotoxin/classification closures, fishery closures, HAB advisories.

Extra: `advisory_type`, `classification` (e.g. Approved/Conditional/Prohibited — as source), `effective_at_utc`, `expires_at_utc`, `last_verified_at_utc`, `authority_url`, `stale_after_hours`.

If `last_verified_at_utc` is older than `stale_after_hours`, product copy must say the closure feed is stale. Missing data ≠ open.

### 6.11 HabitatSpatialLayer

Bathymetry, substrate, growing-area polygons, MPA, lease footprints (permissioned).

Extra: `layer_name`, `native_crs`, `resolution_meters`, `edition_date`, `file_reference` (COG/GeoParquet). Slow-changing; version by edition.

### 6.12 MarketObservation

Landings, price, availability. High latency. Not a v1 primary label.

Extra: `market_variable`, `price_basis` (`dockside`, `wholesale`, `unknown`), `is_executable_now` (default false).

### 6.13 ModelFeatureSnapshot

Immutable feature vector(s) used to issue a forecast. JSON-ish columns allowed; values must be reconstructable.

Extra: `feature_snapshot_id`, `model_version`, `issued_at_utc`, `source_data_cutoff_utc`, `feature_schema_version`, `feature_values` (map), `feature_freshness` (map of source_id → published_at), `known_missing_inputs` (list), `leakage_check_passed` (bool).

No exact private coordinates inside `feature_values`. Use cell IDs, official units, and raster samples.

### 6.14 ModelPrediction

Append-only issued forecast. JSON Schema stub: `schemas/ModelPrediction.schema.json`.

Required forecast fields from the platform spec are columns, not an opaque blob: `forecast_id`, `project_id`, `wedge_id`, `species_scope`, `geographic_scope`, `spatial_cell_or_polygon`, `issued_at_utc`, `forecast_window_start_utc`, `forecast_window_end_utc`, `target_definition`, `prediction_value`, `prediction_unit`, `confidence_value`, `confidence_category`, `uncertainty_interval`, `model_version`, `training_data_cutoff_utc`, `feature_snapshot_id`, `source_data_cutoff_utc`, `feature_freshness_summary`, `known_missing_inputs`, `user_visible_explanation`, `user_visible_limitations`, `user_visible_action_options`, `source_attribution_bundle`, `regulatory_context_snapshot`, `privacy_policy_applied`, `delivery_channel`, `delivered_at_utc`, `prediction_contract_category`, `is_retrospective`.

`user_visible_explanation` is generated from allowed feature names and official units only.

### 6.15 ForecastEvaluation

Join of a locked prediction to later outcomes.

Extra: `evaluation_id`, `forecast_id`, `outcome_event_id`, `metric_name`, `metric_value`, `split_name` (`retrospective_asof`, `retrospective_corrected`, `prospective_pilot`), `evaluated_at_utc`.

`split_name = retrospective_corrected` is the only path that may use `published_at_utc > issued_at_utc`.

### 6.16 UserFeedbackOrOutcome

30-second partner form: did they act, what happened.

Extra: `feedback_id`, `forecast_id`, `acted` (bool), `action_type`, `outcome_summary`, `would_pay_signal` (optional, PRIVATE).

### 6.17 DataUseAgreement

Extra: `agreement_id`, `partner_id`, `version`, `allowed_purposes[]`, `training_allowed`, `commercial_derivatives_allowed`, `aggregation_benchmark_allowed`, `public_release_allowed`, `retention_days`, `revocation_process`, `signed_at_utc`, `expires_at_utc`, `document_uri`.

### 6.18 SourceMetadata

Catalog row matching discovery fields: coverage, license, fragility tier, primary/secondary/fallback, latency, evidence tier, last_verified_at. Fragility and outage live in `source_resilience_plan.md`.

### 6.19 PartnerMetadata

Extra: `partner_id`, `partner_type` (`oyster_farm`, `charter_captain`, `lobster_operator`, `other`), `home_official_unit_id`, `default_privacy_tier`, `outcome_form_version`, `status`.

### 6.20 SensitiveLocationRule

Extra: `rule_id`, `applies_to_taxon_id`, `applies_to_geometry`, `min_public_h3_res` (coarser = smaller res number), `min_delay_hours`, `forced_privacy_tier`, `reason` (`private_fishing_ground`, `farm_lease`, `protected_species`, `spawning_nursery`, `tribal_sovereignty`, `poaching_risk`, `vessel_safety`, `commercial_confidential`), `authority_or_agreement_id`.

Enforced at materialization, not as a UI filter.

---

## 7. Wedge binding (without three platforms)

```text
config/active_wedge.json   # UNRESOLVED until founder lock
  wedge_id
  taxon_id
  aoi_geojson              # clip all jobs
  official_unit_type
  feature_h3_res
  public_h3_res
  outcome_entity           # FarmOperationalOutcome | CatchEffortObservation
  forecast_horizon_hours
```

Same tables. Jobs take `--wedge-id`. Unbounded US-coast ingest is out of scope.

Until lock, engineers may load **tiny fixture rows** (synthetic) for schema tests. No bulk agency archives.

---

## 8. Quality flags (controlled)

| Flag | Meaning |
|---|---|
| `SCHEMA_FAIL` | Does not match canonical types. Quarantine. |
| `CRS_SUSPECT` | Lon/lat swapped or out of AOI. |
| `TIME_TZ_UNKNOWN` | Source time unzoned. |
| `TAXONOMY_UNRESOLVED` | WoRMS match failed. |
| `UNIT_UNMAPPED` | Native unit not converted. |
| `RANGE_IMPLAUSIBLE` | Physical/biological range test failed. |
| `STALE` | Past freshness SLO. |
| `DUPLICATE` | Same source_record_id + version. |
| `RIGHTS_BLOCKED` | Must not enter L1 production. |
| `PRIVACY_STRIPPED` | Lat/lon removed for this materialization. |
| `MISSING_EFFORT` | Catch without effort. |
| `CLOSURE_UNVERIFIED` | Advisory past `stale_after_hours`. |
| `SOURCE_OUTAGE_FALLBACK` | Row from secondary/fallback. |

Flag, do not silent-delete.

---

## 9. Identifiers and keys

| Key | Uniqueness |
|---|---|
| `event_id` | Global. |
| `(source_id, source_record_id, source_dataset_version, revised_at_utc)` | Natural key for L1. |
| `forecast_id` | Global; never recycled. |
| `feature_snapshot_id` | Global; 1:1 with an issuance (or shared by a batch issued together). |
| `ingestion_run_id` | Global. |

---

## 10. Tiny example (synthetic, not real farm data)

```json
{
  "event_id": "01800000-0000-7000-8000-000000000001",
  "entity_type": "CatchEffortObservation",
  "source_id": "partner.charter.example",
  "source_record_id": "trip-fixture-001-set-01",
  "observed_at_utc": "2026-09-17T18:40:00Z",
  "published_at_utc": "2026-09-17T23:10:00Z",
  "ingested_at_utc": "2026-09-18T01:00:00Z",
  "revised_at_utc": "2026-09-17T23:10:00Z",
  "spatial_cell_id": "86283082fffffff",
  "h3_res": 6,
  "spatial_cell_id_public": "85283083fffffff",
  "official_unit_id": "PFMC_SALMON:KMZ_CA",
  "species_taxon_id": "urn:lsid:marinespecies.org:taxname:158075",
  "accepted_scientific_name": "Oncorhynchus tshawytscha",
  "measurement_type": "cpue",
  "privacy_tier": "PRIVATE",
  "data_rights_status": "APPROVED_PARTNER_CONSENT",
  "latitude": null,
  "notes": "Fixture only. Exact coordinates omitted even in the example."
}
```

---

## 11. What this model deliberately omits

- A second “global species cube”
- Public vessel tracks
- Food-safety verdicts
- Exact abundance of wild stocks
- Hardware sensor schemas beyond partner export
- Embedding tables keyed by lat/lon
