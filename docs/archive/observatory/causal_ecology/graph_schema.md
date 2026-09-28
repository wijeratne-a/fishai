# Causal ecology graph schema

**Date:** 2026-09-18  
**Status:** Design contract. No graph database, no trained SCM, no ingest.  
**Output class of any materialized graph today:** `HYPOTHETICAL/RESEARCH MODE`

This schema is how FishAI observatory records **assumed mechanisms** along a single directed path:

**environmental variables → habitat conditions → prey/predator (and pathogen/food) state → life-stage physiology → movement / distribution / abundance**

W1 farmed *Magallana gigas* is sessile after settlement: the last hop is mostly **physiology → operational disruption / mortality / workability**, with **abundance = planted inventory** and **movement ≈ 0 at 72 h**. Those facts are edges, not excuses to skip the path.

---

## 1. Layer types (exactly these five biological layers)

| Code | Layer | What nodes are | What nodes are not |
|---|---|---|---|
| `L1_ENV` | Environmental variables | Air T, solar, in situ water T, tide potential, wind, discharge, pH, climate indices, **satellite SST as its own node** | Animals, harvest legality |
| `L2_HAB` | Habitat conditions | Emersion, microclimate, DO, salinity, stratification, wave loading, culture elevation | Tissue temperature (that is physiology) |
| `L3_BIO` | Prey / predator / pathogen / food-web | Phytoplankton food, named HABs, OsHV-1, *Vibrio*, drills/fouling | NSSP fecal coliform as “prey” |
| `L4_PHYS` | Life-stage physiology | Tissue T, spawn condition, hypoxic/osmotic stress, larval calcification, delayed-death process | SST, growing-area class |
| `L5_OUT` | Movement / distribution / abundance **and declared ops outcomes** | Sessility, planted distribution, inventory, workability, gear loss, farm mortality, **DOH status as a non-biological output node** | Pixel “oyster abundance” from ocean color |

**Required extra node class (not a sixth biological layer):** `CF_*` confounders from `confounder_catalog.md`. Confounders may point at **observed labels**, not at hidden physiology, unless a mechanism is written.

---

## 2. Node record

| Field | Required | Notes |
|---|---|---|
| `node_id` | yes | Stable, dotted (`ENV.air_temperature`) — graph key, not the registry ID |
| `emiv_id` | no | Registry ID from `observatory/emiv/` when a row exists (`EMIV-PHY-ATEMP-001`). Compound nodes may list `A|B`. Leave blank if unresolved. |
| `layer` | yes | `L1_ENV` … `L5_OUT` or `CF` |
| `quantity` | yes | What would be measured |
| `taxon_scope` | yes | WoRMS AphiaID or `abiotic` |
| `life_stage` | yes | e.g. `farm_spat_to_market`, `hatchery_larva`, `n_a` |
| `geography_scope` | yes | e.g. `WA_estuary_named`, `lab_protocol`, `global_physiology` |
| `horizon` | yes | `hours_72`, `days_30`, `seasonal`, `structural` |
| `depth_or_emersion` | yes | `INTERTIDAL_AIR`, `SURFACE_0_5`, `CULTURE_DEPTH`, `n_a` |
| `privacy_tier` | yes | From sensitive-location policy |
| `is_proxy` | yes | `true` for satellite SST, satellite chl, AIS |
| `forbidden_as` | yes | e.g. `body_temperature`, `abundance`, `harvest_legality` |

---

## 3. Edge record (the unit of causal status)

Every relationship is a directed edge with **exactly one** `causal_status` from `causal_status_policy.md`.

| Field | Required |
|---|---|
| `edge_id` | yes (`W1-E01` …) |
| `source_node_id` | yes (or explicit interaction set) |
| `target_node_id` | yes |
| `interaction` | yes if product/synergy (`air_T × emersion × solar`) |
| `causal_status` | **exactly one** of the five |
| `identification_class` | from policy §4 |
| `citations[]` | bibliographic + **URL** + access date `2026-09-18` |
| `horizon` | must match the claim |
| `life_stage` | |
| `geography` | |
| `culture_method` | `intertidal_bag`, `bottom`, `subtidal_raft`, `any`, `lab` |
| `confounders[]` | at least the catalog items that apply |
| `data_support` | `none` / `sparse` / `program_exists` / `lab_only` / `partner_private` — **not** a skill score |
| `predictive_use` | `allowed_as_input` / `baseline_only` / `forbidden` |
| `causal_use` | `forbidden` / `research_only` / `mechanism_note_only` |
| `anti_claim` | sentences that must never be inferred from this edge |
| `falsifier` | pointer into `what_would_falsify.md` |

**Interactions.** Aerial heat is not `air_temperature → mortality`. The W1 thermal mechanism is the **product** `air_temperature × midday_emersion × solar_irradiance` acting on `tissue_temperature` (`EMIV-PHY-ATEMP-001` × `EMIV-PHY-EMERS-001` × `EMIV-PHY-SOLAR-001` → `EMIV-PHY-TISST-001`). Encoding only SST→mortality is a schema violation. SST remains `EMIV-PHY-SST-001` **PROXY**.

**Anti-edges.** Use a normal edge with `causal_status = UNKNOWN` (or `OBSERVED_CORRELATION` plus a hard `anti_claim`) when the arrow is the mistake users will draw. Do not omit SST→tissue-T; **write it and mark it unknown/wrong for emersion**.

---

## 4. Graph-level invariants

1. No edge may point from `ENV.satellite_sst` to `PHYS.tissue_temperature` with status above `UNKNOWN` for **emersion**.  
2. No edge may point from `OUT.doh_harvest_status` to farm mortality as a physiological cause.  
3. No edge may treat AIS, vessel density, or chlorophyll as `OUT.lease_inventory` / abundance.  
4. `L5_OUT` abundance for W1 is operator-controlled unless a wild-set node is added (out of 72 h wedge).  
5. Mixing Hood Canal hypoxia, Willapa aerial heat, and NSSP closures into one `stress` node is **false causal aggregation** (RT-OYS-06). Separate targets.  
6. Cycles are allowed only for documented feedbacks (handling after heat; operator responding to the indicator). Mark as confounder paths.

---

## 5. Query objects (see also driver and counterfactual contracts)

A **driver query** asks what may be said about an arrow or a parent set.

A **counterfactual query** asks about \(Y\) under a hypothetical \(X'\). It does **not** read from a fitted \(do(\cdot)\) engine. It returns a structured **scenario estimate** with status inherited from the **weakest** edge on the assumed path.

**Aggregation rule (weakest link):**

`UNKNOWN` < `EXPERT_HYPOTHESIS` < `OBSERVED_CORRELATION` < `ECOLOGICALLY_SUPPORTED_ASSOCIATION` < `CAUSALLY_TESTED_RELATIONSHIP`

Path status = minimum along the path. A lab-tested aerial-heat mortality edge **and** an unknown SST→tissue edge **cannot** be chained into “SST caused death.”

---

## 6. Serialization (design; not implemented)

Suggested JSON (not ingested, not validated in code this iteration):

```json
{
  "graph_id": "W1-M-GIGAS-2026-09-18",
  "trained_causal_model": false,
  "output_class": "HYPOTHETICAL/RESEARCH MODE",
  "nodes": [],
  "edges": [],
  "access_date": "2026-09-18"
}
```

Do not store `PRIVATE` farm outcomes in a public graph dump.

---

## 7. Relation to other observatory artifacts

| Artifact | Role vs this schema |
|---|---|
| `species_model_factory.md` Step 3 | Ecological profile must cite edge IDs, not a kitchen-sink of layers |
| `data_assimilation_design.md` §5.6 | DAGs here are assumption docs; DA must not treat catchability drivers as \(N\) |
| `ocean_model_comparison.md` §2.21 | “Causal models” = this graph, **rarely a fitted SCM** |
| `API_specification.md` oyster stub | Sibling sentence “Air temperature × daytime emersion is a **causal** stressor (Raymond et al. 2022)” is **too strong**: Raymond is `ECOLOGICALLY_SUPPORTED_ASSOCIATION`. Do not copy into this module. |
