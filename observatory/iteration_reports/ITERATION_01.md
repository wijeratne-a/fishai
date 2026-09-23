# Iteration 01 — Taxonomy and species-support framework

**iteration_id:** `ITERATION_01`  
**date:** 2026-09-18  
**state:** `STATE_0_CONFIGURE` → `STATE_1_FRAMEWORK`  
**responsible_agent:** `TAXONOMY_AND_SPECIES_REGISTRY_AGENT` (+ orchestrator duties)  
**target question:** What identity system, support tiers, and factory process can a saltwater-life observatory use without claiming global tracking?  
**hypothesis:** Most taxa are T0–T2; T3–T6 require evidence this program does not have; WoRMS/Aphia is a sufficient marine authority if synonyms and life stages are first-class.  
**decision:** **continue** (framework in place; do not ingest; do not widen the commercial wedge)

---

## Agent workstreams this iteration

| Stream | This iteration |
|--------|----------------|
| Orchestrator | Directory skeleton under `observatory/` only; `project_state.json`; README relating observatory to commercial wedge |
| Taxonomy | `taxonomy_graph/taxonomy_standard.md` |
| Registry | `global_species_registry/*`, `species_support_tiers.csv` (27 rows) |
| Factory | `species_model_factory.md` steps 1–8 |
| Contract | `user_output_contract.md` |
| Checkpoint | `checkpoints/CHECKPOINT_2026-09-18T2235.md` |

Sibling streams (modalities, hypotheses, architecture, rights, cost, red team) wrote other files in parallel. This report does not claim their results as this agent’s validation.

---

## Evidence gathered

- WoRMS REST accepted-name records for example taxa (2026-09-18), including: *Magallana gigas* 836033; *Oncorhynchus tshawytscha* 158075; *Homarus americanus* 156134; *Mobula birostris* 1026118 (not *Manta*); *Gephyrocapsa huxleyi* 236056 (not *Emiliania*); *Candidatus Pelagibacter ubique* 573763 unavailable name.  
- OBIS occurrence **totals** (metadata `size=0`), e.g. *Gadus morhua* 3 116 403; *Homarus americanus* 921 007; *Pseudoliparis swirei* 2; *Nemopilema nomurai* 37. **No points downloaded.**  
- Commercial wedge still UNRESOLVED / paused (`/Users/wijeratne/dev/fishai/project_state.json` observed `STATE_10_PAUSED_FOR_HUMAN_DECISION`). Recommended W1 Pacific oyster is **not decided**.

---

## Data sources and licenses

| Source | Official URL | Use | License |
|--------|--------------|-----|---------|
| WoRMS | https://www.marinespecies.org/ | Authority | `UNKNOWN` |
| OBIS | https://obis.org/ | Count metadata | `UNKNOWN` |
| GBIF | https://www.gbif.org/ | Cited, not extracted | `UNKNOWN` |
| IUCN Red List | https://www.iucnredlist.org/ | Cited as threat authority; no spatial download | `UNKNOWN` |
| FAO ASFIS | https://www.fao.org/fishery/en/collection/asfis | Collection cited; 3-alpha `UNKNOWN` | `UNKNOWN` |
| Catalogue of Life | https://www.catalogueoflife.org/ | Cross-walk cited | `UNKNOWN` |

Access date: **2026-09-18**.

---

## Technical result

- Support-tier framework T0–T6 with upgrade gates and safety caps.  
- Example tier counts: **T0=4, T1=14, T2=9, T3=0, T4=0, T5=0, T6=0**.  
- Factory defined; **no model trained; no map published**.  
- Current observatory emission for all example taxa: `UNKNOWN/INSUFFICIENT DATA`.

---

## Validation result

Not started for any biological model (`latest_validation_status: not_started`).  
Tier assignments are **catalog judgments** from identity + occurrence counts + a few official species/habitat pages. They are not peer-reviewed by a human taxonomist this iteration.

---

## Uncertainty

High that the 27-row set is incomplete (by design).  
High that many T1 taxa could become T2 after a cited envelope pass — **not done**, so not upgraded.  
High that public T2 for sharks, turtles, mammals, and elkhorn coral would be harmful; those are capped at T1 even when data are richer.  
Low confidence in any global coverage timeline.

---

## Limitations

- 27 examples ≠ global registry.  
- OBIS `total` mixes methods and effort.  
- FAO 3-alpha codes not copied from the 2026 ASFIS file.  
- No ecology-profile cards yet.  
- External telemetry does not justify T5 without ingest + rights + individual≠population UX.  
- This agent is not a substitute for WoRMS editors or NOAA stock-assessment scientists.

---

## Red-team findings (adopted)

Sibling `scientific_red_team_reports/observatory_red_team_01.md`: global “track everything” is **not** scientifically identified; T3–T6 count must stay 0 until evidence; fusion cannot create a census. This iteration complied: no T3+.

---

## Cost estimate

Framework writing only (labor inside the 72 h budget). No sensor spend. Prototype designs used: **0 / 10**. Hypothesis iterations used: **0 / 12**. Data-source discovery passes used: **1 / 5** (taxonomy/OBIS metadata).

---

## Readiness level

**Taxonomy Layer 0:** usable as a protocol.  
**Species models:** none.  
**Digital twin:** design-only (siblings).  
**Product:** none. Commercial wedge remains paused.

---

## Next action

1. Leave `fishai/artifacts/` untouched.  
2. Do not upgrade CSV tiers.  
3. Let rights, modality, and catalog agents finish source-family work.  
4. If a later pass writes ecology profiles, start with the nine T2 taxa and keep output class `HYPOTHETICAL/RESEARCH MODE` until Step 6 validation exists.  
5. Next checkpoint per 4 h interval or on transition toward `STATE_2_MODALITY_AND_HYPOTHESIS_RESEARCH` synthesis.

**Continue.** Do not prototype a world animal map.
