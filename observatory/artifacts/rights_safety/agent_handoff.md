# Agent handoff — DATA_RIGHTS_PRIVACY_AND_ECOLOGICAL_SAFETY + SENSITIVE_SPECIES_AND_LOCATION_PROTECTION

**Program:** Global Saltwater Life Observatory  
**Agents:** DATA_RIGHTS_PRIVACY_AND_ECOLOGICAL_SAFETY_AGENT + SENSITIVE_SPECIES_AND_LOCATION_PROTECTION_AGENT  
**Date:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/`  
**Ingest:** none. **Counsel:** none. This is not legal advice.

Commercial-wedge files under `/Users/wijeratne/dev/fishai/artifacts/data_rights_and_privacy/` were **read and extended, not overwritten**.

---

## 1. Executive finding

**A global public map of saltwater life is unsafe as v1 and is rejected.** Global observation does not justify exposing sensitive data. Public v1, if anything, is environmental context, official designation **links**, taxonomy, and evidence-type legends — not an animal atlas.

None of the new global families (IUCN spatial, Movebank tracks, PAM localization, rare eDNA, GFW, hidden iNat coords, farm/vessel microdata, TEK) is ingestible in this iteration. Physics families already classed `APPROVED_*` in the commercial register remain catalog-only.

The observatory adds a first-class **`DELAYED`** tier and a mandatory **ecological-harm review** before any `PUBLIC` biological layer. Open licences are not a publish button.

**Highest risks:** (1) nesting beaches, spawning aggregations, nurseries; (2) marine-mammal telemetry and acoustic localization (MMPA/ESA harassment); (3) CITES/IUCN-triggered trafficking targets (turtles, sawfish, reef sharks, remnant invertebrates); (4) GFW/AIS identity and private fishing grounds; (5) CARE/Indigenous data; (6) farm performance and unpublished PI sites; (7) IUCN spatial **non-commercial** terms and GFW CC BY-NC contaminating a dual-use stack with FishAI.

---

## 2. Default publish rules by taxon class

Public-product defaults. Internal stores may be finer under ACL. Life-history overrides taxonomy (an LC snapper on a spawn site follows the aggregation row). Full table: `sensitive_location_policy.md` §5.

| Class | Public default |
|---|---|
| Mysticetes / odontocetes (incl. NARW) | `NEVER_PUBLISH` native, telemetry, PAM localization. Link official Slow Zones only. Optional delayed 1°/basin historical presence after review. |
| Pinniped/sirenian haul-outs and pupping | `NEVER_PUBLISH` site GPS |
| Sea turtle nests, beaches, internesting, emergence nights | `NEVER_PUBLISH` |
| Sea turtle foraging/migration tracks | Raw `NEVER_PUBLISH`; coarsened + `DELAYED` ≥1 year if ever public |
| Sawfish, rhino rays, angel sharks | `NEVER_PUBLISH` fine occurrence |
| Shark/ray aggregations, nurseries, pupping | `NEVER_PUBLISH` |
| Pelagic sharks in RFMO fisheries | RFMO published grain only; tags private/`DELAYED` |
| Spawning aggregations (grouper, snapper, etc.) | `NEVER_PUBLISH` GPS/timing/choruses |
| Listed salmonids; holding pools / mouths at spawn | `NEVER_PUBLISH`; official critical habitat only |
| Seahorses, Napoleon wrasse, other listed/endemic fishes | `NEVER_PUBLISH` fine |
| LC pelagics with public RFMO/FAO tables | `COARSENED` at **published** area×year grain — not a CPUE heatmap |
| High-value trafficking taxa (totoaba-class, remnant sturgeon/eel sites) | `NEVER_PUBLISH` |
| Seabird colonies in season | `NEVER_PUBLISH` colony GPS |
| Abalone, conch, giant clam, holothurians, precious coral, lobster hotspots | Remaining beds `NEVER_PUBLISH` |
| Rare coral thickets not on official maps | `NEVER_PUBLISH` |
| Common plankton/microbial eDNA | `COARSENED` survey grid |
| Rare/listed eDNA positives | `NEVER_PUBLISH` sample GPS |
| Aquaculture on private leases | Performance `PRIVATE`; attributed disease `NEVER_PUBLISH` |
| Environmental fields (SST, oxygen, GEBCO) | `PUBLIC` if licensed; fusion inherits biological tier; not navigation |

---

## 3. `NEVER_PUBLISH` classes

Absolute for public products, marketing, open evals, and shared weights (`sensitive_location_policy.md` §6):

1. Nesting beaches, crawls, nest GPS, hatchling-emergence nights  
2. Rookeries, haul-outs, calving/pupping grounds, natal-stream holding pools  
3. Active spawning-aggregation coordinates, depths, timing, and fishing choruses  
4. Nursery / internesting / pupping grounds at capture resolution  
5. Raw tracks of turtles, marine mammals, sawfish, aggregation sharks; tracks that back-solve a nest  
6. Acoustic localization/bearings/TDOA on marine mammals; raw audio that enables it  
7. Rare/listed/aggregation eDNA at native sample coordinates  
8. Unpublished remnant invertebrate and precious-coral beds  
9. VMS; live AIS identity; highliner/competitor routes  
10. Private fishing grounds, trap GPS, charter waypoints, lease corners  
11. Farm KPIs, disease, genetics, yield, buyer prices  
12. Indigenous TEK, treaty targeting layers, unconsented nation data  
13. Unpublished proprietary survey GPS  
14. User/crew/citizen-scientist identity joined to sites  
15. Security-sensitive marine infrastructure as a targeting layer  
16. iNaturalist/eBird **true** coordinates when obscured/private  
17. CITES Appendix I (and high-risk II) wild-population pinpoints  
18. Mosaic products that recover any class above with AIS/charts/iNat  

---

## 4. Is a global public map unsafe as v1?

**Yes. Unsafe. Rejected.**

Mixed-taxon canvases leak the strictest class through the loosest layer; nesting/spawning/NARW/sawfish are exactly what such a map advertises; IUCN spatial and GFW are non-commercial; scientific red team already blocks public fine biological maps; harm-review and revocation are not built; AIS fusion becomes surveillance; a world map will infer TEK unless the default is withhold.

**Allowed v1 public design (still no ingest):** physics/chemistry; bathymetry-as-habitat with not-for-nav notice; taxonomy; evidence-type legend; official designation links; optional **non-biological** sensor-coverage map. Partner biology stays behind ACL. Any later public biology: **one taxon class × coarsened × delayed × harm-reviewed**, never a global animal atlas.

---

## 5. Evidence table (new global families)

| Finding | Evidence | Confidence |
|---|---|---|
| OBIS requires FAIR+CARE; providers must generalize for species/habitat protection and national security before publish; observatory must not undo | https://manual.obis.org/policy.html §§3,7 fetched 2026-09-18 | High on posted text |
| GBIF sensitive practice: Cat 1 withhold/1°; Cat 2 0.1°; Cat 3 0.01°; Cat 4 0.001°; threatened list is a trigger not a pin | https://docs.gbif.org/sensitive-species-best-practices/master/en/ (Chapman 2020) | High |
| IUCN Red List **spatial** downloads non-commercial; commercial → IBAT; category names separately queryable | https://www.iucnredlist.org/resources/spatial-data-download ; summary terms | High on posted terms |
| Movebank rolling embargo 30d–3y and static embargo up to 10y exist to hide current animal locations; public CC0/BY/BY-NC | https://www.movebank.org/cms/movebank-content/permissions-and-sharing | High |
| iNat obscured = random point in 0.2°×0.2° cell; NT–EX default obscured; do not access private lat/lon | https://www.inaturalist.org/pages/geoprivacy ; help articles | High |
| Official NARW Slow Zones / PACM are agency products; observatory-derived PAM localization is not those products | NOAA WhaleMap / PACM pages | High (role distinction) |
| GFW CC BY-NC; no public commercial licence; scraping banned | Commercial register 2026-09-18 | High |
| CARE complements FAIR; open science ≠ Indigenous consent | https://www.gida-global.org/careprinciples | High as ethics/policy; legal form nation-specific |
| ESA §9 / MMPA harassment / CITES appendices are take/trade/harassment regimes, not observatory permits | Policy-level only | High that **HUMAN LEGAL REVIEW** is required; this agent is not counsel |
| Commercial red team: public fine biological maps are BLOCKER | `artifacts/scientific_red_team/deployment_blockers.md` B-ALL-06 | High as internal program constraint |

---

## 6. Source / licence summary (observatory add-on)

Full narrative: `data_rights_register.md`. Inherit CMEMS/Sentinel/NOAA/NASA/GEBCO/WoRMS/MSA/GFW from the commercial register.

| Family | Status class | Privacy default |
|---|---|---|
| OBIS/GBIF CC0–CC BY | `APPROVED_WITH_ATTRIBUTION` | `COARSENED` / `DELAYED` / `NEVER_PUBLISH` by taxon |
| OBIS/GBIF NC | `NONCOMMERCIAL_ONLY` | same |
| OBIS-SEAMAP | `CONDITIONAL_REVIEW_REQUIRED` | `RESTRICTED` / `NEVER_PUBLISH` |
| IUCN spatial / IBAT | `NONCOMMERCIAL_ONLY` / `PAID_LICENSE_REQUIRED` | `COARSENED` if ever licensed |
| IUCN category labels (query/display) | `APPROVED_WITH_ATTRIBUTION` pending counsel | n/a (not a map) |
| CITES trade database | `CONDITIONAL_REVIEW_REQUIRED` | not a wild GPS layer |
| ESA/MMPA precise occurrence | `RESTRICTED` | `NEVER_PUBLISH` |
| Official critical habitat / Slow Zones | `APPROVED_OPEN_COMMERCIAL` as **published** | `PUBLIC` at official grain only |
| Movebank public embargoed CC0/BY | `APPROVED_WITH_ATTRIBUTION` of released portion | still `DELAYED`+`COARSENED` or `NEVER_PUBLISH` |
| Movebank restricted | `APPROVED_PARTNER_CONSENT` | `PRIVATE` / `NEVER_PUBLISH` |
| Rare eDNA | `RESTRICTED` / partner | `NEVER_PUBLISH` GPS |
| Research PAM localization | `APPROVED_PARTNER_CONSENT` | `NEVER_PUBLISH` |
| iNat open geoprivacy CC0/BY | `APPROVED_WITH_ATTRIBUTION` | then observatory taxon defaults |
| iNat hidden coords | `RESTRICTED` | `NEVER_PUBLISH` |
| GFW | `NONCOMMERCIAL_ONLY` | `RESTRICTED` |
| AIS identity / VMS | `PAID` / `RESTRICTED` | `NEVER_PUBLISH` |
| Farms / vessels / PI microdata | `APPROVED_PARTNER_CONSENT` | `PRIVATE` / `NEVER_PUBLISH` |
| Indigenous / TEK | `RESTRICTED` | `NEVER_PUBLISH` |
| Scraping / forums / spot maps | `REJECTED` | `NEVER_PUBLISH` |

---

## 7. Partner network (one paragraph)

Five ordinary classes — vessels, farms, researchers, sensor operators, citizen scientists — plus nations under CARE, not this DPA. Incentives are private tools and credits, **not** cash-per-rare-taxon or public leaderboards. Trust ladder L0–L3 with revocation; provenance on every row; anti-gaming against spoofed rares, AIS mosaics, and hidden-coord fishing; method certification (QARTOD, effort definitions); reputation is operational not a public highliner score. Immediate freeze on ecological-harm incidents. Details: `partner_network_design.md`.

---

## 8. Confidence and limitations

- **High** where named pages were read on 2026-09-18 (OBIS policy, GBIF sensitive-species guide, IUCN spatial/summary terms, Movebank sharing, iNat geoprivacy, CARE, GFW from commercial pass).  
- **Medium** for WDPA/Protected Planet commercial reuse, CITES Trade Database licence, foreign ESA analogues, eBird bulk TOS.  
- **Low / UNKNOWN** for any unlisted national sensitive-species statute.  
- GBIF.org/terms HTML still not independently fetched this pass (prior timeout); NC filter remains mandatory.  
- This agent is **not counsel**. ESA/MMPA/CITES rows are **policy implications**, not opinions. Classifications can change when licences update.  
- No ingest, no robots.txt-as-permission, no partner signatures.

---

## 9. Recommended decisions (for founder + counsel, not locked)

1. **Do not** plan a global public animal map for v1.  
2. Implement licence allowlists (deny GFW, IUCN spatial, NC, VMS, hidden iNat, scrape) before any observatory pipeline exists.  
3. Materialize write-time `PUBLIC` / `COARSENED` / `DELAYED` / `PRIVATE` / `NEVER_PUBLISH` prefixes; public jobs must not mount sensitive stores.  
4. Treat Movebank/PAM/eDNA of listed taxa as partner-gated and `NEVER_PUBLISH` at native grain even when a portal shows a map.  
5. Engage **human legal review** (extend commercial LR-001–008 with IUCN/IBAT, CITES, MMPA PAM, Movebank, CARE).  
6. Keep the observatory stack licence-clean if it might share engineering with commercial FishAI.

---

## 10. Rejected alternatives

| Alternative | Why rejected |
|---|---|
| “It’s a scientific observatory so occurrence should be open” | Harm + CARE + licences; forbidden by program rule |
| Global v1 heatmap with a disclaimer | Disclaimers do not cancel pins (red team) |
| Undo GBIF/OBIS/iNat generalization “for the twin” then forget to re-blur | Leak by design |
| GFW/AIS as life or effort-as-abundance | NC + identity + scientifically false |
| IUCN range shapefiles as a public layer without IBAT/IUCN commercial path | Posted non-commercial spatial terms |
| Live whale/turtle follow-the-tag | Harassment / take facilitation |
| Cash bounties for rare citizen-science | Incentivizes disturbance |
| Nation data via ordinary DPA | CARE; nation protocol only |

---

## 11. Follow-ups

- Counsel: IUCN/IBAT; CITES trade reuse; MMPA PAM vs Slow Zone republication; Movebank owner terms; CARE counsel for any geography with treaty fisheries.  
- DATA_CATALOG / ARCHITECTURE: per-dataset licence + `privacy_tier` + `embargo_until` + sensitive flag; public jobs cannot read `NEVER_PUBLISH`.  
- VALIDATION: reverse-engineering tests on synthetic nests/aggregations/tracks.  
- PRODUCT: no public biological map in year-1 roadmap.  
- Re-fetch GBIF terms HTML.  
- If GFW or IUCN spatial ever becomes strategic: written commercial licence **before** design-as-if-approved.

---

## 12. Artifacts written

All under `/Users/wijeratne/dev/fishai/observatory/`:

1. `data_rights_register.md`  
2. `sensitive_location_policy.md`  
3. `partner_network_design.md`  
4. `artifacts/rights_safety/agent_handoff.md` (this file)

---

## 13. Red-team needed?

**Yes.** Independent attack on: (a) fusion of coarsened mammal + AIS + iNat into a whale wait; (b) turtle-track back-solve to a beach; (c) spawn-chorus acoustics as a fishing app; (d) IUCN/GFW/NC licence bypass through “research-only” weights that later serve a commercial product; (e) CARE leakage via place names; (f) farm re-id in small bays. Not done in this folder.

---

## 14. Next experiment (no ingest)

1. Paper allowlist: 10 families with status class + privacy tier; reject `UNKNOWN`/`NC`/`RESTRICTED` for public design.  
2. Synthetic coarsening test: planted nest/aggregation/track GPS must not be recoverable from the proposed public grain.  
3. UI checklist: prohibited vocabulary (`hot spot`, `go see`, `safe to harvest`, `guaranteed`).  
4. Unsigned DPA walkthrough for one PI telemetry study and one farm, including embargo and unwind.

**Stop condition:** any proposal to scrape, to un-generalize sensitive records, to pay for rare GPS, or to ship a global public animal map.

---

## Return block (for parent agent)

**Default publish rules:** environmental fields `PUBLIC` (licensed); LC pelagics at RFMO published grain `COARSENED`; everything breeding/nesting/spawning/nursery/listed/traded `NEVER_PUBLISH` or delayed 1°/basin only after harm review. See §2.

**`NEVER_PUBLISH` classes:** nests, haul-outs, aggregations, raw telemetry, PAM localization, rare eDNA GPS, VMS/AIS identity, private fishing/farms, TEK, user identity, hidden citizen-science coords, CITES wild pins, security infrastructure, mosaics. See §3.

**Global public map as v1:** **unsafe — rejected.**
