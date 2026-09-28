# Agent Handoff — SCIENTIFIC_RED_TEAM_AGENT

**Date:** 2026-09-18  
**From:** SCIENTIFIC_RED_TEAM_AGENT  
**To:** REQUIREMENTS_AND_WEDGE, MARINE_DOMAIN, DATA_DISCOVERY, DATA_RIGHTS, GEOSPATIAL, QUALITY_AND_VALIDATION, PRODUCT_AND_MONETIZATION, founder  
**Write scope:** `/Users/wijeratne/dev/fishai/artifacts/scientific_red_team/` only  
**10-part handoff** as specified for specialist agents.

---

## 1. Executive finding

No model may go customer-facing. First pass falsified the **planned product class**; second pass audited sibling files (marine domain, quality, product, requirements, rights, geo). `data_discovery/` was still empty. Siblings generally agree on Category C/D and oyster-first, but **do not clear** blockers. New HIGH items: quality **SST ≥ 19 °C** expert rule; product **Totten / top 20% / +1.8 °C** sample brief.

**Highest-severity risks per wedge**

| Wedge | Highest-severity risks |
|---|---|
| **Oyster × WA × 72h** | **BLOCKER:** food-safety / harvest-legality contamination (WAC 246-282-006 already turns temperature into harvest prohibition). **HIGH:** SST ≠ intertidal body temperature (2021 event was atmospheric heat + midday emersion); 72h ≠ 30-day delayed mortality; closures are the wrong label. |
| **Chinook × CA/OR × 24–48h** | **BLOCKER:** 24–48h habitat encounter is not identified by the literature (SST links are seasonal/stock-scale). Catch ≠ abundance ≠ guarantee. Closed-cell scoring and ESA stock-mix / effort-concentration. |
| **Lobster × GOM × CPUE** | **BLOCKER:** AIS/trackers ≠ abundance and are mostly missing or confidential. Public CPUE maps leak locations. **HIGH:** hyperstability and temperature-dependent catchability; reporting-protocol breaks (10% → 100% in 2023). |

**Scientifically safest wedge to pilot:** Pacific oyster operational-stress **private farm brief** (Category D), DOH status as a **separate non-model feed**, air+tide+solar+wave not SST-only, partner labels. Still **NO-GO** until blockers and a human shellfish + NSSP reviewer.

**Least safe:** public Chinook 24–48h encounter heatmap.

**Conditional second:** private lobster Category C CPUE rank on an operator’s **own** strings; never public heatmaps or AIS.

This agent is **not** the qualified human domain reviewer. HIGH/BLOCKER items stay open until a named human signs.

---

## 2. Evidence table

| Claim / question | Finding | Evidence | Tier | Implication |
|---|---|---|---|---|
| Can SST forecast WA oyster 72h mortality? | Falsified as a sufficient mechanism | Raymond et al. 2022; Miner et al. 2025: 2021 AHW, midday emersion, solar; Hesketh & Harley 2023: air ≠ body T | 1 (field) vs 3 (SST) | SST-only product is Low/None confidence |
| Is 72h a mortality horizon? | Incomplete | George et al.: mortality to day 30; triploid > diploid | 1 lab | Indicator ≠ % dead |
| Will ops language stay non-legal? | Unstable without hard UI split | WAC 246-282-006; WA DOH 2026 Vp categories; NSSP | Regulatory | Combined score = shadow food-safety model |
| Do HAB networks replace DOH? | No | SoundToxins/ORHAB warn; reopen needs tissue tests | 1 lab vs 2 ops | Never predict “safe” |
| Can 24–48h env fields predict Chinook encounter? | Not supported | Shelton et al. 2021 seasonal SST; Satterthwaite contact-rate = area/month/effort | 2–3, wrong scale | Habitat SDM is a blocker |
| Is recreational CPUE abundance? | No | Bag limits truncate; CRFS sampling fraction; in-season closures | 2 | Category C rank only |
| Are public salmon data 48h labels? | No | Monthly CPFV logs; RecFIN CTE001 excludes salmon; PR1 20–25% of days | 2 lagged | Need partner trips |
| Is AIS lobster abundance? | No | 33 CFR 164.46 ≥65 ft; Addendum XXIX federal-permit confidential subset | 3 selected | Forbidden feature for public product |
| Is GOM CPUE abundance? | No | ASMFC 2025 peer review hyperstability; Harley 2001; Watson 2019 saturation; Zhang 2025 bottom T catchability | 1–2 | Category C + catchability text |
| Is Maine CPUE a continuous index? | No | Hodgdon 2025 protocol changes 2008–2023 | 2 | Do not splice regimes |
| Random CV valid? | No | Roberts et al. 2017 spatial blocking | Method | Blocker until protocol exists |
| HiveClaw locks species? | No | HiveClaw = local inference/causal runtime | n/a | Wedge remains UNRESOLVED |
| Is SST ≥ 19 °C a valid WA oyster 72h alert? | Falsified | Growth/clearance band; 2021 kill was air×emersion; Hobday MHW ≠ AHW | 1 vs 3 | Rewrite Quality B4 (RT-SIB-01) |
| Does a Totten “ELEVATED + water temp” sample stay non-legal? | Unstable | Totten is 2026 Vp Category 3 | Regulatory | Replace sample brief (RT-SIB-02) |

---

## 3. Source / license table

This agent **did not ingest** datasets. URLs were used as scientific counter-evidence (accessed 2026-09-18). Commercial reuse of the underlying data is **not** approved here; DATA_RIGHTS owns license class.

| Source | URL / ID | Use in this review | License note |
|---|---|---|---|
| Raymond et al. 2022 *Ecology* | https://doi.org/10.1002/ecy.3798 | Oyster AHW mechanism | Paper citation; not a training corpus |
| George et al. 2023/24 | https://doi.org/10.1101/2023.03.02.530828 ; NOAA repo | Delayed mortality, ploidy | Citation only |
| WA DOH Vp plan / categories / closures | https://doh.wa.gov/community-and-environment/shellfish/commercial-shellfish/vibrio-control-plan ; WAC 246-282-006 | Legal wall | Official; display with attribution, not as labels |
| NSSP 2023 | FDA | Sanitation authority | Official |
| SoundToxins | https://www.mdpi.com/2072-6651/15/3/189 | HAB ≠ toxin result | Citation |
| Satterthwaite et al. 2015/2018 | *Fish. Res.* DOIs | Chinook CPUE ≠ 48h SDM | Citation |
| Shelton et al. 2021 | https://doi.org/10.1111/faf.12530 | SST scale mismatch | Citation |
| PFMC / NMFS 2026 salmon measures | pcouncil.org ; Federal Register | Closure mask | Official |
| CDFW CRFS | wildlife.ca.gov/Conservation/Marine/CRFS | Label lag | Official; salmon via OSP |
| Harley et al. 2001 | *CJFAS* | Hyperstability | Citation |
| Watson et al. 2019 | *Fish. Bull.* 117(3) | Trap saturation | Citation |
| Hodgdon et al. 2025 | https://doi.org/10.1093/icesjms/fsaf097 | Reporting bias | Citation |
| ASMFC 2025 lobster assessment / peer review | asmfc.org | CPUE ≠ abundance | Official assessment |
| Zhang et al. 2025 | Copernicus Ocean State Report | Bottom T catchability | Citation |
| 33 CFR 164.46 | eCFR | AIS carriage | Law |
| ASMFC Addendum XXIX / ME DMR trackers | asmfc.org ; maine.gov/dmr | Confidential effort | HUMAN LEGAL REVIEW before any use |
| Roberts et al. 2017 *Ecography* | spatial CV | Method | Citation |

**Do not train on** Addendum XXIX tracks, AIS microdata, farm yields, or exact catch locations.

---

## 4. Confidence / limitations of this red team

| Item | Confidence | Limitation |
|---|---|---|
| Failure modes (proxy, leakage, legality contamination) | **High** | Mechanisms are documented; no FishAI metrics to audit |
| Which private MVP will beat a baseline | **Low–medium** | No partner data in hand |
| Sibling-agent claim audit | **None yet** | Directories empty of files; **re-review required** |
| Legal conclusions | **Not legal advice** | HUMAN LEGAL REVIEW for trackers, logbooks, DOH republication |
| Taxonomy | Common names + binomials as in the prompt | MARINE_DOMAIN owns WoRMS/Aphia lock |
| This agent as domain sign-off | **Invalid** | Explicitly not a human reviewer |

---

## 5. Recommended decision

1. **Founder:** lock **at most one** wedge. Scientific recommendation for a **bounded private pilot:** oyster 72h ops-stress indicator.  
2. **Product:** implement `prediction_contract.md` before any mock UI that includes a map or score.  
3. **Validation:** write protocols that can **fail** the model (2021 AHW holdout; year-block; persistence baseline).  
4. **Rights:** default-deny AIS/trackers/exact spots.  
5. **All agents:** do not train; do not upgrade Category D to abundance or legality.  
6. **Humans required before any customer brief:** shellfish + NSSP (oyster), and/or salmon + ESA (Chinook), and/or lobster + confidentiality (GOM).

---

## 6. Rejected alternatives

| Alternative | Why rejected |
|---|---|
| Public “where is the fish” heatmap (any species) | False precision, effort confounding, location leakage |
| 24–48h Chinook SDM from SST/chlorophyll | Scale mismatch; unidentifiable; ESA risk |
| AIS-based lobster abundance or public CPUE map | Proxy false; coverage false; privacy BLOCKER |
| Oyster “harvest window” or closure-probability product | Shadow food-safety model; NSSP/DOH only |
| Using official closures as ops-stress labels | Wrong process, wrong lag, contaminates the wall |
| Random-split ML leaderboard as go-to-market evidence | Spatial/temporal leakage |
| Disclaimer under a red/green go-fish map | Does not bound the claim |
| “AI / HiveClaw will figure it out” | Unrelated stack; master prompt rule 8 |
| Shipping all three wedges | Mixes labels; violates one-decision MVP |

---

## 7. Follow-ups

- **Done (second pass):** audited marine_domain, quality_and_validation, product_and_monetization, requirements_and_wedge, data_rights, geospatial. New IDs RT-SIB-01…07. Highest new issues: **19 °C SST expert rule** and **Totten/top-20%/+1.8 °C sample brief**. `data_discovery/` still empty — audit when it lands.  
- Bind label dictionaries before feature stores.  
- Founder names human reviewers.  
- If oyster locked: design partner DUA + sensor/tide rule v0.  
- If lobster locked: effort dictionary + private log schema; legal memo on trackers.  
- If Chinook locked: drop 48h habitat goal; partner CPUE rank only.  
- Stop-ship if sales copy uses never-claims.

---

## 8. Artifacts produced

All under `/Users/wijeratne/dev/fishai/artifacts/scientific_red_team/`:

| File | Role |
|---|---|
| `red_team_report.md` | Full falsification narrative |
| `scientific_red_team_report.md` | Same report (required alias/copy) |
| `model_claims_risk_register.md` | Claim IDs, severity, tests |
| `deployment_blockers.md` | No-go list and clearance evidence |
| `remediation_plan.md` | Phased smallest fixes |
| `prediction_contract.md` | Safe language + never-claims |
| `agent_handoff.md` | This file |

---

## 9. Residual red-team / reviewer questions

Items a **human** must still attack (this pass cannot close them):

- Is a 72h oyster **rule** (tide × air) even needed, vs a checklist farmers already run?  
- Minimum n of leases/trips for blocked CV?  
- Public-health reviewer: is *any* temperature “stress” display too close to Vp controls?  
- Salmon reviewer: does a private CPUE rank still concentrate effort on listed stocks?  
- Lobster confidentiality: is statistical-area rank still too fine inshore?  
- After sibling reports land: did anyone propose closure-risk, abundance percentile, or AIS features?

---

## 10. Next experiment (smallest falsifying test)

**Do not train a neural model.**

**If oyster (preferred):** On one consenting lease, issue a **pre-registered 72h rule** (daylight emersion ∩ forecast air/heat index ∩ waves) for 30–60 days **including** at least one spring-tide heat period if season allows. Score workability and protocol mortality vs (a) persistence, (b) SST-only rule. Success = ops indicator has lead time without users treating it as DOH. Failure of SST-only vs air+tide = confirms RT-OYS-02.

**If lobster:** On one operator, rank next-haul CPUE vs that operator’s persistence and month×zone mean using **only their logs + bottom T**. If env model cannot beat persistence, do not ship “AI CPUE.”

**If Chinook:** On one charter, compare month×area climatology vs any 48h SST model on held-out year. Predicted result: climatology wins or ties. If SST “wins,” audit leakage.

**Stop condition:** any experiment that needs public hotspots, AIS labels, or closure labels.

---

**Handoff complete.** Parent return payload: highest-severity risks per wedge (table in §1); safest pilot = private oyster ops-stress with food-safety wall; all wedges blocked for customer-facing deployment; required limitation language in `prediction_contract.md`.
