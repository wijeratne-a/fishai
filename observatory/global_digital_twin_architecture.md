# Global Saltwater Life Observatory — digital twin architecture

**Agents:** OCEAN_DATA_ARCHITECTURE_AGENT · DATA_ASSIMILATION_AND_DIGITAL_TWIN_AGENT · SPATIOTEMPORAL_MODELING_AGENT · ECOSYSTEM_AND_FOOD_WEB_MODELING_AGENT  
**Date:** 2026-09-18  
**Project:** Global Saltwater Life Observatory (long-term) / FishAI (commercial wedge)  
**Status:** Design only. No training. No bulk ingest. No global lake. Wedge UNRESOLVED.

This document is the long-term **layer 0–10** contract for a depth-aware, evidence-typed digital twin of saltwater life. It **extends** `/Users/wijeratne/dev/fishai/artifacts/geospatial_data_engineer/` (canonical kernel, H3 + official polygons, privacy tiers, as-of replay, minimum-sufficient-data). Support tiers **T0–T6** follow `global_species_registry/support_tier_framework.md` (not a parallel factory vocabulary). It does **not** replace that stack and does not authorize production ingest.

---

## 0. Two-stack rule (non-negotiable)

| Stack | What it is | Where it runs | When it is built |
|---|---|---|---|
| **FishAI commercial wedge** | ONE species × ONE geography × ONE customer × ONE recurring decision | Local disk → one-region object store + SQLite/Postgres. Cost envelope **$0 now, ~$30–80/month** at first partner. | After founder lock + rights approval. |
| **Observatory (this design)** | Shared schemas, grids, evidence contract, and a **species model factory** that can host many taxa *later* | Same kernel and privacy model. Sparse cells only. No global cube materialization. | Architecture now. Implementation only as bounded slices, starting with **one** v0 twin. |

The commercial wedge is a **clip + bind** of this architecture (`wedge_id` + AOI + privacy policy), not a fork. The observatory is **not** a product UI, not a world map of “where the fish are,” and not a reason to pull Copernicus/OBIS globally.

**Inherited constraints (do not weaken):**

1. As-of joins on `published_at_utc` ≤ `source_data_cutoff_utc`; append-only forecasts; two eval lanes (`retrospective_asof` / `prospective_pilot` vs `retrospective_corrected`). See `artifacts/geospatial_data_engineer/as_of_replay_design.md`.
2. Privacy tiers `PUBLIC | COARSENED | RESTRICTED | PRIVATE | NEVER_PUBLISH`; write-time coarsening; no public GPS, AIS-as-abundance, or listed-species fine locations. See `security_and_access_model.md` and `artifacts/data_rights_and_privacy/privacy_and_sensitive_location_policy.md`.
3. **No global lake / no bulk ingest yet.** Connectors clip to an AOI. A job that would pull >20 GB of a global product is mis-scoped (`storage_and_retention_plan.md` §3).
4. Claims cannot exceed evidence. Prediction-contract categories **A–E** (`artifacts/scientific_red_team/prediction_contract.md`). SST, chlorophyll, and AIS are never abundance.
5. Taxonomy authority: **WoRMS AphiaID**. Cache used records; do not redistribute the full WoRMS database.

---

## 1. What a digital twin is allowed to mean here

The observatory posterior is **not** a census of animals in the ocean. It is a **time-stamped, spatially indexed, evidence-typed belief** about a *declared state variable*, with uncertainty that **grows** where observations are sparse.

```text
posterior species state
  = f( ecology prior,
       historical observations (as-of),
       current environmental / habitat state,
       new observations (as-of),
       ocean physics (licensed subset or particle set),
       movement / physiology biology,
       observation model (detectability, catchability, shedding, TS, effort),
       uncertainty )
```

If any term is missing, the posterior **must** say so (`known_missing_inputs`, lower `species_model_support_tier`, `confidence_category` ≠ high). Missing data is not filled with a smooth map.

**v0 does not compute a global posterior.** v0 estimates a **local, low-dimensional state** (see §8).

---

## 2. Layer model (0–10)

Geospatial-engineer layers L0–L5 remain the **storage** names. Observatory layers 0–10 are the **scientific** stack. Mapping:

| Observatory | Geospatial L* | Role |
|---|---|---|
| 0 Taxonomy | warehouse `taxon_cache` | Identity |
| 1 Raw obs | L0 | Immutable bytes |
| 2 Normalized obs | L1 | Kernel + typed payload |
| 3 Env / habitat state | L1 rasters + `HabitatSpatialLayer` | Physics/habitat cube (sparse, AOI-clipped) |
| 4 Species ecology knowledge | *new* (catalog, not a lake) | Priors, envelopes, food-web notes |
| 5 Model features | L2 | Leak-safe as-of vectors |
| 6 SDM / abundance / movement | *new* (model registry; empty until gates) | Estimators, not products |
| 7 Forecasts | L3 | Append-only issued state |
| 8 Uncertainty / evidence | columns on L3 + eval | Contract fields; not a separate fake score |
| 9 User outputs / API | L5 + research API | Evidence-typed; coarsened |
| 10 Feedback / updates | L4 + `UserFeedbackOrOutcome` | Labels and revision loops |

```text
L0 taxonomy
    ↓
L1 raw  →  L2 normalized  →  L3 env/habitat state
                ↓                    ↓
         L4 ecology knowledge  →  L5 features (as-of)
                                      ↓
                               L6 models (factory T0–T6)
                                      ↓
                               L7 forecasts (append-only)
                                      ↓
                               L8 uncertainty + evidence
                                      ↓
                               L9 API / briefs (privacy-tiered)
                                      ↓
                               L10 feedback → new L1/L2 (never silent rewrite of L7)
```

Rules carried forward: L0/L1 raw+normalized never overwrite; L2 snapshots immutable; L3/L7 predictions append-only; L10 cannot back-label an issued forecast except as evaluation; L9 is derived. If L9 disagrees with L7, L7 wins for audit.

### Layer 0 — Taxonomy

**State:** accepted scientific name, AphiaID, LSID, synonym graph (cached rows only), rank, marine flag, habitat flag if published by WoRMS.

**Authority:** WoRMS Editorial Board (2026), https://www.marinespecies.org doi:10.14284/170. REST cache of **used** AphiaIDs. CC-BY citation for content used. **No full DB dump.**

**Seed taxa (not a locked wedge):**

| Common | Accepted | AphiaID | Synonym to retain |
|---|---|---|---|
| Pacific oyster | *Magallana gigas* | 836033 | *Crassostrea gigas* 140656 |
| Chinook salmon | *Oncorhynchus tshawytscha* | 158075 | — |
| American lobster | *Homarus americanus* | 156134 | — |

**Does not include:** ITIS-as-competing-species, common-name-only rows as primary keys, ESA ESU identifiers as AphiaIDs (ESUs are management units stored on `RegulatoryRestriction` / stock tables, not as extra species).

Factory binding: every model run has `species_taxon_id = urn:lsid:marinespecies.org:taxname:{AphiaID}` plus optional `life_stage`, `stock_or_management_unit_id`.

### Layer 1 — Raw observations

Identical to geospatial L0: immutable object-store bytes + request sidecar (URL, params, status, SHA-256, clocks). Rights gate before `acquire`. Fixture mode only until wedge + rights lock.

**Additional observatory entity families (design; do not ingest):**

- eDNA sample packages (sequence metadata, not FASTQ lakes)
- Acoustic files / NASC tables (rights-heavy)
- Tag / telemetry messages (almost always `PRIVATE` / `RESTRICTED`)
- Lagrangian particle dumps from a **named** ocean-model experiment (subset, not global)

### Layer 2 — Normalized observations

Observation kernel from `canonical_data_model.md` §4 is **required**. Additive fields for the twin (nullable):

| Field | Purpose |
|---|---|
| `depth_meters` | Positive down (already in kernel) |
| `depth_bin_id` | From the registry in §4.2 |
| `vertical_datum` | e.g. `sea_surface`, `chart_datum`, `sigma_unknown` |
| `observation_process` | `presence_only`, `detection_nondetection`, `count`, `cpue`, `biomass_index`, `edna_conc`, `acoustic_nasc`, `tag_location`, `farm_outcome`, `sensor` |
| `detectability_or_catchability_notes` | Free text; no invented *p* |
| `spatial_uncertainty_class` | `point`, `cell`, `polygon`, `particle_cloud`, `unknown` |
| `species_model_support_tier_eligible` | Max factory tier this row can support (T0–T6), not a claim that we will use it |

Public/COARSENED materializations still **drop** lat/lon/geometry.

Entity types already defined stay. Observational extensions (same kernel):

- `EDNASampleObservation` — concentration or detection at a station/depth; **not** abundance.
- `AcousticIndexObservation` — NASC or PAM detection; Category B at best.
- `TagLocationObservation` — one animal; **not** a population.
- `LagrangianParticleSet` — model-generated; `product_type=model`; never a biological observation.

### Layer 3 — Environmental / habitat state

Eulerian, **sparse**, AOI-clipped fields on `(spatial_cell_id, depth_bin_id, time_bin_utc)` plus official polygons.

Variables are CF-ish (`sea_water_temperature`, `eastward_sea_water_velocity`, …) with `product_type ∈ {observation, analysis, reanalysis, forecast}` and full as-of timestamps.

**Not stored:** every global CMEMS pixel. **Stored:** cell samples used as features, native subset cubes under `raster/{source_id}/`, and polygon layers (growing areas, PFMC areas, NEFSC statistical areas, LMAs, MPAs).

Derived habitat layers (computed at feature time, versioned):

- mixed-layer depth (if the source provides it)
- thermal-band occupancy (e.g. volume of 8–12 °C water in a cell — a **habitat** metric, not Chinook count; Hinke et al. 2005 *MEPS* 304:207–220)
- intertidal emersion hours (oyster)
- bottom-contact temperature (lobster; SST is not a substitute — ASMFC 2025 peer review)

### Layer 4 — Species ecology knowledge

A **dossier store**, not a training corpus: thermal envelopes, depth envelopes, diel/seasonal notes, prey guilds, movement mode (`sessile`, `benthic_walk`, `pelagic_school`, `anadromous`, `planktonic_larva`), literature citations, **what cannot be predicted at the product horizon**.

Sources: MARINE_DOMAIN artifacts already written for the three candidates; FAO/NOAA species pages; peer-reviewed papers **cited, not copied**.

Food-web knowledge at this layer is **qualitative or semi-quantitative priors** (who eats whom, *Calanus* lag to lobster recruitment in years). It is not an Ecopath run and not a 48 h forecast.

`ecology_dossier_version` is hashed into `feature_snapshot_id` when used.

### Layer 5 — Model features

Identical contract to `ModelFeatureSnapshot`: `feature_snapshot_id`, `source_data_cutoff_utc`, `feature_freshness`, `known_missing_inputs`, `leakage_check_passed`.

**Observatory additions:**

- `depth_bin_id` / `habitat_layer_id`
- `observation_density` (`low|medium|high|none`) in the local neighborhood (definitions in uncertainty policy; observatory uses the same rule, not a neural net)
- `spatial_cell_area_km2` (H3 is not equal-area; always persist)
- `in_domain` envelope flags
- **No exact private coordinates** inside `feature_values`

### Layer 6 — SDM / abundance / movement models

A **factory**, not a zoo of unvalidated nets. Each taxon×AOI×target gets at most one *active* estimator per `target_definition`, versioned in a registry that is currently **empty**.

Allowed estimator families and when they are honest are in `ocean_model_comparison.md`. **v0 ships a baseline, not an SDM of global occurrence.**

Factory support tiers **T0–T6** (§7) cap what Layer 6 may emit.

### Layer 7 — Forecasts / issued twin state

`ModelPrediction` plus twin fields in §6.1. Append-only. Corrections = new `forecast_id` + `supersedes_forecast_id`.

A “nowcast” is still an issuance (`forecast_horizon_hours` may be 0) and still has a cutoff.

### Layer 8 — Uncertainty and evidence

Not a separate database. Required columns on every issued state (extends QUALITY `uncertainty_policy.md` and red-team 14-field contract):

See §6.1 (universal output contract). **If observation density is low, confidence cannot be High, and no calibrated-looking percentage is printed.** Empty cells are omitted or returned as `confidence_category=none` / HTTP 200 with `data_support=none` — never as a pretty interpolation.

### Layer 9 — User outputs / research API

Commercial path: coarsened email/SMS/PDF brief (product agents).  
Observatory path: research API in `API_specification.md` — evidence-typed JSON, not a full product, not anonymous S3 listing, not a public heatmap tile server.

### Layer 10 — Feedback and updates

Partner outcome forms, survey revisions, source corrections. New L1 rows. **Never UPDATE L7.** Re-eval only in the declared lane. Hierarchical farm/vessel intercepts may update on a schedule **after** cutoff rules; they do not rewrite history.

---

## 3. Spatial design

### 3.1 Documented index: H3 + official polygons + cell area

**Decision (extends geospatial engineer, does not reopen it):** **H3** is the analytical index. Official operational polygons remain first-class (`official_unit_id`). Persist `cell_area_km2` on every feature and prediction row because H3 is **not** perfectly equal-area ([H3 resolution table](https://h3geo.org/docs/core-library/restable/), accessed 2026-09-18).

| Use | H3 res (approx area) | Notes |
|---|---|---|
| Global catalog / public basin summaries | **4** (~1 770 km²) or **3** | Sparse: store only cells with data or an explicit T2 envelope request |
| Regional / EEZ research | **5** (~253 km²) | Default public coarsening for fish-like products |
| Fish encounter / CPUE features (wedge) | **6** (~36 km²) | Matches geospatial “~10 km language” closest |
| Estuary / farm internal | **8** (~0.74 km²) | Never public at this res for PRIVATE farms |
| Coastal high-res nest (research) | **8–9** inside AOI | Still clip; still privacy-tier |

**Rejected as v0 replacements:** S2, custom Lambert 10 km tiles, HEALPix (polar-honest but extra ops), storing only native rasters.

**Interchange (not analysis):** Darwin Core / OBIS **C-squares** and WGS84 lon/lat may appear on L1 for join to external catalogs. Analysis and privacy coarsening use H3 parent/child.

**Spatial uncertainty** is first-class: `geographic_uncertainty_meters`, `geometry_precision`, `spatial_uncertainty_class`, and a layer-3 `observation_density` raster (counts of independent samples per cell×depth×window). Density **must not** be inferred from vessel AIS.

### 3.2 Four geometric objects (all allowed; not all used in v0)

1. **Eulerian surface grid** — H3 cells.  
2. **Depth bins** — discrete registry (§4), attached to cells. This is the 3D representation.  
3. **Habitat / official polygons** — growing areas, PFMC salmon areas, NEFSC statistical areas, LMAs, MPAs, EEZs. Operators live here.  
4. **Lagrangian particles** — used when the state is a transported tracer (eDNA, larvae, HAB cells), not as a default store for animals.

v0 oyster twin uses (3) + a tiny subset of (1) + **intertidal/surface** bins from (2). No particle cloud.

### 3.3 Coastal high-resolution nesting

Same pattern as nested ROMS, without running ROMS:

- Outer: H3 res 4/5 climatology context (optional, sparse).  
- Inner: AOI clip at wedge res (6 or 8) + official polygons.  
- Features for issuance **only** sample the inner nest and licensed point sensors.

Do not downscale a 1/12° global SST product and call it lease-scale oyster body temperature (Raymond et al. 2022 *Ecology* https://doi.org/10.1002/ecy.3798: 2021 mortality was aerial heat × midday emersion).

---

## 4. Depth representation (decision)

### 4.1 Choice

**Hybrid discrete depth bins + habitat-relative layers, keyed by `(h3_cell, depth_bin_id, time)`. Not a global 3D unstructured mesh. Not terrain-following sigma for the planet.**

Rationale:

| Option | Verdict |
|---|---|
| Full 3D mesh (FVCOM/ROMS native) | Honest for one estuary model we do not run. Impossible as a global lake; rights and cost violate minimum-sufficient-data. |
| Fixed z-levels at CMEMS native (50–75 levels) | Fine as **source** native grid; too heavy as observatory state. |
| Sigma / s-coordinates globally | Coastal-correct, globally painful, extra vertical interpolation error. |
| **Discrete bins + habitat layers (chosen)** | Matches how animals and operators actually stratify (surface vs thermocline vs bottom vs air); cheap; can sit on top of any licensed cube; uncertainty is per-bin. |
| Thermal-isopycnal only | Excellent as a **derived** layer (Chinook 8–12 °C) but not a universal key. |

### 4.2 Depth-bin registry (v0 schema; populate only inside an AOI)

Positive meters downward from sea surface unless noted.

| `depth_bin_id` | Nominal range | Why it exists |
|---|---|---|
| `INTERTIDAL_AIR` | n/a (emersion) | Oyster heat; not an ocean z-level |
| `SURFACE_0_5` | 0–5 m | Skin SST, buoy intake, eDNA surface tows |
| `UPPER_5_25` | 5–25 m | Typical mixed-layer core on shelves |
| `SHELF_25_100` | 25–100 m | Recreational salmon depth band; thermocline often here |
| `SHELF_100_200` | 100–200 m | Shelf break |
| `MESO_200_500` | 200–500 m | Mesopelagic |
| `MESO_500_1000` | 500–1000 m | |
| `BATHY_1000_4000` | 1000–4000 m | Rarely in v0 products |
| `ABYSS_4000_PLUS` | ≥4000 m | Catalog only |
| `BOTTOM_CONTACT` | seafloor − 20 m to seafloor | Lobster / demersal; **derived from bathymetry**, not from SST |
| `MIXED_LAYER` | 0–MLD(t) | Time-varying derived; optional |
| `THERMAL_BAND:{lo}_{hi}C` | species-specific | Habitat volume; not abundance |

Every biological observation maps to one `depth_bin_id` (or `unknown`, which **blocks High confidence**).

**v0 oyster:** `INTERTIDAL_AIR` + `SURFACE_0_5` only.  
**Later lobster:** `BOTTOM_CONTACT` (+ depth band in fathoms as operator metadata).  
**Later Chinook:** `SURFACE_0_5` through `SHELF_25_100` plus `THERMAL_BAND:8_12C`. SST-only → Low/None (Hinke et al. 2005).

Do not interpolate empty bins to make a continuous profile.

---

## 5. Time design

Internal clock: **UTC**. Preserve `observed_at_source_local` + IANA `source_timezone`.

| Clock | Meaning | Twin role |
|---|---|---|
| `observed_at_utc` | Phenomenon time | Physics / label time |
| `published_at_utc` | Source made **this version** available | **As-of join** |
| `ingested_at_utc` | We stored L0 | Ops honesty: v1 requires ingested ≤ cutoff |
| `revised_at_utc` | Source revision | Lineage; old row remains |
| `valid_from_utc` / `valid_to_utc` | Regulations, habitat editions | Point-in-time polygons |
| `issued_at_utc` | We published a forecast/nowcast | Product time |
| `forecast_window_start/end_utc` | Validity interval of the state | |
| `source_data_cutoff_utc` | Max published_at allowed into the snapshot | Locked |
| `training_data_cutoff_utc` | Last label time in any fitted object | Locked |
| `feature_freshness` | Per-source last published_at | User-visible |
| `last_verified_at_utc` | Official closure/season feed | Stale ≠ open |

**Replay:** “Why was state X issued at Y?” reads `feature_snapshot_id` + model/code hashes, **not** live tables (`as_of_replay_design.md`). Observatory nowcasts obey the same rule.

**Freshness SLOs** (starting points; geospatial resilience plan): in-situ 6 h; waves 12 h; SST analysis 36 h; chlorophyll 48 h; official closures 6 h + re-verify before a farm brief. Breach → drop confidence, list `known_missing_inputs`, never silent interpolate.

---

## 6. Universal model output contract

Every Layer 6/7 object, including baselines and “nowcasts,” emits **all** of:

| Field | Rule |
|---|---|
| `predicted_state` | Named target; units; category A–E |
| `uncertainty` | Interval **or** `uncertainty_rationale` if not identifiable. No fake ±. |
| `data_support` | Observation density class; n of labels; strongest evidence tier |
| `extrapolation_risk` | Boolean + dimensions (space, depth, season, climate, management era, platform) |
| `model_type` | Family from `ocean_model_comparison.md` |
| `assumptions` | Short list (e.g. “catchability ∝ bottom T”; “occupancy ≠ abundance”) |
| `feature_freshness` | Per critical input |
| `validation` | Pointer to eval lane + `none` if never evaluated |
| `limitations` | User-visible; contract exclusions |
| `confidence_category` | `high\|medium\|low\|none` from the **rule table**, not a logit |
| `species_model_support_tier` | T0–T6 actually used (registry meanings) |
| `output_class` | `DIRECTLY OBSERVED` \| `REMOTELY DETECTED` \| `SURVEY-DERIVED` \| `TAG/TELEMETRY-DERIVED` \| `OPERATIONALLY OBSERVED` \| `MODEL-INFERRED` \| `FORECAST` \| `HYPOTHETICAL/RESEARCH MODE` \| `UNKNOWN/INSUFFICIENT DATA` |
| `privacy_policy_applied` | |
| `source_data_cutoff_utc` / `feature_snapshot_id` | Replay keys |

**Manufactured confidence is a defect:** if `data_support` is none/low, `confidence_category` cannot be high, `prediction_contract_category` cannot be A, and the API must not return a dense grid of filled values.

---

## 7. Species model factory — support tiers T0–T6

**Binding meanings** are in `global_species_registry/support_tier_framework.md`. This architecture **does not fork** them. A method (GAM, EnKF, particle filter) is not a tier.

**Three axes (never collapse):**

| Axis | Values | Grades |
|---|---|---|
| Observatory `support_tier` | **T0–T6** (this section) | Strongest **output class** allowed for taxon × life-stage × geography |
| Geospatial `evidence_tier` | `T1_direct` … `T4_unverified` | A **single observation row** |
| Commercial `prediction_contract_category` | **A–E** | Claim strength of a number (count / index / CPUE / habitat-risk / unverified indicator) |

A T6 observatory product cannot be justified by `T4_unverified` tweets. A commercial Category D stress brief is **not** automatically observatory T4 (short-horizon forecast) until time-forward or prospective validation exists. Registry example rows for oyster, Chinook, and lobster are **T2**; do not upgrade them because this twin is designed.

| Tier | Registry name | Factory may run | Forbidden |
|---|---|---|---|
| **T0** | Taxonomy only | Aphia lookup | Any map |
| **T1** | Historical occurrence | Effort-biased occurrence summaries | Current presence; capture-resolution hotspots |
| **T2** | Habitat suitability | Envelopes; habitat GAMs; oyster **B4 as stress/workability suitability** (Category D); Chinook thermal-band **habitat** (not bite) | “Animals are here now”; abundance; SST-as-animal |
| **T3** | Current condition estimate | Validated occupancy/index/relative condition at the claimed grain (VAST/sdmTMB, design-based survey, occupancy nowcast) | Calling a lagged assessment “now”; 48 h bite from SST |
| **T4** | Short-horizon forecast | B4/GAM/etc. **issued as** 24 h / 72 h / 7-day **after** prospective or time-forward tests at that horizon | Climatology labeled as a 48 h forecast; juvenile papers as adult encounter |
| **T5** | Direct observation / telemetry | Observation overlay; tag tracks; eDNA **detections as DNA**; acoustics as detected energy | Census from \(n_{\mathrm{tags}}\); public listed-species fine tracks |
| **T6** | Operational grade | T4 or T5 claim **plus** prospective skill vs baseline, calibrated uncertainty, rights, resilience, outcome feedback | Marketing T6 because the taxon is commercially important |

**Promotion:** written evidence URLs, rights, ecological-safety cap, held-out validation for T3+, red-team sign-off, human review for listed/harvested/culturally sensitive taxa (`support_tier_framework.md` §3).

**Iteration 1 fact:** no observatory taxon is T3–T6. Example CSV rows are T0–T2 only. **No DA method creates a tier by existing on paper.**

**FishAI candidates (scientific, not a founder lock):**

| Candidate | Registry tier (global example row) | Honest v0 prototype emission | Do not |
|---|---|---|---|
| Pacific oyster WA farm stress | **T2** | Bounded Category D **stress/workability suitability** as T2 / `HYPOTHETICAL/RESEARCH MODE` until validation; that **AOI×target** may later become T4 without upgrading the global row | Upgrade to T5 because farmers know planted stock (`PRIVATE` ops knowledge ≠ observatory T5) |
| Chinook CA/OR charter | **T2** | Thermal-habitat-with-depth as T2; **no** `/state` if SST-only | T5 public tracks; T3 from PFMC SAFE |
| American lobster GOM | **T2** | Seasonal survey **context** is not a next-trip T3 grid; partner CPUE is Category C **research** until validated | T3 from ASMFC biomass PDF; public string maps |

---

## 8. Recommended v0 twin (smallest scientifically honest slice)

### 8.1 Recommendation

**v0 observatory twin = Pacific oyster (*Magallana gigas*, AphiaID 836033) operational-stress / work-window state on named WA DOH growing areas in one estuary (Willapa Bay system recommended, not locked), 24–72 h horizon, Category D.**

This matches MARINE_DOMAIN scientific ranking, REQUIREMENTS recommended wedge W1, and SCIENTIFIC_RED_TEAM “safest bounded private pilot,” while remaining **RECOMMENDED not DECIDED**.

### 8.2 State actually estimated (and not)

**Estimated (per growing-area or permissioned lease, not per global H3 cell):**

1. Relative **operational stress / disruption indicator** over 24–72 h (heat-at-emersion, water T, DO/salinity **if sensed**, wave/wind workability). Category **D**.  
2. **Workability** of the next tidal work windows (tide × wind/wave). Operational, not biological.  
3. Accompanying **env state**: air T, predicted emersion hours, nearest water T, optional DO/S.  
4. **Observation density**, missing inputs, confidence, evidence badge.

**Not estimated:**

- Oyster abundance or biomass (planter already knows bag count).  
- Harvest legality, NSSP class, biotoxin, *Vibrio*, “safe to eat.”  
- Bay-wide wild set, larvae, OA as adult 72 h killer.  
- Any other taxon.  
- Global 3D posterior.

### 8.3 Why not the other attractive slices

| Slice | Why not v0 |
|---|---|
| Chinook 48 h encounter twin | Horizon poorly identified (Shelton et al. 2021 *Fish and Fisheries* https://doi.org/10.1111/faf.12530); ESA mix; vertical refuge; red-team blocker for public maps. |
| Lobster abundance twin | CPUE ≠ N; needs bottom T; privacy of strings; later **Category C** next-trip research (observatory T4 only after time-forward tests), not a 3D census. |
| Real-time marine mammal occupancy | `NEVER_PUBLISH` / delayed-coarsen policy; MMPA/ESA; scientific occupancy ≠ a public twin. |
| HAB / bloom twin (satellite + Lagrangian + eDNA) | Scientifically the **best** 3D/DA demo, but contaminates the oyster food-safety wall if mixed into W1, and is not the commercial decision. Defer as a **separate** research slice in a named basin, Category D bloom-*presence* not toxin. |
| Global multi-taxa cube | Contradicts no-lake, no-ingest, no manufactured confidence. |

### 8.4 How v0 uses layers

| Layer | v0 content |
|---|---|
| 0 | *M. gigas* 836033 + synonym 140656 |
| 1–2 | Fixture until rights; then tides, NWS/air, licensed in-situ, DOH polygons as **context**, partner outcomes `PRIVATE` |
| 3 | Estuary surface + emersion; no global z-levels |
| 4 | Existing marine_domain dossiers |
| 5 | As-of snapshots of tide×air×water×wave |
| 6 | **B4 expert-rule + B12 climatology** (`baseline_model_spec.md`). No ML. Observatory tier **T2** until time-forward tests exist; B12 must not be labeled a 48 h forecast. |
| 7–9 | Category D brief / research API |
| 10 | 30-second worked-tide / mortality-noticed form |

Depth: `INTERTIDAL_AIR` + `SURFACE_0_5`. Assimilation: **none sequential** (see `data_assimilation_design.md`).

---

## 9. Ecosystem / food-web position (honest)

Food-web and coupled physical–biological models (Ecopath/Ecosim, Atlantis, NPZD, size-spectrum) are **Layer 4 priors or later seasonal context**. They do **not** by themselves mint observatory T3 (current condition) or T4 (forecast).

- Oyster 72 h mortality is **not** a phytoplankton-carbon problem (chlorophyll is a growth/fattening covariate at weeks–months; Lowe/Ruesink Willapa work).  
- Lobster legal CPUE is **not** a same-week *Calanus* forecast (ASMFC 2025: recruitment lag of years).  
- Chinook 48 h encounter is **not** a NWFSC stoplight / JSOES juvenile product.

A coupled model may later constrain **habitat** (hypoxia volume, bloom transport). It must not be wired as fish counts.

---

## 10. What not to build (now, and not “while we wait”)

**Infrastructure**

- Global observation lake; Kafka/Spark/Airflow/K8s; Feast; Snowflake; Iceberg time-travel; vector DB of locations; multi-region; GPU mesh; public tile CDN of parquet.

**Science / models**

- All-taxa posteriors; PINNs / neural operators / spatiotemporal transformers as species abundance engines; unvalidated GNN hotspots; Ecopath-as-a-service; running a global GCM; particle-filter eDNA at planetary scale; real-time whale or listed-ESU maps.

**Products / claims**

- Public spot maps; AIS/GFW as biomass; food-safety or navigation advice; catch guarantees; silent forecast edits; interpolating empty cells to look complete.

**Process**

- Bulk ingest; model training; three wedges in parallel; treating this architecture as permission to download CMEMS/OBIS globally.

---

## 11. Storage and compute (observatory vs wedge)

Unchanged from geospatial storage plan for anything that actually runs:

- Now: `~/fishai-data/` + SQLite.  
- Pilot: one bucket, one region, Postgres+RLS when the first PRIVATE partner file cannot live on one laptop.  
- Observatory “global grid” is a **schema** plus sparse keys, not terabytes.

Native 3D cubes, if ever licensed, stay NetCDF/Zarr **subset** files. Warehouse holds catalogs, not voxels.

---

## 12. Confidence of this architecture

| Item | Confidence | Limitation |
|---|---|---|
| Layer mapping onto existing kernel / replay / privacy | High | Unproven in running code beyond geospatial fixture stub |
| H3 + bins as 3D representation | High for v0; medium as a global bio mesh | Animals follow isotherms/bottom, not z-bins; derived layers required |
| Oyster v0 as smallest honest twin | High scientifically; low commercially (no interviews) | Founder may lock W2/W3 |
| T0–T6 factory | High that meanings follow `support_tier_framework.md` | Easy to confuse with geospatial evidence T1–T4 |
| Observatory T6 (operational grade) | Low that this org will reach it | Needs prospective skill, rights, resilience, feedback — not a Kalman gain |

No datasets were ingested. No models were trained.
