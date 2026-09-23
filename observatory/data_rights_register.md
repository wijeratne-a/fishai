# Data rights register — Global Saltwater Life Observatory

**Document status:** RESEARCH CATALOG, NOT LEGAL ADVICE  
**Access date for cited license and policy pages:** 2026-09-18  
**Program:** Global Saltwater Life Observatory (`/Users/wijeratne/dev/fishai/observatory/`)  
**Scope:** Source-**family** rights, privacy, and ecological-safety rails for a global saltwater life estimation system. No data were ingested.  
**HUMAN LEGAL REVIEW REQUIRED** before any ingest, partner signature, public layer, training corpus, or commercial derivative.

This catalog is **not** an attorney opinion, **not** a license grant, and **not** authorization to collect, train on, redistribute, or publish any dataset. Counsel must confirm each intended use against current terms, territorial law, partner contracts, and nation-specific Indigenous protocols.

**Relationship to the commercial wedge.** The Ocean Intelligence Builder / FishAI 1×1×1×1 files under `/Users/wijeratne/dev/fishai/artifacts/data_rights_and_privacy/` remain the rights record for those three candidate products. This observatory register **extends** that work to global taxa and modalities. **Do not overwrite those files.** Where this document is silent on a family already classified there (CMEMS, Sentinel, NOAA-created environmental products, GEBCO, WoRMS webservices, MSA confidentiality, GFW TOS), inherit that classification.

**Governing rule.** A global scientific mandate to observe saltwater life is **not** a justification to expose sensitive data. A public-domain or CC0 coordinate remains `NEVER_PUBLISH` if releasing it would enable poaching, overfishing, habitat damage, harassment, commercial harm, legal violations, or safety risks.

Companion: `sensitive_location_policy.md`, `partner_network_design.md`, `artifacts/rights_safety/agent_handoff.md`.

---

## 0. Verdict

**A global public species map is unsafe as observatory v1.** See `sensitive_location_policy.md` §12. Public v1 may show environmental context, official boundaries at the grain the authority already publishes, taxonomy, method cards, and coarsened historical presence of **non-sensitive** taxa after ecological-harm review. It may not show a world heatmap of animals.

**No source family is ingestible today.** This is a catalog. Pipeline design may proceed only for families already `APPROVED_*` in the commercial register **and** only into non-public stores, still without bulk download in this iteration.

**Highest observatory-specific legal and harm risks (policy level, not advice):**

| Risk | Why it is first-order for a global observatory |
|---|---|
| Fine occurrence of listed / traded / aggregated animals | ESA/MMPA take and harassment facilitation; CITES trafficking; spawning-aggregation and nesting-beach fishing |
| IUCN Red List spatial downloads | Posted terms: **non-commercial** unless IUCN/IBAT written permission. Categories/names are separately queryable. |
| GFW / AIS / VMS as “effort = life” | NC licence (GFW); vessel identity; not abundance; competitor tracking; security-sensitive routes |
| Raw telemetry and PAM localization | Live or reconstructable tracks of turtles, sharks, marine mammals |
| Rare-taxon eDNA sample points | Remaining population pinpoints |
| Indigenous / TEK / treaty data | CARE; FAIR is not consent |
| Farm / vessel / researcher microdata | Trade secret, statutory confidentiality, unpublished science |
| Mixing CC BY-NC into a later commercial product | Licence contamination of any shared stack with FishAI |

---

## 1. Status classes and privacy tiers

### 1.1 Status classes (same labels as the commercial register)

| Class | Meaning for the observatory |
|---|---|
| `APPROVED_OPEN_COMMERCIAL` | Public-domain or equivalent; commercial use allowed; still apply privacy tiers and ecological-harm review. |
| `APPROVED_WITH_ATTRIBUTION` | Commercial use if credit, DOI, and downstream obligations are implemented. |
| `APPROVED_INTERNAL_ONLY` | May be held internally; no public product, no shared weights, no reseller feed. |
| `APPROVED_PARTNER_CONSENT` | Lawful only under a signed agreement covering the named purpose. |
| `CONDITIONAL_REVIEW_REQUIRED` | Visible or documented, but licence/TOS/mixed rights incomplete. Counsel before ingest. |
| `PAID_LICENSE_REQUIRED` | A commercial contract is the only lawful path. Do not scrape. |
| `RESEARCH_ONLY` | Non-product research under stated terms; not for revenue features. |
| `NONCOMMERCIAL_ONLY` | CC BY-NC or equivalent. Unusable in any commercial FishAI/observatory product until relicensed. |
| `RESTRICTED` | Statute, enforcement, confidentiality, or Indigenous sovereignty. Unauthorized use is unlawful or unethical. |
| `REJECTED` | Do not collect, scrape, or productize. |
| `UNKNOWN` | Insufficient posted terms as of 2026-09-18. Treat as blocked. |

### 1.2 Privacy tiers (observatory; `DELAYED` is first-class)

Stricter of (source licence, partner contract, ecological-harm review, this table) wins.

| Tier | Who may see native resolution | Public product | Training / twin | Example |
|---|---|---|---|---|
| `PUBLIC` | Anyone | Native OK **only after ecological-harm review** and if licence allows | OK | CMEMS SST; GEBCO (not-for-nav); official EEZ/MPA outlines |
| `COARSENED` | Staff + models | Only after spatial generalization | OK at coarsened grain | GBIF Category 2–3 generalized occurrences; RFMO statistical areas |
| `DELAYED` | Staff + models (embargo clock) | Only after the embargo, still at the allowed grain | Internal now; public later | Movebank-style rolling embargo on tracks; post-season nesting summaries |
| `RESTRICTED` | Named staff / statutory or contract purpose | No | Only if licence allows and outputs cannot invert | Mixed IOOS; unpublished HAB; historical AIS internally if counsel clears |
| `PRIVATE` | Contributing partner (and DPA-bound processors) | No microdata | Only if DPA training-use = yes | Farm KPIs; vessel logbooks; PI telemetry before embargo |
| `NEVER_PUBLISH` | Minimize; legal/safety hold only | Never | Never in public or shared weights | Nest GPS; VMS; TEK; MMSI in UX; PAM bearings on a whale |

**Default when unsure:** one tier stricter, then queue for counsel **and** ecological-harm review.

`DELAYED` is not a substitute for `NEVER_PUBLISH`. If the record would still enable harm after any practical embargo (active spawning GPS, remaining abalone bed, calving ground), it stays `NEVER_PUBLISH`.

---

## 2. Observatory permitted-use vs prohibited-use rules

These are **program and ethics rails**, not a substitute for counsel. They apply to research APIs, tiles, notebooks, weights, papers, and demos.

### 2.1 Permitted (if licences, tiers, and ecological-harm review are satisfied)

- Estimate, infer, and forecast saltwater life **with evidence types** (observed / inferred / forecast / unproven / speculative / physically out of reach).
- Publish **environmental** fields (physics, chemistry, bathymetry-as-habitat not as a chart).
- Link **official** season, MPA, critical-habitat, Slow Zone, and CITES authority pages without restating them as observatory authorization to take, enter, or harass.
- Return **partner-private** scores and tracks to the partner who supplied them.
- Publish **coarsened and/or delayed** presence of non-sensitive taxa that pass reverse-engineering tests.
- Use taxonomy authorities (WoRMS AphiaIDs) for names.

### 2.2 Prohibited

| Prohibition | Why |
|---|---|
| **No take, harvest, or fishing authorization** | Seasons, quotas, ESA/MMPA take, CITES permits, and tribal allocations are issued by authorities — never by the observatory. |
| **No navigation or weather-safety advice** | GEBCO, AIS, NWS, CO-OPS disclaim safety fitness. |
| **No MMPA/ESA harassment or take facilitation** | Fine marine-mammal, turtle, or listed-fish locations can attract vessels, drones, and fishers. |
| **No public exact biological pins** | Nesting, spawning, nurseries, haul-outs, remaining beds, live telemetry. |
| **No competitor vessel or farm intelligence** | AIS identity, VMS, routes, farm KPIs. |
| **No Indigenous data without nation protocol** | CARE; FAIR is insufficient. |
| **No training-data laundering of NC, IUCN spatial, GFW, or confidential sources** | Licence and statute. |
| **No scraping, paywall bypass, robots.txt violation, or TOS evasion** | Absolute. |
| **No security-sensitive infrastructure mapping beyond public charting products** | Ports, naval, cables, offshore energy as targeting layers. |
| **No user-identity publication** | Observers, crew, citizen-scientist accounts. |

**Required public disclaimer (draft for counsel):**

> The Global Saltwater Life Observatory provides scientific estimates with explicit uncertainty. It is not a fishing licence, CITES permit, navigation product, weather warning service, wildlife-viewing guide, or take/harassment authorization. Always follow the competent national, regional, and Indigenous authorities. Do not use outputs to locate, pursue, or extract animals.

---

## 3. Source-family register (global)

Each family checked against public licence or policy pages on **2026-09-18** unless inherited from the commercial register (noted). Silent pages → `UNKNOWN` or `CONDITIONAL_REVIEW_REQUIRED`.

### 3.1 Ocean physics / remote sensing / bathymetry

Inherit commercial-register classifications:

| Family | Status | Privacy default | Notes |
|---|---|---|---|
| Copernicus Marine Service products | `APPROVED_WITH_ATTRIBUTION` | `PUBLIC` | Credit + DOI + traceability. Mixed third-party products need product-level credits. |
| Copernicus Sentinel **data** | `APPROVED_WITH_ATTRIBUTION` | `PUBLIC` | Portal chrome other than Sentinel data may be NC. |
| NOAA-created NWS / NDBC / CO-OPS / NCEI-produced | `APPROVED_OPEN_COMMERCIAL` | `PUBLIC` | No endorsement; not navigation/weather-safety. |
| NASA-led unmarked Earthdata | `APPROVED_OPEN_COMMERCIAL` | `PUBLIC` | Default CC0. |
| NASA CSDA commercial satellite | `NONCOMMERCIAL_ONLY` | `RESTRICTED` | No revenue-generating use. |
| GEBCO Grid | `APPROVED_WITH_ATTRIBUTION` | `PUBLIC` | **Not for navigation or safety at sea.** |
| USGS Landsat (USGS archive) | `APPROVED_OPEN_COMMERCIAL` | `PUBLIC` | |
| IOOS RA ERDDAP (global analogues: IMOS, EMODnet, Copernicus in situ) | `CONDITIONAL_REVIEW_REQUIRED` | `PUBLIC` or `RESTRICTED` | Dataset-level licence; many “No License Provided”. |
| ECMWF operational NWP (non-C3S) | `PAID_LICENSE_REQUIRED` | `PUBLIC` | Do not assume GFS = ECMWF. |

Physics fields fused with private ops or sensitive biology inherit the **stricter** biological/ops tier.

### 3.2 Biodiversity aggregators (OBIS / GBIF / SEAMAP)

#### OBIS (IODE/IOC)

- **Policy:** https://manual.obis.org/policy.html (fetched 2026-09-18)  
- **Accepted licences:** CC0, CC BY, CC BY-NC (preference CC0).  
- **FAIR and CARE:** OBIS §3 requires both. Indigenous data must be handled with sensitivity; authority of Indigenous data holders respected.  
- **Access restrictions (OBIS §7):** Legitimate reasons to restrict include privacy, confidentiality, **protection of species, populations, or habitats of concern**, and national security. **Providers should censor or generalize before publishing to OBIS.** The observatory must **not undo** provider coarsening and must coarsen further when ecological-harm review requires it.  
- **Derived OBIS information products:** CC0, still subject to this program’s harm review.  
- **Status:** CC0/CC BY → `APPROVED_WITH_ATTRIBUTION`. CC BY-NC → `NONCOMMERCIAL_ONLY`. Unfiltered mixed download → `REJECTED`.  
- **Privacy:** listed/sensitive/aggregation/nesting occurrence → `COARSENED`, `DELAYED`, or `NEVER_PUBLISH` even if the publisher released points.

#### GBIF

- **Data user agreement:** https://www.gbif.org/terms/data-user  
- **Terms:** https://www.gbif.org/terms (HTML fetch timed out 2026-09-18 in the commercial pass; classification uses that agreement plus GBIF sensitive-species guidance).  
- **Licences:** per-dataset CC0 / CC BY / CC BY-NC; publisher licence prevails.  
- **Sensitive-species practice:** *Current Best Practices for Generalizing Sensitive Species Occurrence Data* (Chapman 2020), https://docs.gbif.org/sensitive-species-best-practices/master/en/ — Categories 1–4 (withhold / 1° / 0.1° / 0.01° / 0.001°). A threatened-species list is a **trigger**, not an automatic public pin.  
- **Status:** same filter as OBIS.  
- **Privacy:** honor `informationWithheld`, `dataGeneralizations`, `coordinateUncertaintyInMeters`. If a record is already generalized, do not treat the published coordinate as truth at native GPS.  
- **Human review:** Yes (DOI citations, NC filter, sensitive flags).

#### OBIS-SEAMAP (Duke) and other megavertebrate nodes

- Extra permission / no-redistribution classes are common; historical default often CC BY-NC.  
- **Status:** `CONDITIONAL_REVIEW_REQUIRED` / often `NONCOMMERCIAL_ONLY`.  
- **Privacy:** marine mammal and turtle occurrence `RESTRICTED` internally; public `NEVER_PUBLISH` at native grain.

### 3.3 Conservation status authorities (IUCN, ESA, MMPA, CITES)

Policy-level implications only. **Not legal advice. HUMAN LEGAL REVIEW.**

#### IUCN Red List (categories, assessments, spatial)

- **Spatial download page:** https://www.iucnredlist.org/resources/spatial-data-download — spatial data “freely available for **non-commercial use**”; commercial use directed to IBAT.  
- **Terms (summary):** https://www.iucnredlist.org/summary-terms/summary-terms-of-use — no commercial use; no redistribute/repost/sublicense including derivative products; attribution required. IUCN warrants that users are **free to view and query** the Red List and places **no restrictions on use of the IUCN Red List Categories associated with each named taxonomic entity**.  
- **Status of range shapefiles / spatial downloads:** `NONCOMMERCIAL_ONLY` until IUCN written permission or IBAT contract (`PAID_LICENSE_REQUIRED`).  
- **Status of category labels (CR/EN/VU/NT/LC/DD/NE) as a join key:** treat as `APPROVED_WITH_ATTRIBUTION` for **query/display of the category name** per the posted warranty; still cite IUCN; still **HUMAN LEGAL REVIEW** before bulk mirroring of assessment text.  
- **Privacy:** IUCN range maps are **not** occurrence pins, but fine coastal polygons for CR/EN taxa can still enable targeting. Public observatory use, if ever licensed: `COARSENED` (EEZ / LME / 1°). Do not ship IUCN spatial as a public hunting layer.  
- **Ecological-harm note:** Red List status is a **sensitivity trigger**, not proof that a location is safe to publish (GBIF Chapman 2020: sensitive-taxon lists ≠ threatened-taxon lists, but overlap is large in the ocean for turtles, sawfish, reef sharks, grouper aggregations).

#### U.S. ESA / MMPA (and analogues)

- **ESA take:** 16 U.S.C. § 1538 — listed species (e.g. many sea turtles, some whales, listed salmon ESUs, smalltooth sawfish). Product must not authorize or facilitate take.  
- **MMPA:** marine mammal take and harassment; NAO 216-100 Appendix B flags confidential marine-mammal data. Commercial register already: MMPA confidential data `RESTRICTED` / `NEVER_PUBLISH`.  
- **Critical habitat GIS:** U.S. government work at **designated** grain `APPROVED_OPEN_COMMERCIAL` as constraint context; CFR text controls; **do not** publish finer occurrence.  
- **Other jurisdictions:** EU Habitats Directive, Australia EPBC, Canada SARA, national wildlife acts — same **policy** pattern: official designated sites may be public; survey microdata usually are not. Classify each statute `CONDITIONAL_REVIEW_REQUIRED` until counsel maps it.  
- **Status of precise listed-species locations:** `RESTRICTED` / `NEVER_PUBLISH`.

#### CITES

- **Appendices I/II/III** identify taxa whose international trade is controlled (many sharks and rays, all sea turtles, seahorses, giant clams, queen conch, some corals).  
- CITES listing is a **trafficking-sensitivity trigger**. Fine wild-population coordinates of Appendix I/II marine taxa default `NEVER_PUBLISH`.  
- **CITES Trade Database** (shipment-level legal trade): useful as **pressure context**, not as a map of remaining wild animals. Licence/reuse `CONDITIONAL_REVIEW_REQUIRED`. Never join trade records to unpublished wild GPS.  
- **Not a permit:** displaying a CITES appendix is not authorization to take or trade.  
- **HUMAN LEGAL REVIEW** before any trade-data product.

### 3.4 Protected areas and sensitive habitats

| Family | Status | Privacy | Notes |
|---|---|---|---|
| WDPA / Protected Planet public boundaries | `CONDITIONAL_REVIEW_REQUIRED` (often non-commercial / attribution; some layers restricted) | `PUBLIC` at **published** official outline | Do not densify. No “life inside the MPA” heatmap. |
| National MPA / Natura 2000 / AMP GIS | `APPROVED_OPEN_COMMERCIAL` or `CONDITIONAL_REVIEW_REQUIRED` per agency | `PUBLIC` at agency grain | Context, not a visit guide to colonies. |
| Ramsar, World Heritage marine | usually public designations | `PUBLIC` designation; `NEVER_PUBLISH` nesting/colony sub-sites | |
| Remaining live rare coral / precious coral beds not in public charts | `RESTRICTED` | `NEVER_PUBLISH` | Harvest and anchor-damage risk. |
| Official nautical charts / ENC | `PAID_LICENSE_REQUIRED` or HO licence | not a life layer | Do not reverse-engineer “secret” reefs from charted hazards as a public biology product. |

### 3.5 Fisheries, vessels, AIS, GFW, VMS

Inherit and globalize the commercial register:

| Family | Status | Privacy | Observatory rule |
|---|---|---|---|
| GFW site, APIs, fishing-effort | `NONCOMMERCIAL_ONLY` | `RESTRICTED` | No commercial observatory/FishAI use. Scraping prohibited. Apparent fishing ≠ animals. |
| Commercial AIS (Spire, Orbcomm, MarineTraffic, etc.) | `PAID_LICENSE_REQUIRED` | `NEVER_PUBLISH` identity | Not abundance. |
| USCG live / Level A–B AIS | `RESTRICTED` | `NEVER_PUBLISH` | |
| Marine Cadastre historical NAIS | `CONDITIONAL_REVIEW_REQUIRED` | `NEVER_PUBLISH` identity | Public-domain vs no-redistribute conflict; counsel. |
| NOAA VMS and national VMS analogues | `RESTRICTED` | `NEVER_PUBLISH` | |
| RFMO / FAO public catch tables | `APPROVED_OPEN_COMMERCIAL` or `CONDITIONAL_REVIEW_REQUIRED` | `PUBLIC` at published (often yearly × area) grain | Not CPUE at set scale. |
| Confidential logbooks, observer, VMS, trip tickets (MSA and foreign analogues) | `RESTRICTED` | `NEVER_PUBLISH` | |
| Private fishing grounds / highliner tracks | `APPROVED_PARTNER_CONSENT` | `PRIVATE` / `NEVER_PUBLISH` publicly | |

**AIS/GFW/VMS are never a measurement of abundance.** If any vessel layer is ever shown: strip identifiers, rule-of-3 cells, delay, label “traffic, not animals.” Default: **do not show**.

### 3.6 Animal-borne telemetry (Movebank and analogues)

- **Permissions:** https://www.movebank.org/cms/movebank-content/permissions-and-sharing  
- **Data policy:** https://www.movebank.org/cms/movebank-content/data-policy  
- Owners retain ownership. Public download uses CC0 / CC BY / CC BY-NC. **Rolling embargo** (30 days, 2–11 months, 1 year, 3 years) and **static embargo** (up to 10 years) exist specifically so current animal locations are not public.  
- Restricted studies require owner permission.  
- **Status:** public CC0/CC BY → `APPROVED_WITH_ATTRIBUTION` **of the released (already embargoed/generalized) portion only**. CC BY-NC → `NONCOMMERCIAL_ONLY`. Restricted studies → `APPROVED_PARTNER_CONSENT`.  
- **Privacy default for marine turtles, mammals, sharks, sawfish, listed birds:** raw tracks `NEVER_PUBLISH`; even public Movebank points get observatory `DELAYED` + `COARSENED` if they still reveal nesting beaches, haul-outs, or aggregations.  
- **Do not** stitch public fragments with AIS or citizen-science photos to re-identify an animal or nest.

### 3.7 eDNA / metabarcoding of rare or listed taxa

| Family | Status | Privacy | Notes |
|---|---|---|---|
| Published eDNA of **common** pelagic/microbial taxa with open licence | per-dataset CC filter | `COARSENED` (station or 0.1°) | Presence of DNA ≠ abundance or live animal. |
| eDNA of **rare, listed, or aggregation-associated** taxa | `RESTRICTED` / `APPROVED_PARTNER_CONSENT` | `NEVER_PUBLISH` native sample coordinates | A positive at a creek mouth or reef is a remaining-population pinpoint. |
| Unpublished lab tables | `APPROVED_PARTNER_CONSENT` | `PRIVATE` | |

Public product, if any: presence in a large region after delay, never a sample-point map of CR/EN/CITES taxa.

### 3.8 Passive acoustic monitoring (marine mammals and fishes)

| Product class | Status | Privacy | Rule |
|---|---|---|---|
| Official conservation products (e.g. NOAA WhaleMap Slow Zones, PACM **as NOAA publishes them**) | U.S. government work → `APPROVED_OPEN_COMMERCIAL` as **link/context** | `PUBLIC` **only at official grain** | Link the authority. Do not densify, interpolate individuals, or add observatory bearings. |
| Research-grade PAM: arrays, bearings, time-difference localization, raw audio of calling whales | `APPROVED_PARTNER_CONSENT` or `RESTRICTED` | `NEVER_PUBLISH` localization; audio `RESTRICTED` | Individual-level tracks enable harassment and vessel routing onto animals. |
| Fish choruses / spawning-aggregation acoustics | `RESTRICTED` | `NEVER_PUBLISH` during and before season | Direct fishing intelligence. |
| NOAA Makara-class internal PAM stores | not a public API | `RESTRICTED` | Do not scrape PACM to rebuild withheld fields. |

**Distinction that must survive into the API:** an official Slow Zone polygon is a **management product**. An observatory-derived lat/lon of a calling right whale is **`NEVER_PUBLISH`.**

### 3.9 Citizen science

| Family | Status | Privacy | Notes |
|---|---|---|---|
| iNaturalist research-grade, **open** geoprivacy, CC0/CC BY | `APPROVED_WITH_ATTRIBUTION` | `COARSENED` if taxon is marine-sensitive even when iNat is open | https://www.inaturalist.org/pages/geoprivacy — obscured = random point in 0.2°×0.2° cell; true coords hidden. Threatened IUCN NT–EX default obscured. |
| iNaturalist **obscured/private** true coordinates | `RESTRICTED` | `NEVER_PUBLISH` | Do not seek `private_latitude` / `private_longitude`. Do not deanonymize. |
| eBird / similar | `CONDITIONAL_REVIEW_REQUIRED` | sensitive-species lists `NEVER_PUBLISH` | TOS often non-commercial for bulk. |
| Social media, forums, “spot” apps | `REJECTED` | `NEVER_PUBLISH` | TOS + location privacy + harassment. |

**Anti-harm:** do not gamify rare-taxon reporting with public pins or cash-per-record (see `partner_network_design.md`).

### 3.10 Aquaculture and farm operations (global)

| Source | Status | Privacy |
|---|---|---|
| Farm sensors, mortality, growth, disease, feed conversion, harvest timing, lease polygons | `APPROVED_PARTNER_CONSENT` | `PRIVATE`; disease and yield `NEVER_PUBLISH` publicly |
| Public concession outlines some countries publish | `CONDITIONAL_REVIEW_REQUIRED` | `COARSENED`; do not attach performance |
| Hatchery genetics / breeding values | `APPROVED_PARTNER_CONSENT` | `NEVER_PUBLISH` |
| NSSP/equivalent sanitation maps | inherit commercial: context only, never harvest authorization | official grain `PUBLIC` as quoted context |

Cross-farm models require DPA + outputs that cannot invert a single farm.

### 3.11 Indigenous data sovereignty

- **CARE Principles:** https://www.gida-global.org/careprinciples — Collective Benefit, Authority to Control, Responsibility, Ethics. Complements FAIR; **FAIR sharing is not consent**.  
- **Local Contexts / TK and BC Notices** where nations use them.  
- Treaty fisheries, usual-and-accustomed areas, TEK, Indigenous place names used as targeting, and co-management catch: `RESTRICTED` until a **nation-drafted** protocol. Default `NEVER_PUBLISH`.  
- Do not scrape tribal sites, harvest calendars, or ethnographic papers as product features.  
- OBIS already requires CARE; the observatory must not undo provider protection.  
- **Status of unconsented Indigenous data:** `REJECTED` / `RESTRICTED`.

### 3.12 Proprietary research, user identity, security infrastructure

| Family | Status | Privacy |
|---|---|---|
| Unpublished survey GPS, embargoed theses, reviewer-only data | `APPROVED_PARTNER_CONSENT` | `PRIVATE` / `DELAYED` per PI; ecological class may still force `NEVER_PUBLISH` |
| User accounts, emails, device IDs, crew manifests | `RESTRICTED` | `NEVER_PUBLISH` |
| Naval operating areas, submarine routes, unpublished cable/pipeline as targeting | `REJECTED` / `RESTRICTED` | `NEVER_PUBLISH` |
| Publicly charted TSS, VTS, and published wind-lease outlines | `CONDITIONAL_REVIEW_REQUIRED` | `PUBLIC` at official grain as **context**, not a surveillance product |
| Copyrighted full-text journals | `REJECTED` for ingest | cite/summarize only |

### 3.13 Reject classes (global)

| Family | Status | Reason |
|---|---|---|
| Paywalled journals, copyrighted full text | `REJECTED` for ingest | Copyright. |
| Website scraping, paywalls, robots.txt bypass | `REJECTED` | Never. |
| Forum / social fishing and wildlife-harassment content | `REJECTED` | Ethics + TOS. |
| Public “spot maps” of exact fishing, nesting, or farm sites | `REJECTED` | Even if some points are already on the internet. |
| Deanonymizing iNat/eBird/Movebank | `REJECTED` | |

---

## 4. Attribution and operational obligations (if ingest proceeds later)

| Family | Minimum control |
|---|---|
| CMEMS / Sentinel / NOAA / GEBCO | Inherit commercial register §5. |
| GBIF / OBIS | Per-dataset licence filter; DOI citations; strip NC; preserve generalization metadata; CARE. |
| IUCN spatial | Do not ingest without IBAT/IUCN commercial path. Category names: cite IUCN. |
| Movebank | Owner terms + embargo; cite study; no live-track republication. |
| Partners | DPA, revocation, no public microdata (`partner_network_design.md`). |
| GFW | Do not ingest for this program’s commercial or dual-use stack. |
| iNaturalist | Honor geoprivacy; do not request hidden coords. |

---

## 5. Ecological-harm review (rights gate)

No layer becomes `PUBLIC` solely because the source licence is open. Before a public tile, API field, figure, or weight dump:

1. Licence class ∈ `APPROVED_*` (not NC/RESTRICTED/UNKNOWN).  
2. Privacy tier ∈ {`PUBLIC`, `COARSENED`, `DELAYED` with embargo elapsed}.  
3. Taxon/habitat class defaults in `sensitive_location_policy.md` §5–6.  
4. Reverse-engineering tests (`sensitive_location_policy.md` §8).  
5. No Indigenous, partner, or user-identity leakage.  
6. Record the review (taxon, grain, embargo, residual harm, reviewer).  

Fail → coarsen, delay, restrict, or `NEVER_PUBLISH`. Do not “fix forward” by blurring a shipped tile without an incident record.

---

## 6. What this register does not do

- Does not authorize ingest (none was performed).  
- Does not replace human counsel, insurance, CITES/ESA/MMPA opinions, or nation protocols.  
- Does not treat “it is on a government map” as a commercial API licence (GFW, MarineTraffic, many MPA viewers, IUCN spatial).  
- Does not allow combining public AIS identity with biology to publish someone else’s fishing pattern or a whale’s current position.  
- Does not interpret “global observatory” as a reason to override `NEVER_PUBLISH`.

---

## 7. Related artifacts

- Commercial wedge (do not overwrite): `/Users/wijeratne/dev/fishai/artifacts/data_rights_and_privacy/`  
- `sensitive_location_policy.md`  
- `partner_network_design.md`  
- `artifacts/rights_safety/agent_handoff.md`
