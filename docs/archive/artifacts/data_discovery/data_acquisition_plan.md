# Data acquisition plan (plan only — no ingest)

**Date:** 2026-09-18 (W1 GT relabel)  
**Rule:** partner-first ladder. Hardware last. No bulk ocean downloads in this iteration.  
**Ladder (mandatory order):** public documented APIs → agency export/DUA → partner export of existing digital logs → existing sensors already in the water → manual observations → mobile apps → third-party integrations → new hardware.  
**W1 label:** `ops_disruption_72h` from partner farm mortality/workability/intervention. WA DOH closures are a **harvest-open constraint + authority link**, not the training set. See `ground_truth_relabel_W1.md`.

## 0. Preconditions (all wedges)

1. Human legal review of every `CONDITIONAL_REVIEW_REQUIRED` row before production use.  
2. Register (do not scrape): Copernicus Marine account; NOAA CO-OPS `application=` name; NWS API User-Agent with contact; optional Earthdata login for native MUR.  
3. One request per host at a time; back off on 429/403; honor robots.txt.  
4. Store raw with license snapshot, access timestamp, and source URL. Do not mix CC BY-NC with commercial feature stores.  
5. Taxonomy authority: WoRMS AphiaIDs 836033 / 158075 / 156134.  
6. Never impersonate NSSP/WA DOH harvest or food-safety authority (WAC 246-282-006). Product copy that treats ops-stress as harvest legality is a blocker.

## Phase A — Public APIs (week 0–2 after wedge lock)

**Purpose:** prove **covariate** plumbing on a tiny spatial/temporal window (one bay, one statistical area, 14 days), not a global lake. Not a labeled ops model.

| Step | Source | Allowed action | Forbidden |
|------|--------|----------------|-----------|
| A1 | NWS API | One `/points` then grid forecast for a single farm/port | High-rate grids for all CONUS |
| A2 | CO-OPS Data API | One WA or ME station, 7-day water_level + predictions + water_temperature | All NWLON history |
| A3 | CMEMS Toolbox | Subset 1/12° T/S for the wedge bbox, 10-day forecast only | Global full-depth archive |
| A4 | CoastWatch ERDDAP | 1 km MUR subset for bbox, last 14 days | Global 2002–present |
| A5 | NOMADS HTTPS | Single GFS-Wave or RTOFS regional file for bbox | OpenDAP (retired); parallel GRIB |

**Exit:** NetCDF/JSON land in an empty raw bucket with checksums; no model training.

## Phase B — Agency export (week 2–6)

Ask in writing. Attach intended commercial use. Accept aggregates.

| Wedge | Ask | Desired table | Fallback if refused |
|-------|-----|---------------|---------------------|
| W1 | WA DOH Office of Environmental Health and Safety | Growing-area polygons, classification, historical commercial **harvest-open/closed** status, station FC time series — **constraint overlay**, not ops labels | Manual encoding of **current** official harvest-open status only; no scrape; still not GT |
| W1 | WDFW/WSDA | WAHH **aggregated** harvest by growing area/month (volume context) | Skip harvest volume; **ops GT remains partner logs** |
| W2 | ODFW Ocean Salmon Management | Weekly catch/effort as CSV (not PDF) | RecFIN public **salmon** report (not CTE001) |
| W2 | RecFIN/PSMFC | Public salmon estimate table documentation + account if needed | ODFW weekly + CDFW summary PDFs |
| W2 | CDFW | Machine-readable in-season sport salmon status (**constraint**) | Parse published PDF after permission |
| W3 | Maine DMR Landings Program | Zone-month landings already public, plus **rule-of-three** effort aggregates if possible | Public PDFs only (not CPUE) |
| W3 | Maine DMR | LEEDS research extract under DUA (confidential) | Partner logs |
| W3 | NOAA GARFO APSD | Not first-line; only if DMR refused and federal permits dominate the partner fleet | Skip VTR |

**Exit:** a dated data-sharing letter. If no letter, stay on public aggregates, official harvest-open links, and partner logs.

## Phase C — Partner export of data they already have (week 3–8, parallel to B)

Do not build an app until exports fail. **This is the W1 label path.**

| Wedge | Partner type | Existing artifact to copy | Fields (minimum) |
|-------|--------------|---------------------------|------------------|
| W1 | 3–8 oyster farms (**Willapa and** Hood Canal/Puget Sound; do not sample only ORCA-adjacent Hood Canal) | Spreadsheet, farm software, packing-house receipts | date, growing area, `ops_disruption_72h`, mortality/seed-loss flag, workability (could crew work tide/gear), intervention (early harvest, re-submerge, shade, move), optional sonde T/S |
| W1 | SoundToxins / Sea Grant | Partner DB extract | site, date, target genera, abundance bin (**covariate**, not label) |
| W2 | 5–15 CPFV/charter (CA and OR) | Existing e-logs / paper trip sheets | date, port, area bin, hours, Chinook kept/released, wind/swell notes, whether trip cancelled |
| W3 | 8–20 lobster boats across ≥2 zones | Paper logs, plotter exports, dealer slips, eMOLT-equipped boats | date, zone/stat area (coarse), trap-hauls, legal count, soak, optional bottom T |

**Contract rules:** no redistribution of raw logs; no public map finer than agreed H3/stat area; deletion on request; no food-safety, harvest-authorization, or catch-guarantee claims in the product copy.

## Phase D — Existing sensors (only after C starts)

- NANOOS ORCA / NVS growers / NERRS CDMO (already in water). **Hood Canal ORCA ≠ Willapa instrumentation.**  
- NERACOOS + eMOLT (already in water).  
- Optional: farms’ own sondes if they already log digitally.

Do **not** buy new ESP/sonde/camera hardware in this phase.

## Phase E — Manual observations

If partners will not export history, run a **14-day paper protocol** (same fields as Phase C) during one high-risk window (WA heat/gear-stress; CA/OR salmon opener; GOM shed/late season). This is cheaper than an app. For W1, the paper protocol **is** the label collection; DOH harvest-open status is recorded **alongside** as a constraint column, not as `y`.

## Phase F — Mobile / integrations / hardware (last)

Only if Phases C–E prove that operators will not share existing logs:

- F: WhatsApp/SMS structured daily checklist (not a new social network).  
- G: Integration with existing dealer/farm software they already pay for.  
- H: Hardware (extra sondes, cameras, AIS analytics) — **last**, after a locked wedge and a rights memo.

## Wedge-specific 30-day plans (choose one after lock)

### If W1 locks

Days 1–7: A1–A5 on **one** growing area (if Hood Canal/ORCA is used for covariate plumbing, **commit in writing** to add Willapa farms for labels in month 2; do not pretend ORCA covers Willapa).  
Days 7–21: three grower NDAs for `ops_disruption_72h` fields; DOH letter for harvest-open GIS **as constraint**.  
Days 21–30: label a retrospective from **grower spreadsheets only**; attach a DOH harvest-open column as context; LiveOcean terms email to UW (do not bulk-pull hindcast until terms exist). **Do not label days with DOH closures as ops disruption.**

### If W2 locks

Days 1–7: season-status table for CA/OR management areas (manual from official PDFs, with URLs and retrieval timestamps) as **hard zeros**.  
Days 7–21: ODFW CSV request + 5 charter NDAs at two ports.  
Days 21–30: join WCOFS/SST/upwelling to **weekly** ODFW estimates as a **weak** baseline only; do not claim 24–48 h until partner trips ≥ N (set by validation agent). RecFIN CTE001 remains **out** (salmon excluded).

### If W3 locks

Days 1–7: GoMOFS + NERACOOS + eMOLT **binned** temperatures for one statistical area.  
Days 7–21: DMR landings dashboard (public) + harvester association conversations; ALWTRP layer from official CFR/GIS as **constraint**.  
Days 21–30: partner CPUE from dealer slips if LEEDS DUA is not in hand. Never queue VTR first. Never treat monthly pounds as CPUE.

## Resilience (two-source rule for P0 physics)

| Need | Primary | Fallback |
|------|---------|----------|
| Global T/S | CMEMS PHY | RTOFS HTTPS |
| West Coast 3D | WCOFS | CMEMS PHY + LiveOcean if licensed |
| GOM 3D | GoMOFS | CMEMS PHY + NERACOOS |
| SST | MUR | NOAA geo-polar blended |
| Waves | GFS-Wave | CMEMS WAV |
| Weather | NWS API | NDBC + GFS |
| W1 **harvest-open constraint** | DOH closures (authority link) | Commercial viewer / safety map (still not GT) |
| W1 **ops labels** | Partner farm logs | 14-day paper protocol; **no public fallback** |
| W2 labels | Partner logs | ODFW weekly → RecFIN salmon report (not CTE001) |
| W3 labels | Partner logs | DMR DUA → never public CPUE |

## Explicit non-acquisition list

- No scraping fortress.wa.gov, SoundToxins maps, RecFIN HTML, or CDFW FileHandler in a loop.  
- No using DOH/NSSP closures as `ops_disruption_72h` labels.  
- No CC BY-NC GBIF/OBIS in the commercial feature store.  
- No GEBCO/OFS “for navigation.”  
- No parallel crawls of ERDDAP.  
- No new ocean hardware until wedge lock + partner logs fail.
