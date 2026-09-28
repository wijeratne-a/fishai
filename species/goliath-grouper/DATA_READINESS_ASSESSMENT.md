# Data readiness — Atlantic goliath grouper

**Date:** 2026-09-23  
**Branch:** `integrate/globe-ux-2026-09-23`  
**Issued product today:** no goliath estimate. Status remains `no_estimate`. The model card remains `NOT_PUBLISHED`. The globe shows historical pattern and unknown current state.  
**Project stage:** data clearance before the first prediction model.  
**Next milestone:** Prediction MVP — Florida Keys Goliath Grouper Detection Nowcast. That nowcast is not fitted and is not issued.

**Species.** Atlantic goliath grouper, *Epinephelus itajara*, WoRMS AphiaID 159353.

**Question.** Can FishAI define a first bounded, effort-aware occurrence model: the probability of detecting the species on a documented survey, in a stated region, depth band, habitat class, and time window?

**Answer in brief.** A candidate survey design exists in public NOAA and FWC descriptions. The files were not ingested. Rights are not approved. Non-detections are not confirmed. No region is cleared. The globe must keep showing historical pattern and unknown current state.

The row-level inventory is `SOURCE_INVENTORY.csv`. Region scores are in `REGION_SCREENING.md`. The decision is in `FIRST_MODEL_FEASIBILITY.md`.

---

## What “ready” means here

A source is ready for a prototype only if all of the following are true:

1. A human rights review records training rights, display rights, and attribution.
2. The table contains the sample frame, not only the rows where a goliath was seen.
3. Effort, date, depth, and method are on the sample.
4. Sensitive sites can be kept out of any public geometry.
5. A named reviewer has not yet been asked to bless a fit. Readiness of the table is not publication.

Public download pages fail item 1 until that review exists. This pass did not assign any `APPROVED_*` value.

---

## Taxonomy and occurrence context

WoRMS AphiaID 159353 is the name key already used in the app. It is not a map.

OBIS, queried for this project on 2026-09-22, returned **332,628** compiled rows with years **1935–2026**. That number is a compiler total. Year spikes in 2010–2016 are dataset composition. The current globe draws a coarsened past-report layer (at least 3 records, at most 80 cells, about 1 degree). That layer is historical context.

OBIS states that contributing datasets are CC0, CC BY, or CC BY-NC, and describes the aggregated product as CC BY-NC. A FishAI training extract still needs each source dataset’s terms. This assessment does not mark the 332,628 rows as trainable.

GBIF is a provenance index. One public resource inspected this pass, GBIF `d733adc7-eb4a-49fc-8bc8-bff87754b14c`, is tagging metadata under CC BY 4.0. It is not a reef-survey frame. Tracks and aggregation sites from that work stay out of the repo.

Museum lots were not added. They rarely carry survey effort or non-detections.

---

## Structured detection and non-detection

### Reef Visual Census (strongest candidate)

NOAA SEFSC and partners run a two-stage stratified random visual census on the Florida reef tract, with region codes for the Florida Keys, Dry Tortugas, southeast Florida, Puerto Rico, the US Virgin Islands, and Flower Garden Banks. The public analysis portal says CSV files cover 1999 onward. InPort item 8585 describes the program. A 2018 Florida Keys analysis-ready CSV is also on NCEI (accession 0208321). This pass did not download those tables.

FWC’s Keys page says visual sampling began in 1998, RVC methods were used from 2008, and surveys became biennial in even years after 2014. The same page says surveys are generally conducted from April through September, at depths up to 100 feet, with around 400 sites and 1,600 diver surveys in a season, and more than 11,000 Keys diver surveys since 2008. Those are program totals for the whole reef-fish survey, not goliath counts.

Published fields include sample unit, year, day, depth in meters, visibility, region, stratum, habitat code, latitude, longitude, and species counts. The portal’s species-code pattern is the first three letters of the genus plus the first four of the species, so the lookup key is `EPIITAJ`. Knowing the key is not the same as knowing how many samples recorded it.

**Non-detections are UNKNOWN.** If the file is a complete list of sample units and species rows are positive counts only, zeros can be built by joining. If the file is only positive records, it cannot support a detection model. That check is the next data task, and it happens only after a rights review.

### FWC inshore fisheries-independent monitoring

FWC describes stratified-random sampling in estuarine and coastal strata, with monthly random sites and gear. An open map service and a SEACAR file list exist. This pass did not query the service, because a goliath point extract would be juvenile habitat and is the wrong artifact to create during a readiness review.

This program is the plausible frame for a **juvenile estuarine** question. It is not a substitute for the adult reef visual census. Non-detections, goliath row counts, and rights are UNKNOWN. Nursery geometry stays withheld.

### Great Goliath Grouper Count

Florida Sea Grant, with FWC and county partners, has run a June diver count on designated artificial reefs since 2010. The public form records bottom time, replicates, depth, visibility, and counts. The program text places the dives on artificial reefs and in a spawning-season context.

Native site names and coordinates are out of scope. The form shows that some effort fields exist. It does not show that a random non-detection frame exists. Suitability for a public map is **not suitable**. A coarsened index would still need a sensitivity approval that this pass does not grant.

### Tagging and Brazil

The public OTN/FWC tagging abstract describes 50 adults tagged in 2010–2013 and mentions spawning sites. This inventory records the dataset’s existence and license. It does not record places.

Projeto Meros do Brasil has worked since 2002. The peer-reviewed participative survey (Giglio et al., doi:10.1590/1982-0224-20130166) states that sampling effort could not be obtained. Telemetry and aggregation monitoring described on the project site are not candidate layers.

### eDNA, BRUVS, and other gears

No rights-cleared eDNA or BRUV table for this species was identified in this pass. Those gears remain categories, not datasets. eDNA would need an explicit false-positive and false-negative statement before it could enter a detection model.

---

## Environmental and habitat covariates

Covariates are conditions at a sample. They are not goliath observations.

| Class | What was found | Readiness |
|---|---|---|
| Bathymetry, slope, roughness | GEBCO is catalogued in the globe and left unwired. Rights in this repo are not approved. | Not suitable until approved, then only aggregated to the sample unit |
| Survey depth | RVC publishes average depth of the secondary unit | Usable only inside an approved RVC extract |
| Reef / hard-bottom / mangrove | Florida habitat maps exist as a class. No layer was chosen or licensed | Not suitable yet |
| Temperature, salinity, oxygen, currents, chlorophyll | Copernicus-class products exist. None are ingested | Not suitable yet. Must not be drawn as animals |
| Seasonality | Must come from the survey date, not from a climatology painted as presence | Unknown until dates are checked |
| Wave exposure | Not selected | Unknown |
| AIS | Rejected | Not a fish layer and not fishing guidance |

Missing covariate values, if a later extract has them, have to be documented. A filled grid is not a sighting.

---

## Rights and sensitivity

| Item | State |
|---|---|
| Any new training approval | None. Accession 0208321 is named in `RVC_RIGHTS_RECORD.md` and remains `CONDITIONAL_REVIEW_REQUIRED` |
| Any new display approval | None beyond the existing coarsened OBIS past-report rule |
| Attribution for a future RVC extract | Not written |
| CC BY-NC constraints inside OBIS | Present, unresolved for a training extract |
| Tagging resource CC BY 4.0 | Allows attribution-based reuse of that metadata resource; does not allow drawing tracks or spawning sites |
| Spawning, wreck, and nursery geometry | Still blocked |
| White shark withhold | Unchanged; this assessment does not touch it |

---

## What this assessment refuses to do

- Treat SST, chlorophyll, or habitat class as a goliath sighting.
- Treat “no public record” as absence.
- Turn 332,628 compiled rows into abundance or current location.
- Interpolate below the sample unit or below about 1 degree on the existing past-report layer.
- Name aggregation, spawning, wreck, or nursery sites.
- Use AIS to find fishing or fish.
- Offer harvest, fishing, or diving guidance.
- Call this document a forecast or a current-location product.
- Change `NOT_PUBLISHED`.
