# Integrated model options

**Scope:** How multiple evidence streams may be combined in research designs. No model fitting here.  
**Companion files:** `EVIDENCE_COMPATIBILITY_MATRIX.csv`, `BIAS_CORRECTION_OPTIONS.md`.

## Non-negotiable constraints

1. **OBIS presence must not enter the RVC detection likelihood.** Compiler presence rows are not survey trials. They do not contribute detections or zeros inside an RVC Bernoulli / binomial / occupancy detection model.
2. **Do not flatten evidence into one binary column.** Keep distinct evidence roles (structured survey detection, survey non-detection, presence-only, track fix, environmental condition). A shared `y ∈ {0,1}` table that mixes OBIS pins with RVC events is forbidden.
3. Observation processes that differ need separate likelihood terms or an explicitly justified shared process—not a source dummy alone (`science/observation/METHOD_SPECIFIC_MODELS.md`).

## Option classes (eligibility only)

| Option | What it may combine | What it must keep separate |
|---|---|---|
| A. Single-process survey model | One RVC-compatible process with constructible non-detections | OBIS; other gears; tracks; climate scenarios |
| B. Shared latent occurrence, separate observation models | Survey processes with declared pooling allow-list; optional presence-only as a **separate** intensity or bias model | Single stacked binary response; OBIS rows inside RVC detection pmf |
| C. Presence-only bias model alongside survey model | OBIS or other compilers as relative intensity with explicit bias | Treating compiler gaps as survey zeros |
| D. Track submodel linked by shared covariates only | Telemetry likelihood for individuals; survey likelihood for population | Feeding occurrence pins into HMM / state-space |
| E. Climate scenario layer | Envelope or mechanistic ensembles for long-term redistribution | Short-horizon RVC detection nowcast |

Options are design templates. No performance ranking or scores are claimed.

## Recommended default for FishAI survey questions

Use **Option A** for Atlantic RVC detection probability under a named protocol. If compilers are used at all, use **Option C** as a **separate** evidence stream that never writes into the RVC detection likelihood.

## Validation before any joint fit

- Each stream has a `process_id` and evidence role.
- Compatibility cell in `EVIDENCE_COMPATIBILITY_MATRIX.csv` is `COMPATIBLE` or `SEPARATE_LIKELIHOOD_ONLY`.
- Bias plan named in `BIAS_CORRECTION_OPTIONS.md` if presence-only or cross-protocol pooling is attempted.
- Method family matches `research/methods/MODEL_SELECTION_RULES.md` question class.
