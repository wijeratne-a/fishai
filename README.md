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
  ingestion/biology/     CalCOFI CUFES (erdCalCOFIcufes) stub
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
