# Data rights register — Ocean Intelligence Builder / FishAI

**Document status:** RESEARCH CATALOG, NOT LEGAL ADVICE  
**Access date for all cited license pages:** 2026-09-18  
**Project:** Ocean Intelligence Builder / FishAI (`/Users/wijeratne/dev/fishai`)  
**Scope:** Three unresolved candidate wedges. No data were ingested.  
**HUMAN LEGAL REVIEW REQUIRED** before any ingest, partner signature, public product launch, or commercial derivative.

This document catalogs publicly posted licenses, statutes, and terms as retrieved on 2026-09-18. It is **not** an attorney opinion, **not** a license grant, and **not** authorization to collect, train on, redistribute, or sell any dataset. Counsel must confirm each intended use against current terms, territorial law, and partner contracts.

---

## 0. Verdict for the three candidates

**No candidate is categorically legally infeasible** if all of the following remain true:

1. The product is decision-support intelligence, not a fishing, harvest, navigation, weather-safety, or food-safety authorization.
2. Confidential government fisheries statistics, VMS, real-time AIS feeds, and raw charter/farm logbooks are **not** used unless a lawful authorization or signed partner agreement exists.
3. Public forecasts use coarsened zones; exact catch, farm, and vessel identity stay private.
4. Tribal / Indigenous data are used only with sovereignty-respecting consent (CARE).
5. Licenses that are CC BY-NC, GFW, commercial AIS, or dataset-unspecified are excluded until a commercial license or counsel clearance exists.

**Can be used now (catalog / prototype design / later ingest with attribution and disclaimers — still no ingest in this iteration):**

| Family | Status class | Notes |
|---|---|---|
| Copernicus Marine Service products | `APPROVED_WITH_ATTRIBUTION` | Free worldwide commercial derivatives; credit + DOI + downstream record-keeping required. Account/SLA. |
| Copernicus Sentinel data (not portal chrome) | `APPROVED_WITH_ATTRIBUTION` | Free, full, open reuse including commercial; credit “Copernicus Sentinel data [Year]”. |
| NOAA-created NWS / NDBC / CO-OPS / most NOAA environmental products | `APPROVED_OPEN_COMMERCIAL` | U.S. public domain unless annotated; no implied NOAA endorsement; do not present modified products as official. Rate-limit NWS. |
| NASA-led Earthdata (unmarked NASA missions) | `APPROVED_OPEN_COMMERCIAL` | Default CC0; citation strongly urged; **not** CSDA commercial-satellite EULAs. |
| GEBCO Grid | `APPROVED_WITH_ATTRIBUTION` | Public domain + attribution; **not for navigation or safety at sea**. |
| USGS Landsat (USGS archive) | `APPROVED_OPEN_COMMERCIAL` | No reuse restriction; source acknowledgment requested. |
| NOAA FOSS / Fisheries of the United States **non-confidential aggregated landings** | `APPROVED_OPEN_COMMERCIAL` | Rule-of-three suppression already applied by NOAA. Not trip CPUE. |
| RecFIN / CRFS / ORBS **published estimates** (not salmon in some RecFIN reports) | `APPROVED_OPEN_COMMERCIAL` | Aggregates. CPFV raw logs are **not** this class. |
| Maine DMR **historical county/year landings tables** | `APPROVED_OPEN_COMMERCIAL` | Public aggregates only. |
| ASMFC / PFMC / NMFS **public** stock assessments, season notices, critical-habitat GIS | `APPROVED_OPEN_COMMERCIAL` | Regulatory text, not a license to fish. |
| WA DOH **published** growing-area classification maps/reports as **context** | `CONDITIONAL_REVIEW_REQUIRED` | Public health maps exist; commercial reuse of site content is not a clean open license; **never** as harvest authorization. |
| WoRMS **webservice taxon match** (not full DB dump, not images) | `APPROVED_WITH_ATTRIBUTION` | Cite WoRMS; do not redistribute entire database. |
| OBIS / GBIF records licensed **CC0 or CC BY** after per-dataset filter | `APPROVED_WITH_ATTRIBUTION` | Filter out CC BY-NC before any commercial product. |
| IOOS RA ERDDAP datasets whose **dataset license metadata** is public-domain / CC0 / CC BY | `CONDITIONAL_REVIEW_REQUIRED` | Many NANOOS catalog records say “No License Provided”. |

**Blocked until license, statute, or signed consent is cleared:**

| Family | Status class | Why blocked |
|---|---|---|
| Global Fishing Watch site, APIs, fishing-effort datasets | `NONCOMMERCIAL_ONLY` | CC BY-NC 4.0 + TOS; scraping prohibited; no public commercial license. |
| Commercial AIS (Spire, Orbcomm, MarineTraffic, VesselFinder, satellite AIS) | `PAID_LICENSE_REQUIRED` | Proprietary. Do not scrape. |
| USCG real-time / Level A–B AIS feeds | `RESTRICTED` | Sharing categories; interconnection agreements; not a public product feed. |
| NOAA VMS | `RESTRICTED` | MSA confidentiality; OLE policy 06-101. |
| PacFIN / ACCSP / state trip tickets, dealer reports, CPFV **raw** logs | `RESTRICTED` | MSA 16 U.S.C. § 1881a; CA FGC § 8022; ME 12 M.R.S. § 6173; ACCSP/PacFIN NDAs. |
| GBIF / OBIS **CC BY-NC** datasets | `NONCOMMERCIAL_ONLY` | Commercial FishAI product cannot mix these into production features. |
| NASA CSDA commercial satellite | `NONCOMMERCIAL_ONLY` | Revenue-generating use prohibited by CSDA EULAs. |
| Partner farm / charter / buyer logbooks, sensors, GPS tracks | `APPROVED_PARTNER_CONSENT` | Unusable until DPA signed. |
| Tribal / Indigenous knowledge, treaty fishery data, TEK | `RESTRICTED` | CARE + nation-specific consent. Default `NEVER_PUBLISH`. |
| SoundToxins / some HAB partner streams | `UNKNOWN` | Catalog license often “not specified”. |
| Website scraping, paywalls, robots.txt bypass | `REJECTED` | Never. |
| Public “spot maps” of exact fishing or farm sites | `REJECTED` | Product and ethics ban, even if some points are public. |

**Highest legal risks by wedge**

| Wedge | Highest risks | Infeasible? |
|---|---|---|
| (1) Pacific oyster × WA farms × 72h ops risk | **Product-claim / food-safety:** appearing to authorize harvest under NSSP/WA DOH. **Trade secret:** farm performance. **Tribal shellfish rights.** Unclear DOH website copyright for bulk reuse. | **No**, if the product is ops-risk only (work windows, temp/DO/pH/wave stress) and **never** harvest/food-safety authorization. |
| (2) Chinook × CA/OR charter encounter | **ESA take facilitation** for listed ESUs. **CA FGC § 8022** CPFV confidentiality. **Public hot-spot maps.** Treaty fisheries. RecFIN often **excludes salmon**. | **No**, but this is the **highest counsel-priority** wedge. Encounter-likelihood for licensed charters ≠ harvest authorization, but marketing and map granularity can still create ESA/unfair-competition risk. |
| (3) American lobster × GOM commercial CPUE | **Statutory confidentiality** of harvester/dealer/vessel statistics (federal + Maine). Next-trip CPUE **cannot** be built from public FOSS/DMR tables alone. AIS/GFW **not** a lawful abundance substitute and poorly covers small lobster boats. | **No**, but **commercially infeasible without partner logbooks** under DPA. Using confidential state/federal CPUE without authorization is **REJECTED**. |

---

## 1. Status classes and privacy tiers

### 1.1 Status classes (use exactly these labels)

| Class | Meaning for FishAI |
|---|---|
| `APPROVED_OPEN_COMMERCIAL` | Public-domain or equivalent; commercial use and redistribution allowed; still apply attribution/disclaimer hygiene and privacy tiers. |
| `APPROVED_WITH_ATTRIBUTION` | Commercial use allowed if credit, DOI, and any downstream obligations are implemented. |
| `APPROVED_INTERNAL_ONLY` | May be held internally; no public product, no training publication, no reseller feed. |
| `APPROVED_PARTNER_CONSENT` | Lawful only under a signed agreement covering the named purpose. |
| `CONDITIONAL_REVIEW_REQUIRED` | Publicly visible but license, TOS, or mixed third-party rights are incomplete. Counsel before ingest. |
| `PAID_LICENSE_REQUIRED` | A commercial contract is the only lawful path. Do not scrape. |
| `RESEARCH_ONLY` | Permitted for non-product research under stated terms; not for revenue features. |
| `NONCOMMERCIAL_ONLY` | CC BY-NC or equivalent. Unusable in a commercial FishAI product until relicensed. |
| `RESTRICTED` | Statute, enforcement, or confidentiality regime. Unauthorized use is unlawful. |
| `REJECTED` | Do not collect, scrape, or productize. |
| `UNKNOWN` | Insufficient posted terms as of 2026-09-18. Treat as blocked. |

### 1.2 Privacy tiers (data after ingest)

| Tier | Rule |
|---|---|
| `PUBLIC` | May appear in public product at native resolution if source allows. |
| `COARSENED` | Public product only after spatial/temporal aggregation (see privacy policy). |
| `RESTRICTED` | Authorized staff / model training under contract; not in public maps. |
| `PRIVATE` | Partner-identifiable operations; return only to that partner (or agreed cohort). |
| `NEVER_PUBLISH` | Do not put in public product, marketing, training corpora shared externally, or open weights. |

**Defaults (non-negotiable unless counsel and partner rewrite them):**

- Exact catch locations → `PRIVATE` / `NEVER_PUBLISH` publicly.
- Public forecasts → broad zones only (`COARSENED`).
- Farm performance → `PRIVATE`.
- Sensitive / listed species locations → `COARSENED`, delayed, or excluded.
- No public spot maps.
- Tribal / Indigenous data → sovereignty/consent; default `NEVER_PUBLISH`.
- AIS/VMS → **not abundance**; vessel identity `PRIVATE` / `NEVER_PUBLISH`.

---

## 2. Product permitted-use vs prohibited-use rules

These are **product and ethics rails**, not a substitute for counsel. They apply to all three wedges.

### 2.1 Permitted (if licenses and privacy tiers are satisfied)

- Provide **relative, probabilistic, decision-support intelligence** to a defined operator class (farm manager, charter captain, commercial lobster operator).
- Show **environmental context** (SST, waves, currents, DO, pH, air, tides) with source credit and “as-is / not official” disclaimers.
- Show **official public** season, closure, and classification **as context**, linking to the issuing authority, without restating them as FishAI’s authorization.
- Return **partner-private** scores to the partner who supplied the ground truth.
- Publish **coarsened** public zone outlooks that cannot be reverse-engineered into secret spots or farm KPIs.
- Use taxonomy authorities (WoRMS AphiaIDs) for species identity.

### 2.2 Prohibited (product claims and data practices)

| Prohibition | Why |
|---|---|
| **No legal fishing authorization** | Seasons, bag limits, ESA take, tribal allocations, and licenses are issued by NMFS, states, and tribes — never by FishAI. |
| **No navigation or weather-safety advice** | GEBCO, AIS, NWS, and CO-OPS explicitly disclaim navigation/safety fitness. Do not route vessels or declare “safe to go”. |
| **No shellfish food-safety or harvest authorization** | NSSP/ISSC/FDA/WA DOH classify growing waters. FishAI must not say an area is safe to harvest or that shellstock is fit for sale. |
| **No catch guarantee** | Encounter/CPUE scores are relative and uncertain. Marketing must not promise fish. |
| **No ESA / MMPA take authorization** | 16 U.S.C. § 1538; listed Chinook ESUs. |
| **No official-government impersonation** | NWS, NOAA, WA DOH, FDA terms forbid presenting modified products as official. |
| **No implied NOAA / NASA / Copernicus / GEBCO endorsement** | All reviewed licenses. |
| **No public exact fishing or farm maps** | Ethics + competitive harm + ESA. |
| **No competitor vessel tracking** | AIS identity is private; not a hunting tool. |
| **No training-data laundering of NC or confidential sources** | CC BY-NC, GFW, MSA, partner DPAs. |
| **No scraping, paywall bypass, robots.txt violation, or TOS evasion** | Absolute. |
| **No sale or redistribution of raw partner or confidential government microdata** | Statute + contract. |

**Required UI disclaimer (draft for counsel):**

> FishAI provides environmental and operational decision support only. It is not a fishing license, harvest permit, navigation product, weather warning service, or shellfish sanitation authority. Always follow NOAA, U.S. Coast Guard, state, tribal, and ISSC/NSSP official sources. Forecasts are probabilistic and do not guarantee catch, safety, or marketability.

---

## 3. Source-class register

Each row was checked against a public license or statute page on **2026-09-18**. Where the page is silent, class = `UNKNOWN` or `CONDITIONAL_REVIEW_REQUIRED`.

### 3.1 Ocean physics / biogeochemistry / remote sensing

#### Copernicus Marine Service (CMEMS)

- **Example:** https://marine.copernicus.eu/  
- **License name:** Licence to Use the Copernicus Marine Service Products (annex to CMEMS SLA)  
- **License URL:** https://marine.copernicus.eu/user-corner/service-commitments-and-licence  
- **Key terms (quoted/paraphrased from page, 2026-09-18):** worldwide, non-exclusive, royalty-free, **perpetual** licence, free of charge, to (a) copy for internal use, (b) modify/adapt/create and **distribute Value Added Products or Derivative Work for any purpose**, (c) redistribute original products. Credits must be visible: *“Generated using E.U. Copernicus Marine Service Information; insert DOIs links here”*. Licensee **must keep records tracing use** and **propagate that duty** in descending licences. IP in originals remains with the EU; new IP in modifications belongs to licensee. Products “as is”; French law. Service currently funded through **30 June 2028**. Some SeaDataNet / EUMETSAT / GHRSST / EMODnet / C3S / ESA-CCI products **pass through** CMEMS — check product-level credits.
- **Status:** `APPROVED_WITH_ATTRIBUTION`  
- **Privacy:** `PUBLIC` for physical fields; coarsen if fused with private ops.  
- **Human review:** Yes (account/SLA, DOI list, record-keeping implementation, mixed third-party products).  
- **Wedges:** all three (SST, currents, waves, BGC as available at coastal resolution).

#### Copernicus Sentinel data (satellite)

- **License name:** Legal notice on the use of Copernicus Sentinel Data and Service Information  
- **License URL:** https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice  
- **Key terms:** free, full and open access; reproduction, distribution, communication, adaptation, combination — “in so far as it is lawful”. Credit *“Copernicus Sentinel data [Year]”* or *“Contains modified Copernicus Sentinel data [Year]”*.  
- **Caveat:** Copernicus Data Space Ecosystem **portal contents other than Sentinel data** are described as **non-commercial** (https://dataspace.copernicus.eu/terms-and-conditions). Use the Sentinel legal notice for the data, not the portal chrome.  
- **Status:** `APPROVED_WITH_ATTRIBUTION` for Sentinel data; `NONCOMMERCIAL_ONLY` for portal-only materials.  
- **Wedges:** oyster (shoreline/temp/turbidity context), Chinook (SST/color), lobster (SST).

#### NASA Earthdata (NASA-led missions)

- **License name:** ESDIS Project Data Use and Citation Guidance; default Creative Commons Zero 1.0  
- **License URL:** https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance  
- **CC0 URL:** https://creativecommons.org/publicdomain/zero/1.0/  
- **Key terms:** Unless marked with a restriction, NASA-led mission data are **CC0**. Citation strongly urged. No NASA endorsement. Non-NASA holdings follow the sponsor’s license. Earthdata Login may be required.  
- **NASA CSDA commercial satellite EULAs:** https://www.earthdata.nasa.gov/engage/open-data-services-software/end-user-license-agreements and https://science.nasa.gov/earth-science/csda/end-user-license-agreements/ — **no revenue-generating use**.  
- **Status:** NASA-led unmarked → `APPROVED_OPEN_COMMERCIAL`. CSDA / partner EULAs → `NONCOMMERCIAL_ONLY` or `PAID_LICENSE_REQUIRED`.  
- **Human review:** Yes, per collection.

#### NOAA environmental (NWS, NDBC, CO-OPS, NCEI-produced)

- **NWS disclaimer:** https://www.weather.gov/disclaimer — public domain unless noted; no copyright claim on NWS info; no implied endorsement; do not modify then present as official; user assumes risk; **rate-limit / no abuse** of NWS IT. Third-party map imagery (Google/Esri) is separately licensed.  
- **CO-OPS:** https://tidesandcurrents.noaa.gov/disclaimers.html (also `https://www.co-ops.nos.noaa.gov/disclaimers.html`) — public domain unless annotated; preliminary data not official QC; attribution requested; 17 U.S.C. § 403 notice for compilations.  
- **NDBC:** https://www.ndbc.noaa.gov/docs/ndbc_web_data_guide.pdf — official HTTP files; **do not scrape mobile pages**; limit request frequency. Some PMEL/ERDDAP copies mark NOAA data as CC0.  
- **NCEI Open Data Policy:** https://www.ncei.noaa.gov/sites/default/files/2023-12/NCEI%20PD-10-2-02%20-%20Open%20Data%20Policy%20Signed.pdf — NOAA-produced environmental data public domain in the U.S.; CC0 preferred for international. **Third-party archived data may carry other licenses.**  
- **Federal open-license policy:** https://resources.data.gov/open-licenses/  
- **Status:** NOAA-created → `APPROVED_OPEN_COMMERCIAL`. Third-party-on-NOAA-sites → `CONDITIONAL_REVIEW_REQUIRED`.  
- **Privacy:** `PUBLIC` for weather/tides/buoys.  
- **Wedges:** all three. **Prohibited use:** weather-safety / navigation advice.

#### USGS Landsat

- **License URL:** https://www.usgs.gov/faqs/are-there-any-restrictions-use-or-redistribution-landsat-data  
- **Key terms:** no restrictions on USGS-downloaded Landsat; may be used or redistributed; source acknowledgment requested.  
- **Status:** `APPROVED_OPEN_COMMERCIAL`

#### GEBCO Grid

- **License name:** Terms of use for the GEBCO Grid and derived information products  
- **License URL:** https://www.gebco.net/data-products/gridded-bathymetry/terms-of-use  
- **Key terms:** placed in the **public domain**, free of charge; copy, publish, distribute, adapt, **commercially exploit**; **must** acknowledge source; must not imply GEBCO/IHO/IOC endorsement or official status; must not mislead. **“The GEBCO Grid should NOT be used for navigation or for any other purpose involving safety at sea.”**  
- **Status:** `APPROVED_WITH_ATTRIBUTION`  
- **Privacy:** `PUBLIC`  
- **Product rail:** habitat/constraint layer only; never a chart.

### 3.2 Biodiversity / taxonomy

#### OBIS

- **Policy:** https://manual.obis.org/policy.html  
- **Publication licenses:** https://manual.obis.org/data_publication.html  
- **Accepted licenses:** CC0, CC BY, CC BY-NC (preference CC0).  
- **CC0:** https://creativecommons.org/publicdomain/zero/1.0/  
- **CC BY 4.0:** https://creativecommons.org/licenses/by/4.0/  
- **CC BY-NC 4.0:** https://creativecommons.org/licenses/by-nc/4.0/  
- **Key terms:** Users must honor **per-dataset** licenses. OBIS derived information products are published under **CC0**. CARE principles required for Indigenous data. Providers should already coarsen sensitive species before publishing; FishAI still coarsens further for listed taxa. Citation of datasets + OBIS required.  
- **OBIS-SEAMAP** (Duke) has extra “permission required” and **no redistribution** except CC0: treat as a **different** node with stricter TOS.  
- **Status:** CC0/CC BY → `APPROVED_WITH_ATTRIBUTION`. CC BY-NC → `NONCOMMERCIAL_ONLY`. Mixed download without filter → `REJECTED`.  
- **Privacy:** occurrence of listed/sensitive taxa → `COARSENED` or `NEVER_PUBLISH`.  
- **Wedges:** species presence context; **not** CPUE or farm ops labels.

#### GBIF

- **Data user agreement:** https://www.gbif.org/terms/data-user  
- **Terms of use:** https://www.gbif.org/terms  
- **Key terms (from 2026-09-18 search of those pages):** Users must comply with the publisher-selected licence in the download (CC0, CC BY, or CC BY-NC). Publisher licences **prevail** over the GBIF user agreement. Attribution is required for CC BY / CC BY-NC and is a community norm even for CC0. GBIF notes “commercial” is grey; **FishAI is a commercial product** — treat CC BY-NC as unusable.  
- **Status:** same filter as OBIS.  
- **Human review:** Yes (DOI download citations, NC filter in pipeline).

#### WoRMS

- **About / terms:** https://marinespecies.org/about.php  
- **Bulk request form:** https://marinespecies.org/usersrequest.php  
- **Key terms:** Images default **CC BY-NC-SA** unless stated. **Re-distribution of the entire database is not permitted** without prior written agreement. Prefer online tools and webservices. Citation: *WoRMS Editorial Board (year). World Register of Marine Species. Available from https://www.marinespecies.org at VLIZ. Accessed [date]. doi:10.14284/170*. Some third-party catalogues label the dataset CC BY 4.0; **the live WoRMS about page does not grant a blanket commercial database licence**.  
- **Status:** taxon webservice lookups → `APPROVED_WITH_ATTRIBUTION`. Full DB snapshot → `CONDITIONAL_REVIEW_REQUIRED`. Images → `NONCOMMERCIAL_ONLY`.  
- **Privacy:** `PUBLIC` (names).

### 3.3 IOOS regional associations

- **IOOS open data sharing:** https://ioos.noaa.gov/data/data-standards/open-data-sharing/ — NOAA grant data-sharing directive; GEOSS full-and-open principles; IOOS-funded observations “made freely available”. This is a **sharing mandate on providers**, not a user licence.  
- **NANOOS ERDDAP legal:** https://erddap.nanoos.org/erddap/legal.html — **dataset-level** license metadata controls reuse; many IOOS Catalog records say “No License Provided”.  
- **NANOOS DMP:** https://nanoos.org/documents/certification/NANOOS_DMP.pdf  
- **NERACOOS ERDDAP:** https://www.neracoos.org / https://data.neracoos.org/erddap/  
- **CENCOOS:** https://www.cencoos.org/  
- **Status:** `CONDITIONAL_REVIEW_REQUIRED` until each dataset’s `license` attribute is CC0/public-domain/CC BY or NOAA-produced.  
- **Wedges:** oyster (NANOOS Puget Sound/coastal), Chinook (NANOOS/CENCOOS), lobster (NERACOOS).  
- **Do not** hammer ERDDAP; respect documented rate/etiquette.

### 3.4 State fisheries, councils, and landings

#### Magnuson-Stevens confidentiality (federal floor)

- **Statute:** 16 U.S.C. § 1881a(b) — https://www.law.cornell.edu/uscode/text/16/1881a  
- **NOAA NAO 216-100:** https://www.noaa.gov/organization/administration/nao-216-100-protection-of-confidential-fisheries-statistics  
- **50 C.F.R. §§ 600.410, 600.415:** https://www.law.cornell.edu/cfr/text/50/600.415  
- **Key terms:** Information submitted in compliance with the Act is **confidential** and shall not be disclosed except to authorized persons. Secretary may publish **aggregate or summary** form that does **not directly or indirectly disclose the identity or business** of any submitter.  
- **Status of confidential microdata:** `RESTRICTED`  
- **Status of NOAA-published non-confidential aggregates:** `APPROVED_OPEN_COMMERCIAL`

#### NOAA FOSS commercial landings (public query)

- **Example:** https://www.fisheries.noaa.gov/foss  
- **Caveats:** https://www.fisheries.noaa.gov/commercial-landing-data-caveats  
- **InPort:** https://www.fisheries.noaa.gov/inport/item/3475 — public if ≥3 reporting units; confidential otherwise; NDA required for confidential.  
- **Citation:** *NOAA Fisheries Office of Science and Technology, Commercial Landings Query, Available at: www.fisheries.noaa.gov/foss, Accessed mm/dd/yyyy*  
- **Status:** `APPROVED_OPEN_COMMERCIAL` for returned non-confidential tables.  
- **Privacy:** `PUBLIC` at published grain; do not attempt to de-suppress.  
- **Wedge 3:** annual/state landings ≠ next-trip CPUE.

#### PacFIN

- **Confidential access policy:** https://pacfin.psmfc.org/pacfin_pub/confagree.php  
- **Key terms:** confidential data for PFMC FMP implementation; authorized individuals only; signed non-disclosure; no sharing with unapproved persons.  
- **Status:** confidential warehouse → `RESTRICTED`. Published non-confidential reports → `APPROVED_OPEN_COMMERCIAL` if the report itself is public.

#### ACCSP

- **Data warehouse:** https://www.accsp.org/what-we-do/data-warehouse/  
- **Key terms:** Partner **rule of 3** (three dealers, three fishermen, **and** three vessels) for public summaries. Partner confidentiality laws prevail. Confidential access is partner-approved, need-based, not a commercial-product licence.  
- **Status:** confidential → `RESTRICTED`. Public non-confidential queries → `APPROVED_OPEN_COMMERCIAL`.

#### California CPFV / commercial records

- **Cal. Fish & Game Code § 8022:** landing receipts and fishing activity records **shall be confidential and shall not be public records**; publish only as summaries that do not disclose the individual record or business. Catch information in those records is confidential.  
- **CDFW MFSU:** https://wildlife.ca.gov/Fishing/Commercial/MFSU  
- **CPFV e-logs:** https://apps.wildlife.ca.gov/marinelogs/cpfv — operators submit; used for resource management.  
- **Public CPFV summaries:** e.g. https://wildlife.ca.gov/Conservation/Marine/Pelagic-Fisheries/Catch — suppress when **<3 vessels**.  
- **Status:** raw logs → `RESTRICTED`. Published summaries → `APPROVED_OPEN_COMMERCIAL`. Partner’s **own** log copy under DPA → `APPROVED_PARTNER_CONSENT` (the operator may share *their* copy; FishAI still must not pull CDFW’s confidential copy).

#### RecFIN / CRFS / ORBS

- **RecFIN:** https://www.recfin.org/  
- **Estimates table:** https://www.fisheries.noaa.gov/inport/item/55977  
- **CTE001 note:** Pacific halibut and **salmon catch estimates are not included** in that RecFIN report. California salmon uses CDFW Ocean Salmon Project.  
- **Status:** published estimates → `APPROVED_OPEN_COMMERCIAL`.  
- **Wedge 2 limitation:** do not assume RecFIN supplies Chinook CPUE; confirm OSP/ODFW salmon products and their licences.

#### Maine DMR lobster

- **12 M.R.S. § 6173:** https://legislature.maine.gov/statutes/12/title12sec6173.html — collected statistics **confidential**; may not be disclosed in a manner that identifies any person or vessel except court order or statutory exception.  
- **DMR Chapter 5:** https://www.maine.gov/dmr/sites/maine.gov.dmr/files/docs/Chapter5_08102021.pdf  
- **Public historical landings:** https://www.maine.gov/dmr/fisheries/commercial/landings-program/historical-data  
- **Survey data request:** https://www.maine.gov/dmr/science/species-information/maine-lobster/surveys/data-request — research requests; confidential fishery-dependent surveys.  
- **Status:** public tables → `APPROVED_OPEN_COMMERCIAL`. Harvester/dealer/sea-sample microdata → `RESTRICTED`.  
- **Wedge 3:** next-trip CPUE needs **partner logbooks**, not DMR confidential extracts.

#### ASMFC / NEFMC / PFMC public documents

- Public FMPs, addenda, stock assessments, and Federal Register rules are U.S. government or commission publications. Treat **text of U.S. government rules** as public domain; commission copyright on non-federal PDFs is `CONDITIONAL_REVIEW_REQUIRED` (cite, quote fairly, do not dump entire copyrighted reports into the product).  
- **Status:** official season/quota notices → `APPROVED_OPEN_COMMERCIAL` as **context**, never as FishAI authorization.

### 3.5 Shellfish sanitation (ISSC / NSSP / WA DOH)

#### ISSC / FDA NSSP

- **ISSC NSSP Guide:** https://issc.org/nssp-guide  
- **FDA 2023 NSSP Guide:** https://www.fda.gov/media/181370/download  
- **Program page:** https://www.fda.gov/food/federalstate-food-programs/national-shellfish-sanitation-program-nssp  
- **Key point:** NSSP is the **federal/state control program** for molluscan shellfish safety. Growing-area classification (Approved, Conditionally Approved, Restricted, Conditionally Restricted, Prohibited) is a **public-health legal determination** by the Authority (in WA: Department of Health).  
- **Status of the Guide PDF:** U.S. government publication → treat as `APPROVED_OPEN_COMMERCIAL` for **citation and context**.  
- **Status of using classifications as a FishAI “safe to harvest” output:** `REJECTED` (product prohibition), even though the maps are public.  
- **Status of using official closures as model labels for food-safety:** `REJECTED`. Using them as **exogenous operational context** (e.g., “official classification this week is X — confirm on DOH”) is `CONDITIONAL_REVIEW_REQUIRED` (claims + copyright of viewer).

#### Washington DOH growing areas

- **Program:** https://doh.wa.gov/community-and-environment/shellfish/growing-areas  
- **Map viewer:** https://fortress.wa.gov/doh/oswpviewer/index.html  
- **Copyright page:** https://doh.wa.gov/about-us/privacy-and-copyright-information — site may contain **third-party copyrighted** content; DOH recommends contacting webmaster (`webrequests@doh.wa.gov`) before using site content. **No CC0/CC BY grant found.** Public Records Act may make some records public **without** granting a commercial API licence.  
- **Status:** `CONDITIONAL_REVIEW_REQUIRED`  
- **Privacy:** growing-area polygons are public-health geography (`PUBLIC` / `COARSENED`); **commercial harvest site locations inside the viewer** may identify businesses → treat as `COARSENED`/`RESTRICTED` until counsel reviews the viewer’s layers.  
- **Wedge 1:** context only.

### 3.6 AIS, VMS, Global Fishing Watch

#### Global Fishing Watch

- **Terms of Use (last modified May 21, 2021):** https://globalfishingwatch.org/terms-of-use/  
- **Commercial FAQ:** https://globalfishingwatch.org/faqs/can-i-use-global-fishing-watch-apis-for-commercial-purposes/  
- **API license/rate limits:** https://globalfishingwatch.org/our-apis/documentation/docs/license-rate-limits.md  
- **Raw AIS FAQ:** https://globalfishingwatch.org/faqs/can-i-download-raw-ais-data/ — raw AIS is **commercial**; GFW cannot give it away.  
- **Key terms:** Site and Services **Non-Commercial Use Only** under **CC BY-NC 4.0** (https://creativecommons.org/licenses/by-nc/4.0/). Commercial use, commercial products, works for hire, and **private internal uses that support a commercial product** are outside the public licence. **Scraping prohibited.** API: 50,000 requests/day, 1,500,000/month (non-commercial). Apparent fishing ≠ actual fishing.  
- **Status:** `NONCOMMERCIAL_ONLY` (public terms) / `PAID_LICENSE_REQUIRED` (custom GFW commercial licence, not generally offered).  
- **Wedges:** **do not use** for commercial FishAI. Even scientifically, AIS ≠ lobster or charter abundance.

#### Marine Cadastre historical AIS (NOAA/BOEM/USCG)

- **Portal:** https://marinecadastre.gov/ais/  
- **FAQ (May 2026):** https://coast.noaa.gov/data/marinecadastre/ais/faq.pdf  
- **USCG sharing categories:** https://navcen.uscg.gov/ais-data-sharing-categories-requirements  
- **COMDTINST 5230.80A:** https://www.navcen.uscg.gov/sites/default/files/pdf/AIS/CI5230_80A.pdf  
- **Key terms from FAQ:** Historical NAIS, land-based, not live; “generally considered public domain”; **intended for coastal and ocean planning, not navigation**. FAQ also restates USCG language that data **may not be used for purposes other than those intended for the disclosure**, and entities **shall not retransmit or redistribute AIS information** other than as approved and **shall not charge a fee**. **Satellite AIS is not included** (agencies cannot redistribute commercial sat-AIS). Alaska broadcast points removed after 2021-03-28 at Marine Exchange of Alaska request.  
- **Status:** `CONDITIONAL_REVIEW_REQUIRED` — public-domain planning use vs USCG no-redistribute/no-fee language is a **direct conflict that counsel must resolve** before any product featuring vessel tracks.  
- **Privacy:** vessel identity `NEVER_PUBLISH` in public FishAI maps; internal use `RESTRICTED`. **Not abundance.**

#### USCG real-time AIS

- **Status:** `RESTRICTED` — Level A/B entities, ISA, FOIA for others. Not a FishAI source.

#### Commercial AIS aggregators (MarineTraffic, VesselFinder, Spire, Orbcomm, ExactEarth)

- **Status:** `PAID_LICENSE_REQUIRED`  
- Scraping those sites: `REJECTED`  
- GFW TOS lists Orbcomm as a third-party provider whose terms also bind GFW users.

#### NOAA VMS

- **Policy 06-101:** https://media.fisheries.noaa.gov/dam-migration/06-101.pdf  
- **Program:** https://www.fisheries.noaa.gov/topic/enforcement/vessel-monitoring  
- **Key terms:** VMS confidential under MSA §§ 311(i) and 402(b); OLE + ACIO. Public disclosure prohibited except statutory exceptions.  
- **Status:** `RESTRICTED`  
- **Privacy:** `NEVER_PUBLISH`  
- **Wedge 3:** most inshore lobster boats are **not** in VMS anyway.

### 3.7 Partner operational data

| Source | Status | Privacy | Notes |
|---|---|---|---|
| Oyster farm sensors, mortality, growth, work logs, lease-level KPIs | `APPROVED_PARTNER_CONSENT` | `PRIVATE` | Trade secret. Training-use and commercial derivatives only if DPA allows. |
| Charter / CPFV operator’s own trip logs, GPS, catch/no-catch | `APPROVED_PARTNER_CONSENT` | `PRIVATE` | Distinct from CDFW’s confidential copy. Operator can share their original. |
| Commercial lobster harvester logbooks, trap hauls, soak times | `APPROVED_PARTNER_CONSENT` | `PRIVATE` | Core of wedge 3. Aggregation rule-of-3+ for any multi-vessel public product. |
| Buyer / processor tickets, prices, inventories | `APPROVED_PARTNER_CONSENT` | `PRIVATE` / `NEVER_PUBLISH` publicly | Antitrust + confidentiality. |
| Tribal co-management or TEK | `RESTRICTED` until nation agreement | `NEVER_PUBLISH` default | CARE: https://www.gida-global.org/careprinciples |

### 3.8 Threatened / listed species and Indigenous data

- **ESA take:** 16 U.S.C. § 1538 — listed Chinook ESUs; product must not authorize or facilitate illegal take.  
- **Critical habitat GIS (West Coast):** https://www.fisheries.noaa.gov/resource/map/critical-habitat-maps-and-gis-data-west-coast-region — public maps; **CFR text controls**; not a complete distribution. Status: `APPROVED_OPEN_COMMERCIAL` as habitat constraint, privacy `PUBLIC` at designated-habitat grain; **do not** publish finer poaching-relevant occurrence.  
- **CARE Principles:** https://www.gida-global.org/careprinciples — Collective Benefit, Authority to Control, Responsibility, Ethics. Complements FAIR. OBIS policy already requires CARE.  
- **Status of unconsented Indigenous data:** `REJECTED` / `RESTRICTED`.

### 3.9 Other / reject classes

| Family | Status | Reason |
|---|---|---|
| Paywalled journals, copyrighted full text | `REJECTED` for ingest; cite/summarize only | Copyright. |
| Social media scrape of fishing reports | `REJECTED` | TOS + location privacy + reliability. |
| Forum/spot-burning sites | `REJECTED` | Ethics + likely TOS. |
| Google Maps / Esri basemap tiles | `PAID_LICENSE_REQUIRED` or provider TOS | NWS disclaimer: third-party imagery separately licensed. OSM may be alternative (`APPROVED_WITH_ATTRIBUTION` under ODbL — if used, share-alike on the database). |
| ECMWF operational products | `PAID_LICENSE_REQUIRED` or C3S subset | Do not assume GFS/NWS = ECMWF. C3S via CMEMS may differ. |
| Observer data (MSA) | `RESTRICTED` | 16 U.S.C. § 1881a(b)(2). |

---

## 4. Wedge source map

### 4.1 Wedge 1 — Pacific oyster × Washington growing areas × 72h farm ops risk

**Usable now (with credits/disclaimers):** CMEMS / NOAA / NANOOS-if-licensed / NWS / CO-OPS / NDBC / Sentinel / Landsat / GEBCO / WoRMS taxon / NSSP **context**.

**Partner-gated:** farm sensors, mortality, handling windows, private lease performance.

**Blocked:** using DOH/FDA classification as a “harvest OK” score; GFW; confidential landings; tribal harvest data without consent; SoundToxins until license known.

**Highest legal risks:** (1) food-safety impersonation of WA DOH/FDA; (2) farm trade secrets in any public or cross-farm model; (3) treaty/tribal shellfish; (4) DOH website copyright for bulk GIS scrape of the viewer — use official bulk/public-records channels, not scraping.

### 4.2 Wedge 2 — Chinook × CA/OR coast × charter encounter 24–48h

**Usable now:** NOAA/CMEMS ocean and weather; ESA critical-habitat polygons as **avoid/constraint** layers; RecFIN **non-salmon** effort context if relevant; PFMC/NMFS **public** season notices as context; WoRMS/OBIS CC0-CC BY for occurrence **coarsened**.

**Partner-gated:** charter own logs (catch/no-catch, zone, effort).

**Blocked:** CDFW/ODFW confidential logs from the agency; GFW/AIS-as-abundance; public heatmaps of successful drifts; CC BY-NC OBIS/GBIF in production; RecFIN salmon if not actually published there.

**Highest legal risks:** (1) **ESA** — listed ESUs, Section 9 take, marketing that targets closed or weak-stock encounters; (2) **FGC § 8022** if FishAI ever received agency microdata; (3) **spot maps** that concentrate effort on remaining fish; (4) treaty fishery interactions. Counsel should review advertising claims (“you’ll find kings”) as potentially **catch guarantee + conservation** risk.

### 4.3 Wedge 3 — American lobster × Gulf of Maine × next-trip CPUE

**Usable now:** public DMR county/year landings; FOSS non-confidential; ASMFC public assessment; NERACOOS-if-licensed; CMEMS/NOAA SST, bottom temp if available, weather, GEBCO bathymetry (not navigation).

**Partner-gated:** haul-level CPUE, trap location (coarsened even internally), soak, bait, vessel identity.

**Blocked:** ACCSP/Maine confidential extracts without authorization; VMS; GFW commercial use; reconstructing individuals from suppressed cells.

**Highest legal risks:** (1) **statutory confidentiality** (MSA + 12 M.R.S. § 6173); (2) antitrust-adjacent sharing of prices across buyers; (3) publishing effort maps that reveal productive bottom to competitors. Not infeasible **with partners**. **Public-data-only next-trip CPUE is scientifically inadequate and must not be backfilled with confidential government files.**

---

## 5. Attribution and operational obligations if ingest proceeds later

| Source | Minimum operational control |
|---|---|
| CMEMS | Visible credit + product DOIs; traceability records; pass duty to customers if redistributing derived data. |
| Sentinel | “Copernicus Sentinel data [Year]” / “Contains modified…” |
| NWS/NOAA | No endorsement; 17 U.S.C. § 403 compilation notice; cache within published refresh rates. |
| GEBCO | Attribution + not-for-navigation notice in UI. |
| GBIF/OBIS | Per-dataset licence filter; DOI citations for each download; strip NC. |
| WoRMS | Citation + webservice (no full dump). |
| Partners | DPA, revocation, no public microdata. |
| GFW | Do not ingest for commercial product. |

---

## 6. What this register does not do

- Does not authorize ingest (none was performed).  
- Does not replace human counsel, insurance, or regulator engagement.  
- Does not interpret “fair use” as a plan to copy copyrighted reports.  
- Does not treat “the map is on a government website” as a commercial API licence (WA DOH viewer, GFW map, MarineTraffic).  
- Does not allow combining public AIS identity with partner catch to publish someone else’s fishing pattern.

---

## 7. Related artifacts

- `source_license_matrix.csv`  
- `privacy_and_sensitive_location_policy.md`  
- `partner_data_rights_template.md`  
- `legal_review_queue.md`  
- `agent_handoff.md`
