# Privacy projection — PUBLIC species pages

**Date:** 2026-09-18  
**Policy:** `../sensitive_location_policy.md`  
**Fixture:** `example_graph_gigas.jsonld`

The raw graph is an **internal** store. PUBLIC species pages (and any research API with role `public`) read a **stripped projection**. A global public life map is still rejected.

---

## 1. Projection rule

`PUBLIC_view = f(raw_graph)` computed at read time (and optionally materialized). Public jobs must not mount PRIVATE tables.

For each node/edge:

1. Drop if `privacy_tier` ∈ {`PRIVATE`, `NEVER_PUBLISH`}.  
2. Drop if `geographic_applicability.geometry_policy` = `NEVER_PUBLISH`.  
3. Drop if subject or object was dropped (no dangling edges).  
4. Coarsen `DELAYED` until embargo; then apply grain caps in the policy.  
5. Replace `RESTRICTED` payloads with counts + citations, no coordinates.  
6. Never add coordinates that were not in the allowed node.

Default when unsure: one tier stricter.

---

## 2. What a PUBLIC *Magallana gigas* page **may** contain

| Allowed | Source in fixture |
|---------|-------------------|
| Accepted name, AphiaID 836033, LSID, synonym *C. gigas* 140656 | Species + Taxon |
| Disambiguation: not Portuguese oyster (1039387), not Olympia (542155) | Species nodes |
| Life stages (`farmed_growout`, `larva`) with **different** EMIV relevance | HAS_LIFE_STAGE, RELEVANT_EMIV |
| Coarsened region **Willapa Bay** as named estuary | OceanRegion |
| Official growing-area **identifier as WDOH publishes** (fixture string) | RegulatoryConstraint — labeled **harvest geography, not stress** |
| Official protected-area **name / link** (Willapa NWR) | ProtectedArea |
| Relevant EMIVs for 72 h ops-stress + why SST/chl/fecal/Ω are out | RELEVANT_EMIV / IRRELEVANT_EMIV |
| Tolerance narratives with citations (Raymond, FAO) | ToleranceRange + Publication |
| HAB split: SoundToxins as a **program**; *Heterosigma* animal-stress vs *Alexandrium* harvest toxin | Survey + CONSTRAINED_BY + FORBIDDEN_TRANSFER |
| Competing hypotheses H1 vs H2 | Hypothesis |
| Transfer blocks (Chinook SST, OA-larva, OsHV-1 CA) as **explanations** | TransferConstraint |
| Support-tier ceiling T2; live output still UNKNOWN until factory publish | Species.support_tier_ceiling |
| “What would help: Willapa in-situ DO” | Missing-knowledge query |

---

## 3. What PUBLIC pages **must strip**

| Strip | Why |
|-------|-----|
| `AquacultureFarm` node `farm/W1_FIXTURE_PRIVATE_LEASE_ZONE_B` | PRIVATE; rule-of-3 / growing-area only |
| Any farm **performance** (none stored — keep it that way) | Policy §3.3, §6.11 |
| Farm logger sensor + its MEASURES edges | PRIVATE |
| `ISSUED_FOR` → farm | Would invert a lease |
| Lease corners, bag GPS, neighbor farm ids | NEVER_PUBLISH / PRIVATE |
| Chinook ESU holding pools, river-mouth pins | NEVER_PUBLISH — **not in fixture** |
| Lobster trap GPS, whale locations | NEVER_PUBLISH — **not in fixture** |
| Individual tag tracks | Tag program citation only |
| SoundToxins **station GPS** or live cell tables presented as “safe to harvest” | Not a harvest product; stations not stored |
| WDOH **open/closed as FishAI authorization** | Official status may be **linked**, never modeled as ours |
| AIS/VMS | Not in this graph |
| User/crew identity | Not in this graph |

The Chinook and lobster species **cards** on a public observatory site, if they exist at all, stay at coarsened stock/region grain. Mixed-stock ocean Chinook is `COARSENED`. No “go here.”

---

## 4. Field-level map (Farm node)

| Property | PRIVATE store | PUBLIC page |
|----------|---------------|-------------|
| `partner_id` | yes (opaque) | **no** |
| `culture_method_class` | yes | Only as a **generic** Willapa method list, not this farm |
| `official_growing_area_id` | yes | yes, as WDOH unit |
| `tidal_setting` | yes | Aggregated (“intertidal culture occurs in this estuary”) if ≥ rule-of-3 |
| yield / mortality / disease attributed | **forbidden in both** | — |
| lat/lon / corners | **forbidden in both** | — |

---

## 5. Reverse-engineering tests (before any page ships)

A PUBLIC page **fails** if a user can:

- Recover the fixture farm or a real lease within 500 m.  
- Isolate one farm by toggling culture method + growing area + sensor presence.  
- Combine the page with the WDOH map viewer to name a non-consenting grower as a model partner.  
- Treat SoundToxins or WDOH badges as “the oysters are dying” or “safe to harvest.”

The fixture is designed so the PUBLIC view is **estuary + official unit + mechanism + citations**. That is intentional.

---

## 6. Implementation sketch

```sql
CREATE VIEW public_nodes AS
SELECT * FROM nodes
WHERE privacy_tier IN ('PUBLIC', 'COARSENED')
  AND type <> 'AquacultureFarm'
  AND coalesce(json_extract(json, '$.geometry_policy'), '') <> 'NEVER_PUBLISH';

CREATE VIEW public_edges AS
SELECT e.* FROM edges e
JOIN public_nodes s ON s.id = e.subject
JOIN public_nodes o ON o.id = e.object
WHERE coalesce(e.privacy_tier, 'PUBLIC') IN ('PUBLIC', 'COARSENED', 'DELAYED')
  AND coalesce(json_extract(e.json, '$.geographic_applicability.geometry_policy'), 'NONE')
      NOT IN ('PRIVATE', 'NEVER_PUBLISH');
```

`DELAYED` rows stay out of the species page until embargo. Open weights and notebooks use `public_*` views only.

---

## 7. Fixture inventory for testers

| Tier | Count in fixture |
|------|------------------|
| PUBLIC nodes | 93 |
| PRIVATE nodes | 2 (farm + farm logger) |
| NEVER_PUBLISH nodes | **0** (omitted, not stubbed) |
| PRIVATE edges | **7** (farm OCCURS_IN / CULTURED_IN / ASSOCIATED_WITH / CONSTRAINED_BY, farm-logger MEASURES ×2, forecast ISSUED_FOR farm) |

If a future editor adds a `NEVER_PUBLISH` node “for completeness,” the PUBLIC loader must reject the file.
