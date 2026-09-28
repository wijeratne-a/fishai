# Zero semantics — Florida Keys Reef Visual Census

**Source:** NCEI ERDDAP `CRCP_Reef_Fish_Surveys_Florida`, `REGION="FLA KEYS"`.  
**Status used for modeling:** species-level non-detection is constructible. A single `NUM == 0` row is not, by itself, the species result.

`NUM` is a non-negative real number, including values such as 0.87 and 2.75. It is not an integer fish count. It behaves like an average across the divers or length records in the published table.

Within each year, every survey event lists the same set of species codes:

| Year | Events | Species codes in every event | Rows with NUM = 0 | Rows with NUM > 0 |
|---|---:|---:|---:|---:|
| 2018 | 843 | 475 | 390,731 | 85,646 |
| 2022 | 648 | 250 | 199,874 | 21,968 |
| 2024 | 622 | 481 | 291,728 | 64,526 |

The three lists are not the same. Their intersection has 249 codes. A code missing from the 2022 list was not recorded as a 2022 non-detection.

The same species code often occupies more than one row in an event, with different `length_fish` values. In 2018, 14,279 species-events had both a zero and a positive `NUM` on different length values. A zero row in that case is a length bin, not a species miss.

**Species-level rule used here:** an event is a detection if any row for that species code has `NUM > 0`. It is a survey non-detection if the code is in that year’s universe and every row for the code has `NUM == 0`. Do not sum `NUM` across length bins.

2022 also has 2,577 species-events where a zero and a positive share the same length value. Length-specific abundance is unresolved. The species-level any-positive rule does not treat those zeros as non-detections.

A survey non-detection means the published table recorded no positive average for that code on that dive. It does not mean the species was absent from the surrounding reef.

| Year | Status |
|---|---|
| 2018 | `CONSTRUCTIBLE_SURVEY_NONDETECTION` |
| 2022 | `CONSTRUCTIBLE_SURVEY_NONDETECTION` |
| 2024 | `CONSTRUCTIBLE_SURVEY_NONDETECTION` |
