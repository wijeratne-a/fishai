# Training problem — Florida Keys goliath grouper detection model

**Date:** 2026-09-23  
**Milestone:** Prediction MVP — Florida Keys Goliath Grouper Detection Nowcast  
**Feasibility:** CONDITIONAL GO  
**Training status:** not started  
**Card:** `NOT_PUBLISHED`

The model is specified. The survey design is specified. Training has not started because a usable dataset is not in hand. Getting that dataset is the current hurdle.

## The training problem

The first model is a probability of detecting Atlantic goliath grouper (*Epinephelus itajara*, AphiaID 159353) on a completed Reef Visual Census dive, in the Florida Keys, at the recorded depth, under the documented survey protocol.

That likelihood needs, for every dive:

- a sample-unit identifier
- a date
- depth
- effort
- habitat or stratum
- a detection or a real non-detection

A file of sightings only cannot train it. A missing species row is not a zero unless the full list of completed dives proves the dive happened and the species was not recorded.

## Why training is blocked

| Need | State |
|---|---|
| Written training and aggregate-display approval | Absent. Status remains `CONDITIONAL_REVIEW_REQUIRED`. |
| Frozen file hash | None. No survey file has been downloaded. |
| Verified zeros | Unverified. The tables have not been opened. |
| `EPIITAJ` present in the table | Unknown. |
| A second, protocol-matched season for a time check | Not cleared. |
| Named reviewer and publisher | None. |

Public pages, a citation request, and a parent collection’s partial CC0 language are not that approval.

## Why the data in hand is not the training set

- The compiled OBIS total (332,628 rows, 1935–2026) is a historical mix of datasets. It has no survey effort and no non-detections.
- Smith et al. (2011) defines the frame: a 200 m primary cell and a 15 m second-stage plot, usually searched by a buddy pair, inside the Keys and Dry Tortugas. It does not contain the data table, and it does not mention goliath grouper.
- NCEI Accession 0208321 is the 2018 field season, published in January 2020. It is set aside as too old for the first training extract.
- Accession 0282183 (1 June–28 November 2022) is the newer file whose page still describes the two-stage design and includes the Keys. It is not approved and not downloaded.
- Accession 0306184 (29 May–26 November 2024) is the newest season. Its page describes a single-stage design, so it is not the same protocol.

## What has to happen before any fit

1. A written yes for acquisition, storage outside the public repository, training, and coarsened display, for 0282183 and 0306184.
2. Download only after that yes. Record the URL, time, file name, byte size, and SHA-256. Keep coordinates out of git, the app, and fixtures.
3. Count dives, `EPIITAJ` detections, valid non-detections, dates, depth, and effort. Confirm the zero rule from the sample frame.
4. Fit the seasonal, depth/habitat, and spatial baselines only after that count exists.

Until those steps are done, the globe stays a historical atlas with no goliath estimate, and no nowcast or forecast is issued.

## Florida programs that still do not train the model

These five Florida observation programs were named as candidates. None clears the detection-given-effort bar today. Rights stay `UNKNOWN` or `CONDITIONAL_REVIEW_REQUIRED`. Native sites stay blocked. No nowcast or forecast is issued. Training remains blocked as above.

**Great Goliath Grouper Count (GGGC).** Florida Sea Grant and FWC have run a June volunteer visual count on artificial reefs since 2010. CLAIM only: trained divers, standardized forms, first two weeks of June, abundance and size-class estimates used in stock assessments. Effort on the blank form is partial; nondetections are unknown; the June artificial-reef window is high-sensitivity and is not a random absence frame.

**FACT Network acoustic telemetry.** FWC and partners operate an Atlantic-coast acoustic array. CLAIM only: roughly 2010–2020, about 7 million detections across 153 sites, with home-reef residence, migration, and spawning-site fidelity. Tracks and aggregation geometry are `not_suitable` for public location products and do not supply a survey nondetection frame for untagged animals.

**REEF Volunteer Fish Survey Project.** CLAIM only: diver surveys since 1993, tens of thousands of surveys, used by FSU and FWC for recovery trends and juvenile mangrove habitat in Florida. Volunteer site choice is opportunistic effort; zeros are not a designed random frame; rights and native sites are uncleared.

**NCRMP Reef Visual Census.** Still the strongest structured candidate on paper (portal span from 1999). CLAIM only: adult goliath density and occurrence on Florida coral reefs including the Keys and Dry Tortugas, with low occurrence so sample sizes can be small. Repo state is unchanged: zeros and `EPIITAJ` are unverified; accession 0208321 (2018 season, published 2020) stays set aside; 0282183 (2022) and 0306184 (2024, single-stage on the landing page) are the later screened accessions; rights remain `CONDITIONAL_REVIEW_REQUIRED` with exit gate `BLOCKED`.

**FSU mark-recapture and sonic tracking (1994–2005).** Program class only: juvenile settlement research in the Ten Thousand Islands region class and adult spawning-aggregation tracking. No sites, wrecks, creeks, or aggregation coordinates are recorded. Telemetry and aggregation geometry fail both the sensitive-location rule and the detection-given-effort training target.
