# FishAI 50% review

> **BRUTAL AUDIT 2026-09-27 — two gates below are false as written.**
> `Join historical ocean data without future leakage` was marked Pass. The join used survey-date **plus t+1 and t+2**. That is post-event leakage. The join is also a regional-box mean, not an event location.
> `Beat a simple baseline on a later year` was marked Pass. 2023 was inspected for species selection, MUR, then OISST. Three survey-only Briers exist for the same claimed experiment (0.1953 / 0.194543 / 0.193133).
> Decision `NEEDS_MORE_ENVIRONMENTAL_COVERAGE` still holds. Publication still `NOT_PUBLISHED`. Globe still has no probability layer. See `audit/brutal-audit/`.

**As of:** 2026-09-26  
**Allowed decision (one):** `NEEDS_MORE_ENVIRONMENTAL_COVERAGE`  
**Publication:** `NOT_PUBLISHED`  
**On the globe:** **no**  
**Internal nowcast backtest:** **closed**

This review is an internal status against the evidence-tier table in `research/global-life-tracking/FISHAI_ROADMAP_BY_EVIDENCE_TIER.md`. It is not a license to draw fish on the map.

## Decision

`NEEDS_MORE_ENVIRONMENTAL_COVERAGE`

Survey-conditioned detection works for two Puerto Rico species on a locked later year. A second historical SST product was matched to the same events and scored once after the join rule was frozen on 2016–2021. It did not earn a place. The only depth-resolved temperature ID found (`hycom_gom310D`) is a Gulf of Mexico 2009–2014 grid and cannot be joined to Puerto Rico 2016–2023. Forecast endpoints for the pilot variables are missing. Milestone 6 (internal nowcast backtest) therefore stays closed.

## What 50% required

One or more regions can, internally and reproducibly: ingest public surveys, keep event and zero meaning, join historical ocean data without future leakage, beat a simple baseline on a later year, reject unsupported conditions, and still show only a historical atlas on the globe.

That bar is met for **survey-only** Puerto Rico detection. It is not met for an environmental nowcast.

## Evidence against the roadmap gates

| Gate | Result |
|---|---|
| Ingest public surveys with event and zero meaning | **Pass** for Atlantic NCRMP visual census and DFO Maritimes catch zeros. Reef Life Survey Method 1 and DATRAS hauls have tested event frames. CalCOFI station/tow/egg/larva tables are present; eggs stay eggs. Presence-only OBIS/Pacific COUNT stay in a separate catalog. |
| Join historical ocean data without future leakage | **Pass** for two SST products (MUR already; OISST `ncdcOisst21Agg_LonPM180` this path). Units `degree_celsius`. OISST valid time is the daily 12:00Z field; survey dates stay day precision. Missing fraction 0.0 on 174 Puerto Rico dates / 925 events. |
| Beat a simple baseline on a later year | **Pass** for survey-only *Stegastes partitus* and *Sparisoma aurofrenatum* on locked 2023 (`audit/prediction-test/PUERTO_RICO_FINAL_REPORT.md`). |
| Environmental covariate beats survey-only | **Fail.** MUR already rejected. OISST scored once after freeze; both species worse on Brier and log loss. Decision: `SST_ADDS_NO_VALUE`. |
| Reject unsupported conditions | **Pass** in synthetic tests (future leakage, missing-to-absence, unit mixups, unsupported cells, mixed protocols, omitted baseline, tune-on-holdout). |
| Historical atlas only on the globe | **Pass.** No public probability layer was written. |
| Restore-tested backup | **Pass.** Off-repo snapshot restore SHA-256 matched (`audit/storage/RESTORE_VERIFICATION.md`). |
| Model-eligible file gate | **Pass.** A synthetic bad file is rejected and quarantined; `data/raw/` is not edited. |

## Milestone record

| Milestone | Status |
|---|---|
| 1 Trust the records | Done. Restore `PASS`. Bad file rejected. `NUM` remains a real-valued average. |
| 2 Five programs, three methods, two non-US regions | Done. Programs: NCRMP RVC, Reef Life Survey / NRMN, ICES DATRAS NS-IBTS, DFO Maritimes Summer RV, CalCOFI. Methods: reef visual census, reef visual transect, bottom trawl, ichthyoplankton. Non-US regions: North Sea, Scotian Shelf / Bay of Fundy, global NRMN sample. Florida 2021 NCRMP year added (no invented 2025 file). |
| 3 Second historical ocean product | Done. OISST matched. Depth search recorded `hycom_gom310D` as ID-only, wrong domain. Current OISST/MUR endpoints listed. Forecast endpoints `MISSING`. Same join config can point at another region. MUR not rescored. |
| 4 Frozen experiment rules | Done. Invalid configs fail. Synthetic run writes `NOT_PUBLISHED` manifest. |
| 5 Environmental decision | Done. `SST_ADDS_NO_VALUE`. No globe layer. |
| 6 Internal nowcast backtest | **Closed.** Requires an accepted environmental model. |
| 7 This review | `NEEDS_MORE_ENVIRONMENTAL_COVERAGE` |

## What is still true

- FishAI is an internal, regional, survey-based detection system.
- Puerto Rico 2023 remains a locked observed benchmark, not a fresh year and not a refit target.
- A survey non-detection is not ecological absence.
- Pacific NCRMP COUNT tables and OBIS remain presence-only.
- CalCOFI egg and larva counts are not adult reef detections.
- RLS Method 1 sample in this run had no zero rows; zeros were not invented.
- DATRAS HL in this extract did not show explicit `HLNoAtLngt==0`; haul events and effort (`HaulDur`) are documented. Missing species on a haul are not treated as zeros.

## Explicitly still out of scope

Global live map, public probability layer, goliath or white-shark locations, OBIS as absence, Pacific zeros invented from missing species, neural models, telemetry as a census, larval particles as adult movement, and any forecast without archived issue time and valid time.

## Next scientific dependency

A depth-relevant or habitat-structure product that actually covers the Puerto Rico survey years and locations, or another non-SST variable with a real dataset ID, frozen on 2016–2021, then scored once on 2023. Until that variable beats or holds survey-only Brier and log loss with calibration within 0.15 of holdout prevalence, the retained model stays survey-only and the globe stays a historical atlas.
