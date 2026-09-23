# Global species registry

**Owner:** `TAXONOMY_AND_SPECIES_REGISTRY_AGENT`  
**Date:** 2026-09-18  
**Status:** Framework + 27 example taxa. Not a complete catalog of saltwater life.  
**Authority:** World Register of Marine Species (WoRMS) / Aphia. See [`../taxonomy_graph/taxonomy_standard.md`](../taxonomy_graph/taxonomy_standard.md).

This registry is the Layer 0 index for the observatory. It records **what a taxon is**, **which support tier is evidence-justified**, and **what must not be claimed**.

It does **not** store occurrence points, tracks, eDNA sample coordinates, or farm/vessel microdata.

---

## What lives here

| File | Role |
|------|------|
| `README.md` | This index |
| `support_tier_framework.md` | T0–T6 rules, upgrade gates, output classes, forbidden inferences |
| [`../species_support_tiers.csv`](../species_support_tiers.csv) | Machine-readable example rows (~27 representative taxa) |

Later iterations may add per-taxon cards under this folder. Each card must cite WoRMS AphiaID, access date, and must not exceed the assigned tier.

---

## Example-row design (iteration 1)

Rows were chosen to span the long-horizon groups in the observatory spec (finfish, elasmobranchs, shellfish, crustaceans, cephalopods, marine mammals, sea turtles, ocean-associated seabirds, plankton, jellyfish, corals, benthic invertebrates, reef fishes, marine plants, algae, microbes, larval stages).

They are **illustrative**, not a priority list for productization.

The three commercial-wedge candidates appear so the programs stay taxonomically aligned without merging scope:

| Wedge candidate | AphiaID | Registry tier | Why not higher |
|-----------------|---------|---------------|----------------|
| Pacific oyster *Magallana gigas* | 836033 | T2 | FAO/NOAA habitat envelopes + OBIS occurrence exist. No observatory current-condition or 72 h forecast. Farm occupancy is private operational knowledge, not a global T5/T6 layer. |
| Chinook *Oncorhynchus tshawytscha* | 158075 | T2 | Historical occurrence + published thermal habitat exist. Annual stock assessments are not a 24–48 h current map. ESA ESU locations are not public targets. |
| American lobster *Homarus americanus* | 156134 | T2 | Surveys and habitat covariates exist at seasonal/stock scale. Trap CPUE is not abundance. No observatory next-trip forecast. |

**Counts in `species_support_tiers.csv`:** T0 = 4, T1 = 14, T2 = 9, T3 = 0, T4 = 0, T5 = 0, T6 = 0.

---

## Evidence used (catalog only)

Access date for all URLs: **2026-09-18**.

| Source | Official URL | Use in this registry | License this pass |
|--------|--------------|----------------------|-------------------|
| WoRMS / Aphia | https://www.marinespecies.org/ | Accepted names, AphiaIDs, synonyms, LSID | `UNKNOWN` (not re-verified for every reuse) |
| WoRMS REST | https://www.marinespecies.org/rest/ | Name lookup (`AphiaRecordsByName`) | `UNKNOWN` |
| OBIS | https://obis.org/ | Taxon occurrence **counts** via `api.obis.org/v3/occurrence?taxonid={AphiaID}&size=0` (metadata only; no point download) | `UNKNOWN` |
| GBIF | https://www.gbif.org/ | Cited as an occurrence network; no extract | `UNKNOWN` |
| IUCN Red List | https://www.iucnredlist.org/ | Cited as a threat-status authority; **no spatial downloads**; categories not copied into public maps | `UNKNOWN` (spatial products often non-commercial) |
| FAO ASFIS | https://www.fao.org/fishery/en/collection/asfis | Fishery statistical names; 3-alpha codes `UNKNOWN` until the 2026 ASFIS file is opened under rights review | `UNKNOWN` |
| Catalogue of Life | https://www.catalogueoflife.org/ | Cross-walk target; WoRMS remains marine authority of record | `UNKNOWN` |

Modest official API metadata lookups are cataloguing, not ingest. Occurrence **points were not downloaded**.

---

## Rules

1. One registry row = one accepted WoRMS taxon **plus** an explicit life-stage if the stage has different observability (e.g. oyster larva ≠ farmed adult).  
2. Freshwater-only taxa are out of scope unless a documented marine or estuarine life-history phase exists.  
3. Stocks, ESUs, DPSs, and aquaculture ploidy lines are **population units**, not extra species. They hang off the AphiaID.  
4. `support_tier` is the highest tier this observatory may **emit toward** given cited evidence **and** ecological-safety caps. `evidence_ceiling_tier` may be equal or higher when safety, not data, is the cap.  
5. `current_observatory_output_class` for every example row is `UNKNOWN/INSUFFICIENT DATA` until a factory run publishes a model. Tiers describe **eligibility**, not a live product.  
6. Do not add a row as T3+ because a paper, a stock assessment, or a commercial wedge exists. Those are inputs to a later factory pass.
