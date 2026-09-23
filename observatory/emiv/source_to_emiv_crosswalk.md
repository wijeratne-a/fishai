# Source → EMIV crosswalk

**EMIV set:** v0.1  
**Registry:** [`emiv_registry.csv`](emiv_registry.csv) `v0.1-draft`  
**Date:** 2026-09-18  
**Ingest:** none. This is a mapping template plus worked examples, not an acquisition.

A source field is admitted only after [`acceptance_gate.md`](acceptance_gate.md). One primary EMIV per field. If the map is empty and there is no validated unique decision value → **defer/reject**.

Discovery catalog IDs below (e.g. `CMEMS-GLO-PHY-001-024`) are **citations of sibling metadata**, not a copy of that tree and not an ingest instruction.

---

## Template (copy a row per source field)

| Column | Required | Allowed values / notes |
| --- | --- | --- |
| `crosswalk_id` | yes | `CW-YYYYMMDD-###` |
| `source_id` | yes | Stable ID (product, station network, partner feed) |
| `source_name` | yes | Human name |
| `provider` | yes | Agency / firm |
| `official_URL` | yes | Landing page actually read |
| `source_field` | yes | Native variable name (`thetao`, `analysed_sst`, `WDIR`, …) |
| `measurand_in_words` | yes | What the field is, not what marketing hopes |
| `primary_emiv_id` | yes | Exactly one ID from the registry, or `NONE` |
| `secondary_emiv_ids` | no | Dependencies (`EMIV-QUA-*` typical) |
| `claim_class` | if biology or could be read as biology | See catalog C; else `n/a` |
| `role` | yes | `label` \| `covariate` \| `constraint` \| `quality` \| `proxy` |
| `model_use_status_inherited` | yes | Copy from registry; do not “upgrade” |
| `gate_outcome` | yes | `ADMIT` \| `ADMIT_PROXY` \| `DEFER` \| `REJECT` \| `REJECT_AS_ABUNDANCE_PROXY` |
| `privacy_tier` | yes | Policy tiers; native NEVER_PUBLISH ⇒ do not recommend public native grain |
| `rights_status` | yes | `YES` \| `NO` \| `CONDITIONAL` \| `UNKNOWN` for intended use |
| `as_of_ok` | yes | Can issuance-time availability be reconstructed? |
| `mismatch_notes` | yes if proxy | Skin vs bulk vs air; geography; horizon |
| `explicitly_not` | yes | One line |
| `unique_decision_value` | if `primary_emiv_id=NONE` | Named decision or `none` → defer/reject |
| `recorded_at` | yes | ISO date |

Do not add a column to a feature store from a filled-in hope. `UNKNOWN` is allowed in rights, skill, and RMSE.

---

## Example rows

### 1. Copernicus SST / global physics temperature — physics, not fish

| Field | Example A (satellite-class SST use) | Example A-fail (abundance) |
| --- | --- | --- |
| `crosswalk_id` | CW-20260918-001 | CW-20260918-001F |
| `source_id` | CMEMS-GLO-PHY-001-024 | CMEMS-GLO-PHY-001-024 |
| `source_name` | Copernicus Marine Global Ocean Physics Analysis and Forecast | (same) |
| `provider` | Copernicus Marine Service (Mercator Ocean) | (same) |
| `official_URL` | https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description | (same) |
| `source_field` | `thetao` (near-surface) or a CMEMS SST product field | `thetao` |
| `measurand_in_words` | Model/analysis seawater potential temperature on a ~1/12° 3-D grid | “Where the fish are” |
| `primary_emiv_id` | **EMIV-PHY-SST-001** if used as surface SST-class field; **EMIV-PHY-WTEMP-001** / **WTEMP-002** if explicitly in situ-equivalent bulk at stated depth | EMIV-BIO-SSTN-001 |
| `secondary_emiv_ids` | EMIV-QUA-FRESH-001 \| EMIV-QUA-QFLAG-001 \| EMIV-QUA-DCOV-001 | n/a |
| `claim_class` | n/a (physics) | invalid abundance |
| `role` | `proxy` (W1) or `covariate` | `label` or abundance covariate |
| `model_use_status_inherited` | W1_PROXY (SST) / CANDIDATE (depth T) | REJECTED_AS_ABUNDANCE_PROXY |
| `gate_outcome` | **ADMIT_PROXY** for W1 water-T gap fill with mismatch; **ADMIT** as PHY covariate for other wedges | **REJECT_AS_ABUNDANCE_PROXY** |
| `privacy_tier` | PUBLIC after licence; fusion inherits biology | n/a |
| `rights_status` | CONDITIONAL (Copernicus Marine licence retrieved 2026-09-18: commercial originals + attribution; still not a skill claim) | n/a |
| `as_of_ok` | Yes if forecast/analysis cycle time is stored; delayed reanalysis must not leak | n/a |
| `mismatch_notes` | Coarse for Willapa/Puget tidal creeks; skin/foundation vs bulk; **not aerial heat**; estuary bias UNKNOWN vs local OFS | Category error |
| `explicitly_not` | Not oyster abundance; not ops GT; not navigation | Not an EMIV of fish |
| `unique_decision_value` | n/a | none |
| `recorded_at` | 2026-09-18 | 2026-09-18 |

**MUR / GHRSST `analysed_sst`** (e.g. NOAA-MUR-SST-v4.1) maps the same way: primary **EMIV-PHY-SST-001**, W1_PROXY, fail if BIO-ABUND.

---

### 2. NDBC / ORCA in situ — sensors of EMIVs, not a species API

| Field | NDBC metocean | NANOOS ORCA (Hood Canal) |
| --- | --- | --- |
| `crosswalk_id` | CW-20260918-002 | CW-20260918-003 |
| `source_id` | NOAA-NDBC | NANOOS-ORCA (Twanoh / Hoodsport / Dabob as cataloged) |
| `source_name` | National Data Buoy Center | NANOOS ORCA profiling moorings |
| `provider` | NOAA NDBC | NANOOS / APL-UW (confirm owner on station page) |
| `official_URL` | https://www.ndbc.noaa.gov/ | https://nvs.nanoos.org/ (ORCA via NANOOS ERDDAP as cataloged) |
| `source_field` | `WDIR`/`WSPD`, `WVHT`, `ATMP`, `WTMP`, … | `temperature`, `salinity`, `oxygen` at depth bins (native names as published) |
| `measurand_in_words` | Point metocean: wind, waves, air T, bulk water T | In situ T, S, DO profiles in **Hood Canal** |
| `primary_emiv_id` | **EMIV-PHY-WIND-001**, **EMIV-PHY-WAVE-001**, **EMIV-PHY-ATEMP-001**, **EMIV-PHY-WTEMP-001** (one row per field) | **EMIV-PHY-WTEMP-001/002**, **EMIV-PHY-SALIN-001**, **EMIV-BGC-DOXY-001** |
| `secondary_emiv_ids` | EMIV-QUA-CALIB-001 \| EMIV-QUA-QFLAG-001 \| EMIV-QUA-FRESH-001 | same + EMIV-QUA-DCOV-001 |
| `claim_class` | n/a | n/a |
| `role` | `covariate` | `covariate` |
| `model_use_status_inherited` | W1_CORE for wind/waves/air T/water T | W1_CORE methods; **wrong geography if treated as Willapa** |
| `gate_outcome` | **ADMIT** as PHY/BGC | **ADMIT** as PHY/BGC for Hood Canal; **DEFER** as Willapa label/truth |
| `privacy_tier` | PUBLIC after licence | PUBLIC env; farm join PRIVATE |
| `rights_status` | CONDITIONAL / typical U.S. Gov — **UNKNOWN until rights agent for redistribution** | UNKNOWN commercial (discovery catalog) |
| `as_of_ok` | Yes if station timestamps kept | Yes if profile times kept |
| `mismatch_notes` | Point ≠ lease; fetch/microclimate UNKNOWN | **Hood Canal ORCA ≠ Willapa instrumentation** |
| `explicitly_not` | Not fish abundance; not navigation safety cert | Not Willapa farm GT; not DOH class |
| `unique_decision_value` | n/a | n/a |
| `recorded_at` | 2026-09-18 | 2026-09-18 |

If a product advertised “NDBC fish activity” or “ORCA oyster abundance,” that use is **REJECT_AS_ABUNDANCE_PROXY** even though the same bytes **ADMIT** as physics.

---

### 3. WA DOH closures — HUMAN PRESSURE / regulatory constraint, not biodiversity abundance, not ops mortality

| Field | Correct | Fail (ops GT) | Fail (abundance) |
| --- | --- | --- | --- |
| `crosswalk_id` | CW-20260918-004 | CW-20260918-004F1 | CW-20260918-004F2 |
| `source_id` | WDOH-GROWING-AREA-CLOSURES | (same) | (same) |
| `source_name` | WA DOH commercial shellfish growing-area classification / closures | | |
| `provider` | Washington State Department of Health | | |
| `official_URL` | https://doh.wa.gov/community-and-environment/shellfish/growing-areas | | |
| `source_field` | growing-area class / commercial closure status | used as `ops_disruption_72h` | used as oyster N |
| `measurand_in_words` | Official **harvest legally open?** status under NSSP | farm mortality/workability | abundance |
| `primary_emiv_id` | **EMIV-HUM-HARV-001** | EMIV-ECO-OPSOUT-001 (wrong) | EMIV-BIO-ABUND-001 (wrong) |
| `claim_class` | n/a (regulation) | OPERATIONALLY_OBSERVED (false) | DIRECT_COUNT (false) |
| `role` | **`constraint`** | `label` | abundance |
| `gate_outcome` | **ADMIT** as must-show constraint + authority link | **REJECT** | **REJECT** |
| `privacy_tier` | PUBLIC as the authority publishes | | |
| `rights_status` | UNKNOWN redistribution; do not scrape TOS-blocked portals; request export | | |
| `mismatch_notes` | Misses heat-kill and gear damage when harvest stays open | Label contamination; WAC 246-282-006 | Category error |
| `explicitly_not` | Not `y` for W1; not food-safety stamp by FishAI; not abundance | — | — |
| `recorded_at` | 2026-09-18 | 2026-09-18 | 2026-09-18 |

Related: `EMIV-BGC-FECAL-001` is the lab indicator **input** to NSSP, still not ops GT.

---

### 4. Partner farm mortality — BIODIVERSITY/ECOSYSTEM **ops outcome**

| Field | Value |
| --- | --- |
| `crosswalk_id` | CW-20260918-005 |
| `source_id` | PARTNER-FARM-OPS-LOGS |
| `source_name` | Permissioned grower logs (mortality, workability, intervention) |
| `provider` | Named farm under DUA (none onboarded 2026-09-18) |
| `official_URL` | Contract / DUA (not a public API) |
| `source_field` | `mortality` / `workability` / `intervention` as partner protocol |
| `measurand_in_words` | Operationally observed cultured-stock outcome on a lease |
| `primary_emiv_id` | **EMIV-ECO-OPSOUT-001** |
| `secondary_emiv_ids` | EMIV-HUM-CULT-001 \| EMIV-HUM-HAND-001 \| EMIV-QUA-FRESH-001 |
| `claim_class` | OPERATIONALLY_OBSERVED farm outcome (**not** wild DIRECT_COUNT, **not** CPUE, **not** suitability) |
| `role` | **`label`** (`ops_disruption_72h`) |
| `model_use_status_inherited` | W1_CORE |
| `gate_outcome` | **ADMIT** only after DUA; until then the label EMIV is **unidentified** (DEFER skill claims) |
| `privacy_tier` | **PRIVATE**; public microdata **NEVER_PUBLISH**; attributed disease **NEVER_PUBLISH** |
| `rights_status` | CONDITIONAL on contract; redistribution NO |
| `as_of_ok` | Required: log time vs issuance |
| `mismatch_notes` | Completeness UNKNOWN; bag-scale GPS not for public maps |
| `explicitly_not` | Not WA DOH class; not planted-stock sold as wild abundance; not NSSP |
| `unique_decision_value` | n/a (EMIV exists) |
| `recorded_at` | 2026-09-18 |

This is the **only** W1 ops-risk ground truth path in the registry.

---

### 5. AIS effort — HUMAN PRESSURE, not abundance

| Field | Correct | Fail |
| --- | --- | --- |
| `crosswalk_id` | CW-20260918-006 | CW-20260918-006F |
| `source_id` | AIS-LAWFUL-FEED (generic; GFW not used) | GFW / AIS density “fish map” |
| `source_name` | AIS vessel transmissions | Global Fishing Watch-class fishing hours |
| `provider` | Flag state / lawful AIS aggregator | GFW / similar |
| `official_URL` | Feed-specific | https://globalfishingwatch.org/ (example of the product class) |
| `source_field` | position / inferred activity | `fishing_hours` as N |
| `measurand_in_words` | Vessel activity (incomplete) | “fish abundance” |
| `primary_emiv_id` | **EMIV-HUM-AIS-001** (and/or EMIV-HUM-FISH-001, EMIV-HUM-SHIP-001) | EMIV-BIO-AISN-001 |
| `claim_class` | n/a (vessels) | invalid abundance |
| `role` | `covariate` (effort/pressure) if ever | abundance |
| `model_use_status_inherited` | **DEFERRED** (privacy, carriage gaps, NC risk) | REJECTED_AS_ABUNDANCE_PROXY |
| `gate_outcome` | **DEFER** for v0; **REJECT** if identity published or GFW ingested (NC) | **REJECT_AS_ABUNDANCE_PROXY** |
| `privacy_tier` | NEVER_PUBLISH identity, highliner routes, native reconstructed fishing | |
| `rights_status` | UNKNOWN per feed; GFW typically NC → do not ingest | |
| `mismatch_notes` | Class A/B; switch-off; most inshore Maine lobster boats have no AIS carriage duty | Category error |
| `explicitly_not` | Not Chinook/lobster/oyster abundance | — |
| `recorded_at` | 2026-09-18 | 2026-09-18 |

---

## Quick map (common ocean APIs)

| API / product class | Valid primary EMIV(s) | Fails the gate if used as |
| --- | --- | --- |
| Copernicus PHY SST / `thetao` | PHY-SST-001, PHY-WTEMP-001/002 | Fish/shellfish **abundance** |
| Copernicus BGC `chl` / `o2` | BGC-CHL-001, BGC-DOXY-001 (model) | Animal **abundance**; estuary DO truth |
| Copernicus WAV | PHY-WAVE-001 | Navigation cert; abundance |
| MUR / CoastWatch SST | PHY-SST-001 | Abundance; W1 headline; bottom T |
| VIIRS/OLCI ocean color | BGC-CHL-001, PHY-LIGHT-001 | Fish census |
| NDBC / CDIP | PHY-WIND/WAVE/ATEMP/WTEMP | Abundance |
| NANOOS ORCA / NERRS | PHY-WTEMP, PHY-SALIN, BGC-DOXY | Willapa GT; abundance |
| CO-OPS tides | PHY-TIDE-001, PHY-SEALV-001 | Independent moon-phase driver |
| USGS discharge | BGC-RUNOFF-001 | NSSP determination; mortality label |
| WCOFS / GoMOFS / RTOFS | PHY-WTEMP/SALIN/CURR (MODEL-INFERRED) | Abundance; navigation |
| GEBCO | PHY-BATHY-001 | Navigation |
| OBIS / GBIF | BIO-OCC-001 (compilation) | Real-time tracking; un-generalizing sensitive points |
| WA DOH closures | HUM-HARV-001 | Ops mortality; abundance |
| Partner farm logs | ECO-OPSOUT-001 | Public KPI map |
| AIS / GFW | HUM-AIS-001 / FISH-001 | Abundance; public identity |

---

## Empty-map rule

If a new API cannot fill `primary_emiv_id` and `unique_decision_value` is `none`, the gate outcome is **DEFER** (queue a new-EMIV proposal) or **REJECT** (no decision value). Do not park it under “other covariates.”
