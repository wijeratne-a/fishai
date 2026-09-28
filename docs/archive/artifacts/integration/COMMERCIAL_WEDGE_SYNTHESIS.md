# Commercial wedge synthesis — FishAI

**Date:** 2026-09-18  
**Agent:** COMMERCIAL_LAYER_INTEGRATOR (claims remediator)  
**Project state:** `STATE_10_PAUSED_FOR_HUMAN_DECISION` — **unchanged**  
**Wedge:** **RECOMMENDED, not DECIDED.** This file does not lock W1/W2/W3.  
**Go / no-go:** **PAUSE**, not GO.  
**Ingest / ML / observatory:** none. No data ingested. No model trained. Nothing written under `observatory/`.

---

## One-paragraph founder recommendation

Keep the run **paused**. Do **not** lock a wedge in `config/project_config.json` from this memo. The **recommended** (not decided) first commercial test is **W1: Pacific oyster (*Magallana gigas*) × Washington DOH commercial growing areas in the Willapa Bay system × farm operator × a daily email + 1-page PDF 72-hour Category D operational-stress / work-window brief**, with a **hard WA DOH wall** (official growing-area / biotoxin / Vp status as a separate attributed module, never mixed into an ops score). Two or more specialist agents already agree: **halt all customer-facing model claims**. After you lock a wedge, the only honest next product is a **manual** decision brief in a later pilot — not “AI abundance,” not harvest legality, not SST-as-body-temperature. W2 (Chinook 24–48h encounter) and W3 (lobster next-trip CPUE) remain viable research options if you already have captains or a co-op; they are worse first commercial tests. Answer `decision_required.md` (minimum: items 3, 8, 9, plus geography lock). Until then: no ingest, no training, no interviews without permission, no customer send.

---

## Recommended W1 (not locked)

| Axis | Recommended value |
|---|---|
| Species | Pacific oyster, *Magallana gigas* (Thunberg, 1793), WoRMS AphiaID **836033** (synonym *Crassostrea gigas* 140656) |
| Geography | WA DOH **commercial growing areas in the Willapa Bay system** (Pacific County), e.g. Nahcotta and adjacent Willapa polygons — **not** statewide WA, **not** Totten Inlet as a demo (2026 Vp Category 3 harvest-control area) |
| Customer | Commercial oyster **farm operator** (crew lead / farm manager) |
| Recurring decision | Next **24–72 hours**: stress / disruption / **work window** — mobilize, handle/move gear, or delay husbandry because of **air × low-tide emersion × solar** and **wind/wave workability**, with water T / DO / salinity as **supporting covariates** (lag and spatial mismatch documented) |
| Delivery | Daily **email + 1-page PDF**; WhatsApp/SMS only as an Elevated ping that deep-links the 14-field brief |
| Explicitly not | Food-safety harvest authorization; DOH open/closed as a model output; biotoxin “safe to eat”; SST as oyster body temperature; commands; three-decimal fake precision; “top 20%” ranks |

**v0 after founder lock:** analyst-assembled manual brief from NWS air + CO-OPS tides + wind/wave + linked DOH status. No ML. No map product. No AIS.

---

## W2 and W3 (still options, not decided)

### W2 — Chinook charter encounter ranking

- Species: Chinook salmon, *Oncorhynchus tshawytscha*, AphiaID **158075**
- Geography (if chosen): one PFMC/state ocean salmon area; recommended if W2: **Cape Falcon, OR to Humbug Mountain, OR** recreational
- Customer: **CPFV / charter captain**
- Decision: next **24–48 hours**, relative **effort-normalized encounter rank** among coarsened cells **inside an open area**
- **Customer-facing model: HALTED.** Literature does not identify 24–48h habitat encounter from SST/chlorophyll. Allowed later research only: open/closed mask + partner-log climatology + optional weather-workability as a **confounder**, not “fish are here.” Closed or unverified regulation ⇒ **no score**.
- Explicitly not: legal fishing authorization; navigation/weather-safety; exact GPS hotspots; wild-population counts; ESA take advice

### W3 — Gulf of Maine lobster effort allocation

- Species: American lobster, *Homarus americanus*, AphiaID **156134**
- Geography (if chosen): **NMFS Statistical Area 513**
- Customer: **commercial lobster operator** (day-trip inshore)
- Decision: **next trip** expected **CPUE / effort allocation** among coarsened sub-areas on **that operator’s own strings**
- Conditional second pilot only if a co-op will share private haul CPUE. **No AIS/GFW as abundance. No public hotspot map.**
- Explicitly not: abundance census; public hotspot map; right-whale compliance engine; exact set locations

---

## Agreement across specialist agents

Status of folders: requirements, marine domain, rights, geospatial, quality/validation, product, red team, and a **partial** data-discovery catalog all exist. None of them lock the wedge. None approve ingest.

| Agent | Agrees that… | Does **not** claim… |
|---|---|---|
| **Requirements** | W1 is the best *starting* ONE×ONE×ONE×ONE if relationships are also unresolved; pause until founder lock | WTP; Willapa in-situ adequacy |
| **Marine domain** | Honest v1 target for oyster is Category **D** ops-stress; top covariates start with **air T × tidal emersion**; DOH polygons are a frame not a label; Chinook 24–48h is the weakest operator product | A locked species; bag-level % dead |
| **Data rights** | None of the three is categorically illegal if claims stay inside decision-support; oyster is the cleanest **if** food-safety is structurally impossible in the UI; GFW/AIS/confidential landings blocked; NANOOS/IOOS/DOH GIS need review before ingest | Ingest approval; legal advice |
| **Geospatial** | Design-only canonical model; stay local + fixture; as-of snapshots required; public products coarsened; do not build the lake | Measured coverage/latency; license clearance for CMEMS/NANOOS |
| **Quality / validation** | Protocol only; no GT in hand; advanced ML blocked; oyster label = partner ops disruption **not** closures; B12/B3/B4 as first “model”; numeric GO gates are **HYPOTHESIS** | Any skill number; identifiability of 24–48h Chinook |
| **Product** | First *sellable* test is email+PDF 72h oyster ops brief; Chinook crowded/season-gated; lobster needs private logs; **0 interviews** | That farms will pay; that NANOOS is beaten |
| **Scientific red team** | Safest *scientific* pilot = private oyster Category D ops-stress with food-safety wall, air+tide+solar+wave; still **NO-GO** for any customer-facing model; Chinook heatmap least defensible; lobster public CPUE map is a blocker | Human domain sign-off (this agent is not the reviewer) |
| **Data discovery** | Public physics/weather catalogs exist; **ground truth at the decision horizon is the binding gap** for all three; partner logs do not exist in-repo | A complete, rights-approved catalog (still incomplete) |

**Where two or more already agree (binding for this integrator):**

1. **Halt customer-facing model claims** until a named human domain reviewer and a locked wedge exist.
2. Product, if it proceeds after lock, may be a **manual** Category D (oyster) or Category C (lobster/Chinook rank) **decision brief**, not an abundance/harvest/AI score.
3. Official closures, RecFIN, DMR landings, and AIS are **not** 24–72h labels.
4. SST is not oyster body temperature, not Chinook presence, not lobster density.

**Disagreement / residual tension (do not paper over):**

- Quality’s first pass scored “label specifiable = 5” and expert-rule feasibility high; red team says specifiable ≠ identifiable and the old SST ≥ 19 °C rule was invalid. **Integrator action:** B4 rewritten; Chinook identifiability not treated as solved; numeric gates stay **HYPOTHESIS**.
- Product wanted a 30-day paid-signal test; red team forbids shipping a numeric score. **Integrator action:** manual brief only after lock; sample copy remediated so it cannot be pasted as a live forecast.
- Marine domain listed 8–12 °C thermal habitat with depth as a Chinook covariate; red team rejects it as v1 copy. **Integrator action:** customer-facing Chinook model halted; SST/chl not v0 encounter features.
- Geo H3 res 8 is fine for **private raster sampling**, fatal as a public stress choropleth. Unresolved until product geography = named lease / DOH area.
- Data discovery still incomplete; rights agent default-denies GFW/live AIS; discovery must not treat that as ajar.

---

## Remaining blockers (HIGH still open = **yes**)

Copy remediation of the Totten / “top 20%” / SST≥19°C-as-kill language **does not** clear scientific or legal deployment blockers. Red-team global status remains **NO-GO** for customer-facing models.

| ID | Still blocking | Why copy-edit is not clearance |
|---|---|---|
| B-ALL-01…04 | No spatiotemporal validation, no as-of replay, no prospective baseline beat, 14-field contract not in a live UI path | Protocol exists; nothing executed |
| B-ALL-05 | No named human domain reviewer | Agents cannot accept residual HIGH risk |
| B-ALL-07 | No source approved for ingest | Rights register is catalog-only |
| B-ALL-08 | Wedge UNRESOLVED | Cannot mix oyster/Chinook/lobster labels |
| B-OYS-01 | Food-safety / harvest-legality wall not implemented as a **shipping** product constraint | Sample now *describes* Module A vs Module B; no live UI |
| B-OYS-03 | SST-only thermal spec | Sample/B4 now air×emersion-first; **no fitted features** |
| B-OYS-04 | No partner farm outcome stream | Zero DUAs |
| B-CHK-* | 24–48h habitat encounter not identified; ESA/stock-mix; no partner trips | Model claims halted; blockers remain if W2 is chosen |
| B-LOB-* | AIS/privacy/hyperstability | Remain if W3 is chosen |
| RT-SIB-04…07 | Chinook thermal-habitat v1, H3 product grain, AIS diagnostic left ajar, scorecard identifiability inflation | Not fully rewritten (surgical halt only); still HIGH/MEDIUM |
| RT-OYS-01 | Combined score / harvest-window language will still be *read* as legality by operators | Needs NSSP-literate human reviewer before any real send |

**Sibling copy that was patched in this pass (see `claims_remediation_log.md`):** RT-SIB-01 (B4 SST≥19°C kill law), RT-SIB-02 (Totten / top 20% / +1.8 °C sample), RT-SIB-03 (“safely work” / B5 “harvest plans”). **Status vs red-team register:** copy is no longer the unsafe original; **HIGH scientific blockers stay OPEN** until a human reviewer signs.

---

## What is NOT ready

- Founder identity, legal entity, and Section 2 configuration
- A **DECIDED** wedge
- Customer interviews (traction = **zero**)
- Design-partner farms / captains / co-op DUAs
- Any ingest-approved source
- Ground-truth labels at product grain
- Fitted baselines (B12/B3/B4 are specs only)
- A trained or even rule-scored model
- A live 14-field email path with human QA
- Named shellfish + NSSP (or salmon+ESA, or lobster+confidentiality) reviewers
- Paid pilot, pricing evidence, or outcome loop
- Hardware, maps, AIS, HAB/Vibrio product, or a terminal
- Data-discovery catalog freeze (present, incomplete)

---

## Exact founder questions (from `decision_required.md`)

Answer in writing (email, that file, or `config/project_config.json`). Until answered, other agents may catalog public sources but **must not ingest, partner-collect, or start ML**.

### A. Identity

1. Confirm working **PROJECT_NAME** = FishAI, or supply another.
2. Supply **FOUNDER_OR_ORGANIZATION** (legal/operating name). Do not assume HiveClaw.

### B. Lock the wedge (pick exactly one)

3. Choose **W1, W2, or W3**, or write a replacement that is still one species × one named geography × one customer type × one recurring decision.
4. If W1: geography lock — **Willapa Bay DOH growing areas (recommended)** vs **named South Puget Sound growing areas** vs another single DOH-named area set. Statewide “Washington growing areas” is too broad. **Do not** start with Totten as a temperature-led harvest demo.
5. If W2: PFMC/ODFW/CDFW polygon (recommended if W2: **Cape Falcon, OR to Humbug Mountain, OR**) and confirm customer is **CPFV / charter captain**.
6. If W3: NMFS statistical area (recommended if W3: **Statistical Area 513**) and confirm customer is **commercial lobster operator**.
7. Confirm **life stage** if it changes the label (W1: grow-out diploid/triploid; W2: ocean adult Chinook; W3: legal-size commercial lobster).

### C. Decision, metric, delivery

8. Confirm the **single primary decision**.
9. Confirm **PRIMARY_OUTCOME_METRIC** (W1 candidates: A stress/disruption event / B workable window / C mortality band). Without this, Quality cannot define a label.
10. Confirm **forecast horizon**, **decision frequency**, **spatial resolution**, **product delivery format** (email/SMS/WhatsApp/PDF; not a terminal).
11. Confirm the product will **not** issue food-safety, navigation, weather-safety, or legal-harvest authorization.

### D. Pilot and constraints

12. **HUMAN_DOMAIN_EXPERTS_AVAILABLE** — names/roles, or “none yet.” (Red team: oyster needs shellfish extension **and** NSSP/public-health literate reviewer.)
13. **TARGET_PILOT_CUSTOMER_COUNT**, **PILOT_START_DATE**, **SUCCESS_THRESHOLD**, **FAILURE_THRESHOLD**.
14. Permission to run the interview script with 8–15 operators in the chosen wedge (no farm/catch GPS in notes).
15. **DATA_STORAGE_REGION**, **SECURITY_REQUIREMENTS**, **BUDGET_CONSTRAINT**, **COMPUTE_CONSTRAINT**.
16. Any **KNOWN_DATA_PARTNERS**, **KNOWN_LIMITATIONS**, or **REGULATORY_OR_SAFETY_CONSTRAINTS**.

**Minimum set that unblocks STATE_2:** items **3, 8, 9**, plus geography lock (4/5/6 as applicable).

---

## Highest-priority next action

**Founder wedge lock** (and PRIMARY_OUTCOME_METRIC), then 8–15 interviews with `artifacts/requirements_and_wedge/interview_script.md`. Do not ingest. Do not train. Do not send the sample brief as if it were validated.

**After lock (not now):** 14-day **manual** Willapa (or chosen polygon) Category D brief for one consenting farm; 30-second outcome form; DOH module separate; compare to “tides + NANOOS”; stop if the farm would not change a crew call **or** if they only want harvest-legal advice.
