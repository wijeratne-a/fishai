# Ontology — marine biological knowledge graph

**Date:** 2026-09-18  
**Namespace:** `urn:fishai:observatory:kg:`  
**Taxonomy authority:** WoRMS / Aphia (`../taxonomy_graph/taxonomy_standard.md`)  
**Edge payload:** `edge_metadata_schema.json` (required on **every** edge)  
**Fixture:** `example_graph_gigas.jsonld`

This ontology is a **constraint system** for ecological claims. It does not assert that FishAI has a live global twin.

---

## 1. Identity rules

1. One accepted marine species = one `Species` node keyed by WoRMS AphiaID and LSID.  
2. Unaccepted names are `Taxon` alias nodes with `valid_aphiaid`. They never get their own support tier or model.  
3. Stocks, ESUs, aquaculture lines, and ploidy are `StockPopulation` children of an AphiaID — **never** a second AphiaID.  
4. Life stage is first-class. A model on `ocean_immature_adult` Chinook does not apply to `farmed_growout` oysters, or even to *gigas* `larva`.  
5. `privacy_tier` is stored on nodes. `NEVER_PUBLISH` geometry is not a public node. Official MPA / growing-area polygons may exist **as the authority publishes them**.  
6. Aquaculture `Farm` nodes are `PRIVATE`, carry **no performance** (no mortality %, yield, disease attributed to a named farm), and no lease-corner coordinates.

### Seed taxa (from marine_domain; REST-checked 2026-09-18)

| Accepted name | AphiaID | LSID | Role in this graph |
|---------------|---------|------|--------------------|
| *Magallana gigas* (Thunberg, 1793) | **836033** | `urn:lsid:marinespecies.org:taxname:836033` | W1 fixture species |
| *Crassostrea gigas* (Thunberg, 1793) | 140656 | unaccepted / superseded combination of 836033 | Required join synonym |
| *Oncorhynchus tshawytscha* (Walbaum, 1792) | **158075** | `urn:lsid:marinespecies.org:taxname:158075` | Transfer-block contrast |
| *Homarus americanus* H. Milne Edwards, 1837 | **156134** | `urn:lsid:marinespecies.org:taxname:156134` | Transfer-block contrast |
| *Ostrea lurida* P. P. Carpenter, 1864 | 542155 | | Native oyster; 2021 mortality contrast; **not** a *gigas* synonym |
| *Magallana angulata* (Lamarck, 1819) | 1039387 | | Portuguese oyster; **never** synonymized with *gigas* |
| *Heterosigma akashiwo* | 160585 | | HAB taxon that can stress **the animal** |
| *Alexandrium catenella* | 231873 | | HAB taxon that drives **NSSP harvest** toxins, not ops-stress |
| *Protoceratium reticulatum* | 110321 | | Yessotoxins; mixed animal-stress vs harvest — keep split |

---

## 2. Classes

| Class | Key | Notes |
|-------|-----|-------|
| **Species** | `worms_aphiaid` | Accepted name only |
| **Taxon** | AphiaID, possibly unaccepted | Higher ranks, synonyms |
| **StockPopulation** | `{scheme}:{id}` | Farmed introduced *gigas*; CA/OR mixed ocean Chinook; GOM/GBK lobster. Listed ESUs may be named **without geometry**. |
| **LifeStage** | taxonomy_standard codes | `farmed_growout`, `larva`, `ocean_immature_adult`, `legal_benthic_adult`, … |
| **Habitat** | culture or biome class | Intertidal bag vs subtidal off-bottom vs shelf pelagic |
| **OceanRegion** | named basin / estuary | Willapa Bay, Hood Canal, CA/OR shelf, GOM coarse. No trap or nest GPS. |
| **DepthZone** | twin depth-bin ids | `INTERTIDAL_AIR`, `SURFACE_0_5`, `SUBTIDAL_BOTTOM`, `SHELF_THERMAL_BAND` |
| **EnvironmentalVariable** | **EMIV id** | Registry `v0.1-draft` (`EMIV-PHY-ATEMP-001`, …). Graph URN `@id`s keep the old slug path |
| **ToleranceRange** | species × stage × EMIV | Envelopes with citation; FAO floors are not no-effect levels |
| **Prey** | taxon or resource guild | Seston/phytoplankton for *gigas* **growth**, not 72 h mortality |
| **Predator** | taxon or guild | Not a 72 h Willapa ops driver in the marine_domain dossier |
| **Disease** | name | OsHV-1: causal **where present**; not a WA 72 h driver without PCR |
| **Parasite** | name | Fixture: not asserted as a Willapa 72 h driver |
| **Survey** | program | SoundToxins, NANOOS NVS, WSG Rapid Response |
| **Observation** | event or paper-derived fact | Coarsened; no lease pins |
| **Sensor** | network or class | CO-OPS, NWS, NANOOS; farm loggers `PRIVATE` without GPS |
| **Tag** | program, not animal | Chinook archival tags (Hinke). No tracks in the graph |
| **Model** | version + target | Includes **rejected** models so transfers can be blocked |
| **Publication** | DOI or official URL | Cited, not copied |
| **DataSource** | catalog | WoRMS, NOAA Fisheries, WA DOH, SoundToxins, NANOOS, CO-OPS |
| **Fishery** | named fishery | WDFW Willapa oyster reserves — not the 72 h farm-stress label |
| **AquacultureFarm** | opaque partner id | **PRIVATE**; no performance fields |
| **ProtectedArea** | official id | Link authority outline only |
| **RegulatoryConstraint** | official unit | WDOH growing area, NSSP class, Vp controls — **display ≠ ops score** |
| **HumanPressure** | named pressure | Heat dome, handling, runoff |
| **Forecast** | forecast_id | Append-only issued state pointer; fixture is hypothetical |
| **ValidationResult** | split + status | Fixture: protocol only / not ready |
| **Hypothesis** | H-id | Competing mechanisms |
| **TransferConstraint** | rule id | Machine-checkable FORBIDDEN_TRANSFER |

### 2.1 EMIV ids (registry `v0.1-draft`)

`observatory/emiv/` **`v0.1-draft`** is the catalog. These were provisional slugs matching `artifacts/marine_domain/variable_relevance_matrix.csv`; `emiv_id` is now the registry ID. Graph `@id` URNs are unchanged. Compound: `emiv:wind_wave` → `EMIV-PHY-WIND-001|EMIV-PHY-WAVE-001`. Tide stage is not a separate KG node (folded into emersion; use `EMIV-PHY-TIDE-001` from the registry). Crosswalk: [`../emiv/engine_id_crosswalk.md`](../emiv/engine_id_crosswalk.md).

| EMIV id | Variable | *gigas* 72 h ops-stress | Chinook 24–48 h encounter | Lobster next-trip CPUE |
|---------|----------|-------------------------|---------------------------|------------------------|
| `EMIV-PHY-ATEMP-001` | Air temperature | **MECHANISTIC_CAUSAL** with emersion (intertidal) | NOT_APPLICABLE | NOT_APPLICABLE |
| `EMIV-PHY-EMERS-001` | Tide / aerial exposure | **MECHANISTIC_CAUSAL** modulator | NOT_APPLICABLE (offshore troll) | UNKNOWN / unverified |
| `EMIV-PHY-SOLAR-001` | Incoming solar / insolation (emersion) | **MECHANISTIC_CAUSAL** with air × emersion; **not chlorophyll** | NOT_APPLICABLE | NOT_APPLICABLE |
| `EMIV-PHY-TISST-001` | Tissue / bag / bed thermistor T | Organism/gear thermal state; W1_CORE if partner sensor else CANDIDATE | NOT_APPLICABLE | NOT_APPLICABLE |
| `EMIV-PHY-WTEMP-001` | In situ water T | MECHANISTIC_CAUSAL | Use with depth; not SST-as-count | PROXY for bottom T |
| `EMIV-BGC-DOXY-001` | DO | MECHANISTIC_CAUSAL; local; sparse in Willapa | Habitat edge only | WRONG_GEOGRAPHY if copied from SNE |
| `EMIV-PHY-SALIN-001` | Salinity | MECHANISTIC_CAUSAL after runoff | Weak | Weak in GOM inshore |
| `EMIV-PHY-WIND-001\|EMIV-PHY-WAVE-001` | Storms / wind / waves | MECHANISTIC_CAUSAL for **disruption** | CONFOUNDER for realized encounter | CONFOUNDER for haulability |
| `EMIV-PHY-SST-001` | Skin SST | PROXY only; **not** tissue T; not abundance | PROXY for thermal habitat; fish may go deeper | PROXY; poor substitute for bottom T |
| `EMIV-BGC-CHL-001` | Chl-a | PROXY for **growth**; not 72 h mortality; never abundance | PROXY / WRONG_STAGE if juvenile papers used for adults | PROXY; never abundance |
| `EMIV-BGC-OMEGA-001` | Ω_aragonite / pH family | MECHANISTIC_CAUSAL for **larva**; WRONG_STAGE for adult bags | NOT_APPLICABLE at 48 h | NOT_APPLICABLE at next trip |
| `EMIV-BGC-FECAL-001` | NSSP fecal indicator | **WRONG_TARGET** for animal stress | NOT_APPLICABLE | NOT_APPLICABLE |
| `EMIV-PHY-WTEMP-003` | Bottom T | NOT_APPLICABLE for intertidal air heat | Subsurface T related | MECHANISTIC_CAUSAL for **catchability** |
| `EMIV-ECO-HAB-001` | Named HAB cells that affect the **animal** | Conditional MECHANISTIC_CAUSAL (*Heterosigma*, *Protoceratium*) | NOT_APPLICABLE | NOT_APPLICABLE |

SoundToxins cell counts of *Alexandrium* bind to **RegulatoryConstraint** (harvest toxin / `EMIV-HUM-HARV-001`), not to `EMIV-ECO-HAB-001`.

---

## 3. Relations (predicates)

Every instance is a `KnowledgeEdge` with the metadata in `edge_metadata_schema.json`.

| Predicate | Typical domain → range | Meaning |
|-----------|------------------------|---------|
| `HAS_LIFE_STAGE` | Species → LifeStage | Stage exists for this taxon |
| `HAS_SYNONYM` | Species → Taxon | Unaccepted name for joins |
| `PARTITION_OF` | StockPopulation → Species | Stock/ESU/farmed line |
| `OCCURS_IN` | Species/Stock/Farm → OceanRegion | Distribution **fact** at declared grain — not a pin |
| `CULTURED_IN` | StockPopulation → Habitat | Intertidal vs subtidal vs bottom |
| `PREFERS_DEPTH` | Species+LifeStage → DepthZone | Habitat depth, not a hotspot |
| `ASSOCIATED_WITH` | any → any | Weak / mixed; prefer a tighter predicate |
| `RELEVANT_EMIV` | Species → EnvironmentalVariable | Use in this decision × stage × region |
| `IRRELEVANT_EMIV` | Species → EnvironmentalVariable | Available but not this question |
| `HAS_TOLERANCE` | Species → ToleranceRange | Envelope; stage-scoped |
| `PREYS_ON` | Species → Prey | Diet; timescale on the edge |
| `PREYED_ON_BY` | Species → Predator | Inverse |
| `AVOIDS` | Species → EMIV or Habitat | Behavioral/physiological avoidance (e.g. aerial extremes) |
| `HOSTS_DISEASE` | Species → Disease | Presence **not** assumed from another coast |
| `HOSTS_PARASITE` | Species → Parasite | |
| `SAMPLED_BY` | Species/HAB → Survey | |
| `OBSERVED_IN` | Observation → Region/Habitat | Coarsened |
| `OBSERVED_BY` | Observation → Sensor/Survey/Publication | |
| `MEASURES` | Sensor → EnvironmentalVariable | |
| `TAGGED_BY` | Species → Tag program | No individual ids |
| `MODELED_BY` | Species+Decision → Model | |
| `USES_EMIV` | Model → EnvironmentalVariable | Feature allowlist |
| `VALIDATED_AGAINST` | Model/Forecast → ValidationResult | |
| `ISSUED_FOR` | Forecast → Species/Region/Farm | Farm ISSUED_FOR is PRIVATE |
| `CONSTRAINED_BY` | Species/Farm/Fishery → RegulatoryConstraint | Legal mask, not biology |
| `PRESSURED_BY` | Species/Habitat → HumanPressure | |
| `CITED_IN` | any → Publication | |
| `SOURCED_FROM` | any → DataSource | |
| `COMPETES_WITH` | Hypothesis → Hypothesis | |
| `SUPPORTS` | Observation/Publication → Hypothesis | |
| `CONFLICTS_WITH` | Edge or Hypothesis → Edge or Hypothesis | Materialized conflict |
| `FORBIDDEN_TRANSFER` | Model → Model or Species+Habitat | **Hard block** |
| `HAS_CONFIDENCE` | Model/Forecast/Edge-set → qualitative | Never fake ± |

---

## 4. Transfer constraints (cannot wish these away)

A model **M** trained or specified on `(taxon, life_stage, depth_zone, habitat_class, region, decision, emiv_set)` may be applied to a target **T** only if **all** hold:

1. **Taxon:** `T.aphiaid = M.aphiaid` OR a `DOMAIN_REVIEWED` analog edge exists (none in v0).  
2. **Life stage:** intersection of `life_stage_applicability` is non-empty.  
3. **Depth zone:** intersection non-empty (intertidal air ≠ shelf thermocline).  
4. **Habitat class:** culture method / biome compatible (oyster bag ≠ troll water).  
5. **Decision:** `decision_applicability` equal. Category **D** on Chinook (encounter) ≠ Category **D** on *gigas* (ops stress).  
6. **EMIVs:** every `USES_EMIV` with `causal_status=MECHANISTIC_CAUSAL` on M is `RELEVANT_EMIV` with compatible causal_status on T. PROXY-only features cannot become MECHANISTIC_CAUSAL on T by transfer.  
7. **Geography:** `geographic_applicability` overlaps **or** an explicit `WRONG_GEOGRAPHY` is absent and an extrapolation flag is set (v0: no silent basin hop. Willapa ≠ Hood Canal).  
8. **Causal status:** M has no `WRONG_*` status for T’s question.  
9. **No** `FORBIDDEN_TRANSFER` edge and no `TransferConstraint` match.  
10. **Privacy:** transfer must not materialize `NEVER_PUBLISH` or neighbor-farm geometry.

If any check fails, the factory emits `UNKNOWN/INSUFFICIENT DATA` or refuses the bind. It does **not** interpolate.

### 4.1 Canonical block — Chinook SST encounter ↛ Pacific oyster bags

**Do not** transfer a Chinook (`158075`) satellite-SST encounter model to *Magallana gigas* (`836033`) intertidal or subtidal bags.

| Check | Chinook source | *gigas* target | Result |
|-------|----------------|----------------|--------|
| Taxon | 158075 | 836033 | **Fail** |
| Life stage | `ocean_immature_adult` | `farmed_growout` | **Fail** |
| Depth | `SHELF_THERMAL_BAND` (fish dive when SST warms) | `INTERTIDAL_AIR` or `SUBTIDAL_BOTTOM` | **Fail** |
| Habitat | CA/OR shelf pelagic, mobile | Willapa leased bags, sessile planted stock | **Fail** |
| Decision | 24–48 h relative **encounter** in **open** water | 24–72 h **operational stress / work-window** | **Fail** (same letter D, different target) |
| Primary EMIV | `EMIV-PHY-SST-001` is **PROXY** for 8–12 °C habitat; SST-as-count is WRONG_TARGET | `EMIV-PHY-ATEMP-001` × `EMIV-PHY-EMERS-001` × `EMIV-PHY-SOLAR-001` is **MECHANISTIC_CAUSAL** (tissue T is `EMIV-PHY-TISST-001`, not SST); SST misses aerial heat and emersion | **Fail** |
| Mobility | Highly mobile | Sessile after settlement | **Fail** |
| Privacy | ESA mixed-stock; no ESU pins | Farm PRIVATE; no performance | Different rails; still no transfer |

**Machine edge:** `kg:constraint/block_chinook_sst_to_gigas_bags` with predicate `FORBIDDEN_TRANSFER`.

Other v0 blocks in the fixture:

| Constraint | Why |
|------------|-----|
| Larval Ω_aragonite model → adult 72 h bags | `WRONG_STAGE` (2009 seed crisis ≠ market-bag mortality) |
| WA DOH growing-area class → ops-stress label | `WRONG_TARGET` (NSSP harvest legality) |
| SoundToxins *Alexandrium* cells → ops-stress score | Harvest toxin, not animal stress |
| OsHV-1 CA timing → Willapa 72 h | `WRONG_GEOGRAPHY`; 2020 OR/WA sentinels did not detect virus |
| Hood Canal hypoxia model → Willapa without basin id | `WRONG_GEOGRAPHY` |
| SNE / LIS hypoxia → GOM lobster CPUE | `WRONG_GEOGRAPHY` |
| Juvenile chl-nearshore Chinook papers → adult charter | `WRONG_STAGE` |
| Satellite SST → lobster abundance or GOM catchability | PROXY / WRONG_TARGET; need **bottom** T |
| AIS vessel density → any abundance | WRONG_TARGET (project non-negotiable) |

---

## 5. W1 Willapa encoding (normative for the fixture)

**Species:** *Magallana gigas* 836033, stock `wa_introduced_farmed`, stages `farmed_growout` (spat through market) and `larva` (out of the 72 h farm-ops decision).

**Habitats (must stratify):**

- Intertidal bag / longline / tumble: aerial heat × daytime low tide.  
- Subtidal / raft: water-column heat, DO, HAB exposure; less aerial heat.  
- Bottom culture: more like subtidal physiology + burial/storm disruption; Willapa “fattening line” is **seasonal growth**, not 72 h mortality.

**Regulatory vs biology (hard wall):**

- `RegulatoryConstraint` `WA_DOH_GROWING_AREA:Willapa-Nahcotta-fixture` **frames geography** and **constrains harvest**. It is not the stress target.  
- SoundToxins is a `Survey` + `DataSource`. *Heterosigma* / *Protoceratium* may `ASSOCIATED_WITH` animal-stress HAB EMIV. *Alexandrium* `CONSTRAINED_BY` NSSP. **Do not** print SoundToxins as an operations label.

**Farm:** one PRIVATE fixture `farm:W1_FIXTURE_PRIVATE_LEASE_ZONE_B`. Properties allowed: opaque id, culture-method class, intertidal vs subtidal flag, growing-area **name**. Properties **forbidden:** yield, mortality, genetics, buyer, lease corners, neighbor ids.

**Forecast:** synthetic Category D indicator, `HYPOTHETICAL_RESEARCH`, `validation:protocol_only`. Not a customer claim.

---

## 6. Node property minima

Every node:

| Field | Rule |
|-------|------|
| `@id` | `urn:fishai:observatory:kg:…` |
| `@type` | One class from §2 |
| `privacy_tier` | Default `PUBLIC` for literature/taxonomy; farms `PRIVATE` |
| `last_updated` | 2026-09-18 for this fixture |

Species additionally: `worms_aphiaid`, `lsid`, `scientific_name_accepted`, `worms_status`, `access_date`.

Models additionally: `taxon_aphiaid`, `life_stage`, `decision_applicability`, `emiv_allowlist[]`, `support_tier_ceiling`.

---

## 7. Cardinality and integrity

- A `Species` must have ≥1 `HAS_LIFE_STAGE`.  
- A `RELEVANT_EMIV` edge must set `decision_applicability` and `causal_status`.  
- `FORBIDDEN_TRANSFER` edges have `review_status` at least `EDITOR_DRAFT`.  
- `Farm` must not contain keys `mortality`, `yield`, `kpi`, `latitude`, `longitude`, `lease_corners`.  
- No node with `privacy_tier=NEVER_PUBLISH` may appear in the PUBLIC projection. Prefer **omission** over a stub that invites a coordinate.  
- `CONSTRAINED_BY` a food-safety authority never implies `RELEVANT_EMIV` for ops-stress.

---

## 8. `causal_status` (proposed causal-engine enum)

`observatory/causal_ecology/` was absent. This enum is the **alignment target**. Map from marine_domain `causal_or_proxy`:

| marine_domain string | Graph `causal_status` |
|----------------------|------------------------|
| `causal`, `causal_for_habitat`, `causal_for_where`, `causal_if_named_taxon`, `causal_where_present` | `MECHANISTIC_CAUSAL` |
| `causal_for_catchability`, `causal_for_realized_encounter`, `causal_for_opportunity`, `causal_confounder` | `CONFOUNDER` or `MECHANISTIC_CAUSAL` of **catchability/opportunity**, never of abundance — set `prediction_contract_category` accordingly |
| `proxy`, `proxy_for_*`, `proxy_stage_dependent` | `PROXY` |
| `wrong_target`, `wrong_target_if_as_abundance` | `WRONG_TARGET` |
| `wrong_timescale` | `WRONG_TIMESCALE` |
| `wrong_geography_if_imported` | `WRONG_GEOGRAPHY` |
| `causal_for_larvae_proxy_for_adults` | split into two edges (larva MECHANISTIC_CAUSAL, adult WRONG_STAGE or PROXY) |
| `unverified`, `weak` | `UNKNOWN` or `HYPOTHETICAL` |
| `survey_context`, `causal_prior` | `ASSOCIATIVE` or `MECHANISTIC_CAUSAL` with `WRONG_TIMESCALE` for the 24–72 h decision |

---

## 9. What the ontology refuses to represent as public biology

- Exact catch, set, trap, charter, or lease waypoints  
- Farm performance and attributed disease outbreaks  
- ESA ESU holding pools, spawning aggregations, nests, haul-outs  
- AIS/VMS identity or density-as-abundance  
- SoundToxins or WDOH values as “safe to harvest” or “oysters dying”

Those absences are **features**. Missing-knowledge queries should report them as withheld or unknown, not as zeros.
