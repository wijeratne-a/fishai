# Bias correction options

**Scope:** Eligible bias-handling patterns for multi-source research designs. No fitted corrections or performance numbers here.

## Principles

- Correct **within** a declared observation process first (effort, list membership, visibility, depth, protocol for RVC).
- Presence-only compilers need **sampling-bias** treatment, not survey detectability covariates copied from RVC.
- **OBIS presence must not enter the RVC detection likelihood**; bias correction does not license stacking OBIS into RVC `y`.
- **Do not flatten evidence into one binary column** and then “fix” the mix with a source factor.

## Options by problem

| Problem | Eligible option | Not eligible |
|---|---|---|
| RVC detection varies with conditions | Include visibility, depth, and protocol (and other recorded detection covariates) in the RVC observation model | Ignore protocol differences; pool regions with a source dummy only |
| Taxon missing from a year’s RVC list | Exclude from that year’s non-detection set | Mint zeros for unlisted taxa |
| Pacific positive-only extracts | Treat as presence-only or detection-given-recorded-count; no constructed zeros | Invent absences from missing rows |
| OBIS / compiler spatial reporting intensity | Separate presence-only model with explicit bias or effort proxy layers; optional shared latent occurrence **without** shared detection pmf | Append OBIS rows as `y=1` into RVC table; treat unqueried cells as `y=0` |
| Cross-protocol surveys (visual vs gear) | Separate detection models; hierarchical sharing of occurrence parameters only if justified | Single binary column + source intercept |
| Preferential sampling of reefs or ports | Preferential-sampling or intensity-weighting designs stated up front | Post-hoc deletion of inconvenient regions without a stated frame |
| Climate scenario uncertainty | Ensemble across climate models / pathways / structures | Single envelope map as unbiased truth |

## Integration with other WS artifacts

- Process declaration: `science/observation/OBSERVATION_PROCESS_SCHEMA.json`
- Detectability variables: `science/observation/DETECTABILITY_VARIABLES.csv`
- Compatibility cells: `EVIDENCE_COMPATIBILITY_MATRIX.csv`
- Model family gates: `research/methods/MODEL_SELECTION_RULES.md`

## Explicit refusals

- Source dummy as the only accommodation when visibility, depth, protocol, zero rules, or effort currency differ.
- Flattening OBIS + RVC (+ telemetry) into one presence/absence column.
- Calling particle-track density a bias-corrected fish occurrence field.
