# Species Model Card — W1 Pacific oyster 72h ops-risk (DRAFT)

**card_id:** `SMC-W1-OYSTER-OPS-RISK-v0-DRAFT`  
**schema_version:** `SMC-SCHEMA-2026-09-18-v1`  
**as_of_date:** `2026-09-18`  
**card_status:** **NOT_PUBLISHED**  
**operational_status:** **NOT_OPERATIONAL**  
**claim_pack:** `claim_pack_W1_oyster_ops_D_v0`  
**wedge_id:** `W1_oyster_wa_ops_72h`  
**wedge_lock_status:** **UNRESOLVED** (founder has not locked species × geography × customer × decision; W1 is RECOMMENDED in commercial artifacts, not DECIDED)  
**factory_step:** 5 (architecture/baselines specified; steps 6–7 not reached)  
**observatory_output_class:** `HYPOTHETICAL/RESEARCH MODE`  
**capability_class:** 4 (forecast of 72h farm stress **requires** partner labels + lease sensors; not forecastable today)  
**interviews_completed:** **0**  
**observations_ingested:** **0**  
**evidence_tier_strongest_label:** `none` (no labels in hand)  
**supersedes_card_id:** `null`  
**red_team_blocker_ids:** `B-ALL-01`–`B-ALL-08`, `B-OYS-01`–`B-OYS-05`, `RT-OYS-01`, `RT-OYS-04`, `RT-OYS-08`, `RT-XCUT-01`, `RT-XCUT-11`  
**extrapolation_flag:** `true` (vacuous: no training envelope exists)

This card is a **SPEC** for an unpublished expert-rule + climatology baseline. **No training. No ingest. No interviews.** It cannot authorize a globe layer or a customer brief.

---

## 1. Species identity

| | |
|---|---|
| Common name | Pacific oyster (Pacific cupped oyster, Japanese oyster, Miyagi oyster) |
| Accepted scientific name | *Magallana gigas* (Thunberg, 1793) |
| WoRMS AphiaID | 836033 |
| LSID | `urn:lsid:marinespecies.org:taxname:836033` |
| Principal synonyms | *Crassostrea gigas* (Thunberg, 1793), AphiaID **140656**, unaccepted superseded combination. Industry/WA agencies still use *C. gigas* — same biological species, required join key. |
| Common-name collisions | **Portuguese oyster** = *Magallana angulata* (do not synonymize). **Olympia / native oyster** = *Ostrea lurida*. Eastern/Virginia oyster = *Crassostrea virginica*. “Oysters” on WA DOH maps mix taxa and are food-safety geography. |
| Population unit | Permissioned **named lease** inside a WA DOH growing area. Not a wild stock. Not partitioned as a fishery ESU. |

Registry row: `OBS-TAX-003` (adult). Larval row `OBS-TAX-027` is **out of this card**.

---

## 2. Taxonomic authority

- Authority: **WoRMS**
- URL: https://www.marinespecies.org/aphia.php?p=taxdetails&id=836033
- Access date: **2026-09-18**
- WoRMS status: accepted
- License status: **UNKNOWN** for full-database reuse; taxon **webservice lookup** catalogued as `APPROVED_WITH_ATTRIBUTION` in the commercial data-rights register (cite WoRMS; no full dump). Images default CC BY-NC-SA — not used here.
- Notes: NOAA Fisheries dual-labels *Crassostrea gigas; Magallana gigas* and already uses Genus *Magallana* in its classification table (page updated 2026-04-13).

---

## 3. Geographic scope

- Description: Washington State commercial aquaculture leases and adjacent classified growing waters. Scientifically coherent v1 bound is **one estuary** (Willapa Bay **or** a named South/Central Puget Sound cluster), not “all Washington tidelands.” Hood Canal hypoxia ≠ Willapa heat.
- Bounding units: WA DOH commercial growing areas as **spatial convenience only**; WA DNR aquaculture leases; recommended research AOI Willapa Bay (Pacific County) if later locked.
- Public grain: **no public lease-level stress map**. If anything public ever ships: coarsened growing-area **environmental** context without farm performance (`B-OYS-05`).
- Founder-locked: **false** (UNRESOLVED wedge).

---

## 4. Depth scope

- Depth band: `INTERTIDAL_AIR` (emersion/aerial heat) **plus** `SURFACE_0_5` water for subtidal/off-bottom culture. Stratify by culture type; do not pool.
- Depth known: **false** at product grain today (no lease metadata ingested).
- Notes: Satellite SST skin ≠ intertidal tissue temperature. A 1 km SST pixel is the wrong grain for a bag/bed.

---

## 5. Life stage

- **In scope:** already-planted spat, juvenile grow-out, and market-size adults on the farm, plus **gear** workability. Sessile after settlement — biomass on the lease is known to the operator; the question is stress/disruption, not “where are the oysters.”
- **Out of scope:** hatchery larvae / OA veligers (2009 seed-crisis stage); wild set as a census; Olympia oyster.

---

## 6. Prediction target

- Name: 72h operational disruption / environmental-stress **indicator**
- Definition: Rank of physical/operational stress conditions (workability, emersion-heat exposure, wave/gear) relative to **this lease’s** comparable tides/season. Category **D**. **Not** mortality percent. **Not** harvest legality.
- Horizon: 24–72 hours from issuance (UTC + local tide clock)
- Unit: tercile or elevated/typical/reduced **indicator** vs named comparison set (not a probability of death)
- `label_id`: `ops_disruption_72h` (binary workability/mortality-protocol/gear-loss — **specified, zero rows**)

---

## 7. Output category (A–E / visual truth state)

- Prediction-contract category: **D**
- Visual-truth state **today:** `UNKNOWN` (do not draw a stress field)
- Visual-truth state **if ever live:** ops-stress ordinal encoding (`FORECAST` / `MODEL_INFERENCE` of the **indicator**), never presence teal, never red = oysters here, never combined with DOH open/closed.

Not A (farmers already know bag counts). Not B (no coastwide farm-mortality survey). Not C (not a capture fishery). Not E (SST-as-oyster-risk is rejected).

---

## 8. Support tier T0–T6

- Factory eligibility tier: **T2** (habitat/stress envelope from literature; registry `OBS-TAX-003`)
- Emitted tier: **T0** (nothing published; live class `UNKNOWN/INSUFFICIENT DATA`)
- Evidence ceiling tier: **T2** until partner outcomes + prospective tests exist. T4/T6 **not assigned**. Commercial importance does not upgrade the tier.
- Notes: Farm occupancy is `OPERATIONALLY OBSERVED` **on a private lease**, not a global T5 layer.

---

## 9. Training data sources

| source_id | role | ingested | rights_class | notes |
|---|---|---|---|---|
| partner_farm_mortality_workability_logs | label | **false** | `APPROVED_PARTNER_CONSENT` (unsigned) | Required GT; n=0 |
| partner_lease_sensors | feature | **false** | `APPROVED_PARTNER_CONSENT` | In situ T/S/DO; n=0 |
| NWS_air_temp_forecast | feature | **false** | `APPROVED_OPEN_COMMERCIAL` (catalog) | Primary B4 input when built |
| CO-OPS_tides | feature | **false** | `APPROVED_OPEN_COMMERCIAL` | Emersion clock |
| NWS_wind_wave | feature | **false** | `APPROVED_OPEN_COMMERCIAL` | Workability; farm-specific threshold not invented |
| CMEMS_or_NOAA_SST | supporting / not_used as label | **false** | `APPROVED_WITH_ATTRIBUTION` / open | **Wrong thermal variable** if used as oyster body T |
| NANOOS_ERDDAP | feature | **false** | `CONDITIONAL_REVIEW_REQUIRED` | Dataset license often missing |
| WA_DOH_growing_area_status | context_only | **false** | `CONDITIONAL_REVIEW_REQUIRED` | **Never a label** |
| SoundToxins | forbidden as ops label | **false** | `UNKNOWN` | HAB harvest ≠ animal stress |
| GFW_AIS | forbidden | **false** | `NONCOMMERCIAL_ONLY` / `REJECTED` for this use | Irrelevant to sessile stock |

No source in this table has been downloaded into FishAI stores.

---

## 10. Data rights status

- Overall: **catalog only; ingest not authorized**
- Human legal review: **REQUIRED**
- Ingest authorized: **false**
- Privacy default: farm performance `PRIVATE` / `NEVER_PUBLISH` publicly; lease polygons private-by-default
- Notes: Highest legal risk is food-safety impersonation of WA DOH/FDA/NSSP (WAC 246-282-006). Tribal shellfish: CARE; default `NEVER_PUBLISH`. Do not scrape the DOH map viewer.

---

## 11. Observation count

- Ingested n: **0**
- Catalog metadata n: OBIS *M. gigas* occurrence metadata total **43714** as of 2026-09-18 (effort-biased compiled records; **not** farm 72h labels; **not ingested**)
- Partner label n: **0**

---

## 12. Observation methods

**None operated by FishAI.** Specified future labels (not collected): partner daily workability (worked tide Y/N), protocol mortality counts, gear-loss Y/N, optional HOBO/lease sondes. Official DOH sanitary survey / biotoxin tissue tests are **context**, not ops labels. NANOOS grower stations are covariates if later licensed — not GT.

---

## 13. Environmental variables

| name | role | mechanism_status | notes |
|---|---|---|---|
| Air temperature × daytime emersion × solar | primary | causal | 2021 AHW analogue (Raymond et al. 2022). Intertidal only. |
| Wind / wave workability | primary | causal | Farm-specific threshold; **drop clause** if partner has not given one |
| In situ water T / DO / S | supporting | causal (local) | Sensor lag vs bags; Hood Canal DO ≠ Willapa heat |
| Satellite SST | supporting or not_used | **wrong_variable** if sold as body T | Skin ≠ intertidal tissue; SST-only ⇒ Low/None |
| Chlorophyll-a | not_used as 72h mortality | proxy | Food/growth weeks–months; never abundance |
| pH / Ω_aragonite | not_used | causal **for larvae**, not 72h adults | Wrong stage |
| NSSP / fecal coliform / Vp / biotoxin | context_only | n/a (legal) | **forbidden_as_label** |
| AIS | not_used | n/a | Irrelevant |

**Forbidden default:** SST ≥ 19 °C for ≥12 h (growth/clearance band, not a WA intertidal mortality law). Hobday MHW flags dropped (wrong event class).

---

## 14. Feature availability / latency

- As-of replay implemented: **false**
- `availability_at_prediction_time`: **specified_not_built** (design in `as_of_replay_design.md`)
- Notes: `B-ALL-02` open. Cannot be OPERATIONAL without frozen issuance snapshots. Env forecast age, in situ age, and **DOH last-verified** must be separate clocks.

---

## 15. Model architecture

- Family: **expert_rule_plus_climatology**
- Trained: **false**
- Description: Unfitted **B4** expert-rule (air × daytime emersion × optional farm wind/wave OR) plus **B12** seasonal-spatial climatology of `ops_disruption_72h` (`baseline_model_spec.md` Candidate A). No ML. No neural net. No EnKF. Architecture agent: open-loop B4+B12. **Neither B4 nor B12 has been computed** — 0 labels.

---

## 16. Baseline comparison

- Baselines specified: **true** (B1, B2, B12, B3, B4, B5)
- Baselines fitted: **false**
- Relevant baseline id: `null` (would likely be **B4** for “better than a grower’s thresholds,” **B12** for climatology)
- Beats relevant baseline: **not_evaluated**
- Notes: Beating a water-temperature baseline is not oyster stress. If B4 already has acceptable recall/false-alert tradeoff, ML must beat B4, not merely B1.

---

## 17. Validation approach

- Protocol id: `VAL-PROTOCOL-2026-09-18-v1` §4.1
- Time-forward run: **false**
- Spatial holdout run: **false**
- Prospective pilot run: **false**
- Status: **NOT_RUN** (vacuous fail of `B-ALL-01`)

Required later: basin spatial blocks; onset vs continuation split; **do not** score against DOH closures or SST.

---

## 18. Performance metrics

- Available: **false**
- Primary metric: `null` (specified hypotheses: Brier skill vs B12; recall-at-precision vs B4; false alerts/farm-month)
- Value: `null`
- Split: `null`
- Notes: No numeric skill may be quoted. Thresholds in the quality scorecard are hypotheses, not FishAI results.

---

## 19. Calibration results

- Calibration plot accepted by a named human: **false**
- ECE / coverage: `null`
- Notes: Do not print calibrated-looking percentages. Delayed mortality (days–weeks after 4 h aerial heat; George et al.) means a 72h window can miss the labeled death.

---

## 20. Known biases

- Sensor farms are better capitalized; failed farms vanish (survivorship).
- Culture method, ploidy (triploid vs diploid), density, bag color, elevation in cm dominate residuals.
- Pooling Willapa, South Sound, and Hood Canal confounds mechanisms.
- Operator behavior (the action the brief would suggest) confounds observed mortality.
- 2021 event is an atmospheric heat × midday tide template, not a typical summer day.

---

## 21. Known failure modes

- **Food-safety / harvest-legality contamination** (BLOCKER RT-OYS-01): any combined green/red with DOH/NSSP.
- SST-as-body-temperature (HIGH RT-OYS-02).
- Closures used as ops labels (BLOCKER RT-OYS-04).
- “Harvest window” as model output (BLOCKER RT-OYS-08).
- Single “stress score” mixing heat, hypoxia, HAB, disease, waves (RT-OYS-06).
- Public lease-level map (privacy + false precision).
- Importing OsHV-1 timing from CA/EU into WA without PCR.
- Treating OA nowcast as 72h adult-farm headline.

---

## 22. Uncertainty method

- Method: specified rule table in `uncertainty_policy.md` (FRESH, DENSITY, IN_DOMAIN, SOURCE_HEALTH, CALIBRATION_OK, LABEL_SUPPORT). Not implemented. SST-only ⇒ **Low** or **None**.
- Confidence labels allowed: **false** until labels exist (policy exists; issuance forbidden)
- Numeric probabilities allowed: **false**

---

## 23. Geographic / seasonal / depth gaps

- No Willapa (or any) lease time series in-repo.
- Hood Canal ORCA ≠ Willapa instrumentation.
- Winter vs summer mechanisms differ; summer mortality literature ≠ 72h gear/heat indicator without culture metadata.
- Subtidal vs intertidal: drop aerial-heat clause for fully subtidal rather than substituting SST.
- Depth microclimate (cm of elevation) unobserved.

---

## 24. Sensitive-location rules

- Publish class: **PRIVATE** (lease ops). Public default **NEVER_PUBLISH** for farm KPIs, disease, yield, exact lease corners.
- Never-publish: other farms’ mortality; harvest-site business identification from DOH viewer internals; tribal harvest locations; combined sanitation+stress maps.
- Public max grain: coarsened growing-area **environment** only, after ecological-harm + counsel review — **not authorized today**.

---

## 25. Last retrained date

`null` — **never trained**.

---

## 26. Current model version

`W1_oyster_ops_risk_v0_SPEC`

---

## 27. Reviewer status

- Status: **REQUIRED_HUMAN_REVIEW**
- Human reviewer names: **[] (none named)**
- Red-team signoff: **false** (red team is NO-GO; this agent is not the human reviewer)
- Domain-reviewer signoff: **false**
- Review date: `null`

Required later: human **shellfish** reviewer **and** NSSP/public-health reviewer (food-safety wall), plus named publisher (`governance.md`).

---

## 28. Permitted user claims

Only `claim_pack_W1_oyster_ops_D_v0` (see `permitted_vs_prohibited_claims.md`). In short: Category D **operational stress indicator** on a named permissioned lease; not food-safety; not harvest authorization; SST is not body temperature. **Not issuable today.**

---

## 29. Prohibited user claims

**Food-safety; harvest authorization; SST = body temperature; abundance.** Also: open/closed as a model output; NSSP/FDA/WA DOH/ISSC “meets requirements”; toxin-free / no *Vibrio*/PSP/DSP/ASP; combined sanitation+ops score; another farm’s KPIs; “harvest now”; weather-safety “safely work the tide”; 19 °C SST kill-law; percent dead to false precision.

---

## 30. Recommended use cases

- Research packaging of **air × tide × wave** with a **separate** official DOH module, after DUA + sensors + human review.
- Honest `UNKNOWN` / data-gap globe hatch over Willapa **without** an oyster count.
- Factory documentation that T2 eligibility ≠ a 72h forecast.

---

## 31. Not-recommended use cases

- Customer-facing 72h brief on 2026-09-18.
- Globe “oyster risk” heatmap.
- Using this card to lock the commercial wedge.
- Training on DOH closures or SST-only.
- Cross-farm public leaderboard.

---

## Approval block

| Role | Name | Date | Scope |
|---|---|---|---|
| Scientific red-team | *(none — NO-GO recorded, not a human sign-off)* | 2026-09-18 | n/a |
| Domain reviewer | **none named** | | |
| Publisher | **none named** | | |
