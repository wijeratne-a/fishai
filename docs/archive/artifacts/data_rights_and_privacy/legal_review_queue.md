# Legal review queue — FishAI

**Status:** COUNSEL INTAKE LIST, NOT LEGAL ADVICE  
**Date:** 2026-09-18  
**Rule:** Nothing in `READY_FOR_INGEST_DESIGN` may be ingested until the named human review is closed. This agent did not ingest data.

Priority: **P0** blocks all wedges or a specific wedge’s core label. **P1** blocks a planned feature. **P2** hygiene before launch.

---

## P0 — close before any production path or partner DPA signature

| ID | Question for counsel | Why it matters | Wedge | Current class | Blocked until |
|---|---|---|---|---|---|
| LR-001 | Confirm product-claim rails: no fishing authorization, no nav/weather-safety, no NSSP harvest/food-safety stamp, no catch guarantee — sufficient vs FTC/state UDAP and sector regulators? | Core company risk on all marketing and UI | All | Product policy | Disclaimer + UI review signed |
| LR-002 | May a commercial product use CMEMS derivatives if we implement visible credit, DOI list, and **downstream record-keeping** (licence §2.6)? | Primary physics source | All | `APPROVED_WITH_ATTRIBUTION` | Attribution/records design approved |
| LR-003 | Chinook encounter product for **listed ESUs**: ESA §9 take facilitation, advertising, and map grain. Is relative 24–48h encounter-likelihood for licensed charters defensible if seasons are only linked, not restated as permission? | Highest biological-law risk | 2 | Product + ESA | Written ESA memo; possibly NMFS informal consult |
| LR-004 | Is **next-trip lobster CPUE** lawful if labels come **only** from partner logbooks under DPA, never ACCSP/Maine/NMFS confidential files? | Wedge 3 is otherwise label-blocked | 3 | `APPROVED_PARTNER_CONSENT` vs `RESTRICTED` | DPA + no-gov-microdata warranty |
| LR-005 | WA DOH growing-area **viewer/GIS bulk reuse** for a commercial ops-risk tool (context only, not harvest OK). Copyright page tells users to contact webmaster; no CC licence found. | Wedge 1 context layer | 1 | `CONDITIONAL_REVIEW_REQUIRED` | Written DOH permission **or** public-records extract with reuse terms |
| LR-006 | CARE / treaty: any use of tribal usual-and-accustomed areas, TEK, or co-managed harvest as features? Default is deny. | Sovereignty | All, esp. 1–2 | `RESTRICTED` | Nation protocol or explicit exclusion in product spec |
| LR-007 | Marine Cadastre historical AIS: FAQ says generally public domain **and** restates USCG no-redistribute / no-fee / purpose-limited terms. Can FishAI even store tracks internally? | Identity + TOS conflict | 2, 3 | `CONDITIONAL_REVIEW_REQUIRED` | Counsel opinion; default **do not ingest** |
| LR-008 | GFW: confirm commercial FishAI **cannot** use APIs or CC BY-NC datasets, including “internal R&D that supports a commercial product” (GFW FAQ + TOS). | Easy unlawful ingest | All | `NONCOMMERCIAL_ONLY` | Exclusion in pipeline allowlist |

---

## P1 — close before the named feature

| ID | Question | Feature | Wedge | Class | Notes |
|---|---|---|---|---|---|
| LR-009 | Per-dataset IOOS/NANOOS/NERACOOS/CENCOOS licence harvest: many catalog records “No License Provided”. Protocol for NOAA-produced vs university vs tribal sensors. | Coastal in situ | All | `CONDITIONAL_REVIEW_REQUIRED` | Dataset allowlist, not RA-wide |
| LR-010 | GBIF/OBIS production filter: drop CC BY-NC; keep DOI citations; CARE. Liability if a publisher mislabelled NC? | Biodiversity context | All | Mixed | Pipeline test required |
| LR-011 | WoRMS: webservice vs full DB dump; images CC BY-NC-SA. OK to cache taxon matches? | Taxonomy authority | All | `APPROVED_WITH_ATTRIBUTION` | No full redistributable copy |
| LR-012 | RecFIN CTE001 **excludes salmon**. What is the licence for CDFW Ocean Salmon Project / ODFW salmon estimates used as **public** (not confidential) time series? | Chinook labels from public estimates | 2 | Unknown until product identified | Do not assume RecFIN |
| LR-013 | FGC § 8022 vs partner sharing **their own** CPFV operational copy. Any prohibition? | Charter DPA | 2 | `APPROVED_PARTNER_CONSENT` | Template §B1 |
| LR-014 | SoundToxins / ORHAB / other HAB: license unspecified. | Oyster context | 1 | `UNKNOWN` | Written provider terms |
| LR-015 | NASA Earthdata: confirm no CSDA commercial-sat collections in the stack. | SST/ocean color | All | Mixed | Collection-level EULA check |
| LR-016 | Sentinel vs Data Space portal TOS (portal chrome NC). | Shoreline/color | 1, 2 | Split | Use Sentinel legal notice for data |
| LR-017 | Buyer/processor price data: antitrust if cohort benchmarks. | Optional commercial layer | 1, 3 | `APPROVED_PARTNER_CONSENT` | Default silo |
| LR-018 | OpenStreetMap ODbL share-alike vs Google/Esri paid tiles for the app basemap. | UX map | All | Mixed | Pick one; don’t scrape |
| LR-019 | Publishing coarsened public zone scores trained on partner data: is that a commercial derivative requiring extra Partner opt-in? | Public app | All | DPA §E | Default opt-in false |
| LR-020 | Model weights: are partner-trained weights a “distribution” of CMEMS/GBIF requiring credit pass-through in the app only, or also in weight cards? | ML release | All | Attribution | CMEMS §2.6 descending licences |

---

## P2 — launch hygiene

| ID | Question | Notes |
|---|---|---|
| LR-021 | 17 U.S.C. § 403 compilation notice for NOAA-heavy UIs. | NWS/CO-OPS |
| LR-022 | GEBCO not-for-navigation notice in every bathymetry view. | All wedges |
| LR-023 | NWS rate-limit / abuse policy; caching design. | Weather |
| LR-024 | CMEMS account SLA: login non-transferable; GDPR of user records vs Company CRM. | EU |
| LR-025 | Insurance: professional disclaimer vs implied safety for going to sea. | Product |
| LR-026 | California CCPA/CPRA, WA, ME consumer/employee GPS if any personal data. | Partners |
| LR-027 | Export of vessel/location time series. | Unlikely ITAR but check |
| LR-028 | Copyright in ASMFC/PFMC PDFs — cite/summarize, no corpus ingest. | RAG later |
| LR-029 | FOSS/DMR public landings: prohibition on re-identification / mosaic with partner data. | Wedge 3 |
| LR-030 | Marketing review: words “safe”, “legal”, “approved”, “guaranteed”, “hot spot”. | All |

---

## Ready vs blocked (ingest design, still no ingest)

### May proceed to **pipeline design / allowlist drafting** (not ingest) now

- CMEMS, Sentinel data, NOAA-created NWS/NDBC/CO-OPS/NCEI-produced, USGS Landsat, GEBCO, NOAA FOSS non-confidential, Maine DMR public tables, RecFIN published non-salmon estimates, NMFS public critical habitat and season notices, WoRMS webservice, OBIS/GBIF **after** CC0/CC BY filter design.

### Blocked for design-as-if-approved

- GFW, VMS, USCG live AIS, confidential PacFIN/ACCSP/CPFV/Maine microdata, CC BY-NC biodiversity, CSDA sats, scraping, SoundToxins until terms, AIS identity layers, tribal data, DOH viewer scrape, public spot maps.

### Partner DPA

- Required before any ground-truth for all three wedges. Template in `partner_data_rights_template.md` is **not** signed.

---

## Suggested counsel packet

Provide:

1. This queue  
2. `data_rights_register.md`  
3. `source_license_matrix.csv`  
4. Product UI disclaimer draft (register §2.2)  
5. Three wedge one-pagers (register §4)  
6. Any founder answers on: commercial vs research entity, whether a public consumer map is in v1, and whether tribal partnership is in scope  

**Requested output from counsel:** go/no-go per source family; ESA memo for wedge 2; confidentiality memo for wedge 3; DOH reuse path for wedge 1; DPA revisions.

---

## Logging

| Date | Agent | Action |
|---|---|---|
| 2026-09-18 | DATA_RIGHTS_AND_PRIVACY_AGENT | Opened queue from public licence pages. No ingest. No attorney-client relationship created. |
