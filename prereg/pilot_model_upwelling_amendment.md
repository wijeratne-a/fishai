# Pilot model amendment: upwelling removed (path B)

**Scope:** `configs/models/cufes_sardine.yaml` and `configs/models/cufes_anchovy.yaml` (production pilot configs).

## Finding

The CUFES evidence table has `upwelling` null on all 14,592 rows. No single, consistent, publicly licensed wind product covers both the CUFES training years and daily nowcasts. This is the `no_consistent_wind_product` case already described in `prereg/harmonization_wcofs_glorys.md`.

## Amendment

- `upwelling` is removed from `covariates.dynamic` and `covariates.upstream_fields` for both the sardine and anchovy pilot models.
- `s(upwelling_z, k = 3)` is removed from `model.formula_shared` for both pilot models. The formula no longer depends on any `upwelling_z` column, so loading and fitting work with an all-null or planned-gap `upwelling` column in the covariate table.
- `upwelling` is never imputed, interpolated, or filled from a proxy.
- No events are excluded because of the missing `upwelling`.

## Reintroduction

Reintroducing `upwelling` needs both:

1. a later prereg amendment that names the covariate, its lag structure, and its formula term; and
2. a publicly licensed wind (or upwelling) product that is consistent across the training years and the nowcast period.

Until both exist, the pilot production configs must not list `upwelling` as a covariate or reference `upwelling_z` in a formula.

## Test configs

`configs/models/*_synthetic.yaml` are test scaffolding. They keep `upwelling` so the generic planned-gap drop path stays covered. They are not pilot production configs.
