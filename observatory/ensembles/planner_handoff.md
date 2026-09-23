# Planner handoff — disagreement → Active Observation Planner

**Date:** 2026-09-18  
**From:** ensembles (`ENS-W1-OSI72-v0`)  
**To:** `observatory/observation_planner/` (folder **absent** on 2026-09-18; this is the inbound contract)  
**Also useful to:** change detection, detection-bias, causal-ecology agents when those trees exist  
**Status:** Score-field spec. **No tickets issued. No sensors tasked. No ingest.**

High-disagreement × high-impact is an **observation problem**, not a reason to train a deeper model first.

---

## 1. Rule `DIS-PLAN-W1-v0` (hypothesis)

Fire `planner_eligible = true` if **any**:

| # | Condition |
|---|---|
| R1 | `disagreement_index ≥ 0.5` **and** `impact ∈ {medium, high}` |
| R2 | Required member `cannot_issue` **and** `impact = high` (code `DISAGREE_DATA_GAP`) |
| R3 | `ood_flag = true` **and** `impact ∈ {medium, high}` (agreement does **not** cancel this) |

**Do not fire** when members agree Typical, in-domain, critical inputs fresh, and the farm is not in a planned work window (impact low).

**Do not fire** to “go confirm abundance.” W1 is ops-risk. Planner asks for **outcomes and missing drivers**, not a census.

Numeric cutoffs are HYPOTHESIS, same class as quality GO thresholds: lock after first retro without using the bake-off to tune the ticket rate into a vanity dashboard.

---

## 2. Impact (`impact`) — W1 definition

Impact is **decision cost if the High member is right and ignored**, not biological drama.

| `impact` | Hypothesis rule |
|---|---|
| `high` | B4 **primary** clause fires (air×daytime emersion **or** partner wave/wind workability) **or** a scheduled husbandry/crew window overlaps the 72h valid interval |
| `medium` | Either member is `elevated`, or B4 supporting covariates (DO/S/water T) watch-only, or logs missing on a stocked intertidal lease in Jun–Sep |
| `low` | Both eligible members `typical`, no overlapping work window, in-domain |
| `unknown` | Universe unclear (unstocked, culture type missing) |

Impact **must not** use WA DOH closure, Vp category, or another farm’s mortality.

---

## 3. Payload the planner must accept

Every ticket (or fixture) is this object. Extra planner fields are allowed; dropping these is not.

```text
ticket_id                  PLAN-W1-{date}-{cell}
rule_id                    DIS-PLAN-W1-v0
fired_by                   R1 | R2 | R3 (list)
issued_at                  UTC
valid_from / valid_to      OSI-72 window

# Identity (coarsened for any non-partner audience)
wedge_id                   oyster_wa_ops_72h
taxon                      Magallana gigas / Aphia 836033
life_stage                 farmed_growout
spatial_cell_id_private    partner lease-zone (PRIVATE)
spatial_cell_id_public     coarsened growing-area / bay id
depth_band                 INTERTIDAL_AIR and/or SURFACE_0_5
publish_class              PRIVATE | COARSENED | RESTRICTED | NEVER_PUBLISH
culture_type               intertidal_bag | on_bottom | floating | unknown
stocked                    true | false | unknown

# Ensemble scores
ensemble_id                ENS-W1-OSI72-v0
member_bands               {B12, B4, B5?}
disagreement_index         0 | 0.5 | 1 | null
disagreement_codes[]       taxonomy
ensemble_mean_status       usually suppressed_unvalidated
ood_flag
ood_dimensions[]
impact                     high | medium | low | unknown
confidence_worst           min of members (high>medium>low>none inverted)
missing_data_state[]

# What to observe (options, not commands)
observation_need_codes[]   see §4
suggested_modalities[]     see §4
privacy_constraints        no public lease KPI; coarsen; no neighbor import
success_criterion          e.g. "72h workability Y/N + protocol mortality band logged"
do_not_observe[]           toxin tissue as OSI label; DOH as y; other farms; AIS

# Contestability
resolution_hypothesis      one sentence
linked_fixture_id          if synthetic
```

**Geographic precision on tickets leaving the partner ACL:** public cell only. Planner UIs that look like a “go here” waypoint fail red-team RT-XCUT-10 / sensitive-location policy.

---

## 4. Observation-need codes (W1)

Planner should rank **cheap, label-shaped** observations over new satellites.

| Need code | Why it appears | Suggested modality (options) | Not this |
|---|---|---|---|
| `NEED_OUTCOME_LOG` | `DISAGREE_DATA_GAP` on farm logs; B4 High vs B12 Typical | 30-s workability + protocol mortality form for 72h | Sensor alarm as the only y |
| `NEED_CULTURE_METADATA` | Emersion clause on/off unknown | Culture type, ploidy, intertidal vs float | Assume Willapa = intertidal |
| `NEED_WORKABILITY_THRESHOLD` | Wave clause dropped | Partner “do not work this tide” rule | Invented Hs |
| `NEED_EMERSION_GEOMETRY` | Tide table without bed elevation / bag height | Lease emersion hours vs CO-OPS 9440910 offset | SST as body T |
| `NEED_IN_SITU_SUPPORT` | Supporting DO/S/T missing in a basin where that mechanism matters | Existing NANOOS/Ecology station **distance documented**; optional on-lease T | SST-only High confidence |
| `NEED_AHW_SLICE` | `DISAGREE_UNUSUAL_OCEAN` / OOD climate | Keep issuing B4; flag 2021-type holdout; do not add MHW SST rule | Hobday flag as oyster kill |
| `NEED_HUMAN_PRIOR` | B5 missing; decision-value claims wanted | Pre-brief yes/no/already_planned | Harvest-plan question |
| `NEED_RIGHTS_CLEARANCE` | Feature exists but license UNKNOWN | Rights review, not a field trip | Ingest anyway |

**Default first observation for the canonical fixture:** `NEED_OUTCOME_LOG` + `NEED_HUMAN_PRIOR`, not a new habitat model.

---

## 5. Priority (hypothesis)

| Priority | When |
|---|---|
| P0 | `impact=high` and (`D=1` or DATA_GAP on outcomes) in a stocked intertidal cell |
| P1 | R3 OOD with medium/high impact even if \(D=0\) |
| P2 | `D=0.5`, medium impact, or missing B5 only |
| P3 | Metadata gaps (culture, thresholds) without an imminent work window |

Cap public/coarsened tickets so a bay-wide AHW does not emit one pin per H3 cell. Collapse to **growing area × day**.

---

## 6. What the planner must not do with this feed

- Task a survey to “count oysters” (planted stock; wrong quantity).  
- Treat disagreement as food-safety uncertainty.  
- Publish a heatmap of P0 tickets.  
- Auto-ingest partner logs because a ticket exists.  
- Open `MC-ST` / `MC-FW` training as the resolution.  
- Average the members so the ticket closes.

Closing a ticket requires the **observation** (or an explicit `cannot_collect` + reason), not a smoother model.

---

## 7. Sibling handoffs (when those folders exist)

| Sibling | Use of these fields |
|---|---|
| Change detection | \(D\) flipping day-to-day is not automatically an ocean change; require driver deltas (air, emersion, waves) |
| Detection bias | Missing logs are selection, not low stress |
| Causal ecology | Why-code `DISAGREE_ECOLOGICAL_ASSUMPTIONS` is a **hypothesis label**, not a causal claim |

Until those agents write, store codes only.
