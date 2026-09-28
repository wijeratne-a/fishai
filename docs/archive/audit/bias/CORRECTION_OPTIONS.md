# Correction options

**Status:** Options only. **Do not apply corrections** in this phase. No coordinates in this audit.

## Eligible options (document; do not run)

| Problem | Option | Requires before use |
|---|---|---|
| RVC daylight / diel detectability | Include time-of-day or sun elevation in the **observation** model for visual surveys | Event timestamps; guild-scoped behavior hypothesis |
| RVC depth limit | Condition on surveyed depth; mask predictions outside depth support | Depth field; support policy |
| Habitat stratification | Model habitat as design/effort structure; avoid interpreting stratum frequency as abundance | `HABITAT_CD`; design notes |
| Year-varying species lists | Non-detection only in years the code appears on the list | Per-year list membership table |
| Pacific positive-only | Treat as presence-only or detection-given-recorded-count; **never** mint zeros | Explicit presence-only likelihood |
| OBIS presence-only + coastal bias | Separate presence-only model with sampling-intensity treatment; optional shared latent occurrence **without** shared RVC detection pmf | Declared OBIS process; no coordinate dump into public artifacts |
| Preferential coastal reporting | Preferential-sampling or intensity weights stated up front | Effort or bias proxy layers verified in-repo |
| Unjoined SST | Historical as-of join before any SST covariate claim | `jplMURSST41` matched to dive time/location in protected storage |

## Explicitly not eligible here

- Applying any of the above corrections now (phase is acquisition; no refits).
- Flattening OBIS into RVC presence/absence.
- Using GEBCO or bathymetry as a reef-presence correction.
- Source dummy alone as a substitute for visibility, depth, protocol, and list rules.
- Publishing bias-corrected globe layers.

## Pointers

Related integration notes live under `research/integration/BIAS_CORRECTION_OPTIONS.md`. This file is the acquisition-phase bias audit companion and does not authorize those methods.
