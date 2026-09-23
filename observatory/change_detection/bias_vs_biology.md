# Bias vs biology — mandatory decision tree

**Date:** 2026-09-18  
**Status:** Binding on every change-detection record.  
**Rule name:** **Observation-artifact rule.**  
**This pass:** apply to fixtures only. Do not run a live detector.

A biological event class is illegal unless this tree completes and does not terminate on `DATA_GAP` or `POSSIBLE_OBSERVATION_ARTIFACT`. Skipping nodes because “the map looks like a crash” is a red-team fail (`RT-OBS-03`, `RT-OBS-05`, `RT-OBS-09` in `observatory/scientific_red_team_reports/observatory_red_team_01.md`).

Companion methods: `methods.md`. Schema: `event_schema.md`.

---

## 0. How to use the tree

- Evaluate nodes **in order**. First terminal class wins.  
- Record the **exit node id** on the event (`review_gate_ids` / notes).  
- Observation-process explanations are listed **before** ecological ones.  
- Ties go to the weaker claim (`DATA_GAP` > artifact > possible process).  
- `POSSIBLE_*` means unconfirmed. It is not a diagnosis and not an alert.

**Universal bans (apply at every node):**

- Reduced observation rate ≠ population decline.  
- SST / chlorophyll / AIS ≠ abundance, range, mortality, or HAB toxin.  
- WA DOH / NSSP open-closed ≠ oyster ops-stress *y*.  
- No public aggregation or lease-KPI map.  
- No operational alert from this folder (`issued_as_operational_alert=false`).

---

## 1. Decision tree

```
N0  Fixture / live gate
    │
    ├─ record is not FIXTURE and product gates are open? → STOP (no writer in this pass)
    └─ else continue (fixtures reconstruct classification only)
            │
N1  Grain / stage / depth coverage
    │  Is the claimed taxon × official unit × depth bin × life stage
    │  actually observed in both baseline and window (or is the gap the claim)?
    │
    ├─ NO → DATA_GAP                    [exit E-GAP]
    └─ YES → N2
            │
N2  Wrong-label / authority wall
    │  Is the only “signal” an official harvest, sanitation, season, or toxin
    │  closure, or AIS/VMS, or a habitat raster with no biological index?
    │
    ├─ YES, harvest/toxin authority only → do not emit biological class;
    │     attach as constraint; ops series → DATA_GAP or NO_SIGNIFICANT_CHANGE
    │     depending on whether ops GT exists        [exit E-AUTH]
    ├─ YES, AIS/chl/SST as animals → POSSIBLE_OBSERVATION_ARTIFACT
    │     (usually Category E misuse)               [exit E-PROXY]
    └─ NO → N3
            │
N3  Effort comparability
    │  Is sampling effort (visits, angler-hours, trap-hauls, survey tows,
    │  clear-sky days, eDNA volume, logger uptime, farm-walk days)
    │  known or bounded and comparable after a documented standardisation?
    │
    ├─ effort missing or incomparable → DATA_GAP or POSSIBLE_OBSERVATION_ARTIFACT
    │     (prefer DATA_GAP if you cannot even sign the bias)   [exit E-EFFORT]
    ├─ effort fell and raw counts fell in the same direction,
    │     no p-correction → POSSIBLE_OBSERVATION_ARTIFACT     [exit E-EFFORT-DROP]
    └─ effort OK or corrected → N4
            │
N4  Detection probability / catchability / platform
    │  Could p(detect), catchability, gear, observer, water clarity,
    │  acoustic frequency, eDNA assay, regulation, or weather-workability
    │  produce the same sign without a density change?
    │
    ├─ yes, and not modeled/bounded → POSSIBLE_OBSERVATION_ARTIFACT [exit E-P]
    └─ no or bounded → N5
            │
N5  Spatial transfer / wrong instrument geography
    │  Is the series borrowed from another basin, depth, or program
    │  (e.g. Hood Canal ORCA used as Willapa DO; SST pixel as intertidal tissue)?
    │
    ├─ YES → DATA_GAP (wrong grain) + note confounder           [exit E-TRANSFER]
    └─ NO → N6
            │
N6  Process identification (what kind of biology, if any)
    │
    ├─ residual within pre-registered climatology band
    │     → NO_SIGNIFICANT_CHANGE                               [exit E-NSC]
    │
    ├─ mortality / disruption pathway?
    │     Independent outcome (protocol count, published survey, farm log)
    │     OR named physical path with the RIGHT variables
    │     (W1 intertidal: air × daytime emersion × solar; not SST-only;
    │      not Hobday marine-heatwave SST percentile as the 2021 analogue)
    │     → POSSIBLE_MORTALITY_EVENT                            [exit E-MORT]
    │     else do not use this class
    │
    ├─ HAB?
    │     Named taxon + animal-stress mechanism (feeding shutdown, yessotoxins
    │     as grower-stress hypothesis, Heterosigma, etc.)
    │     AND explicitly not NSSP/PSP/DSP/ASP harvest stamp
    │     → POSSIBLE_HAB_EVENT                                  [exit E-HAB]
    │     tissue-toxin / growing-area closure only → back to E-AUTH
    │
    ├─ timing of a designed seasonal index moved after effort calendar
    │     → PHENOLOGY_SHIFT                                     [exit E-PHEN]
    │
    ├─ vertical index moved after detectability correction
    │     → DEPTH_SHIFT                                         [exit E-DEPTH]
    │
    ├─ spatial centroid / occupancy edge moved after effort/p
    │     → RANGE_SHIFT                                         [exit E-RANGE]
    │
    ├─ occupancy/spread increase after correction, or labeled transport
    │     → DISPERSAL_EVENT                                     [exit E-DISP]
    │
    └─ unusual concentration
          → AGGREGATION_EVENT                                   [exit E-AGG]
            privacy: default NEVER_PUBLISH at native grain;
            W1 commercial: do not emit as a product map
```

After N6, always fill `alternative_explanations[]` with at least one observation-process alternative **even when** a biological class is assigned.

---

## 2. Worked exits (W1 and research)

| Exit | Typical story people want | What the engine says |
|---|---|---|
| **E-EFFORT-DROP** | “Oyster abundance collapsed; fewer survey points this winter” | `POSSIBLE_OBSERVATION_ARTIFACT`. Planted stock is sessile; visit rate is not *N*. |
| **E-PROXY** | “SST +1.8 °C so the lease died” | Not a mortality class. SST-only ⇒ confidence **low/none** (prediction contract). Need air × emersion. |
| **E-TRANSFER** | “ORCA Hood Canal is hypoxic, so Willapa oysters …” | `DATA_GAP`. Different basin, different mechanism mix (heat/food vs stratification). |
| **E-AUTH** | “DOH closed the area, ops-stress model should alert” | Closure is Module A **context**, not `ops_disruption_72h` *y*. |
| **E-MORT** | 26–28 Jun 2021 heat dome × lowest tides | `POSSIBLE_MORTALITY_EVENT` as a **literature fixture**, air×tide pathway, delayed deaths possible outside 72 h. Still not an operational 2026 alert. |
| **E-HAB** | 2018–19 grower die-offs; *Protoceratium*/yessotoxins hypothesized | `POSSIBLE_HAB_EVENT` only as animal-stress hypothesis; **not** “safe/unsafe to eat.” |
| **E-AGG** | “New oyster beds / whale / grouper spawn pin” | Class exists for research bookkeeping; public product **withheld**. |
| **E-RANGE** | “Pacific oysters shifting poleward this week on the lease” | Not applicable at W1 72 h (sessile planted). Research range shifts need surveys + effort. |

---

## 3. Special rules by tempting failure mode

### 3.1 Reduced observation rate

If `n_obs_window / n_obs_baseline` falls and the raw biological count falls:

1. Standardize (rate per effort).  
2. If the standardized index is stable → `NO_SIGNIFICANT_CHANGE` or artifact of reporting.  
3. If you cannot standardize → `DATA_GAP`.  
4. **Never** emit relative-abundance low, recruitment failure, or mortality solely from *n_obs*.

Literature spine: MacKenzie et al. 2002 occupancy (*p* vs ψ); Harley, Myers & Dunn 2001 hyperstability of CPUE; Maunder & Punt 2004 standardization.

### 3.2 Catchability and weather

Chinook and lobster: wind/swell and bottom temperature move **catchability** (and whether a trip happens). A quiet CPUE week can be a workability week. Classify as artifact until soak/hours/bottom T are in the index (`model_limitations.md`).

W1: inability to work a tide is an **ops** outcome (`LEASE_WORKABILITY_LOG`), not wild abundance.

### 3.3 Habitat suitability deteriorating

An EMIV flag (warming, hypoxia, low Ω) may be real physics and still say **nothing** about current *N*. Attach as `related_env_anomalies[]`. Do **not** create a biological class from the raster. Occupancy/CPUE after N3–N4 may later support `RANGE_SHIFT` / `DEPTH_SHIFT` / `POSSIBLE_MORTALITY_EVENT`.

### 3.4 eDNA and acoustics

eDNA occupancy ≠ GPS of live animals; copies/L ≠ biomass. Acoustic NASC ≠ species-*N*. Anomalies in those series default to `POSSIBLE_OBSERVATION_ARTIFACT` or `DATA_GAP` until an observation operator (transport/decay, TS calibration) is documented (`physics_feasibility_reports/physical_limits.md`).

### 3.5 Platform and management-era breaks

New gauge size, new e-logbook mandate, new satellite, new PCR assay, COVID sampling collapse: treat as **change-points in the observation process** first (`methods.md` §change-point). Biological change-points require the observation change-point to be ruled out.

### 3.6 Sensitive concentration

If N6 points to `AGGREGATION_EVENT` for spawn, nursery, haul-out, nest, or remnant invertebrate beds:

- `privacy_tier=NEVER_PUBLISH` at capture resolution.  
- `task_type=DO_NOT_COLLECT_SENSITIVE_GPS` unless a statutory/partner protocol with coarsening exists.  
- `product_claim_family=SUPPRESSED_PRIVACY`.  
- No public story.

---

## 4. Confidence after the tree

Even a correctly classed `POSSIBLE_MORTALITY_EVENT` is **low** or **none** when:

- critical local sensors missing;  
- SST-only thermal path;  
- no partner outcome stream;  
- extrapolation (heat dome analogue never seen in the fitted climatology — there is **no fitted climatology** today).

`high` is unavailable in this pass (no prospective calibration; uncertainty policy). Fixtures use `low` or `none` except where a **mechanism** is tier-1 literature and we still refuse product High.

---

## 5. One-sentence form (paste onto every record)

> Observation-artifact rule: do not interpret a change in detections as a change in animals until effort and detection probability are comparable, coverage exists at the claimed grain, official closures are not used as biological labels, and SST/chlorophyll/AIS are not treated as abundance; otherwise class `DATA_GAP` or `POSSIBLE_OBSERVATION_ARTIFACT`.
