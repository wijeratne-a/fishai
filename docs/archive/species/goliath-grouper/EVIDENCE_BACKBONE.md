# Evidence backbone — Atlantic goliath grouper

**Default ingest state:** **NOT INGESTED.**  
**Rights status:** **UNKNOWN** until a data-rights review assigns `APPROVED_*`. Catalog only.  
**Point-in-time rule:** no future covariates for past labels. A 2026 ocean cube cannot label a 2011 row.

This is not a database. No partner telemetry, survey microdata, or restricted spawning-site coordinates are stored here.

---

## Observation-state classes (keep separate)

| Class | Meaning |
|---|---|
| **Confirmed presence** | A protocol recorded the taxon at a place, depth (if any), and time. |
| **Non-detection with effort** | A survey looked and did not record the taxon. Requires effort. |
| **No survey** | No protocol ran. **Unknown**, not absence. |
| **Restricted** | Exists but must not be shown at native grain (aggregations, nurseries). |

**AIS and fishing effort are not fish presence.** They may later be *effort covariates* after rights review — never painted as animals.

---

## Source inventory

| Source | What it can support | Rights (today) | Ingested? | Notes |
|---|---|---|---|---|
| **OBIS occurrence API** (official) | Historical compiled presence rows; coarse 1° counts | UNKNOWN (compiler + many datasets; licenses vary) | **NOT INGESTED** into a warehouse. Globe may do a **live, rate-limited, coarsened** lookup (`n ≥ 3`, max 80 cells, ~1°) labeled **past reports** | 2026-09-22 official count for *Epinephelus itajara*: **332,628** compiled records, years **1935–2026**. 2010–2016 dominate the count — treat as **dataset composition**, not a population boom. Not a census. Not current presence. |
| **WoRMS** | Name and AphiaID 159353 | Public taxonomic service; attribute WoRMS/FishBase | Name only | Not a distribution. |
| **SEAMAP / state surveys** (catalog) | Possible effort-aware detections if public and approved | UNKNOWN | NOT INGESTED | Not fetched as tables in this pass. |
| **NOAA / FSU tagging & sonic tracking** (described on NOAA species page) | Movement and habitat use in Ten Thousand Islands and offshore summer/fall work | UNKNOWN / likely restricted for public pins | NOT INGESTED | NOAA mentions sonic tags and 1,000+ adult tags. **Do not request or draw tracks.** |
| **ATN / telemetry portals** | Animal-borne movement if public | UNKNOWN | NOT INGESTED | Do not scrape. |
| **Visual / diver / BRUV** | Confirmed presence with high wreck bias | UNKNOWN | NOT INGESTED | Aggregation-site risk. |
| **Passive acoustics** (swim-bladder rumble) | Possible detection of callers, not a headcount | UNKNOWN | NOT INGESTED | Florida Museum describes the sound; no PAM network is claimed. |
| **eDNA** | Occupancy of DNA at a station, not GPS of a fish | UNKNOWN | NOT INGESTED | None in this product. |
| **Ocean covariates** (Copernicus SST, salinity, currents, chlorophyll) | Habitat **inputs** | UNKNOWN until credit + license check | NOT INGESTED | **Not proof of presence.** |
| **Mangrove / reef / bathymetry maps** | Habitat suitability covariates | UNKNOWN | NOT INGESTED | Suitability ≠ animals. GEBCO is catalogued, not tiled as terrain. |
| **AIS / VMS / fishing effort** | Human effort; possible bias correction later | UNKNOWN | NOT INGESTED | **Not fish.** |
| **FWC Goliath Harvest Program** | Legal harvest events if ever public | UNKNOWN | NOT INGESTED | Program page not retrieved. Catch ≠ abundance. |

---

## Schema fields required per future record

Minimum if ingest is ever approved:

- `taxon_aphia_id` (159353 or documented synonym)
- `scientific_name`
- `event_time` (ISO, timezone)
- `lon`, `lat` (native)
- `public_lon`, `public_lat` or `public_cell_id` (**coarsened before persist**)
- `depth_m` or `depth_band` or `depth_unknown`
- `life_stage` if known (`juvenile` / `adult` / `unknown`)
- `observation_type` (visual, capture, acoustic, eDNA, tag, compiled)
- `observation_state` (`confirmed_presence` / `nondetection_with_effort` / `no_survey` / `restricted`)
- `effort` (protocol + duration/area/hooks — required for non-detection)
- `source_id`, `license`, `rights_class`
- `sensitive_flag` (aggregation / nursery / wreck)
- `as_of_available_utc` (when this row could have been known)

Do not persist native wreck coordinates in a public table.

---

## Point-in-time / leakage

- Labels at time *t* may use only covariates published at or before *t*.
- A seasonal climatology used as a **baseline** must be labeled climatology, not a 24h forecast.
- OBIS year spikes (2010–2016) are not to be used as an abundance index without an effort model.
