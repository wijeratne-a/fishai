# Spatial leakage tests

Block field is `SUB_REGION_NAME` / `SUB_REGION_NR`. Adjacent primary sample units in different named subregions can sit in train and test in the same year. The same named subregion can be huge.

Puerto Rico uses **3** spatial folds. Flower Garden Banks uses **2** folds on 164 train events. That is not a spatial block design that can carry a generalization claim.

Repeated sites: `PRIMARY_SAMPLE_UNIT` + `STATION_NR` can recur across years. Temporal holdout therefore tests **the same reef system later**, not a new place. That is a legitimate transfer question only if labeled as such. Reports call it an “untouched year,” which hides site reuse.

No distance-based de-duplication exists.

**Metrics invalid as spatial generalization:** FGB scores; PR spatial Brier used as if blocks were independent habitats.
