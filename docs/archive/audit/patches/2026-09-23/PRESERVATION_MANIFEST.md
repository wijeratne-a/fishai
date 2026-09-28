# FishAI Parallel Work Preservation

## Baseline

Prior records still matched before any artifact was written:

- `audit/current-state-audit-2026-09-23.md` classification: `FUNCTIONAL_HISTORICAL_ATLAS`
- `audit/parallel-reconciliation-manifest-2026-09-23.md` state: `NOT_SAFE_TO_RECONCILE`
- Both worktrees existed and were based on `20db75e50b3ad48a28aff8edd3528792598b908d`

No difference from that baseline was found in branch, SHA, or application diffs.

- Base commit: `20db75e50b3ad48a28aff8edd3528792598b908d`
- Main worktree: `/Users/wijeratne/dev/fishai`, branch `branch`
- UX worktree: `/Users/wijeratne/.cursor/worktrees/fishai-ux-11dc21e2/fishai-4091d9f6d7c3`, branch `ux/globe-honesty-pass`
- Remote: none configured. **CANNOT_VERIFY_REMOTE_STATE**
- Snapshot A: 2026-09-23 21:19:12 PDT
- Snapshot B: 2026-09-23 21:22:19 PDT
- Snapshot C: 2026-09-23 21:24:28 PDT

Original worktrees were not modified, committed, or merged. Temporary check worktrees under `/tmp/fishai-preserve-2026-09-23/` were removed after the restore test. `git worktree list` again shows only the two original trees.

## Main Artifact

- Patch: `audit/patches/2026-09-23/main-globe-camera.patch`
- Status copy: `audit/patches/2026-09-23/main-status.txt`
- Diff stat: `audit/patches/2026-09-23/main-diff-stat.txt` (14 files, 209 insertions, 65 deletions)
- Name status: `audit/patches/2026-09-23/main-name-status.txt`
- Untracked copy: `audit/patches/2026-09-23/main-untracked/species/goliath-grouper/OBSERVATION_PLAN.md`
- Original untracked file was copied, not moved.

Modified tracked files:

- `globe/IMPLEMENTATION_BRIEF.md`
- `globe/prototype/README.md`
- `globe/prototype/VERIFICATION.md`
- `globe/prototype/index.html`
- `globe/prototype/public/fixtures/taxa.json`
- `globe/prototype/src/answer.ts`
- `globe/prototype/src/basemap.ts`
- `globe/prototype/src/camera.ts`
- `globe/prototype/src/layers.ts`
- `globe/prototype/src/main.ts`
- `globe/prototype/src/mapApp.ts`
- `globe/prototype/src/places.ts`
- `globe/prototype/src/styles.css`
- `globe/prototype/src/types.ts`

Checksum (`shasum -a 256`):

`0f0eeaa00afbc9ac867436c945ba6ccf0999a6ac5ac54a893ebd953a33fe6b79`

Apply check: **RESTORABLE**

Commands, each exit 0:

- `git worktree add --detach /tmp/fishai-preserve-2026-09-23/main-check 20db75e50b3ad48a28aff8edd3528792598b908d`
- `git apply --check audit/patches/2026-09-23/main-globe-camera.patch`
- `git apply --binary audit/patches/2026-09-23/main-globe-camera.patch`

`git apply` warned that 2 patch lines add trailing whitespace. Exit code was still 0. No `.rej` files. The 14 restored files were byte-identical to the main worktree. The copied observation plan restored to `species/goliath-grouper/OBSERVATION_PLAN.md` and matched the original.

## UX Artifact

- Patch: `audit/patches/2026-09-23/ux-honesty.patch`
- Status copy: `audit/patches/2026-09-23/ux-status.txt`
- Diff stat: `audit/patches/2026-09-23/ux-diff-stat.txt` (12 files, 546 insertions, 105 deletions)
- Name status: `audit/patches/2026-09-23/ux-name-status.txt`
- Untracked copy: `audit/patches/2026-09-23/ux-untracked/globe/prototype/UX_AUDIT_NOTES.md`
- Original untracked file was copied, not moved.

Modified tracked files:

- `globe/prototype/README.md`
- `globe/prototype/VERIFICATION.md`
- `globe/prototype/index.html`
- `globe/prototype/public/fixtures/taxa.json`
- `globe/prototype/src/answer.ts`
- `globe/prototype/src/evidence.ts`
- `globe/prototype/src/layers.ts`
- `globe/prototype/src/legend.ts`
- `globe/prototype/src/main.ts`
- `globe/prototype/src/mapApp.ts`
- `globe/prototype/src/styles.css`
- `globe/prototype/src/types.ts`

Checksum (`shasum -a 256`):

`7fd76e27b1d5af48159903d6760c859ff4195de04ac38177fa337a17eb1bfe64`

Apply check: **RESTORABLE**

Commands, each exit 0, on a separate clean worktree (the two patches were not applied together):

- `git worktree add --detach /tmp/fishai-preserve-2026-09-23/ux-check 20db75e50b3ad48a28aff8edd3528792598b908d`
- `git apply --check audit/patches/2026-09-23/ux-honesty.patch`
- `git apply --binary audit/patches/2026-09-23/ux-honesty.patch`

`git apply` warned that 1 patch line adds trailing whitespace. Exit code was still 0. No `.rej` files. The 12 restored files were byte-identical to the UX worktree. The copied `UX_AUDIT_NOTES.md` restored to `globe/prototype/UX_AUDIT_NOTES.md` and matched the original.

The live `git diff --binary --full-index` in each source worktree matched the saved patch byte for byte at capture time.

## Stability Observation

Application-file sizes and modification times were identical at A, B, and C. `audit/patches/` was ignored for this comparison. Between A and B, Git status gained only `?? audit/patches/`, which this session created.

### Snapshot A — 2026-09-23 21:19:12 PDT

- Main diff stat: 14 files, +209 / −65
- UX diff stat: 12 files, +546 / −105
- Vite: PID 69241 cwd `/Users/wijeratne/dev/fishai/globe/prototype` on `[::1]:5173`; PID 87539 cwd the UX `globe/prototype` on `127.0.0.1:5173`

### Snapshot B — 2026-09-23 21:22:19 PDT

- Same application status, diff stats, sizes, and mtimes
- Same Vite PIDs and cwd values

### Snapshot C — 2026-09-23 21:24:28 PDT

- Same application status, diff stats, sizes, and mtimes
- Same Vite PIDs and cwd values
- `shasum -a 256 -c audit/patches/2026-09-23/SHA256SUMS.txt` exit 0

Files that changed: none observed among application files.

Classification: **STABLE_DURING_OBSERVATION**

This does not mean an implementation agent has stopped. Both dev servers were still listening. Process intent beyond those PIDs was not established.

## Other checksums

Verified with `shasum -a 256 -c` immediately after writing, and again at snapshot C. Both runs exited 0.

| File | SHA-256 |
|---|---|
| `main-globe-camera.patch` | `0f0eeaa00afbc9ac867436c945ba6ccf0999a6ac5ac54a893ebd953a33fe6b79` |
| `ux-honesty.patch` | `7fd76e27b1d5af48159903d6760c859ff4195de04ac38177fa337a17eb1bfe64` |
| copied `OBSERVATION_PLAN.md` | `4d4f4a3f4666c8c8f0905e65eb185438d51273c1b4d42c8443d938ceaaba0052` |
| copied `UX_AUDIT_NOTES.md` | `db789cf34c36fec2ba32e741674f018bfd6c48aa51159a6d3a0a95b8f03c25af` |
| `audit/current-state-audit-2026-09-23.md` | `e2ab8840e1d80fb07773d336143136194f16d588fdcb149f24cbd7ce673644a1` |
| `audit/parallel-reconciliation-manifest-2026-09-23.md` | `e1b192247854bdc24d54cedea638096961f7245d6bd95d9282869dc77daf7e3c` |

## Preservation Status

**BOTH_WORKSTREAMS_PRESERVED**

## Reconciliation Readiness

**TECHNICALLY_PRESERVED_BUT_AWAITING_HUMAN_CONFIRMATION**

- [x] Both tracked diffs are preserved.
- [x] Both untracked files are preserved.
- [x] Patch checks pass.
- [x] Restoration tests pass. Whitespace warnings did not reject hunks or change bytes.
- [x] Checksums verify.
- [x] No application-file changes were observed during the stability window.
- [ ] A human explicitly confirms the implementation agents are finished.
- [ ] An integration branch has been selected.

Do not start reconciliation until those last two boxes are true. The patches were not applied to either original worktree, and they must not be applied together onto one tree.
