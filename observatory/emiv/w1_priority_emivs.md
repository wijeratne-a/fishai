# W1 priority EMIVs — Willapa Pacific oyster 72 h OPS-RISK

**EMIV set:** v0.1  
**Date:** 2026-09-18  
**Candidate (RECOMMENDED, not DECIDED):** Pacific oyster (*Magallana gigas*, WoRMS Aphia 836033) × Washington growing areas (Willapa recommended) × farm operator × 24–72 h **operational disruption risk**.

**Target name:** `ops_disruption_72h`  
**Prediction class:** Category **D** relative stress/disruption risk, evaluated against partner outcomes — **not** abundance, **not** NSSP harvest legality, **not** vibrio-safe-to-eat.

Sibling sources (read, not copied into commercial `artifacts/`): marine-domain variable matrix, W1 GT relabel, scientific red team, sensitive-location policy.

---

## 1. What W1 is and is not

| Is | Is not |
| --- | --- |
| Ops-risk on **already planted** stock | Wild oyster abundance or recruitment |
| Physics of **air × midday emersion × solar**, water T, DO, salinity, waves/wind | SST-only marine heatwave story (SST ≠ tissue/bag T) |
| Labels from **partner farm logs** | WA DOH commercial closures as `y` |
| Constraint overlay: **harvest legally open?** via the authority | FishAI harvest authorization (WAC 246-282-006) |
| Willapa (or a named growing area) as geography | Hood Canal ORCA as Willapa truth |

Public closures **miss heat-kill and gear damage when harvest stays legally open.** Training ops-stress on closures, or printing ops-stress as harvest legality, is a **BLOCKER**.

---

## 2. W1_CORE list (registry `model_use_status`)

Ten rows. All are `LITERATURE` or `PROTOCOL_ONLY` for the **physics**, and the **label is `UNVALIDATED`** (no partner logs in this repo; none ingested).

| ID | Name | Role in 72 h ops-risk | Why core |
| --- | --- | --- | --- |
| **EMIV-PHY-ATEMP-001** | Near-surface air temperature | Causal aerial heat/desiccation when emersed | 2021 heat dome + midday minus tides (Raymond et al. 2022, *Ecology*, https://doi.org/10.1002/ecy.3798) |
| **EMIV-PHY-TIDE-001** | Tide stage / water level | Clock of exposure and flushing | NOAA CO-OPS official in WA waters https://tidesandcurrents.noaa.gov/ |
| **EMIV-PHY-EMERS-001** | Intertidal emersion duration and timing | Realized exposure window | Air T does nothing to a raft that never emerses; bag elevation is required metadata |
| **EMIV-PHY-SOLAR-001** | Incoming solar / insolation during emersion | Midday sun on emerged culture | Third term of the expert-rule product air × midday emersion × solar. **Not chlorophyll.** |
| **EMIV-PHY-WTEMP-001** | Near-surface bulk water temperature | Metabolism / summer co-stressor | In situ (NANOOS/NERRS/farm loggers). SST is not this row |
| **EMIV-BGC-DOXY-001** | Dissolved oxygen | Hypoxia co-stressor | No satellite DO; **do not impute from SST**. Stratified basins (Hood Canal literature) ≠ automatically Willapa |
| **EMIV-PHY-SALIN-001** | Practical salinity | Flood / freshwater pulse stress | Euryhaline species; acute lows + TSS/contaminants |
| **EMIV-PHY-WAVE-001** | Sea state / waves | Gear loss, burial, workability | Operational disruption, not physiology |
| **EMIV-PHY-WIND-001** | Surface wind | Workability, wave generation, mixing | NWS/NDBC; local fetch UNKNOWN in global models |
| **EMIV-ECO-OPSOUT-001** | Farm operational outcome | **Label:** mortality, workability, intervention | Only partner logs (DUA). PRIVATE / NEVER_PUBLISH publicly |

**High-value CANDIDATE — W1_CORE when a partner sensor exists:** `EMIV-PHY-TISST-001` tissue or bag/bed thermistor temperature (organism/gear thermal state). Distinct from `EMIV-PHY-SST-001` (**PROXY**) and `EMIV-PHY-WTEMP-001` (bulk water). Do not SST-fill.

**Required metadata (not separately W1_CORE, but the air-heat pathway is unidentified without it):** `EMIV-HUM-CULT-001` culture method and tidal elevation class (intertidal vs subtidal, bag vs bottom vs raft).

**Quality gates on every issuance (CANDIDATE, still mandatory as process):** `EMIV-QUA-FRESH-001`, `EMIV-QUA-QFLAG-001`, `EMIV-QUA-CALIB-001`, `EMIV-QUA-DCOV-001` (v0 bins: `INTERTIDAL_AIR` + `SURFACE_0_5`).

---

## 3. W1_PROXY (allowed with mismatch flag)

| ID | Name | Mismatch | Allowed use |
| --- | --- | --- | --- |
| **EMIV-PHY-SST-001** | Satellite SST (skin/foundation) | Skin ≠ bulk; **not tissue/bag T**; **misses aerial heat on emersion**; land contamination in estuaries; not DO; not farm outcome | Fill well-mixed unstratified shallow water T **only** when in situ WTEMP is missing; never headline; never abundance; never a stand-in for `EMIV-PHY-TISST-001` |
| **EMIV-BGC-RUNOFF-001** | Freshwater runoff / precip | Proxy for salinity/turbidity pulses, not oyster measurement; also used in some NSSP **conditional** hydrology — that is harvest constraint, not mortality | Event covariate; not `y` |

Copernicus global PHY `thetao` at ~1/12° is a **coarser cousin of the SST/WTEMP proxy path**, not Willapa creek truth.

---

## 4. Must-show constraint — not W1_CORE, not the label

| ID | Name | Role |
| --- | --- | --- |
| **EMIV-HUM-HARV-001** | Official harvest / closure / growing-area status | **“Is harvest legally open?”** Authority link to WA DOH / NSSP. `model_use_status=CANDIDATE`. |

**WA DOH commercial closures are not the ops label.** They are human-pressure / regulatory constraint. Fecal indicators (`EMIV-BGC-FECAL-001`) feed NSSP; they are not heat-kill.

Do not scrape fortress.wa.gov if TOS/robots forbid it; request an export. Redistribution licence: **UNKNOWN**.

---

## 5. Explicitly out of W1 headline

| Topic | EMIV if any | Why out |
| --- | --- | --- |
| OA / Ω_ar / pH as adult 72 h killer | `EMIV-BGC-PH-001`, `OMEGA-001` | Wrong stage (larval/seed crisis 2009) |
| Chlorophyll as mortality or abundance | `EMIV-BGC-CHL-001` | Weak 72 h; planted stock ≠ chl |
| Moon phase | — | Tide tables already capture the useful part |
| OsHV-1 | `EMIV-ECO-DIS-001` **DEFERRED** | Not detected at OR/WA sentinels 2020; do not import CA |
| SoundToxins HAB cells | `EMIV-ECO-HAB-001` | Conditional covariate; partner-gated; **not** legal reopen; **not** GT |
| LiveOcean 3-D T/S/O2 | maps to WTEMP/SALIN/DOXY | Rights **UNKNOWN** — DEFER paid layers |
| ORCA Hood Canal (Twanoh, Hoodsport, Dabob) | in situ methods for WTEMP/DOXY/SALIN | **Not Willapa.** Document out-of-sample if used |
| AIS | `EMIV-HUM-AIS-001` **DEFERRED** | Not oysters; privacy |

---

## 6. Minimum W1 issuance packet (design only)

For a named lease/growing area and issuance time `t`:

1. **Label path** (training/eval only, partner ACL): `EMIV-ECO-OPSOUT-001` at 24–72 h. If missing → no ops-stress **skill claim**.
2. **Constraint column** (user-facing authority): `EMIV-HUM-HARV-001` as posted, not as `y`.
3. **Core env:** ATEMP, TIDE, EMERS (needs culture elevation), SOLAR, WTEMP-001, DOXY (or explicit UNKNOWN — never SST-filled), SALIN, WAVE, WIND. TISST if a partner thermistor exists (then W1_CORE for that issuance).
4. **Proxy flags:** SST and RUNOFF only if tagged proxy. SST is **not** tissue T.
5. **Quality:** freshness, QC flags, calibration/fouling, which depth bins were actually observed.
6. **Copy wall:** not food-safe, not harvest-legal, not navigation, not abundance.

Until partner logs exist, W1 is at most a **constraint + covariate** brief. That is not T6 and not OPERATIONAL.

---

## 7. Evidence ceiling (do not upgrade)

| Claim | Ceiling |
| --- | --- |
| Air × emersion can kill intertidal oysters | `LITERATURE` (Raymond 2022 and related heatwave work) |
| CO-OPS tides are usable predictions | `PROTOCOL_ONLY` (agency operational ≠ FishAI ops-risk skill) |
| Farm logs predict 72 h disruption | `UNVALIDATED` (no logs here) |
| SST nowcast of Willapa kill | Fail if presented as core; `W1_PROXY` only |
| Global CMEMS skill in Willapa | UNKNOWN / generally too coarse |

No W1 EMIV is `OPERATIONAL` in registry v0.1-draft.
