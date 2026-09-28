# Agent handoff — marine biological knowledge graph / ontology

**Date:** 2026-09-18  
**Agent:** MARINE BIOLOGICAL KNOWLEDGE GRAPH / ONTOLOGY DESIGNER  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/knowledge_graph/` only  
**Did not write:** `globe/**`, commercial `artifacts/**`, OBIS/GBIF dumps, a graph platform.

**Read:** `artifacts/marine_domain/` (WoRMS IDs 836033 / 158075 / 156134 and covariates); `observatory/sensitive_location_policy.md`; `observatory/taxonomy_graph/taxonomy_standard.md`.  
**Absent (noted at authoring, not invented as dumps):** `observatory/emiv/` slugs later bound to registry `v0.1-draft` (this wiring pass). `observatory/causal_ecology/` — `causal_status` enum proposed in `ontology.md` §8 as the alignment target.

**Project context:** FishAI `STATE_10_PAUSED_FOR_HUMAN_DECISION`; wedge UNRESOLVED; W1 Pacific oyster × Willapa is RECOMMENDED not DECIDED. This graph is observatory Layer 4 catalog knowledge, not a product lock and not a global map.

---

## 1. Executive finding

Build a **typed, evidence-bearing knowledge graph** so the observatory can pick the right variables, refuse illegal model hops, explain claims, and show what is missing — **behind privacy tiers**. Do **not** build a public globe of saltwater life.

**Recommended v0 store: JSON-LD in git + SQLite projection. Not Neo4j.**

Fixture (`example_graph_gigas.jsonld`): **95 nodes, 127 edges** encoding Pacific oyster W1 (Willapa), intertidal vs subtidal, air × tide, DO, salinity, SoundToxins as HAB **constraint** (not ops label), WDOH as **regulatory** node (not stress label), one PRIVATE farm with **no performance**.

### Return block (requested)

| Question | Answer |
|----------|--------|
| **Recommended store for v0** | **JSON-LD files + SQLite** (`nodes` / `edges` + JSON metadata). Neo4j only later if editors, multi-hop product queries, and ops ownership exist. Details: `store_recommendation.md`. |
| **Node / edge counts in fixture** | **95 nodes, 127 edges** (222 `@graph` items). PRIVATE nodes 2; PRIVATE edges 7; NEVER_PUBLISH public nodes **0**. |
| **Example of blocking a nonsensical transfer** | **Chinook SST encounter model (`taxon 158075`) ↛ *Magallana gigas* bags (`836033`).** Failures: taxon, life stage (`ocean_immature_adult` vs `farmed_growout`), depth (`SHELF_THERMAL_BAND` vs `INTERTIDAL_AIR`), habitat (shelf pelagic vs leased bags), decision (encounter D vs ops-stress D), EMIV (`EMIV-PHY-SST-001` PROXY vs `EMIV-PHY-ATEMP-001` × `EMIV-PHY-EMERS-001` MECHANISTIC_CAUSAL). Machine: `FORBIDDEN_TRANSFER` from `kg:model/chinook-sst-encounter` to `kg:model/b4-gigas-air-tide-stress` and to species 836033. |
| **One missing-knowledge query** | MECHANISTIC_CAUSAL `RELEVANT_EMIV` for *gigas* × `gigas_wa_72h_ops_stress` × Willapa with **no PUBLIC `MEASURES` in Willapa**. Fixture hit: **`EMIV-BGC-DOXY-001`**. SQL/Cypher: `query_library.md` §2. Secondary hit: animal-stress HAB (`EMIV-ECO-HAB-001`; SoundToxins is a survey, not a 72 h sensor — and not an ops label). |

---

## 2. Evidence table

| Finding | Evidence | Confidence |
|---------|----------|------------|
| WoRMS IDs | marine_domain + REST 2026-09-18: *M. gigas* 836033; synonym 140656; Chinook 158075; lobster 156134; *O. lurida* 542155; *M. angulata* 1039387; *Heterosigma* 160585; *A. catenella* 231873; *P. reticulatum* 110321 | High |
| Air × tide is the intertidal 72 h mechanism | Raymond et al. 2022; marine_domain variable matrix `include_in_v1=yes` | High |
| DO causal but Willapa-sparse | Cheney 2000 (Puget Sound); NANOOS stronger in Hood Canal; data_discovery critical gap | High |
| WDOH ≠ stress | marine_domain; project_state rejected_sources; product thesis hard wall | High |
| SoundToxins ≠ ops label | Split animal-stress HAB vs NSSP harvest toxins | High |
| Farms PRIVATE, no KPIs | sensitive_location_policy §3.3, §5 aquaculture row, §6.11 | High |
| Chinook SST ↛ oyster bags | ontology transfer checks; Hinke 2005 vs Raymond 2022 | High |
| No global public map | sensitive_location_policy §12 | High |
| EMIV / causal_ecology folders | `emiv/` **bound** `v0.1-draft` this wiring pass; causal_ecology present as sibling | Certain |

---

## 3. Source / license table

No datasets ingested. Catalog citations only. Licenses `UNKNOWN` until a rights pass.

| Source | URL / path | Use |
|--------|------------|-----|
| WoRMS REST / taxon pages | https://www.marinespecies.org/ | AphiaIDs, LSIDs |
| marine_domain dossiers | `/Users/wijeratne/dev/fishai/artifacts/marine_domain/` | Mechanisms, stages, limitations |
| NOAA Fisheries Pacific oyster | https://www.fisheries.noaa.gov/species/pacific-oyster | Biology, introduction |
| WA DOH growing areas | https://doh.wa.gov/community-and-environment/shellfish/growing-areas | Regulatory geography |
| SoundToxins | https://soundtoxins.org/about.html | HAB program |
| NANOOS NVS | https://nvs.nanoos.org/ShellfishGrowers | Sensor class |
| CO-OPS | https://tidesandcurrents.noaa.gov/ | Emersion |
| Raymond 2022 | https://doi.org/10.1002/ecy.3798 | Heat × tide |
| Cheney 2000 | *J. Shellfish Res.* 19:353–359 | Multi-stressor PS |
| Hinke 2005 | https://doi.org/10.3354/meps304207 | Chinook 8–12 °C / depth |
| Dumbauld 2023 | https://doi.org/10.3354/dao03868 | OsHV-1 OR/WA sentinels |
| FAO gigas sheet | FAO culture CD-ROM URL in marine_domain | Envelopes |
| sensitive_location_policy | `observatory/sensitive_location_policy.md` | Tiers |
| taxonomy_standard | `observatory/taxonomy_graph/taxonomy_standard.md` | Identity |

---

## 4. Confidence and limitations

| Item | Confidence | Limitation |
|------|------------|------------|
| Ontology coverage of requested classes | High | One fixture estuary, not all taxa |
| Transfer-block completeness | Medium–high | Analog transfers (e.g. *C. virginica*) not encoded |
| EMIV ids | High for bound rows | Unresolved: no KG tide node (`EMIV-PHY-TIDE-001` exists in registry); wind/wave still one graph node |
| causal_status enum | Medium | Proposed; migrate if causal engine ships a different list |
| Numeric tolerance curves | Low | Event analogues and FAO floors only; no bag-level LT50 |
| SoundToxins taxon lists | Medium | Split is principled; cell-count series not loaded |
| SQLite as v0 | High for team size | Not a concurrent multi-editor server |
| No human domain sign-off | Certain | `EDITOR_DRAFT` except a few `DOMAIN_REVIEWED` walls |

**Did not:** interview growers; ingest NANOOS/SoundToxins/DOH GIS; implement SQLite loader; bind a live `/state` API; write globe tiles.

---

## 5. Recommended decision

1. **Accept** JSON-LD + SQLite as the v0 knowledge store.  
2. **Accept** the transfer constraint table (especially Chinook SST ↛ oyster bags; DOH/SoundToxins walls; OA-larva; OsHV-1 CA; Hood Canal ≠ Willapa).  
3. **Keep** farms PRIVATE with no performance fields.  
4. **EMIV slugs are bound** to `observatory/emiv/` `v0.1-draft`; do not mint a second identifier family. Unresolved keys stay in `engine_id_crosswalk.md`.  
5. **Do not** stand up Neo4j, load OBIS, or publish a species heatmap.

---

## 6. Rejected alternatives

| Alternative | Why |
|-------------|-----|
| Neo4j / graph SaaS now | Premature platform; privacy harder to audit |
| Global occurrence graph from OBIS/GBIF | Forbidden ingest; not Layer 4 ecology |
| Public farm nodes “but coarsened” | Inverts leases with WDOH viewer |
| SST as the *gigas* 72 h driver | PROXY; misses air × emersion |
| Mixing SoundToxins / WDOH into B4 | WRONG_TARGET |
| Stub NEVER_PUBLISH nests “for completeness” | Becomes a leak; omit instead |
| One Category D meaning across wedges | Encounter ≠ ops-stress |

---

## 7. Follow-up questions

1. Remaining unresolved planner/KG keys (OVS/EUR scores, H3, taxon IDs, B4/B12, harm penalties) stay engine internals — **not** EMIVs. Solar = `EMIV-PHY-SOLAR-001`; bag/tissue T = `EMIV-PHY-TISST-001`.  
2. Does causal_ecology adopt `ontology.md` §8 or replace it?  
3. Founder W1 lock (Willapa vs named South Sound)? Graph clips either way.  
4. Will a domain editor (shellfish) promote `EDITOR_DRAFT` edges?  
5. Loader script in a later pass (JSON-LD → SQLite), or stay file-only until wedge lock?

---

## 8. Artifacts generated

All under `/Users/wijeratne/dev/fishai/observatory/knowledge_graph/`:

| File | Role |
|------|------|
| `README.md` | Why a graph, not a globe; privacy-tiered query layer |
| `ontology.md` | Classes, relations, transfer rules, EMIV table |
| `edge_metadata_schema.json` | Ten required fields on every edge |
| `example_graph_gigas.jsonld` | W1 fixture (95 / 127) |
| `conflict_detection.md` | How contradictions surface |
| `query_library.md` | Cypher / SPARQL-like / SQLite |
| `store_recommendation.md` | JSON-LD + SQLite now |
| `privacy_projection.md` | PUBLIC species-page strip list |
| `agent_handoff.md` | This document |

---

## 9. Should this be red-teamed?

**Yes — targeted.** Attacks: PUBLIC page + WDOH map viewer naming a partner farm; SoundToxins badge read as harvest advice; Chinook card leaking ESU geography; LLM tool hopping `FORBIDDEN_TRANSFER`; treating FAO DO >2 mg L⁻¹ as a no-effect level; averaging CONFLICT_OPEN edges into one score.

Human NSSP/shellfish review is still required. This agent is not that reviewer.

---

## 10. Suggested next experiment

No bulk download.

1. Load the JSON-LD into a throwaway SQLite file.  
2. Run `query_library.md` §2 and §4. Pass if DO is missing for Willapa PUBLIC and Chinook SST transfer is blocked.  
3. Materialize `privacy_projection.md` views; assert farm id absent.  
4. Stop. Do not expand to a world graph.

---

## Fixture stats (copy)

```
node_count: 95
edge_count: 127
nodes_by_privacy_tier: PUBLIC 93, PRIVATE 2
never_publish_public_nodes: 0
private_farm_nodes: 1
```

Classes present: Species, Taxon, StockPopulation, LifeStage, Habitat, OceanRegion, DepthZone, EnvironmentalVariable, ToleranceRange, Prey, Predator, Disease, Parasite, Survey, Observation, Sensor, Tag, Model, Publication, DataSource, Fishery, AquacultureFarm, ProtectedArea, RegulatoryConstraint, HumanPressure, Forecast, ValidationResult, Hypothesis, TransferConstraint.
