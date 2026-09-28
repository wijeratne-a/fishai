# Protocol compatibility

Every downloaded Atlantic year uses the ERDDAP columns `PRIMARY_SAMPLE_UNIT`, `STATION_NR`, `time`, `NUM`, and `SPECIES_CD`. Within a year, every event carries the same species list and includes `NUM = 0` rows. The event key had no metadata collisions.

The species list is not the same size every year. Examples: Florida Keys 249 codes in 2014 and 481 in 2024; Puerto Rico 216 in 2016 and 481 in 2023. A species is a non-detection only in a year whose list contains its code. Years are marked `COMPATIBLE_WITH_ADJUSTMENT`, not identical protocols.

`NUM` is a real-valued average. Detection is any positive `NUM` across length bins. That rule is the same in every Atlantic file that was checked.

These discovery targets are not in the ERDDAP year lists, so they were not downloaded: Florida Keys 2020, Puerto Rico 2014, USVI 2013 and 2015, Flower Garden Banks 2013 and 2015. Puerto Rico 2014 was not pooled, including because it is absent from this table. A belt-transect year cannot be assumed from a file that is not here.

The 2024 Florida accession narrative has described a single-stage design. The table still has the same event key and zero pattern. 2024 was used only as the untouched holdout, not as proof that the field method was unchanged.

Holdouts were 2024 for Florida and Flower Garden Banks, and 2023 for Puerto Rico and USVI. No model was tuned on those years.
