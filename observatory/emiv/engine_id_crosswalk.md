# Engine ID crosswalk — stub/slug → registry

**Date:** 2026-09-18  
**Registry:** [`emiv_registry.csv`](emiv_registry.csv) · set `v0.1` · artifact **`v0.1-draft`** (84 rows)  
**This pass:** Thin registrar add of solar + tissue/bag T. No ingest. No training. No science rewrite. No wedge lock. `STATE_10` unchanged.

**Confirmations (binding):**

- WA DOH / NSSP harvest-open / closure is **`EMIV-HUM-HARV-001` — constraint, not the ops label** (`EMIV-ECO-OPSOUT-001`).
- Satellite SST is **`EMIV-PHY-SST-001` — `W1_PROXY`**, not bulk water T, not tissue T, not abundance.

W1_CORE (10): `EMIV-PHY-ATEMP-001`, `EMIV-PHY-TIDE-001`, `EMIV-PHY-EMERS-001`, `EMIV-PHY-SOLAR-001`, `EMIV-PHY-WTEMP-001`, `EMIV-BGC-DOXY-001`, `EMIV-PHY-SALIN-001`, `EMIV-PHY-WAVE-001`, `EMIV-PHY-WIND-001`, `EMIV-ECO-OPSOUT-001`.

`EMIV-PHY-TISST-001` is **CANDIDATE** with high decision value; **W1_CORE when a partner sensor exists**. Not SST. Not bulk water T.

Graph URN `@id`s (`urn:fishai:observatory:kg:emiv/air_temperature`) and causal `node_id`s (`ENV.air_temperature`) are **stable keys**, not recycled. Only `emiv_id` / `emiv_ids[]` / anomaly `variable` slots were remapped.

---

## 1. Observation planner (`EMIV-CAT-SHORT-###` stubs)

| Old stub | Registry id | Notes |
|---|---|---|
| `EMIV-ENV-AIR-001` | `EMIV-PHY-ATEMP-001` | W1_CORE |
| `EMIV-ENV-TIDE-001` | `EMIV-PHY-TIDE-001` + `EMIV-PHY-EMERS-001` | Stub conflated tide and emersion |
| `EMIV-ENV-WAT-001` | `EMIV-PHY-WTEMP-001` | Bulk in situ, not SST |
| `EMIV-ENV-SST-001` | `EMIV-PHY-SST-001` | PROXY |
| `EMIV-ENV-SOL-001` | `EMIV-PHY-SOLAR-001` | W1_CORE; not chlorophyll |
| `EMIV-ENV-BAG-001` | `EMIV-PHY-TISST-001` | CANDIDATE; W1_CORE when partner sensor exists |
| `EMIV-ENV-DO-001` | `EMIV-BGC-DOXY-001` | Listed in schema; unused in fixture CSV |
| `EMIV-ENV-SAL-001` | `EMIV-PHY-SALIN-001` | |
| `EMIV-ENV-WAV-001` | `EMIV-PHY-WIND-001` + `EMIV-PHY-WAVE-001` | Stub conflated wind and waves |
| `EMIV-OUT-OPS-001` | `EMIV-ECO-OPSOUT-001` | W1_CORE label |
| `EMIV-OUT-WRK-001` | `EMIV-ECO-OPSOUT-001` | Workability is a facet of ops outcome (deduped) |
| `EMIV-OUT-CUL-001` | `EMIV-HUM-CULT-001` | Required metadata, not separately W1_CORE |
| `EMIV-POL-NSSP-001` | `EMIV-HUM-HARV-001` | Constraint, never \(y\) |
| `EMIV-DET-PDE-001` | `EMIV-QUA-PDETECT-001` | scoring_spec only |
| `EMIV-DET-OCC-001` (K04 eDNA rec only) | `EMIV-BIO-EDNA-001` | Rec remains KILLED (DNA ≠ abundance) |

**Files touched:** `observation_planner/README.md`, `recommendation_schema.md`, `scoring_spec.md`, `architecture.md`, `agent_handoff.md`, `w1_willapa_oyster_plan.md`, `fixture_recommendations.csv`.

---

## 2. Change detection (variable tokens in `related_env_anomalies`)

Fixture record keys `EMIV-FIX-*` are **not** catalog IDs and were left in place.

CSV encoding: `env_anomaly_id|emiv_id|sign|grain`.

| Old `variable` token | Registry id | Events |
|---|---|---|
| `air_temperature` | `EMIV-PHY-ATEMP-001` | FIX-CD-2021-001 |
| `emersion_hours` | `EMIV-PHY-EMERS-001` | FIX-CD-2021-001 |
| `named_HAB_cell_count` | `EMIV-ECO-HAB-001` | FIX-CD-2019-002 |
| `dissolved_oxygen` | `EMIV-BGC-DOXY-001` | FIX-CD-2026-004 (wrong-basin ORCA; still DATA_GAP) |
| `water_temperature` on SST-only fixtures | `EMIV-PHY-SST-001` | FIX-CD-FIXT-006, FIX-CD-RES-009 (token had said water T; finding was always skin SST) |
| `bottom_temperature` | `EMIV-PHY-WTEMP-003` | FIX-CD-RES-008, FIX-CD-RES-010 |

**Files touched:** `change_detection/README.md`, `event_schema.md`, `agent_handoff.md`, `w1_oyster_examples.md`, `fixture_events.csv`.

---

## 3. Knowledge graph (`emiv:*` slugs)

| Old slug | Registry id |
|---|---|
| `emiv:air_temperature` | `EMIV-PHY-ATEMP-001` |
| `emiv:emersion_duration` | `EMIV-PHY-EMERS-001` |
| `emiv:water_temperature` | `EMIV-PHY-WTEMP-001` |
| `emiv:dissolved_oxygen` | `EMIV-BGC-DOXY-001` |
| `emiv:salinity` | `EMIV-PHY-SALIN-001` |
| `emiv:wind_wave` | `EMIV-PHY-WIND-001\|EMIV-PHY-WAVE-001` (one graph node, two registry rows) |
| `emiv:satellite_sst` | `EMIV-PHY-SST-001` |
| `emiv:chlorophyll_a` | `EMIV-BGC-CHL-001` |
| `emiv:omega_aragonite` | `EMIV-BGC-OMEGA-001` |
| `emiv:fecal_coliform` | `EMIV-BGC-FECAL-001` |
| `emiv:bottom_temperature` | `EMIV-PHY-WTEMP-003` |
| `emiv:hab_cell_density_animal_stress` | `EMIV-ECO-HAB-001` |

No separate KG node for tide stage; use `EMIV-PHY-TIDE-001` from the registry. Harvest toxin / DOH overlay remains **RegulatoryConstraint** + `EMIV-HUM-HARV-001`, not `EMIV-ECO-HAB-001`.

**Files touched:** `knowledge_graph/README.md`, `ontology.md`, `query_library.md`, `conflict_detection.md`, `agent_handoff.md`, `edge_metadata_schema.json`, `example_graph_gigas.jsonld`.

---

## 4. Causal ecology (`ENV.*` / `HAB.*` / `OUT.*` node_ids)

`node_id` strings were **not renamed**. Bindings added in `w1_magallana_gigas_causal_graph.md` §1.0.

| node_id | Registry id |
|---|---|
| `ENV.air_temperature` | `EMIV-PHY-ATEMP-001` |
| `ENV.water_temperature_in_situ` | `EMIV-PHY-WTEMP-001` |
| `ENV.satellite_sst` | `EMIV-PHY-SST-001` |
| `ENV.solar_irradiance` | `EMIV-PHY-SOLAR-001` |
| `ENV.solar_geometry_timing` | `EMIV-PHY-SOLAR-001` |
| `ENV.precipitation_discharge` | `EMIV-BGC-RUNOFF-001` |
| `ENV.wind_waves` | `EMIV-PHY-WIND-001` \| `EMIV-PHY-WAVE-001` |
| `ENV.astronomical_tide` | `EMIV-PHY-TIDE-001` |
| `ENV.pH_omega` | `EMIV-BGC-OMEGA-001` (related `EMIV-BGC-PH-001`) |
| `ENV.nutrients` | `EMIV-BGC-NUTR-001` |
| `ENV.climate_modes` | `EMIV-HUM-CLIM-001` |
| `HAB.emersion_duration` | `EMIV-PHY-EMERS-001` |
| `HAB.water_column_heat` | `EMIV-PHY-WTEMP-001` |
| `HAB.dissolved_oxygen` | `EMIV-BGC-DOXY-001` |
| `HAB.salinity` | `EMIV-PHY-SALIN-001` |
| `HAB.turbidity` | `EMIV-BGC-TURB-001` |
| `HAB.wave_loading` | `EMIV-PHY-WAVE-001` |
| `HAB.stratification_flushing` | `EMIV-PHY-STRAT-001` |
| `HAB.culture_method_elevation` | `EMIV-HUM-CULT-001` |
| `HAB.residence_time_currents` | `EMIV-PHY-CURR-001` |
| `BIO.phytoplankton_food` | `EMIV-BGC-CHL-001` (pigment proxy) |
| `BIO.hab_animal_stress` | `EMIV-ECO-HAB-001` |
| `BIO.oshv1` | `EMIV-ECO-DIS-001` |
| `BIO.vibrio` | `EMIV-ECO-DIS-001` |
| `BIO.predators_fouling` | `EMIV-ECO-PRED-001` |
| `PHYS.handling_stress` | `EMIV-HUM-HAND-001` |
| `PHYS.tissue_temperature` | `EMIV-PHY-TISST-001` |
| `OUT.lease_inventory` | `EMIV-BIO-ABUND-001` (farm count; PRIVATE) |
| `OUT.ops_workability` | `EMIV-ECO-OPSOUT-001` |
| `OUT.ops_gear_disruption` | `EMIV-ECO-OPSOUT-001` |
| `OUT.farm_mortality_72h` | `EMIV-ECO-OPSOUT-001` |
| `OUT.farm_mortality_delayed` | `EMIV-ECO-OPSOUT-001` |
| `OUT.doh_harvest_status` | `EMIV-HUM-HARV-001` |

**Files touched:** `causal_ecology/README.md`, `causal_status_policy.md`, `agent_handoff.md`, `graph_schema.md`, `w1_magallana_gigas_causal_graph.md`.

---

## 5. Ensembles

No EMIV ID stubs or `emiv:*` slugs. **No files patched.**

---

## 6. Unresolved (left in place; not measurands)

No registry row, or a planner/product key that is **not** an EMIV (do **not** mint rows for scores, H3, taxon IDs, B4/B12 model ids, or harm penalties):

| Key / slug | Where | Why unresolved |
|---|---|---|
| `EMIV-TAX-MGIG-001` | planner | Taxon identity (WoRMS 836033), not an EMIV |
| `EMIV-GEO-WBAY-001` | planner | Geography key |
| `EMIV-GEO-H3C-001` | planner | Geography key |
| `EMIV-MOD-B4-001` | planner | Model class, not a variable |
| `EMIV-MOD-B12-001` | planner | Model class, not a variable |
| `EMIV-UNC-EUR-001` | planner | Score, not a variable |
| `EMIV-UNC-OVS-001` | planner | Score, not a variable |
| `EMIV-DET-TRI-001` | planner | Product ternary (absent / not-detected / no-obs) |
| `EMIV-DET-OCC-001` | scoring_spec occupancy ψ | Model parameter; **not** remapped to eDNA except K04 |
| `EMIV-POL-HARM-001` | planner | Policy penalty |
| `EMIV-POL-PRIV-001` | planner | Policy penalty |
| `other` (tidal transport) | FIX-CD-RES-012 | Could be `CURR`/`TIDE`; not identified as one measurand |
| `HAB.intertidal_microclimate` | causal graph | Residual microclimate (color/shade/wind) — not the tissue/bag T row |
| `BIO.hab_human_toxin` | causal graph | NSSP toxin producers ≠ `HARV` status and ≠ animal-stress HAB |
| `PHYS.metabolic_spawn_condition` | causal graph | Physiology state |
| `PHYS.hypoxic_stress` | causal graph | Physiology state |
| `PHYS.osmotic_stress` | causal graph | Physiology state |
| `PHYS.larval_calcification` | causal graph | Physiology state (Ω is the env input) |
| `PHYS.delayed_mortality` | causal graph | Outcome timing (ops facet exists separately) |
| `OUT.sessile_no_72h_movement` | causal graph | Fact, not a measured EMIV |
| `OUT.planted_distribution` | causal graph | Placement metadata |
| `CF.*` | causal graph | Confounders, not EMIVs |
| KG `@id` slug paths | jsonld | Left as URN aliases |

Resolved this pass: `EMIV-ENV-SOL-001` → `EMIV-PHY-SOLAR-001` (**W1_CORE**; not chlorophyll). `EMIV-ENV-BAG-001` / `PHYS.tissue_temperature` → `EMIV-PHY-TISST-001` (**CANDIDATE**; W1_CORE when partner sensor exists). `ENV.solar_irradiance` and `ENV.solar_geometry_timing` bind to `EMIV-PHY-SOLAR-001`. SST remains **`EMIV-PHY-SST-001` `W1_PROXY`**.

---

## 7. Optional pointer (outside the five engines)

`P0_WILLAPA_MGIGAS_OSI72.md` — one sentence: DOH = `EMIV-HUM-HARV-001` constraint; SST = `EMIV-PHY-SST-001` PROXY.

**Not edited:** `globe/**`, `artifacts/integration/**`, `project_state.json` / `STATE_10`. Registry now **84** rows (this patch added SOLAR + TISST).

This folder’s [`README.md`](README.md) files table now lists this crosswalk.
