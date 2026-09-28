# Execution report

```
BIOLOGICAL DATA ACQUIRED: yes, Florida Keys rows from CRCP_Reef_Fish_Surveys_Florida
YEARS ACQUIRED: 2018, 2022, 2024
EVENT FRAME VERIFIED: yes. Key YEAR + PRIMARY_SAMPLE_UNIT + STATION_NR + time. Events 843, 648, 622. No metadata collisions.
ZERO SEMANTICS: CONSTRUCTIBLE_SURVEY_NONDETECTION at species level in all three years
FIRST SPECIES: Chaetodon capistratus (CHA CAPI, WoRMS 159661)
ENVIRONMENTAL DATA ACQUIRED: survey depth, visibility, and habitat used in the baseline. A 5,186-byte MUR SST box was saved and not joined.
BASELINE FIT: yes, internal logistic versus prevalence. Spatial-block Brier 0.2446 versus 0.2621. Not published.
PUBLICATION STATUS: NOT_PUBLISHED. AUTO_ACQUIRE_INTERNAL_ONLY.
NEXT BLOCKER: join a date-matched temperature field and confirm whether it beats this survey-only baseline. Do not publish.
FINAL DECISION: PROCEED_TO_ENVIRONMENTAL_JOIN
```

## What was executed

```text
python3 scripts/acquisition/download_noaa_rvc.py 2018
python3 scripts/acquisition/download_noaa_rvc.py 2022 2024
python3 scripts/validation/validate_noaa_rvc.py
python3 scripts/modeling/fit_internal_baseline.py
python3 -m unittest tests/test_rvc_acquisition.py
```

ERDDAP classification is `AUTO_ACQUIRE_INTERNAL_ONLY`. The dataset attributes say no access constraints and no use constraints. They do not authorize a public nowcast. Raw files are gitignored.

## Files

| Year | Rows | Uncompressed bytes | Compressed bytes | SHA-256 |
|---|---:|---:|---:|---|
| 2018 | 476,377 | 181,576,416 | 9,268,221 | `18761a19f00ee9becea2973b07ad957728ff98e2299d537da153308917ba819a` |
| 2022 | 221,842 | 84,856,311 | 4,669,159 | `80483d603630453ccd2b7adf4ff7e82f2398bdbc112ac96a9161185c0739a204` |
| 2024 | 356,254 | 134,399,101 | 7,795,903 | `f022ee17600974c92050f019365e6cf8646fe2aec651d13dc8a9d4682c460476` |

Accession URLs in the files match 0208321, 0282183, and 0306184.

Goliath grouper code in this table is `EPI ITAJ`. Detection events: 1, 1, and 6. It was not fit.

## Git

Safe to commit: scripts, tests, audit notes, `data/metadata/`, `data/manifests/`, `.gitignore`.

Must stay local: `data/raw/`, `data/interim/`, `data/restricted/`, and any file with survey coordinates. The gzip tables and the SST sample are ignored.

## Single next action

Join survey-date sea temperature to the 2,113 butterflyfish events inside protected storage, then repeat the same five-block Brier comparison. Do not put the result on the globe.
