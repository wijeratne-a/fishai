# Wedge options — exactly three viable ONE × ONE × ONE × ONE products

**Agent:** REQUIREMENTS_AND_WEDGE_AGENT  
**Access date for all cited URLs:** 2026-09-18  
**Status:** Options only. Founder has not chosen. Do not treat any row as DECIDED.  
**Long-term vision (not the v0):** trusted intelligence layer for biological, environmental, operational, regulatory, and commercial ocean conditions. v0 is one recurring decision, not a terminal.

Inspection of `/Users/wijeratne/dev/HiveClaw`, Atlas, NeuroClaw, and `docs/venture_swarm` found **no** FishAI entity, marine species choice, or ocean-product founder configuration. HiveClaw is local LLM inference. Those repos are not used as marine facts.

No candidate was replaced. Alternatives considered and rejected are at the end.

---

## How “narrow enough” was tested

A wedge is viable only if all are true:

1. One accepted taxon (WoRMS) with a common-name that operators actually use.
2. One named agency geography (DOH growing area, PFMC/ODFW salmon area, NMFS statistical area) — not “the West Coast.”
3. One paying operator type who repeats a decision inside 72 hours when the season/farm is active.
4. A label that is not a legal/safety authorization.
5. A catalog of lawful official sources (not ingested).
6. A path to permissioned outcomes without publishing secret spots, farm P&L, Indigenous knowledge, or protected-species dens.
7. Public incumbents are maps/regs/assessments; the gap is a **decision brief with uncertainty**, not another dashboard.

---

## W1 — Pacific oyster × Willapa Bay growing areas × farm operator × 24–72h stress / work-window

### The four locks

| Lock | Specification |
| --- | --- |
| Species | Pacific oyster. Accepted WoRMS name *Magallana gigas* (Thunberg, 1793), AphiaID [836033](https://www.marinespecies.org/aphia.php?p=taxdetails&id=836033). Industry and WA sources still say *Crassostrea gigas* (unaccepted combination, AphiaID [140656](https://www.marinespecies.org/aphia.php?p=taxdetails&id=140656)). Query both IDs in OBIS/GBIF; display Pacific oyster + accepted scientific name. |
| Geography | Washington State Department of Health **commercial shellfish growing-area polygons in the Willapa Bay system**, Pacific County (Nahcotta annual review and adjacent Willapa/Pacific Coast classified waters). Not “all Puget Sound.” Optional founder swap: a **named** South Puget Sound growing area (e.g. Totten / Hammersley) — still one polygon set. |
| Customer | Commercial oyster farm operator (farm manager / crew lead), not DOH, not recreational harvester, not a generic “seafood buyer.” |
| Decision | Before the next work window (24–72h): **operational stress, disruption, or workability** — mobilize labor, handle/move bags or beds, or delay because of heat-at-low-tide, wave/wind, and water-column stress (temperature, DO, salinity, freshwater pulse). |

**Use-case letter:** C (shellfish-farm operational risk). **Not** food-safety authorization.

### Why this is narrow enough

- One cultured species, not “shellfish.”
- Official growing-area boundaries already exist ([WA DOH Growing Areas](https://doh.wa.gov/community-and-environment/shellfish/growing-areas); 2025 Nahcotta review PDF).
- The decision is a farm operations call, not NSSP classification.
- Intertidal culture makes tides + heat a real work constraint (2021 heat dome).

### Tradeoffs

**For**

- USDA NASS 2023 Census of Aquaculture Table 19: Washington **114 farms**, **$106,801 thousand** Pacific oyster sales ([AQUA tables](https://www.nass.usda.gov/Publications/AgCensus/2022/Online_Resources/Aquaculture/AQUA.txt)).
- Pacific County 2022 Census of Agriculture (reported by *Chinook Observer* citing USDA): **29 farms**, **$43.25 million** oysters and clams — concentrated coastal buyer pool.
- Documented mortality: Pacific Shellfish Institute reports **20–80%** losses in multiple WA commercial growing areas in recent summers ([PSI triploid oyster health](https://www.pacshell.org/triploid-oyster-health.asp)). WDFW 2018 grower reports: **80–90% per bag** vs **5–10% typical** in Discovery Bay / northern Whidbey ([WDFW Medium](https://wdfw.medium.com/whats-been-causing-mass-shellfish-die-offs-around-puget-sound-1ada7071a242)) — different basins; treat as evidence of severe events, not a Willapa parameter.
- 2021 heat dome + extreme low tides: Washington Sea Grant Rapid Response Network; Raymond et al. 2022 *Ecology* ([doi:10.1002/ecy.3798](https://doi.org/10.1002/ecy.3798)); UW News 21 Jun 2022. Pacific oysters more affected than Olympia oysters; southern inland sites worse.
- Observing system already aimed at growers: [NANOOS NVS Shellfish Growers](https://nvs.nanoos.org/ShellfishGrowers); NOAA NCCOS product page. WA sites include Padilla Bay NERR, UW ORCA (Hood Canal), Ecology (incl. Willapa Bay Center), Pacific Shellfish Institute (Bay Center).
- Tides: NOAA CO-OPS station **9440910 Toke Point, Willapa Bay** ([datums](https://tidesandcurrents.noaa.gov/datums.html?id=9440910)); API [https://api.tidesandcurrents.noaa.gov/api/prod/](https://api.tidesandcurrents.noaa.gov/api/prod/) with documented length limits and throttling.
- Fixed leases → less “secret fishing spot” leakage than W2/W3.
- Farms run when salmon seasons are closed.

**Against**

- NANOOS already packages water quality; a clone dashboard has no wedge. Product must be **tomorrow’s work/stress call**.
- Food-safety gravity well: DOH classifications, rainfall closures, HABs (SoundToxins, ORHAB). Easy to accidentally imply “safe to harvest.”
- ORCA moorings are Hood Canal, not Willapa; Willapa in-situ is thinner (Ecology / PSI Bay Center). Spatial transfer is an assumption.
- Farm outcomes are private (WDFW Aquatic Harvest Hub user manual: harvest data disclosure exemptions, RCW 42.56.430).
- Mixed culture (Manila clam, geoduck) on some farms — keep the **decision** on Pacific oyster or the wedge collapses.
- WTP untested (no interviews).

### Minimum customer requirements

- 3 design-partner farms in the named growing areas; ≥1 intertidal/bag or on-bottom Pacific oyster plot.
- Weekly (stress-season daily) contact who can act on a 60-second brief.
- Consent: coarsened zone-level outcomes may train a private model; **no** public performance map; revocation path.

### Minimum data requirements (catalog; do not ingest yet)

| Need | Candidate official source | Role |
| --- | --- | --- |
| Growing-area polygons / official open-closed | WA DOH Growing Areas + annual reviews (e.g. [Nahcotta 2025 PDF](https://doh.wa.gov/sites/default/files/2025-08/nahcotta.pdf), [Pacific Coast 2025 PDF](https://doh.wa.gov/sites/default/files/2025-08/pacific.pdf)) | Boundary + **attributed** regulatory context. Not a FishAI safety model. |
| Tides / work window | CO-OPS 9440910 and predictions | Heat-at-low-tide and access window |
| Weather / waves / wind | NWS public-domain marine products ([disclaimer](https://www.weather.gov/disclaimer)) | Workability; **link official forecast**; do not give navigation advice |
| Water temperature, salinity, DO, chlorophyll | NANOOS NVS / NERR / Ecology / ORCA where provider terms allow | Stress covariates. Coverage gap in Willapa must be stated. |
| SST / marine heatwave context | Copernicus Marine (licence: credit “E.U. Copernicus Marine Service Information”; [licence](https://marine.copernicus.eu/user-corner/service-commitments-and-licence)); NOAA SST | Regional anomaly, not farm DO |
| Taxonomy | WoRMS 836033 | Name lock |
| Outcome label | Partner logs; PSI mortality form is **research-only**, not a commercial label | Ground truth |

SoundToxins ([soundtoxins.org](https://soundtoxins.org/about.html); NWFSC/WSG partnership) and ORHAB are **HAB early-warning research**, not FishAI food-safety. Catalog for later rights review; do not make toxin scores the v0 label.

### Why not “all Washington growing areas”

South Puget Sound vs Willapa differ in tidal range, heat, hypoxia, and species mix (Washington Sea Grant *Shellfish Aquaculture in Washington State* PDF, 2013 regional split: South Puget Sound vs Willapa). Statewide v0 is four wedges pretending to be one.

---

## W2 — Chinook × Cape Falcon–Humbug Mountain × charter captain × 24–48h relative encounter

### The four locks

| Lock | Specification |
| --- | --- |
| Species | Chinook / king salmon. *Oncorhynchus tshawytscha* (Walbaum, 1792), WoRMS AphiaID [158075](https://marinespecies.org/aphia.php?p=taxdetails&id=158075). |
| Geography | One ocean salmon management area: **Cape Falcon, OR to Humbug Mountain, OR** recreational fishery as mapped by ODFW for 2026 ([2026 Oregon Ocean Recreational Salmon Seasons PDF](https://www.dfw.state.or.us/mrp/salmon/Regulations/docs/2026_Ocean_Sport_Salmon_Map.pdf)). Founder may swap to one 2026 CDFW ocean salmon zone (e.g. Fort Bragg 40°10'–Point Arena) if captain access is CA-only — still one polygon. |
| Customer | CPFV / charter captain, not private trailer-boat and not commercial troll. |
| Decision | Given the area is legally open: **which coarsened cells inside the area have higher relative Chinook encounter conditions in the next 24–48h**, to choose trip area / whether to run. |

**Use-case letter:** A (sportfishing / charter encounter forecast). Output class: **relative encounter likelihood (Category D)** or effort-normalized catch index (Category C) — never a count of wild fish.

### Why this is narrow enough

- One species (Chinook), not “salmon.”
- One named management area, not CA+OR+WA.
- Decision is tomorrow’s trip, not seasonal allocation.
- 2026 seasons exist (NMFS final rule [2026 Ocean Salmon Specifications](https://www.fisheries.noaa.gov/action/2026-ocean-salmon-specifications-and-management-measures), 91 FR 29092, 19 May 2026) after **full CA closures in 2023 and 2024**.

### Tradeoffs

**For**

- Clear money at risk: CDFW 2023 disaster spend-plan draft: **127 eligible CPFVs**, NOAA allocation **$4,791,327** to that sector; per-angler prices **$225 / $265** used in the formula ([draft spend plan](https://ncgasa.org/wp-content/uploads/2024/04/2023-California-Salmon-Disaster-Spend-Plan-Draft_040324.pdf)). 2024 CA SRFC/KRFC disaster: **100% revenue loss**, **$36,348,617** vs 5-year average excluding 2023 ([NOAA determination PDF](https://www.fisheries.noaa.gov/s3/2024-12/CA-Salmon-Determination-2024.pdf)). Oregon 2023 commercial ocean salmon: **91% revenue loss** ([Commerce letter](https://www.fisheries.noaa.gov/s3/2024-06/OR-131-Ocean-Salmon-Determination-2023.pdf)).
- RecFIN ([recfin.org](https://www.recfin.org/)) and CDFW CRFS ([CRFS](https://wildlife.ca.gov/Conservation/Marine/CRFS)) exist as lagged catch/effort estimates; CPFV logs are required in CA.
- Captains already choose area vs fuel/time every open morning.

**Against**

- **Season fragility:** a closure zeros the product. CA 2023–2024 is the existence proof.
- RecFIN/CRFS are **not** 24-hour labels (sample-based, delayed). Partner trip logs are mandatory.
- ESA-listed Chinook, Southern Resident killer whales in the NMFS action species list, tribal fisheries — high legal/ecological sensitivity.
- Public hotspot maps would violate the privacy rule and invite overharvest narratives.
- SST/chlorophyll ≠ fish. Habitat covariates only.
- 2026 CA recreational seasons are pulse-like (CDFW [Ocean Salmon Fishery Information](https://wildlife.ca.gov/Fishing/Ocean/Regulations/Salmon)); OR Cape Falcon–Humbug has a longer “all salmon except coho” window (15 Mar–31 Aug 2026 per ODFW map, subject to in-season action).
- WTP untested; disaster payments ≠ subscription intent.

### Minimum customer requirements

- ≥5 captains with 2026 (or 2022 and earlier) Chinook trips in the locked area.
- 30-second post-trip form: date, coarsened cell, effort, Chinook kept/released/zero, no public GPS.
- Agreement that FishAI is not a fishing licence or weather router.

### Minimum data requirements

- NMFS/PFMC 2026 measures + in-season notices; ODFW/CDFW regs with timestamps.
- RecFIN/CRFS for **retrospective baseline**, not live spots.
- NOAA/Copernicus oceanography as covariates.
- NWS marine forecasts as official links only.
- Partner CPFV logs for labels.

---

## W3 — American lobster × NMFS Statistical Area 513 × commercial operator × next-trip CPUE / effort

### The four locks

| Lock | Specification |
| --- | --- |
| Species | American lobster. *Homarus americanus* H. Milne Edwards, 1837, WoRMS AphiaID [156134](https://www.marinespecies.org/aphia.php?p=taxdetails&id=156134). |
| Geography | **NMFS Statistical Area 513** (GOM inshore southern/western Maine). Maine DMR ventless-trap materials treat 511/512/513 as the three federal statistical areas in the Gulf of Maine; 513 described as Cape Elizabeth–NH border in [DMR 2025 science update deck](https://www.maine.gov/dmr/sites/maine.gov.dmr/files/inline-files/Forum2025_DMRScienceUpdateSlideDeck_0.pdf). Do not start with all LCMA 1 or Zones A–G. |
| Customer | Commercial lobster license holder running day trips (trap/pot). Not dealer, processor, or recreational. |
| Decision | **Next trip:** expected CPUE (legal lobster per unit effort) and where to allocate haul/set effort among **coarsened** sub-areas inside 513. |

**Use-case letter:** B (commercial fisheries planning / expected CPUE). Output class: **Category C** effort-normalized index, coarsened.

### Why this is narrow enough

- One species, one statistical area, one gear (traps), one next-trip allocation decision.
- Maine landings program and ASMFC assessments exist at coarse scale.
- Day-trip inshore fishery is the GOM majority (ASMFC: GOM ~82% of US landings since 1982).

### Tradeoffs

**For**

- Maine DMR lobster table (updated 6 Feb 2026; 2025 preliminary): **78,826,683 lb**, **$461,384,405**, **5,060** trap-capable commercial licenses; 2024: 87.3 million lb, $536.5 million, 5,218 licenses ([lobster_table.pdf](https://www.maine.gov/dmr/sites/maine.gov.dmr/files/inline-files/lobster_table.pdf)). DMR news 6 Mar 2026: **~21,000 fewer trips** in 2025 vs 2024 (~10% effort drop) ([DMR news](https://www1.maine.gov/dmr/news/fri-03062026-1200-2025-maine-commercial-fisheries-value-again-tops-600-million)).
- NOAA: 2023 US American lobster **121 million lb**, **$633 million**; ME+MA = 93% of US harvest ([NOAA lobster management](https://www.fisheries.noaa.gov/species/american-lobster/management)).
- Ventless trap survey stratified by SA 511–514 and depth (NOAA IR, [repository.library.noaa.gov](https://repository.library.noaa.gov/view/noaa/66494/noaa_66494_DS1.pdf)) — seasonal index, not next-trip CPUE.
- Climate/temperature is first-order in the 2025 assessment — a covariate story exists.

**Against**

- ASMFC Oct 2025: GOM/GBK **not depleted**, abundance down **34%** from 2018 peak, **overfishing occurring** (exploitation 0.465 vs threshold 0.464); 2021–23 average abundance **202 million** lobsters, below industry target 229 million, above limit 143 million ([ASMFC press](https://asmfc.org/news/press-releases/american-lobster-benchmark-stock-assessment-finds-gom-gbk-stock-not-depleted-but-experiencing-overfishing-sne-stock-significantly-depleted-but-not-experiencing-overfishing/); [overview PDF](https://asmfc.org/wp-content/uploads/2025/11/AmericanLobsterStockAssmtOverview_Oct2025.pdf)). **Do not publish those numbers as a FishAI local forecast.**
- Haul-level CPUE is confidential. Statewide landings cannot label tomorrow’s trip.
- Exact trap locations are the moat of each boat; a public map is both a privacy violation and a non-starter for WTP.
- North Atlantic right whale take-reduction: seasonal restricted areas, sinking groundlines, haul-interval rules ([NOAA lobster management](https://www.fisheries.noaa.gov/species/american-lobster/management)). FishAI must **link official rules**, never claim compliance.
- High coordination cost: many small vessels vs a few oyster farms.
- WTP untested; inflation-adjusted 2025 value “more in line with 2008” (Commissioner Wilson) — pain is real, payment is not evidenced.

### Minimum customer requirements

- ≥8 SA 513 harvesters **or** one co-op/association that can contract outcome sharing.
- Private haul log: date, coarsened cell, trap-hauls, legal count, bait/soak if available.
- Written ban on publishing set GPS, even in model explanations.

### Minimum data requirements

- DMR historical landings (coarse) + metadata on confidentiality.
- ASMFC assessment as **context / limitation**, not a feature that implies local abundance.
- VTS / sea-sampling as seasonal baselines if redistribution/commercial use is approved by rights agent (likely CONDITIONAL).
- NERACOOS / NOAA temperature covariates.
- Official ALWTRP / restricted-area feeds as **constraint layers with URLs**, not predictions.
- Partner haul CPUE for the label.

---

## Side-by-side

| Test | W1 Oyster | W2 Chinook | W3 Lobster |
| --- | --- | --- | --- |
| Decision exists if fishery closed? | Yes | No | Mostly yes (whale closures still bind) |
| Official polygon exists? | DOH growing area | PFMC/ODFW area | NMFS SA 513 |
| Partner count to start | 3 farms | 5 captains | 8 boats or 1 co-op |
| Public 24h label? | No | No | No |
| Secret-spot risk | Medium (leases) | High | High |
| Forbidden-claim gravity | Food safety | ESA / licence / navigation | Whales / census |
| Environmental data density | High (uneven in Willapa) | Medium | Medium |
| Recommended if founder has no relationships yet | **Yes (extension path: PCSGA, PSI, WSG)** | Only with captains | Only with DMR/industry intro |

---

## Alternatives considered and not used as a fourth wedge

These failed the ONE × ONE × recurring-72h × lawful-label test **more clearly** than the three above. They are not ranked as the three options.

| Alternative | Why not |
| --- | --- |
| Statewide multi-species WA shellfish | Violates one species; geoduck/Manila have different decisions |
| WA geoduck only | High value, few farms, slower decisions, heavy politics; weaker 24–72h work-window story than intertidal oysters |
| Eastern oyster (*Crassostrea virginica*) Maine | Smaller than WA Pacific oyster sales (USDA Table 19: ME Eastern 76 farms, $14.211 million vs WA Pacific $106.801 million) |
| CA/OR Dungeness crab delayed opener | High value, but the painful decision is **seasonal** (whale/domoic delay), not a daily 24–48h product; domoic is food-safety adjacent |
| CA full-state Chinook | 2023–24 closure; too many PFMC zones |
| All Gulf of Maine lobster (511–514 + GB) | Geography not one statistical area |
| Recreational Fishbrain-style app | Generic map; secret spots; weak B2B WTP; violates product thesis |
| Global Copernicus dashboard | Explicitly forbidden by the north-star |

---

## Evidence and licence snapshot (catalog only)

| Source | Owner | URL | License / terms (as stated at access) | Tier | Confidence | Use |
| --- | --- | --- | --- | --- | --- | --- |
| WoRMS *M. gigas* | VLIZ / WoRMS | https://www.marinespecies.org/aphia.php?p=taxdetails&id=836033 | Check WoRMS citation terms; taxonomy lookup | 1 (authority list) | High | Name lock W1 |
| WoRMS *O. tshawytscha* | VLIZ / WoRMS | https://marinespecies.org/aphia.php?p=taxdetails&id=158075 | Same | 1 | High | Name lock W2 |
| WoRMS *H. americanus* | VLIZ / WoRMS | https://www.marinespecies.org/aphia.php?p=taxdetails&id=156134 | Same | 1 | High | Name lock W3 |
| USDA Census of Aquaculture 2023 | USDA NASS | https://www.nass.usda.gov/Publications/AgCensus/2022/Online_Resources/Aquaculture/AQUA.txt | US government work; do not disclose suppressed (D) cells | 2 (census) | High | W1 scale |
| WA DOH growing areas | WA DOH | https://doh.wa.gov/community-and-environment/shellfish/growing-areas | Agency public information; not FishAI certification | 1 (authority) | High | W1 boundary / official status link |
| NANOOS Shellfish Growers | NANOOS / partners | https://nvs.nanoos.org/ShellfishGrowers | Public viewer; **provider terms may differ**; IOOS DMP notes exceptions | 3 (in-situ + portal) | Medium | W1 covariates |
| CO-OPS API | NOAA NOS | https://api.tidesandcurrents.noaa.gov/api/prod/ | US Gov public domain typical; respect throttle/length limits | 1/3 | High | W1 tides |
| NWS disclaimer | NOAA NWS | https://www.weather.gov/disclaimer | Public domain unless noted; no endorsement; no modified-as-official | 3 | High | Weather link |
| Copernicus Marine licence | Mercator Ocean / EU | https://marine.copernicus.eu/user-corner/service-commitments-and-licence | Free; commercial value-added allowed with **mandatory credit + DOI** | 3 | High | SST |
| OBIS data policy | IOC-UNESCO OBIS | https://obis.org/data/datapolicy/ | Per-dataset CC0 / CC BY / CC BY-NC; **verify each dataset**; NC blocks commercial | 1/4 occ. | Medium | Occurrence catalog only; not abundance |
| NMFS 2026 salmon measures | NOAA Fisheries | https://www.fisheries.noaa.gov/action/2026-ocean-salmon-specifications-and-management-measures | US Gov | 1 (regulation) | High | W2 season |
| RecFIN | PSMFC | https://www.recfin.org/ | Management database; query/use terms via PSMFC; not a live label | 2 | Medium | W2 baseline |
| Maine DMR landings | Maine DMR | https://www11.maine.gov/dmr/fisheries/commercial/landings-program/historical-data | State public aggregates; fine-scale confidential | 2 | High | W3 scale |
| ASMFC 2025 lobster assessment | ASMFC | https://asmfc.org/species/american-lobster/ | Commission publication; cite; not a local CPUE model | 2 (assessment) | High | W3 limitation |
| PSI oyster mortality project | Pacific Shellfish Institute | https://www.pacshell.org/triploid-oyster-health.asp | Research; voluntary form **research-only** | 2/4 | Medium | W1 pain evidence |

**No source in this table is APPROVED for ingestion.** Rights agent must classify each before any download into production storage.

---

## Scoring (agent judgment, 0–5; not a founder decision)

| Criterion | W1 | W2 | W3 |
| --- | --- | --- | --- |
| Recurring decision while budget remains | 5 | 2 | 4 |
| Lawful public covariates | 4 | 3 | 3 |
| Path to private ground truth | 4 | 3 | 2 |
| Sensitive-location blast radius (higher = worse) | 2 | 5 | 5 |
| Documented operator pain | 4 | 4 | 4 |
| WTP evidence | 1 | 1 | 1 |
| Forbidden-claim proximity | 4 | 4 | 4 |
| Narrowness | 5 | 4 | 4 |

W1 leads on recurrence, ground-truth logistics, and privacy. W2/W3 remain viable if the founder already has those operators.
