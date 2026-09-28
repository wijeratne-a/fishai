# Deployment Blockers

**Agent:** SCIENTIFIC_RED_TEAM_AGENT  
**Date:** 2026-09-18  
**Rule:** No model, score, map, or brief may go customer-facing until every **BLOCKER** is cleared and every **HIGH** is resolved, explicitly bounded with visible limitation language, or accepted in writing by a qualified **human domain reviewer**. This agent is **not** that reviewer.

**Current global status:** **NO-GO** for all three wedges. No model has been trained; validation is vacuously failed (RT-XCUT-01).

---

## 0. Blockers that apply to every wedge

| ID | Blocker | Why it is blocking now | Clearance evidence required |
|---|---|---|---|
| B-ALL-01 | No spatiotemporal validation artifact exists | Cannot claim skill; random-split ocean models lie | Written protocol + first time-forward / spatial-block / out-of-year design approved by validation agent **and** human reviewer |
| B-ALL-02 | No as-of feature snapshot / replay | Temporal leakage is the default | `availability_at_prediction_time` for every feature; frozen issuance snapshots |
| B-ALL-03 | No baseline beaten prospectively | Seasonal×spatial average and persistence will likely win | Documented baselines; prospective log showing lift **or** product labeled as climatology/persistence, not “AI forecast” |
| B-ALL-04 | No prediction contract in the UI path | Users will upgrade Category D → abundance/legal/guarantee | Ship `prediction_contract.md` fields 1–14 on every output |
| B-ALL-05 | No human domain reviewer named | Agents cannot accept residual HIGH risk | Named human, credentials, date, scope, which IDs accepted |
| B-ALL-06 | Public fine-scale biological maps | False precision + location leakage | Public products coarse; exact spots NEVER_PUBLISH |
| B-ALL-07 | Rights not approved for training data | Unlawful/confidential layers (AIS tracks, farm yields, logbooks) | Data-rights class ≠ REJECTED/UNKNOWN/RESEARCH_ONLY for any training feature |
| B-ALL-08 | Wedge still UNRESOLVED | Cannot mix labels across oyster/Chinook/lobster | Founder lock of one species × geography × customer × decision |

Until B-ALL-01…05 and B-ALL-08 are cleared, **do not train** a production model and **do not** send a customer brief that contains a numeric score.

---

## 1. Oyster × WA × 72h — blockers

| ID | Blocker | Linked risks | Clearance |
|---|---|---|---|
| B-OYS-01 | Food-safety / harvest-legality wall not implemented as a **hard product constraint** | RT-OYS-01, RT-OYS-04, RT-OYS-08 | Separate UI modules: (A) ops-stress indicator, (B) official DOH/NSSP status with authority, timestamp, URL, boundary, last-verified. **No combined score.** Ban words in §3. No “harvest window” model output. |
| B-OYS-02 | Intention to use closures / Vp triggers as labels | RT-OYS-04 | Labels = partner mortality/workability/gear/sensors only. Closures = context. Written label dictionary signed by domain reviewer. |
| B-OYS-03 | SST-only (or SST+chl) thermal specification | RT-OYS-02 | Feature spec includes air temperature, tide/emersion, solar geometry, wind; SST labeled Tier 3 covariate not “oyster temperature.” Culture-type stratum required. |
| B-OYS-04 | No partner farm outcome stream | RT-OYS-10, XCUT-01 | At least one DUA with protocol for mortality/workability; n sufficient for blocked CV (human reviewer sets n_min). |
| B-OYS-05 | Public lease-level stress map | RT-OYS-05, XCUT-11 | Private-by-default; public only coarsened growing-area **environmental** context without farm performance. |

**Would still not be enough:** beating a baseline on water temperature. That is not oyster stress.

---

## 2. Chinook × CA/OR × 24–48h — blockers

| ID | Blocker | Linked risks | Clearance |
|---|---|---|---|
| B-CHK-01 | Habitat-style 24–48h encounter model | RT-CHK-01, RT-CHK-11 | **Do not deploy.** Only allowed experiment: rank vs comparable open-season days from partner logs, or an explicitly labeled seasonal climatology. Human salmon biologist must agree the target is identifiable. |
| B-CHK-02 | Any abundance or catch-guarantee language / heatmap | RT-CHK-02, XCUT-09 | Contract language live; rank bands not probabilities of “catching fish”; no “limits tomorrow.” |
| B-CHK-03 | Scoring closed or about-to-close cells | RT-CHK-09 | Regulation mask from NMFS/CDFW/ODFW in-season sources; closed ⇒ **no prediction**. |
| B-CHK-04 | Public fine-scale spot map | RT-CHK-03, RT-CHK-06 | ≥ PFMC subarea or ≥10 km, and still reviewed for ESA effort-concentration. Default: **no public map**. |
| B-CHK-05 | No trip-level partner labels | RT-CHK-04 | DUA with effort (angler-hours), retained, released, area coarsened; social/AIS not labels. |
| B-CHK-06 | ESA / stock-mix review absent | RT-CHK-03 | Human reviewer documents that the product does not target or advertise listed-stock aggregations. |

**Would still not be enough:** a high AUROC on month×port. That is a calendar model.

---

## 3. Lobster × GOM × CPUE — blockers

| ID | Blocker | Linked risks | Clearance |
|---|---|---|---|
| B-LOB-01 | AIS/GFW/VMS/Addendum XXIX tracks as abundance or public effort layer | RT-LOB-01, RT-LOB-10 | **Forbidden** as abundance. Tracker/AIS training requires documented legal basis + HUMAN LEGAL REVIEW. Default: do not ingest. |
| B-LOB-02 | Public CPUE/hotspot map | RT-LOB-04 | Operator-private brief only, **or** basin-scale rank so coarse a competitor cannot set on a cell. Human confidentiality review. |
| B-LOB-03 | Copy that treats CPUE as abundance | RT-LOB-02 | Category C language only; catchability confounders (bottom T, soak, bait, molt, gauge) listed as missing if absent. |
| B-LOB-04 | Effort undefined (landings without trap-hauls/soak) | RT-LOB-07 | Effort dictionary: legal lobsters per trap-haul (or documented alternative). No raw landings-as-CPUE. |
| B-LOB-05 | Training across 2008–2023 reporting regimes as one index | RT-LOB-03 | Split or explicitly model protocol change; do not claim a continuous standardized index without it. |
| B-LOB-06 | Recommending unfished cells | RT-LOB-05 | Condition on the partner’s existing footprint; no “go here” waypoints. |

---

## 4. What is *not* a clearance

- Another agent rewriting the claim more softly without changing labels, maps, or UI.
- A disclaimer below a red/green map (disclaimers do not cancel a heatmap).
- Internal notebook metrics on a random split.
- “Partner is excited.”
- Investor language about an “ocean abundance platform.”

---

## 5. Minimum path to a **bounded** research pilot (still not customer-facing production)

Only after B-ALL-01–05, B-ALL-08, and the wedge-specific blockers:

1. **Oyster (preferred scientific pilot):** one consenting farm; private 72h ops-stress **indicator**; DOH module separate; air+tide+wave; human shellfish + NSSP reviewers.
2. **Lobster (conditional):** one consenting operator; private next-trip CPUE **rank** on own strings; no AIS; human lobster + confidentiality reviewers.
3. **Chinook (last):** one consenting charter; private CPUE **rank** vs climatology; no public map; human salmon + ESA reviewers.

Any of these pilots must still print the 14-field contract and collect outcomes. **Shipping the pilot to paying customers** additionally requires prospective lift vs baseline or an explicit “climatology product” label.

---

## 5b. Sibling-spec blockers (do not ship these as written)

| ID | Artifact | Block until |
|---|---|---|
| B-SIB-01 | Quality B4 SST ≥ 19 °C / Hobday MHW as oyster expert rule | Rewrite B4: air × daytime emersion primary; water T/DO secondary and basin-specific; no 19 °C default |
| B-SIB-02 | Product sample brief (Totten, top 20%, +1.8 °C water first) | Replace sample with contract language; non-Category-3 demo area; terciles; air×tide first |
| B-SIB-03 | Requirements “safely work”; Quality B5 “harvest plans” | Strike “safely” and “harvest” from ops metrics |
| B-SIB-04 | Chinook v0 SST/chl + 10 km / H3-6 product map | No Chinook map; no SST/chl as encounter v0; PFMC-area climatology only |

These do **not** clear B-ALL-* or wedge blockers.

---

## 6. Stop-ship triggers after a pilot starts

- Any user or sales person describes the product as food-safe, legal harvest, abundance, or catch guarantee.
- A closed salmon cell is scored.
- A lobster or charter map is shared beyond the data owner.
- Evaluation is found to have used future or revised fields.
- Official DOH/NMFS/ODFW/CDFW/DMR status is stale and not marked stale.

On any trigger: halt distribution, document in the risk register, require human re-approval.
