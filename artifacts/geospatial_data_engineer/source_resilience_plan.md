# Source resilience plan

**Agent:** GEOSPATIAL_DATA_ENGINEER_AGENT  
**Date:** 2026-09-18  
**Wedge:** UNRESOLVED. Tables below cover **all three candidates**. After lock, implement only the rows for the active wedge. Fragility and fallbacks are hypotheses until DATA_DISCOVERY / DATA_RIGHTS confirm licenses and SLAs.

**Rules:**

- Every critical variable has `primary`, `secondary`, `fallback_proxy` (or an explicit “no fallback — degrade”).
- Tiers: **A** stable documented alternatives; **B** usable, limited alternatives; **C** experimental, unclear rights, manual, or single point of failure.
- **No production-critical prediction relies solely on Tier C.**
- On outage: (1) log, (2) activate approved fallback, (3) reduce confidence, (4) expose missing-data, (5) alert a human, (6) **never silent**.

---

## 1. Outage state machine

```text
OK → LATE (past freshness SLO) → DEGRADED (fallback in use) → MISSING (no usable input)
```

Each transition writes `source_health` and, if the variable is on the forecast’s critical set, stamps the next `ModelPrediction`:

- `known_missing_inputs += source_id`
- `confidence_category` drops at least one notch (high→medium or medium→low)
- `user_visible_explanation` names the gap in plain language
- operator alert (email/SMS to the on-call founder)

There is no default interpolation of SST, closures, or partner labels.

---

## 2. Freshness SLOs (starting points)

| Variable class | SLO to mark LATE | Critical for |
|---|---|---|
| NDBC / tide / in-situ | 6 h | oyster ops, safety context (not navigation advice) |
| Wave / wind forecast product | 12 h | oyster work window; charter go/no-go context |
| SST analysis | 36 h | all three |
| Chlorophyll | 48 h (cloud gaps expected) | Chinook, lobster (secondary) |
| Official shellfish closure GIS | 6 h + always re-verify before a farm brief | oyster product copy |
| Fishery season/area notice | 24 h | Chinook, lobster |
| Partner outcome form | 7 d (sparse OK) | labels, not same-day env |

SLO breaches increment `source_health` even if a fallback exists.

---

## 3. Fragility register (candidate sources)

Rights status is **UNKNOWN until the rights agent says otherwise**. Do not ingest. Official landing pages for planning:

### 3.1 Shared environmental

| Variable | Primary | Secondary | Fallback proxy | Fragility | Notes |
|---|---|---|---|---|---|
| SST | Regional NOAA/CoastWatch or CMEMS analysis subset | The other of NOAA/CMEMS | Nearby NDBC water temp | A if both licensed; else B | Clip to AOI; never global cubes |
| Waves / wind | NWS / NOAA wave model or CMEMS waves | The other | NDBC buoy waves (point) | A/B | Product is **not** navigation advice; link official forecast |
| Tides | NOAA CO-OPS | Backup station in same basin | Tide table edition (static, low skill) | A | |
| Currents | Regional model if licensed | SST front proxy only as **weak** covariate | none — degrade | B/C | Do not claim current-driven abundance |
| Chlorophyll | NOAA OC / CMEMS OC | the other | none (clouds) — degrade | B | Not fish count |
| In-situ metocean | NDBC / CDIP / NANOOS or NERACOOS | Neighbor station | raster only | A/B | Station allowlist in AOI |

Example landing pages (accessed 2026-09-18): Copernicus Marine [https://marine.copernicus.eu/](https://marine.copernicus.eu/); NOAA NDBC [https://www.ndbc.noaa.gov/](https://www.ndbc.noaa.gov/); NOAA CO-OPS [https://tidesandcurrents.noaa.gov/](https://tidesandcurrents.noaa.gov/); NANOOS [https://www.nanoos.org/](https://www.nanoos.org/); NERACOOS [https://www.neracoos.org/](https://www.neracoos.org/).

### 3.2 Taxonomy

| Variable | Primary | Secondary | Fallback | Fragility |
|---|---|---|---|---|
| Accepted scientific name | WoRMS REST Aphia | Manual taxdetails page | Keep `scientific_name_at_source`, flag `TAXONOMY_UNRESOLVED` | A |

[WoRMS REST](https://www.marinespecies.org/rest/) / [about/terms](https://marinespecies.org/about.php). Cache used records; do not redistribute the entire DB. Attribution required.

### 3.3 Wedge A — Pacific oyster × WA farm ops 24–72h

| Variable | Primary | Secondary | Fallback | Fragility |
|---|---|---|---|---|
| Growing-area polygons | WA DOH GIS commercial growing areas | geo.wa.gov copy | Manual area name only — **no map** | A |
| Biotoxin / classification closure | WA DOH closure zones + map viewer | County/program notice | Show STALE, never “open” | A/B |
| Farm outcome labels | Partner form / export | Weekly call notes structured later | **No public proxy** | B (single partner = B; one farm = C until n≥3) |
| Farm sensors | Partner/vendor export | NANOOS nearby | SST/wave raster only | B/C |
| Work-window metocean | Waves + wind + tides | Buoy-only | Seasonal climatology baseline | A |

DOH URLs: [growing areas](https://doh.wa.gov/community-and-environment/shellfish/growing-areas), [GIS downloads](https://doh.wa.gov/data-and-statistical-reports/data-systems/geographic-information-system/downloadable-data-sets), [viewer](https://fortress.wa.gov/doh/oswpviewer/index.html). Closures are **authority data**. Models must not authorize harvest.

If partner outcomes are the only label and n=1 farm, the **label series** is Tier C: ship only a baseline + disclaimer, or pause. Env covariates can still be Tier A.

### 3.4 Wedge B — Chinook × CA/OR charter 24–48h

| Variable | Primary | Secondary | Fallback | Fragility |
|---|---|---|---|---|
| Management area geometry | PFMC/NMFS definitions | State regs pages | Named lat bounds in config | A |
| Season / bag / area status | NMFS WCR + CDFW/ODFW official pages | The other agency | STALE notice; no inferred open | B (HTML can break — schema-change detection required) |
| Encounter labels | Partner charter log (catch + **effort**) | CRFS/RecFIN if rights-approved later | **No AIS proxy** | B |
| Env habitat covariates | SST, waves, (optional chl) | buoys | climatology baseline | A |

PFMC/NMFS: [Salmon FMP](https://www.pcouncil.org/documents/2022/12/pacific-coast-salmon-fmp.pdf/), [ocean salmon fisheries](https://www.fisheries.noaa.gov/west-coast/sustainable-fisheries/ocean-salmon-fisheries-west-coast). Lock **one** management area at wedge decision (e.g. KMZ vs Fort Bragg).

AIS/VMS, fishing forums, and social photos are Tier C / T4 and **cannot** be the production label.

### 3.5 Wedge C — American lobster × GOM CPUE next trip

| Variable | Primary | Secondary | Fallback | Fragility |
|---|---|---|---|---|
| Statistical areas | NEFSC InPort 26262 | GARFO copies | Configured area codes | A |
| LMA / closures | GARFO lobster management areas | ASMFC notices | STALE; no inferred open | A/B |
| CPUE labels | Partner haul logs (catch + trap hauls) | State harvester reporting **if licensed** | Landings-only (weak, biased) | B |
| Bottom temp | NERACOOS / in-situ | SST proxy (weak) | climatology | B |
| Stock index (context) | ASMFC/NOAA assessment products | prior year index | omit from short-horizon model | A (low frequency) |

[NEFSC Statistical Areas](https://www.fisheries.noaa.gov/inport/item/26262); [Lobster Management Areas](https://www.fisheries.noaa.gov/resource/map/lobster-management-areas). Landings without effort are not CPUE.

---

## 4. Monitoring

Every job writes `source_health`:

| Field | Detects |
|---|---|
| `http_status`, `bytes`, `checksum` | outage, empty body |
| `schema_hash` | column/unit rename |
| `null_rate`, `row_count` | feed gone hollow |
| `max_observed_at`, `max_published_at` | late publication |
| `bbox_outside_aoi_rate` | wrong product / swapped CRS |
| `unit_change_flag` | °F vs °C |
| `outlier_rate` | bad sensor |
| `rights_status` | license change requires pause |

Schema-hash change → automatic `DEGRADED` + human alert. Do not auto-map new columns.

Owner contact / status page URLs live on `SourceMetadata` (filled by discovery). If unknown, fragility cannot be A.

---

## 5. Production-critical vs contextual

A variable is **production-critical** if its absence should block or force-low-confidence the brief.

| Wedge | Critical (must have primary or secondary) | Contextual |
|---|---|---|
| Oyster WA | time, tides/waves-or-wind, growing-area id, closure feed **or** explicit STALE, partner outcome **for evaluation** (not necessarily for each brief) | chl, farm sonde |
| Chinook | time, SST or seasonal baseline, official area status **or** STALE, effort-normalized labels for eval | chl, currents |
| Lobster | time, effort-normalized partner/agency CPUE for eval, LMA/stat-area status **or** STALE | satellite chl, AIS |

A climatology baseline is a valid **model** fallback (Tier A method) when live SST is missing; it is not a fake observation. Record `SOURCE_OUTAGE_FALLBACK` and drop confidence.

---

## 6. What not to depend on

- A single unpaid HTML page with no schema (unless secondary exists)
- Unclear-rights ERDDAP dumps
- Hardware we do not own
- Global Fishing Watch or AIS as abundance
- Social media
- One partner’s PRIVATE GPS as a public layer
- Tier C experimental eDNA/acoustics as the only input

---

## 7. Alert routing (v1)

Until a pager exists: log file + email/SMS to the founder on `DEGRADED`/`MISSING` for critical variables. Briefs still go out if the template can render `confidence=low` and the missing-data sentence. If **closure/season** status is MISSING, the brief leads with “verify with the authority; our copy is stale/unavailable.”
