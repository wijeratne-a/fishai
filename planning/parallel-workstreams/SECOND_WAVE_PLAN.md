# FishAI second-wave parallel plan

**As of:** 2026-09-25  
**Phase:** `GLOBAL_DATA_ACQUISITION`  
**Project decision:** `CONTINUE_GLOBAL_DATA_ACQUISITION_AND_PARALLEL_HARDENING`  
**Registry:** `WORKSTREAMS.yaml` (not modified by this wave plan)

## Scope of this document

Classify proposed agents for a second parallel wave. Exclusive directories listed under `START_NOW` are reserved for those agents (treat as launched / ownership claimed). Do **not** relaunch `ALREADY_COVERED` work. Do **not** touch `data/raw`, manifests owned by acquisition, acquisition scripts, globe sources, or model score tables.

## Dependency snapshot (inspected)

| Path | Present | Notes |
|---|---|---|
| `labels/` | yes | Biological label schema, life-stage mapping, observation semantics |
| `features/` | yes | Variable catalog, guild/source matrices, leakage risks |
| `research/methods/` | yes | Distribution / movement / climate matrices + selection rules |
| `science/observation/` | yes | Observation-process schema, detectability, method models |
| `evaluation/` | yes | `evaluation/support/` exists; `evaluation/domain/` absent |
| `ui-functional/` | yes | Functional audit + scientific display requirements |
| `schemas/` | yes | Source/event/observation/effort/taxon/measurement/provenance + globe contracts |
| `security/` | yes | Sensitivity policy, rules, precommit scan, coordinate exposure test |
| Separate backup directory | **no** | Only `docs/BACKUP_AND_RECOVERY.md`; last restore `NOT_RUN` |

## Backup status

| Item | Value |
|---|---|
| Last restore | `NOT_RUN` |
| Separate backup directory documented | no |
| Claim status | **blocked / not verified** — do not report backup success |

## Classifications

### START_NOW (18)

Exclusive dirs already assigned this wave. Record ownership; do not duplicate their files from this planner.

| Agent / exclusive dir | Constraint |
|---|---|
| `science/measurements` | Measurement vocabulary / units contracts only |
| `science/time` | Temporal precision classes; no invented timestamps |
| `audit/contracts` | Cross-artifact contract inventory |
| `models/config` | Config skeletons only; no training |
| `audit/predictors` | Predictor inventory / eligibility audits |
| `research/hypotheses` | Hypothesis register; no fits |
| `planning/end-goal` | End-goal / phase-exit criteria |
| `audit/bias` | Bias gap quantification (extends WS12 themes) |
| `audit/repository-integrity` | Tracked-tree integrity checks |
| `audit/reproducibility` | Repro checklist / pin inventory |
| `audit/protocols` | Protocol audit notes beyond existing matrix |
| `audit/model-readiness` | **New CSVs only** (dir already has `MODEL_INPUT_REQUIREMENTS.csv`) |
| `audit/ui-scientific` | Scientific honesty of UI copy/labels |
| `audit/map-performance` | Performance/stall audit notes; do not change camera code by default |
| `tests/failure-recovery` | Failure-path tests |
| `tests/end-to-end-second-wave` | Second-wave e2e harness |
| `audit/storage` | Storage policy audit; must not claim backup without restore |
| `internal-tools/coverage-dashboard` | Internal coverage dashboard only |

### REDUCED_SCOPE (3)

| Agent | Allowed work | Hard stop |
|---|---|---|
| Protocol change detection | Add **year-pair classes** only | Do not rewrite `audit/multi-species/ATLANTIC_PROTOCOL_MATRIX.csv` wholesale (matrix already exists) |
| Spatial support | New code only under `evaluation/domain/` | Do not reimplement `evaluation/support/` (mask, policy, metrics already present) |
| UI interaction tests | Tests that assert interaction contracts | Must **not** edit `globe/` or prototype sources |

### WAIT_FOR_DEPENDENCY (1)

| Agent | Blocker |
|---|---|
| Backup verify / restore claim | Restore result is `NOT_RUN`; no separate backup directory is documented → status remains **blocked, not verified** until restore test passes under WS14 / `scripts/storage/` |

### ALREADY_COVERED (11) — do not relaunch

| Topic | Evidence |
|---|---|
| Observation labeling | `labels/` |
| Life-stage rules | `labels/LIFE_STAGE_*`, `science/life-stage/LIFE_STAGE_MODEL_RULES.md` |
| Model-question router | `science/MODEL_QUESTION_ROUTER.yaml` |
| Distribution / movement / climate method matrices | `research/methods/*_MODEL_MATRIX.csv` |
| Observation-process schema | `science/observation/OBSERVATION_PROCESS_SCHEMA.json` |
| RVC zero semantics | `audit/multi-species/ATLANTIC_ZERO_SEMANTICS.md` + CURRENT_STATUS |
| Atlantic protocol matrix | `audit/multi-species/ATLANTIC_PROTOCOL_MATRIX.csv` |
| File validation of Keys 2024 | CURRENT_STATUS (356,254 rows validated) |
| Sensitivity scan | `security/precommit_sensitive_scan.py` (WS13 complete for cycle) |
| Checksum verification | CURRENT_STATUS (25/25 match); `scripts/storage/verify_checksums.py` |
| Globe publish gates | `docs/GLOBE_DATA_CONTRACT.md`, globe schemas; no species `PUBLISHED` |

### OWNERSHIP_CONFLICT (0)

No second-wave proposal claims the same exclusive output directory as another **new** agent in this wave. Reduced-scope agents must not collide with `ALREADY_COVERED` artifacts beyond the allowed deltas above.

### NOT_APPROPRIATE_IN_ACQUISITION_PHASE (5)

| Proposal | Reason |
|---|---|
| Refitting Puerto Rico 2023 | Acquisition phase; no additional fits |
| New species models | Explicitly prohibited until phase ends |
| Nowcasts | Not issued; env join still incomplete |
| Forecasts | Not in scope |
| Live globe layers | Globe remains historical atlas; no live likelihood layers |

## Classification counts

| Classification | Count |
|---|---|
| START_NOW | 18 |
| REDUCED_SCOPE | 3 |
| WAIT_FOR_DEPENDENCY | 1 |
| ALREADY_COVERED | 11 |
| OWNERSHIP_CONFLICT | 0 |
| NOT_APPROPRIATE_IN_ACQUISITION_PHASE | 5 |
| **Total** | **38** |

## Out of bounds (all agents this wave)

- Edit `WORKSTREAMS.yaml`
- Modify `data/raw/`, acquisition manifests, or acquisition scripts
- Edit globe / prototype for UI tests
- Change model score CSVs or retrain
- Claim backup success while restore is `NOT_RUN`
