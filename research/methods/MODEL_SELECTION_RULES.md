# Model selection rules

**Scope:** Research method selection only. No model fitting in this workstream.  
**Matrices:** `MOVEMENT_MODEL_MATRIX.csv`, `DISTRIBUTION_MODEL_MATRIX.csv`, `CLIMATE_MODEL_MATRIX.csv`.

## Three separate questions

| Class | Question | Primary matrix |
|---|---|---|
| (1) Population occurrence | Where and when does a population tend to be detected or occur under a stated survey or occurrence process? | `DISTRIBUTION_MODEL_MATRIX.csv` |
| (2) Individual tracks | How does a tagged or otherwise identified individual move through space and time? | `MOVEMENT_MODEL_MATRIX.csv` |
| (3) Long-term redistribution | How might suitable habitat or range shift under multi-year to multi-decadal climate scenarios? | `CLIMATE_MODEL_MATRIX.csv` |

Do not answer one class with a model family reserved for another.

## Hard rules

1. **Ordinary occurrence points must not drive a state-space or HMM track model.** Unordered presence pins, compiler occurrences, and survey detections without individual identity and ordered time are not tracks.
2. **Particle tracks are not fish behavior.** Lagrangian or particle products describe transport under ocean velocity and release assumptions. They may support larval dispersal or connectivity scenarios; they do not estimate adult or juvenile behavioral states.
3. **Survey occurrence families** (GLM, GAM, hurdle / zero-inflated, occupancy, spatial GLMM) apply only to protocol-matched survey events with valid detections and, where claimed, constructible non-detections. See `science/observation/` for observation-process constraints.
4. **HMM, state-space, and step-selection** apply only to ordered tracks of the same individual (or an explicitly defined track unit). They are not population occurrence models.
5. **Particle tracking** is for larval or passive/semi-passive transport questions, not for fitting behavior from occurrence tables.
6. **Climate envelope and mechanistic climate models** are only for long-term redistribution scenarios. Any climate-class claim must carry **ensemble uncertainty** (climate models, pathways, and/or structural alternatives). They are not short-horizon detection nowcasts.
7. **Do not invent performance numbers.** Matrices and this file list eligibility and forbidden uses only. No Brier, AUC, or skill figures are asserted here.

## Decision path

1. Name the scientific question class: occurrence, tracks, or long-term redistribution.
2. Confirm the data shape matches the matrix row (survey frame, ordered individual track, or climate scenario inputs).
3. Reject any family whose `forbidden_uses` column matches the planned use.
4. If observation processes differ across sources, do not pool with a source dummy alone; see WS47 and WS48.

## Cross-links

- Observation process and detectability: `science/observation/`
- Multi-source integration constraints: `research/integration/`
