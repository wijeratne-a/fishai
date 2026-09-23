# Scoring specification — Observation Value Score

**Status:** DESIGN HYPOTHESIS. Weights are locked for this design pass; **numeric 0–1 inputs are uncalibrated** until a human reviewer accepts a prospective calibration table.  
**Date:** 2026-09-18  
**No scores issued against real animals or real leases.** W1 numbers in `w1_willapa_oyster_plan.md` and `fixture_recommendations.csv` are **FIXTURE** illustrations.

---

## 1. Locked formula

\[
\begin{aligned}
\mathrm{OVS}
&= 0.25\,\mathrm{EUR}
+ 0.20\,\mathrm{EcoImp}
+ 0.15\,\mathrm{ConsPri}
+ 0.15\,\mathrm{DecVal} \\
&\quad + 0.10\,\mathrm{FcstDis}
+ 0.10\,\mathrm{Feas}
+ 0.05\,\mathrm{CostEff}
- \mathrm{HarmPen}
- \mathrm{LegalPen}
\end{aligned}
\]

| Symbol | Name | Range | Role |
|---|---|---|---|
| `EUR` | Expected Uncertainty Reduction | [0, 1] | How much this observation is expected to shrink **decision-relevant** uncertainty |
| `EcoImp` | Ecological Importance | [0, 1] | Importance of the **process / habitat / life-history moment** being constrained |
| `ConsPri` | Species / habitat conservation priority | [0, 1] | Listing, remnant habitat, aggregation vulnerability — **not** a licence to publish |
| `DecVal` | Decision Value | [0, 1] | Value to a named operator or scientific decision at the product horizon |
| `FcstDis` | Forecast Disagreement | [0, 1] | Disagreement among models, baselines, or sensors that this obs would adjudicate |
| `Feas` | Feasibility | [0, 1] | Can this be collected lawfully, on the ladder, in the next planning window |
| `CostEff` | Cost Efficiency | [0, 1] | Information per dollar/hour (order-of-magnitude; **ESTIMATE**) |
| `HarmPen` | Ecological Harm Penalty | [0, 1] | Subtracted |
| `LegalPen` | Legal / Privacy Penalty | [0, 1] | Subtracted |

**OVS is not a probability, not abundance, and not a public heatmap value.** It is an internal ranking statistic for **human-gated** collection design.

After penalties, OVS may be negative. Negative OVS ⇒ do not recommend (even if kill rules did not fire). Rank only `kill_flag = false` and `OVS > 0`.

---

## 2. Input definitions (0–1)

All inputs are **hypotheses**. Do not print three-decimal biological probabilities in customer briefs (`prediction_contract.md`). Internal planner scores may use three decimals for audit.

### 2.1 Expected Uncertainty Reduction (`EUR`)

Expected reduction in **the uncertainty that actually changes the issuance** (missing critical inputs, unidentifiable \(H\), label gap), not reduction in a pretty posterior volume.

| Score | Meaning |
|---:|---|
| 0.00 | Observation is independent of the state we issue (wrong variable, wrong horizon, wrong basin) |
| 0.20 | Marginal covariate already well observed (e.g. another SST pixel for W1) |
| 0.50 | Fills a supporting gap (e.g. Willapa in-situ water T when only NWP exists) |
| 0.80 | Closes a **critical** missing input named in the uncertainty policy |
| 1.00 | Hypothetical perfect observation of the **label itself** at the decision grain (almost never assigned) |

**W1 critical EUR drivers (hypothesis):** partner `ops_disruption_72h` labels; culture method / tidal elevation; bag/body temperature during daytime emersion. SST-only: cap `EUR ≤ 0.20`.

**IMPLEMENTABLE_NOW proxy** (not full VOI):

\[
\widehat{\mathrm{EUR}} = \mathrm{clip}_{[0,1]}\big( w_c \cdot \mathbf{1}_{\text{closes critical missing}} + w_l \cdot \mathbf{1}_{\text{is label}} + w_d \cdot \Delta \mathrm{disagreement} \big)
\]

with starting weights \(w_c=0.45,\; w_l=0.40,\; w_d=0.15\) (hypothesis). Full Bayesian VOI is `REQUIRES_RESEARCH_BREAKTHROUGH` globally (`information_gain_methods.md`).

### 2.2 Ecological Importance (`EcoImp`)

Importance of reducing uncertainty in **this ecological or operational process**, not IUCN category (that is `ConsPri`).

| Score | Meaning |
|---:|---|
| 0.00 | Decorrelated from any observatory process |
| 0.30 | Local husbandry detail with weak twin meaning |
| 0.50 | Standard habitat covariate |
| 0.70 | First-order process at the product horizon (W1: air × emersion heat) |
| 1.00 | Keystone / basin-scale process under active scientific or management question |

Farmed Pacific oyster on a lease still scores **medium–high EcoImp** when the process is intertidal heat-kill physics (2021 analogue). It does **not** score high `ConsPri`.

### 2.3 Conservation Priority (`ConsPri`)

Trigger for **care and concealment**, not a targeting bonus.

| Score | Meaning |
|---:|---|
| 0.00–0.20 | Widespread LC / farmed non-native stock, no aggregation overlay |
| 0.21–0.49 | Habitat of conservation interest; mixed native/non-native beds |
| 0.50–0.74 | Listed, depleted, or aggregation-forming taxa/habitats |
| 0.75–1.00 | Cat-1 GBIF / ESA / MMPA / CITES App I / remnant beds |

**High `ConsPri` raises `HarmPen` / `LegalPen` and may fire kill rules.** It must **not** be used to send the public to the animal. For W1 *M. gigas* grow-out, default `ConsPri ≈ 0.10–0.20`. If a rec would mix *Ostrea lurida* native beds or unpublished remnant habitat, raise `ConsPri` **and** apply kill/coarsen.

### 2.4 Decision Value (`DecVal`)

Value to the **named decision** in the prediction contract.

| Score | Meaning |
|---:|---|
| 0.00 | No operator or scientific decision uses this |
| 0.25 | Context only (nice to have) |
| 0.50 | Improves a supporting covariate |
| 0.80 | Directly changes B4/B12/confidence or evaluation |
| 1.00 | Is the evaluation label or a required metadata field for \(H\) |

W1: farm workability / mortality-above-normal / intervention logs → high. WA DOH open/closed → **high for a harvest-legal product we are not building**; **low (`≤ 0.15`) for `ops_disruption_72h`**. Do not launder DOH into `DecVal` by calling it “disruption.”

### 2.5 Forecast Disagreement (`FcstDis`)

How much **admissible** sources disagree on the quantity this observation would measure.

| Score | Meaning |
|---:|---|
| 0.00 | Single source, no alternative, or disagreement is on a forbidden proxy |
| 0.40 | Mild spread (NWP members agree within operational noise) |
| 0.70 | Material spread (air vs bag T; B4 vs empty-label climatology; depth of 8–12 °C band) |
| 1.00 | Models/baselines contradict on the **action** (work this tide vs not) |

**Do not** manufacture disagreement from AIS vs CPUE or SST vs “fish.” Forbidden-proxy disagreement scores **0** and may kill.

### 2.6 Feasibility (`Feas`)

| Score | Meaning |
|---:|---|
| 0.00 | Illegal, impossible this window, or blocked by ladder |
| 0.30 | Requires new hardware or ungranted rights |
| 0.60 | Possible with partnership not yet signed |
| 0.85 | Partner can do this with existing tools in ≤14 days after DUA |
| 1.00 | Already-paid public pairing or already-running sensor, rights cleared |

**Hardware before ladder:** cap `Feas ≤ 0.25` and apply `KILL_HARDWARE_BEFORE_LADDER` unless stages 1–5 are documented complete.

### 2.7 Cost Efficiency (`CostEff`)

Order-of-magnitude **ESTIMATE**, not a quote (`observation_modality_catalog.md` cost labels).

| Score | Typical (ESTIMATE) |
|---:|---|
| 0.90–1.00 | 30-second form; public API pairing; copy of a spreadsheet they already have |
| 0.60–0.89 | Manual 14-day protocol; export existing HOBO |
| 0.30–0.59 | Extra site visit; lab qPCR on opportunistic water |
| 0.00–0.29 | Dedicated ship-day, new glider, new drone program |

If dollar cost is `UNKNOWN`, set `CostEff` from ladder position and mark `cost_band=UNKNOWN` — do not invent USD.

---

## 3. Penalty ranges (subtracted)

Penalties are **not** “negative importance.” They encode harm and legal/privacy residual **after** coarsening.

### 3.1 Ecological Harm Penalty (`HarmPen`) ∈ [0, 1]

| Band | Range | Examples | Planner action |
|---|---|---|---|
| None / negligible | 0.00–0.09 | Private form about own farmed stock; public tide table | Score normally |
| Residual | 0.10–0.29 | Extra handling of heat-stressed bags to place a logger; low-altitude farm drone with partner consent | Score; require harm_review |
| Moderate | 0.30–0.49 | Repeated disturbance near pinniped haul-out (even if coarsened rec); new lights/bait in sensitive habitat | Score only if partner-ACL and review PASS; never public |
| **High — KILL** | **≥ 0.50** | Targeting spawn aggregations, nests, listed holding waters, remnant invertebrate beds, live whale localization | **`kill_flag=true` — do not recommend** |

### 3.2 Legal / Privacy Penalty (`LegalPen`) ∈ [0, 1]

| Band | Range | Examples | Planner action |
|---|---|---|---|
| Routine private | 0.00–0.19 | DUA collection of farm outcomes; coarsened H3 res 5–6 rec | Score; `privacy_tier=PRIVATE` or `COARSENED` |
| Sensitive ACL | 0.20–0.49 | Lease performance, vessel identity internally, unpublished PI sites | Partner ACL only; no public derivative |
| **High — KILL** | **≥ 0.50** | `NEVER_PUBLISH` class targeting; NSSP impersonation; MSA confidential microdata; hidden iNat; TEK without nation protocol; public farm KPI map | **`kill_flag=true` — do not recommend** |

**Mosaic rule:** if `HarmPen + LegalPen ≥ 0.70` and either is ≥ 0.30, treat as kill (reverse-engineering / combination risk).

---

## 4. Kill rules (override OVS)

If any kill fires, **do not recommend**, even if OVS would be the daily maximum. Record the rec in the audit table with `kill_flag=true` so the miss is visible.

| Code | Condition | Rationale |
|---|---|---|
| `KILL_HARM_HIGH` | `HarmPen ≥ 0.50` | Policy harm classes |
| `KILL_LEGAL_HIGH` | `LegalPen ≥ 0.50` | Privacy / statute / contract |
| `KILL_MOSAIC` | `HarmPen + LegalPen ≥ 0.70` and min(·) ≥ 0.30 | Combination recovers a forbidden site |
| `KILL_NEVER_PUBLISH` | Target is a §6 `NEVER_PUBLISH` class at native or targeting grain | Nests, aggregations, haul-outs, PAM bearings, rare eDNA GPS, lease corners, farm KPIs **as public recs** |
| `KILL_PUBLIC_SPOT` | Recommendation would ship a public biological pin / heatmap / “go here” | Global public animal map rejected |
| `KILL_WRONG_TARGET` | Observation labels the **wrong decision** (W1: DOH/NSSP as `ops_disruption_72h`; AIS as abundance; SST as body T sold as kill law) | Red team / GT relabel |
| `KILL_NSSP_IMPERSONATION` | Sampling or copy that a reasonable operator would read as harvest/food-safety authorization | WAC 246-282-006; prediction contract |
| `KILL_AIS_ABUNDANCE` | Uses vessel density as animals | Contract §0 |
| `KILL_HARDWARE_BEFORE_LADDER` | New capital sensor/platform while public→partner→existing→manual→mobile→integration is incomplete | Acquisition plan |
| `KILL_UNREVIEWED_PUBLIC_BIO` | Public biological layer without ecological-harm review | Policy §4 |
| `KILL_LISTED_HOLDING` | Fine geography of listed-species holding waters, mouths at spawn, natal pools | ESA / policy |
| `KILL_SPAWN_AGG` | Coordinates, depth, or moon-timed chorus of spawning aggregations | IUU intelligence |
| `KILL_CLOSED_UNIVERSE` | Chinook rec inside closed management area; unstocked farm; lobster restricted configuration | Uncertainty suppression |
| `KILL_NO_HUMAN_GATE` | Auto-tasking vessels/drones/samplers without named human approval | Architecture |

**Partner-private collection of farm KPIs is allowed under DUA** (`privacy_tier=PRIVATE`). **Recommending that those KPIs be published or used as a public ranking is `KILL_NEVER_PUBLISH`.**

---

## 5. Absent vs not detected vs no observations

Never collapse these. Persist planner key `EMIV-DET-TRI-001` (no registry row; related quality EMIVs: `EMIV-QUA-PDETECT-001`, `EMIV-QUA-SEFFORT-001`).

| Code | Meaning | What the twin may say | What it must not say |
|---|---|---|---|
| `SPECIES_ABSENT` | Design-based or operator-certain **absence**: farm unstocked; survey with modeled \(p_{\mathrm{detect}}\) high enough that non-detection supports absence **under stated assumptions**; official “no gear in water” | “Stocked = false” / “absence assumed given p_detect model vX” | “The bay has no oysters” from one empty grab |
| `NOT_DETECTED` | Effort occurred; the modality’s detection function did not fire | “Not detected; \(p_{\mathrm{detect}}\) = …” | Absence of the organism |
| `NO_OBSERVATIONS` | No effort, no sensor, no log in the cell×depth×window | `UNKNOWN/INSUFFICIENT DATA` | Empty = zero animals; unfished Chinook cell = no fish |

**Rules:**

1. `NO_OBSERVATIONS` is the default.  
2. eDNA non-detect is `NOT_DETECTED` until a transport + decay + shedding model is locally calibrated — still not `SPECIES_ABSENT`.  
3. PAM silence is `NOT_DETECTED` for vocal taxa (calling rate unknown).  
4. CPUE zero is `NOT_DETECTED` / catchability-confounded, **never** abundance zero.  
5. Public products must hatch `NO_OBSERVATIONS` rather than interpolate a smooth “empty ocean” (`prediction_contract.md` §6).

Occupancy notation (MacKenzie et al. 2002): observed \(y=0\) may be unoccupied (\(1-\psi\)) or occupied but missed (\(\psi(1-p)\)). The planner’s job is to buy observations that **separate** \(\psi\) and \(p\), not to paint zeros as truth.

---

## 6. Calibration hypotheses (lock after first retro; do not neural-net)

1. Weights in §1 stay fixed until a named human changes them in writing.  
2. `EUR` proxy in §2.1 is replaced by empirical drop in Brier / MAE / confidence-upgrade rate once labels exist.  
3. If >50% of non-killed recs score `OVS > 0.70`, the 0–1 inputs are compressed — rescale, do not add a second model.  
4. `ConsPri` must correlate with harm-review strictness, not with public rank.  
5. W1 fixture scores in this folder are **not** a calibration plot.

---

## 7. Worked numeric example (FIXTURE)

**Candidate:** W1-R1 — permissioned 30-second farm outcome form (`worked_lease`, `workability`, `handling_done`, `mortality_above_normal` / intervention flags) on **named Willapa Bay growing waters**, `privacy_tier=PRIVATE`.  
**Not:** a public pin; not DOH tissue sampling; not a new sensor.

| Input | Value | One-line reason |
|---|---:|---|
| EUR | 0.92 | Closes the **label gap**; public physics cannot manufacture `ops_disruption_72h` |
| EcoImp | 0.70 | Constrains the 2021-class heat × emersion / workability process |
| ConsPri | 0.15 | Farmed *M. gigas*; not a listed-wild targeting layer |
| DecVal | 0.95 | Is the evaluation label and B5 workflow input |
| FcstDis | 0.85 | B4 expert rule vs empty-label world; model–reality disagreement is the point |
| Feas | 0.90 | Spec already exists (`outcome_capture_spec.md`); no hardware |
| CostEff | 0.95 | ~30 s; ESTIMATE highest information-per-dollar on this slice |
| HarmPen | 0.02 | Logging own stock; no extra field disturbance |
| LegalPen | 0.08 | KPIs are PRIVATE; DUA collection is the design, not publication |

Weighted sum:

\[
\begin{aligned}
&0.25(0.92)+0.20(0.70)+0.15(0.15)+0.15(0.95)\\
&+0.10(0.85)+0.10(0.90)+0.05(0.95)\\
&=0.230+0.140+0.0225+0.1425+0.085+0.090+0.0475=0.7575
\end{aligned}
\]

Penalties: \(0.02+0.08=0.10\).

\[
\mathrm{OVS}=0.7575-0.10=\mathbf{0.658}
\]

Kill checks: harm 0.02 < 0.50; legal 0.08 < 0.50; mosaic 0.10 < 0.70; not `NEVER_PUBLISH` as a **public** rec; not NSSP; ladder stage = partner export / manual structured. **`kill_flag=false`.**

**Contrast (killed, not recommended):** “Sample WA DOH closure stations to train ops-stress.” `DecVal` for the **ops** model ≤ 0.15; `KILL_WRONG_TARGET` + `KILL_NSSP_IMPERSONATION`. OVS is irrelevant.

**Contrast (low, not in top 8):** “Task a glider in the open Pacific for more SST.” `EUR≤0.20`, `DecVal≤0.10`, `Feas` capped, `KILL_HARDWARE_BEFORE_LADDER` and wrong grain.

---

## 8. Ranking procedure

1. Generate candidates from uncertainty tiles × EMIV coverage gaps × ladder-legal modalities (`architecture.md`).  
2. Score §1.  
3. Apply kill rules.  
4. Drop `OVS ≤ 0`.  
5. Coarsen geography to H3 res 5–6 or named water-body / official unit.  
6. Human approval list (max N per cycle; W1 fixture N=8).  
7. **Stop.** Do not auto-email a skipper or a drone vendor.

---

## 9. EMIV bindings (registry `v0.1-draft`)

| Field | ID | Registry? |
|---|---|---|
| W1 ops label | `EMIV-ECO-OPSOUT-001` | yes (**W1_CORE**) |
| p_detect | `EMIV-QUA-PDETECT-001` | yes |
| OVS | `EMIV-UNC-OVS-001` | unresolved (planner score) |
| EUR | `EMIV-UNC-EUR-001` | unresolved (planner score) |
| Ternary detection | `EMIV-DET-TRI-001` | unresolved (product enum) |
| Occupancy ψ | `EMIV-DET-OCC-001` | unresolved (model parameter; not `EMIV-BIO-EDNA-001`) |
| Harm penalty | `EMIV-POL-HARM-001` | unresolved (policy score) |
| Legal/privacy penalty | `EMIV-POL-PRIV-001` | unresolved (policy score) |

Canonical catalog: [`../emiv/emiv_registry.csv`](../emiv/emiv_registry.csv). Crosswalk: [`../emiv/engine_id_crosswalk.md`](../emiv/engine_id_crosswalk.md).
