# Decision required — FishAI / Ocean Intelligence Builder

**Date:** 2026-09-18  
**Agent:** REQUIREMENTS_AND_WEDGE_AGENT  
**Project state:** `STATE_10_PAUSED_FOR_HUMAN_DECISION`  
**Why this file exists:** Founder did not supply Section 2 configuration. After catalog-only official-source research, species, geography, customer, decision, and primary outcome metric remain **UNRESOLVED**. The prompt requires a stop here. Nothing below is DECIDED.

No data have been ingested. No model has been trained. HiveClaw / Atlas / NeuroClaw inspection did not yield a FishAI legal entity or a marine-product founder choice.

---

## 1. Exact founder decisions required before proceeding

Answer these in writing (email, this file, or `config/project_config.json`). Until they are answered, other agents may catalog public sources but **must not ingest, partner-collect, or start ML**.

### A. Identity

1. Confirm working **PROJECT_NAME** = FishAI, or supply another.
2. Supply **FOUNDER_OR_ORGANIZATION** (legal/operating name). Do not assume HiveClaw.

### B. Lock the wedge (pick exactly one)

3. Choose **W1, W2, or W3** below, or write a replacement that is still one species × one named geography × one customer type × one recurring decision.
4. If W1: choose geography lock — **Willapa Bay DOH growing areas (recommended)** vs **named South Puget Sound growing areas** vs another single DOH-named area set. Statewide “Washington growing areas” is too broad.
5. If W2: choose the PFMC/ODFW/CDFW management polygon (recommended if W2: **Cape Falcon, OR to Humbug Mountain, OR** recreational ocean salmon area) and confirm customer is **CPFV / charter captain**, not private skiff or commercial troll.
6. If W3: choose the NMFS statistical area (recommended if W3: **Statistical Area 513**) and confirm customer is **commercial lobster operator**, not dealer or recreational.
7. Confirm **life stage** if it changes the label (W1: grow-out diploid/triploid; W2: ocean adult Chinook; W3: legal-size commercial lobster).

### C. Decision, metric, delivery

8. Confirm the **single primary decision** (wording in Section 2).
9. Confirm **PRIMARY_OUTCOME_METRIC** (candidates in each wedge below). Without this, Quality/Validation cannot define a label.
10. Confirm **forecast horizon**, **decision frequency**, **spatial resolution**, **product delivery format** (email/SMS/WhatsApp/PDF; not a terminal).
11. Confirm the product will **not** issue food-safety, navigation, weather-safety, or legal-harvest authorization.

### D. Pilot and constraints

12. **HUMAN_DOMAIN_EXPERTS_AVAILABLE** — names/roles, or “none yet.”
13. **TARGET_PILOT_CUSTOMER_COUNT**, **PILOT_START_DATE**, **SUCCESS_THRESHOLD**, **FAILURE_THRESHOLD**.
14. Permission to run the interview script with 8–15 operators in the chosen wedge (no farm/catch GPS in notes).
15. **DATA_STORAGE_REGION**, **SECURITY_REQUIREMENTS**, **BUDGET_CONSTRAINT**, **COMPUTE_CONSTRAINT**.
16. Any **KNOWN_DATA_PARTNERS**, **KNOWN_LIMITATIONS**, or **REGULATORY_OR_SAFETY_CONSTRAINTS** the founder already has.

Minimum set that unblocks STATE_2: items **3, 8, 9**, plus geography lock (4/5/6 as applicable).

---

## 2. Three viable narrow wedges

All three are ONE × ONE × ONE × ONE. All are catalog-only. None is DECIDED. Taxonomy from WoRMS, accessed 2026-09-18.

### W1 — Pacific oyster farm operations (RECOMMENDED, not decided)

| Axis | Value |
| --- | --- |
| Species | Pacific oyster, *Magallana gigas* (Thunberg, 1793), WoRMS AphiaID **836033** (synonym *Crassostrea gigas* AphiaID 140656) |
| Geography | Washington DOH **commercial growing areas in the Willapa Bay system** (Pacific County), e.g. Nahcotta and adjacent Willapa polygons — not all WA waters |
| Customer | Commercial oyster **farm operator** (crew lead / farm manager) |
| Recurring decision | Next **24–72 hours**: is this a **stress / disruption / work window**? Mobilize, handle/move gear, or delay husbandry because of heat-at-low-tide, waves/wind, temperature / dissolved oxygen / salinity stress |
| Explicitly not | Food-safety harvest authorization; DOH open/closed; biotoxin “safe to eat” |

### W2 — Chinook charter encounter ranking

| Axis | Value |
| --- | --- |
| Species | Chinook salmon, *Oncorhynchus tshawytscha* (Walbaum, 1792), WoRMS AphiaID **158075** |
| Geography | One PFMC/state ocean salmon area: **Cape Falcon, OR to Humbug Mountain, OR** recreational fishery (2026 ODFW ocean sport salmon map). Do not start with all CA+OR. |
| Customer | **Charter / CPFV captain** operating that area when the season is open |
| Recurring decision | Next **24–48 hours**: **relative encounter / trip-area ranking** among coarsened cells inside the open area (not a secret-spot map) |
| Explicitly not | Legal fishing authorization; navigation/weather-safety; exact GPS hotspots; wild-population counts; ESA take advice |

### W3 — Gulf of Maine lobster effort allocation

| Axis | Value |
| --- | --- |
| Species | American lobster, *Homarus americanus* H. Milne Edwards, 1837, WoRMS AphiaID **156134** |
| Geography | **NMFS Statistical Area 513** (southern Gulf of Maine / western Maine inshore; DMR treats 513 as Cape Elizabeth–NH border in survey materials) |
| Customer | **Commercial lobster operator** (day-trip inshore) |
| Recurring decision | **Next trip**: expected **CPUE / effort allocation** among coarsened sub-areas (where to spend soak/haul effort), not exact trap coordinates |
| Explicitly not | Abundance census; public hotspot map; right-whale compliance advice that overrides NOAA; exact set locations |

Why these three were kept: official taxonomy, bounded agency geographies, a repeated expensive decision, and a path to permissioned outcomes. No replacement beat them on those tests (see `wedge_options.md`).

---

## 3. Tradeoffs

| | W1 Oyster ops | W2 Chinook charter | W3 Lobster CPUE |
| --- | --- | --- | --- |
| Recurrence | Daily/event in warm season; farms operate year-round | Only when ocean salmon is **open**; CA was fully closed 2023 and 2024 | Near-year-round, trip-based; 2025 Maine trips fell ~10% vs 2024 |
| Public environmental data | Strong: NANOOS Shellfish Growers, ORCA (uneven), CO-OPS tides (Toke Point 9440910), NWS, Copernicus SST | Moderate: SST/fronts/upwelling as **habitat covariates only**; not presence | Moderate: NERACOOS/bottom temp as covariates; VTS/sea-sampling are survey indices, not haul CPUE |
| Ground truth | Needs **3 farm partners** logging mortality/work days; public DOH data is sanitation, not farm outcome | Needs **captain trip logs**; RecFIN/CRFS are lagged management estimates, not 24h labels | Needs **permissioned haul CPUE**; DMR landings are confidential at fine scale |
| Sensitive-location risk | Farm performance private; leases coarsened; **lower** “secret spot” risk than capture fisheries | **High**: productive locations; ESA-listed Chinook stocks; tribal usual-and-accustomed areas | **High**: trap locations commercially sensitive; North Atlantic right whale entanglement geography |
| Adjacent forbidden claim | Food-safety / NSSP closures | Fishing authorization, navigation, abundance | Whale-rule compliance, stock census |
| Industry scale (documented, not WTP) | USDA 2023: **114 WA Pacific oyster farms**, **$106.801 million** sales; Pacific County 2022 Ag Census (press): 29 farms, $43.25 million oysters+clams | 2023 CA ocean salmon disaster: **127 eligible CPFVs**; NOAA allocated **$4.79 million** to that sector; 2024 CA disaster **100% revenue loss**, **$36.35 million** all evaluated sectors | Maine DMR preliminary 2025: **78.8 million lb**, **$461.4 million**, **5,060** commercial trap licenses |
| Incumbent overlap | NANOOS already shows water quality to growers — FishAI must **decide work/stress**, not clone the map | Recreational apps (Fishbrain/Fishidy) and state regs — FishAI must rank **relative encounter with uncertainty**, not spots | Landings dashboards and stock assessments — FishAI must support **next-trip effort**, not publish another landings chart |
| Best first if founder has… | WA grower access / PCSGA / PSI / Sea Grant path | OR (or open CA 2026) charter relationships | Maine harvester / co-op relationships and appetite for private CPUE |

**Recommendation (not a decision):** W1, because the decision repeats even when fisheries are closed, farm geography is already an official polygon, public covariates exist, and the sensitive-location blast radius is smaller than W2/W3. See `recommended_initial_wedge.md`.

---

## 4. Minimum customer / data requirements for each

### W1 — Oyster

**Customers:** ≥3 Willapa (or chosen growing-area) Pacific oyster farms; at least one intertidal/bag or on-bottom operation where heat-at-low-tide and work windows matter. One crew-lead interview per farm.

**Data (catalog now, ingest only after rights approval):**

- Official: WA DOH growing-area polygons and **attributed** classification/closure URLs (context, not the product); NOAA CO-OPS tides (9440910 Toke Point); NWS marine/coastal forecasts; NANOOS/NERR/Ecology/PSI in-situ where licenses allow; Copernicus Marine SST with required credit.
- Partner (consent required): daily or event mortality % by bag/bed; work-day completed vs postponed; handling events; optional existing sensors. No public farm-performance map.
- Not required for v0: new hardware; Vibrio/biotoxin lab results as a FishAI safety score.

**Label candidate:** stress/disruption event in 24–72h (mortality jump or forced work delay) **or** “workable vs not workable” tide/wave/heat window — founder must pick one.

### W2 — Chinook charter

**Customers:** ≥5 CPFV captains who ran Chinook trips in the chosen 2026 open area; written agreement to log species, catch/no-catch, effort (angler-hours or lines), coarsened area, not public GPS.

**Data:** PFMC/NMFS 2026 season rule and in-season notices; ODFW/CDFW regs; RecFIN/CRFS as **lagged baseline only**; Copernicus/NOAA SST and oceanographic covariates; NWS marine forecasts as **linked official weather**, never as FishAI navigation advice.

**Label candidate:** trip-level Chinook CPUE or binary encounter in coarsened cells. RecFIN cannot be the 24h label.

**Season risk:** if the chosen area closes, the product has no decision to serve. 2026 CA/OR seasons are open under NMFS final rule (91 FR 29092, 19 May 2026) but in-season closures happen.

### W3 — Lobster

**Customers:** ≥8 commercial harvesters in SA 513 (or one co-op that can sign for them) willing to share **private** haul-level catch and trap-haul effort, coarsened spatially.

**Data:** Maine DMR historical landings (statewide/zone, not haul); ASMFC 2025 assessment as context not a 24h forecast; ventless-trap survey indices as seasonal baseline; NERACOOS/NOAA bottom temp; NOAA right-whale restricted-area **official links** as constraints, not a FishAI compliance engine.

**Label candidate:** next-trip expected CPUE (legal lobster per trap-haul) in coarsened sub-areas.

**ASMFC Oct 2025:** GOM/GBK **not depleted**, **overfishing occurring**. Any abundance-like language is a red-team blocker.

---

## 5. What is blocked until those decisions

Blocked:

- Transition out of `STATE_10_PAUSED_FOR_HUMAN_DECISION`
- Setting `INITIAL_*` in `config/project_config.json` to anything but UNRESOLVED
- Data ingestion, partner collection, logbook capture
- Canonical schema freeze, pipelines, ML, baselines against a real label
- Customer-facing briefs that name a species/geography as the product
- Expanding to a second species, state, or customer type
- Hardware proposals
- Using DOH/SoundToxins/ORHAB as a FishAI “safe to harvest” model
- Using AIS as abundance
- Publishing fishing or farm coordinates

Allowed while paused:

- Other agents **cataloging** official URLs for the three wedges
- Interview scheduling **after** founder names the wedge and grants contact permission
- Rights review of cataloged sources (no ingest)

**Highest-priority next action:** founder selects W1/W2/W3 and PRIMARY_OUTCOME_METRIC, then 8–15 interviews with the script in `artifacts/requirements_and_wedge/interview_script.md`.
