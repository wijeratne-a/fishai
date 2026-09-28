# RVC extract rights record

**Date read:** 2026-09-23  
**Milestone:** Prediction MVP — Florida Keys Goliath Grouper Detection Nowcast  
**Step:** 1 of the sequence in `FIRST_MODEL_FEASIBILITY.md`  
**Step status:** **NOT COMPLETE**  
**Rights class:** `CONDITIONAL_REVIEW_REQUIRED`  
**Training permission:** not granted  
**Display permission:** not granted  
**File hash:** none. No file was acquired.  
**Ingest:** none  
**Acquisition:** did not occur  
**Schema verification:** not started. `RVC_SCHEMA_VERIFICATION.md` was not written.  
**Exit gate:** `BLOCKED`  
**Card:** `NOT_PUBLISHED`

This note is a reading of public landing pages. It is not a license grant, not legal advice, and not an `APPROVED_*` decision. The observatory register requires a human legal review before ingest, training, or a public layer.

---

## Named candidate

| Field | Value |
|---|---|
| Dataset | National Coral Reef Monitoring Program: Assessment of fish communities in the Florida Reef Tract from 2018-06-05 to 2018-12-17 |
| Accession | NCEI **0208321**, version **1.1** |
| Identifier | `gov.noaa.nodc:0208321` |
| Landing page | https://www.ncei.noaa.gov/archive/accession/0208321 |
| Published | 2020-01-14 |
| Time | 2018-06-05 to 2018-12-17 |
| Regions on the page | Dry Tortugas; Florida Keys from Key West north to Miami; Miami north to Martin County |
| Bounding box on the page | West −83.1, East −80, South 24.4, North 27.2 |
| Method on the page | Two-stage stratified random survey. Bohnsack/Bannerot stationary point count. 7.5 m radius cylinder. |
| Formats listed | CSV, ODS, PDF, Shapefile |
| Parent collection | `gov.noaa.nodc:NCRMP-Fish-Florida`, DOI https://doi.org/10.7289/v52n50ks |
| Other accessions in that collection | 0156445, 0169400, 0208321, 0253454, 0282183, 0306184 |
| Collection time span on the parent page | 2014-05-01 to present, revised 2025-07-23 |

Accession 0208321 is one year. A time-forward test needs more than one year. A rights decision for the milestone should cover the parent collection, not this granule alone. This granule is the file whose landing page was read in full.

The multi-year SEFSC portal (https://grunt.sefsc.noaa.gov/rvc_analysis20/, InPort item 8585) is a second distribution. It is not the same object as accession 0208321.

---

## What the pages say

### Accession 0208321

Read 2026-09-23 from the NCEI landing page.

- Access level: public.
- Use constraint: the citation below.
- Access constraint: NOAA and NCEI give no warranty. The user is responsible for results of any application other than the intended purpose.
- The accession page does **not** say CC0, public domain, or a training grant.
- Point of contact named on the page: Jeremiah Blondeau, NOAA SEFSC Miami Laboratory.

**Citation to store with any future extract:**

> NOAA Southeast Fisheries Science Center; NOAA National Centers for Coastal Ocean Science (2020). National Coral Reef Monitoring Program: Assessment of fish communities in the Florida Reef Tract from 2018-06-05 to 2018-12-17 (NCEI Accession 0208321). https://www.ncei.noaa.gov/archive/accession/0208321. In NOAA Southeast Fisheries Science Center; NOAA National Centers for Coastal Ocean Science (2018). National Coral Reef Monitoring Program: Assessment of coral reef fish communities in the Florida Reef Tract. [indicate subset used]. NOAA National Centers for Environmental Information. Dataset. https://doi.org/10.7289/v52n50ks. Accessed [date].

### Parent collection

Read 2026-09-23 from https://accession.nodc.noaa.gov/NCRMP-Fish-Florida.

Use constraints on that page include both the citation and this sentence:

> Some of the data in this dataset has been dedicated to the public domain under the Creative Commons CC0 1.0 Universal (CC0 1.0) Public Domain Dedication.

The page also lists SPDX `CC0-1.0`. It does not say which accessions are inside that “some.” Accession 0208321’s own page does not repeat the CC0 sentence. CC0 is therefore not recorded for 0208321.

Partners named on the collection include University of Miami, Nova Southeastern University, Florida Fish and Wildlife Conservation Commission, Florida Department of Environmental Protection, National Park Service, Florida Keys National Marine Sanctuary, and Broward and Miami-Dade counties. A NOAA landing page does not by itself put partner-contributed rows in the public domain.

### InPort 8585, the SEFSC portal

Read 2026-09-23 from https://www.fisheries.noaa.gov/inport/item/8585.

| Field | Text on the page |
|---|---|
| Data access policy | To qualified Researchers |
| Data access constraints | None |
| Data use constraints | Please cite |
| Status | In Work |

Those three access lines do not form one clear license. “Qualified researchers” and “no access constraints” are different rules. This portal stays `CONDITIONAL_REVIEW_REQUIRED`.

The same InPort record describes the analysis-ready product as a flat file in which replicate samples are averaged at the second-stage unit and zeros are added. That is a provider process statement. It is not a count of `EPIITAJ` rows. Step 2 still has to open an approved file and count zeros.

### USGS republication

A USGS OBIS/GBIF resource for Florida Keys Reef Visual Census 2018 (GBIF UUID `60b463ce-d58e-4982-b772-ae8fc9a6f1ef`) carries a CC0 1.0 statement by USGS. That is a standardized copy, not accession 0208321, and not the SEFSC analysis-ready file. Its CC0 statement is not applied backward to the NOAA files.

---

## Protocol

| Item | Source |
|---|---|
| Design paper | Smith, S. G., Ault, J. S., Bohnsack, J. A., Harper, D. E., Luo, J., and McClellan, D. B. (2011). Fisheries Research 109(1): 25–41. https://doi.org/10.1016/j.fishres.2011.01.012 |
| Field method | Bohnsack/Bannerot stationary point count, 7.5 m radius cylinder, as stated on the NCEI accession and collection pages |
| Design | Two-stage stratified random survey |
| Species code | Portal rule: first three letters of the genus and first four of the species, so `EPIITAJ` for *Epinephelus itajara* |
| Zeros | Claimed for the InPort analysis-ready file. Not verified in a downloaded table |

---

## Why this is not clearance

| Required record | State |
|---|---|
| Named extract | Accession 0208321 v1.1 is named. The multi-year collection is the set a nowcast would actually need. |
| File hash | Absent. Coordinates were not downloaded into this repo. |
| License | Citation is required. CC0 is not established for this accession. |
| Training permission | Not granted |
| Display permission | Not granted. Native sample coordinates stay out of the repo until a sensitive-site review. |
| Attribution | Citation text is recorded above. Subset phrase is still blank because no subset was taken. |
| `APPROVED_*` | Not assigned |

A human reviewer has to decide, in writing, whether accession 0208321 and the rest of DOI `10.7289/v52n50ks` may be used for training and for a coarsened detection layer. Until that writing exists, step 1 stays open and no baseline is fit.

---

## Acquisition decision, 2026-09-23

**Decision:** `CONDITIONAL_REVIEW_REQUIRED`

No written approval was received for internal acquisition, storage, preprocessing, model training, derived-model development, aggregate display, publication of derived results, redistribution, coordinate handling, sensitive-species handling, derivative works, or commercial use. Public access, a citation request, “no access constraints,” and the parent collection’s “some of the data” CC0 sentence were not treated as that approval.

Download of accession 0208321 did not occur. No byte size, SHA-256, retrieval timestamp, access-control path, approver, or approval date exists. Coordinates from this accession are not in the repository, the browser, fixtures, or this note.

`RVC_SCHEMA_VERIFICATION.md` was not created. Zeros, `EPIITAJ`, effort, and the sample frame are unverified.

The other parent-collection accessions were screened from landing pages only and recorded in `RVC_MULTIYEAR_READINESS.csv`. None was downloaded. None is rights-cleared for this project. Accession 0306184’s own page states a CC0 dedication; that statement is not a FishAI approval, and that accession’s page describes a single-stage design. Accession 0169400’s page says the raw package was originally meant to be distributed by request and that the submitter still recommends contact before use of the raw data.

Sensitive-coordinate rule for any later extract: raw coordinates stay outside this repository, out of the browser, out of fixtures, and out of logs, screenshots, summaries, and diffs. No aggregate tile is authorized.

**Blocker:** written rights approval for accession 0208321, plus a frozen file hash and a verified table, are absent. Exit gate: `BLOCKED`.
