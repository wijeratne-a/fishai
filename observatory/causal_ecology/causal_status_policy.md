# Causal status policy — FishAI observatory

**Module:** Causal Inference and Counterfactual Ecology Engine (design only)  
**Date:** 2026-09-18  
**Status:** Binding on every edge, driver query, and counterfactual under `observatory/causal_ecology/`.  
**Trained causal model:** **none.** This policy classifies *literature and mechanism claims*, not fitted structural causal models, not product scores.

Companion: `graph_schema.md`, `driver_query_contract.md`, `counterfactual_contract.md`.  
Does not loosen: `artifacts/scientific_red_team/prediction_contract.md`, `observatory/user_output_contract.md`, `observatory/sensitive_location_policy.md`.

`emiv/` registry (`v0.1-draft`) is present. This policy classifies literature/mechanism claims; it does not ingest. Node bindings: [`../emiv/engine_id_crosswalk.md`](../emiv/engine_id_crosswalk.md). `WA DOH` = `EMIV-HUM-HARV-001` (constraint). SST = `EMIV-PHY-SST-001` (`W1_PROXY`).

---

## 1. Non-negotiables

1. **Do not claim causation from correlation.** A significant coefficient, a SHAP plot, a heatmap, or a co-occurring SST blob is not an effect of an intervention.
2. **Exactly one status per directed relationship.** No dual labels, no “mostly causal,” no averaging.
3. **Status is scoped** by taxon, life stage, geography, culture method, and time horizon. Transferring a status across those axes is a new edge, defaulting to `UNKNOWN` until re-justified.
4. **FishAI has not identified any marine effect.** `CAUSALLY_TESTED_RELATIONSHIP` means *published designed tests or physically determined mechanisms exist for that scoped edge*, not that this program ran them, and not that a 72 h product may speak the verb “caused.”
5. **Promotion is never automatic.** Software may only demote. A named human domain reviewer may promote, and only with a written identification strategy.
6. **Product language ceiling:** even a `CAUSALLY_TESTED_RELATIONSHIP` may appear in operator copy only as an **input / mechanism note**, never as a guaranteed outcome, harvest authorization, or abundance claim (`prediction_contract.md` RT-XCUT-08).
7. **Observatory output class** for any causal graph or counterfactual today: `HYPOTHETICAL/RESEARCH MODE`. Capability class: (5) scientifically plausible but unproven as a fitted engine; some *component* mechanisms are (1) observable or (2) inferable. Default live emission remains `UNKNOWN/INSUFFICIENT DATA`.

---

## 2. The five statuses (exactly one)

| Status | Meaning | What it may support | What it may **not** support |
|---|---|---|---|
| `OBSERVED_CORRELATION` | Two quantities co-vary in data or event tables. Direction, confounding, and intervention response are **not** established for this scope. | Hypothesis generation; “these series moved together”; confounder warnings | “Driven by,” “if we change X then Y,” kill laws, abundance |
| `ECOLOGICALLY_SUPPORTED_ASSOCIATION` | A directed mechanism is biologically coherent **and** supported by field ecology, natural-history reconstruction, or multi-stressor observation at **matching stage/horizon/geography family**. Not a designed identification of \(P(Y \mid do(X))\). | Category D **indicator** design; which covariates belong in an expert rule; which natural experiments to run | User-facing “X caused Y”; policy counterfactuals as fact; pooling basins |
| `CAUSALLY_TESTED_RELATIONSHIP` | A **designed experiment**, factorial challenge, biomimetic manipulation, physical identity, or literal operator intervention identifies a directed effect **in the cited setting**. External validity to this farm/hour is a separate claim. | Justifying that an expert-rule term is not an arbitrary correlative widget; lab envelopes; physical tide×elevation geometry | A trained SCM; a 72 h mortality percent; transferring CA/EU/Aus results into Washington without a new edge |
| `EXPERT_HYPOTHESIS` | Practitioners or papers propose a directed effect; local tests are missing, mixed, or only narrative. | Interview scripts; monitoring priorities; explicit “untested” flags | Any customer-facing driver sentence that omits the hypothesis flag |
| `UNKNOWN` | Insufficient evidence **or** the proposed arrow is a known category error for this scope (wrong stage, wrong geography, regulation ≠ physiology, proxy ≠ body). | Honest abstention; anti-edges; “do not feature” | Filling the gap with SST, chlorophyll, AIS, or closures |

**Default when unsure:** `UNKNOWN`.  
**Default when only a scatterplot exists:** `OBSERVED_CORRELATION`.  
**Default when ecology is good but identification is not:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`.

---

## 3. What does *not* promote a status

| Tempting move | Required status after the move |
|---|---|
| Satellite SST or chlorophyll correlates with a mortality table | `OBSERVED_CORRELATION` or `UNKNOWN` (if the mechanism is known-wrong) |
| 2021 maps look red where SST was warm | Still not tissue temperature; see W1 anti-edges |
| NANOOS “>64°F for >24 h” grower flag | Operational **concern band**, not a kill law (`OBSERVED_CORRELATION` if used as death) |
| WA DOH growing-area closure co-occurs with summer heat | `OBSERVED_CORRELATION` of calendar; `UNKNOWN` as causal mortality |
| OsHV-1 kills oysters in California / France / Australia | New edge required for **Washington 72 h**; that edge is `UNKNOWN` until local detection + test |
| Ω_aragonite impairs **larvae** in hatchery/lab | Does not promote adult 72 h bag mortality off `UNKNOWN` |
| A digital twin, DAG drawing, or “causal AI” brand | No status change. Graphs are assumption documents (`ocean_model_comparison.md` §2.21) |
| Beating a correlative baseline | Predictive skill ≠ causal identification (`driver_query_contract.md`) |

---

## 4. Identification vocabulary (required on every edge)

Every edge record must name **one** identification class:

| Class | Typical methods | Honest ceiling |
|---|---|---|
| `PHYSICAL_IDENTITY` | Tide tables + bed elevation → emersion hours; solar geometry | High for the physical quantity; still not mortality |
| `OPERATOR_INTERVENTION` | Planting, lowering bags, shading, harvest | Causal for inventory/exposure **if logged**; confounds later outcomes |
| `LAB_EXPERIMENT` | Controlled temperature, aerial heat, pathogen challenge, carbonate chemistry | High in protocol; transport to lease is a different edge |
| `FIELD_MANIPULATION` | Shade structures, outplants, split-plot culture | Best field identification; rare in v1 |
| `NATURAL_EXPERIMENT` | 2021 heat dome × tide-timing contrast (Salish afternoon lows vs Olympic morning lows) | `ECOLOGICALLY_SUPPORTED_ASSOCIATION` until pre-registered contrasts survive confounder list |
| `OBSERVATIONAL_ADJUSTMENT` | Regression / matching / DAGs with measured confounders | Ceiling `OBSERVED_CORRELATION` until a human reviewer accepts the adjustment set **and** a negative-control test |
| `POLICY_MAPPING` | NSSP tissue threshold → harvest classification | Not a physiological edge |
| `NONE` | Anecdote, lore, moon tables independent of tide | `EXPERT_HYPOTHESIS` or `UNKNOWN` |

Pearl-style \(do(\cdot)\) language is allowed **only** inside research queries that already declare `query_mode = causal` or `both`, and only as a **requested identification**, never as a computed result. This engine does not compute \(do(\cdot)\).

---

## 5. Confounders are first-class

An edge that does not list how the required confounders could spoil the interpretation is incomplete (`confounder_catalog.md`).

Minimum confounder set for **any** observatory causal claim about marine life or farm outcomes:

1. sampling effort  
2. vessel access  
3. season  
4. geography  
5. depth  
6. observation method  
7. regulation  
8. fishing behavior (including farm handling / harvest)  
9. climate modes  
10. data availability  

W1 adds culture method, ploidy, microhabitat, delayed death, and **label contamination by DOH closures**.

Conditioning on a **collider** (e.g. only analyzing leases that reported mortality; only trips that left the dock) is a documented bias, not a feature.

---

## 6. Predictive vs causal (do not collapse)

| Query | Allowed evidence | Forbidden collapse |
|---|---|---|
| **Predictive** | Associations, expert rules, persistence, as-of features | Calling the predictor a cause |
| **Causal** | Identification class ≠ `NONE` / `OBSERVATIONAL_ADJUSTMENT` without reviewer; explicit intervention | Answering with a correlative model “because it predicts” |
| **Both** | Two **separate** answers, two statuses, two limitation lists | One blended sentence |

A quantity can be a **good predictor and a bad cause** (month, port, SST in well-mixed shallows). A quantity can be a **real cause and a bad 72 h predictor** (OsHV-1 where unmonitored; delayed death).

---

## 7. Counterfactual labeling

Every counterfactual output, internal or external, begins with:

**`SCENARIO ESTIMATE — NOT OBSERVED FACT`**

See `counterfactual_contract.md`. Missing that banner is a contract break. User-facing emission without named human domain review is forbidden for the list in that file §6.

---

## 8. Privacy and sensitive locations

Causal graphs and scenarios inherit `sensitive_location_policy.md`:

- Farm mortality, yield, disease, and lease GPS: `PRIVATE` / `NEVER_PUBLISH` publicly.  
- Counterfactuals that would invert which farm failed: coarsen to growing-area or withhold.  
- AIS/VMS are not abundance and are not W1 physiology.  
- Official DOH polygons may be **linked**, not impersonated as mortality.

---

## 9. Amendment

Agents may only **tighten** this policy. Loosening (promoting statuses, dropping confounders, allowing unlabeled counterfactuals) requires a named human domain reviewer and a dated amendment note. Software must not rewrite `CAUSALLY_TESTED_RELATIONSHIP` onto correlative SST edges.
