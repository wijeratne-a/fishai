# Driver query contract

**Date:** 2026-09-18  
**Status:** Binding for any “what drives \(Y\)?” question in the observatory causal-ecology module.  
**Engine:** design only. **No trained causal model. No \(do(\cdot)\) estimator. No ingest.**

A driver query is not a forecast brief. Forecasts still obey `prediction_contract.md` (14 fields, Category C/D). This contract is how we **talk about arrows**.

---

## 1. Required declaration: predictive vs causal vs both

Every query **must** set exactly one `query_mode`:

| `query_mode` | Question allowed | Answer shape |
|---|---|---|
| `predictive` | Which inputs, available at issuance, associate with later **labels** of the declared target? | Rank or include/exclude as **features**; status may be correlative; **must not** say “causes” |
| `causal` | What would happen to \(Y\) if we **intervened** on \(X\) (or if a well-defined natural contrast occurred), holding the adjustment set? | Only if a path exists whose weakest `causal_status` and `identification_class` support it; otherwise `UNKNOWN` |
| `both` | Both questions | **Two answers.** Two evidence lists. Two confounder lists. No blended sentence |

If the user (or another agent) does not declare a mode, **do not infer causal**. Serve `predictive` **or** refuse with `UNKNOWN`.

---

## 2. Required query fields

| Field | Content |
|---|---|
| `taxon` | Accepted name + AphiaID + life stage |
| `geography` | Named official unit or lab protocol, not “the Pacific” |
| `target_Y` | Exact quantity (e.g. `ops_disruption_72h`, `tissue_temperature`, **not** “oyster health”) |
| `candidate_drivers[]` | Node IDs |
| `query_mode` | `predictive` / `causal` / `both` |
| `horizon` | |
| `culture_method` / depth | required for W1 |
| `requested_identification` | What experiment or observation would distinguish (even if not run) |

---

## 3. Required answer fields

| Field | Content |
|---|---|
| `query_mode_echo` | Must match |
| `edge_ids[]` | From the species graph |
| `causal_status` per driver | Exactly one of the five |
| `evidence[]` | Citation + URL + what the paper **actually** measured |
| `confounders[]` | From `confounder_catalog.md`; not a decorative list |
| `distinguishing_design` | **Experiment vs observation** that would separate this driver from alternatives (§5) |
| `data_support` | `none` / `sparse` / `program_exists` / `lab_only` / `partner_private` |
| `predictive_verdict` | `usable_as_input` / `proxy_only` / `do_not_use` |
| `causal_verdict` | `research_only` / `mechanism_note_only` / `not_identified` / `wrong_quantity` |
| `anti_claims[]` | Forbidden sentences |
| `output_class` | `HYPOTHETICAL/RESEARCH MODE` until a human reviewer says otherwise |

**Ceiling:** the answer may not be stronger than the weakest cited edge. A stack of Tier-3 rasters does not create a causal driver.

---

## 4. Distinguishing experiment vs observation (mandatory paragraph)

Each driver answer includes a short **identifying contrast**:

| Pattern | When to use | Example (W1) |
|---|---|---|
| **Designed experiment** | Can assign \(X\) | Lab: 30 °C water **alone** vs 30 °C water **then** 44 °C aerial emersion (George et al. 2023). If water-only does not reproduce field death, **+2 °C water is not the 2021 mechanism.** |
| **Field manipulation** | Shade, lower bags, split elevation | Shade during midday emersion vs unshaded same bed: tests solar × air vs water T. |
| **Natural experiment / contrast** | Assignment not controlled but a known clash of timings | 26–28 Jun 2021: Salish **afternoon** lows vs Olympic Coast **morning** lows (Raymond et al. 2022; Miner et al. 2025). SST-only should **not** rank sites if aerial timing is the mechanism. |
| **Negative control observation** | Quantity that should **not** move if the mechanism is true | Satellite SST near-normal while biomimetic / mud / tissue T is lethal → SST is not body T. |
| **Wrong-label control** | Alternative \(Y\) | If a driver “predicts” **DOH closures** but not partner mortality/workability, it is not an ops-stress driver. |
| **Wrong-stage control** | Ω, OsHV-1, juvenile chl papers | Hatchery larval Ω vs market-bag 72 h; CA OsHV-1 vs WA sentinels. |

**Observation without a contrast is not identification.** Monitoring NANOOS temperature next to unnamed mortality rumors remains `OBSERVED_CORRELATION`.

---

## 5. W1 default driver table (ops target, not harvest)

Target \(Y\) = Category **D** `ops_disruption_72h` (workability, emersion-heat **indicator**, gear/wave). **Not** NSSP.

| Driver | `query_mode=predictive` | `query_mode=causal` | Distinguishing design |
|---|---|---|---|
| Air T × midday emersion × solar | **Primary input** if tide-timed | Mechanism note: heating path is lab/biomimetic-tested; **2021 field deaths** are `ECOLOGICALLY_SUPPORTED_ASSOCIATION` | Shade or elevation split; 2021 morning-vs-afternoon tide contrast vs SST-only |
| In situ water T | Secondary input | Co-stressor / metabolism; **not** 2021 body T | George water-only vs water+aerial; subtidal vs intertidal split |
| Satellite SST | Forbidden as sole model; Low/None confidence | **Not identified** as tissue T or kill law | Must lose to air×tide on 2021-type days or labels are wrong |
| DO | Input **where local sensors exist** | Real physiology; basin-specific; not a WA-wide law | Named basin + culture depth; Hood Canal ≠ Willapa |
| Salinity / runoff | After named rain | Multi-stressor, not salinity alone | Hydrograph vs salinity vs TSS vs DO decomposition |
| Wind / waves | Ops disruption input | Disruption ≠ physiology | Gear-loss labels vs mortality labels |
| Ω / pH | **Do not headline** 72 h bags | Causal for **larvae**, `UNKNOWN` for 72 h adults | Hatchery larval assays ≠ bag counts |
| OsHV-1 | Not a WA 72 h feature without PCR | `UNKNOWN` as WA 72 h driver | Sentinel PCR + challenge; 2020 OR/WA non-detect is not “absent forever” but is not a driver |
| HAB (animal-stress taxon) | Conditional, named taxon only | `EXPERT_HYPOTHESIS` in WA 72 h | Split SoundToxins **animal** taxa vs NSSP harvest list |
| DOH closure | Must-show **constraint**, not a feature of \(Y\) | `UNKNOWN` as causal mortality | Closures while harvest stays open during heat-kill (2021-type) |
| Chlorophyll / AIS / moon⊥tide | `do_not_use` for this \(Y\) | `not_identified` / wrong quantity | — |

---

## 6. Refusals (do not answer as if identified)

Refuse or answer `UNKNOWN` when the query:

- asks “what **caused** mortality” from SST/chl/AIS alone;  
- mixes ops-stress and food-safety into one driver list;  
- wants Chinook 24–48 h “bite drivers” from juvenile chlorophyll papers;  
- wants lobster **abundance** drivers from CPUE or AIS;  
- wants a numeric importance ranking from a model that does not exist;  
- wants public lease-level drivers (privacy).

---

## 7. Language

| Allowed | Forbidden |
|---|---|
| “Associated with forecast air temperature overlapping daytime emersion” (`prediction_contract.md` §3) | “Caused by SST” |
| “Lab protocol identified aerial heat after warm water as increasing delayed mortality” | “The twin shows warming will kill 37% of bags” |
| “WA DOH status is official context; it is not a mortality driver in this model” | “Closed because oysters are dying” / “Open so oysters are healthy” |
