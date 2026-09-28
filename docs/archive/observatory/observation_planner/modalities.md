# Observation modalities — planner view

**Date:** 2026-09-18  
**Companion catalog (do not duplicate physics):** `observatory/observation_modality_catalog.md`  
**Cost labels:** `ESTIMATE` = order of magnitude, not a quote. `UNKNOWN` = do not invent USD. `CITED` only if a named source is given here (this file mostly ESTIMATE/UNKNOWN).  
**Status:** Planner gating — when a modality may enter the candidate set, and when it must not.

This is **not** a shopping list. New hardware is last on the ladder. W1 default: **do not** propose eDNA, gliders, hydrophones, or drones.

---

## Shared gates

A modality is eligible **only if**:

1. It reduces a **named** uncertainty on the locked target (W1: ops-stress / workability, not NSSP).  
2. Geography can be expressed as H3 res 5–6 or named water-body.  
3. Kill rules would not fire (`scoring_spec.md`).  
4. Ladder stage is respected.  
5. A human must approve before any platform moves.

**FP/FN** below are qualitative. Do not print fake detection rates.

---

## 1. eDNA sampler (targeted qPCR / metabarcoding / autonomous)

| Field | Assessment |
|---|---|
| **Maturity** | Operational-adjacent for **occupancy**; not operational abundance |
| **Cost band** | ESTIMATE: **LOW–MED** per opportunistic sample (lab dominates); **HIGH** for autonomous ESP-class networks |
| **Typical FP** | Contamination; rare-taxa inflation; transport from elsewhere |
| **Typical FN** | Primer dropout, inhibition, shedding below LOD, wrong depth |
| **IG** | Occupancy / community; tracer with hydrodynamics — **not** \(N\), not GPS |
| **W1** | **Do not use** as next observation (stock already known) |
| **Privacy** | Rare/listed positives at native GPS = `NEVER_PUBLISH` |

**When NOT to use**

- To count farmed oysters or reopen harvest.  
- To locate spawning aggregations or listed fishes.  
- As a substitute for farm mortality logs.  
- Across a thermocline “because the bottle was handy.”  
- Before a lab with blank discipline exists.

**Fallback:** partner logs (W1); visual/camera occupancy in one estuary (research).

---

## 2. Glider / AUV (physics, optics, optional EK/eDNA)

| Field | Assessment |
|---|---|
| **Maturity** | Operational for T/S/O2/optics regionally (IOOS glider DACs); biology payloads local |
| **Cost band** | ESTIMATE: **HIGH** per campaign vs a form; cheaper than a dedicated ship-day if already in theater |
| **Typical FP/FN** | Physics: calibration/biofouling. Biology payloads inherit camera/EK/eDNA errors |
| **IG** | **Vertical** structure (hypoxia, thermocline) — high where that is the named error (Hood Canal DO; Chinook depth of 8–12 °C). Near-zero for Willapa intertidal **air** heat |
| **W1** | **Not a next observation.** Open-Pacific glider for SST is `KILL_WRONG_TARGET` + usually `KILL_HARDWARE_BEFORE_LADDER` |
| **Privacy** | Camera/EK tracks can reveal fishing spots — coarsen |

**When NOT to use**

- W1 emersion-heat / farm workability.  
- As a fish census.  
- In EEZs without notification/permission.  
- To densify listed-species locations.

**Fallback:** existing NANOOS/NERRS/ORCA **in the correct basin**; partner sondes.

---

## 3. Hydrophone / PAM / DAS

| Field | Assessment |
|---|---|
| **Maturity** | Operational monitoring in sanctuaries; DAS research for low-frequency baleen |
| **Cost band** | ESTIMATE: **MED** SoundTrap-class unit unknown USD; **LOW** if reusing NCEI archives; DAS access **UNKNOWN** |
| **Typical FP** | Detector false calls; shipping; other species |
| **Typical FN** | Non-calling animals; masking; duty cycle |
| **IG** | Vocal **presence**; silence ≠ absence |
| **W1** | **Not applicable** (oysters are not a PAM target) |
| **Privacy** | Localization / bearings / live listed callers = `NEVER_PUBLISH` |

**When NOT to use**

- To find fish choruses that map spawning aggregations.  
- To publish NARW-precision tracks.  
- As abundance.  
- For W1.

**Fallback:** official Slow Zone **links**; archive reuse for research occupancy.

---

## 4. Vessel of opportunity — water sample (SOOP / ferrybox / extra Niskin)

| Field | Assessment |
|---|---|
| **Maturity** | Operational in pockets (ferrybox, CPR, underway T) |
| **Cost band** | ESTIMATE: **LOW** marginal if the ship already steams; **MED** if it adds station time |
| **Typical FP/FN** | Same as the payload (eDNA, chl, T); route bias |
| **IG** | Occupancy/physics along **existing** tracks — not a designed survey |
| **W1** | Low. Willapa leases are not a Pacific transit problem |
| **Privacy** | Do not publish track+sample as a targeting layer |

**When NOT to use**

- As the W1 label.  
- To chase rare eDNA along a highliner track.  
- Before asking partners for the logs they already have.

**Fallback:** dock/intake sample in a designed occupancy box (research); partner export.

---

## 5. Aerial / drone

| Field | Assessment |
|---|---|
| **Maturity** | Operational for marine-mammal/seabird surveys; UAV mature nearshore/farms |
| **Cost band** | ESTIMATE: **MED** small UAV AOI; manned survey **HIGH** |
| **Typical FP/FN** | Glare, ID error; availability bias when animals are down |
| **IG** | Surface-available megafauna; intertidal **gear/emersion extent** if partner-consented |
| **W1** | Optional **later** for “were beds emerged / gear standing” — **not** before forms and existing loggers; disturbance + farm privacy |
| **Privacy** | Haul-outs, people, lease layout. Harassment is a harm cost |

**When NOT to use**

- Over pinniped haul-outs or bird colonies for “ completeness.”  
- As a public farm map.  
- BVLOS without aviation/sanctuary review.  
- Before ladder stages 1–5.

**Fallback:** partner photo on the 30-second form (PRIVATE, EXIF stripped); tide tables.

---

## 6. Scientific survey allocation (which stratum to add / revisit)

| Field | Assessment |
|---|---|
| **Maturity** | Operational inside agencies (ICES/NOAA design) |
| **Cost band** | ESTIMATE: **HIGH** (ship-days); planner may only **suggest strata at official-unit grain** |
| **Typical FP/FN** | Design-based if protocol held; wrecked if opportunistic |
| **IG** | Category B indices at **seasonal** scale — not 72 h farm ops |
| **W1** | **Wrong horizon.** Do not allocate a trawl survey to score oyster workability |
| **Privacy** | Unpublished PI stations `RESTRICTED` / `NEVER_PUBLISH` |

**When NOT to use**

- 24–72 h operator products.  
- To “fill empty ocean” on a public heatmap.  
- Mixing Olympia vs Pacific, or legal vs all lobster, as one stratum.

**Fallback:** partner outcomes; existing VTS/sea-sampling **as seasonal priors**, not W1 labels.

---

## 7. Camera / sonar (BRUV, farm cam, EK80, mapping sonar)

| Field | Assessment |
|---|---|
| **Maturity** | Operational in surveys and some farms; species-ID from EK **not solved** in mixed fish |
| **Cost band** | ESTIMATE: BRUV **LOW–MED** hardware; ship EK **HIGH** unless already installed (then marginal **LOW** if shared privately) |
| **Typical FP/FN** | Bait bias, turbidity, TS overlap, siphonophores |
| **IG** | Presence / relative composition in frame; backscatter index with ID haul |
| **W1** | Weak for 72 h heat-kill; optional gear-integrity later |
| **Privacy** | Echotracks and frames can burn holes |

**When NOT to use**

- As species census without ID.  
- High-power sonar near mammals without review.  
- Public fishing-spot reconstruction.  
- W1 before logs/thermistor/air×tide.

**Fallback:** human gear-loss flag on the outcome form.

---

## 8. Which environmental variable to measure **better**

Rank **variables**, then instruments. W1 order (marine-domain + quality B4):

| Rank | Variable | Why | Better instrument | Not this |
|---:|---|---|---|---|
| 1 | Air T **during daytime emersion** | 2021 mechanism | NWS/met + **on-bed/bag** thermistor | SST pixel |
| 2 | Tide / emersion duration / elevation | Hours of air | CO-OPS + **culture elevation metadata** | Moon table as mortality |
| 3 | Partner outcome (workability, mortality flag, intervention) | Label | 30-second form | DOH closures |
| 4 | Wind / wave vs **farm-specific** work rule | Ops disruption | NWS/GFS-Wave + **their** threshold | Invented knot limit |
| 5 | Water T at the lease | Supporting co-stress | Existing farm sonde / nearest **Willapa** station | Hood Canal ORCA as Willapa |
| 6 | DO | Hypoxia co-stressor (basin-dependent) | Local sonde; **not** inferred from SST | Copy Hood Canal law to Willapa |
| 7 | Salinity / runoff | Flood / freshwater pulse | Gauge + local S | NSSP rainfall rule as mortality |
| 8 | SST | Lagged, mismatched supporting only | Already abundant | Primary W1 driver |
| — | pH / Ω | Larval hatchery story | Out of W1 adult 72 h | Headline OA nowcast |
| — | Chlorophyll | Growth weeks–months | Not 72 h mortality | Abundance |
| — | Bottom T (GOM lobster, not W1) | Catchability | eMOLT-class | SST |

**Global (non-W1) later:** prefer **bottom T** over SST for benthic CPUE; **subsurface T** over SST for Chinook habitat; **oxygen** on stratified shelves; never AIS.

---

## 9. Manual structured observation / partner form (first-class modality)

| Field | Assessment |
|---|---|
| **Maturity** | Operational wherever a protocol exists (this program: spec only) |
| **Cost band** | ESTIMATE: **VERY LOW** (30 s) |
| **Typical FP/FN** | Recall error; non-response |
| **IG** | **Highest W1** — is the label |
| **Privacy** | `PRIVATE`; no public leaderboard |

**When NOT to use:** as a public rare-species form; requiring exact GPS; as a food-safety report to DOH (point them to official channels).

---

## 10. Ladder vs modality (enforcement)

| Ladder stage | Typical modalities |
|---|---|
| Public data | Tide, NWS air, waves, licensed model fields — **pair**, don’t pile SST |
| Partner export | Spreadsheets, HOBO CSV, culture metadata |
| Existing sensors | Farm sondes, NANOOS **in-basin**, CO-OPS |
| Manual structured | 30 s / 14-day paper |
| Mobile capture | Same fields as manual |
| Integration | Farm software they already pay for |
| New hardware | Extra thermistors, cameras, gliders — **only after the above fail a documented test** |

If a candidate’s modality is new hardware while a higher-ladder option for the **same EUR** exists, drop hardware (`KILL_HARDWARE_BEFORE_LADDER` or `Feas` cap).
