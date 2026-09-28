# W1 Willapa oyster plan — first slice of the Active Observation Planner

**Date:** 2026-09-18  
**Wedge:** RECOMMENDED, not DECIDED — Pacific oyster (*Magallana gigas*, AphiaID 836033) × **Willapa Bay named growing waters** × farm operator × 24–72 h **ops-stress / workability** (Category D).  
**Status:** `DESIGN_FIXTURE` only. No ingest. No partner contact from this file. **Do not task** vessels, drones, gliders, or samplers.  
**Geography grain:** named water-body + synthetic H3 res 5–6 IDs. **No lease-corner GPS.**

This is the **first slice** of the information-gain engine. Global PAM/eDNA/glider planning is deferred (`architecture.md`). Commercial integration files are out of scope.

---

## 1. Decision and non-decisions

**Ask:** What should a Willapa grower watch in the next 72 h so that an ops-stress brief is **evaluable and physically on-mechanism**?

**Honest target:** relative operational disruption / environmental-stress **indicator** — workability of the tide, emersion-heat exposure, wave/gear — **not** survival guarantee, **not** yield, **not** NSSP.

**Wrong targets (do not collect “next observations” for these as if they were W1 GT):**

| Wrong target | Why |
|---|---|
| WA DOH / NSSP growing-area closures, fecal coliform, biotoxin tissue, Vp control | Food-safety **authority**. Public closures **miss heat-kill and gear damage while harvest stays legally open**. Training `ops_disruption_72h` on closures is a **BLOCKER** (`ground_truth_relabel_W1.md`; WAC 246-282-006) |
| More satellite SST | Skin ≠ intertidal body/bag T; 2021 kill was **atmospheric heat × midday emersion** (Raymond et al. 2022 *Ecology* https://doi.org/10.1002/ecy.3798) |
| Open-Pacific glider | Wrong basin, wrong depth bin (`INTERTIDAL_AIR` vs pelagic), hardware-before-ladder |
| Hood Canal ORCA as Willapa | **Hood Canal ≠ Willapa instrumentation** |
| eDNA / hydrophone / AIS | Wrong quantity |
| Mixing *Ostrea lurida* | Different taxon; 2021 mortality differed |

**Must-show, not a sample plan:** link official DOH harvest-open status with timestamp. That is a **constraint module**, not a planner rec to “go sample closures.”

---

## 2. Mechanism → observation classes

From marine-domain + quality B4 (hypothesis thresholds, not WA law):

1. **Air temperature overlapping daytime low-tide emersion** (solar as input).  
2. **Culture method / tidal elevation** (intertidal bag vs subtidal vs bottom).  
3. **Wind/wave workability** using the **farm’s** rule, not an invented knot limit.  
4. **Partner outcomes:** worked the tide? hard/abort? handling done? mortality-above-normal? gear? intervention?  
5. Supporting: lease water T, DO, salinity — **in-basin**.

A **30-second outcome form** (`artifacts/product_and_monetization/outcome_capture_spec.md`) can beat a new sensor on OVS: it is the **label**, it is on the ladder, and it is cheap. Existing bag thermistors beat new gliders.

---

## 3. Scoring notes (FIXTURE)

Weights and kill rules: `scoring_spec.md`. Inputs are **uncalibrated hypotheses**. Arithmetic is shown so a reviewer can reject a row without rejecting the formula.

Detection ternary: `NOT_APPLICABLE` (planted stock). Unstocked lease ≠ “oysters absent from Willapa.”

`privacy_tier`: logs and bag T = `PRIVATE`. Public air×tide pairing = `PUBLIC` physics (still not a biological map). Harm review on fixtures: `FIXTURE_PENDING_HUMAN`.

Registry EMIV IDs: `recommendation_schema.md` §6 and [`../emiv/engine_id_crosswalk.md`](../emiv/engine_id_crosswalk.md). **`EMIV-HUM-HARV-001` is the harvest constraint, never the ops label. `EMIV-PHY-SST-001` is PROXY.**

---

## 4. Ranked fixture recommendations (8)

All `kill_flag=false`. Rank by OVS descending. **Not tasking orders.**

### Rank 1 — W1-FIX-R01 · Partner 30-second outcome form  
**OVS = 0.658**

| | |
|---|---|
| **Action** | Permissioned 30 s form per brief window: `worked_lease`, `workability` (ok/hard/aborted/na), `handling_done`, flags (gaping, mortality_above_normal, gear, freshwater_feel, low_do_feel), `brief_changed_plan`. Optional photo EXIF-stripped. |
| **Why highest** | Closes **LABEL_SUPPORT**. Public physics cannot invent `ops_disruption_72h`. Highest EVSI on this slice. |
| **Taxa / geo / depth / time** | *M. gigas* · Willapa named growing waters · `NA_METADATA` · each 24–72 h window |
| **Modality / ladder** | `MANUAL_STRUCTURED_OUTCOME_FORM` / `PARTNER_EXPORT` (same fields if they already keep a sheet) |
| **EUR 0.92 · EcoImp 0.70 · ConsPri 0.15 · DecVal 0.95 · FcstDis 0.85 · Feas 0.90 · CostEff 0.95 · Harm 0.02 · Legal 0.08** | |
| **IG method** | IMPLEMENTABLE_NOW: rule EUR + discrete EVSI on “is the brief evaluable?” |
| **Cost band** | ESTIMATE VERY LOW |
| **Validation objective** | Primary label; B5 workflow; completeness gates |
| **Uncertainty reduced** | `LABEL_SUPPORT`, Brier identifiability, B4 vs reality |
| **Ecological risk** | Negligible if no extra handling mandate |
| **Constraints** | DUA; not a DOH report; no exact GPS required; no neighbor publication |
| **Fallback** | 14-day paper protocol (R05) |
| **EMIV** | `EMIV-ECO-OPSOUT-001`, `EMIV-UNC-EUR-001` |
| **privacy_tier** | `PRIVATE` |

Weighted sum \(0.7575 - 0.10 = 0.658\).

### Rank 2 — W1-FIX-R02 · Pair public air forecast with tide (emersion-heat covariate)  
**OVS = 0.613**

| | |
|---|---|
| **Action** | Bind **already-paid** NWS/grid air temperature to **CO-OPS predicted water level** at the named Willapa station cluster (public Toke Point class — official gauge, not a farm pin) and solar geometry, to flag **daytime emersion ∩ heat**. Design only; no bulk archive pull in this pass. |
| **Why high** | Correct **variable pairing**. Does not require hardware. Ladder stage 1. Not “more SST.” |
| **Depth** | `INTERTIDAL_AIR` |
| **Modality / ladder** | `ENV_PUBLIC_PAIRING` / `PUBLIC_DATA` |
| **EUR 0.62 · EcoImp 0.72 · ConsPri 0.10 · DecVal 0.80 · FcstDis 0.55 · Feas 0.95 · CostEff 0.98 · Harm 0.00 · Legal 0.02** | |
| **IG** | IMPLEMENTABLE_NOW ensemble/timing disagreement between heat and tide |
| **Cost** | ESTIMATE VERY LOW (agency-paid) |
| **Validation** | B4 primary clause; confidence High forbidden if this pairing missing and only SST remains |
| **Uncertainty reduced** | `air_x_emersion` timing; SST-only failure mode |
| **Fallback** | Airport/met + published tide table, still paired |
| **EMIV** | `EMIV-PHY-ATEMP-001`, `EMIV-PHY-TIDE-001`, `EMIV-PHY-EMERS-001`, `EMIV-PHY-SOLAR-001`, `EMIV-MOD-B4-001` |
| **privacy_tier** | `PUBLIC` (physics) |

\(0.633 - 0.02 = 0.613\).

### Rank 3 — W1-FIX-R03 · Culture method, tidal elevation band, ploidy  
**OVS = 0.573**

| | |
|---|---|
| **Action** | One-time (then on change) partner metadata: intertidal bag / on-bottom / floating; elevation band (not cm GPS); diploid/triploid/mixed; seed vs market. |
| **Why** | Same estuary, opposite outcomes without this \(H\). Drop air×emersion clause if fully subtidal rather than substituting SST. |
| **Depth** | `INTERTIDAL_AIR` or `SURFACE_0_5` as declared |
| **Modality / ladder** | `PARTNER_METADATA` / `PARTNER_EXPORT` |
| **EUR 0.80 · EcoImp 0.65 · ConsPri 0.15 · DecVal 0.88 · FcstDis 0.70 · Feas 0.92 · CostEff 0.93 · Harm 0.02 · Legal 0.10** | |
| **Validation** | Stratify B4/B12; no pooling Olympia; no silent ploidy mix |
| **Uncertainty reduced** | \(H\) misspecification; culture confounding |
| **Fallback** | Coarse three-class self-report on the 30 s form |
| **EMIV** | `EMIV-HUM-CULT-001` |
| **privacy_tier** | `PRIVATE` |

\(0.693 - 0.12 = 0.573\).

### Rank 4 — W1-FIX-R04 · Export existing bag/bed thermistors  
**OVS = 0.566**

| | |
|---|---|
| **Action** | Copy HOBO/Onset/farm-sonde files **already on gear** (air/bag/mud). Do not buy loggers until it is shown partners have none. |
| **Why** | Adjudicates **air vs tissue/bag**. Highest physical EUR after the label. |
| **Depth** | `INTERTIDAL_AIR` |
| **Modality / ladder** | `EXISTING_LOGGER_EXPORT` / `EXISTING_SENSORS` |
| **EUR 0.88 · EcoImp 0.75 · ConsPri 0.12 · DecVal 0.85 · FcstDis 0.90 · Feas 0.70 · CostEff 0.80 · Harm 0.03 · Legal 0.12** | |
| **Feas 0.70** | Only if devices exist; else skip to R05, do **not** auto-upgrade to new hardware |
| **Uncertainty reduced** | `air_vs_tissue`; microclimate |
| **Fallback** | Manual max/min shade vs sun note on form (weak) |
| **EMIV** | `EMIV-PHY-TISST-001` (tissue/bag T; W1_CORE when partner sensor exists), `EMIV-PHY-ATEMP-001` |
| **privacy_tier** | `PRIVATE` |

\(0.7155 - 0.15 = 0.566\).

### Rank 5 — W1-FIX-R05 · 14-day paper protocol in a heat×emersion window  
**OVS = 0.529**

| | |
|---|---|
| **Action** | If digital export fails: same fields as R01 on paper for ~14 days during a high-risk tide/heat window. Record DOH harvest-open **alongside as constraint**, never as \(y\). |
| **Ladder** | `MANUAL_STRUCTURED` |
| **EUR 0.78 · EcoImp 0.68 · ConsPri 0.15 · DecVal 0.82 · FcstDis 0.75 · Feas 0.75 · CostEff 0.85 · Harm 0.04 · Legal 0.10** | |
| **Fallback** | R07 mobile of the **same** schema (not a new social app) |
| **EMIV** | `EMIV-ECO-OPSOUT-001`, `EMIV-HUM-HARV-001` (constraint alongside, never \(y\)) |
| **privacy_tier** | `PRIVATE` |

\(0.669 - 0.14 = 0.529\).

### Rank 6 — W1-FIX-R06 · Farm-specific “do not work this tide” wind/wave threshold  
**OVS = 0.492**

| | |
|---|---|
| **Action** | Ask the partner for **their** workability rule. If they have none, **do not invent one** (quality B4). Pair with public NWS/GFS-Wave. |
| **Depth** | `SURFACE_0_5` / NA |
| **Ladder** | `PARTNER_EXPORT` |
| **EUR 0.55 · EcoImp 0.40 · ConsPri 0.08 · DecVal 0.88 · FcstDis 0.50 · Feas 0.85 · CostEff 0.90 · Harm 0.00 · Legal 0.05** | |
| **Does not mean** | Weather-safety certification or “safe to work” |
| **EMIV** | `EMIV-PHY-WIND-001`, `EMIV-PHY-WAVE-001`, `EMIV-ECO-OPSOUT-001` |
| **privacy_tier** | `PRIVATE` (threshold) + public forecast physics |

\(0.5415 - 0.05 = 0.492\).

### Rank 7 — W1-FIX-R07 · Mobile / WhatsApp capture of the **same** 30 s fields  
**OVS = 0.443**

| | |
|---|---|
| **Action** | Magic link / “OK / HARD / ABORT” email reply **only if** R01/R05 completeness fails. Same schema. No new social network. No required lat/lon. |
| **Ladder** | `MOBILE_CAPTURE` (after manual/export) |
| **EUR 0.70 · EcoImp 0.65 · ConsPri 0.15 · DecVal 0.80 · FcstDis 0.70 · Feas 0.60 · CostEff 0.70 · Harm 0.05 · Legal 0.12** | |
| **Feas lower** | App fatigue; still before integrations/hardware |
| **EMIV** | `EMIV-ECO-OPSOUT-001` |
| **privacy_tier** | `PRIVATE` |

\(0.6125 - 0.17 = 0.443\).

### Rank 8 — W1-FIX-R08 · Existing **Willapa-relevant** in-situ water T/S (not Hood Canal ORCA)  
**OVS = 0.380**

| | |
|---|---|
| **Action** | Catalog and (later, after rights) use NANOOS NVS / NERRS / CO-OPS / farm sondes that actually represent **Willapa / adjacent Pacific County waters**. Explicitly **do not** treat Twanoh/Hoodsport/Dabob as Willapa. |
| **Depth** | `SURFACE_0_5` |
| **Ladder** | `EXISTING_SENSORS` / public IOOS with **UNKNOWN** commercial rights until review |
| **EUR 0.45 · EcoImp 0.55 · ConsPri 0.10 · DecVal 0.50 · FcstDis 0.40 · Feas 0.70 · CostEff 0.75 · Harm 0.00 · Legal 0.08** | |
| **Why last of the eight** | Real supporting covariate, but **not** the 2021 primary mechanism and **not** the label. Still beats new SST and beats a glider. |
| **Fallback** | Partner bucket thermometer logged on the form (weak, still local) |
| **EMIV** | `EMIV-PHY-WTEMP-001`, `EMIV-PHY-SALIN-001` |
| **privacy_tier** | `COARSENED` / public stations; farm sondes `PRIVATE` |

\(0.460 - 0.08 = 0.380\).

---

## 5. Explicitly not ranked (killed or low)

| ID | Action | Result |
|---|---|---|
| W1-FIX-K01 | Sample WA DOH closure / biotoxin stations to train ops-stress | **`KILL_WRONG_TARGET` + `KILL_NSSP_IMPERSONATION`**. Show DOH as authority link only |
| W1-FIX-K02 | Task a glider in the open Pacific for SST/T/S | **`KILL_HARDWARE_BEFORE_LADDER` + `KILL_WRONG_TARGET`**. EUR cap 0.20. Fixture OVS still **+0.037** — kill rules override a positive score |
| W1-FIX-K03 | Ingest more MUR/VIIRS SST as the primary W1 observation | Low OVS (`EUR≤0.20`); not killed if supporting, **killed if sold as body T / harvest** |
| W1-FIX-K04 | eDNA grid on leases for oyster “abundance” | Wrong state; stock is planted; rare-taxa GPS risk |
| W1-FIX-K05 | Hydrophone | Not an oyster ops modality |
| W1-FIX-K06 | Drone mosaic of beds as a public map | `KILL_PUBLIC_SPOT` / farm privacy |
| W1-FIX-K07 | New bag loggers **before** asking whether HOBO files exist | `KILL_HARDWARE_BEFORE_LADDER` |

---

## 6. Top 5 actions (parent return)

1. **W1-FIX-R01** — 30 s partner outcome form (OVS 0.658) — PRIVATE  
2. **W1-FIX-R02** — Public air × tide × solar pairing (0.613) — physics PUBLIC  
3. **W1-FIX-R03** — Culture / elevation / ploidy metadata (0.573) — PRIVATE  
4. **W1-FIX-R04** — Existing bag/bed thermistor export (0.566) — PRIVATE  
5. **W1-FIX-R05** — 14-day paper protocol if export fails (0.529) — PRIVATE  

Human approval required before any partner is asked. This file is not outreach.

---

## 7. What would change the ranking

- If partners **already** have dense bag T and complete mortality sheets: R01/R04 EUR drops; R02 still needed for **lead time**; do not buy gliders.  
- If culture is **all subtidal floats**: drop emersion-heat EUR; raise DO/water T; still not DOH GT.  
- If founder locks South Sound instead of Willapa: **swap named water-body and station cluster**; do not keep Hood Canal ORCA as a silent default.

---

## 8. Machine table

See `fixture_recommendations.csv` (FIXTURE rows, including killed examples for audit).
