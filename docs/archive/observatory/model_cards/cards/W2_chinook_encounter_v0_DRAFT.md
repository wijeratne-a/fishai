# Species Model Card — W2 Chinook 24–48h encounter (DRAFT)

**card_id:** `SMC-W2-CHINOOK-ENCOUNTER-v0-DRAFT`  
**schema_version:** `SMC-SCHEMA-2026-09-18-v1`  
**as_of_date:** `2026-09-18`  
**card_status:** **NOT_PUBLISHED**  
**operational_status:** **NOT_OPERATIONAL**  
**claim_pack:** `claim_pack_W2_chinook_encounter_C_v0`  
**wedge_id:** `W2_chinook_caor_encounter_24_48h`  
**wedge_lock_status:** **UNRESOLVED**  
**factory_step:** 4 (eligibility recorded; 24–48h habitat model **rejected**; partner-log rank specified, not built)  
**observatory_output_class:** `HYPOTHETICAL/RESEARCH MODE`  
**capability_class:** 5 at 24–48h from environment (plausible but **unproven** / not identified); 4 for an operational partner-log product (needs new label infrastructure)  
**interviews_completed:** **0**  
**observations_ingested:** **0**  
**evidence_tier_strongest_label:** `none`  
**supersedes_card_id:** `null`  
**red_team_blocker_ids:** `B-ALL-01`–`B-ALL-08`, `B-CHK-01`–`B-CHK-06`, `RT-CHK-01`, `RT-CHK-02`, `RT-CHK-03`, `RT-CHK-09`, `RT-SIB-04`, `RT-XCUT-01`, `RT-XCUT-11`  
**extrapolation_flag:** `true`

**Identifiability (read this first).** Environmental fields **do not identify** 24–48h ocean Chinook encounter. That finding is red-team **BLOCKER** `RT-CHK-01` / `B-CHK-01` for **habitat-style / SST-chl SDMs**. The 24–48h *clock* is **not** an extra independent blocker if — and only if — the target is a **partner-log Category C rank vs comparable open-season days** (or an explicitly labeled seasonal climatology) with a closed-area hard mask. That allowed experiment has **0 logs**, is **NOT_PUBLISHED**, and is **NOT_OPERATIONAL**. Public 24–48h encounter heatmaps remain the least defensible product.

---

## 1. Species identity

| | |
|---|---|
| Common name | Chinook salmon (king; CA/OR sport). Also spring, tyee, quinnat; **blackmouth** is typically Puget Sound usage, not this wedge. |
| Accepted scientific name | *Oncorhynchus tshawytscha* (Walbaum, 1792) |
| WoRMS AphiaID | 158075 |
| LSID | `urn:lsid:marinespecies.org:taxname:158075` |
| Principal synonyms | *Salmo tshawytscha* Walbaum, 1792. NCBI spelling *O. tschawytscha* is not a second species. |
| Common-name collisions | Silver/coho = *O. kisutch* (CA ocean coho retention prohibited). Steelhead = *O. mykiss*. CRFS/ORBS “salmon” mixes Chinook+coho. |
| Population unit | **Mixed ocean stocks** in a named PFMC/CDFW/ODFW **management area**. Not a single ESU. Listed units (e.g. Sacramento winter-run, California Coastal) **must not** be mapped at capture resolution. |

Registry: `OBS-TAX-002`. WoRMS / ITIS / NOAA: no material name disagreement.

---

## 2. Taxonomic authority

- Authority: **WoRMS**
- URL: https://www.marinespecies.org/aphia.php?p=taxdetails&id=158075
- Access date: **2026-09-18**
- WoRMS status: accepted
- License status: **UNKNOWN** for bulk DB; webservice lookup catalogued `APPROVED_WITH_ATTRIBUTION`
- Notes: Record Walbaum vs “Walbaum in Artedi” authority-string difference only.

---

## 3. Geographic scope

- Description: Bounded CA/OR **ocean** recreational Chinook, **south of Cape Falcon** as a scientific suggestion — **one** PFMC recreational management area or one ODFW catch area (e.g. Newport **or** San Francisco area). Do not mix CA KMZ with Monterey without a stock-mix model. Biological range (Monterey area to Chukchi) is **context only**.
- Bounding units: PFMC/CDFW ocean salmon management areas; ODFW ocean catch areas; in-season harvest guidelines.
- Public grain: **no public map**. If ever reviewed: ≥ PFMC subarea, still ESA effort-concentration reviewed. Default: **no public map** (`B-CHK-04`).
- Founder-locked: **false**.

---

## 4. Depth scope

- Depth band: continental-shelf **water column**; adults occupy ~**8–12 °C** by changing **depth** when the surface warms (Hinke et al. 2004, 2005). Surface SST is a proxy, often the **wrong vertical cell**.
- Depth known: **false** (no subsurface field + no tags ingested).
- Notes: Surface “hotspot” maps can point captains to empty warm water while fish are deeper.

---

## 5. Life stage

- **In scope:** legal-size **ocean-phase** immature and maturing Chinook (charter troll/mooch).
- **Out of scope:** freshwater egg–fry–smolt; estuary entry; **JSOES / juvenile** surface-trawl stage (wrong stage and mostly wrong geography); river spawning aggregations (often closed; listed-stock risk).

---

## 6. Prediction target

- Name: 24–48h relative **effort-normalized encounter rank**
- Definition: Rank of expected CPUE vs comparable **open-season** days in this **named management area** (same month / weather-workability bin if used). Category **C** preferred. **Not** occurrence. **Not** abundance. **Not** a 48h habitat census.
- Horizon: **24–48 hours, only if the area is open.** Closed or unverified ⇒ output **None** (no score).
- Unit: lower / middle / upper tercile of the **stated comparison set**
- `label_id`: `encounter_48h` (trip-level catch/no-catch + effort; **zero rows**)

---

## 7. Output category (A–E / visual truth state)

- Prediction-contract category: **C** (preferred); **D** only as explicit relative risk, never sold as C/A
- Visual-truth state **today:** `UNKNOWN`
- Visual-truth if ever live and **private**: `OPERATIONAL_CATCH_OR_EFFORT` (rank) or `FORECAST` of that rank — **PRIVATE** default. Not `HABITAT_SUITABILITY` as “fish are here.” Not purple occurrence.

Not A/B. Category E (raw SST/chl/AIS) is **rejected**.

---

## 8. Support tier T0–T6

- Factory eligibility tier: **T2** (literature habitat envelope; registry `OBS-TAX-002`)
- Emitted tier: **T0**
- Evidence ceiling tier: **T2** public. T3/T4 **not assigned**. A stock-assessment PDF does not upgrade Chinook to T3. Archival tags in literature are **not ingested** (no T5).
- Notes: Commercial W2 research ≠ an observatory current-condition model.

---

## 9. Training data sources

| source_id | role | ingested | rights_class | notes |
|---|---|---|---|---|
| partner_charter_trip_logs | label | **false** | `APPROVED_PARTNER_CONSENT` | Effort hours, retained, released, coarsened area; n=0 |
| NMFS_CDFW_ODFW_in_season_regs | context / hard mask | **false** | `APPROVED_OPEN_COMMERCIAL` as **context** | Closed ⇒ no score |
| RecFIN_CRFS_ODFW_weekly | baseline_only (B12) | **false** | public estimates; CTE001 **excludes salmon** | **Not** a 24–48h label (`RT-CHK-04` HIGH) |
| SST_chl_currents | forbidden as v0 encounter features | **false** | env families catalogued separately | Habitat SDM **BLOCKER** |
| JSOES_NWFSC_stoplight | not_used | **false** | public | Wrong stage / year-scale |
| AIS_CPFV | forbidden | **false** | `RESTRICTED` / NC / paid | Traffic ≠ Chinook |
| social_limits_posts | forbidden | **false** | `REJECTED` | Tier 4 |
| ESA_critical_habitat_GIS | context constraint | **false** | `APPROVED_OPEN_COMMERCIAL` at **designated** grain | Not a targeting layer |

---

## 10. Data rights status

- Overall: **catalog only; ingest not authorized**
- Human legal review: **REQUIRED** (highest counsel-priority wedge: ESA + CA FGC § 8022)
- Ingest authorized: **false**
- Privacy default: exact drifts `PRIVATE` / `NEVER_PUBLISH`; listed-ESU fine occurrence `NEVER_PUBLISH`
- Notes: Operator may share **their** log copy under DPA; FishAI must not pull CDFW confidential CPFV copies. Treaty fisheries: CARE.

---

## 11. Observation count

- Ingested n: **0**
- Catalog metadata n: OBIS metadata **222473** (compiled, effort-biased, mixed stocks/stages; **not** 24–48h charter GT; **not ingested**)
- Partner label n: **0**

---

## 12. Observation methods

**None ingested.** Specified labels: partner charter trip (anglers, hours, retained, released, area coarsened). Public CRFS ~20–25% of days; CPFV logs historically **monthly**; RecFIN salmon often absent. Social/AIS **not** methods for labels. GSI/CWT exist for **stock mix**, not daily maps.

---

## 13. Environmental variables

| name | role | mechanism_status | notes |
|---|---|---|---|
| Open/closed + harvest-guideline mask | primary | causal for **feasibility** | First-order; not fish density |
| Wind/swell (trip feasibility) | supporting confounder | causal for **realized** encounters | Must not be sold as “fish are here”; not weather-safety advice |
| Season / run-timing prior | supporting | correlative | Calendar; climatology B12 |
| Thermal habitat ~8–12 °C **with depth** | research only | causal for **habitat use**, not 48h rank | Does **not** identify 24–48h encounter without subsurface skill + labels (`RT-SIB-04` HIGH) |
| Satellite SST / chlorophyll | forbidden as v0 encounter features | proxy / **wrong scale** | Shelton et al. 2021 seasonal/stock; Hassrick et al. juvenile |
| Forage fish | not_used (unobserved) | causal if observed | No lawful 48h public forage field |
| AIS | forbidden_as_label | proxy | Effort/crowding, not biomass |
| River-mouth concentration | not_used | mixed | Often illegal; listed-stock risk |

---

## 14. Feature availability / latency

- As-of replay implemented: **false**
- `availability_at_prediction_time`: **specified_not_built**
- Notes: 8-day chlorophyll composites include **future** days if mis-timestamped (`RT-XCUT-02`). Regulation last-verified is a **separate** clock. Public CPUA is lagged — cannot backfill 24–48h.

---

## 15. Model architecture

- Family: **climatology** (allowed experiment) or **none** (habitat SDM **not selected**)
- Trained: **false**
- Description: **Rejected:** 24–48h SDM from SST/chlorophyll/currents. **Specified only:** (1) rank vs comparable open-season partner-log days, or (2) explicitly labeled **seasonal-spatial climatology (B12)** — never marketed as “AI nowcast.” Expert-rule B4 may zero closed cells and optionally (research) a training-only SST band — **not customer-facing habitat**. No AIS term. **Nothing fitted.**

---

## 16. Baseline comparison

- Baselines specified: **true**
- Baselines fitted: **false**
- Relevant baseline id: `null` (would be **B12** month×port-complex; public CRFS/RecFIN is B12 at coarse grain, **zero product lift** if restated as 48h)
- Beats relevant baseline: **not_evaluated**
- Notes: A high AUROC on month×port is a **calendar model**, not clearance (`deployment_blockers.md`).

---

## 17. Validation approach

- Protocol id: `VAL-PROTOCOL-2026-09-18-v1` §4.2
- Time-forward / spatial holdout / prospective: **false** / **false** / **false**
- Status: **NOT_RUN**

Closed days are **excluded** (not zeros). Do not train commercial troll to predict charter. Do not train WA/OR June juveniles to predict CA August adults.

---

## 18. Performance metrics

- Available: **false**
- Primary metric: `null` (specified: PR-AUC / Brier vs B12; ranking on visited cells only)
- Value: `null`
- Split: `null`
- Notes: Bag-limit truncation and “limit early, go home” bias CPUE.

---

## 19. Calibration results

- Calibration plot accepted by human: **false**
- ECE / coverage: `null`
- Notes: Partner logs with effort ⇒ at most **Medium** in v1. SST/chl-only ⇒ **None**. No three-decimal “chance of limits.”

---

## 20. Known biases

- Effort confounding; weather-workability vs biology.
- Skipper skill, bait, crowding, secret spots.
- Reporting / missing zeros; weekend social reports.
- Mixed hatchery/wild; mark-selective rules north of Cape Falcon.
- Interannual run size dominates season length (2023–2024 CA closures vs 2026 guidelines).
- RecFIN/CRFS spatial effort bias.

---

## 21. Known failure modes

- **24–48h env identifiability failure (BLOCKER)** for habitat-style models.
- Catch ≠ abundance ≠ guarantee (BLOCKER for public wording).
- Stock-mix / ESA effort-concentration (BLOCKER for hotspot maps).
- Scoring closed cells (BLOCKER).
- Month×port climatology sold as 48h AI (HIGH).
- Chlorophyll = forage = adult bite (HIGH).
- Fine public spot maps (HIGH / location leakage).
- AIS as fish (HIGH).

---

## 22. Uncertainty method

- Method: rank bands + uncertainty policy; **None** if closed/unverified or env-only
- Confidence labels allowed: **false** (no issuance)
- Numeric probabilities allowed: **false**

---

## 23. Geographic / seasonal / depth gaps

- No locked port or PFMC area.
- No subsurface thermal field at issuance.
- Prey unobserved at 48h.
- River-mouth and listed-ESU holding water: **not modeled**.
- Depth refuge unobserved (capability often 7 for “where every legal Chinook is”).
- Public GT is weekly/half-month, not 24–48h.

---

## 24. Sensitive-location rules

- Publish class: **PRIVATE** for any score; public biological map **NEVER_PUBLISH** at v0
- Never-publish: exact drifts; listed-ESU pins; river-mouth hotspots; competitor CPFV tracks
- Public max grain: none authorized; later floor ≥ PFMC subarea **and** ESA review

---

## 25. Last retrained date

`null` — **never trained**.

---

## 26. Current model version

`W2_chinook_encounter_v0_SPEC`

---

## 27. Reviewer status

- Status: **REQUIRED_HUMAN_REVIEW**
- Human reviewer names: **[] (none named)**
- Red-team signoff: **false**
- Domain-reviewer signoff: **false**
- Review date: `null`

Required later: ocean salmon biologist familiar with PFMC contact-rate models **and** an ESA/effort-concentration reviewer (`scientific_red_team_report.md`).

---

## 28. Permitted user claims

Only `claim_pack_W2_chinook_encounter_C_v0`. Relative CPUE rank in an **open** named area vs partner-log comparison set; not abundance; not a catch guarantee; closed cells unscored. **Not issuable today.**

---

## 29. Prohibited user claims

“You will catch fish”; “limits tomorrow”; abundance in this cell; scores on closed water; public spot maps; listed-stock targeting; retained catch as a survey; “where the fish are” heatmaps; SST/chl 24–48h habitat certainty; AIS as Chinook; juvenile indices as adult bite.

---

## 30. Recommended use cases

- Later **private** charter rank vs climatology, after DUA, regulation mask, and named salmon+ESA reviewers.
- Teaching example of **horizon mismatch** (seasonal SST papers ≠ 48h SDM).
- Globe: `UNKNOWN` hatch, not a king-salmon layer.

---

## 31. Not-recommended use cases

- Public 24–48h encounter heatmap (least scientifically defensible product).
- Customer brief on 2026-09-18.
- Using SST/chl/H3-6 cells as v0 product grain.
- Expanding observatory T2 eligibility into a commercial Chinook SKU.

---

## Approval block

| Role | Name | Date | Scope |
|---|---|---|---|
| Scientific red-team | *(NO-GO; not a human sign-off)* | 2026-09-18 | n/a |
| Domain reviewer | **none named** | | |
| Publisher | **none named** | | |
