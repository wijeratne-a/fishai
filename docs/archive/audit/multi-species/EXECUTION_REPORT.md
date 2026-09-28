# Multi-species baseline execution

```
ATLANTIC REGION/YEAR FRAMES VALIDATED: 17 files. All have one species list per year, NUM=0 rows, and no event-key collisions.
INCOMPATIBLE YEARS EXCLUDED: Florida 2020, Puerto Rico 2014, USVI 2013 and 2015, Flower Garden Banks 2013 and 2015 are not in these ERDDAP year lists and were not downloaded.
SPECIES RANKED: 6 Florida, 4 Puerto Rico, 4 USVI, 2 Flower Garden Banks.
MODELS FIT: 16
MODELS PASSING SPATIAL VALIDATION: 2 Puerto Rico species, plus Florida and Flower Garden Banks rows that later failed the holdout are not counted as accepted.
MODELS PASSING TEMPORAL VALIDATION: 2
MODELS BEATING PREVALENCE BASELINE: Puerto Rico Stegastes partitus and Sparisoma aurofrenatum, on both spatial blocks and the 2023 holdout.
ENVIRONMENTAL MODELS TESTED: 0
NOWCAST-RESEARCH-READY SPECIES: 0
PACIFIC EVENT FRAMES RECOVERED: replicate ids exist; zero rows do not. Status POSITIVE_ONLY.
OBIS RECORDS REQUESTED: 672
OBIS RECORDS SAVED: 672
NEW 2025 DATA FOUND: no
NEXT BOTTLENECK: historical sea temperature is not matched to survey dates and places, so the two accepted baselines cannot move to a nowcast test.
FINAL DECISION: MORE_ENVIRONMENTAL_COVERAGE_REQUIRED
```

Training years were every compatible year before the holdout. The holdout was scored once. OBIS records were not used as training rows. The globe was not changed.

USVI logistic scores were non-numeric, so those four models are rejected rather than interpreted. Flower Garden Banks has 38 holdout events and neither species beat the simple baseline on both tests.

## Commands

```text
python3 scripts/validation/validate_atlantic_frames.py
python3 scripts/modeling/fit_regional_detection_models.py
python3 scripts/acquisition/watch_ncrmp_releases.py
```

Missing years downloaded first: Florida Keys 2014 and 2016; Puerto Rico 2019 and 2016; USVI 2019 and 2017; Flower Garden Banks 2023 and 2018.

## Next action

Match a historical analysed sea-surface temperature to the Puerto Rico survey dates inside protected storage, then repeat the same 2023 holdout for *Stegastes partitus* and *Sparisoma aurofrenatum*. Keep the result off the globe.
