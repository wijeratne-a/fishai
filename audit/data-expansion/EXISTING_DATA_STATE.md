# Existing data state

Checked 2026-09-24 before the regional downloads.

Florida Keys Reef Visual Census files were already present and were not downloaded again:

| Year | Rows | SHA-256 |
|---|---:|---|
| 2018 | 476,377 | `18761a19f00ee9becea2973b07ad957728ff98e2299d537da153308917ba819a` |
| 2022 | 221,842 | `80483d603630453ccd2b7adf4ff7e82f2398bdbc112ac96a9161185c0739a204` |
| 2024 | 356,254 | `f022ee17600974c92050f019365e6cf8646fe2aec651d13dc8a9d4682c460476` |

Latest Florida observation date on the ERDDAP dataset is 2024-11-26. The internal butterflyfish baseline was already fit. Zero semantics for those three years are `CONSTRUCTIBLE_SURVEY_NONDETECTION` at species level.

No other NCRMP region was on disk before this run.
