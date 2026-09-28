# Store recommendation

**Date:** 2026-09-18  
**Team size assumed:** small (one engineer + domain editor, no graph-platform SRE).  
**v0 recommendation:** **JSON-LD files in git + SQLite**. Not Neo4j. Not a graph SaaS.

---

## 1. Decision

| Horizon | Store | Why |
|---------|--------|-----|
| **v0 (now)** | Canonical **JSON-LD** (`example_graph_gigas.jsonld` and later per-taxon files) + a **SQLite** projection (`nodes`, `edges`, JSON metadata columns) | Schema is still moving. The artifact must be reviewable in PRs. Queries in `query_library.md` are SQL-shaped. Privacy projection is a SQL view. Matches the commercial/observatory local-disk stack (SQLite/parquet, ~$0–80/month). |
| **v1 (later)** | Same JSON-LD as source of truth; SQLite or Postgres if concurrent editors | Add check constraints and an append-only `edge_revisions` table. Still no cluster. |
| **Only if needed** | Neo4j / Memgraph / RDF triple store | When variable-length paths are a daily product path, editors > few, and someone will operate backups, auth, and upgrades. Not this iteration. |

This graph is Layer 4 **catalog knowledge**, not a 224 M-row occurrence cube. OBIS/GBIF dumps would be the wrong store for the wrong problem.

---

## 2. Why not a graph platform now

1. **Premature ops.** Neo4j Aura/Enterprise (or self-hosted Bolt + JVM) is a product. The observatory has no ingest, no wedge lock, and no live API.  
2. **Privacy.** A connected graph database invites “just hop to the farm node.” SQL views that **omit** `privacy_tier IN (PRIVATE, NEVER_PUBLISH)` are easier to audit than labeled property-graph traversal with forgotten filters.  
3. **Diffability.** Domain experts review citations in git. A 95-node fixture is a file, not a database dump.  
4. **HiveClaw lesson (local):** causal runtime chose SQLite over Neo4j for a single-team store (`HiveClaw/docs/adr/CAUSAL_RUNTIME_H5.md`). Same constraint class.  
5. **RDF purity is optional.** JSON-LD gives `@id` stability and a future SPARQL door without requiring Jena today.

Rejected now: Neptune, TigerGraph, TerminusDB, “knowledge-graph platform” vendors, embedding the graph in a vector DB.

---

## 3. v0 physical layout

```
observatory/knowledge_graph/
  *.md, edge_metadata_schema.json, example_graph_gigas.jsonld   # git source of truth
  (not committed) /tmp or local:
    kg_v0.sqlite   # built by a loader that is not required this pass
```

```sql
CREATE TABLE nodes (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  privacy_tier TEXT NOT NULL CHECK (privacy_tier IN
    ('PUBLIC','COARSENED','DELAYED','RESTRICTED','PRIVATE','NEVER_PUBLISH')),
  json TEXT NOT NULL
);
CREATE TABLE edges (
  id TEXT PRIMARY KEY,
  predicate TEXT NOT NULL,
  subject TEXT NOT NULL REFERENCES nodes(id),
  object TEXT NOT NULL REFERENCES nodes(id),
  privacy_tier TEXT NOT NULL DEFAULT 'PUBLIC',
  json TEXT NOT NULL
);
CREATE INDEX edges_spo ON edges(subject, predicate, object);
CREATE INDEX edges_pos ON edges(predicate, object, subject);
```

Validate `edges.json` against `edge_metadata_schema.json` on load. Refuse rows with `geometry_policy=NEVER_PUBLISH` unless the edge itself is stored in a break-glass database that **public jobs cannot mount**. This fixture contains **zero** such rows.

---

## 4. When to revisit Neo4j

Reconsider only if **all** are true:

- Editors need interactive graph UI daily.  
- Query load is multi-hop explanation in production (not a nightly SQL report).  
- Node/edge counts exceed what SQLite JSON1 comfortably serves (rule of thumb: **>50k edges** or many concurrent writers).  
- A named owner will patch, backup, and ACL the server.  
- Privacy projection tests still pass on the new store.

Until then, Cypher in `query_library.md` is documentation of intent.

---

## 5. What not to store here

| Data | Where it belongs instead |
|------|--------------------------|
| OBIS/GBIF occurrence points | Do not ingest. Catalog counts live in the species registry. |
| Twin posteriors / forecasts | Observatory layers 7–8 (append-only forecast store) |
| Farm KPIs | Never in this graph; not in PUBLIC SQLite |
| Nest / trap / ESU GPS | `NEVER_PUBLISH` hold — not this file |
| Full WoRMS database | Cache used AphiaIDs only |

JSON-LD in git **is** the v0 recommended store. SQLite is the query cache.
