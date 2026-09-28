# FishAI — end-to-end project context

**As of:** 2026-09-27  
**Audience:** next operator, next agent, or a human who has not been in the last chats.

This file is the current scientific and product picture. Several older status files are **stale or stamped untrusted**. Prefer this file, then the pointers in §11.

---

## 1. What this project is

FishAI is an **internal, scientifically honest, regional, survey-based detection system**.

The only claim that is currently defensible:

> For a **named common species**, in a **named region**, with a **named survey method and season**, estimate the **probability that a completed, documented survey records that species**, with uncertainty and a baseline, **inside training support**.

That is **question 2** (survey detection). It is **not** a live location, not a count of fish, not ecological absence, not a nowcast, and not a fishing recommendation.

The running globe is a **historical atlas**: Earth, past reports, and **unknown**. No species card is `PUBLISHED`. No probability layer is on the map. No nowcast or forecast is issued.

### What it is not

- A live global fish map, fish finder, or “where should I fish” product.
- A tracker of untagged individuals.
- A generic ocean dashboard or dump of Copernicus/HYCOM as animals.
- Occupancy (true presence) or abundance, unless a later program earns those separately.
- The paused commercial wedge in `README.md` (Willapa oyster email/PDF). That track was never locked. Do not treat it as the current program.

### How a result is supposed to be built

Biological constraints → survey evidence with zeros and effort → pre-registered hypotheses → **one locked later-year test** → a detection probability with a support mask. Habitat-suitability priors and presence-only maps are not a substitute for that chain.

Crowd data, if ever used, must be **complete checklists with effort**, not catch pins.

---

## 2. The nine questions (do not collapse them)

Defined in `research/predicting-fish-distributions/CORE_PROBLEM_DEFINITION.md`.

| # | Question | FishAI status |
|---|---|---|
| 1 | Population distribution | Habitat rasters missing. Spatial models wait on joins. |
| 2 | Survey detection | **The only working lane.** One trusted later-year pass (Keys damselfish 2022). |
| 3 | Relative abundance | Counts exist; no multi-year catchability-stable index model. |
| 4 | Individual movement | No tags. `REQUIRES_TELEMETRY`. |
| 5 | Population / seasonal redistribution | Surveys are warm-season only. Next adjacent step: Keys survey center-of-gravity **after** habitat joins. |
| 6 | Larval connectivity | One CalCOFI cruise is not validation. Wrong larval vertical behaviour can beat a passive particle model (Bode et al. 2019). |
| 7 | Nowcast | `UNSUPPORTED_BY_AVAILABLE_EVIDENCE`. No env term has passed a trusted later-year test **and** there are no contemporaneous labels. |
| 8 | Forecast | Same as 7, plus no issue-time forecast archive. |
| 9 | Climate redistribution | Later research lane. Not a product. |

Research recommendation (locked as methodology, not a globe change): **`FOCUS_ON_STRUCTURED_SURVEY_EXPANSION_FIRST`**.

Readiness labels used everywhere: `DO_NOW`, `DO_AFTER_ENVIRONMENTAL_JOINS`, `DO_AFTER_MORE_STRUCTURED_DATA`, `REQUIRES_TELEMETRY`, `REQUIRES_PARTNERSHIP_OR_RESTRICTED_DATA`, `NOT_RECOMMENDED`, `UNSUPPORTED_BY_AVAILABLE_EVIDENCE`.

---

## 3. Current state (honest)

**Publication:** `NOT_PUBLISHED` for every species card.  
**Globe:** historical atlas only. UI label is **“What is known”**, not “Where now.”  
**Brutal-audit decision (2026-09-27):** `UI_AND_LOGIC_REPAIRED_BUT_MODEL_RESULTS_UNTRUSTED` for the Puerto Rico / 16-species era.  
**Trusted later-year detection result:** Florida Keys bicolor damselfish, 2022, survey-only (habitat + depth + visibility).  
**Backup:** off-repo snapshot restore was tested (`audit/storage/RESTORE_VERIFICATION.md`).  
**Git:** last globe-related commit cited as `0bf64b5`; working tree has often been dirty; no remote assumed. Do not invent a clean history.

Older “about 30% complete / 50% review Pass” documents mixed later work with invalid Puerto Rico numbers. Use this file instead of `audit/project-status/CURRENT_STATUS.md` (banner: STALE) and do not treat the 50% leakage/holdout gates as Pass (`FIFTY_PERCENT_REVIEW.md` is bannered).

---

## 4. What the data actually mean

### Atlantic Reef Visual Census (NCRMP)

- Unit: completed dive (stationary point count).
- `NUM` is a **real-valued average**, not an integer fish count.
- **Detection** = any length-bin `NUM` > 0 after collapse.
- **Zero** is a non-detection **only if that species is on that year’s species list**. List size changes by year. Do not infer zeros from missing codes.
- A survey miss is **not** ecological absence from the reef.
- Rights: RVC record still `CONDITIONAL_REVIEW_REQUIRED`; permission letters `NOT_SENT`. ERDDAP pulls were classed `AUTO_ACQUIRE_INTERNAL_ONLY`. Nothing is cleared for public display.

| Region | Years on disk (typical) | Notes |
|---|---|---|
| Florida Keys | 2014, 2016, 2018, 2022, 2024 (2021 file has no Keys dives) | Best frame. 2022 burned for **bicolor damselfish only**. |
| Puerto Rico | 2016, 2019, 2021, 2023 | **2023 burned** (species pick, MUR, OISST). Do not rescore. |
| U.S. Virgin Islands | 2017, 2019, 2021, 2023 | Older logistic fits diverged (NaN). Convergence is now enforced. |
| Flower Garden Banks | 2018, 2022, 2023, 2024 | Tiny 2024 n (~38 events). Do not overclaim. |

Do **not** invent a 2025 reef file from a fieldwork announcement. If it is not in the catalog, it is not on disk.

Pacific NCRMP (Hawaii, American Samoa, CNMI/Guam, PRIAs): **positive counts only**. Presence-only. Never mint zeros. Never train as absence.

### Santa Barbara kelp forest (SBC LTER)

- Fish: `knb-lter-sbc.17.41`. Kelp: `knb-lter-sbc.18.30`.
- 11 **fixed** sites, late July–August, 40 m × 2 m FISH transect (80 m²). Not a regional map. Not winter.
- Detection: COUNT > 0; zero only if explicit species rows exist and all COUNT = 0. `-99999` or missing rows = `NOT_EVALUATED`, never zero.
- 2022 scored (and burned) for kelp bass and barred sand bass.

### Other biology (samples / not detection frames)

- CalCOFI cruise 202204: eggs/larvae, not adult reef fish.
- DATRAS / DFO / RLS: small public samples. Do not share the RVC zero constructor with them.
- OBIS Keys box: presence reports only; never training zeros; not “now.”
- GBIF: catalog only.

### Environment

- HYCOM GOFS 3.1 water_temp joined at dive depth for Keys and SBC. **Offsets allowed: `{0, -1, -2}` only.** Future-day joins are leakage (fixed after brutal audit).
- hycom.org GOFS 3.1 GLBy ends **2024-09-04**. FishAI preregistration used **2024-09-05**. Do not collapse those dates.
- Successor: **ESPC-D-V02** from 2024-08-10, 8-day forecast, **last 8 runs then scrubbed**, page flag `[missing data]`. Product shift vs GOFS must be tested.
- RTOFS: still on NOMADS HTTPS (dirs observed `rtofs.20260926/27`). OpenDAP on NOMADS retired **2026-02-23**. CoastWatch ERDDAP RTOFS search **HTTP 404**. RTOFS is not dead; that ERDDAP id path is gone.
- MUR/OISST: joined to Puerto Rico dates; join and holdout are **untrusted**.
- VIIRS chlorophyll over Keys reef: mostly masked / bottom-contaminated. Do not use as a default reef covariate.
- `data/raw/habitat/` is **empty**. Binding gap for distribution (Q1).
- Surface SST is **not** an accepted bottom proxy unless mixed-layer depth is verified at occupied depth.

Raw survey files: `data/raw/` (gitignored). Restricted env joins: `data/restricted/` (gitignored). Manifests and checksums: `data/manifests/`. Never commit coordinates, `.env`, or credentials. GBIF credentials live in gitignored `.env`.

---

## 5. Model results that still count

**Do not rescore** Puerto Rico 2023, Keys 2022 damselfish, or SBC 2022 bass. Locks exist. Rescoring is not new evidence.

| Result | Decision | Cite? |
|---|---|---|
| Keys *Stegastes partitus*, train 2014/2016/2018, test **2022 once** | `BEATS_BASELINE_BUT_MISCALIBRATED_ON_TEST_YEAR`. Brier **0.095 vs 0.125** prevalence; AUC 0.86; mean p 0.907 vs obs 0.855. Temperature **dropped** on training CV (0.08145 with T vs 0.08115 without). No year dummies. | **Yes**, as the one trusted Q2 example. Internal. Not published. |
| SBC kelp bass (*Paralabrax clathratus*), train 2001–2018, test 2022 | `DID_NOT_BEAT_BASELINE_ON_TEST_YEAR`. Brier 0.296 vs 0.244. Temperature passed site CV then failed the cooler 2022 year (pred 0.38 vs obs 0.60). | Yes, as a **failure**. Temperature is not a kept predictor. |
| SBC barred sand bass | Failed; 9 usable 2022 detections. Substitution for striped bass (zero rows). **Substitution unconfirmed.** | Failure / insufficient. |
| Puerto Rico 2023 STE PART / SPA AURO | **UNTRUSTED.** Holdout reused; three disagreeing estimators; future-day SST; vis/depth imputed to 15; year dummies score 2023 as 2016. | Do not cite as skill. |
| Older 16-species suite | 14/16 failed an untouched year; the two “passes” are the untrusted PR pair. USVI NaNs rejected. FGB n too small. | Do not treat as a successful fleet. |
| Goliath grouper | Keys detections 1 / 1 / 6 (2018/2022/2024). `INSUFFICIENT`. Sensitive. Stay `no_estimate`. | Do not model. Do not map sites. |

Estimator discipline for **new** fits: one estimator, explicit `TRAIN_YEARS`, no year dummies on temporal transfer, refuse missing depth/visibility, reject nonfinite coefficients, proper scores (Brier, log loss) vs named prevalence baseline, cluster bootstrap by site, calibration check. Spatial CV is **not** a later-year test. Accuracy/AUC/Boyce are not enough when zeros exist.

`predict` refuses out-of-support rows; `score()` currently does not (Keys and SBC both have this gap). Do not silently “fix” it by rescoring locked years.

Artifacts:

- Code: `scripts/modeling/florida_keys_one_species.py`, `scripts/modeling/socal_kelp_bass.py`
- Cards: `models/florida-keys/ste_part_v1.json`, `models/socal/kelp_bass_v1.json`, `models/socal/barred_sand_bass_v1.json`
- Locks/reports: `audit/florida-keys-one-species/`, `audit/socal-kelp-bass/`
- Tests: `tests/prediction-test/` (including brutal-audit guards)

---

## 6. Safety and display

`research/predicting-fish-distributions/SAFETY_AND_NON_TARGETING_BOUNDARIES.md`

**Never**

- Fishing, dive, spear, or harvest advice.
- Real-time untagged-fish positions.
- Fine grids of wrecks, nurseries, spawning aggregations, FADs.
- Tracks, receivers, tag IDs.
- AIS/VMS as fish.
- Catch pins as zeros or public hotspots.
- Publishing any probability without `PUBLISHED` **and** a support mask **and** a non-location label.

**Sensitive, withheld:** goliath grouper, white shark, aggregation/nursery/wreck sites.

If a layer is ever published: coarsen (typically ≥ 10 km for targeted taxa), delay, show valid time, model version, unknown, and extrapolation. Engineering cannot unsay a published grid.

---

## 7. What to work on next (scientific)

From `FISHAI_RESEARCH_PRIORITY_ORDER.md` and `FINAL_RESEARCH_DECISION.md`.

**Do now**

1. More common species on existing zero-bearing frames, **one locked model at a time**. Keys 2022 is still unused for species other than bicolor damselfish (disclose any design exposure).
2. WoRMS accepted-name map (audit TAX-001). No invented AphiaIDs.
3. Run manifests on every new fit.

**After habitat / bathymetry joins**

4. Keys spatial GLMM / sdmTMB with land/barrier mask, then survey center-of-gravity (Q5 within the survey domain, not tracks).
5. Archive ocean **analyses and forecasts** with issue time and valid time **now**. ESPC scrubs old forecast runs. GLORYS is a reanalysis, not an issued forecast.

**Do not**

- Issue a nowcast or forecast.
- Fit a macro “fish” or guild model.
- Train MaxEnt/GBIF as the product.
- Use N-mixture on single-visit RVC.
- Edit the Path-to-50% plan as if it were still the operator runbook.
- Expand the globe with unpublished probabilities.

Nowcast (all required, none fully met): env term that beat survey-only on a locked later year; issue-time fields at occupied depth; independent observations after freeze; skill vs climatology; safety coarsening. EPA NowCast analogue: refuse when contemporaneous data are missing (needs two of the last three hours). Biennial RVC is not a nowcast.

---

## 8. Repo map

| Path | Role |
|---|---|
| `research/predicting-fish-distributions/` | Canonical sparse-data research package (2026-09-27). Decision + matrices + 511 sources. |
| `research/global-life-tracking/` | Earlier source catalog S01–S123, EcoCast, occupancy, safety papers. Reused, not duplicated. |
| `audit/` | Brutal audit, Keys, SBC, Puerto Rico (untrusted), multi-species, project-status (partly stale), storage restore. |
| `scripts/modeling/` | Detection fits. Keys script is the template; SBC imports it. |
| `scripts/acquisition/` | Survey/ocean download scripts. HYCOM NCSS: use netcdf, not csv. |
| `models/` | Serialized internal cards. Not globe layers. |
| `globe/` | Historical atlas + visual contract. No live animals. |
| `observatory/` | Long-term scientific catalogs. Not a shipped census. |
| `science/` | Temporal integrity and related rules (future-day SST already forbidden). |
| `schemas/`, `labels/`, `evaluation/` | Contracts and tests. Not fully wired into every fit path. |
| `data/raw/`, `data/restricted/` | Gitignored payloads. |
| `data/manifests/` | Tracked checksums and source tables. |
| `README.md`, `decision_required.md`, `P0_WILLAPA_*` | **Stale commercial-pause track** (2026-09-18). Do not follow as current science. |
| `audit/project-status/CURRENT_STATUS.md` | **STALE.** Bannered. |

Research package highlights:

- `FINAL_RESEARCH_DECISION.md`, `EXECUTIVE_SUMMARY.md`
- `FISHAI_DATA_GAP_ANALYSIS.md`, `FISHAI_METHOD_RECOMMENDATIONS.md`
- Matrices: method comparison, sparse/bias, observation, movement (25 rows, none `DO_NOW`), nowcast (15), forecast (11), behavior (11 guilds × 33 variables), commercial tools (40)
- `SOURCE_INDEX.csv` — S01–S123 plus P001–P010, P300–P400, P500–P576, P700–P899
- Worker notes under `_work/` are not scientific sources; the published matrices are.

---

## 9. Standing operator rules

Copy these into any new chat that will touch code or reports.

1. No raw coordinates in git or reports.
2. No public globe prediction unless `PUBLISHED`.
3. Do not rescore PR 2023, Keys 2022 damselfish, or SBC 2022 bass.
4. `NUM` is a real-valued average.
5. Presence-only is never training absence.
6. Do not invent 2025 survey files.
7. Do not edit the 50% plan as current truth.
8. Never print or commit credentials.
9. Default chat replies are short bullets unless the user asks for a write-up.
10. One species, one estimator, one unused later year. Failures are results.
11. Confirm with the user before new model fitting if the request is ambiguous.
12. Python 3.8 in play historically: no dict `|` merge if that interpreter is used.
13. Do not use a shell variable named `path` (it clobbers `PATH` in zsh).

Cursor always-on rule: `/Users/wijeratne/dev/.cursor/rules/short-replies.mdc`.

---

## 10. Known engineering debts (do not “clean up” by rescoring)

- Eligibility gate still not wired into every `fit()` path.
- Year dummies remain in older regional design code; do not unlock 2023 to “fix” them.
- Habitat encoding mismatch existed across PR estimators.
- Unused random seed on some older runs.
- `score()` vs `predict()` out-of-support inconsistency.
- Globe pointer/pinch/tilt not fully re-verified after stall log.
- Large uncommitted planning/audit/script set; no assumed remote.
- Copernicus account may exist; products not ingested. GBIF needs the gitignored account.

---

## 11. What to read, in order

1. This file.
2. `research/predicting-fish-distributions/FINAL_RESEARCH_DECISION.md`
3. `research/predicting-fish-distributions/CORE_PROBLEM_DEFINITION.md`
4. `research/predicting-fish-distributions/FISHAI_DATA_GAP_ANALYSIS.md`
5. `audit/brutal-audit/EXECUTION_REPORT.md`
6. `audit/florida-keys-one-species/REPORT.md`
7. `audit/socal-kelp-bass/SUMMARY.md`
8. `research/predicting-fish-distributions/SAFETY_AND_NON_TARGETING_BOUNDARIES.md`
9. `research/predicting-fish-distributions/VALIDATION_AND_BACKTESTING_PROTOCOL.md`

Do not start from `README.md` or `CURRENT_STATUS.md` without their stale banners.
