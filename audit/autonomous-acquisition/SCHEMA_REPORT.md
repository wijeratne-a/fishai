# Schema report — Florida Keys RVC extract

ERDDAP dataset `CRCP_Reef_Fish_Surveys_Florida`. Metadata file: `data/metadata/noaa-rvc-erddap-metadata.csv`.

The requested columns were present. Each file has a header and a units row. `validate_noaa_rvc.py` passed on 2026-09-24.

Event key adopted: `YEAR + PRIMARY_SAMPLE_UNIT + STATION_NR + time`.

Across 843, 648, and 622 events, that key had no collisions on date, depth, habitat, subregion, or stratum. Coordinates parsed inside a Florida Keys bounding box. Depth was present and nonnegative. `NUM` was numeric and never negative. Region was `FLA KEYS` on every data row. Year matched the requested year. Accession URL matched 0208321, 0282183, and 0306184 respectively.

Blank `SCIENTIFIC_NAME` cells exist (57,379 in 2018, 6,544 in 2022, 46,143 in 2024). Those rows were not used as the first-model taxon. Species codes, not common names, identify taxa.

`NUM` is a real-valued average, not a raw integer count. See `ZERO_SEMANTICS.md`.
