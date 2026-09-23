# Query library

**Date:** 2026-09-18  
**Store v0:** JSON-LD file + SQLite (see `store_recommendation.md`). Cypher / SPARQL are **dialects for later**, written against the same ontology.

Prefix: `kg:` = `urn:fishai:observatory:kg:`.

Gigas = `kg:species/worms-836033`. Decision = `gigas_wa_72h_ops_stress`.

---

## 0. SQLite v0 shape (assumed)

```sql
CREATE TABLE nodes (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  privacy_tier TEXT NOT NULL,
  json TEXT NOT NULL
);
CREATE TABLE edges (
  id TEXT PRIMARY KEY,
  predicate TEXT NOT NULL,
  subject TEXT NOT NULL,
  object TEXT NOT NULL,
  privacy_tier TEXT NOT NULL DEFAULT 'PUBLIC',
  json TEXT NOT NULL
);
-- edge json holds the ten required metadata fields.
```

JSON-LD `@graph` loads into these two tables (`KnowledgeEdge` → `edges`, everything else → `nodes`).

---

## 1. Biologically relevant EMIVs for a species × decision

**Question:** Which environmental variables may enter a *M. gigas* 72 h ops-stress model in Willapa, at `farmed_growout`?

### Cypher

```cypher
MATCH (s:Species {worms_aphiaid: 836033})-[e:RELEVANT_EMIV]->(v:EnvironmentalVariable)
WHERE e.decision_applicability = 'gigas_wa_72h_ops_stress'
  AND 'farmed_growout' IN e.life_stage_applicability
  AND e.causal_status IN ['MECHANISTIC_CAUSAL', 'INTERVENTION_SUPPORTED']
  AND e.review_status <> 'REJECTED'
RETURN v.emiv_id, e.causal_status, e.confidence, e.citation
ORDER BY v.emiv_id;
```

Expected fixture hits: `air_temperature`, `emersion_duration`, `water_temperature`, `dissolved_oxygen`, `salinity`, `wind_wave`, `hab_cell_density_animal_stress` (conditional).

### SPARQL-like

```sparql
SELECT ?emiv ?status ?conf ?cite
WHERE {
  kg:species/worms-836033 kg:RELEVANT_EMIV ?v .
  ?edge kg:subject kg:species/worms-836033 ;
        kg:predicate kg:RELEVANT_EMIV ;
        kg:object ?v ;
        kg:decision_applicability "gigas_wa_72h_ops_stress" ;
        kg:causal_status ?status ;
        kg:confidence ?conf ;
        kg:citation ?cite .
  FILTER(?status IN ("MECHANISTIC_CAUSAL", "INTERVENTION_SUPPORTED"))
}
```

### SQLite

```sql
SELECT json_extract(n.json, '$.emiv_id') AS emiv_id,
       json_extract(e.json, '$.causal_status') AS causal_status,
       json_extract(e.json, '$.confidence') AS confidence
FROM edges e
JOIN nodes n ON n.id = e.object
WHERE e.predicate = 'RELEVANT_EMIV'
  AND e.subject = 'urn:fishai:observatory:kg:species/worms-836033'
  AND json_extract(e.json, '$.decision_applicability') = 'gigas_wa_72h_ops_stress'
  AND json_extract(e.json, '$.causal_status') IN ('MECHANISTIC_CAUSAL', 'INTERVENTION_SUPPORTED')
  AND EXISTS (
    SELECT 1 FROM json_each(json_extract(e.json, '$.life_stage_applicability'))
    WHERE json_each.value = 'farmed_growout');
```

Also run the inverse (`IRRELEVANT_EMIV`) so the UI can say **why SST/chl/fecal coliform/Ω are out**.

---

## 2. Missing knowledge (canonical)

**Question:** Which MECHANISTIC_CAUSAL EMIVs for this species × decision × region have **no PUBLIC sensor** in that region?

This is the measurement-recommendation query.

### Cypher

```cypher
MATCH (s:Species {worms_aphiaid: 836033})-[r:RELEVANT_EMIV]->(v:EnvironmentalVariable)
WHERE r.decision_applicability = 'gigas_wa_72h_ops_stress'
  AND r.causal_status = 'MECHANISTIC_CAUSAL'
  AND r.geographic_applicability.region_id = 'urn:fishai:observatory:kg:region/willapa-bay'
OPTIONAL MATCH (sens:Sensor)-[m:MEASURES]->(v)
  WHERE m.geographic_applicability.region_id = r.geographic_applicability.region_id
    AND coalesce(m.privacy_tier, sens.privacy_tier) IN ['PUBLIC', 'COARSENED']
WITH v, r, count(sens) AS public_sensors
WHERE public_sensors = 0
RETURN v.emiv_id AS missing_emiv,
       r.citation AS why_it_matters,
       'Recommend in-situ sensor or partner logger (PRIVATE) in Willapa' AS next_measurement;
```

**Fixture expectation:**

- **`EMIV-BGC-DOXY-001` (primary gap):** NANOOS `MEASURES` DO is scoped to Hood Canal / ORCA-class geography, not Willapa. Farm logger MEASURES DO is `PRIVATE` and does not count for PUBLIC coverage. Air T (`EMIV-PHY-ATEMP-001`) and emersion (`EMIV-PHY-EMERS-001`) **do** have PUBLIC NWS/CO-OPS MEASURES in Willapa (as proxies).
- **`EMIV-ECO-HAB-001` (secondary):** SoundToxins **samples HAB taxa** (`SAMPLED_BY`) but is not a 72 h in-situ `Sensor` `MEASURES` edge — and must not be used as an ops-stress label anyway.

### SQLite (v0 missing-knowledge)

```sql
WITH needed AS (
  SELECT e.object AS emiv_id,
         json_extract(e.json, '$.geographic_applicability.region_id') AS region_id,
         json_extract(e.json, '$.citation') AS citation
  FROM edges e
  WHERE e.predicate = 'RELEVANT_EMIV'
    AND e.subject = 'urn:fishai:observatory:kg:species/worms-836033'
    AND json_extract(e.json, '$.decision_applicability') = 'gigas_wa_72h_ops_stress'
    AND json_extract(e.json, '$.causal_status') = 'MECHANISTIC_CAUSAL'
),
public_measures AS (
  SELECT object AS emiv_id,
         json_extract(json, '$.geographic_applicability.region_id') AS region_id
  FROM edges
  WHERE predicate = 'MEASURES'
    AND json_extract(json, '$.geographic_applicability.geometry_policy') IN ('PUBLIC', 'COARSENED', 'NONE')
    AND coalesce(privacy_tier, 'PUBLIC') IN ('PUBLIC', 'COARSENED')
)
SELECT n.emiv_id, n.citation
FROM needed n
LEFT JOIN public_measures p
  ON p.emiv_id = n.emiv_id AND p.region_id = n.region_id
WHERE p.emiv_id IS NULL;
```

---

## 3. Competing hypotheses

```cypher
MATCH (h1:Hypothesis)-[c:COMPETES_WITH]->(h2:Hypothesis)
WHERE c.decision_applicability = 'gigas_wa_72h_ops_stress'
OPTIONAL MATCH (e)-[:SUPPORTS]->(h1)
OPTIONAL MATCH (f)-[:SUPPORTS]->(h2)
RETURN h1.label, h2.label, c.notes, c.review_status,
       collect(DISTINCT e.label) AS evidence_h1,
       collect(DISTINCT f.label) AS evidence_h2;
```

Fixture: H1 air×tide (Raymond 2021 / intertidal) vs H2 hypoxia (Cheney 2000 / Puget Sound). Resolution = **stratify by habitat**, not pick a winner.

---

## 4. Block a nonsensical transfer (Chinook SST ↛ oyster bags)

```cypher
MATCH (src:Model {taxon_aphiaid: 158075})-[b:FORBIDDEN_TRANSFER]->(tgt)
WHERE tgt.taxon_aphiaid = 836033 OR tgt:Model AND tgt.taxon_aphiaid = 836033
   OR tgt.worms_aphiaid = 836033
RETURN src.id, type(tgt), tgt.id, b.citation, b.causal_status, b.review_status;
```

### SQLite

```sql
SELECT e.id, e.subject, e.object,
       json_extract(e.json, '$.citation') AS citation
FROM edges e
WHERE e.predicate = 'FORBIDDEN_TRANSFER'
  AND e.subject LIKE '%chinook-sst-encounter%'
  AND (e.object LIKE '%836033%' OR e.object LIKE '%b4-gigas%');
```

Factory gate: if this query returns ≥1 row, **do not bind** Chinook SST weights, features, or posteriors onto *gigas* bags.

---

## 5. Explain a synthetic forecast

```cypher
MATCH (f:Forecast {forecast_id: '01800000-0000-7000-8000-000000000031'})
OPTIONAL MATCH (f)-[:MODELED_BY]->(m:Model)
OPTIONAL MATCH (m)-[u:USES_EMIV]->(v)
OPTIONAL MATCH (m)-[:VALIDATED_AGAINST]->(val)
OPTIONAL MATCH (f)-[iss:ISSUED_FOR]->(target)
WHERE coalesce(iss.privacy_tier, target.privacy_tier) <> 'PRIVATE'
  AND target.privacy_tier <> 'PRIVATE'
RETURN f, m, collect(v.emiv_id), val.status, collect(target.id);
```

PUBLIC explain **must** drop `ISSUED_FOR` the PRIVATE farm.

---

## 6. SoundToxins / WDOH wall

```cypher
MATCH (st:Survey {name: 'SoundToxins'})-[b:FORBIDDEN_TRANSFER]->(m:Model)
RETURN b.citation;
MATCH (stock:StockPopulation)-[c:CONSTRAINED_BY]->(r:RegulatoryConstraint)
WHERE r.official_unit_id STARTS WITH 'WA_DOH_GROWING_AREA'
  AND c.causal_status = 'WRONG_TARGET'
RETURN r.official_unit_id, c.notes;
```

These queries exist so a brief assembler cannot “helpfully” mix biotoxin status into the ops score.

---

## 7. Public species-page projection

See `privacy_projection.md`. Query form:

```sql
SELECT id, type, json FROM nodes
WHERE privacy_tier = 'PUBLIC'
  AND type NOT IN ('AquacultureFarm')
  AND coalesce(json_extract(json, '$.geometry_policy'), '') <> 'NEVER_PUBLISH';

SELECT * FROM edges
WHERE coalesce(privacy_tier, 'PUBLIC') IN ('PUBLIC', 'COARSENED')
  AND predicate NOT IN ('ISSUED_FOR')  -- further filter: drop edges whose subject/object is PRIVATE
  AND subject NOT IN (SELECT id FROM nodes WHERE privacy_tier = 'PRIVATE')
  AND object NOT IN (SELECT id FROM nodes WHERE privacy_tier = 'PRIVATE');
```

---

## 8. Recommend measurements (derived from §2)

Rank missing EMIVs by `(confidence of RELEVANT_EMIV descending, whether USES_EMIV on the bound model)`. For the W1 fixture, **Willapa dissolved oxygen** is the top PUBLIC gap. Partner loggers fill it only inside `PRIVATE`.

Do not recommend AIS, satellite SST-as-oyster-health, or fecal coliform as the next biological measurement for this decision — those are `IRRELEVANT_EMIV` / `WRONG_TARGET`.
