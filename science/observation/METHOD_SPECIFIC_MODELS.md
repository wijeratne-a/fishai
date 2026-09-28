# Method-specific observation models

**Scope:** Observation-process guidance for research. No model fitting here.  
**Schema:** `OBSERVATION_PROCESS_SCHEMA.json`  
**Variables:** `DETECTABILITY_VARIABLES.csv`

## Global rules

1. **A missing row is not a non-detection.** Non-detections exist only when a completed protocol and an explicit zero-construction policy allow them (for Atlantic RVC: taxon on that year’s species list and effort complete).
2. **Do not combine sources with only a source dummy when processes differ.** If detectability, effort currency, spatial support, or zero semantics differ, keep separate likelihoods or an explicitly shared process allow-list—not a single intercept shift by source name.
3. Each modeling table must declare a `process_id` that validates against `OBSERVATION_PROCESS_SCHEMA.json`.

## RVC / stationary reef visual census

**Detectability includes visibility, depth, and protocol.**

| Component | Role |
|---|---|
| Visibility | Detection covariate: harder to see fish when visibility is poor |
| Depth | Detection / availability: changes what is observable and which habitat is sampled |
| Protocol | Process identity: plot rules, timing, and observer procedure define the likelihood |

Additional RVC constraints:

- `NUM` (Atlantic extracts) is a published real-valued average, not necessarily an integer fish count.
- Length-bin rows: detection is any positive bin for the taxon at the event, under project zero rules.
- Species list size changes by year: a code is a non-detection only in years that include it.
- Pacific positive-only extracts: do not invent zeros from missing taxa.

Occupancy-style RVC models need stated replicates. A single station visit is not automatically a multi-occasion detection history.

## Presence compilers (e.g. OBIS)

- Evidence role is presence-only (or historical occurrence), not survey non-detection.
- No RVC detection likelihood. Compiler bias layers are not visibility/depth/protocol detectability.
- Must not be flattened into the same binary detection column as RVC events (see `research/integration/`).

## Telemetry / tracks

- Observation process is track fixes with location error, not survey detection.
- Route model family selection to `research/methods/MOVEMENT_MODEL_MATRIX.csv`.

## Egg / larval surveys

- Separate process from adult reef visual census.
- Particle tracking, if used, remains transport—not adult behavior (`MODEL_SELECTION_RULES.md`).

## Pooling checklist

Before any multi-source fit:

1. Same `method_family` and compatible `nondetection_policy`?
2. Same effort currency and spatial/temporal support?
3. Detectability variables defined for each process (for RVC: visibility, depth, protocol at minimum)?
4. Explicit `may_pool_with_process_ids` on both sides?

If any answer is no, keep separate observation models.
