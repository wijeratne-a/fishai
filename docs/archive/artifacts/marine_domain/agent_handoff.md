# Agent handoff — MARINE_DOMAIN_AGENT

**Project:** Ocean Intelligence Builder / FishAI  
**Date:** 2026-09-18  
**Access date for all URLs:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/artifacts/marine_domain/`  
**Wedge status:** **UNRESOLVED.** No founder-locked scope. Three candidates are scored scientifically only.

**Non-negotiables observed:** lawful official/peer-reviewed sources; no data ingestion; SST/AIS/chlorophyll never treated as abundance; no protected-species precise locations; food-safety harvest authorization and catch guarantees excluded.

---

## 1. Executive finding

All three candidates are **scientifically coherent** if and only if the prediction target stays inside the class listed below. None supports Direct Count. None supports treating SST, AIS, or chlorophyll as animals.

| ID | Candidate | Honest v1 target | Top scientific fit for a 24–72 h **operator** product |
|----|-----------|------------------|------------------------------------------------------|
| **C1** | Pacific oyster (*Magallana gigas*) × WA growing areas × farm operator × 24–72 h **operational stress/disruption** | **Category D** relative habitat-encounter-risk of **stress/disruption** | **Highest.** Animals are sessile and already counted by the farmer. 24–72 h physics (air T × tide, water T, DO, storms) are real. Main failure is confusing WA DOH harvest legality with animal stress. |
| **C3** | American lobster (*Homarus americanus*) × bounded GOM statistical area × commercial operator × next-trip **CPUE / effort allocation** | **Category C** effort-normalized **catch**, explicitly not abundance | **Middle.** Best survey infrastructure, but next-trip signal is mostly **catchability** (bottom T, molt, bait, soak, weather). Satellite SST is the wrong temperature. |
| **C2** | Chinook (*Oncorhynchus tshawytscha*) × bounded CA/OR coastal area × charter captain × 24–48 h **relative encounter likelihood** | **Category D** relative habitat-encounter-risk; evaluate with Category C CPUE | **Lowest for this horizon.** Mixed mobile stocks, ESA overlay, vertical thermal refuge, and regulations dominate. Juvenile chl-habitat papers and NWFSC stoplight indicators are the **wrong stage and timescale**. |

**Taxonomy:** WoRMS accepts *Magallana gigas* (AphiaID 836033); *Crassostrea gigas* (140656) is an unaccepted superseded combination. NOAA dual-labels the oyster but already uses Genus *Magallana*. Chinook and lobster names **agree** across WoRMS, ITIS, and NOAA.

**This is not a product decision.** If a later agent locks a wedge, it must not widen C2 into a catch guarantee, C1 into NSSP authorization, or C3 into exact abundance.

---

## 2. Evidence table (per candidate)

### C1 — Pacific oyster × Washington farms

| Item | Finding | Tier | Confidence |
|------|---------|------|------------|
| **Recommended target** | Category **D**: 24–72 h relative **operational stress/disruption risk** on a named lease/culture method. Not harvest open/closed. | — | High |
| **Top 5 covariates** | (1) Air temperature × tidal emersion (2) Water temperature (3) Dissolved oxygen (4) Salinity/runoff (5) Storms/wind/waves; **plus** culture method as required metadata | 1–2 | High |
| **Cannot predict** | Bag-level % dead without loggers; OsHV-1 timing in WA; NSSP/biotoxin closures; larval set; “oyster abundance”; OA as adult 72 h killer | — | High |
| **Survey / ground truth** | **No** stock assessment. Ground truth = farm mortality logs / PSI / WSG rapid-response surveys. Covariates: NANOOS, NERRS, Ecology, SoundToxins (HAB split). DOH growing areas = **wrong label**. | 1–3 | High |
| **Name** | Accepted *Magallana gigas* (Thunberg, 1793), AphiaID 836033; synonym *C. gigas* 140656 | 1 | High |

### C2 — Chinook × CA/OR charter

| Item | Finding | Tier | Confidence |
|------|---------|------|------------|
| **Recommended target** | Category **D**: 24–48 h relative **encounter likelihood** in an **open** PFMC recreational area. Category C CPUE is the **evaluation metric**, not a promised catch. | — | High |
| **Top 5 covariates** | (1) Open/closed + harvest guideline mask (2) Wind/swell go/no-go (3) Thermal habitat ~8–12°C **with depth** (4) Season/run-timing prior (5) Shelf depth / distance-from-shore | 1–2 | High |
| **Cannot predict** | Catch guarantee; abundance; ESA ESU locations; school waypoints; adult bite from SST/chl/AIS or from JSOES/stoplight | — | High |
| **Survey / ground truth** | PFMC SAFE (annual); CDFW CRFS / harvest trackers (half-month); **ODFW weekly port Chinook + trips** (best public sport CPUE); CWT/GSI stock mix; JSOES = **wrong stage** | 1 | High |
| **Name** | *Oncorhynchus tshawytscha* (Walbaum, 1792), AphiaID 158075 — no material taxonomic disagreement | 1 | High |

### C3 — American lobster × GOM statistical area

| Item | Finding | Tier | Confidence |
|------|---------|------|------------|
| **Recommended target** | Category **C**: next-trip **legal CPUE** and relative effort allocation inside **one** SA (511/512/513) or zone. **Catch ≠ abundance.** | — | High |
| **Top 5 covariates** | (1) **Bottom** temperature (2) Molt phenology prior (3) Depth (4) Soak/bait (operator) (5) Storms/wind; substrate as static map | 1–2 | High |
| **Cannot predict** | Exact abundance; SST/chl as lobsters; next-haul pounds from satellite; settlement this week; moon as proven driver; whale locations | — | High |
| **Survey / ground truth** | **Yes, excellent at seasonal scale:** ASMFC 2025 benchmark; Maine VTS, sea sampling, settlement; MENH inshore trawl; NEFSC BTS; CFRF fleet; eMOLT bottom T. None is next-trip abundance. | 1 | High |
| **Name** | *Homarus americanus* H. Milne Edwards, 1837, AphiaID 156134 — no material disagreement | 1 | High |

---

## 3. Source / license table

Licenses as findable on 2026-09-18. Peer-reviewed papers are **cited, not copied**. No datasets ingested.

| Source | URL | License / access (as findable) | Used for |
|--------|-----|--------------------------------|----------|
| WoRMS *M. gigas* | https://www.marinespecies.org/aphia.php?p=taxdetails&id=836033 | Database citation; images default CC BY-NC-SA (WoRMS about page) | Taxonomy |
| WoRMS *C. gigas* unaccepted | https://www.marinespecies.org/aphia.php?p=taxdetails&id=140656 | Same | Synonym / AphiaID 140656 |
| WoRMS *O. tshawytscha* | https://www.marinespecies.org/aphia.php?p=taxdetails&id=158075 | Same | Taxonomy |
| WoRMS *H. americanus* | https://www.marinespecies.org/aphia.php?p=taxdetails&id=156134 | Same | Taxonomy |
| NOAA Fisheries Pacific oyster | https://www.fisheries.noaa.gov/species/pacific-oyster | U.S. Government work (public domain) | Biology, aquaculture, OA, names |
| NOAA Fisheries Chinook | https://www.fisheries.noaa.gov/species/chinook-salmon | U.S. Government work | Biology, ESA count, management |
| NOAA Fisheries American lobster | https://www.fisheries.noaa.gov/species/american-lobster | U.S. Government work | Biology, habitat, 2025 status, ALWTRP note |
| NOAA ocean salmon | https://www.fisheries.noaa.gov/west-coast/sustainable-fisheries/ocean-salmon-fisheries-west-coast | U.S. Government work | CA/OR ocean fishery frame |
| NOAA NWFSC ocean indicators | https://www.fisheries.noaa.gov/west-coast/science-data/ocean-ecosystem-indicators-pacific-salmon-marine-survival-northern | U.S. Government work | **Wrong timescale** warning |
| WA DOH growing areas | https://doh.wa.gov/community-and-environment/shellfish/growing-areas | State government | Spatial frame; **not** stress label |
| WA DNR aquaculture | https://dnr.wa.gov/aquatics/shellfish/aquaculture | State government | Lease/culture context |
| NANOOS NVS Shellfish Growers | https://nvs.nanoos.org/ShellfishGrowers | IOOS/NANOOS (check use policy before any future access) | Covariate availability |
| SoundToxins | https://soundtoxins.org/about.html | Program pages; journal MDPI CC-BY for 2023 paper | HAB vs harvest split |
| WA Sea Grant Rapid Response | https://waseagrant.uw.edu/our-programs/seafood-fisheries-aquaculture/aquaculture/rapid-response-network/ | University/Sea Grant | 2021 event; grower network |
| WDFW 2019 die-off note | https://wdfw.medium.com/whats-been-causing-mass-shellfish-die-offs-around-puget-sound-1ada7071a242 | WDFW communication | Event evidence (tier 3) |
| FAO cultured *C. gigas* | https://www.fao.org/fishery/docs/CDrom/aquaculture/I1129m/file/en/en_pacificcuppedoyster.htm | FAO (check FAO license for reuse) | Temp/salinity/DO envelopes |
| ASMFC lobster species + 2025 overview | https://asmfc.org/species/american-lobster/ ; https://asmfc.org/wp-content/uploads/2025/11/AmericanLobsterStockAssmtOverview_Oct2025.pdf | ASMFC copyright; official public PDF | Stock status; temperature |
| ASMFC 2025 peer review | https://asmfc.org/wp-content/uploads/2025/11/AmLobsterBenchmarkAssessment_PeerReviewReport_Oct2025_web.pdf | ASMFC copyright | Bottom T vs SST |
| Maine DMR VTS / sea sampling / landings | https://www.maine.gov/dmr/science/species-information/maine-lobster/surveys/ventless-trap-survey | State government | Survey existence |
| eMOLT | https://www.emolt.org/ | Cooperative; OMB control noted on site | Bottom T covariate |
| CFRF lobster fleet | https://www.cfrfoundation.org/jonah-crab-lobster-research-fleet | Nonprofit project pages | Trip-level Category C design |
| DFO LFA 34 2024 | https://publications.gc.ca/collections/collection_2025/mpo-dfo/fs70-7/Fs70-7-2024-040-eng.pdf | Crown copyright / GC publications | Adjacent stock; landings≠biomass |
| PFMC Review of 2025 Ocean Salmon Fisheries | https://www.pcouncil.org/documents/2026/02/review-of-2025-ocean-salmon-fisheries.pdf/ | Council document (NOAA-funded) | SAFE / catch-effort |
| CDFW ocean salmon | https://wildlife.ca.gov/Fishing/Ocean/Regulations/Salmon | State government | Open/closed mask |
| ODFW weekly sport estimates | https://www.dfw.state.or.us/mrp/salmon/docs/Wk_36_2026_Sport_Salmon_Estimates.pdf | State government | CPUE evaluation series |
| Hinke et al. 2005 MEPS 304 | https://doi.org/10.3354/meps304207 | Journal copyright; cite only | Adult thermal habitat |
| Raymond et al. 2022 *Ecology* | https://doi.org/10.1002/ecy.3798 | Ecological Society; cite only | 2021 heatwave |
| Cheney et al. 2000 *J. Shellfish Res.* 19:353–359 | PSI publications list https://www.pacshell.org/publications.asp | Journal copyright; cite only | Puget Sound multi-stressor |
| Mills et al. 2017 *Front. Mar. Sci.* | https://doi.org/10.3389/fmars.2017.00337 | Frontiers (typically CC-BY) | Lobster season timing |
| Hassrick et al. 2016 *Fish. Oceanogr.* | https://onlinelibrary.wiley.com/doi/10.1111/fog.12141 | Wiley copyright; cite only | Juvenile CA–OR (wrong stage for charter) |
| USDA-ARS / OSU PSBC | https://marineresearch.oregonstate.edu/comes/molluscan-broodstock-programusda-ars-pacific-shellfish-breeding-center | U.S. Government / university | OsHV-1, families |

---

## 4. Confidence and limitations of **this dossier**

| Area | Confidence | Limitation |
|------|------------|------------|
| Taxonomy / AphiaIDs | High | *Magallana* remains contested in industry language; dual-label in UI. |
| Target-class assignment (C vs D vs E) | High | Founder could still demand E; scientifically that is a reject. |
| 24–72 h covariate ranking | Medium–high | No new statistical fit was run (ingestion forbidden). Rankings are mechanistic + literature. |
| “Top 5” completeness | Medium | Operator metadata (handling, bait, skill) can outrank ocean layers. |
| Expert names | Medium | Taken from public program pages; incumbents must be re-checked. |
| 2026 in-season salmon details | Medium | CDFW/NOAA closures change within season; do not freeze 18 Sep 2026 rules as biology. |
| License strings | Medium | Some IOOS/FAO/ASMFC reuse terms need a lawyer/data-manager pass before any future download. |

**What this agent did not do:** interview operators; download data; fit models; choose a wedge; design UX; map whales or listed ESUs.

---

## 5. Recommended decision (scientific ranking only)

**Do not lock a wedge in this handoff.**

If a subsequent scoping agent must **rank scientific tractability** for a lawful 24–72 h operator layer that is **not** abundance and **not** harvest authorization:

1. **C1 oyster stress (Category D)** — best mechanism–horizon match; sessile known stock; existing grower-sensor culture; ground truth is scarce but **well-defined**.
2. **C3 lobster next-trip CPUE (Category C)** — best official surveys; must keep catchability vs abundance in the user-facing sentence; needs **bottom T** and effort metadata.
3. **C2 Chinook encounter (Category D)** — valid only as relative risk in **open** water with weather + thermal-habitat-with-depth; highest misuse and ESA risk.

**Bounded geography suggestions (still not locks):** Willapa Bay **or** a named Puget Sound growing-area cluster; **one** ODFW catch area **or** one CDFW PFMC recreational area; **one** of NMFS SA 511/512/513.

---

## 6. Rejected alternatives (do not revive without new evidence)

| Rejected | Why |
|----------|-----|
| Category A Direct Count for any wild mobile candidate at 24–72 h | Not identified at useful resolution |
| Category E SST/chl/AIS as “fish” or “oysters” or “lobsters” | Explicitly forbidden and scientifically false |
| C1 = WA DOH growing-area open/closed or biotoxin | Food-safety / legal harvest; out of wedge |
| C1 adult farm risk = ocean acidification nowcast | Right stage is hatchery larvae (2009), not 72 h market bags |
| C2 = catch guarantee or abundance | Out of wedge; mixed ESA stocks |
| C2 = NWFSC stoplight or JSOES as tomorrow’s bite | Year-scale / juvenile stage |
| C2 river-mouth hotspot maps | Closure + listed-stock risk |
| C3 = exact abundance or stock-assessment biomass next trip | Wrong horizon; CPUE≠N |
| C3 = SNE hypoxia / shell-disease narrative copied into GOM | Different stock |
| C3 moon-phase v1 feature | Tier 4 |
| Spiny lobster, Olympia oyster, coho, “Portuguese oyster” as *gigas* | Wrong taxon |

---

## 7. Follow-ups

1. Operator interviews (see `expert_interview_targets.md`) — 1 grower, 1 charter, 1 lobsterman — **before** any wedge lock.  
2. Confirm *Magallana* vs *Crassostrea* display policy with industry (PCSGA) without changing the accepted name.  
3. License/use-policy pass on NANOOS, eMOLT, SoundToxins, ASMFC PDFs before any future **access** (still no ingestion in this agent).  
4. If C1 proceeds: define a **stress** HAB list vs NSSP list with SoundToxins.  
5. If C2 proceeds: write an ESA mixed-stock ethics note with STT/SWFSC; hard-mask closures.  
6. If C3 proceeds: decide SA vs zone; legal-only CPUE label; bottom-T requirement.  
7. Data-governance agent: farm mortality logs and sea-sampling are **not public microdata**.

---

## 8. Artifacts produced

All under `/Users/wijeratne/dev/fishai/artifacts/marine_domain/`:

- `species_geography_scope.md`
- `variable_relevance_matrix.csv`
- `species_lifecycle_and_seasonality.md`
- `model_limitations.md`
- `expert_interview_targets.md`
- `agent_handoff.md` (this file)

---

## 9. Red-team?

**Yes — scientific red-team of this dossier (not a product teardown).**

| Attack | Response already in dossier? | Residual risk |
|--------|------------------------------|---------------|
| “You ranked C1 first, so the wedge is oysters.” | Ranking is explicitly **not** a lock. | Downstream agent ignores the banner. |
| “NANOOS already shows SST to growers, so SST is oyster health.” | SST listed as proxy; air T × tide and DO required. | UI still ships a red SST blob. |
| “ODFW weekly catch *is* 48 h Chinook.” | Weekly ≠ 48 h; effort-confounded; closed days. | Model trained on weekly tables, sold as tomorrow. |
| “ASMFC has abundance, so next-trip abundance is easy.” | 2025 assessment is stock-scale; catchability covariates exist **because** CPUE≠N. | Marketing quotes “202 million lobsters.” |
| “Chlorophyll predicts salmon in peer review.” | Those papers are mostly **juveniles** and **presence**, not adult charter abundance. | Citation-washing. |
| “Growing-area polygons are the oyster geography.” | Allowed as **frame**, forbidden as **label**. | Food-safety product creep. |
| “Just add AIS.” | AIS = effort; privacy; not abundance. | Fish-finder by another name. |
| “Interview DMR for the good GPS sets.” | Interview rules forbid precise protected-species and confidential set locations. | Someone asks anyway. |

Recommend an independent **red-team agent** before any public claim language. Highest-severity misuse: **C2 ESA maps** and **C3 whale maps**.

---

## 10. Next experiment (no ingestion; paper/public-table protocol)

**Goal:** Test whether each candidate’s **stated target class** is even evaluable with **already public** tables, without building a data lake.

| Experiment | Design | Pass criterion (pre-registered) | Fail / stop |
|------------|--------|----------------------------------|-------------|
| **E1 C1** | Reconstruct 26–28 Jun 2021: predicted intertidal stress = forecast air T + predicted daytime emersion vs documented mortality (Raymond et al. 2022 maps; WSG narrative). Compare to SST-only. | Tide×air ranks affected vs less-affected sites better than SST-only. | If SST-only wins, the D-target is not identified at public grain → do not ship SST. |
| **E2 C2** | Using **ODFW weekly** Chinook / angler-trips for **one** port (e.g. Newport): persistence baseline (last week’s CPUE) vs week-ahead wind/swell + SST. **Do not** claim 48 h if only weekly labels exist. | Report skill honestly; if only weekly labels exist, **C2 48 h is not currently testable** with public data. | That negative result is success of the experiment. |
| **E3 C3** | Using published Mills et al. 2017 **season-start** logic vs DMR monthly landings: confirm seasonal phenology is predictable **and** that this is **not** next-trip CPUE. | Document timescale gap in writing. | If a vendor calls monthly landings “next trip,” fail the claim. |

**Stop rule:** if the only passing “model” is Category E (raw SST/chl), the candidate is **not ready**.

---

## Return block (for parent agent)

**C1 Pacific oyster WA** — Target **D** (24–72 h operational stress/disruption). Top 5: air T × emersion, water T, DO, salinity/runoff, storms (+ culture method). Cannot predict: harvest legality, bag-level mortality without sensors, OsHV-1, abundance. Ground truth: farm/PSI/WSG mortality; NANOOS/NERRS covariates; **not** DOH NSSP.

**C2 Chinook CA/OR** — Target **D** (24–48 h relative encounter in **open** water); evaluate with **C**. Top 5: open/closed mask, wind/swell, 8–12°C thermal habitat with depth, season prior, shelf position. Cannot predict: catch, abundance, ESA locations, bite from chl/SST/AIS/JSOES. Ground truth: ODFW weekly port CPUE; CDFW CRFS; PFMC SAFE (context).

**C3 Lobster GOM** — Target **C** (next-trip legal CPUE / allocation); **not** abundance. Top 5: bottom T, molt prior, depth, soak/bait, storms (+ substrate static). Cannot predict: N, SST-as-lobsters, moon, whales. Ground truth: DMR VTS/sea sampling (seasonal), ASMFC 2025, eMOLT/CFRF for T and trip CPUE design.
