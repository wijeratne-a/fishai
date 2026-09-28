# Completion and attention

**As of:** 2026-09-25  
**End state this percentage measures:** a defensible, uncertainty-aware probability of detecting a named fish on a documented survey, in a stated region, depth, and time, later extended to a validated nowcast and forecast, shown honestly on the globe.  
**Overall:** about **30%** of that end state.  
**Phase now:** `GLOBAL_DATA_ACQUISITION`. No species card is `PUBLISHED`. No nowcast or forecast is issued.

The percentage is a judgment of distance to that end state, not a count of files. The globe and the survey store are much further along than a live prediction.

## Completion by piece

| Piece | About | What that means |
|---|---:|---|
| Honest globe shell | 70% | Historical atlas runs. Current estimate and forecast stay off unless a card is published. Interaction bugs are still open. |
| Structured Atlantic surveys | 55% | Keys, Puerto Rico, USVI, and Flower Garden Banks have multi-year files with real zero rows. Many catalog years and 2025 releases are still absent. |
| Pacific and other surveys | 20% | Four Pacific regions are downloaded as positive counts only. CalCOFI is one cruise sample. Most national trawl programs are not acquired. |
| Labels, units, and contracts | 45% | Rules and tests exist. They are not applied to every raw file as a production pipeline. |
| Internal detection models | 20% | Two Puerto Rico species beat a prevalence baseline on a held-out year. Florida, USVI, and Flower Garden Banks did not. No environmental model. |
| Ocean predictors joined to dives | 5% | One sea-surface temperature snippet exists and is not matched to surveys. Bottom temperature, oxygen, chlorophyll, currents, and substrate are missing. |
| Nowcast and forecast | 0% | No current-condition join, no forecast grid, no species nowcast. |
| Serving a probability on the globe | 10% | The gate that refuses an unpublished layer works. Valid time, model version, extrapolation, and withheld-site states are not on the map. |
| Safety and reproducibility | 40% | Coordinates stay out of Git. Checksums for 25 files matched. The 16 fits cannot be rebuilt from a recorded seed, commit, and artifact hash. No backup restore has succeeded. |

## What is working

The globe shows Earth, past reports, and unknown. Goliath grouper stays `no_estimate`. The oyster card is `NOT_PUBLISHED`. The Willapa screen is a synthetic demo.

Atlantic Reef Visual Census tables repeat one species list per year and include `NUM = 0`. `NUM` is an average, not a count of fish. A species is detected only if any length-bin row is positive. A survey miss is not absence from the reef.

Puerto Rico 2023 holdout, trained on 2016, 2019, and 2021:

- Bicolor damselfish, *Stegastes partitus*. Holdout Brier 0.195 versus prevalence 0.205.
- Redband parrotfish, *Sparisoma aurofrenatum*. Holdout Brier 0.232 versus prevalence 0.248.

Those two results are internal. They are not on the map.

OBIS: 672 of 672 Keys records from 26 June through 23 July 2026 are saved and were not used as training rows. Checksums: 25 ok, 0 mismatch. Unit, time, label, contract, and synthetic end-to-end tests have passed in their own suites.

## What needs attention

**Do these before any published layer**

1. **Historical environment is not on the dives.** The two accepted Puerto Rico models use survey fields only. Bottom temperature, oxygen, chlorophyll, currents, and substrate are not in hand. A sea-surface temperature snippet from 23 September 2026 is not joined. Until a date-matched field is tested on the same 2023 holdout, there is no nowcast.
2. **Most fitted species failed the holdout.** Florida Keys species did not beat prevalence. USVI logistic fits went non-numeric and are rejected. Flower Garden Banks has 38 events in 2024 and did not beat the simple baseline. Do not treat the suite of 16 as a success.
3. **The 16 fits cannot be reconstructed.** They lack a git commit, random seed, environment lock, and artifact hash. Do not rerun them just to fill that gap unless the run is recorded from the start.
4. **No backup restore.** Checksums of the working copies passed. There is no separate backup location, so recovery is unproven.
5. **Goliath grouper is not a model.** Code `EPI ITAJ`: 1, 1, and 6 detection events. The card stays `NOT_PUBLISHED`. Do not map those points.

**Data problems that will distort a later model**

6. **Species lists change size by year.** A code is a non-detection only in years that list it. Pooling years as one protocol overstates comparability. Florida 2024 was described elsewhere as a single-stage design. It was used only as a holdout.
7. **Pacific tables have no zeros.** Hawaii, American Samoa, CNMI/Guam, and the remote islands can show positive counts. They cannot support a detection model until a completed-survey species list exists.
8. **2025 reef surveys are not in ERDDAP.** Puerto Rico’s public table ends 16 November 2023. The U.S. Virgin Islands end 18 August 2023. Florida ends 26 November 2024. Do not invent a 2025 file from a fieldwork announcement.
9. **OBIS is stale relative to “now.”** The newest saved Keys event date is 23 July 2026. Those rows are presence reports, not survey absences, and not current locations.
10. **Forecast ocean fields were not found.** A CoastWatch search for RTOFS returned HTTP 404. WCOFS was not subset. Copernicus needs an account. GBIF bulk download needs an account.

**Product and engineering**

11. **Globe interactions are unverified.** Painted focus ring, pointer drag, pinch, and right-drag tilt were not confirmed. A map-moving stall was logged, not reproduced, and not fixed.
12. **Scientific display is specified and not built.** Valid time, model version, extrapolation, withheld sensitive sites, and environmental latency are not on the live map.
13. **Contracts are not wired through.** Schemas and label tests exist beside the raw files. The acquisition path does not yet refuse a bad file by those schemas.
14. **A large set of planning and audit files is uncommitted.** Raw survey files must stay untracked. Manifests, scripts, and audits are the commit candidates. Do not commit coordinates.

## What not to treat as broken

The globe refusing a current location is correct. Unknown as the default is correct. Keeping goliath unpublished is correct. Leaving Pacific zeros uninvented is correct. Not calling the Puerto Rico baselines a nowcast is correct.

## Order of attention

1. Keep acquiring structured surveys that actually publish a file. Do not pause that for a redesign.
2. When modeling resumes, join historical sea temperature to Puerto Rico dates in protected storage and repeat only the two accepted species on the 2023 holdout. Do not tune on that year.
3. Record provenance on any new fit before it is run.
4. Prove a backup restore on a non-coordinate file, or keep the backup status blocked.
5. Leave the globe as a historical atlas until a reviewed model and a support mask exist.

**Overall: about 30% of the way to a served, validated detection product.** The honest map is largely in place. The prediction is not.
