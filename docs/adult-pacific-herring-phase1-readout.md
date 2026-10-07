# Adult Pacific herring (*Clupea pallasii*) — Phase 1 readout

Branch: `cursor/fishai-adult-pacific-herring`. Date: 2026-10-07.

## Disclosure

Public NOAA SWFSC CPS life-history data only. Pilot domain: Southern California Bight 50-mile
nowcast bbox in `data/SOURCES.yaml` (`pilot.bbox`: 32–35°N, 117–121°W). No raw coordinates or
catch tables are committed. This is not live tracking and not harvest advice.

## Data acquisition

ERDDAP tabledap pulls on `oceanview.pfeg.noaa.gov` returned **504 Gateway Time-out** on
year-bounded trawl haul-catch requests (pilot bbox). Per pipeline fallback, full CSV mirrors were
used from NOAA InPort GCS (`nmfs_odp_swfsc`), then filtered client-side:

| Product | GCS object |
|---|---|
| Trawl haul catch | `CPS_Trawl_LifeHistory_HaulCatch.csv` |
| Trawl specimens | `CPS_Trawl_LifeHistory_Specimen.csv` |
| Nearshore set catch | `CPS_Trawl_LifeHistory_Nearshore_SetCatch.csv` |
| Nearshore specimens | `CPS_Trawl_LifeHistory_Nearshore_Specimen.csv` |

Helper: `src/fishai/ingestion/adult/gcs_mirror.py`. Viability script:
`scripts/adult_species_viability_gate.py`.

## Viability gate (non–presence-only presences, pilot bbox)

| Source | Non–presence-only presences | Notes |
|---|---:|---|
| Trawl haul catch | **0** | 372 *C. pallasii* rows range **36.94–54.40°N** (all **north of** pilot lat_max 35°N) |
| Nearshore set catch | **0** | 2 `Clupeidae` family-level rows in bbox (not species-level presences) |
| **Total** | **0** | |

Trawl presence-only rows for *C. pallasii* in bbox: 0.

**Verdict: species not viable** in the pilot bbox (<100 presences). **STOP** before training-table
build, GLORYS join, sdmTMB fit, CV, and 24h forecast validation.

## Staged inputs (local cache, gitignored)

GCS CSVs cached under `data/raw/swfsc_cps_gcs_mirror/` for a future cutoff follow-up if the
pilot domain changes. Specimen length fields are populated for herring **outside** the pilot
bbox (global mirror counts: trawl 7,134 specimens with length; nearshore 3,110 with length;
**0** herring specimens inside pilot bbox).

## Awaiting follow-up

Per workflow: **L50 adult length cutoff** for *C. pallasii* before any training table — moot while
viability fails in this bbox. If you want a northern-CA pilot extension or a different species
frame, say so explicitly.

## Phase 2+ status

| Step | Status |
|---|---|
| Training table + implied zeros | **Blocked** (viability) |
| GLORYS join | Copernicus service env present; not run |
| sdmTMB hurdle + spatial-block CV | **Not run** |
| 24h forecast validation | **Not run** |
