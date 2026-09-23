# DATA_DISCOVERY_AGENT handoff

**Date:** 2026-09-18 (W1 GT relabel)  
**Project:** Ocean Intelligence Builder / FishAI  
**Wedge:** UNRESOLVED  
**Ingest performed:** none (metadata probes only)  
**Correction:** WA DOH closures are **not** W1 ops GT. See `ground_truth_relabel_W1.md`.

## Executive finding

The three candidate wedges are **not data-equivalent**. Shared NOAA/Copernicus physics and NWS weather can support any of them. **Labels at the advertised horizon cannot.**

**Corrected W1 GT:** `ops_disruption_72h` = partner farm **mortality / workability / intervention**. Public DOH commercial closures are an official **harvest legally open?** **constraint** and **user-facing authority link**. They miss heat-kill and gear damage when harvest stays legally open. Training ops-stress on closures, or ops-stress copy as harvest legality, is a **BLOCKER** (WAC 246-282-006). Never impersonate NSSP/WA DOH.

**W1 is still the best lawful *constraint + covariate* path (yes):** estuary in situ (NANOOS/NERRS) plus 72 h NOAA/Copernicus/NWS plus a public harvest-open overlay, without confidential catch microdata. That is **not** a claim that W1 has public ops labels. Hood Canal ORCA ≠ Willapa instrumentation.

**W2 (Chinook × CA/OR × 24–48 h charter encounter)** has a clean, mostly federal feature stack (WCOFS, MUR, PFEL upwelling, chlorophyll, waves) but **cannot support a 24–48 h claim** on RecFIN/ODFW latency. RecFIN CTE001 **excludes salmon**. Partner CPFV logs are mandatory. 2026 seasons are tightly quota-constrained; closed days must be hard zeros.

**W3 (lobster × GOM × next-trip CPUE)** has the best *in situ* process data (eMOLT bottom temperature, NERACOOS, GoMOFS 72 h) and the worst *lawful CPUE* path (LEEDS/VTR confidential; public landings lack effort). Do not build a public CPUE model from monthly pounds.

Licenses: Copernicus Marine and GEBCO commercial terms were **retrieved**. Most state/IOOS/academic sources remain **UNKNOWN**. Every catalog row is **CONDITIONAL_REVIEW_REQUIRED**. Visual access is not commercial use.

## Evidence (what was actually checked)

| Claim | Evidence | Strength |
|-------|----------|----------|
| Seattle tide station exists and is forecast-capable | CO-OPS MDAPI 9447130 JSON, 2026-09-18 | Direct |
| Pacific oyster accepted name *Magallana gigas* | WoRMS REST Aphia 836033 | Direct |
| Chinook Aphia 158075 | WoRMS REST | Direct |
| American lobster Aphia 156134 | WoRMS taxon page | Direct |
| MUR SST ERDDAP live through 2026-09-17, 0.01° | `jplMURSST41` info JSON | Direct |
| NANOOS ERDDAP serving ORCA Hood Canal moorings | ERDDAP catalog index JSON | Direct |
| CMEMS global PHY/BGC/WAV IDs and 10-day forecast | Product pages | Direct |
| CMEMS commercial use + attribution | Licence page 2026-09-18 | Direct |
| GEBCO commercial use, not navigation | GEBCO_2026 terms | Direct |
| NWS API public domain + User-Agent + unpublished rate limit | NWS API docs / disclaimer | Direct |
| RecFIN CTE001 excludes salmon | CTE001 report text | Direct (rechecked; no error) |
| ODFW publishes weekly ocean salmon catch/effort PDFs | Catch index page (through 30 Aug 2026) | Direct |
| Maine lobster public tables are monthly pounds/value by zone | DMR landings pages / LobByCntyMoZone.pdf | Direct |
| VTR confidential, rule-of-3 public | InPort 1423 + NAO 216-100 | Direct (rechecked; no error) |
| LEEDS harvester microdata not public | Reporter portal; DMR landings program | Direct (rechecked; no error) |
| NOMADS OpenDAP retired 23 Feb 2026 | NWS/community notices | Secondary |
| LiveOcean ~72 h Salish Sea forecast + known BGC biases | UW data-access page (full fetch timed out once; URLs from search-verified official pages) | Medium |
| SoundToxins is partner-gated | Program/NCCOS descriptions | Medium |
| FOSS guest portal | InPort; this environment received Access Denied on fisheries.noaa.gov/foss | Medium |

Taxonomy probes did **not** pull occurrence dumps from OBIS/GBIF.

## Source / license table (P0 and rights-critical)

| source_id | Commercial? | Redistribute? | Attribution | Review |
|-----------|-------------|---------------|-------------|--------|
| CMEMS-GLO-PHY-001-024 (and WAV/BGC) | YES (licence retrieved) | YES originals | YES | CONDITIONAL (registration, credit wording) |
| GEBCO-2026-GRID | YES | YES | YES | CONDITIONAL (not navigation) |
| NWS-API-FORECAST | YES (disclaimer) | YES | YES (no endorsement) | CONDITIONAL |
| NOAA CO-OPS / WCOFS / GoMOFS / NDBC / GFS-Wave / PFEL | CONDITIONAL (U.S. Gov typical) | CONDITIONAL | YES | CONDITIONAL_REVIEW_REQUIRED |
| NOAA-MUR-SST-v4.1 | CONDITIONAL (PO.DAAC/Earthdata) | CONDITIONAL | YES | CONDITIONAL_REVIEW_REQUIRED |
| UW-LIVEOCEAN | **UNKNOWN** | **UNKNOWN** | YES | **Blocker for paid W1 if unlicensed** |
| NANOOS / NERACOOS / eMOLT ERDDAP | UNKNOWN / NOAA as-is | CONDITIONAL | YES | CONDITIONAL; bin eMOLT positions |
| WDOH closures / viewer | UNKNOWN | UNKNOWN | YES | Request export; **do not scrape**; **constraint only**; no NSSP impersonation |
| SOUNDTOXINS | UNKNOWN | NO (partner) | YES | DUA |
| RecFIN / CRFS / ODFW weekly | UNKNOWN | UNKNOWN | YES | Public reports only; no raw interviews; not CTE001 for salmon |
| ME-DMR-LANDINGS PDFs | UNKNOWN | UNKNOWN | YES | Public aggregates OK to cite |
| ME-DMR-HARVESTER-LEEDS | **NO** microdata | **NO** | YES | DUA |
| NOAA-VTR-GARFO | **NO** | **NO** | YES | NAO 216-100 |
| OBIS / GBIF | CONDITIONAL per dataset | CONDITIONAL | YES | Strip CC BY-NC |
| PARTNER logs (all wedges) | CONDITIONAL contract | NO | YES | DUA before any model claim; W1 ops GT lives here |

## Confidence

| Item | Confidence | Reason |
|------|------------|--------|
| W1 is the best lawful **constraint + covariate** path | **High** | Public harvest-open overlay + IOOS in situ + NOAA/Copernicus physics; **not** public ops labels |
| DOH closures are the wrong ops-stress label | **High** | Sibling marine-domain, validation, red-team, and rights findings; WAC 246-282-006 |
| W3 has best catchability physics | **High** | eMOLT + GoMOFS 72 h |
| W2 24–48 h encounter is not supportable on public GT | **High** | Weekly/monthly estimates only; CTE001 excludes salmon |
| LiveOcean may be used commercially today | **Low** | Terms UNKNOWN |
| State HTML portals are a stable API | **Low** | PDF/HTML fragility documented |
| Catalog completeness vs all possible ocean data | **Medium** | Minimum-sufficient, not encyclopedic |

## Recommended decision

1. **If the founder needs one wedge now:** lock **W1 Pacific oyster / Washington / 24–72 h operational disruption**, scoped as **ops risk** (`ops_disruption_72h` from farms), **plus** a separate official harvest-open constraint. Never as NSSP authorization or vibrio-safe-to-eat.  
2. **Day-1 covariate stack:** NWS + CO-OPS + USGS (conditional harvest-open hydrology) + NANOOS ORCA/NVS + WCOFS + CMEMS PHY fallback + WoRMS.  
3. **Day-1 constraint:** DOH harvest-open status as an **authority link**, not `y`.  
4. **Day-1 label path:** grower NDAs. Do **not** wait for LiveOcean or SoundToxins to start covariates; **do** wait for farm logs before claiming ops-stress skill.  
5. **Keep W3 as the physics research track** (eMOLT/GoMOFS) only if a lobster association will share trip CPUE under DUA within 30 days.  
6. **Park W2** until ≥1 charter partner stream exists; otherwise the product becomes a weather/regs dashboard, not an encounter model.

## Rejected alternatives (this agent)

| Alternative | Why rejected |
|-------------|--------------|
| Train W1 ops-stress on DOH/NSSP closures | Wrong label; WAC 246-282-006 blocker; misses heat-kill when harvest is open |
| Build all three wedges’ data lakes now | Violates minimum-sufficient; triples confidential-data burden |
| Scrape DOH/ODFW/CDFW as GT | TOS/robots; brittle; counsel risk; DOH is not ops GT |
| Use RecFIN CTE001 for Chinook | Salmon explicitly excluded |
| Train lobster CPUE on monthly DMR pounds | No effort denominator |
| Lead with VTR/LEEDS | Lawful but slow; partner logs first; still confidential |
| Lead with ICES/FAO/Argo/GBIF | Wrong basin or wrong horizon |
| New buoys/cameras first | Violates acquisition ladder |
| Ship LiveOcean-derived paid layers without terms | Rights UNKNOWN |
| Food-safety or catch-guarantee SKU | NSSP/MSA and honesty constraints |

## Follow-ups (other agents / humans)

- **DATA_RIGHTS_AND_PRIVACY:** LiveOcean, SoundToxins, DOH GIS **as constraint**, RecFIN QueryBuilder, eMOLT positions, partner DUAs.  
- **MARINE_DOMAIN:** W1 target is ops disruption not vibrio/PSP legal determination — **aligned after this relabel**.  
- **VALIDATION:** labels = partner `ops_disruption_72h`; DOH = context column.  
- **GEOSPATIAL:** WGS84 exchange; source-local time for tides; H3 vs growing-area polygons vs PFMC areas vs DMR zones.  
- **Founder / BD:** three WA growers (**include Willapa**, not only Hood Canal), five CA/OR charters, eight GOM boats — only after wedge lock.  
- **Counsel:** commercial use of state portals and IOOS ERDDAP mirrors; WAC 246-282-006 product-copy review.

## Artifacts

| File | Contents |
|------|----------|
| `artifacts/data_discovery/data_catalog.csv` | 56 sources × required columns, 0–1 scores (DOH rescored) |
| `artifacts/data_discovery/source_gap_analysis.md` | Critical gaps, GT vs constraint tables |
| `artifacts/data_discovery/data_source_priority_queue.md` | Top 10 after relabel + P0 constraint callout |
| `artifacts/data_discovery/data_acquisition_plan.md` | Public→agency constraint→partner **label** |
| `artifacts/data_discovery/scoring_and_verification.md` | Formula, probes, relabel note |
| `artifacts/data_discovery/ground_truth_relabel_W1.md` | Sibling-agent conflict table |
| `artifacts/data_discovery/_build_catalog.py` | Regenerator (no data download) |

## Red-team?

**Yes — this relabel is the response to the harvest-legality blocker.** Re-run product-copy review before any public demo.

Attack surface still visible:

- Product copy that sounds like harvest **authorization** (NSSP / WAC 246-282-006) or a **catch guarantee**.  
- Publishing eMOLT/charter/lobster coordinates.  
- Using CC BY-NC or partner HAB maps in a paid app.  
- Treating OFS/GEBCO as navigation.  
- HTML scraping presented as “official API.”  
- 24–48 h Chinook skill claimed from weekly PDFs.

## Next experiment (no bulk ingest)

**Exp-DD-001 (recommended if W1 favored):**  
On **one** WA growing area, join 14 days of NWS, CO-OPS, and a **single** NANOOS station as **covariates**. Record DOH harvest-open status as a **constraint column**. Labels, if any, come only from a grower spreadsheet (`ops_disruption_72h`). Success = a day table with licenses recorded and **two distinct columns** (constraint vs label) — not a model. If the site is Hood Canal/ORCA, document that Willapa is out of sample.

**Exp-DD-002 (if W3 favored):**  
Bin eMOLT temperatures to DMR zone (not GPS) for 14 days and compare to **public** zone-month seasonality only. Success = proof that catchability features can be built without confidential CPUE. Do **not** claim CPUE skill.

**Exp-DD-003 (do not run as first):**  
Charter encounter. Blocked until partner logs exist.

## Return summary for parent orchestrator

- **Top 10 overall (after relabel):** GoMOFS, NWS API, WCOFS, LiveOcean, CO-OPS, eMOLT, NANOOS ORCA, CMEMS PHY, GFS-Wave, NANOOS NVS growers. DOH closures are P0 **constraint** (SPS 0.745), not #1 GT.  
- **Corrected W1 GT:** partner `ops_disruption_72h` (mortality, workability, intervention).  
- **Critical gaps:** W1 farm-level GT + Willapa vs Hood Canal; W2 24–48 h labels (CTE001 still excludes salmon); W3 confidential CPUE (LEEDS/VTR still NO).  
- **Best lawful constraint + covariate path:** **Yes, W1.**
