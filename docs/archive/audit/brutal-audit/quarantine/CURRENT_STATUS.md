# FishAI current status

> **STALE as of 2026-09-27 — do not use as an operator runbook.**
> Restore was run (`BACKUP_VERIFIED`). MUR and OISST were joined. The two Puerto Rico 2023 Briers cited below are `UNTRUSTED_AS_GENERALIZATION` (holdout reused; three disagreeing estimators; future-day SST join; vis/depth imputed).
> Read `audit/brutal-audit/EXECUTION_REPORT.md`. Do not follow “What is next.”

**As of:** 2026-09-25  
**Phase:** global data acquisition. Internal baselines already exist and are not being expanded in this phase.  
**Publication:** no species card is `PUBLISHED`. No nowcast or forecast is issued.

## Product

FishAI is a marine globe plus a local store of public survey and ocean files. The intended product is a probability of detecting a named species on a documented survey, in a named region, depth, and time. That probability is not on the map.

The running globe shows Earth, past reports, and unknown. It does not show where animals are right now.

## Globe

Branch `integrate/globe-ux-2026-09-23`. Integration commit `478983b`. Stabilization commit `0bf64b5`. Build passed. Behavior was checked on both loopback address families.

The interface is a functional historical atlas. Goliath grouper stays `no_estimate`. The only model card is Pacific oyster, `NOT_PUBLISHED`. The Willapa screen is a synthetic working-conditions demo, not an animal location.

A map-moving stall was logged and not reproduced, so the camera code was left unchanged. Painted focus ring, pointer drag, pinch, and right-drag tilt were not verified in that session.

## Goliath grouper

The card remains `NOT_PUBLISHED`. A first detection model was judged conditional on a rights-cleared, zero-bearing survey, then the species was dropped as the first fit.

In the Florida Keys Reef Visual Census extract the code is `EPI ITAJ`, not `EPIITAJ`. Detection events are 1 in 2018, 1 in 2022, and 6 in 2024. That is too few for a species model. The Great Goliath Grouper Count, FACT telemetry, REEF surveys, and FSU mark-recapture notes are not a training table. Tracks, wrecks, nurseries, and spawning sites are not in the repo.

## Surveys on disk

Raw files are under `data/raw/` and Git ignores that directory. A checksum check of 25 manifest entries reported 25 matches and 0 mismatches. A backup restore has not been run, so no backup is claimed.

Atlantic tables repeat one species list on every dive in a given year and include `NUM = 0`. `NUM` is a real average, not an integer fish count. A species counts as detected if any length-bin row is positive. A survey non-detection is not proof the animal was absent from the surrounding reef. List size changes by year, so a code is a non-detection only in years that include it.

| Region | Years on disk | Holdout year | Frame |
|---|---|---|---|
| Florida Keys | 2014, 2016, 2018, 2022, 2024 | 2024 | Zero-bearing. The 2024 file validated at 356,254 data rows |
| Puerto Rico | 2016, 2019, 2021, 2023 | 2023 | Zero-bearing. 248 events in 2023 |
| U.S. Virgin Islands | 2017, 2019, 2021, 2023 | 2023 | Zero-bearing. 562 events in 2023 |
| Flower Garden Banks | 2018, 2022, 2023, 2024 | 2024 | Zero-bearing. 38 events in 2024 |

Not in these ERDDAP year lists, so not downloaded: Florida 2020, Puerto Rico 2014, USVI 2013 and 2015, Flower Garden Banks 2013 and 2015. A 2025 reef-fish file was not in the catalog.

Pacific tables for Hawaii, American Samoa, CNMI/Guam, and the Pacific Remote Islands have positive counts and no zeros. Replicate IDs exist. Non-detections cannot be constructed. They are presence layers only.

A separate CalCOFI CUFES sample, cruise 202204 (April 2022), is stored locally (39,321 bytes, about 418 rows). It is classified `AUTO_ACQUIRE_INTERNAL_ONLY`. It is an egg survey, not a live fish map.

## Presence records and ocean fields

OBIS: 672 of 672 Florida Keys records from 2026-06-26 through 2026-07-23 were saved by splitting the query into weeks, because page offsets were ignored. They were not used as training rows. They are not current locations.

MUR analysed sea-surface temperature exists only as a small snippet with valid time 2026-09-23. It is not joined to survey dives. No forecast grid was saved. GBIF bulk download still needs an account. Copernicus has no credentials here.

## Internal models

These are not on the globe.

An earlier Florida Keys fit for foureye butterflyfish (*Chaetodon capistratus*) beat a prevalence baseline on spatial blocks (Brier 0.2446 versus 0.2621). That run was not the later holdout design.

The later suite trained on earlier years and scored the latest year once. Sixteen species models were fit. Two passed both the spatial blocks and the untouched holdout, both in Puerto Rico:

- Bicolor damselfish, *Stegastes partitus*. 2023 holdout Brier 0.195 versus prevalence 0.205.
- Redband parrotfish, *Sparisoma aurofrenatum*. 2023 holdout Brier 0.232 versus prevalence 0.248.

Florida, USVI, and Flower Garden Banks did not clear that bar. The USVI logistic fits diverged to non-numeric scores and are rejected. No environmental model was tested. No species is ready for an internal nowcast. The modeling decision on that suite is `MORE_ENVIRONMENTAL_COVERAGE_REQUIRED`. The acquisition phase after that is still `CONTINUE_GLOBAL_DATA_ACQUISITION`, and it does not add more fits until the user ends that phase.

## Contracts and safety

JSON schemas exist for sources, events, observations, effort, taxa, measurements, provenance, and future globe evidence. They are not wired to the live map. Internal model output is a different label from a published nowcast or forecast.

A pre-commit style scan of tracked-style trees reported no sensitive hits. Coordinate-bearing survey files stay under `data/raw/`. Workstream status is in `planning/parallel-workstreams/WORKSTREAMS.yaml`.

## What is next

Match historical sea-surface temperature to the Puerto Rico survey dates inside protected storage, then repeat the 2023 holdout for the two accepted species only. Keep that result off the globe. Keep acquiring public survey files. Do not publish goliath locations, a forecast, or a current-location layer.
