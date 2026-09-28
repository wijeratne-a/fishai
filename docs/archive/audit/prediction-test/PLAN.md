# Puerto Rico internal prediction test — plan

**INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.**

## Goal

Repeat a survey-only detection feasibility check for two Puerto Rico Reef Visual Census species only: *Stegastes partitus* (`STE PART`) and *Sparisoma aurofrenatum* (`SPA AURO`). Compare a constant training-prevalence baseline to one L2-regularized logistic model. Record provenance. Keep results off the globe.

## Data

- Source: `data/raw/biological/noaa-ncrmp/CRCP_Reef_Fish_Surveys_Puerto_Rico/{2016,2019,2021,2023}.csv.gz` (read only; do not rewrite).
- Train years: 2016, 2019, 2021. Holdout: 2023 scored once. No tuning on 2023. No other species refit.
- Event key: `YEAR + PRIMARY_SAMPLE_UNIT + STATION_NR + time`.
- Detection: any row for the species code with `NUM > 0`. Non-detection is not ecological absence. Species must appear on that year’s species list.
- Predictors only: depth (`SAMPLE_DEPTH`), underwater visibility, year, habitat code. No SST join. No OBIS.

## Method

1. Build event-level labels for the two codes.
2. Spatial leave-one-subregion-out on training years only.
3. Fit prevalence baseline and L2 logistic once on all training events; score 2023 once.
4. Write results and a run manifest under `audit/prediction-test/` (no latitude/longitude). Publication status: `NOT_PUBLISHED`.

## Out of scope

Globe/prototype, `model-cards.json`, `PUBLICATION_DECISION.md`, multi-species `MODEL_RESULTS.csv`, environmental joins, nowcasts.
