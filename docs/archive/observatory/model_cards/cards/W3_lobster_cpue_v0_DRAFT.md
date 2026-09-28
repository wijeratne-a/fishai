# Species Model Card — W3 American lobster next-trip CPUE (DRAFT)

**card_id:** `SMC-W3-LOBSTER-CPUE-v0-DRAFT`  
**schema_version:** `SMC-SCHEMA-2026-09-18-v1`  
**as_of_date:** `2026-09-18`  
**card_status:** **NOT_PUBLISHED**  
**operational_status:** **NOT_OPERATIONAL**  
**claim_pack:** `claim_pack_W3_lobster_cpue_C_v0`  
**wedge_id:** `W3_lobster_gom_cpue_next_trip`  
**wedge_lock_status:** **UNRESOLVED**  
**factory_step:** 5 (CPUE-not-abundance architecture specified; AIS path **rejected**; nothing fitted)  
**observatory_output_class:** `HYPOTHETICAL/RESEARCH MODE`  
**capability_class:** 4 (next-trip legal CPUE requires partner haul-level effort + soak; public landings are the wrong grain)  
**interviews_completed:** **0**  
**observations_ingested:** **0**  
**evidence_tier_strongest_label:** `none`  
**supersedes_card_id:** `null`  
**red_team_blocker_ids:** `B-ALL-01`–`B-ALL-08`, `B-LOB-01`–`B-LOB-06`, `RT-LOB-01`, `RT-LOB-04`, `RT-LOB-10`, `RT-XCUT-01`, `RT-XCUT-11`  
**extrapolation_flag:** `true`

**Non-negotiables:** **catch ≠ abundance.** AIS / GFW / VMS / tracker pings are **banned** as abundance, as a public effort layer, and as the default training feature (`B-LOB-01`, `RT-LOB-01`, `RT-LOB-10`). Public CPUE heatmaps are a **BLOCKER**.

---

## 1. Species identity

| | |
|---|---|
| Common name | American lobster (Maine / northern / North Atlantic lobster as marketing names) |
| Accepted scientific name | *Homarus americanus* H. Milne Edwards, 1837 |
| WoRMS AphiaID | 156134 |
| LSID | `urn:lsid:marinespecies.org:taxname:156134` |
| Principal synonyms | None material. Authority punctuation H. Milne Edwards vs Milne Edwards only. |
| Common-name collisions | Spiny lobster (*Panulirus* spp.) — no large claws. European lobster = *Homarus gammarus*. Slipper/squat “lobsters” are not Nephropidae. |
| Population unit | Operator’s **own effort footprint** inside **one** NMFS statistical area (511 **or** 512 **or** 513) or one Maine zone. ASMFC **GOM/GBK vs SNE** are management stocks, not extra species. DFO LFA 34 is adjacent science, not this operator’s area. |

Registry: `OBS-TAX-005`. WoRMS / ITIS / NOAA: no material identity disagreement.

---

## 2. Taxonomic authority

- Authority: **WoRMS**
- URL: https://www.marinespecies.org/aphia.php?p=taxdetails&id=156134
- Access date: **2026-09-18**
- WoRMS status: accepted
- License status: **UNKNOWN** for bulk DB; webservice lookup catalogued `APPROVED_WITH_ATTRIBUTION`

---

## 3. Geographic scope

- Description: US inshore Gulf of Maine commercial trap fishery. Recommended scientific v1: **one** statistical area (512 or 513) or one Maine zone A–G — not the entire GOM/GBK stock. Eastern vs western Maine sublegal trends have diverged (DMR 2024).
- Bounding units: NMFS SA 511/512/513; Maine lobster zones; LCMA Area 1.
- Public grain: **none**. Operator-private brief only, or basin-scale so coarse a competitor cannot set on a cell — **not authorized**. Exact strings `NEVER_PUBLISH`.
- Founder-locked: **false**.

---

## 4. Depth scope

- Depth band: benthic trap depths in the operator’s footprint (VTS analogue 2–32 fathom in ME is **survey** grain, not this product’s census).
- Depth known: **false** (no partner depth/soak table ingested).
- Notes: **Bottom temperature** is the relevant thermal variable. Satellite SST is a **poor substitute** (ASMFC 2025 peer review). SST skin ≠ bottom T.

---

## 5. Life stage

- **In scope:** **legal-size** benthic juveniles/adults entering baited traps (legal recruits / post-molt pulse).
- **Out of scope:** eggs on females as a density target (protected; v-notch/eggers discarded — they affect **legal** CPUE); pelagic larvae; YOY settlement as next-trip truth; SNE hypoxia narrative copied into GOM.

---

## 6. Prediction target

- Name: next-trip **legal catch per defined effort**
- Definition: Expected **legal** catch per trap-haul (or documented alternative) for the next planned haul window, **rank** vs **this operator’s** comparable trips (season, soak band, zone). Category **C**. **This is catchability-influenced catch, not abundance.**
- Horizon: next trip / next soak haul (hours to a few days) — not a 10-year stock outlook
- Unit: tercile of the operator’s comparison set (not pounds as a calibrated guarantee)
- `label_id`: soak-adjusted legal CPUE (count or weight per trap-haul) — **zero rows**

---

## 7. Output category (A–E / visual truth state)

- Prediction-contract category: **C**
- Visual-truth state **today:** `UNKNOWN`
- Visual-truth if ever live: `OPERATIONAL_CATCH_OR_EFFORT` in **PRIVATE** UI only. Public choropleth forbidden. Not `SURVEY_INDEX` (VTS/NEFSC are seasonal context). Not AIS `REMOTE_DETECTION` titled as lobsters.

Not A (impossible at trip grain). Category E (SST/AIS/chl as lobsters) **rejected**. Category B survey indices are **inputs/context**, not the next-trip label.

---

## 8. Support tier T0–T6

- Factory eligibility tier: **T2** (registry `OBS-TAX-005`)
- Emitted tier: **T0**
- Evidence ceiling tier: **T2** for public observatory. Seasonal surveys do **not** make next-trip T3/T4. No T5 trap-sensor ingest. Commercial W3 is **not** T6.
- Notes: Do not upgrade because ASMFC 2025 exists. Assessment terminal year ≠ next haul.

---

## 9. Training data sources

| source_id | role | ingested | rights_class | notes |
|---|---|---|---|---|
| partner_haul_logbooks | label | **false** | `APPROVED_PARTNER_CONSENT` | Legal count, trap-hauls, soak, discards as agreed; n=0 |
| eMOLT_or_trap_bottom_T | feature | **false** | partner / `CONDITIONAL_REVIEW_REQUIRED` | Catchability covariate; positions coarsened |
| NERACOOS_GoMOFS | feature | **false** | `CONDITIONAL_REVIEW_REQUIRED` | Physics; not CPUE |
| ME_DMR_public_landings_tables | context / climatology research only | **false** | `APPROVED_OPEN_COMMERCIAL` aggregates | Monthly pounds **≠** next-trip CPUE |
| ME_DMR_LEEDS_harvester | forbidden without authorization | **false** | `RESTRICTED` (12 M.R.S. § 6173) | Confidential |
| NOAA_VTR_ACCSP | forbidden without authorization | **false** | `RESTRICTED` (MSA) | Confidential |
| GFW_AIS_VMS_AddendumXXIX | **forbidden** | **false** | NC / `RESTRICTED` / `NEVER_PUBLISH` | **Banned** as abundance/effort product |
| ASMFC_2025_assessment | context | **false** | cite; do not dump copyrighted PDF | Stock-scale, wrong horizon |
| Maine_VTS_sea_sampling | context (seasonal) | **false** | research requests; microdata restricted | Not next-trip legal CPUE |

**AIS is not in the feature set.** Provenance line if ever live: **no AIS**.

---

## 10. Data rights status

- Overall: **catalog only; ingest not authorized**. Public-data-only next-trip CPUE is scientifically inadequate and must **not** be backfilled with confidential government files.
- Human legal review: **REQUIRED**
- Ingest authorized: **false**
- Privacy default: strings, high-CPUE cells, tracker paths `NEVER_PUBLISH`; vessel identity `NEVER_PUBLISH`
- Notes: Highest legal risks — MSA + Maine confidentiality; competitor intelligence; antitrust-adjacent price sharing. Tracker 1-minute pings default **REJECTED** for training/maps (`RT-LOB-10`).

---

## 11. Observation count

- Ingested n: **0**
- Catalog metadata n: OBIS metadata **921007** (compiled occurrence, not legal CPUE, not ingested)
- Partner label n: **0**

Maine 100% e-reporting since 2023 is **real but not in this repo**, monthly lag, one 10-minute square per trip, confidential microdata.

---

## 12. Observation methods

**None ingested.** Specified: operator trap-haul logs (legal count, soak hours, bait, zone, discards). Survey methods (VTS 3-day soaks Jun–Aug; NEFSC trawl; settlement collectors; sea sampling) are **wrong timescale or wrong selectivity** for next-trip legal CPUE. AIS is **not** an observation of lobster.

---

## 13. Environmental variables

| name | role | mechanism_status | notes |
|---|---|---|---|
| Bottom temperature | primary catchability | causal for **activity/appetite/molt**, not N | McLeese & Wilder 1958 onward; ASMFC catchability covariates |
| Soak, bait, trap design, trap density | primary | causal for CPUE | If missing ⇒ Low confidence; landings without effort are not CPUE |
| Depth band | supporting | correlative / allocation | Seasonal inshore–offshore |
| Substrate / shelter | supporting static | correlative | Not a daily layer |
| Storms / wind | supporting | causal for haulability | Not navigation advice |
| Molt phenology prior | supporting | causal seasonal | Mills et al. 2017 is **weeks**, not hours |
| Satellite SST | not_used as lobster T | **wrong_variable** | Skin ≠ bottom |
| Chlorophyll / *Calanus* | not_used at trip horizon | recruitment lag (years) | Wrong timescale |
| Moon / tides | not_used v1 | unknown / weak published | Tier 4 until tested locally |
| AIS / GFW / VMS | **forbidden** | proxy of **vessels**, not animals | Coverage: 33 CFR 164.46 ≥65 ft; most inshore boats absent |
| Whale locations | forbidden | n/a | ALWTRP is a **mask**, not a map we emit |

---

## 14. Feature availability / latency

- As-of replay implemented: **false**
- `availability_at_prediction_time`: **specified_not_built**
- Notes: Last haul in the comparison set and bottom-T forecast age must be clocked. Public DMR tables are monthly — too slow for next-trip. Reporting-regime breaks (10% → optimized active → 100% in 2023) forbid a continuous unadjusted index (`B-LOB-05`, `RT-LOB-03`).

---

## 15. Model architecture

- Family: **expert_rule_plus_climatology** (specified) — B12 TMS×month climatology + B3 persistence + B4 without AIS
- Trained: **false**
- Description: Private rank on the partner’s **existing footprint** only (`B-LOB-06`). No “go here” waypoints. No neural net on AIS density. No public hotspot model. **Nothing fitted.** Condition on soak; do not call raw landings CPUE (`B-LOB-04`).

---

## 16. Baseline comparison

- Baselines specified: **true**
- Baselines fitted: **false**
- Relevant baseline id: `null` (likely **B3** last-soak persistence and/or **B12** square-month; beating B12 is the real test in GOM)
- Beats relevant baseline: **not_evaluated**
- Notes: Models that ignore vessel ID often lose to B3 (skill, soak habits). Post-2023 reporting era only unless a break-adjusted series is documented.

---

## 17. Validation approach

- Protocol id: `VAL-PROTOCOL-2026-09-18-v1` §4.3
- Time-forward / spatial holdout / prospective: **false** / **false** / **false**
- Status: **NOT_RUN**

Do not calibrate to dealer landings without trap-hauls. Do not use NEFSC trawl as inshore next-trip label. Do not use VTS sublegal CPUE as legal landings. Vessel-holdout required later.

---

## 18. Performance metrics

- Available: **false**
- Primary metric: `null` (specified: MAE on log1p soak-adj CPUE; rank vs B3/B12)
- Value: `null`
- Split: `null`

---

## 19. Calibration results

- Calibration plot accepted by human: **false**
- ECE / coverage: `null`
- Notes: High confidence **never** in v1 without prospective calibration. Missing soak/bottom T ⇒ Low. Do not print pounds ± fake.

---

## 20. Known biases

- Temperature-dependent **catchability** (central confounder of “CPUE = abundance”); hyperstability (Harley et al. 2001).
- Trap saturation (~24 h) and neighbor-gear competition.
- Highliner / latent-permit / zone-license selection; partner logs ≠ GOM stock.
- Legal selectivity (vents, gauge, v-notch, eggers): landings CPUE ignores most animals VTS was designed to see.
- Protocol breaks across 2008–2023 reporting regimes.
- Whale-safe gear rules change configuration (regulatory confounding ≠ animals left).

---

## 21. Known failure modes

- AIS hotspot as “where the lobsters are” (**BLOCKER**).
- Public CPUE/string maps (**BLOCKER**).
- CPUE-up sold as stock-up (HIGH).
- SST as habitat-now (HIGH).
- Soak-unnormalized landings as CPUE (HIGH).
- Recommending unfished cells (HIGH; presence-only, no true zeros).
- Restricted-area CPUE drop as emigration (MEDIUM; whale/gear closures).
- Importing SNE hypoxia / shell-disease into GOM.

---

## 22. Uncertainty method

- Method: rank terciles + listed catchability confounders; quantile interval only after prospective calibration
- Confidence labels allowed: **false** (no issuance)
- Numeric probabilities allowed: **false**

---

## 23. Geographic / seasonal / depth gaps

- No locked SA or zone.
- No bottom-T at trap depth in-repo.
- Offshore Area 3 / migrants out of inshore v1.
- Winter low-activity vs summer molt pulse are different processes.
- Settlement/*Calanus* explain **future** legal abundance (5–8 year lag), not tonight’s haul.
- Moon-phase unpublished as a local driver.

---

## 24. Sensitive-location rules

- Publish class: **PRIVATE**
- Never-publish: strings, high-CPUE cells, tracker paths, VMS/AIS identity, right-whale localizations (link official Slow Zones only, do not densify)
- Public max grain: none for CPUE. Rule-of-3+ if any multi-vessel aggregate is ever contemplated (not today)

---

## 25. Last retrained date

`null` — **never trained**.

---

## 26. Current model version

`W3_lobster_cpue_v0_SPEC`

---

## 27. Reviewer status

- Status: **REQUIRED_HUMAN_REVIEW**
- Human reviewer names: **[] (none named)**
- Red-team signoff: **false**
- Domain-reviewer signoff: **false**
- Review date: `null`

Required later: human lobster scientist **and** confidentiality reviewer (`deployment_blockers.md` §5).

---

## 28. Permitted user claims

Only `claim_pack_W3_lobster_cpue_C_v0`. Effort-normalized **legal** catch rank on **your** gear; catchability confounders visible; **not abundance**; **AIS not used**. **Not issuable today.**

---

## 29. Prohibited user claims

AIS hotspot = lobsters; CPUE-up = stock-up; cell-level abundance; public string/CPUE maps; guaranteed landings/price/haul; set on another operator’s gear; GFW screenshots; SST as bottom T or as N; soak-free landings as CPUE; “go 2 nm east.”

---

## 30. Recommended use cases

- Later **private** next-trip rank on one consenting operator’s strings, with soak + bottom T, no AIS, after DUA and named reviewers.
- Teaching example: **catch ≠ abundance**; temperature moves catchability.
- Globe: no lobster hotspot layer.

---

## 31. Not-recommended use cases

- Public GOM CPUE heatmap.
- AIS/GFW “effort = life” globe mode.
- Customer brief on 2026-09-18.
- Using FOSS/DMR monthly pounds as next-trip GT.
- Whale-finding byproduct.

---

## Approval block

| Role | Name | Date | Scope |
|---|---|---|---|
| Scientific red-team | *(NO-GO; not a human sign-off)* | 2026-09-18 | n/a |
| Domain reviewer | **none named** | | |
| Publisher | **none named** | | |
