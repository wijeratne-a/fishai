# Real spatial-block CV staging (PR #5 + bot2 table)

**Not for publication.** Dry-run outputs are **EVIDENCE ONLY — NOT FOR DISPLAY**.

## Prerequisites

1. Bot2 training table at `data/processed/calcofi_cufes/cufes_training_covariates.parquet` (PR #28 / `cursor/real-training-table-evidence`, commit `5f188c2` or newer).
2. R packages via `Rscript renv/scripts/bootstrap.R` (or Docker `rocker/r-ver` + `renv::restore()`).
3. Barrier land RDS: `staging/cv-real-run/build_scb_pilot_land_sf.R` (shoreline hash `2f677a16…20996c`).

## Build training table (local only)

```bash
staging/cv-real-run/build_bot2_training_table.sh
```

Uses a read-only clone of `cursor/real-training-table-evidence` for bot2 Python code; writes under this repo’s `data/processed/`.

## Official CV dry-run command

```bash
staging/cv-real-run/run_official.sh
```

Equivalent:

```bash
Rscript scripts/models/cufes_real_spatial_cv_staging.R --species both \
  --out-dir staging/cv-real-run/dry-run
```

Memory fallback:

```bash
Rscript scripts/models/cufes_real_spatial_cv_staging.R --species both \
  --mesh-cutoff-km 12 --out-dir staging/cv-real-run/dry-run-coarse
```

Manifest: `staging/cv-real-run/dry-run/cufes_real_spatial_cv_staging_manifest.json`.

Configs (no `upwelling`; `log(bottom_depth_m)` via `bottom_depth_m`): `configs/staging/cufes_*_real_cv.yaml`.
