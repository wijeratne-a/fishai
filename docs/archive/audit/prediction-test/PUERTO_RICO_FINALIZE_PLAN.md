# Puerto Rico prediction slice — finalize plan

**INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.**

Scope is only the internal Puerto Rico Reef Visual Census detection test for:

- `STE PART` (*Stegastes partitus*)
- `SPA AURO` (*Sparisoma aurofrenatum*)

Train years: **2016, 2019, 2021**. Untouched holdout: **2023** (score once; never tune on it). Do not refit other species. Do not modify globe/prototype, `model-cards.json`, or `PUBLICATION_DECISION.md`. Do not set `PUBLISHED`. `data/raw/` is read-only except downloading a missing year gzip into the existing NCEI path. No latitude/longitude in `audit/` or non-gitignored `data/processed` files. Coordinate-bearing environmental joins live under `data/raw/` or `data/restricted/` (gitignored).

Detection rule: species detected if any row for that code has `NUM > 0` (`NUM` is a real-valued average). Event key: `YEAR + PRIMARY_SAMPLE_UNIT + STATION_NR + time`. Survey non-detection is not ecological absence. A code is a non-detection only if it is on that year's species list.

---

## Goals and done-criteria

### 1. Confirm Puerto Rico gzip inputs

| Done when | Evidence |
|---|---|
| All four year files exist under `data/raw/biological/noaa-ncrmp/CRCP_Reef_Fish_Surveys_Puerto_Rico/{2016,2019,2021,2023}.csv.gz` and are non-trivial | Paths recorded with sha256 in `PUERTO_RICO_RUN_MANIFEST.json` |
| Any missing year is downloaded once from public NCEI ERDDAP `CRCP_Reef_Fish_Surveys_Puerto_Rico`; existing non-trivial files are not redownloaded | Download only if missing; else reuse |

### 2. Event table (survey fields + detection flags)

| Done when | Evidence |
|---|---|
| Events built with depth, visibility, habitat, year, subregion block, and detection flags for both species | In memory and/or under `data/restricted/` |
| No coordinates written to audit outputs | Final report states `COORDINATES IN REPORT: NO`; sanitize checks pass |

### 3. Historical SST join (`jplMURSST41` analysed_sst)

| Done when | Evidence |
|---|---|
| For each distinct survey date, analysed SST requested for a coarse Puerto Rico regional box (or event locations only inside `data/restricted/`) | Cache under `data/restricted/environmental/jplMURSST41/by-date/` |
| Survey-date SST assigned to events; never use a 2026 “latest” snippet as 2016–2023 condition | Join keyed by survey calendar date ±2 days |
| Dates with no SST within 2 days marked missing; missing fraction reported | Report field `SST MISSING FRACTION` |
| Requests: cache by date, sequential, backoff on 429/5xx; no fabricated values | Manifest records cache policy / blocker if any |
| If ERDDAP fails after retries: record hard blocker; still finish survey-only confirmation from existing test | `BLOCKERS:` in final report |

### 4. Fit models (fixed seed) on train years only

| Done when | Evidence |
|---|---|
| Prevalence baseline fit on training years only | Metrics in report |
| Survey-only L2 logistic: depth, visibility, year, habitat | Same |
| SST logistic (survey fields + survey-date SST) **only if** SST missingness on **training** events &lt; 20% | Same; otherwise SST model skipped with reason |
| Spatial-block comparison on training subregions | Spatial Brier recorded |
| 2023 scored **once** per model; no hyperparameter pick using 2023 | Seed `20260926`; holdout used only for final score |

### 5. SST acceptance rule

| Done when | Evidence |
|---|---|
| Retain SST model only if 2023 Brier **and** log loss are ≤ survey-only **and** mean predicted probability within 0.15 of holdout prevalence | `MODEL RETAINED` in report |
| Otherwise keep survey-only and state SST did not earn a place | Explicit in report body |

### 6. Final report

| Done when | Evidence |
|---|---|
| `audit/prediction-test/PUERTO_RICO_FINAL_REPORT.md` exists and begins with the required `FINAL STATUS` block | File on disk |
| Label present: INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED | Header / footer |
| `PUBLICATION: NOT_PUBLISHED`; `ON THE GLOBE: NO` | Status block |

### 7. Tests

| Done when | Evidence |
|---|---|
| Existing `tests/prediction-test/` unittests pass | unittest exit 0 |
| Any new synthetic SST/acceptance tests pass (no real coordinates) | unittest exit 0 |

### 8. Run manifest

| Done when | Evidence |
|---|---|
| `audit/prediction-test/PUERTO_RICO_RUN_MANIFEST.json` records seed, gzip sha256, git HEAD, `DIRTY_TREE`/`CLEAN`, SST missing fraction, model retained | File on disk |

---

## Out of scope

Globe/prototype changes, `model-cards.json`, `PUBLICATION_DECISION.md`, other species/regions, publishing, inventing SST skill after ERDDAP failure.

## Execution order

1. Write this plan (done when this file exists with the criteria above).
2. Confirm/download gzips → event table → SST join (or blocker) → fit → accept/retain → report → tests → manifest.
3. Stop only when all done-criteria are met or a hard external blocker is recorded with evidence.
