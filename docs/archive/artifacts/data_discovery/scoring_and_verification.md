# Scoring scale and verification log

**Agent:** DATA_DISCOVERY_AGENT  
**Date:** 2026-09-18  
**Project:** Ocean Intelligence Builder / FishAI  
**Ingest:** none (catalog + modest official metadata probes only)

## Score scale (0–1)

All component scores and `source_priority_score` use a **0–1** scale.

```
source_priority_score =
  0.30 * decision_relevance
+ 0.20 * expected_predictive_lift
+ 0.15 * timeliness
+ 0.15 * rights_score
+ 0.10 * coverage_score
+ 0.10 * defensibility_score
```

| Component | 1.0 means | 0.0 means |
|-----------|-----------|-----------|
| decision_relevance | Directly needed for the 24–72h action (constraint or outcome) | Irrelevant at this horizon |
| expected_predictive_lift | Likely material skill vs a naive climatology/persistence | No plausible skill contribution |
| timeliness | Updates inside the decision lead time | Annual/lagged only |
| rights_score | Clear commercial use + redistribution path | Confidential / NC / unknown hostile |
| coverage_score | Matches wedge geography and grain | Wrong scale or empty in domain |
| defensibility_score | Official, documented, citable, scientifically standard | Anecdote / unofficial scrape |

**Minimum-sufficient rule:** a source is cataloged only if it improves prediction quality, lead time, actionability, economic-risk coverage, defensibility, scientific credibility, or resilience. ICES DATRAS and FAO FishStatJ were inspected and **excluded** (wrong basin or annual global grain).

## License policy used here

- Do **not** infer commercial rights from a public website.
- Mark `license` **UNKNOWN** unless the license text was retrieved.
- Mark `commercial_use_allowed` / `redistribution_allowed` **UNKNOWN** or **CONDITIONAL** rather than guessing YES.
- Every catalog row is `legal_review_status = CONDITIONAL_REVIEW_REQUIRED` (human counsel).
- Copernicus Marine license was retrieved: commercial use and original-product redistribution allowed **with attribution**.
- GEBCO terms were retrieved: commercial exploitation allowed **with attribution**; **not for navigation**.
- NWS disclaimer was retrieved: public domain unless noted; no endorsement; do not present modified content as official.
- GBIF/OBIS: per-dataset CC0 / CC BY / CC BY-NC; **CC BY-NC is not a commercial path**.
- NOAA VTR / Maine harvester microdata: confidential; `commercial_use_allowed = NO` for microdata.

## Metadata probes performed (sequential, not bulk)

| Time (session) | Endpoint | Result | Bulk data? |
|----------------|----------|--------|------------|
| 2026-09-18 | CO-OPS MDAPI `stations/9447130.json` (Seattle) | Mixed tide NWLON station; lat 47.60264, lon -122.3393; forecast=true | No |
| 2026-09-18 | WoRMS REST `AphiaRecordsByName/Magallana gigas` | AphiaID **836033**, accepted | No |
| 2026-09-18 | WoRMS REST `AphiaRecordsByName/Oncorhynchus tshawytscha` | AphiaID **158075**, accepted | No |
| 2026-09-18 | WoRMS taxon page `Homarus americanus` | AphiaID **156134** | No |
| 2026-09-18 | OBIS API `/v3/taxon/836033` | Accepted `Magallana gigas` | No |
| 2026-09-18 | CoastWatch ERDDAP `jplMURSST41/index.json` | Daily 0.01° SST; coverage 2002-06-01 to **2026-09-17**; NASA JPL / PO.DAAC license string + NOAA as-is | No |
| 2026-09-18 | NANOOS ERDDAP `info/index.json` | Live catalog including ORCA Twanoh/Hoodsport/Dabob, Cha'Ba/NEMO, Backyard Buoys | No |

Probes not performed (to respect rate limits / robots / TOS): NOMADS GRIB, Copernicus netCDF, RecFIN QueryBuilder login, LEEDS, VTR, SoundToxins DB, DOH GIS export, USGS time-series values, NWS `/points` (User-Agent app not yet registered).

## Evidence-tier and fragility vocabularies

**evidence_tier:** `T1` official operational/regulatory; `T2` documented model/index/partnership; `T3` opportunistic; `T4` partner GT that does not exist until DUA.

**source_fragility_tier:** `F1` dual-homed operational; `F2` single portal/API with known churn; `F3` research/cooperative hosting; `F4` PDF/manual or dataset does not exist yet.

**candidate_wedge_ids:** `W1_oyster_wa` | `W2_chinook_caor` | `W3_lobster_gom`

## W1 label correction (2026-09-18 follow-up)

WA DOH commercial growing-area closures were originally scored as if they were 24–72h ops-stress **ground truth** (DR=1.00, EPL=0.85, SPS=0.885, rank 1). That is scientifically and legally wrong. They are rescored as a **must-show harvest/food-safety constraint** (DR=0.90, EPL=0.30, SPS=0.745, still P0). The W1 training label is `ops_disruption_72h` from partner farm mortality/workability/intervention. See `ground_truth_relabel_W1.md`.
