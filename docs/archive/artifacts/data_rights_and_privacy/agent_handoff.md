# Agent handoff — DATA_RIGHTS_AND_PRIVACY_AGENT

**Project:** Ocean Intelligence Builder / FishAI  
**Agent:** DATA_RIGHTS_AND_PRIVACY_AGENT  
**Date:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/artifacts/data_rights_and_privacy/`  
**Ingest:** none. **Counsel:** none. This is not legal advice.

---

## 1. Executive finding

None of the three candidate wedges is **categorically legally infeasible**, provided FishAI stays a decision-support product (no fishing licence, no navigation/weather-safety, no shellfish sanitation stamp, no catch guarantee), refuses confidential government microdata and GFW/CC BY-NC, coarsens public maps, and obtains signed partner DPAs for operational labels.

**Usable now for catalog/design (with attribution, still no ingest):** Copernicus Marine (commercial derivatives + credit + traceability), Copernicus Sentinel data, NOAA-created weather/tides/buoys, NASA-led CC0 Earthdata, GEBCO (not for navigation), USGS Landsat, public FOSS/DMR/RecFIN **aggregates**, NMFS public habitat/season documents, WoRMS webservices, OBIS/GBIF **CC0/CC BY only**.

**Blocked:** Global Fishing Watch (CC BY-NC / no public commercial licence), VMS, USCG live AIS, PacFIN/ACCSP/CA FGC § 8022/Maine 12 M.R.S. § 6173 confidential files, CC BY-NC biodiversity, NASA CSDA sats, scraping, unconsented tribal data, public spot maps, SoundToxins until licensed, Marine Cadastre AIS until counsel resolves public-domain vs no-redistribute.

**Highest risks:** (1) oyster — impersonating WA DOH/FDA NSSP harvest authority + farm trade secrets; (2) Chinook — **ESA take facilitation** + CPFV confidentiality + hot-spot maps; (3) lobster — statutory CPUE confidentiality; public tables cannot lawfully or scientifically replace partner logbooks.

Wedge 3 without partners is **not illegal as a public-aggregate dashboard**, but **is legally and scientifically infeasible as next-trip CPUE**. Wedge 2 is the highest counsel-priority. Wedge 1 is the cleanest **if** food-safety claims are structurally impossible in the UI.

---

## 2. Evidence table

| Finding | Evidence | Confidence |
|---|---|---|
| CMEMS allows any-purpose value-added products if credited and traceability records kept | Licence https://marine.copernicus.eu/user-corner/service-commitments-and-licence accessed 2026-09-18 | High on posted text |
| NOAA-created NWS data public domain with endorsement/official-use limits | https://www.weather.gov/disclaimer | High |
| NASA-led unmarked Earthdata default CC0; CSDA is noncommercial | https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance | High |
| GBIF/OBIS are per-dataset CC0 / CC BY / CC BY-NC | https://www.gbif.org/terms ; https://manual.obis.org/policy.html | High |
| GFW TOS + FAQ: noncommercial CC BY-NC; commercial needs custom licence; scraping banned | https://globalfishingwatch.org/terms-of-use/ ; commercial FAQ | High |
| MSA + NAO 216-100 + 50 CFR 600.4xx confidential fisheries stats | 16 U.S.C. § 1881a; NOAA NAO 216-100 | High |
| CA CPFV/landing records confidential | FGC § 8022; CDFW MFSU | High |
| ME landings microdata confidential; public county/year tables exist | 12 M.R.S. § 6173; DMR Ch. 5; DMR historical data page | High |
| ACCSP public rule of 3 (dealers AND fishermen AND vessels) | ACCSP data warehouse page | High |
| GEBCO public domain commercial use; not for navigation | https://www.gebco.net/data-products/gridded-bathymetry/terms-of-use | High |
| WA DOH maps exist but site copyright is not an open licence | DOH growing areas + privacy/copyright page | Medium (reuse path unclear) |
| NSSP/ISSC is the harvest-safety authority, not FishAI | FDA 2023 NSSP Guide; ISSC | High (program role) |
| IOOS RA datasets often lack a licence field | NANOOS ERDDAP legal.html; catalog “No License Provided” | High that it is conditional |
| Marine Cadastre AIS terms internally in tension | AIS FAQ May 2026 vs USCG sharing instruction language | Medium — counsel must resolve |
| RecFIN CTE001 excludes salmon | RecFIN report notes | High for that report; other salmon products not fully licensed here |
| CARE required for Indigenous data | https://www.gida-global.org/careprinciples ; OBIS policy | High as ethics/policy; legal form is nation-specific |

---

## 3. Source / licence table (summary)

Full matrix: `source_license_matrix.csv`.

| Family | Status class | Privacy default |
|---|---|---|
| CMEMS | `APPROVED_WITH_ATTRIBUTION` | `PUBLIC` |
| Sentinel data | `APPROVED_WITH_ATTRIBUTION` | `PUBLIC` |
| NOAA-created env | `APPROVED_OPEN_COMMERCIAL` | `PUBLIC` |
| NASA-led CC0 | `APPROVED_OPEN_COMMERCIAL` | `PUBLIC` |
| NASA CSDA | `NONCOMMERCIAL_ONLY` | `RESTRICTED` |
| GEBCO | `APPROVED_WITH_ATTRIBUTION` | `PUBLIC` |
| Landsat USGS | `APPROVED_OPEN_COMMERCIAL` | `PUBLIC` |
| WoRMS webservice | `APPROVED_WITH_ATTRIBUTION` | `PUBLIC` |
| OBIS/GBIF CC0-CC BY | `APPROVED_WITH_ATTRIBUTION` | `COARSENED` |
| OBIS/GBIF NC | `NONCOMMERCIAL_ONLY` | `COARSENED` |
| IOOS RA | `CONDITIONAL_REVIEW_REQUIRED` | `PUBLIC` |
| FOSS/DMR/RecFIN public aggregates | `APPROVED_OPEN_COMMERCIAL` | `PUBLIC`/`COARSENED` |
| Confidential fisheries / VMS / observer | `RESTRICTED` | `NEVER_PUBLISH` |
| WA DOH growing areas | `CONDITIONAL_REVIEW_REQUIRED` | `COARSENED` |
| NSSP Guide (US gov text) | `APPROVED_OPEN_COMMERCIAL` as **citation** | `PUBLIC` |
| GFW | `NONCOMMERCIAL_ONLY` | `RESTRICTED` |
| Marine Cadastre AIS | `CONDITIONAL_REVIEW_REQUIRED` | `NEVER_PUBLISH` identity |
| Commercial AIS | `PAID_LICENSE_REQUIRED` | `NEVER_PUBLISH` |
| Partner logs | `APPROVED_PARTNER_CONSENT` | `PRIVATE` |
| Tribal/TEK | `RESTRICTED` | `NEVER_PUBLISH` |
| Scraping / forums | `REJECTED` | `NEVER_PUBLISH` |

---

## 4. Confidence and limitations

- **High** where a named licence/statute page was read on 2026-09-18 (CMEMS, GFW TOS, GEBCO, NWS, MSA, ME statute, FGC 8022, CARE, Sentinel legal notice).
- **Medium** for WA DOH reuse, IOOS dataset licences, Marine Cadastre AIS redistribution, RecFIN salmon substitutes, ASMFC PDF copyright.
- **Low / UNKNOWN** for SoundToxins and any source not in the matrix.
- GBIF.org/terms HTML fetch **timed out**; classification used search snippets of the official URLs plus the data-user agreement URL. Counsel should re-read live pages.
- This agent is **not counsel**. Classifications can be wrong, incomplete, or outdated the day after posting. Licences change (CMEMS §8; GFW TOS “effective immediately”).
- No robots.txt crawl of bulk endpoints was used to green-light ingest.
- HiveClaw/other repos were not treated as FishAI licence grants.

---

## 5. Recommended decision (for founder + counsel, not locked)

1. Keep all three wedges **research-eligible**; do not kill any on legal infeasibility.  
2. If choosing on **legal friction alone**: **oyster ops-risk first** (environmental stack is the cleanest; risk is claims, which engineering can hard-block).  
3. Treat **Chinook** as requiring an ESA/advertising memo before a public map.  
4. Treat **lobster next-trip CPUE** as **partner-contingent**; do not plan ACCSP confidential access for a startup product.  
5. Implement licence allowlists (deny GFW, NC, VMS, scrape) in geospatial design **before** any pipeline exists.  
6. Hire/engage **human legal review** (LR-001–008) before ingest.

---

## 6. Rejected alternatives

| Alternative | Why rejected |
|---|---|
| Scrape GFW / MarineTraffic / DOH viewer as “the map is public” | TOS, NC licence, copyright page, USCG rules, ethics |
| Use AIS/VMS/GFW as abundance or CPUE | Scientifically false and legally restricted |
| Build lobster CPUE from confidential DMR/ACCSP extracts without authorization | Unlawful |
| Use RecFIN CTE001 as Chinook labels | Report excludes salmon |
| Train on GBIF/OBIS mixed downloads without licence filter | NC contamination |
| Publish heatmaps of charter success or farm beds | Privacy policy + ESA + trade secret |
| Claim harvest “Approved” from a model | NSSP/WA DOH role; product ban |
| CSDA or ECMWF operational without paying | EULA / paid licence |
| Treat IOOS “free download” as a commercial licence | Often no licence field |

---

## 7. Follow-ups

- Counsel closes `legal_review_queue.md` P0.  
- DATA_DISCOVERY / GEOSPATIAL: implement per-dataset licence field; CC filter; CMEMS DOI registry; NWS cache policy.  
- PRODUCT: hard-coded disclaimers and disabled claim vocabulary (`safe`, `legal`, `guaranteed`, `hot spot`).  
- REQUIREMENTS: founder confirms whether v1 is partner-only or has a public map (changes AIS/DOH/ESA exposure).  
- QUALITY: reverse-engineering tests for coarsened maps.  
- Re-read GBIF terms HTML (fetch timeout).  
- Identify CDFW OSP / ODFW salmon estimate licence pages.  
- Contact WA DOH webmaster / data steward for growing-area GIS — do not scrape.  
- If GFW is ever strategic, email `apis@globalfishingwatch.org` for a custom licence; until then, deny.

---

## 8. Artifacts written

All under `/Users/wijeratne/dev/fishai/artifacts/data_rights_and_privacy/`:

1. `data_rights_register.md`  
2. `source_license_matrix.csv`  
3. `privacy_and_sensitive_location_policy.md`  
4. `partner_data_rights_template.md`  
5. `legal_review_queue.md`  
6. `agent_handoff.md` (this file)

---

## 9. Red-team needed?

**Yes.** Scientific and legal red-team should attack: (a) ESA facilitation via Chinook UX; (b) NSSP impersonation via oyster UX; (c) re-identification of lobster/charter/farm from “coarsened” tiles; (d) licence-filter bypass (NC + CMEMS mixed products + IOOS empty licence); (e) AIS identity leakage. Not done in this folder.

---

## 10. Next experiment

**Do not ingest.** Next lawful experiment:

1. Paper allowlist: for a single wedge, list 10 datasets with licence URL, status class, and privacy tier — reject any `UNKNOWN`/`NC`/`RESTRICTED`.  
2. Dummy (synthetic) coarsening test: show that a public H3/area layer cannot recover planted secret GPS.  
3. Draft UI with prohibited-claim checklist; legal review of screenshots.  
4. One **unsigned** DPA walkthrough with a hypothetical farm or charter using the template.

Stop condition: any proposal to scrape, to pull confidential landings, or to ship a spot map.
