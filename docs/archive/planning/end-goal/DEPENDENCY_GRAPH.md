# Dependency graph

```mermaid
flowchart TD
  A[GLOBAL_DATA_ACQUISITION] --> B[Structured surveys on disk + manifests]
  B --> C{Phase ended by user?}
  C -->|no| B
  C -->|yes| D[Historical env match in protected storage]
  D --> E[jplMURSST41 as-of join to PR dives]
  E --> F[Optional re-score PR holdout species only]
  F --> G{Beats survey-only baseline?}
  G -->|no| H[MORE_ENVIRONMENTAL_COVERAGE or stop]
  G -->|yes| I[Still NOT a nowcast / NOT PUBLISHED]
  I --> J[Current-field as-of rules]
  J --> K[Verified forecast ID required]
  K --> L[Forecast path still gated]
  B -.-> X[Do not publish globe layer]
  F -.-> X
  I -.-> X
  M[WCOFS not acquired] -.-> K
  N[RTOFS search HTTP 404] -.-> K
  O[Copernicus account required] -.-> K
  P[Bottom temp O2 chl currents substrate MISSING] -.-> H
  Q[Pacific positive-only] -.-> R[No constructed zeros]
  S[PR 2023 holdout baselines passed] -.-> F
  S -.-> T[Not nowcasts; no refit in current phase]
```

## Edge notes

| From | To | Rule |
|---|---|---|
| Acquisition | Historical env match | Scientific next step; **blocked for execution** while phase is acquisition |
| Historical SST join | Refit/re-score | Only after phase allows; only two PR species first; off-globe |
| Any internal pass | Globe publish | **No edge.** Publication is a separate gate |
| Missing predictors | Demersal/pelagic hypotheses | Remain `untested-in-this-repo` until IDs verified |
| Bias audit | Applied correction | **No edge** this phase |
