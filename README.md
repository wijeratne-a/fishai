# FishAI — Southern California Bight pilot

FishAI is a **50-mile nowcast skeleton** for the Southern California Bight pilot domain (**32–35°N, 121–117°W**). The active program ingests **CalCOFI CUFES sardine/anchovy egg-stage evidence**, **WCOFS/GLORYS-class physics**, and **SCCOOS HF radar / NDBC / IOOS glider consistency checks**, then fits **sdmTMB delta-lognormal** models in R. This branch provides installable layout, CI, and contracts—not live ingestion or published nowcasts.

## Evidence-state vocabulary

Map and API outputs must use one primary evidence state (plus uncertainty), not conflated labels:

| State | Meaning |
| --- | --- |
| **Direct Observation** | Structured survey or instrument detection at known effort (for the pilot: **egg-stage CUFES counts**, not adult fish presence). |
| **Historical Pattern** | Learned or climatological pattern without a contemporaneous detection. |
| **Current Nowcast** | Model or fused estimate for the valid nowcast window with documented inputs. |
| **Forecast** | Forward-looking statement with explicit issue time and valid window. |
| **Unknown** | Insufficient evidence to assign a stronger state. |

**CUFES labels are egg-stage evidence.** They support spawning-habitat and egg-density questions; they must **not** be displayed or modeled as adult fish presence without a separate life-stage contract.

## Repository layout

```
src/fishai/
  ingestion/biology/     CalCOFI CUFES (erdCalCOFIcufes); SWFSC CPS trawl haul catch (FRDCPSTrawlLHHaulCatch)
  ingestion/physics/     WCOFS; GLORYS (training/hindcast only; T/S at 3 m linear z)
  physics/store.py       Read-only ``open_wcofs_cycle`` / ``list_wcofs_cycles`` (Bot4 sensors)
  ingestion/sensors/     SCCOOS HF radar, NDBC, IOOS glider stubs
  models/                Python experiment config, baselines, run manifest
  models/R/              sdmTMB R code (bootstrap via renv)
  evaluation/            Metrics and numeric support mask (reusable)
  validation/            Survey file eligibility gate
  api/                   Future nowcast API stub
  schemas/               JSON schemas for observations and provenance
data/SOURCES.yaml        License manifest (CI-enforced for ingestion modules)
labels/                  Label validation rules (YAML/JSON)
science/                 Measurement and temporal integrity rules
security/                Sensitive-data pre-commit scanner
tests/                   Unit and synthetic protocol tests (no network)
docs/archive/            Archived planning, audit, and legacy scripts
```

Legacy one-off modeling and acquisition code lives under `docs/archive/legacy_scripts/`. **`ingest.py` event hashing (ship_code omitted) and SEAMAP `zero_fill.py` were not ported.**

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

CLI entrypoints (stubs exit non-zero):

```bash
fishai-bio
fishai-physics
fishai-sensors
fishai-models
```

### R / sdmTMB

```bash
Rscript renv/scripts/bootstrap.R   # network required; refreshes renv.lock
```

Target packages: **sdmTMB**, **fmesher**, **sdmTMBextra**.

### Docker

```bash
docker build -t fishai-pilot .
docker run --rm fishai-pilot
```

## CI

GitHub Actions runs: editable install, `pytest`, `security/precommit_sensitive_scan.py`, checks for committed data under `data/raw`/`data/processed` and forbidden binary extensions, and ingestion coverage in `data/SOURCES.yaml`.

## Data policy

Do not commit raw coordinates, telemetry, or grid binaries (see `.gitignore`). Tests use synthetic fixtures only.

## SWFSC CPS trawl haul catch (`FRDCPSTrawlLHHaulCatch`)

**Provenance:** NOAA SWFSC Fisheries Resources Division coastal pelagic species (CPS) mid-water trawl surveys (DEPM, acoustic-trawl, SaKe), served on CoastWatch ERDDAP (`oceanview.pfeg.noaa.gov`). Related tables: `FRDCPSTrawlLHSpecimen`, `FRDCPSTrawlLHLengthFrequency` (individuals/length bins for subsets of catches).

**License:** ERDDAP `NC_GLOBAL.license` (recorded verbatim as `license_text` in `data/SOURCES.yaml` and `cps_trawl_metadata.json` after sync).

**Outputs:** `data/processed/swfsc_cps_trawl_haul_catch/cps_trawl_hauls.parquet` (tow metadata and effort) and `cps_trawl_catch.parquet` (long catch). Haul key: `CPSTrawl:{cruise}:{ship}:{haul}`.

**Effort fields:** Tow duration (minutes) and great-circle distance (nautical miles) are computed from start/stop times and coordinates when present. **Net mouth area is not in the dataset** — `net_mouth_area_m2` is always null with reason `not_in_source_dataset`. Ship speed uses `ship_spd_through_water` when reported.

**Catch semantics:** `subsample_count` is the source subsample count (not a raised haul total). Optional `count_raised_est` is computed only when both weight fields are present and `subsample_weight > 0`. If exactly one of `subsample_weight` / `remaining_weight` is present, `weight_kg` is null and `weight_flag=weight_partial` (partial values kept in separate columns).

**Zero-catch gate:** Implied zeros require a per-cruise+ship entry in `config/cps_trawl_zero_frame_evidence.yaml` (shipped empty). A cruise is VERIFIED only when the entry lists `expected_hauls` equal to `report_haul_log` minus `aborted_tows`. `expand_haul_species_matrix()` refuses zeros otherwise (`zero_frame_unverified`, `haul_not_in_verified_frame`, etc.). Hauls whose only catch is `Animalia` are always excluded (`animalia_only_undocumented`). `presence_only=Y` never receives weight; missing weights are never zero.

**CLI:** `fishai-bio sync cps-trawl --start YYYY-MM-DD --end YYYY-MM-DD` (batched yearly ERDDAP CSV → raw cache → parquet).
