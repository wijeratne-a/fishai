# Canonical first prototype — P0-WILLAPA-MGIGAS-OSI72

**Canonical ID:** `P0-WILLAPA-MGIGAS-OSI72`  
**Status:** **RECOMMENDED, not DECIDED.** This file does not lock W1/W2/W3.  
**Project state:** `STATE_10_PAUSED_FOR_HUMAN_DECISION` — **unchanged.**  
**Scribe role:** alignment only. No new research. No ingest. No training. No observatory in-flight edits.

---

## Independent agreement (not a founder lock)

Four already-written tracks name the same first cell. Agreement is on a **recommended** prototype, not a decision.

| Track | Where | What it already says |
|---|---|---|
| Commercial synthesis | `artifacts/integration/COMMERCIAL_WEDGE_SYNTHESIS.md` | Recommended (not locked) first commercial test is **W1**: Pacific oyster (*Magallana gigas*) × WA DOH commercial growing areas in the **Willapa Bay** system × farm operator × daily **email + 1-page PDF** 72-hour **Category D** operational-stress / work-window brief, with a hard WA DOH food-safety wall. Go/no-go is **PAUSE**, not GO. |
| Observatory cost / roadmap | `observatory/artifacts/product_cost/agent_handoff.md`; `observatory/1_year_plan.md`; `observatory/3_year_plan.md`; `observatory/product_roadmap.md`; `observatory/global_coverage_roadmap.md`; `observatory/cost_and_deployment_models/cost_model.md` | Year-1 build object is framework + **one** prototype cell **`P0-WILLAPA-MGIGAS-OSI72`**: public-data-first software twin of *M. gigas* 24–72h operational stress / work-window on Willapa DOH growing-area / lease geography. Hardware last. Not a global taxa map. |
| Physics red team | `observatory/physics_feasibility_reports/physical_limits.md` | Honest W1 physics is **air × emersion × in-situ T/DO/waves**, not satellites or eDNA. SST-only oyster mortality is **PX-18** (`PHYSICALLY_UNLIKELY`). Allowed product class includes farm sensors + tide + air as **Category D** ops-stress for sessile cultured animals. |
| Digital twin architecture | `observatory/global_digital_twin_architecture.md` §8; `observatory/data_assimilation_design.md` | **v0 observatory twin** = *M. gigas* (AphiaID **836033**) operational-stress / work-window state on named WA DOH growing areas in one estuary (Willapa **recommended, not locked**), 24–72 h, Category D. |

Coverage reporting id in the roadmap template is `CELL-WILLAPA-MGIGAS-OSI72` (`observatory/global_coverage_roadmap.md` §8) — same cell, reporting label only.

---

## What it is

- **ONE×ONE×ONE×ONE** slice: species *Magallana gigas* (WoRMS **836033**; synonym *Crassostrea gigas* 140656) × Willapa Bay system **DOH commercial growing areas** (Pacific County; e.g. Nahcotta and adjacent polygons) × commercial oyster **farm operator** × recurring **24–72 hour** stress / disruption / **work-window** decision.
- A **Category D** environmental / operational-stress indicator plus **workability** (tide × wind/wave), with water T / DO / salinity as **supporting covariates** when sensed. Variable IDs: `observatory/emiv/` `v0.1-draft` — WA DOH harvest status is `EMIV-HUM-HARV-001` (**constraint, not ops label**); satellite SST is `EMIV-PHY-SST-001` (`W1_PROXY`).
- After a later founder lock (not now): analyst-assembled **manual** brief from NWS air + CO-OPS tides + wind/wave + **attributed** DOH status as a **separate module**. Delivery: daily **email + 1-page PDF**.
- Observatory v0 of the **same cell**: sparse H3 + official polygons; depth bins **`INTERTIDAL_AIR` + `SURFACE_0_5` only**; Layer 6 = **B4 expert-rule + B12 climatology**; observatory support **T2** / `HYPOTHETICAL/RESEARCH MODE` until time-forward or prospective tests exist (then T4 for this AOI×target only — not a global-row upgrade).
- Open-loop DA: **no sequential filter**. No EnKF. No global cube / lake.

---

## What it is not

- **Not DECIDED.** W2 (Chinook 24–48h encounter) and W3 (lobster next-trip CPUE) remain viable if the founder picks them (`decision_required.md`).
- Not food-safety, NSSP class, biotoxin, *Vibrio*, harvest legality, or DOH open/closed as a model output.
- Not oyster abundance/biomass, bag-level % dead, SST-as-body-temperature, a map product, AIS, hardware, HAB mixed into the ops brief, or “AI abundance.”
- Not EnKF / 4D-Var / particle-filter DA, not a global 3D posterior, not Copernicus/OBIS bulk ingest, not T3–T6, not a 48 h forecast label on climatology (B12).
- Not a live UI, not interviews, not a paid pilot, not permission to ingest or train.

---

## v0 stack (already specified; not implemented here)

Cited from architecture §8.4 / §4.2 and DA design §§3–4 and §10:

| Axis | v0 |
|---|---|
| Estimators | **B4** expert-rule + **B12** climatology (`artifacts/quality_and_validation/baseline_model_spec.md`). No ML. |
| Depth | **`INTERTIDAL_AIR` + `SURFACE_0_5`** on **H3** (+ official growing-area polygons). No full z-mesh. |
| Support tier | **T2** until time-forward tests |
| Assimilation | Open-loop rules; **no EnKF**; **no global cube** |
| Physics | Tide tables + NWP/in-situ; no GCM |

---

## HIGH blockers remain

Copy remediation and this ID do **not** clear scientific or legal deployment gates. `project_state.json`: `latest_red_team_status=HIGH_BLOCKERS_OPEN`; `latest_validation_status=PROTOCOL_ONLY`; `pilot_status=NOT_STARTED`; `traction_status=ZERO_INTERVIEWS`.

Still open (from commercial synthesis; not re-scored here): no founder wedge lock (**B-ALL-08**); no named human domain reviewer (**B-ALL-05**); no ingest-approved source (**B-ALL-07**); no partner farm outcome stream / DUA (**B-OYS-04**); food-safety wall not a **shipping** UI constraint (**B-OYS-01**); no spatiotemporal validation / as-of replay / prospective baseline beat / live 14-field path (**B-ALL-01…04**). Red-team customer-facing model status remains **NO-GO**. Physics: SST-only thermal spec remains invalid (**PX-18** / **B-OYS-03**).

---

## Next human action

Answer **`decision_required.md`**. Minimum to unblock STATE_2: items **3, 8, 9**, plus geography lock (4/5/6 as applicable). Until then: no ingest, no training, no wedge lock from this memo, no customer send.
