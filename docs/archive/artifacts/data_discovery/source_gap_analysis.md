# Source gap analysis

**Date:** 2026-09-18 (W1 GT relabel)  
**Wedge status:** UNRESOLVED (three candidates cataloged)  
**Score scale:** 0–1 (see `scoring_and_verification.md`)  
**Label correction:** see `ground_truth_relabel_W1.md`

FishAI does not yet have a locked wedge. The lawful, minimum-sufficient data path is **not equal** across candidates. Physics and weather are strong for all three. **Ground truth at the decision horizon** is the binding constraint.

## Candidate definitions (decision units)

| ID | Species | Geography | User | Horizon | Decision | Explicitly not |
|----|---------|-----------|------|---------|----------|----------------|
| W1 | Pacific oyster (*Magallana gigas*, Aphia 836033; synonym *Crassostrea gigas*) | Washington growing areas | Farm operator | 24–72 h | Operational stress / disruption (`ops_disruption_72h`) | Food-safety legal harvest authorization (NSSP / WA DOH / WAC 246-282-006) |
| W2 | Chinook (*Oncorhynchus tshawytscha*, Aphia 158075) | Bounded CA/OR coast | Charter captain | 24–48 h | Relative encounter likelihood | Catch guarantee / abundance census |
| W3 | American lobster (*Homarus americanus*, Aphia 156134) | Bounded GOM statistical area | Commercial operator | Next trip | Expected CPUE / effort allocation | Exact abundance |

## What is already good enough (do not over-collect)

Shared, high-value public physics/weather (resilience set):

- Copernicus Marine global physics (commercial-allowed with attribution; registration).
- NOAA WCOFS (West Coast) and GoMOFS (GOM) 72 h coastal OFS.
- NWS API, CO-OPS tides/station met, NDBC, GFS-Wave.
- MUR 1 km SST (Earthdata/PO.DAAC terms CONDITIONAL) with NOAA geo-polar SST fallback.
- GEBCO (commercial-allowed, **not navigation**) plus NOAA coastal relief for inshore.

These improve lead time and defensibility. They do **not** close the outcome gap.

## Critical gaps by wedge

### W1 — Pacific oyster × WA growing areas × 24–72 h farm ops risk

**Corrected GT:** the training label is `ops_disruption_72h` from **partner farm logs** (mortality, workability, intervention). It is **not** WA DOH growing-area class or commercial closures.

**Must-show constraint (not a label):** WA DOH commercial closures and classification are the official answer to **“is harvest legally open?”** Link users to that authority. Do not impersonate NSSP/WA DOH. Do not train the ops-stress model on closures. Public closures **miss heat-kill and gear damage when harvest stays legally open.**

**Gaps that still break a 72 h ops-risk product:**

1. **Farm-true outcomes.** Partner farm logs do not exist in this repo. WAHH harvest reports are administrative, lagged, confidential, and are **not** mortality/workability labels.
2. **Willapa / Grays Harbor vs Hood Canal.** NANOOS ORCA (Twanoh, Hoodsport, Dabob) is excellent Hood Canal / some Puget Sound **covariates**. **Hood Canal ORCA ≠ Willapa instrumentation.** ORCA is not a Willapa farm label.
3. **LiveOcean rights.** Estuary-resolving ~72 h T/S/O2. Commercial terms **UNKNOWN**. WCOFS is the NOAA fallback but coarser in fjords.
4. **HAB cell data access.** SoundToxins is a leading **covariate** (partner-gated), not a legal reopen authority and not the ops GT.
5. **Machine-readable harvest-open history.** The live DOH closure report is HTML. A constraint archive may require a **DOH data request**, not scraping fortress.wa.gov. That archive still is not `ops_disruption_72h`.
6. **Conditional rainfall harvest-open rules.** USGS discharge + NWS precip can inform *when* Conditionally Approved areas may trip NSSP rules. Those rules are area-specific, not an open API, and are **constraints**, not mortality labels.

**Ground-truth vs constraint sources (W1):**

| Role | Source | Lawful path | Horizon fit |
|------|--------|-------------|-------------|
| **Ops GT (label)** | Partner farm logs: mortality, workability, intervention | Contract / DUA | Daily / 24–72 h |
| Harvest-open **constraint** + authority link | WDOH commercial closures + classification viewer | Public view; redistribution UNKNOWN; request GIS/history | Event-scale, hours |
| Administrative harvest volume (not ops GT) | WDFW WAHH | Agency DUA | Monthly, not 72 h |
| Leading covariate, not legal reopen, not ops GT | SoundToxins, PNW HAB Bulletin, ESP pDA | Partner / public bulletin | Hours–days |
| In situ covariates (Hood Canal ≠ Willapa) | NANOOS ORCA / NVS / NERRS Padilla Bay | Cite metadata; commercial UNKNOWN | Minutes–hours |

### W2 — Chinook × CA/OR coast × 24–48 h charter encounter

**Physics path is lawful and adequate for a first feature store:** WCOFS, MUR SST, PFEL Bakun upwelling, CoastWatch chlorophyll, NWS/NDBC/GFS-Wave, USGS/Columbia plume via discharge.

**Gaps that break a 24–48 h encounter product:**

1. **Labels are too slow.** RecFIN comprehensive estimates are the standardized historical GT, but salmon is **excluded from CTE001** (must use the salmon report). Latency is weeks–months. ODFW weekly catch/effort PDFs are the best *public* in-season proxy and still miss 24–48 h and are PDF-fragile.
2. **No public trip-level CPFV log API.** CRFS/ORBS generate the estimates; raw interviews are confidential.
3. **Season is a hard zero (constraint, not GT).** 2026 CA/OR ocean salmon is highly constrained (KRFC / California Coastal Chinook / SONCC coho). An encounter model that ignores in-season closures will be wrong in a legally dangerous way. In-season updates are PDFs (CDFW FileHandler URLs are brittle).
4. **Forage and fish presence are not real-time.** JSOES and CalCOFI-class surveys were treated as insufficient for 24–48 h and kept out of P0. CCIEA is annual credibility, not a nowcast.
5. **Charter go-no-go vs fish encounter are coupled.** Wind/swell cancel trips; remaining trips are a selected sample (endogeneity).

**Ground-truth / outcome sources (W2):**

| Role | Source | Lawful path | Horizon fit |
|------|--------|-------------|-------------|
| Historical GT | RecFIN salmon catch estimates + CRFS/ORBS | Public reports; QueryBuilder account; raw confidential | Monthly / weekly estimates |
| In-season public GT | ODFW ocean salmon catch index PDFs | Public view; request CSV | Weekly |
| Constraint (not GT) | PFMC/NOAA specs + CDFW/ODFW in-season | Public | Hours–days after posting |
| Needed GT | Partner charter/CPFV logs | DUA | Per trip (24–48 h) |

### W3 — American lobster × GOM × next-trip CPUE

**Physics path is the strongest of the three for the actual process (bottom temperature / catchability):** eMOLT trap temperatures, NERACOOS buoys, GoMOFS 72 h, NWS/GFS-Wave, ALWTRP/Slow Zones as effort **constraints**.

**Gaps that break a next-trip CPUE product:**

1. **Public landings have no effort.** Maine DMR monthly pounds/value by zone are excellent economics and seasonality, useless as CPUE without trap-hauls.
2. **True CPUE is confidential.** LEEDS harvester reports and NOAA eVTR are the administrative GT. Access is DUA/NDA/MOU under MSA confidentiality and NAO 216-100. Rule-of-three aggregates will not train a vessel-level next-trip model.
3. **eMOLT spatial privacy.** Bottom temperature is the right covariate; raw gear positions are ecologically and competitively sensitive. Need binned/aggregated products in any commercial UI.
4. **Surveys are the wrong horizon.** Ventless (Jun–Aug juveniles) and ME-NH inshore trawl (seasonal) inform year-class, not tomorrow’s soak.
5. **Regulatory surface is moving.** ALWTRP Phase 1 (2021) plus 2022–2026 restricted-area actions; NOAA had an ALWTRP environmental-analysis NOI open through 16 Oct 2026 at retrieval. A CPUE tool that recommends sets in closed/restricted configurations is a legal defect, not a model defect.
6. **State-only vs federal permit reporting mix** historically incomplete for federal VTR; 2024 eVTR expansion helps but does not create a public dataset.

**Ground-truth / outcome sources (W3):**

| Role | Source | Lawful path | Horizon fit |
|------|--------|-------------|-------------|
| Needed administrative GT | ME DMR LEEDS effort+catch | DUA with DMR | Trip |
| Needed federal GT | GARFO VTR | NAO 216-100 NDA/MOU | Trip (48 h eVTR) |
| Public proxy (weak) | DMR monthly landings/value | Public PDFs | Monthly |
| Needed operational GT | Partner trip logs ± eMOLT | DUA | Next trip |
| Context only | Ventless, inshore trawl, ASMFC assessment, NEFSC trawl | Public summaries / InPort | Seasonal–annual |

## Cross-cutting gaps (all wedges)

| Gap | Why it matters | Lawful mitigation |
|-----|----------------|-------------------|
| Visual web access ≠ commercial license | Most state portals, IOOS ERDDAP mirrors, academic object stores | Counsel review; prefer NOAA/Copernicus/GEBCO first |
| ERDDAP “may be redistributed” + “not for legal use” | Ambiguous for a paid decision product | Treat as CONDITIONAL; do not use as legal advice |
| NOMADS OpenDAP retired 23 Feb 2026 | RTOFS/WW3 access path churn | HTTPS / GRIB filter; CMEMS as physics fallback |
| No partner ops/encounter/CPUE logs in-repo | Cannot train horizon-matched labels | Partner export first; do not substitute DOH/RecFIN-CTE001/monthly pounds |
| Ecological sensitivity of fishing locations | Charter and lobster fine-scale maps | Coarse H3/stat-area only; never publish strings/GPS |
| Food-safety / catch-guarantee product risk | NSSP, WAC 246-282-006, MSA optics | Encode as constraints and authority links, not authorizations or guarantees |

## Inspected and excluded (minimum-sufficient)

| Source class | Why excluded from catalog rows |
|--------------|--------------------------------|
| ICES DATRAS / European stock DBs | Wrong ocean; no lift for WA/CA/OR/GOM 24–72 h |
| FAO FishStatJ | Annual global; no next-trip or 72 h actionability |
| CalCOFI full cruise archive | Seasonal research lag ≫ 48 h; credibility only via CCIEA summaries already noted |
| NWFSC JSOES microdata | Excellent salmon-ocean science; wrong horizon for charter tomorrow |
| Commercial satellite tasking / new hardware | Violates partner-first acquisition ladder |
| Scrape of DOH/ODFW/CDFW HTML | Robots/TOS risk; agency export instead |

## Which wedge has the best lawful *constraint + covariate* path?

**Yes: W1 (Pacific oyster, Washington)** remains the best lawful **constraint + covariate** path, **not** because DOH closures are ops GT.

1. A **public official harvest-open constraint** (DOH commercial closures/class) exists at event timescale and can be shown as an authority link. W2/W3 also have public regs, but W1 uniquely pairs that with **estuary in situ** (NANOOS/NERRS) plus 72 h NOAA/Copernicus physics **without confidential catch microdata**.
2. **72 h covariates** can be assembled from NOAA CO-OPS + NWS + NANOOS/NERRS + WCOFS, with LiveOcean as a high-lift but rights-gated upgrade.
3. HAB networks (SoundToxins, ORHAB, NANOOS) are **covariates**, not day-one confidential logbooks.

**Withdrawn:** the claim that public closures are an official **ops disruption outcome** that lets W1 train without farm logs. Ops GT still requires partners, as W2 and W3 do.

W3 has the best *process* physics (eMOLT + GoMOFS) but the worst *lawful CPUE label* path.  
W2 has a clean shelf-physics stack but cannot honestly advertise 24–48 h encounter skill on weekly PDFs.
