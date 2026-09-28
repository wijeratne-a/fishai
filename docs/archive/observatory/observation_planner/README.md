# Active Observation Planner — research / ops tooling

**Program:** FishAI / Global Saltwater Life Observatory  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/observation_planner/`  
**Date:** 2026-09-18  
**Status:** `DESIGN_ONLY`. No ingest. No model. No field tasking.  
**Commercial wedge:** W1 first (Pacific oyster × Willapa × 72 h farm ops-stress). **RECOMMENDED, not DECIDED.**

This directory is the **information-gain engine design**: a batch scorer that answers *“What is the next highest-value observation to collect?”* It is **not** a public map of animals, **not** a hunt-the-fish product, **not** a vessel/drone dispatcher, and **not** an NSSP / WA DOH harvest tool.

---

## What this is

An **ops and research planner** that ranks candidate observations by **uncertainty reduction and decision/scientific value**, not by data volume.

The system must not passively wait for whatever happens to arrive. It must propose the next observation *class* (partner form, existing sensor export, public pairing, later hardware) under:

- the prediction contract (`artifacts/scientific_red_team/prediction_contract.md`);
- the sensitive-location policy (`observatory/sensitive_location_policy.md`) — **a global public animal map is REJECTED**;
- the partner-first acquisition ladder (`artifacts/data_discovery/data_acquisition_plan.md`);
- human approval **before any real-world tasking**.

This iteration outputs **FIXTURE** recommendations at **H3 res 5–6 or named water-body** grain. It does **not** output GPS that would target spawning aggregations, nests, haul-outs, private farm corners, or listed-species holding waters.

---

## What this is not

| Not | Why |
|---|---|
| A public “where is the life” globe | Policy §12: mixed-taxon public maps are unsafe as v1 |
| A poaching / fishing-spot optimizer | `anti_goals.md` |
| A command to task ships, gliders, drones, or eDNA boats | Human gate; this pass does not task anyone |
| More SST as if it were oyster body temperature | Wrong variable for W1 (Raymond et al. 2022) |
| WA DOH closure sampling as ops ground truth | Wrong target (`ground_truth_relabel_W1.md`) |
| Commercial integration code | Do not write `fishai/globe/**` or commercial connectors from this agent |

---

## Commercial W1 first

Until the founder locks a wedge, the **only scored slice** is:

> Pacific oyster (*Magallana gigas*, AphiaID 836033) on **named Willapa Bay growing waters**, 24–72 h **operational disruption / environmental-stress indicator** (Category D). Not harvest legality. Not food safety. Not abundance.

Highest-value next observations for that slice are **intertidal air × tide × (bag/body) temperature** and **farm log outcomes** — not a glider in the open Pacific, and not another SST layer.

See `w1_willapa_oyster_plan.md` and `fixture_recommendations.csv`.

A later global planner may rank eDNA, PAM, survey allocation, and gliders **after** W1 partner-first work, and only at coarsened cells with harm review. That global layer is **design-only** in this pass (`architecture.md`).

---

## Observation Value Score (locked weights)

\[
\begin{aligned}
\mathrm{OVS} &= 0.25\,\mathrm{EUR} + 0.20\,\mathrm{EcoImp} + 0.15\,\mathrm{ConsPri} + 0.15\,\mathrm{DecVal} \\
&\quad + 0.10\,\mathrm{FcstDis} + 0.10\,\mathrm{Feas} + 0.05\,\mathrm{CostEff} \\
&\quad - \mathrm{HarmPen} - \mathrm{LegalPen}
\end{aligned}
\]

Inputs are on \([0,1]\). Penalties are on \([0,1]\) and **subtract**. **Kill rules override a high OVS.** Formulas, calibration hypotheses, and a worked numeric example: `scoring_spec.md`.

---

## File map

| File | Contents |
|---|---|
| `README.md` | This file |
| `scoring_spec.md` | OVS formula, 0–1 definitions, penalties, kill rules, ternary occupancy, worked example |
| `information_gain_methods.md` | VOI, ensembles, occupancy/\(p_{\mathrm{detect}}\), eDNA transport, depth vs horizontal; IMPLEMENTABLE_NOW vs REQUIRES_RESEARCH_BREAKTHROUGH |
| `recommendation_schema.md` | Required fields for a recommendation object |
| `modalities.md` | Observation modalities: maturity, cost band ESTIMATE, FP/FN, when **not** to use |
| `w1_willapa_oyster_plan.md` | First slice: 8 ranked FIXTURE recs; DOH sampling is the wrong target |
| `fixture_recommendations.csv` | Synthetic coarsened cells, `FIXTURE=true` |
| `anti_goals.md` | Forbidden optimizations |
| `architecture.md` | Batch job on uncertainty tiles + EMIV coverage; human approval; partner-first |
| `agent_handoff.md` | Handoff to parent / sibling agents |

---

## EMIV binding (registry `v0.1-draft`)

Canonical IDs live in [`../emiv/emiv_registry.csv`](../emiv/emiv_registry.csv) (set `v0.1`, artifact `v0.1-draft`, 84 rows). Planner `emiv_ids[]` use those IDs where a registry row exists. Crosswalk (old stub → registry): [`../emiv/engine_id_crosswalk.md`](../emiv/engine_id_crosswalk.md).

This is **ID wiring only**. Do not treat bound IDs as ingested features. WA DOH / NSSP harvest status is **`EMIV-HUM-HARV-001` (constraint, not ops label)**. Satellite SST is **`EMIV-PHY-SST-001` (`W1_PROXY`)**.

W1_CORE examples used here: `EMIV-ECO-OPSOUT-001` (farm `ops_disruption_72h` outcome), `EMIV-PHY-ATEMP-001`, `EMIV-PHY-TIDE-001`, `EMIV-PHY-EMERS-001`, `EMIV-PHY-SOLAR-001`. `EMIV-PHY-TISST-001` is CANDIDATE until a partner thermistor exists. Planner-only stubs with **no** registry row (`EMIV-DET-TRI-001`, `EMIV-POL-HARM-001`, taxon/geo/score IDs) stay as local keys — listed under unresolved in the crosswalk.

---

## Acquisition ladder (do not skip)

Do **not** recommend **new** hardware before:

1. Public data already paid for (pair it correctly)  
2. Partner export of logs they already keep  
3. Existing sensors already in the water / on the farm  
4. Manual structured observations (30-second / paper protocol)  
5. Mobile capture of the **same** fields  
6. Integrations with software they already pay for  

Then, and only then, new sondes, gliders, drones, eDNA autosamplers.

---

## Kill rules (short)

If **Ecological Harm Penalty ≥ 0.50** or **Legal/Privacy Penalty ≥ 0.50**, **do not recommend**, even if OVS would be high. Additional hard kills: `NEVER_PUBLISH` targeting; public rare-species pins; AIS-as-abundance; NSSP impersonation; hardware-before-ladder; unreviewed public biology. Full table: `scoring_spec.md` §6.

---

## Non-actions this pass

- No dataset download or scrape  
- No real vessel, drone, glider, hydrophone, or eDNA tasking  
- No lease-corner or bag-row GPS  
- No edits under `fishai/globe/**` or commercial integration paths  
- No claim that a planner is running in production  
