# Agent handoff — Active Observation Planner / information-gain engine

**Date:** 2026-09-18  
**Agent:** ACTIVE_OBSERVATION_PLANNER (information-gain engine designer)  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/observation_planner/` only  
**Did not write:** `fishai/globe/**`, commercial integration files, `artifacts/**`  
**Ingest:** none. **Field tasking:** none. **Counsel:** none.

---

## 1. Executive finding

The observatory must **not wait passively for data**. Rank the next observation by **uncertainty reduction and decision/scientific value**, not row count.

**W1 (first slice, FIXTURE):** the highest-value next observations are a **permissioned 30-second farm outcome form** and **air × tide × (existing bag/body) temperature** — not a glider in the open Pacific, not more SST, and **not WA DOH closure sampling**.

**Top 5 W1 recommended observation actions (fixture, not orders):**

| Rank | ID | Action | OVS | Privacy |
|---:|---|---|---:|---|
| 1 | W1-FIX-R01 | 30 s partner outcome form (`ops_disruption_72h`) | 0.658 | `PRIVATE` |
| 2 | W1-FIX-R02 | Public NWS air × CO-OPS tide × solar pairing | 0.613 | `PUBLIC` physics |
| 3 | W1-FIX-R03 | Culture method / elevation band / ploidy metadata | 0.573 | `PRIVATE` |
| 4 | W1-FIX-R04 | Export **existing** bag/bed thermistors | 0.566 | `PRIVATE` |
| 5 | W1-FIX-R05 | 14-day paper protocol if export fails | 0.529 | `PRIVATE` |

Ranks 6–8 (still recommended, lower): farm-specific workability threshold (0.492); mobile capture of the **same** form (0.443); existing **Willapa-in-basin** water T/S, explicitly not Hood Canal ORCA (0.380).

**Global planner status:** **design only**. Batch scorer on uncertainty tiles × EMIV coverage is specified, not implemented. No global animal map. No platform tasking.

**EMIV:** [`../emiv/`](../emiv/) registry **`v0.1-draft`** (84 rows). Planner stubs remapped where a registry row exists (`engine_id_crosswalk.md`). Unresolved local keys remain (taxon/geo/scores/B4 — **not** solar/bag-T). **DOH = `EMIV-HUM-HARV-001` constraint. SST = `EMIV-PHY-SST-001` PROXY.**

---

## 2. Evidence table

| Finding | Evidence | Confidence |
|---|---|---|
| W1 label is partner mortality/workability/intervention, not DOH closures | `ground_truth_relabel_W1.md`; marine-domain handoff; prediction contract §3 | High |
| 2021 mechanism is air × midday emersion, not SST census | Raymond et al. 2022; quality B4 rewrite; red team | High |
| 30 s form can beat a new sensor | `outcome_capture_spec.md`; ladder in `data_acquisition_plan.md`; OVS worked example | High as design; untested WTP |
| Hood Canal ORCA ≠ Willapa | data discovery gap analysis | High |
| Public biological globe is rejected | `sensitive_location_policy.md` §12 | High (policy) |
| Occupancy zeros ≠ absence | MacKenzie et al. 2002; uncertainty policy Chinook note | High (methods) |
| eDNA inverse to N is underdetermined | Andruszkiewicz 2019; DA design §2.5 | High |
| No fitted model / no labels in-repo | quality handoff Gate 3 | High |
| Fixture OVS numbers are uncalibrated | `scoring_spec.md` §6 | Certain |

---

## 3. Source / license table

No ingest. Citations already owned by sibling dossiers.

| Source | Use |
|---|---|
| `observatory/sensitive_location_policy.md` | Kill / coarsen / NEVER_PUBLISH |
| `artifacts/scientific_red_team/prediction_contract.md` | Claim language; oyster never-claims |
| `artifacts/marine_domain/**` | Covariate ranking; Willapa vs other basins |
| `artifacts/quality_and_validation/**` | B4, uncertainty, labels |
| `artifacts/data_discovery/**` | Ladder; DOH is constraint |
| `observatory/observation_modality_catalog.md` | Modality physics |
| `artifacts/product_and_monetization/outcome_capture_spec.md` | 30 s schema |
| WoRMS 836033 | Taxonomy |
| H3 restable (docs) | Res 5–6 grain |

Commercial reuse of NANOOS/LiveOcean/etc. remains **UNKNOWN** until rights review.

---

## 4. Confidence and limitations

| Item | Confidence | Limitation |
|---|---|---|
| W1 ranking direction (form + air×tide ≫ glider/SST/DOH) | High | OVS decimals are illustrative |
| Kill thresholds 0.50 / mosaic 0.70 | Medium | Hypothesis; human may tighten |
| Global VOI engine | Low | REQUIRES_RESEARCH_BREAKTHROUGH |
| Partner will actually log | Unknown | Completeness gates not observed |
| EMIV IDs | Bound to `v0.1-draft` | Unresolved stubs listed in `engine_id_crosswalk.md` |

---

## 5. Recommended decision

1. Treat this folder as the **planner contract**. Do not ship a public rec map.  
2. If W1 locks: collect **R01–R05** after DUA and human approval; pair public air×tide **without** calling it body T.  
3. Keep DOH as a **must-show constraint**, never as the next “sample plan” for ops GT.  
4. Do not stand up glider/eDNA/PAM tasking for W1.  
5. Registry IDs are live (`observatory/emiv/`); keep unresolved planner keys rather than minting a second ontology.

---

## 6. Harm / privacy kill rules (binding)

**Score override:** if `HarmPen ≥ 0.50` or `LegalPen ≥ 0.50` → **do not recommend**, even if OVS is large. Mosaic: `HarmPen + LegalPen ≥ 0.70` with both ≥ 0.30 → kill.

**Hard kills:** `NEVER_PUBLISH` targeting (nests, spawn aggregations, haul-outs, PAM bearings, rare eDNA GPS, lease corners, public farm KPIs); public rare-species pins; AIS-as-abundance; NSSP impersonation / DOH-as-ops-GT; hardware before ladder; unreviewed public biology; listed holding waters; auto-tasking without a named human.

**Ternary:** `SPECIES_ABSENT` ≠ `NOT_DETECTED` ≠ `NO_OBSERVATIONS`. Empty ocean is unknown, not zero.

Partner-private farm KPIs under DUA are allowed; **publishing** them is killed.

---

## 7. Rejected alternatives

| Rejected | Why |
|---|---|
| Passive ingest of whatever ERDDAP offers | Optimizes quantity |
| Open-Pacific glider for W1 | Wrong variable and grain |
| SST-first observation plan | Falsified mechanism |
| DOH closure assay as highest-value obs | Wrong target + legal |
| Public hunt-the-fish globe | Policy §12 |
| Real H3 indexes hugging leases | Targeting risk |
| Implementing EnKF sensor paths | No DA system; breakthrough-class |

---

## 8. Follow-ups (other agents / humans)

- Founder: lock or reject W1 geography (Willapa vs South Sound).  
- Rights: DUA for R01/R03/R04; NANOOS commercial terms for R08.  
- Product: 30 s form as specified; never mix ops score with DOH.  
- Quality: do not score B4 against closures.  
- EMIV owner: absorb remaining unresolved planner keys (`TAX`/`GEO`/`SOL`/`BAG`/`MOD`/`UNC`/`DET-TRI`/`POL-*`).  
- **Do not** have this agent contact farms or task platforms.

---

## 9. Artifacts produced

All under `/Users/wijeratne/dev/fishai/observatory/observation_planner/`:

- `README.md`  
- `scoring_spec.md`  
- `information_gain_methods.md`  
- `recommendation_schema.md`  
- `modalities.md`  
- `w1_willapa_oyster_plan.md`  
- `fixture_recommendations.csv`  
- `anti_goals.md`  
- `architecture.md`  
- `agent_handoff.md` (this file)

---

## 10. Return block (for parent)

**Top 5 W1 (FIXTURE):** (1) 30 s partner outcome form OVS 0.658 PRIVATE; (2) public air×tide×solar pairing 0.613; (3) culture/elevation/ploidy metadata 0.573; (4) existing bag thermistor export 0.566; (5) 14-day paper protocol 0.529. Partner form may beat a new sensor. DOH sampling is the wrong target. No glider, no extra SST as primary.

**Global planner:** design only — batch OVS on uncertainty tiles × EMIV coverage; human gate; partner-first ladder. EMIV catalog **`v0.1-draft`** bound; leftover stubs in `engine_id_crosswalk.md`.

**Kill rules:** harm or legal/privacy penalty ≥ 0.50 (or mosaic ≥ 0.70) ⇒ do not recommend; plus NEVER_PUBLISH targeting, public spots, AIS-as-abundance, NSSP impersonation, hardware-before-ladder, listed holding waters, auto-tasking.

**Did not:** ingest data; task vessels/drones/samplers; emit targeting GPS; write globe/commercial integrations.
