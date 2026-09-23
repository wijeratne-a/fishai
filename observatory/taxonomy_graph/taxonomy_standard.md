# Taxonomy standard

**Authority of record for saltwater taxa:** World Register of Marine Species (WoRMS), Aphia identifiers.  
**Date:** 2026-09-18  
**Owner:** `TAXONOMY_AND_SPECIES_REGISTRY_AGENT`  
**Status:** Binding for the observatory registry, model factory, and any later join to OBIS/GBIF/FAO/COL.

This standard is a **naming and identity protocol**. It is not a distribution model.

---

## 1. Authority stack

| Role | System | Official URL | Rule |
|------|--------|--------------|------|
| **Marine taxonomic authority** | WoRMS / Aphia | https://www.marinespecies.org/ | Accepted scientific name + AphiaID are primary keys |
| Persistent identifier | LSID | `urn:lsid:marinespecies.org:taxname:{AphiaID}` | Store alongside AphiaID |
| Machine lookup | WoRMS REST | https://www.marinespecies.org/rest/ | Catalog-only lookups; no bulk mirror this pass |
| Occurrence networks | OBIS, GBIF | https://obis.org/ · https://www.gbif.org/ | Join on AphiaID (OBIS) or on synonym-resolved names (GBIF). Occurrence ≠ taxonomy. |
| Threat status | IUCN Red List | https://www.iucnredlist.org/ | Status is not a taxon ID. Do not treat IUCN as a second species. Spatial layers: rights + harm review before any use; default do not download. |
| Fishery statistical names | FAO ASFIS | https://www.fao.org/fishery/en/collection/asfis | 3-alpha codes are statistical items, not always 1:1 with WoRMS species. Subspecies are not in ASFIS. |
| Cross-domain catalogue | Catalogue of Life | https://www.catalogueoflife.org/ | Use to reconcile non-marine synonyms. **If COL and WoRMS disagree on a marine taxon, WoRMS wins for this observatory** until an editor decision is recorded. |
| National lists | ITIS, NOAA Fisheries pages, etc. | various | Index as vernacular/agency labels. Do not split one biological species into two registry rows because agencies lag a genus move. |

**Access date for URLs in this document:** 2026-09-18.  
**Licenses:** `UNKNOWN` unless a later rights pass records a verified licence for a specific reuse.

WoRMS is also a backbone contributor to OBIS, GOOS biological data, and COL (see WoRMS about: https://marinespecies.org/about.php). COL 2026 Extended Release programmatically integrates many sources; mismatches can occur. Record both IDs; do not silently merge.

---

## 2. Canonical taxon record (minimum fields)

Every registry row and every model must carry:

| Field | Requirement |
|-------|-------------|
| `worms_aphiaid` | Integer AphiaID of the **accepted** name |
| `lsid` | `urn:lsid:marinespecies.org:taxname:{AphiaID}` |
| `scientific_name_accepted` | Exact WoRMS accepted name |
| `scientific_authority` | Authorship string from WoRMS |
| `worms_status` | `accepted` / `unaccepted` / `superseded combination` / `unavailable name` / etc. |
| `valid_aphiaid` | If unaccepted, pointer to accepted |
| `principal_synonyms[]` | At least the names needed to join FAO, NOAA, industry, and legacy papers |
| `common_names[]` | Disambiguated; flag collisions |
| `rank` | species, genus, … |
| `kingdom` … `family` | From WoRMS classification |
| `environment_flags` | marine / brackish / freshwater / terrestrial as WoRMS states them |
| `life_stage` | See §4. Default `unspecified_mixed` is allowed only at T0–T1 |
| `population_unit` | See §5. Default `not_partitioned` |
| `support_tier` | T0–T6 |
| `access_date` | ISO date the WoRMS record was checked |
| `license_status` | `UNKNOWN` until verified |

Unaccepted names **may** exist as alias rows but must not receive their own support tier. They redirect.

Example (commercial-wedge alignment, not a product lock):

- Accepted: *Magallana gigas* (Thunberg, 1793), AphiaID **836033**, LSID `urn:lsid:marinespecies.org:taxname:836033`  
- Required alias: *Crassostrea gigas* (Thunberg, 1793), AphiaID **140656**, status superseded combination  
- Do **not** treat Portuguese oyster *Magallana angulata* as a synonym  
- Do **not** treat Olympia oyster *Ostrea lurida* as a synonym  

Verified 2026-09-18 via WoRMS REST `AphiaRecordsByName` and the taxon page https://www.marinespecies.org/aphia.php?p=taxdetails&id=836033

---

## 3. Marine vs estuarine vs freshwater rules

The observatory scope is **saltwater marine life**, including organisms that use **brackish / estuarine** waters as part of a marine life history.

### 3.1 In scope

| Case | Rule | Example |
|------|------|---------|
| Marine stenohaline | In | *Thunnus thynnus* |
| Marine + brackish | In | *Mytilus edulis*, *Magallana gigas* (WoRMS environment: marine, brackish, …) |
| Anadromous / catadromous / amphidromous **ocean phase** | Ocean and estuary phases in; freshwater spawning/rearing as **life-stage partitions**, not as a freshwater product | Chinook *Oncorhynchus tshawytscha*: ocean-phase adults are in; eggs in gravel are a freshwater stage of a marine-associated species |
| Estuarine residents | In, with explicit salinity domain | Many crabs, oysters, seagrasses |
| Ocean-associated seabirds | In when the question is marine distribution; breeding-colony maps are **sensitive** and usually `NEVER_PUBLISH` at nest resolution | *Phoebastria immutabilis* |
| Marine microbes, plankton, larvae | In | *Prochlorococcus marinus*; oyster larvae |

### 3.2 Out of scope unless a documented saltwater phase exists

| Case | Rule |
|------|------|
| Obligate freshwater fishes, mussels, plants | Out |
| Terrestrial stages with no marine ecology | Out |
| Human pathogens in seawater that are not marine organisms of interest | Out of the **species twin**; may appear as water-quality context in a different layer |

### 3.3 How to record mixed environments

Store WoRMS `isMarine`, `isBrackish`, `isFreshwater`, `isTerrestrial` when retrieved. For models:

1. Declare the **salinity domain** of the estimate (oceanic, coastal, estuarine, tidal freshwater).  
2. Do not train an ocean model on inland freshwater occurrences without a life-stage filter.  
3. Do not treat an estuary polygon as “the ocean” or as “inland.”  
4. Diadromous taxa **must** have life-stage rows or a `population_unit` that names the phase (e.g. `ocean_immature_adult` vs `freshwater_juvenile`). Mixing juvenile river data into an ocean encounter model is a known failure mode (documented in the commercial Chinook dossier).

### 3.4 Introduced marine species

Introduced/culture species (Pacific oyster in Washington) remain in the registry as the same AphiaID. Geography of introduction is a **distribution fact**, not a new taxon. Mark `introduction_status` when known from WoRMS notes; do not invent invasion maps.

---

## 4. Life stages

Life stage is a first-class dimension. Eggs, larvae, juveniles, adults, spawning aggregations, and resting stages often differ in habitat, observability, and legal protection.

**Controlled vocabulary (initial):**

| Code | Meaning |
|------|---------|
| `unspecified_mixed` | Records do not separate stages; T0–T1 only unless proven harmless |
| `egg` | |
| `larva` | Including planktonic veligers, phyllosoma, etc. |
| `spore_or_propagule` | Algae, seagrass, microbes |
| `juvenile` | |
| `subadult` | |
| `adult` | |
| `spawning_adult` | Sensitive; coordinates default `NEVER_PUBLISH` |
| `brooding_or_ovigerous` | e.g. berried lobster; legal selectivity ≠ abundance |
| `colony` | Corals, some tunicates |
| `bloom_or_aggregation` | Plankton, jellyfish, Sargassum mats — still not a census of all cells |
| `farmed_growout` | Aquaculture stock already planted; operator-observed, usually `PRIVATE` |
| `tagged_individual` | T5 candidate only; not a population |

**Rules:**

1. A higher tier on adults does **not** automatically apply to larvae. Example: *Magallana gigas* farmed adults may be T2 for habitat/stress; veligers in the same CSV are T0.  
2. Spawning aggregations, natal beaches, and pupping/calving grounds are **population units + sensitive locations**, not public T2 layers.  
3. “Larval transport from an ocean model” is `MODEL-INFERRED` or `HYPOTHETICAL/RESEARCH MODE`, never `DIRECTLY OBSERVED`.  
4. Ploidy (triploid oysters) and hatchery vs wild (Chinook) are **attributes of a population unit**, not species.

---

## 5. Stock, population, ESU, and other partitions

WoRMS identifies **species** (and higher/lower ranks). Fisheries and conservation identify **populations**.

This observatory stores population units as children of an AphiaID:

| Unit type | Examples | Public mapping rule |
|-----------|----------|---------------------|
| Biological population / stock | ASMFC GOM/GBK vs SNE lobster | Coarse; do not publish tow-level CPUE |
| Management area | PFMC ocean salmon zones; Maine lobster zones; WA DOH growing areas | Official polygons may be linked **as geography**, not as species |
| ESU / DPS / listed unit | California Coastal Chinook, Sacramento winter-run | **Do not emit precise locations or targeting layers** |
| Distinct breeding colony / rookery | Albatross, turtles, seals | `NEVER_PUBLISH` at nest/haulout resolution |
| Aquaculture line / ploidy | Triploid *M. gigas* | Private farm metadata |
| Genetic stock identified by GSI/CWT | Ocean Chinook mix | Mixing context, not a hotspot map |

**Naming:** `population_unit = "{scheme}:{id}"` e.g. `PFMC:ocean_SF_recreational` or `not_partitioned`.

**Never** give a population unit a second AphiaID. **Never** treat “king salmon” and “Chinook” as two species. **Never** treat *Manta birostris* and *Mobula birostris* as two species: WoRMS accepts **Mobula birostris** AphiaID **1026118**; *Manta birostris* AphiaID 105857 is unaccepted (verified 2026-09-18).

---

## 6. Common-name collisions (mandatory disambiguation)

Before a common name enters any UI or CSV:

1. Resolve via WoRMS vernaculars when present.  
2. Record collisions explicitly.

Known traps already in the commercial dossier (retain):

| String | Risk | Correct handling |
|--------|------|------------------|
| Portuguese oyster | Applied on some *gigas* pages; true Portuguese oyster is *Magallana angulata* | Never synonymize |
| Oysters (WA DOH maps) | Growing-area food-safety geography, mixed taxa | Geography, not taxonomy |
| King salmon | Chinook | Same as *O. tshawytscha* |
| Silver / coho | Different species *O. kisutch* | Separate AphiaID |
| Lobster | Clawed *Homarus* vs spiny *Panulirus* | Separate families |
| Portuguese vs Pacific oyster | See above | |
| “Manta ray” | *Mobula birostris* accepted | Use accepted genus |
| *Emiliania huxleyi* | WoRMS unaccepted | Accepted **Gephyrocapsa huxleyi** AphiaID **236056** (verified 2026-09-18) |
| *Candidatus Pelagibacter ubique* | WoRMS status **unavailable name** | May exist as T0 with that status; do not pretend it is a fully available species name |

---

## 7. Joining external catalogues

| Join | Method | Failure mode |
|------|--------|--------------|
| OBIS | `taxonid` = AphiaID | Children/synonyms may be rolled up or not; record whether request used accepted ID only |
| GBIF | Scientific name + backbone key when known | GBIF backbone may lag WoRMS genus moves (*Magallana* vs *Crassostrea*) — query both |
| FAO ASFIS | Scientific name in the annual ASFIS list | ASFIS still uses *Crassostrea gigas* for Pacific cupped oyster; store ASFIS 3-alpha as an alias when verified |
| IUCN | Scientific name / SIS id | Assessment may use a synonym; IUCN category is not occurrence |
| NCBI / GenBank | taxid | Required for eDNA reference; molecular ID ≠ visual ID |
| NOAA / ICES / FAO fact sheets | Species pages | Agency common names |

Until a 3-alpha code is read from the official ASFIS 2026 list, CSV field `fao_asfis_3alpha` stays `UNKNOWN`.

---

## 8. What taxonomy does not decide

- Presence, abundance, or legal take.  
- Whether a model is validated.  
- Whether coordinates may be published (harm review does).  
- Freshwater products.  
- The commercial 1×1×1×1 wedge. Taxonomy alignment with W1/W2/W3 is **identity only**.

---

## 9. Change control

1. Re-resolve AphiaIDs when WoRMS `modified` date on a used taxon is newer than `access_date`.  
2. If an accepted name changes (e.g. *Crassostrea* → *Magallana*), keep the old AphiaID as alias; migrate models under the accepted ID; do not drop historical joins.  
3. Splits: freeze old models; new rows start at T0 until evidence is re-attributed.  
4. All taxonomy lookups this pass: modest REST/name resolution only; **no WoRMS dump ingest**.
