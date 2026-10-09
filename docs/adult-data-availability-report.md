# Adult-fish data availability report — FishAI adult workstream

Date: 2026-10-06. Scope: row-level (tow/transect/set-level) public sources of
adult/juvenile Pacific sardine (*Sardinops sagax*) and northern anchovy
(*Engraulis mordax*) observations **with survey effort**, for the Southern
California Bight pilot and the wider California Current.

## Verdict

| Source | Row-level public? | Verdict |
|---|---|---|
| NOAA SWFSC CPS mid-water trawl hauls (`FRDCPSTrawlLHHaulCatch`) | **Yes** — ERDDAP tabledap, public | Already ingested in repo (`swfsc_cps_trawl_haul_catch`) |
| NOAA SWFSC CPS nearshore purse-seine sets (`FRDCPSNearshoreSetCatch`) | **Yes** — ERDDAP tabledap, public | **New — scaffolded on this branch** |
| CDFW–CWPA aerial survey (CCPSS) | **No** — reports only | Not usable; see §3 |

## 1. SWFSC CPS mid-water trawl haul catch (ATM / DEPM / SaKe)

- **Access:** `https://coastwatch.pfeg.noaa.gov/erddap/tabledap/FRDCPSTrawlLHHaulCatch` (also served via `oceanview.pfeg.noaa.gov`)
- **Granularity:** one row per haul × species; haul metadata (position, time, tow duration/distance derivable).
- **Coverage:** 2003-07-09 → 2025-09-10; lat 28.65–54.40, lon −134.08 → coast. Includes acoustic-trawl method (ATM) survey hauls — the trawl component that apportions acoustic backscatter to species.
- **License:** NOAA ERDDAP free-use disclaimer — "may be used and redistributed for free"; not CC, no warranty. Recorded verbatim in `data/SOURCES.yaml`.
- **Effort:** tow-level (start/stop positions and times); zero-catch expansion gated by `config/cps_trawl_zero_frame_evidence.yaml` (per-cruise human audit; shipped empty).
- **Status in repo:** already ingested (`src/fishai/ingestion/biology/cps_trawl/`). Nothing new needed.

## 2. SWFSC CPS nearshore purse-seine set catch (NEW)

- **Access:** `https://coastwatch.pfeg.noaa.gov/erddap/info/FRDCPSNearshoreSetCatch/index.html` (info page verified 2026-10-06; "Accessible: public"); tabledap CSV via `https://coastwatch.pfeg.noaa.gov/erddap/tabledap/FRDCPSNearshoreSetCatch.csv?...`
- **Granularity:** one row per purse-seine set × species: `cruise, ship, date, time, set, latitude, longitude, state, gearType, itis_tsn, scientific_name, totalNumber, totalWeightkg`.
- **Coverage:** 2019-06-21 → 2026-06 (cruises 201907–202606); lat 32.56–48.36, lon −125.23 → −117.14. Covers the Southern California Bight nearshore — the exact blind spot of the ship-based ATM survey (<40 m).
- **License:** same NOAA ERDDAP free-use disclaimer as above; recorded verbatim in `data/SOURCES.yaml` under `swfsc_cps_nearshore_set_catch`.
- **Effort:** purse-seine sets are the sampling frame (point events — no tow duration; recorded as explicit nulls with reason, never imputed). Implied zeros only for sets in a verified cruise frame (`config/cps_nearshore_zero_frame_evidence.yaml`, shipped empty).
- **Why it matters:** fishery-independent adult/juvenile CPS catch with effort in the nearshore zone where sardine/anchovy schools concentrate and where the ATM vessel cannot sample. Complements the mid-water trawl hauls spatially.
- **Status in repo:** scaffolded on this branch (`src/fishai/ingestion/biology/cps_nearshore/` + wrapper `swfsc_cps_nearshore_set_catch.py`, SOURCES.yaml entry, tests with synthetic fixtures). No real data downloaded or committed.

## 3. CDFW–CWPA aerial survey (CCPSS) — not available at row level

- Searched: CDFW wildlife.ca.gov, California Natural Resources Agency open data (data.cnra.ca.gov), catalog.data.gov, PFMC briefing-book archives.
- **Finding:** no public row-level (transect/school-level) dataset exists. What is public: seasonal summary reports and presentations (biomass minimum estimates, school counts, e.g. sardine ~18.1k mt aerial vs 36k mt ATM in summer 2017) hosted on pcouncil.org.
- The survey is a CDFW + California Wetfish Producers Association (industry) partnership; raw transect/school observations are not published.
- **Consequence:** the aerial survey cannot enter the training pipeline under the public-data-only rule. Its published biomass estimates remain usable only as independent validation aggregates, not as training rows.

## 4. What was NOT used and why

- **NCEI water-column sonar archives** (e.g. RL1807 ME70): raw acoustic backscatter without species apportionment — not training-usable alone; the trawl hauls that apportion it are already ingested via §1.
- **Acoustic-trawl transect backscatter (sA) products:** no public row-level transect dataset found on ERDDAP/NCEI; only cruise-report figures.
- **Fishery-dependent sources** (logbooks, landings): excluded by the presence-only / effort-confounding rule; commercial aggregates would additionally need ≥3 vessels per MSA 402(b).

## 5. Data-rule compliance notes

- Publicly licensed only: both ERDDAP sources carry the NOAA free-use disclaimer (not CC); verbatim license text in `data/SOURCES.yaml`; `require_approved()` gates ingestion on `status: approved`.
- Never presence-only: both sources are survey effort frames (trawl hauls / purse-seine sets); the matrix emits 1 / 0-in-verified-frame / null-not-available — never bare presences.
- Commercial aggregates ≥3 vessels: not applicable (fishery-independent surveys, no vessel-level commercial data).
- Public maps of commercially fished stocks no finer than 10 km: no maps produced on this branch; any downstream map work must aggregate to ≥10 km.
- No raw data committed: ingestion writes to `data/raw/` and `data/processed/` (git-ignored); tests use synthetic fixtures only.
