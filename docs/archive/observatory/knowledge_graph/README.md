# Marine biological knowledge graph

**Program:** Global Saltwater Life Observatory / FishAI  
**Path:** `/Users/wijeratne/dev/fishai/observatory/knowledge_graph/`  
**Date:** 2026-09-18  
**Status:** Schema + small fixture only. No OBIS/GBIF dumps. No globe map. No commercial integration files.  
**Taxonomy:** WoRMS AphiaIDs from `artifacts/marine_domain/` (verified REST 2026-09-18).

This folder is **Layer 4** of the observatory (species ecology knowledge): a typed graph of what is biologically relevant, what must not be transferred, and what is missing. It is **not** a global public map of saltwater life.

---

## Why a graph, not a globe

A public world canvas of “where the animals are” is rejected by `../sensitive_location_policy.md` §12. Mixed taxa, spawning and nursery sites, farm performance, ESA ESU holding water, trap GPS, and Indigenous data cannot share one heatmap. The knowledge graph holds **identity, mechanism, applicability, and evidence** so models and species pages can be honest. Locations that would be `NEVER_PUBLISH` are **not public nodes**.

The commercial 1×1×1×1 wedge, if later locked, **clips** this graph (taxon × region × decision). It does not become a second product atlas.

## What this graph is for

| Use | How the graph helps |
|-----|---------------------|
| Select biologically relevant variables | `RELEVANT_EMIV` / `IRRELEVANT_EMIV` with `causal_status` and `decision_applicability` |
| Prevent nonsensical model transfers | `FORBIDDEN_TRANSFER` + transfer constraints (Chinook SST encounter ↛ oyster bags) |
| Explain predictions | Walk `MODELED_BY` → EMIVs → publications → sensors |
| Surface missing knowledge | Required MECHANISTIC_CAUSAL EMIVs with no in-region sensor or observation |
| Species pages | Public projection of taxon, stages, envelopes, citations — no farms, no pins |
| Recommend measurements | Missing-knowledge query ranked by decision |
| Generate hypotheses | `Hypothesis` nodes with `COMPETES_WITH` |
| Detect conflicting evidence | Same predicate, incompatible `causal_status`, range, or geography (see `conflict_detection.md`) |

## What this graph is not

- Not occurrence points, tracks, or a twin posterior.  
- Not harvest authorization, food safety, or navigation.  
- Not farm KPIs. Aquaculture farm nodes are `PRIVATE` and carry **no performance**.  
- Not a Neo4j platform. v0 store is **JSON-LD + SQLite** (`store_recommendation.md`).

## Query layer and privacy tiers

All reads go through a **projection**, not the raw store:

| Tier | Who | Graph they see |
|------|-----|----------------|
| `PUBLIC` | Anyone | Species pages: taxon, coarsened regions, official designations, literature, relevant EMIVs. No farms, no loggers, no tags-as-tracks, no `NEVER_PUBLISH` geometry. |
| `COARSENED` / `DELAYED` | Staff + delayed public | Official-unit grain; embargoed observations |
| `RESTRICTED` | Named staff | Mixed-licence surveys without public GPS |
| `PRIVATE` | Partner + processors | Farm node existence, lease-class habitat, their sensors — still no neighbor farms |
| `NEVER_PUBLISH` | Break-glass / legal hold | **Not a queryable public node type.** Do not insert nest/trap/ESU GPS into this fixture. |

Details: `privacy_projection.md`. Policy: `../sensitive_location_policy.md`.

## Fixture (Pacific oyster W1 analog)

`example_graph_gigas.jsonld` encodes *Magallana gigas* (AphiaID **836033**) in **Willapa Bay** with:

- Intertidal vs subtidal culture and depth bins `INTERTIDAL_AIR` / `SURFACE_0_5` / `SUBTIDAL_BOTTOM`  
- Air temperature × tide (emersion) as the primary 24–72 h intertidal mechanism  
- Dissolved oxygen and salinity as causal co-stressors (DO sparse in Willapa)  
- SoundToxins as a **HAB constraint / data source**, not an operations-stress label  
- WA DOH growing area as a **regulatory** node (NSSP harvest geography), not a stress label  
- One `PRIVATE` aquaculture farm fixture with **no** yield, mortality, or lease corners  
- Explicit blocks: Chinook SST encounter model; larval Ω_aragonite model; DOH class-as-stress; OsHV-1 imported from CA without WA PCR  

**v0 store:** JSON-LD files in git + SQLite edge/node tables. Not Neo4j.

**Fixture counts** (from `example_graph_gigas.jsonld` `fixture_stats`): **95 nodes**, **127 edges**. PUBLIC nodes 93; PRIVATE nodes 2 (farm + farm logger); NEVER_PUBLISH public nodes 0. PRIVATE edges 7. Full type breakdown in the JSON-LD and `agent_handoff.md`.

## Sibling folders (read, not owned)

| Path | Used for |
|------|----------|
| `artifacts/marine_domain/` | WoRMS IDs, covariates, life stages, limitations |
| `observatory/sensitive_location_policy.md` | Privacy tiers; no public sensitive locations |
| `observatory/taxonomy_graph/taxonomy_standard.md` | Identity protocol |
| `observatory/emiv/` | Registry **`v0.1-draft`**. Graph `emiv_id` values are registry IDs (`EMIV-PHY-ATEMP-001`, …). URN `@id`s (`kg:emiv/air_temperature`) unchanged. Crosswalk: [`../emiv/engine_id_crosswalk.md`](../emiv/engine_id_crosswalk.md) |
| `observatory/causal_ecology/` | **Absent** 2026-09-18. `causal_status` enum is proposed here as the alignment target |

## Files in this folder

| File | Role |
|------|------|
| `README.md` | This index |
| `ontology.md` | Classes, relations, transfer constraints |
| `edge_metadata_schema.json` | Required fields on every edge |
| `example_graph_gigas.jsonld` | Small W1 fixture |
| `conflict_detection.md` | How contradictions surface |
| `query_library.md` | Cypher / SPARQL-like / SQLite examples |
| `store_recommendation.md` | JSON-LD + SQLite now; Neo4j later |
| `privacy_projection.md` | What PUBLIC species pages strip |
| `agent_handoff.md` | Return block for the orchestrator |

Did not write `globe/**`. Did not write commercial `artifacts/**`. Did not ingest OBIS/GBIF.
