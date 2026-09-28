# Agent handoff — REQUIREMENTS_AND_WEDGE_AGENT

**Agent ID:** REQUIREMENTS_AND_WEDGE_AGENT  
**Project:** FishAI / Ocean Intelligence Builder  
**Handoff time:** 2026-09-18T23:45:00-07:00  
**Project state after this work:** `STATE_10_PAUSED_FOR_HUMAN_DECISION`  
**Data ingested:** none  
**ML:** none  

Recipients: orchestrator; after founder decision, MARINE_DOMAIN, DATA_DISCOVERY, DATA_RIGHTS_AND_PRIVACY, GEOSPATIAL_DATA_ENGINEER, QUALITY_AND_VALIDATION, PRODUCT_AND_MONETIZATION, SCIENTIFIC_RED_TEAM.

Do not redefine the wedge. Do not write into this folder except to correct this agent’s errors.

---

## 1. Executive finding

The founder did not configure the project. HiveClaw and other `~/dev` repos do not name a FishAI company or a marine species. Under the master prompt, that requires a **stop**. Three lawful, narrow wedges were researched from official sources (catalog only) and remain options:

- **W1 (RECOMMENDED, not DECIDED):** Pacific oyster × Willapa Bay WA DOH growing areas × farm operator × 24–72h operational stress/work-window (**not** food-safety).
- **W2:** Chinook × Cape Falcon–Humbug Mountain, OR (or one named 2026 CA zone) × charter captain × 24–48h relative encounter.
- **W3:** American lobster × NMFS Statistical Area 513 × commercial operator × next-trip expected CPUE / effort allocation.

W1 is recommended because the decision still exists when fisheries close (CA salmon 2023–24 is the counterexample for W2), three farms can supply labels, official growing-area polygons exist, and secret-spot leakage is lower than capture fisheries. **Willingness to pay is untested (zero interviews).** Other agents may catalog public URLs for all three wedges but must not ingest, collect partner data, or train models until the founder answers `decision_required.md`.

---

## 2. Evidence table

| Finding | Evidence | Tier | Confidence | Relevance |
| --- | --- | --- | --- | --- |
| *M. gigas* accepted, AphiaID 836033; *C. gigas* 140656 unaccepted combination | WoRMS taxdetails 836033 / 140656 | 1 | High | W1 taxonomy |
| Chinook AphiaID 158075 | WoRMS 158075 | 1 | High | W2 taxonomy |
| American lobster AphiaID 156134 | WoRMS 156134 | 1 | High | W3 taxonomy |
| WA Pacific oyster: 114 farms, $106,801k sales (2023) | USDA NASS Census of Aquaculture Table 19 | 2 | High | W1 beachhead scale |
| WA total aquaculture 162 farms, $276,890k (2023) | USDA Table 1 | 2 | High | Context only |
| Pacific County 29 farms, $43.25M oysters+clams (2022 Ag Census via press) | Chinook Observer citing USDA | 4 (secondary report of census) | Medium | Willapa concentration |
| PCSGA: >$270M contribution, >3,200 jobs | pcsga.org/shellfish-economics | 4 | Low | Association marketing; do not use as NASS |
| PSI: 20–80% summer mortality in multiple WA growing areas | pacshell.org triploid project | 2/4 | Medium | W1 pain |
| 2021 heat dome × extreme lows killed intertidal shellfish; Pacific oysters worse than Olympia; more impact south/inland | Raymond et al. 2022 *Ecology*; UW News; WSG RRN | 1/2 | High | W1 mechanism |
| 2018 grower reports of 80–90%/bag vs 5–10% typical in some Puget Sound sites | WDFW Medium | 2/4 | Medium | Not a Willapa parameter |
| DOH growing-area program classifies commercial harvest waters; 2025 annual reviews exist (Nahcotta, Pacific Coast, Possession Sound) | doh.wa.gov growing-areas + 2025 PDFs | 1 | High | W1 boundary; **not** FishAI safety |
| NANOOS NVS Shellfish Growers exists specifically for grower water-quality decisions | nvs.nanoos.org/ShellfishGrowers; NCCOS product page | 3 | High | Incumbent viewer; packaging gap hypothesis |
| CO-OPS station 9440910 Toke Point, Willapa Bay | tidesandcurrents.noaa.gov datums | 1 | High | W1 tides |
| NWS products public domain with no-endorsement / no modified-as-official | weather.gov/disclaimer | 3 | High | Weather **link** only |
| Copernicus Marine: free licence; commercial value-added allowed with credit + DOI | marine.copernicus.eu licence | 3 | High | SST catalog |
| OBIS: per-dataset CC; some NC; occurrence ≠ abundance; sensitive records generalized | obis.org/data/datapolicy ; manual.obis.org/policy | 1/4 | High | Catalog only |
| 2026 US West Coast ocean salmon measures final (91 FR 29092, 19 May 2026) | fisheries.noaa.gov action page; FR 2026-09973 | 1 | High | W2 season exists |
| 2026 OR recreational Cape Falcon–Humbug Chinook window described (15 Mar–31 Aug except coho mark-selective overlap; in-season possible) | ODFW 2026 ocean sport salmon PDF | 1 | High | W2 geography |
| CA 2023 + 2024 ocean salmon fully closed; 2024 disaster 100% / $36.35M; 2023 CPFV 127 boats / $4.79M allocation | PFMC 2024 season PDF; NOAA 2024 determination; CDFW/NCGASA spend-plan draft | 1/2 | High / medium (draft) | W2 season risk + charter $ |
| CRFS/RecFIN estimate CA recreational catch/effort including CPFV; not a 24h product | wildlife.ca.gov/CRFS; recfin.org | 2 | High | Lagged baseline only |
| ME lobster 2025 prelim.: 78.8M lb, $461.4M, 5,060 licenses; −21k trips vs 2024 | DMR lobster_table.pdf; DMR news 6 Mar 2026 | 2 | High (prelim.) | W3 scale |
| GOM/GBK 2025: not depleted, overfishing, −34% from 2018; 202M avg abundance 2021–23 | ASMFC press + overview PDF | 2 | High | Limitation language; not a local forecast |
| VTS stratified by SA 511–514 | NOAA IR PDF | 2 | High | Seasonal index, not haul CPUE |
| Right-whale trap/pot rules exist and evolve | NOAA lobster management page | 1 | High | Official-link constraint |
| Founder config absent | Empty repo + prompt | 1 | High | Pause trigger |

---

## 3. Source / license table

See also `wedge_options.md`. **None approved for ingestion.**

| Source | Owner | Official URL | Access date | License / restriction | Rights class (proposed, not approved) |
| --- | --- | --- | --- | --- | --- |
| WoRMS taxon pages | VLIZ | https://www.marinespecies.org/ | 2026-09-18 | Cite WoRMS; check site terms | APPROVED_WITH_ATTRIBUTION for **lookup**, not bulk scrape |
| USDA NASS AQUA.txt | USDA | https://www.nass.usda.gov/Publications/AgCensus/2022/Online_Resources/Aquaculture/AQUA.txt | 2026-09-18 | US Gov; respect (D) suppression | APPROVED_WITH_ATTRIBUTION for citation |
| WA DOH growing areas | WA DOH | https://doh.wa.gov/community-and-environment/shellfish/growing-areas | 2026-09-18 | Agency public info; not a FishAI certificate | CONDITIONAL: display as official status with URL/time |
| DOH 2025 area PDFs | WA DOH | e.g. https://doh.wa.gov/sites/default/files/2025-08/nahcotta.pdf | 2026-09-18 | Public reports | Same |
| NANOOS NVS | NANOOS + providers | https://nvs.nanoos.org/ShellfishGrowers | 2026-09-18 | Public viewer; **provider-specific**; DMP notes SOS exceptions (OOI, ONC) | CONDITIONAL_REVIEW_REQUIRED per stream |
| NANOOS DMP | NANOOS | https://nanoos.org/documents/certification/NANOOS_DMP.pdf | 2026-09-18 | Plan, not a blanket commercial licence | Review |
| CO-OPS API | NOAA NOS | https://api.tidesandcurrents.noaa.gov/api/prod/ | 2026-09-18 | Typical US Gov; throttle; length limits | APPROVED_OPEN_COMMERCIAL likely; confirm |
| NWS disclaimer | NOAA NWS | https://www.weather.gov/disclaimer | 2026-09-18 | Public domain unless noted | APPROVED_OPEN_COMMERCIAL with no-endorsement |
| CMEMS licence | Mercator Ocean | https://marine.copernicus.eu/user-corner/service-commitments-and-licence | 2026-09-18 | Free; credit + DOI required | APPROVED_WITH_ATTRIBUTION |
| OBIS policy | IOC-UNESCO | https://obis.org/data/datapolicy/ | 2026-09-18 | Per dataset CC0/BY/BY-NC | CONDITIONAL; NC = NONCOMMERCIAL_ONLY |
| NMFS 2026 salmon | NOAA | https://www.fisheries.noaa.gov/action/2026-ocean-salmon-specifications-and-management-measures | 2026-09-18 | US Gov | Official regs |
| ODFW 2026 map | ODFW | https://www.dfw.state.or.us/mrp/salmon/Regulations/docs/2026_Ocean_Sport_Salmon_Map.pdf | 2026-09-18 | State | Official regs |
| CDFW ocean salmon | CDFW | https://wildlife.ca.gov/Fishing/Ocean/Regulations/Salmon | 2026-09-18 | State | Official regs |
| RecFIN | PSMFC | https://www.recfin.org/ | 2026-09-18 | Query/use via PSMFC | CONDITIONAL |
| Maine DMR landings | ME DMR | https://www11.maine.gov/dmr/fisheries/commercial/landings-program/historical-data | 2026-09-18 | Public aggregates | Coarse public; fine-scale RESTRICTED |
| ASMFC lobster | ASMFC | https://asmfc.org/species/american-lobster/ | 2026-09-18 | Cite commission | Context only |
| PSI project page | PSI | https://www.pacshell.org/triploid-oyster-health.asp | 2026-09-18 | Research; mortality form research-only | RESEARCH_ONLY for the form |
| SoundToxins | NWFSC/WSG | https://soundtoxins.org/about.html | 2026-09-18 | Partnership; not a commercial dump | CONDITIONAL; food-safety adjacent |

Rejected as labels: AIS-as-abundance; forum catch reports; DOH-as-FishAI-authorization.

---

## 4. Confidence and limitations

| Item | Confidence | Limitation |
| --- | --- | --- |
| Pause is required | High | Prompt Section 2 stop rule |
| Three wedges are viable research options | Medium-high | No operator interviews |
| W1 recommendation | Medium | Relationship-gated W2/W3 could win |
| Any WTP | None | Zero interviews |
| Willapa in-situ adequacy | Low-medium | ORCA is Hood Canal |
| 2026 salmon remaining open | Medium | In-season closures |
| Licence classifications | Low until rights agent | This agent proposes, does not approve |
| PCSGA $270M / jobs | Low | Not NASS |

Limitations: no paywalled sources accessed; no robots.txt bypass; no farm/vessel PII collected; 2025 DMR lobster figures preliminary; USDA (D) cells not inferred; Chinook Observer is secondary for county census.

---

## 5. Recommended decision

**PAUSE for human wedge approval.**  
Recommended (not decided): **W1 Willapa Pacific oyster 24–72h work/stress brief.**  
Next human action: complete `decision_required.md` items 3, 8, 9, and geography lock.

---

## 6. Rejected alternatives

- Global/multi-species terminal  
- Statewide WA shellfish  
- Geoduck-first  
- Maine Eastern oyster-first (smaller USDA sales)  
- Dungeness delayed-opener as v0 (seasonal + biotoxin gravity)  
- CA-wide Chinook  
- GOM-wide lobster  
- Consumer spot-map app  
- Using RecFIN/DMR landings/ASMFC abundance as 24h labels  
- Impersonating DOH/NWS/NOAA whale rules  

---

## 7. Follow-up questions

See `decision_required.md` Section 1 (full list). Blocking subset:

1. W1, W2, or W3?
2. Exact polygon names?
3. PRIMARY_OUTCOME_METRIC (W1: A stress-event / B workability / C mortality band)?
4. Named design partners or permission to interview?
5. FOUNDER_OR_ORGANIZATION?

---

## 8. Artifacts generated

```
/Users/wijeratne/dev/fishai/README.md
/Users/wijeratne/dev/fishai/project_state.json
/Users/wijeratne/dev/fishai/config/project_config.json
/Users/wijeratne/dev/fishai/decision_required.md
/Users/wijeratne/dev/fishai/artifacts/requirements_and_wedge/wedge_options.md
/Users/wijeratne/dev/fishai/artifacts/requirements_and_wedge/recommended_initial_wedge.md
/Users/wijeratne/dev/fishai/artifacts/requirements_and_wedge/customer_decision_map.md
/Users/wijeratne/dev/fishai/artifacts/requirements_and_wedge/decision_economics.md
/Users/wijeratne/dev/fishai/artifacts/requirements_and_wedge/interview_script.md
/Users/wijeratne/dev/fishai/artifacts/requirements_and_wedge/assumptions_register.md
/Users/wijeratne/dev/fishai/artifacts/requirements_and_wedge/agent_handoff.md
/Users/wijeratne/dev/fishai/iteration_reports/ITERATION_REPORT_2026-09-18_01.md
/Users/wijeratne/dev/fishai/checkpoints/CHECKPOINT_2026-09-18T2215.md
```

Directory skeleton created for other agents (empty).

---

## 9. Red-team needed?

**Yes, after wedge lock, before any customer-facing sentence.** Not blocking while paused.

High-severity themes to queue for SCIENTIFIC_RED_TEAM_AGENT:

- Food-safety impersonation (W1)
- Habitat-as-abundance (W2)
- Assessment-count-as-local-CPUE (W3)
- Secret-spot leakage via maps/explanations (W2/W3)
- Heat-mortality causal overclaim (W1)
- Spatial transfer Willapa ← Hood Canal ORCA (W1)

---

## 10. Suggested next experiment

**Do not run until founder lock.**

Highest priority score (qualitative): **founder decision** (unblocks everything).

After W1 lock: 14-day **manual** Willapa brief for one farm; 30-second outcome form; no ingest beyond what the farm already screenshots from official sites; compare to “tides + NANOOS” status quo. Score: decision value high, uncertainty reduction high, feasible, legally conservative.

After W2 lock: five captains, open-day coarsened logs vs last-week persistence baseline.

After W3 lock: DUA conversation with one co-op; no public map mockups.

---

## Notes for sibling agents (non-binding)

| Agent | Do now | Do not |
| --- | --- | --- |
| MARINE_DOMAIN | Dossiers for **all three** taxa at catalog depth, or wait for lock | Lock species |
| DATA_DISCOVERY | Catalog URLs in this handoff | Download bulk, parallelize OBIS against guidance |
| DATA_RIGHTS | Classify table in §3 | Approve ingest of NANOOS wholesale |
| GEOSPATIAL | Draft **empty** canonical thoughts only if needed; prefer wait | Freeze schema on three geographies |
| QUALITY | Cannot define labels yet | Invent PRIMARY_OUTCOME_METRIC |
| PRODUCT | Do not build UI | Wireframe all three as if decided |
| RED_TEAM | Optional pre-mortem on forbidden claims | Falsify a model that does not exist |
