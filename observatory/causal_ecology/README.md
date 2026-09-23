# Causal Inference and Counterfactual Ecology Engine (design)

**Directory:** `/Users/wijeratne/dev/fishai/observatory/causal_ecology/`  
**Date:** 2026-09-18  
**Status:** Assumption graph + query contracts + W1 example. **No trained causal model. No ingest. No globe product. No commercial integration files.**

This module is how the observatory **refuses to confuse correlation with causation** while still writing down mechanisms honestly.

Default observatory emission remains `UNKNOWN/INSUFFICIENT DATA`. Anything in this folder is `HYPOTHETICAL/RESEARCH MODE` until a named human domain reviewer says otherwise.

---

## Read first

| File | What it is |
|---|---|
| [`causal_status_policy.md`](causal_status_policy.md) | Exactly one status per edge; promotion rules; no causation from correlation |
| [`graph_schema.md`](graph_schema.md) | Path: env → habitat → prey/pathogen → physiology → movement/distribution/abundance |
| [`confounder_catalog.md`](confounder_catalog.md) | Required ten confounders + W1 extras |
| [`driver_query_contract.md`](driver_query_contract.md) | Predictive vs causal vs both; evidence; confounders; experiment vs observation |
| [`counterfactual_contract.md`](counterfactual_contract.md) | Eight scenario templates; banner **SCENARIO ESTIMATE — NOT OBSERVED FACT** |
| [`w1_magallana_gigas_causal_graph.md`](w1_magallana_gigas_causal_graph.md) | 56 scored edges with citations and URLs |
| [`fixture_counterfactuals.md`](fixture_counterfactuals.md) | Five W1 worked scenarios |
| [`what_would_falsify.md`](what_would_falsify.md) | Pre-registered demotions |
| [`agent_handoff.md`](agent_handoff.md) | Return block for the parent agent |

---

## Non-negotiables (W1)

1. **2021 Salish / heat-dome:** air temperature × midday emersion × solar. **Not** satellite SST as body temperature.  
2. **SST ≥ 19 °C is not a kill law.**  
3. **OsHV-1 is not an established 72 h Washington driver.**  
4. **Ocean acidification is hatchery-larva, not a 72 h bag headline.**  
5. **WA DOH closure is regulatory, not causal mortality in the ops model.**

---

## What this is not

- Not a fitted SCM, DoWhy/EconML pipeline, or HiveClaw runtime bound to oysters.  
- Not `globe/**` and not a widening of the commercial wedge.  
- Not harvest authorization, food safety, navigation, or abundance.  
- `emiv/` registry is **`v0.1-draft`**; node `node_id` values stay dotted graph keys. Bindings: [`../emiv/engine_id_crosswalk.md`](../emiv/engine_id_crosswalk.md). No evidence-model inventory was merged into this graph (IDs only).

Sources read (cite-only): `artifacts/marine_domain/**`, `artifacts/scientific_red_team/prediction_contract.md`, `observatory/sensitive_location_policy.md`, marine-domain variable matrix, W1 GT relabel, observatory output/factory/DA notes.
