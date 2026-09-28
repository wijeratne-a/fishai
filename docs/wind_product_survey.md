# Surface wind product survey (CUFES SCB pilot)

Research note for **bot2 (physics)** — FishAI Southern California Bight (SCB) egg nowcast pilot. This document does **not** change feature-table or ingestion code; it records live-server verification of candidate **surface wind** products for:

1. **Training covariates** — CalCOFI CUFES egg samples, roughly **1996–2022**, bbox **32–35°N, 121–117°W**.
2. **Daily near-real-time nowcasts** — operational latency **≤ 2 calendar days**, still updating in **2026**.

**Verification run:** 2026-09-28 UTC. Methods: HTTPS GET of ERDDAP `info/.../index.json`, Copernicus CDS catalogue JSON, RSS `data.remss.com` directory listings, and RSS CCMP product HTML. **≤ 2 concurrent requests per host; &lt; 100 total requests.** No invented metadata — gaps are stated explicitly.

## Decision criteria

| Criterion | Requirement |
|-----------|-------------|
| Spatial | Global/gridded product usable over SCB bbox |
| Training era | Covers CUFES pilot window (≥ 1996 through ≥ 2022) |
| Nowcast | Active updates in Sep 2026 with **≤ 2 day** typical lag |
| Processing | **Same algorithm / product version** for history and nowcast (no train-on-v3 / run-v2-NRT split) |

## Summary table

| Candidate | Access (primary) | ERDDAP id (if any) | Time start (metadata) | Time end (metadata) | Grid | Latency (evidence) | Licence | Same processing train + nowcast? |
|-----------|------------------|--------------------|------------------------|---------------------|------|--------------------|---------|----------------------------------|
| **RSS CCMP v3.1** | [data.remss.com/ccmp/v03.1/](https://data.remss.com/ccmp/v03.1/) | *(PIFSC mirror unverified; see note)* | 1996 (`Y1996/` tree) | 2026-08-31 (latest daily file in `Y2026/M08/`) | 0.25°; 4× daily maps | **~17 d** (Aug 31 file; dir updated 2026-09-17) | CC-BY-4.0 | **Yes** (single v3.1 reanalysis stream) |
| **RSS CCMP v2.1 NRT** | [data.remss.com/ccmp/v02.1.NRT/](https://data.remss.com/ccmp/v02.1.NRT/) | `ccmp-daily-v2-1-NRT` *(host DNS failed)* | 2015 (`Y2015/` earliest) | 2026-09-27 (file dated 20260927) | 0.25° (v2.1 RT filenames) | **~1 d** | CC-BY-4.0 | **No** (v2.1 ≠ v3.1; short history) |
| **NCEI Blended Sea Winds v2.0 (science daily stress)** | [noaacwBlendedWindStressDaily](https://coastwatch.noaa.gov/erddap/griddap/noaacwBlendedWindStressDaily) | `noaacwBlendedWindStressDaily` | 1987-07-09T18:00:00Z | 2026-08-31T00:00:00Z | 0.25° daily **stress** | **~28 d** on survey date | Cite NCEI (ERDDAP) | **Yes** for science file only |
| **NCEI Blended Sea Winds v2.0 (NRT daily stress)** | [noaacwBlendednrtWindStressDaily](https://coastwatch.noaa.gov/erddap/griddap/noaacwBlendednrtWindStressDaily) | `noaacwBlendednrtWindStressDaily` | 2023-01-01T18:00:00Z | **2023-03-05T18:00:00Z** | 0.25° | **Stale** | Cite NCEI (ERDDAP) | **No** (GFS direction in NRT vs ERA5 in science `source` attr.) |
| **ERA5 single levels (CDS)** | [reanalysis-era5-single-levels](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels) | — | 1940-01-01 | 2026-09-22 (catalogue extent) | 0.25° hourly | **~5 d** (ERA5T; catalogue text) | CC-BY-4.0 | **Yes** |
| **NCEP GFS (PacIOOS `ncep_global`)** | [ncep_global](https://pae-paha.pacioos.hawaii.edu/erddap/griddap/ncep_global) | `ncep_global` | **2022-12-01T12:00:00Z** | 2026-10-05T15:00:00Z (incl. forecast) | 0.5°; 3 h | **≤ 2 d** for recent analyses (`testOutOfDate=now+136hours`) | ERDDAP disclaimer | **Yes** but **no pre-2022 archive** on this ERDDAP set |
| **ASCAT Metop-C QC 1-day (PFEG)** | [erdQCwindproducts1day](https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdQCwindproducts1day) | `erdQCwindproducts1day` | 2021-09-03T12:00:00Z | 2026-09-08T12:00:00Z | ~0.33° | **~20 d** | ERDDAP disclaimer | **Yes** but **no 1996–2020 coverage** |
| **ASCAT all Metop QM 1-day (PFEG)** | [erdQMwind1day](https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdQMwind1day) | `erdQMwind1day` | 2013-08-27T12:00:00Z | **2022-12-31T12:00:00Z** | 0.25° | **Stale** | ERDDAP disclaimer | N/A (feed stopped) |

Machine-readable copy of candidates: `config/wind_candidates.yaml`.

## Per-candidate notes

### 1. CCMP v3.x (Remote Sensing Systems)

- **Product page:** [remss.com/measurements/ccmp/](https://www.remss.com/measurements/ccmp/) — documents **CCMP 3.1** on a **0.25°** grid, **CC-BY-4.0**, and states v3.1 changes *“make it possible to produce CCMP 3.1 with low latency”* (qualitative; no ≤2-day SLA in HTML).
- **Archive:** HTTPS browse [data.remss.com/ccmp/v03.1/](https://data.remss.com/ccmp/v03.1/) shows **`Y1996` … `Y2026`**; **`Y2026/M08`** contains `CCMP_Wind_Analysis_20260831_V03.1_L4.nc` with directory timestamps **2026-09-17** → about **17-day** publication lag on 2026-09-28.
- **Separate NRT tree:** [data.remss.com/ccmp/v02.1.NRT/](https://data.remss.com/ccmp/v02.1.NRT/) remains **v2.1** (`CCMP_RT_*_V02.1_*` filenames), earliest **`Y2015`**, **~1-day** lag (20260927 posted 2026-09-28). That is a **different version** from v3.1 reanalysis.
- **ERDDAP:** FishAI `data/SOURCES.yaml` points at `ccmp-daily-v2-1-NRT` on `coastwatch.pifsc.noaa.gov`. That hostname **did not resolve** during this survey (`curl: Could not resolve host`). PFEG ERDDAP returned **404** for `ccmp-daily-v2-1-NRT` info URLs.

### 2. NCEI Blended Sea Winds v2.0

- **Science quality daily** ERDDAP [`noaacwBlendedWindStressDaily`](https://coastwatch.noaa.gov/erddap/info/noaacwBlendedWindStressDaily/index.json): `time_coverage_start` **1987-07-09**, `time_coverage_end` **2026-08-31**, 0.25° **vector wind stress** (not neutral u/v). `source` lists satellites + **direction from ERA5**.
- **NRT companion** [`noaacwBlendednrtWindStressDaily`](https://coastwatch.noaa.gov/erddap/info/noaacwBlendednrtWindStressDaily/index.json): title claims “last ~45 days”, but metadata **`time_coverage_end` = 2023-03-05** — **not current in 2026**. NRT `source` uses **GFS0.25** for direction vs ERA5 in science → **inconsistent processing** across streams.

### 3. ERA5 (Copernicus CDS)

- Catalogue [`reanalysis-era5-single-levels`](https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-single-levels): extent through **2026-09-22**, **0.25°**, licence **CC-BY-4.0**, description states **“updated daily with a latency of about 5 days”** (ERA5T).
- **Meets** unified reanalysis for 1996–2022 training, but **does not meet** the **≤ 2 day** nowcast latency requirement. Accepting ~5 days would be a **project policy decision**, not met by the stated bot2 threshold.

### 4. NCEP GFS / NAM analyses

- **GFS via PacIOOS ERDDAP `ncep_global`:** [`info/ncep_global/index.json`](https://pae-paha.pacioos.hawaii.edu/erddap/info/ncep_global/index.json) — **`time_coverage_start` 2022-12-01** only; 0.5° 3-hourly; **`testOutOfDate`: `now+136hours`** (recent analyses within ~2 days, plus forecast tail to 2026-10-05). **Insufficient history** for CUFES training without a separate reanalysis archive.
- **NAM:** PacIOOS `nam_3hourly` ERDDAP info returned **HTTP 404** on 2026-09-28 (not documented further here).

### 5. ASCAT on CoastWatch ERDDAP

- **coastwatch.pfeg.noaa.gov:** search API lists multiple ASCAT griddap sets. **`erdQCwindproducts1day`** (Metop-C, 2020-present in title): coverage **2021-09-03 → 2026-09-08**, ~**20-day** lag vs survey date. **`erdQMwind1day`**: ends **2022-12-31** (stale).
- **coastwatch.noaa.gov:** griddap index includes blended **wind stress** products above; **no separate ASCAT u/v** datasets appeared in the griddap index JSON (1000 rows scanned).

## Recommendation

### **`none qualifies`**

No surveyed product satisfies **all three** requirements together:

1. **Full CUFES training window (1996–2022)** with continuous gridded surface winds over the SCB.
2. **Near-real-time nowcast latency ≤ 2 days** with confirmed updates in **September 2026**.
3. **One consistent processing chain** for both historical training and operational nowcast.

**Why the near-misses fail**

| Product | Blocker |
|---------|---------|
| **CCMP v3.1** | Single consistent v3.1 reanalysis and full history, but **~17-day** lag vs calendar (not ≤2 d). |
| **CCMP v2.1 NRT** | **~1-day** latency and active 2026 files, but **v2.1 algorithm**, history only from **~2015**, incompatible with v3.1 training archive. |
| **NCEI Blended v2.0 science** | Long science record through **2026-08-31**, but **~28-day** lag; NRT ERDDAP stream **frozen 2023** and **different direction prior**. |
| **ERA5** | Unified reanalysis **1940–present**, but **~5-day** ERA5T latency (**not ≤2 d**). |
| **NCEP GFS `ncep_global`** | Good recent latency, but ERDDAP archive starts **2022-12-01** — no 1996–2022 training. |
| **ASCAT ERDDAP composites** | Either **too short** (post-2013/2021) or **stale** / **>2-day** lag. |

**Suggested follow-ups (out of scope for this PR)**

- Negotiate RSS CCMP **v3.1 operational latency SLA** or a documented NRT v3.1 stream (if/when published separately from v2.1.NRT).
- Restore or replace **NCEI blended NRT** ERDDAP (`noaacwBlendednrtWindStressDaily`) and confirm direction harmonization with the science product.
- If policy allows **>2-day** nowcast lag, re-open **ERA5** or **CCMP v3.1** under an explicit latency exception.

## Evidence pointers

- CCMP v3.1 latest file listing: `https://data.remss.com/ccmp/v03.1/Y2026/M08/`
- CCMP v2.1 NRT September 2026 listing: `https://data.remss.com/ccmp/v02.1.NRT/Y2026/M09/`
- Blended science / NRT ERDDAP info URLs in table above
- ERA5 CDS collection JSON (latency sentence in `description` field)
- PacIOOS GFS ERDDAP `time_coverage_start` / `testOutOfDate`
