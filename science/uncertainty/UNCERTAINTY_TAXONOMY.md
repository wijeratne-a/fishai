# Uncertainty taxonomy

**Status:** Contract for internal model outputs. Not a published nowcast.

## Principle

Uncertainty is **multi-component**. Do not collapse epistemic, aleatoric, support, and observation uncertainty into a single confidence score or a single color band.

## Components (keep separate)

| Component | What it answers | Typical sources |
|---|---|---|
| `aleatoric` | Irreducible outcome noise given the same covariates | Detection process, effort variation, Bernoulli residual |
| `epistemic_parameter` | Uncertainty in fitted parameters | Finite sample, model misspecification under the same family |
| `epistemic_structural` | Uncertainty from model-class choice | Alternative likelihoods, omitted covariates |
| `spatial_support` | Whether the query is inside spatial training support | Domain mask `SPATIAL_EXTRAPOLATION` / distance |
| `environmental_support` | Whether covariates are inside environmental ranges | Domain mask `ENVIRONMENTAL_EXTRAPOLATION` |
| `temporal_support` | Whether time features are inside training support | Domain mask `TEMPORAL_EXTRAPOLATION` |
| `observation_process` | Label / effort frame uncertainty | Incomplete zeros, protocol change, taxon-in-frame ambiguity |
| `data_coverage` | How much evidence exists nearby in feature space | Neighbor count, support radius occupancy |

## Forbidden collapses

- Multiplying or averaging components into one `confidence` without retaining the parts
- Mapping all uncertainty to ROC AUC, Brier, or a single interval width
- Treating support labels as calibrated probabilities
- Replacing missing components with `0` silently — use `null` and state `UNKNOWN`

## Product language

- Internal outputs may list components with units or qualitative levels per field.
- Public surfaces must not invent a numeric “% sure” from an unmerged bag of components.
- `UNSUPPORTED` or unknown observation-process status blocks publication claims.

See `UNCERTAINTY_OUTPUT_SCHEMA.json` and `PROPAGATION_RULES.md`.
