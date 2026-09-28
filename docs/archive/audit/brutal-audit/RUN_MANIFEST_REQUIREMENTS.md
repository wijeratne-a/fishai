# Run manifest requirements

A result may not be cited unless the manifest records:

- git commit (clean tree or explicit dirty hash list)
- input file checksums (events, SST cache, taxonomy)
- TRAIN_YEARS, HOLDOUT_YEAR, spatial block field
- estimator (steps, L2, seed actually used)
- feature list and habitat encoding rule
- SST offsets allowed (must be <= 0)
- missing-data policy (must be refuse, not impute 15)
- metrics code identity
- `holdout_inspected: true|false`
- `publication_status: UNTRUSTED_RESULT | INSPECTED_HOLDOUT | INTERNAL_ONLY`

`require_run_manifest` in the experiment schema is necessary and currently **not** what produced MODEL_RESULTS.csv.
