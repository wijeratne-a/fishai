# Partner network design — Global Saltwater Life Observatory

**Status:** DESIGN, NOT AN EXECUTED PROGRAM  
**Date:** 2026-09-18  
**HUMAN LEGAL REVIEW REQUIRED** before any DUA/DPA, payment, or ingest.  
**No partners are signed. No data are collected.**

The network exists to improve **evidence-typed** estimates **for contributors and licensed researchers** without turning livelihoods, nests, or vessels into a public map.

Companion: `data_rights_register.md`, `sensitive_location_policy.md`. Commercial-wedge analogues (do not overwrite): `artifacts/data_rights_and_privacy/partner_data_rights_template.md`, `artifacts/product_and_monetization/partner_data_program.md`.

---

## 0. Defaults that do not wait for counsel’s prose

| Default | Rule |
|---|---|
| Exact productive spots, nests, aggregations, haul-outs, PAM bearings | `PRIVATE` / `NEVER_PUBLISH` |
| Farm performance, disease, genetics | `PRIVATE` / `NEVER_PUBLISH` publicly |
| Vessel identity and routes | `PRIVATE` / `NEVER_PUBLISH` publicly |
| Shared research file | Spatially coarsened, temporally delayed, opt-in, written method |
| Public heatmaps of catch, yield, or wildlife | **Forbidden** |
| GFW / AIS as abundance | **Forbidden** |
| Cash-per-rare-taxon or public rare-species leaderboards | **Forbidden** (incentivizes disturbance) |
| Hardware mandate | **Forbidden** until partner-first ladder fails |
| Indigenous nations | Not “partners” under this DPA; nation-drafted CARE protocol only |
| Training-use | Account-only until explicit opt-in and unwind is technically possible |

---

## 1. Partner classes

| Class | Who | What they may contribute | What they must never be asked for by default |
|---|---|---|---|
| **Vessel / fishing operator** | Commercial, charter, small-scale, research ships | Effort-normalized catch/absence, coarsened area, sensor streams they own | Trap/set GPS; other vessels’ patterns; passenger manifests |
| **Aquaculture farm** | Marine/brackish farms, hatcheries | Sensors, husbandry timing, mortality **private** | Public lease performance; neighbor farms; harvest legality |
| **Researcher / PI** | Universities, government labs, NGOs with permits | Embargoed telemetry, PAM, eDNA, surveys under their permits | Hidden iNat coords; another PI’s embargoed tracks |
| **Sensor operator** | Glider/HF-radar/hydrophone/camera networks, IOOS-class RAs | QC’d physics and acoustic **summary** products they are licensed to share | Array geometry that localizes listed callers; install GPS if it enables harassment |
| **Citizen scientist** | Individual observers, clubs, iNat/eBird-class users | Presence of **non-sensitive** taxa at **already-public** grain | True coords of obscured taxa; real-time whale pins |
| **Indigenous nation / tribal government** | Rights holders | Only under **their** protocol | Nothing via this template |
| **Buyer / processor** (if ever) | Dealers | Siloed tickets | Cross-firm prices; supplier maps |

A single organization may wear two hats (a farm that is also a dealer; a PI who operates hydrophones). Apply the **stricter** class rules.

---

## 2. Why they would participate (incentives)

Incentives must not buy disturbance, fabricated rares, or leaked spots.

| Class | Primary incentive | Secondary | Do not use |
|---|---|---|---|
| Vessel | Private brief / logbook that uses **their** zeros; data-contribution credits | Coauthorship on delayed coarsened papers; reduced seat price | Public highliner rank; cash per shark |
| Farm | Lease-level ops-risk / environment brief; private calibration | Association delayed benchmark (opt-in) | Public mortality leaderboard |
| Researcher | Compute, QC, citation, DOI of coarsened products; embargo respected | Reciprocal access to **non-sensitive** physics | Scooping; publishing their tracks |
| Sensor operator | Attribution, QARTOD-style quality visibility, joint proposals | Hardware support only with a separate memo | Unlicensed redistribution |
| Citizen scientist | Better ID tools, personal life-list **private**, contribution badge **without coordinates** | Club-level delayed summaries | Gamified rare pins; paid bounties on CR/EN |
| Nation | Control, benefit-sharing, capacity — **defined by them** | — | Extractive “consultation” |

**Product-gated credits beat cash-for-rows.** Paying per log buys rushed taps; paying per listed species buys harassment.

---

## 3. Trust, verification, and certification

### 3.1 Trust ladder (every account)

| Level | Meaning | What they can write | What they can read |
|---|---|---|---|
| L0 Unverified | Email only | Nothing that touches the twin | Public physics only |
| L1 Identity-verified | Org/vessel/farm/permit check | `PRIVATE` rows scoped to self | Own rows + public |
| L2 Protocol-certified | Documented method, units, QC | Eligible for cohort training if opted in | Own + agreed coarsened cohort |
| L3 Reputation-stable | Time-in-network, low dispute rate, audit samples | May mentor / sign other L1s | Same, plus named research collaborations |
| LX Revoked | Harm, fraud, or legal breach | None | Export of **their** remaining allowed copy only |

Indigenous nations skip this ladder; their protocol supersedes.

### 3.2 Verification by class

| Class | Identity | Authority to share | Method |
|---|---|---|---|
| Vessel | Registry / permit / owner affidavit | Owner, not a deckhand click-wrap for GPS | Permit number stored hashed; names in partner table only |
| Farm | Lease/concession id | Operator with authority | Lease polygons stay `PRIVATE` |
| Researcher | Institutional email + permit/IACUC/MMPA/ESA authorization as applicable | PI of the study | Embargo dates in metadata |
| Sensor operator | Organization + station list | Licence to redistribute each stream | Per-dataset licence field |
| Citizen scientist | Account; optional club | Observer owns the observation | **No** path to hidden iNat coords |

### 3.3 Certification (methods, not marketing badges)

- Sensors: IOOS QARTOD / equivalent QC flags required on streams used as twin inputs.  
- Catch: effort definition (haul, soak, hooks, hours) mandatory; landings without effort cannot enter CPUE-class features.  
- PAM: detection software version, duty cycle, and **no public localization**.  
- eDNA: primer/assay, blank controls, lab id; rare positives auto-tier `NEVER_PUBLISH` GPS.  
- Citizen science: research-grade analogue (multi-agree ID) still does **not** relax geoprivacy.

Certification can be revoked independently of the legal DPA.

---

## 4. Provenance

Every contributed observation carries:

- `partner_id` (opaque), `contributor_class`, `dua_version`  
- `source_record_id`, `observed_at_utc`, `privacy_tier`, `embargo_until`  
- `method_id` / protocol hash  
- `licence_class` (never inferred from “it was emailed”)  
- `sensitive_flag` (taxon, place type, reviewer)  
- W3C PROV-style derivation: raw → coarsened → public-safe  

Public derivatives must cite datasets/DOIs **without** naming vessels, farms, or observers. Internal lineage must be able to **delete/return** a partner’s raw rows without leaving GPS in notebooks.

**No** anonymous S3 listing. **No** embeddings of coordinate strings (commercial geospatial model already forbids vector search in v1; observatory follows).

---

## 5. Anti-gaming and abuse

Assume some users will optimize the metric.

| Attack | Why it happens | Mitigation |
|---|---|---|
| Fake rare-species pins | Status, bounties, vandalism | No public rare map; no cash-per-taxon; multi-source corroboration before even `RESTRICTED` use |
| Location spoof / GPS jitter | Hide spots or invent effort | Device integrity optional later; v1: flag impossible speeds/teleports; do not “correct” toward known aggregations |
| Duplicate / copy-paste logs | Credits for completeness | Hash rows; uniqueness on vessel-day-effort |
| Screenshot of another captain’s plotter | Theft | ToS; reject images with foreign MMSI/UI; human audit sample |
| Effort inflation | Better “CPUE” | Require zeros; compare to weather/workability; partner-private only |
| Sensor-on-the-aggregation | “Help science” while fishing a spawn | Protocol forbids targeting known aggregations; ecological review of station placement |
| Deanonymize iNat/Movebank | Curiosity / scoop | Technical ban on `private_latitude`; ToS; revocation |
| Mosaic with AIS | Rebuild tracks | No public AIS identity; tests in `sensitive_location_policy.md` §8 |
| Retaliation dumps | Dispute | Revocation + legal hold; do not publish “evidence” maps |

**Citizen science special:** treat sudden clusters of CR/EN marine taxa as **incident candidates**, not as a product feature.

---

## 6. Ecological safeguards (network-level)

1. **No viewing guide.** The network must not tell the public where to find whales, turtles, or spawners.  
2. **No live wildlife.** Partner apps may show **their own** vessel and farm; they may not show others’ biological pins.  
3. **Seasonal shutoff.** Nesting/pupping/spawning windows: even L2 partners do not receive **other** partners’ nearby sensitive events.  
4. **Hydrophone/camera placement.** New devices near listed mammal habitat or turtle beaches need ecological review, not just an RF licence.  
5. **Research permits.** PIs warrant MMPA/ESA/CITES/wildlife-permit coverage for telemetry and close approach. The observatory does not supply that permit.  
6. **CARE.** Nations can refuse, limit, or embargo; the stack must technically support withhold-by-polygon and withhold-by-taxon.  
7. **Harm incident** (`sensitive_location_policy.md` §14) suspends the contributing feed and the public layer involved.

---

## 7. Reputation

Reputation is **operational**, not a social score:

- Completeness of required fields (including zeros)  
- QC flag rates  
- Dispute/incident count  
- Timely embargo respect  
- Revocation history  

Use it to gate L2/L3 and cohort training — **not** as a public ranking of fishers or farms. Public leaderboards of catch or rare finds are an ecological and commercial hazard.

---

## 8. Revocation

| Trigger | Speed | Company actions |
|---|---|---|
| Ordinary withdrawal | `[30]` days (template) | Stop ingest; disable features; delete/return raw within `[45]` days except minimized legal logs |
| Privacy/purpose breach by Company | Immediate (partner may revoke) | Same + incident record |
| Ecological harm, poaching facilitation, harassment, fraud | Immediate | Freeze public layer; preserve forensic copy; notify counsel and, if a nation, the nation |
| Licence contamination (NC/GFW/IUCN spatial mixed in) | Immediate for that source | Quarantine; do not “clean” by hoping |

**Training unwind:** if cohort/foundation training was on, Annex must specify retrain or suppress. **If unwind is impossible, that training-use must not be offered.** Forecasts already delivered are not rewritten; future jobs drop the partner’s `PRIVATE` rows.

Survival: confidentiality, non-publication of microdata, CARE obligations.

---

## 9. Role-specific programs (v0 design)

### 9.1 Vessels

- **Receive:** private logbook; coarsened-range outlook; completeness credits.  
- **Give:** catch/absence + effort + **coarsened** area (exact GPS optional, default off, `NEVER_PUBLISH` if on).  
- **Ban:** public CPUE heatmaps; AIS overlay on catch; recommending unfished cells as waypoints.

### 9.2 Farms

- **Receive:** lease-level environmental/ops context; official sanitation **links**, not a harvest stamp.  
- **Give:** sensors and outcomes they choose.  
- **Ban:** cross-farm KPI maps; disease attribution; scraping concession viewers as open APIs.

### 9.3 Researchers

- **Receive:** physics store, QC, citation plumbing, embargo clocks.  
- **Give:** studies with Movebank-class sharing levels mapped to observatory tiers.  
- **Ban:** silent republish of restricted tracks; using the observatory to bypass a journal embargo **or** a conservation embargo.

### 9.4 Sensor operators

- **Receive:** attribution, joint grant text, quality dashboard.  
- **Give:** licensed streams only.  
- **Ban:** public live hydrophones on listed callers; documenting array layout in public repos.

### 9.5 Citizen science

- **Receive:** ID assistance; private personal map.  
- **Give:** non-sensitive observations at public grain.  
- **Ban:** uploading obscured-species true coords; contests; scraping iNat hidden fields.

Ingest path for iNat-class data, if ever: official API, licence filter, **honor geoprivacy**, then still apply observatory §5 taxon defaults (an open LC observation of a grouper **on a known spawn night** is still `NEVER_PUBLISH` at native grain).

---

## 10. Agreement stack

| Instrument | Use |
|---|---|
| Observatory DPA (counsel-drafted from the commercial template, extended to PI/sensor/citizen classes) | Ordinary partners |
| Nation protocol (CARE, Local Contexts) | Indigenous data |
| Data-use addendum for training-use (1 account-only / 2 cohort / 3 foundation) | Explicit choice; silence = 1 |
| Subprocessor list | Annex |
| Research permit warranty | PIs |
| Click-wrap ToS | **Insufficient** for GPS logs, PAM, or eDNA |

Commercial template path: `/Users/wijeratne/dev/fishai/artifacts/data_rights_and_privacy/partner_data_rights_template.md` — copy concepts, **do not overwrite**.

---

## 11. Partner-first data ladder (no hardware heroics)

1. Open/public licensed physics and official designations (context).  
2. Agency public aggregates.  
3. Partner exports of existing loggers and spreadsheets.  
4. Existing boat/farm/research sensors.  
5. Manual structured observations under DPA.  
6. Low-cost capture (photo) with EXIF stripped of sensitive GPS.  
7. Logbook / Movebank / ERDDAP integrations with licence fields.  
8. Licensed commercial data (AIS etc.) only if counsel + harm review.  
9. Proprietary hardware **only** with a separate approval memo (payback, burden, privacy, certification, ecological placement).

---

## 12. Anti-goals

- A global public contributor map.  
- Paying for listed-species coordinates.  
- Using citizen science to un-generalize GBIF/OBIS.  
- Association deals that force members to share exact spots to get the paid tier (individual `PRIVATE` must remain available).  
- “Anonymized” cells that re-identify a single farm, beach, or vessel.

---

## 13. Ready vs blocked

**May design now:** DPA extensions, trust ladder, provenance fields, anti-gaming tests on **synthetic** data.

**Blocked until counsel + ecological-harm review:** any real partner ingest; any public biological layer; GFW/AIS identity; hidden citizen-science coordinates; nation data without a nation protocol.
