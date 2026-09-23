# Agent handoff — Causal Inference and Counterfactual Ecology Engine

**Agent:** Causal Inference and Counterfactual Ecology Engine designer  
**Date:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/causal_ecology/` only  
**Did not write:** `globe/**`, commercial `artifacts/**` integration, `config/`, HiveClaw  
**Trained causal model:** **none**  
**Wedge:** UNRESOLVED commercially; W1 graph is an **example**, not a founder lock  
**`emiv/`:** registry **`v0.1-draft`** bound by ID only; causal statuses unchanged. Crosswalk: `observatory/emiv/engine_id_crosswalk.md`.

**Read:** `artifacts/marine_domain/*` (including variable matrix), `artifacts/scientific_red_team/prediction_contract.md`, `observatory/sensitive_location_policy.md`, W1 GT relabel, observatory output/factory/DA/ocean-model causal notes, red-team oyster attacks.

---

## 1. Executive finding

The observatory may keep a **causal ecology graph as an assumption document**: every arrow has exactly one of five statuses. It may **not** emit causation from correlation, may **not** answer \(do(\cdot)\) with a fitted model, and may **not** user-face counterfactuals without review.

W1 (*Magallana gigas*, AphiaID 836033, WA farm 72 h ops-stress) encodes the red-team / marine-domain rails:

- 2021 = **air × midday emersion × solar**, not SST as body T  
- **SST ≥ 19 °C is not a kill law**  
- **OsHV-1 ≠ established 72 h WA driver**  
- **OA = hatchery larva, not 72 h bag headline**  
- **WA DOH closure = regulatory, not causal mortality in the ops model**

Sibling API stub that calls Raymond et al. 2022 a “causal stressor” is **too strong** (that field path is `ECOLOGICALLY_SUPPORTED_ASSOCIATION`). Not edited (outside write path).

---

## 2. W1 edges by causal status (return block)

| Status | **n** | What that means here |
|---|---:|---|
| `CAUSALLY_TESTED_RELATIONSHIP` | **8** | Tide/elevation geometry; biomimetic heat budget; George 2023 lab water-then-aerial delayed mortality; planting → inventory; larval Ω (lab); OsHV-1 **where present** (not WA); lab *Vibrio*×heat×spawn |
| `ECOLOGICALLY_SUPPORTED_ASSOCIATION` | **17** | 2021 Salish field path; water T metabolism; DO/neap/flood/turbidity/storms; culture strata; sessility; delayed-label mismatch; seasonal food/residence; basin split |
| `OBSERVED_CORRELATION` | **13** | SST as mixed-shallows proxy; **≥19 °C kill-law temptation**; SST vs 2021 maps; satellite chl vs growth; DOH policy mapping; season/effort/access/method/climate/harvest confounding |
| `EXPERT_HYPOTHESIS` | **6** | WA animal-stress HAB; nutrients→HAB at 72 h; WA field *Vibrio*; handling after heat; lease microhabitat residuals; WA field ploidy |
| `UNKNOWN` | **12** | SST→emersion tissue T; chl/AIS→abundance; current direction & prey drop as 72 h death; OA adult 72 h; **OsHV-1 as WA 72 h driver**; **DOH→ops mortality**; MPA→bag survival; moon⊥tide; WA-wide preferred-depth law; sensor availability as “biology” |
| **Total** | **56** | `w1_magallana_gigas_causal_graph.md` E01–E56 |

**8 + 17 + 13 + 6 + 12 = 56.**

No edge is a FishAI-identified effect. Three tested edges are **off-headline** if misused: larval OA, OsHV-1-where-present, lab *Vibrio*.

---

## 3. Counterfactuals forbidden as user-facing without review

**Default:** all eight contracted templates are **not user-facing.** All must carry **`SCENARIO ESTIMATE — NOT OBSERVED FACT`.**

**Hard-forbidden** on briefs, maps, decks — even with the banner — until a **named human domain reviewer** and a written amendment:

1. Any scenario **without** the banner, or phrased as observed fact.  
2. **`+2 °C water` or SST ≥ 19 °C as a kill law** or as a **2021 replay** (2021 was AHW × midday emersion × solar).  
3. **30-day marine heatwave as 2021** or as a **72 h bag-death forecast**.  
4. **OA / Ω as a 72 h market-bag headline.**  
5. **OsHV-1 outbreak timing in Washington.**  
6. **HAB in region as harvest legality, “safe to eat,” toxin-free, or mixed ops+sanitation score.**  
7. **WA DOH / NSSP closure as causal mortality or survival.**  
8. **MPA reduces fishing → oyster survival or abundance.**  
9. **Current-direction change as 72 h causal mortality.**  
10. **Prey / chlorophyll drop as 72 h kill or as oyster abundance.**  
11. **Preferred-depth hypoxia at public lease grain** (inverts farm KPIs).  
12. Numeric % mortality, catch/harvest guarantees, commands, weather-safety, public biological heatmaps.

Fixtures A–E in `fixture_counterfactuals.md` are **internal examples**. Current-direction, prey-drop, and MPA were **not** fixtured as 72 h mortality stories on purpose.

**After review, internal-only mechanism notes (still bannered, still not product):** +2 °C water as **metabolism/spawn co-factor**; DO below a named threshold in a **named basin with sensors**; named animal-stress HAB as **hypothesis**; culture-depth hypoxia **tradeoff**; seasonal residence-time/food as **growth**.

---

## 4. Evidence table (design, not skill)

| Finding | Evidence | Confidence |
|---|---|---|
| Five-status ceiling is the right honesty tool | Arif & MacNeil 2022; `ocean_model_comparison.md` §2.21; RT-XCUT-08 | High |
| 2021 ≠ SST body T | Raymond 2022 https://doi.org/10.1002/ecy.3798; Miner 2025 https://doi.org/10.3389/fmars.2025.1503019; Hesketh & Harley https://doi.org/10.1111/gcb.16390 | High |
| Water-then-air lab delayed death; not 72 h % | George 2023 https://doi.org/10.1111/gcb.16880 | High for lab; Low for lease transport |
| OA larvae ≠ adult 72 h | Waldbusser 2015 https://doi.org/10.1038/nclimate2479; Barton 2012 **correlation** https://doi.org/10.4319/lo.2012.57.3.0698 | High (stage split) |
| OsHV-1 not WA 72 h driver | Dumbauld 2023 https://doi.org/10.3354/dao03868 | High for “not established”; not a forever-absent claim |
| Closures ≠ ops GT | WA DOH; `ground_truth_relabel_W1.md`; RT-OYS-01 | High |
| No public farm mortality panel | marine_domain dossier | High |

---

## 5. Source / license (cite only; no ingest)

Same rail as marine-domain handoff: WoRMS, NOAA Fisheries, FAO culture sheet, NANOOS, SoundToxins, WA DOH, WSG Rapid Response, WDFW 2019 note, PSI publications list, USDA-ARS PSBC page, NOAA OAP. Peer-reviewed DOIs above. Licenses **UNKNOWN** until rights agent. Farm outcomes `PRIVATE`.

---

## 6. Confidence and limitations of **this** design

| Area | Confidence | Limitation |
|---|---|---|
| Status assignments for W1 headline rails | High | Still literature classification, not identification on partner logs |
| Exact 56-edge inventory | Medium | Another reviewer might split/merge interactions |
| Lab → lease transport | Low | George/Wendling/Waldbusser ≠ Willapa bags |
| Chinook/lobster graphs | N/A | Not built this pass (schema is reusable) |
| Numeric scenario magnitudes | **None** | Forbidden |

**Did not:** interview growers; ingest NANOOS; fit DAG/SCM; edit `globe/` or commercial APIs; claim HiveClaw as marine causal ID.

---

## 7. Artifacts produced

All under `observatory/causal_ecology/`:

- `README.md`
- `causal_status_policy.md`
- `graph_schema.md`
- `confounder_catalog.md`
- `driver_query_contract.md`
- `counterfactual_contract.md`
- `w1_magallana_gigas_causal_graph.md`
- `fixture_counterfactuals.md`
- `what_would_falsify.md`
- `agent_handoff.md` (this file)

---

## 8. Follow-ups (not this agent)

1. Named shellfish-domain reviewer on E05 vs E03 (field vs lab).  
2. If wedge locks W1: implement expert-rule **inputs** (air×tide×solar), not a causal engine.  
3. Pre-register F-W1-HEAT-01 (air×tide vs SST-only on 2021) before any training.  
4. Tighten sibling API assumption language (Raymond ≠ identified cause).  
5. Do not start Chinook/lobster causal graphs until W1 statuses survive that review.

---

## Return block (for parent)

**W1 edge counts:** `CAUSALLY_TESTED_RELATIONSHIP` **8**; `ECOLOGICALLY_SUPPORTED_ASSOCIATION` **17**; `OBSERVED_CORRELATION` **13**; `EXPERT_HYPOTHESIS` **6**; `UNKNOWN` **12**; total **56**. No trained causal model.

**Forbidden user-facing without review:** every counterfactual by default; hard-forbid unlabeled/fact-like scenarios; +2 °C water or SST≥19 °C **kill / 2021 replay**; 30-day MHW as 2021 or 72 h death; OA as 72 h bag headline; OsHV-1 WA timing; HAB as food-safety or mixed score; **DOH closure as causal mortality**; MPA→oyster survival; current-direction 72 h death; prey/chl drop as 72 h kill or abundance; preferred-depth hypoxia at **public lease grain**; guarantees, commands, public biological heatmaps.
