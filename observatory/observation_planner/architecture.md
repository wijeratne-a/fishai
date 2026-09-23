# Architecture — Active Observation Planner

**Date:** 2026-09-18  
**Status:** DESIGN ONLY. No scheduler, no tasking bus, no ingest.  
**Rule:** a scored recommendation is a **memo to a human**, not a command to a platform.

---

## 1. Placement in the stack

```text
uncertainty tiles (H3 res 5–6 + official units + depth bins)
        × EMIV coverage / missing-critical map
        × modality catalog (ladder-filtered)
        → batch scorer (OVS)
        → kill-rule filter
        → coarsen geography
        → HUMAN APPROVAL
        → (later) partner request or rights-cleared public pairing
        → never auto-task vessels / drones / samplers
```

Commercial W1 binds the same engine to **one estuary**. The observatory schema may later add global tiles; it must **not** implement a global lake or a public animal map (`global_digital_twin_architecture.md`).

v0 DA remains **open-loop B4 + B12 + uncertainty rules**. The planner does not assume an EnKF.

---

## 2. Batch job (logical)

**Trigger:** daily in W1 season (hypothesis: May–September), weekly otherwise; on named NWP heat/storm events. This pass does not run the job.

**Inputs (when lawful, later):**

| Input | Source of truth | This pass |
|---|---|---|
| Uncertainty tiles | `observation_density`, `missing_data_state`, `confidence_category` | Empty — design the keys |
| EMIV coverage | `observatory/emiv/` registry `v0.1-draft` | Bind `emiv_id` from the registry; unresolved stubs in `engine_id_crosswalk.md` |
| Ladder state | Which stages are complete | All incomplete; hardware blocked |
| Harm / privacy | `sensitive_location_policy.md` | Apply kill rules |
| Candidate generator | Modalities × named gaps | W1 fixture list only |

**Outputs:** `ObservationRecommendation[]` (`recommendation_schema.md`). Persist append-only. Do not overwrite a killed rec; supersede with a new id.

**Spatial keys:** H3 res 5 (public/research coarsen, ~253 km² class) or res 6 (~36 km²) **or** official polygon (`WA DOH growing-area cluster`, named bay). Persist `cell_area_km2` later; H3 is not equal-area. **Res 8 is not a public planner grain.**

**No real H3 indexes in fixtures** so this folder cannot be used as a targeting list.

---

## 3. Human approval gate

| May happen without a named human | Must not |
|---|---|
| Score FIXTURE / DESIGN rows in git | Email a grower |
| Pair public tide tables on a whiteboard | Task a vessel, drone, glider, eDNA pump |
| Draft a DUA field list | Place a logger on someone else’s gear |
| Rank ladder stages | Scrape fortress.wa.gov or hidden iNat |

**Approver roles (hypothesis):** domain reviewer (shellfish) + privacy/harm reviewer + partner liaison. Software agents may only **tighten** kill rules, not loosen (`prediction_contract.md` amendment spirit).

If `human_approval_required` is stripped by a future API, that API is a defect (`KILL_NO_HUMAN_GATE`).

---

## 4. Partner-first before hardware

Encoded as both ladder order and kill rule `KILL_HARDWARE_BEFORE_LADDER`.

1. Public data (pair air × tide; do not pile SST)  
2. Partner export (outcomes, metadata, existing CSV)  
3. Existing sensors (farm HOBO, in-basin IOOS — correct basin)  
4. Manual structured (30 s / 14-day)  
5. Mobile capture of the **same** fields  
6. Integrations with software they already pay for  
7. New hardware (extra thermistors, then — much later — cameras/gliders)

W1 expected path stops at 4–5. A Pacific glider is not on this path.

---

## 5. EMIV coverage map (logical)

When `emiv/` exists, coverage is:

```text
(emiv_id, geography_key, depth_bin, time_window) →
  {present, stale, missing, rights_blocked, never_publish}
```

The planner proposes observations only for `missing` or `stale` on **admissible** IDs. `never_publish` IDs are never “gaps to fill” with a public rec.

Coverage keys use registry IDs (`recommendation_schema.md` §6). Recs may still list unresolved planner stubs; that is not `emiv_catalog=UNAVAILABLE`. No ingest implied.

---

## 6. What not to build yet

- Kafka/Airflow tasking of platforms  
- Public WebGL globe of recs (`fishai/globe/**` out of scope)  
- Vector DB of secret spots  
- Reinforcement-learning survey agent  
- Auto-email to skippers  
- Consumption of GFW/AIS as animal density  
- Global eDNA mesh scheduler  

MVP compute, if ever: a Python batch on local parquet of **coverage flags**, not live ocean.

---

## 7. Failure modes

| Failure | Mitigation |
|---|---|
| High OVS on a nest pin | Kill rules + coarsen + no real H3 |
| Planner waits forever for satellite | EUR cap on SST; label-first W1 |
| Planner becomes NSSP | `KILL_NSSP_IMPERSONATION`; DOH is overlay |
| Empty cells painted as absence | Ternary `NO_OBSERVATIONS` |
| Hardware vendor-driven roadmap | Ladder gate |
| Dual-use mosaic with iNat/AIS | `KILL_MOSAIC` |

---

## 8. Relation to commercial W1

The commercial product, if locked, needs **outcome capture + air×tide brief**, not this planner as a user-facing feature. The planner is **internal ops/research tooling** that tells the team what to collect next. It must not appear as a public “recommended fishing/harvest cell.”
