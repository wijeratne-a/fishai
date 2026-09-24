# Parallel reconciliation manifest — 2026-09-23

**State:** `NOT_SAFE_TO_RECONCILE`

This session did not merge worktrees, did not edit application files, and did not change publication status.

Observation start: 2026-09-23 20:57:25 PDT.  
HEAD both trees: `20db75e50b3ad48a28aff8edd3528792598b908d` on a single local commit. No remote. **CANNOT_VERIFY_REMOTE_STATE.**

Nothing was staged in either tree.

## Dirty worktrees

### Main checkout

| | |
|---|---|
| Path | `/Users/wijeratne/dev/fishai` |
| Branch | `branch` |
| SHA | `20db75e50b3ad48a28aff8edd3528792598b908d` |
| Staged | none |
| Purpose | Globe basemap (NASA GIBS Blue Marble + EOX Sentinel-2 cloudless 2020), camera tuning, place fly-to, goliath honesty copy, taxon record. GEBCO stays unwired. |
| Appears complete | As its own pass, the diff is coherent. It is not an integrated product. Uncommitted. |
| Verification actually run | **No, not in this session.** `globe/prototype/VERIFICATION.md` claims a 2026-09-22 browser pass. That claim is **CLAIMED_NOT_VERIFIED** here. |

Modified:

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

Untracked:

- `species/goliath-grouper/OBSERVATION_PLAN.md`

Unique to this tree (UX working copy still matches HEAD):

- `globe/prototype/src/basemap.ts`
- `globe/prototype/src/camera.ts`
- `globe/prototype/src/places.ts`
- `globe/IMPLEMENTATION_BRIEF.md`
- `species/goliath-grouper/OBSERVATION_PLAN.md`

### UX worktree

| | |
|---|---|
| Path | `/Users/wijeratne/.cursor/worktrees/fishai-ux-11dc21e2/fishai-4091d9f6d7c3` |
| Branch | `ux/globe-honesty-pass` |
| SHA | `20db75e50b3ad48a28aff8edd3528792598b908d` |
| Staged | none |
| Purpose | First-run purpose line, mode labels, plain-language legend, evidence grouping, answer-strip wording. |
| Appears complete | As a UX pass, yes, but it is not a superset of the main globe. It drops pieces the integrated app must keep (see conflicts). Uncommitted. |
| Verification actually run | **No, not in this session.** An earlier UX pass reported browser checks. Those checks are **CLAIMED_NOT_VERIFIED** against today’s split servers. |

Modified:

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

Untracked:

- `globe/prototype/UX_AUDIT_NOTES.md`

Unique to this tree:

- `globe/prototype/src/evidence.ts` (modified only here)
- `globe/prototype/src/legend.ts` (modified only here)
- `globe/prototype/UX_AUDIT_NOTES.md`

## Overlaps

These working copies differ from each other. Taking either file whole discards the other tree:

`index.html`, `README.md`, `VERIFICATION.md`, `public/fixtures/taxa.json`, `src/answer.ts`, `src/layers.ts`, `src/main.ts`, `src/mapApp.ts`, `src/styles.css`, `src/types.ts`.

Semantic conflicts already visible (not inferred from mtime):

- UX `taxa.json` removes the common-name alias `goliath`. Main keeps it. Both keep AphiaID 159353 and `no_estimate`.
- UX `layers.ts` deletes `GOLIATH_APHIA_ID`. Main `main.ts` imports it and uses a goliath-specific answer.
- UX `answer.ts` / `types.ts` drop `whatCouldBeWrong`. Main renders that limitation line.
- UX `main.ts` has no goliath-specific ecology answer. It does add zoom-button wiring.
- UX `mapApp.ts` adds `zoomBy` and past-report click. Main `mapApp.ts` carries the camera/basemap pass. Both still have `flyToPlace`.
- Main Learn copy still says “Guessed”. UX legend and truth labels say “Estimate” / “Unknown”.
- Two Vite processes share port 5173: PID 69241 cwd `.../fishai/globe/prototype` on `[::1]:5173`; PID 87539 cwd the UX worktree on `127.0.0.1:5173`.

## File matrix

Paths under `globe/prototype/` unless noted. Preferred basis is semantic, not whichever file is newer.

| File | Main tree changed? | UX tree changed? | Main purpose | UX purpose | Conflict risk | Preferred basis | Manual merge required? |
|---|---|---|---|---|---|---|---|
| `index.html` | Yes | Yes | Goliath sentence in Learn; short mode names; “Guessed” remains | Purpose line; Find Species / Explore Ocean / Evidence & Data / Learn & Methods; Measured/Estimate vocabulary | High | UX structure and labels, plus main’s goliath withholding sentence | Yes |
| `README.md` | Yes | Yes | Globe stack, honesty rules, claimed verification split | Short pointer toward the UX pass | Medium | Main honesty rules, then UX purpose wording | Yes |
| `VERIFICATION.md` | Yes | Yes | Claims a 2026-09-22 browser pass for goliath and camera math | Claims UX checks | High | Neither, until one server is retested. Do not treat either as current | Yes |
| `public/fixtures/taxa.json` | Yes | Yes | Adds *E. itajara* 159353, `no_estimate`, alias `goliath`, aggregation note | Same taxon and status; drops alias `goliath`; shorter note | High | Main record (alias + sensitivity note). Do not take the UX file whole | Yes |
| `src/answer.ts` | Yes | Yes | Renders `whatCouldBeWrong` and target note | Clearer empty depth line; hides targets until expert; drops `whatCouldBeWrong` | High | Main fields, UX depth wording and expert disclosure | Yes |
| `src/layers.ts` | Yes | Yes | Exports `GOLIATH_APHIA_ID`; historical-pattern copy | Renames guessed→estimate; deletes `GOLIATH_APHIA_ID` | High | Main constant, UX plain-language strings | Yes |
| `src/main.ts` | Yes | Yes | Goliath ecology answer, publication refusal, place fly-to | Mode wiring, zoom buttons, generic refusal, gap hint | High | Main file as the base. Port UX controls onto it. Do not replace the file | Yes |
| `src/mapApp.ts` | Yes | Yes | Camera/basemap apply path, past-report source, drag-vs-click, fly-to | `zoomBy`, past-report click selection | High | Main file as the base. Port UX click and zoom helpers | Yes |
| `src/styles.css` | Yes | Yes | Small chrome adjustments | Purpose, tools, legend, evidence, mobile | Medium | UX presentation rules, after checking they do not hide honesty text | Yes |
| `src/types.ts` | Yes | Yes | Adds `whatCouldBeWrong` | Truth labels Estimate / Forecast / Unknown; removes `whatCouldBeWrong` | High | UX labels, main optional field kept | Yes |
| `src/basemap.ts` | Yes | No | NASA/EOX registry, attribution, resolution, GEBCO `wired: false` | Unchanged from HEAD | Low | Main | No |
| `src/camera.ts` | Yes | No | Constants, reduced motion, drag threshold, north/home/tilt helpers | Unchanged from HEAD | Low | Main | No |
| `src/places.ts` | Yes | No | Place search / fly-to targets | Unchanged from HEAD | Low | Main | No |
| `src/evidence.ts` | No | Yes | HEAD past-report summary and escaped evidence HTML | Grouped plain-language evidence | Medium | UX, after checking honesty strings and `escapeHtml` remain | Review, not a blind copy |
| `src/legend.ts` | No | Yes | HEAD still says Guessed / Future / Don’t know | Measured, Estimate, Forecast, Past reports, Unknown | Low | UX | No, if honesty microcopy stays |
| `UX_AUDIT_NOTES.md` | No | Untracked | Absent | UX findings | Low | Keep the untracked file | No |
| `globe/IMPLEMENTATION_BRIEF.md` | Yes | No | Points the brief at the goliath slice | Unchanged from HEAD | Low | Main | No |

## Desired integrated result

Preserve from the main globe/camera work:

- NASA GIBS and EOX basemap configuration, attribution, and resolution metadata in `basemap.ts`
- Camera constants, reduced-motion handling, drag-versus-click protection
- Home, north, tilt, and projection controls
- Place search and fly-to
- Biological-resolution warning when past reports are on screen
- GEBCO remaining unwired

Preserve from the UX/honesty work:

- Standing purpose statement
- Modes: Find Species, Explore Ocean, Evidence & Data, Learn & Methods
- Legend words: Measured, Estimate, Forecast, Past reports, Unknown
- Grouped evidence and progressive disclosure
- First-run clarity and accessibility improvements that do not weaken honesty
- Do not keep “Guessed” or “Don’t know” where “Estimate” and “Unknown” already exist

Preserve from both:

- “No issued location.”
- “No forecast issued.”
- “This is not live tracking, a fishing map, or a count of animals.”
- Publication gates (`PUBLISHED` count stays zero)
- Goliath `no_estimate`, AphiaID 159353, including the `goliath` search alias
- White-shark location withholding
- Willapa demo hidden until Learn
- Past reports labeled historical, not present animals
- Main’s goliath “what could be wrong” line and ecology depth note (not a depth model)
- `GOLIATH_APHIA_ID`

## Safety checklist

- [ ] Other implementation agents have stopped writing. **Cannot verify.** Two Vite servers from the prior passes are still listening.
- [x] Start Git status of application files recorded (20:57:25 PDT). End status at 20:59:19 PDT matched: same 14 modified application files and the same untracked `OBSERVATION_PLAN.md` on main; same 12 modified files and `UX_AUDIT_NOTES.md` on the UX tree. Diff stat stayed 209 insertions and 65 deletions. The only new untracked paths were these two audit files. Other processes did not change application files during this window. Vite PIDs 69241 and 87539 were still listening.
- [ ] Both worktrees’ changes are preserved in commits or patch files. **False.** All of the work above is uncommitted. This session did not create commits or patches.
- [ ] No untracked file is at risk of deletion. **False until copied.** At risk: `species/goliath-grouper/OBSERVATION_PLAN.md`, `globe/prototype/UX_AUDIT_NOTES.md`.
- [x] Audit report saved at `audit/current-state-audit-2026-09-23.md`.
- [x] This manifest records overlaps and intended semantics.
- [ ] One integration branch has been selected in Git. **Not created.** Recommended name, later: `integrate/globe-ux-2026-09-23`, branched from the main checkout only after patches exist.
- [x] Intended semantics for every overlapping file are in the matrix above.

Because the unchecked items are false, this session does not merge and does not edit overlapping application files.

## Preservation plan (do not execute in this session)

1. **Integration base:** the main checkout `/Users/wijeratne/dev/fishai` (branch `branch`). It holds basemap, camera, places, `GOLIATH_APHIA_ID`, and the goliath answer. The UX tree is the source of legend, evidence grouping, and mode labels, not the base to overwrite main with.
2. **Preserve each dirty tree before any merge**, as named patches (preferred over a commit until a human asks to commit):
   - From the main checkout: `git diff > audit/patches/main-globe-camera-2026-09-23.patch`, and copy `species/goliath-grouper/OBSERVATION_PLAN.md` beside it.
   - From the UX worktree: `git diff > audit/patches/ux-honesty-2026-09-23.patch`, and copy `globe/prototype/UX_AUDIT_NOTES.md` beside it.
   - Do not use `git reset --hard`, `git clean`, `git checkout -- .`, `git restore .`, forced branch deletion, or an unreviewed merge tool.
3. **Accept from main without combining the other version:** `basemap.ts`, `camera.ts`, `places.ts`, `IMPLEMENTATION_BRIEF.md`.
4. **Accept from UX after a honesty read:** `legend.ts`, `UX_AUDIT_NOTES.md`. `evidence.ts` only if past-report wording and HTML escaping survive.
5. **Manual semantic merge:** every row marked Yes in the matrix. For `main.ts` and `mapApp.ts`, start from the main file and port specific UX functions (`zoomBy` wiring, past-report click, mode labels, gap hint). Do not concatenate the two files and do not take the UX `main.ts` as a replacement. That file has no goliath-specific answer and its `layers.ts` no longer exports `GOLIATH_APHIA_ID`.
6. **Vite servers:** do not kill them while another session may be using them. When agents have stopped, confirm cwd with `lsof -a -p 69241 -d cwd` and `lsof -a -p 87539 -d cwd`, stop only those two processes, and start a single `npm run dev` from the integration tree. Check both `http://127.0.0.1:5173/` and `http://[::1]:5173/` serve the same HTML.
7. **Verify** with the test plan below. One URL only.
8. **Restore if integration fails:** both worktrees are the originals until patches exist. Leave them in place. Re-apply the named patches onto a fresh worktree from `20db75e`. Do not hard-reset the dirty trees.

## Post-integration test plan

Run these only after one integrated tree exists. Do not claim they passed from this manifest.

### Build

- `npm run build` in `globe/prototype` (TypeScript `tsc --noEmit` plus Vite).
- Lint only if a lint script exists. Today `package.json` has no lint script.
- No unresolved imports.
- No conflict markers.

### Cold load

- One server and one unambiguous URL.
- Globe renders.
- Standing purpose text is visible.
- Oyster demo does not open by itself.
- No current estimate and no forecast.

### Goliath grouper

- Search resolves *Epinephelus itajara*.
- AphiaID remains 159353.
- Status remains `no_estimate`.
- Answer says “No issued location.”
- Answer says “No forecast issued.”
- Depth is ecology, not a depth model.
- Past reports are labeled historical.
- Capped OBIS results are labeled a partial extract.
- Missing cells are not biological absence.
- No spawning or wreck coordinates.

### Unsupported species

- No estimate or forecast layer.
- Historical records stay separate from current presence.

### Sensitive species

- White-shark search returns no geometry.
- UI state cannot bypass that withhold.

### Willapa demo

- Hidden until Learn.
- Labeled synthetic.
- Cannot become the default species answer.

### Camera

- Mouse drag, wheel zoom, double-click zoom, rotate, tilt.
- Drag does not select.
- Fly-to, north reset, tilt reset, home.
- 2D/3D keeps species context.
- Reduced motion shortens or skips flights.

### Accessibility

- Keyboard search, visible focus, skip link, panel names.
- 390px layout.
- Legend meaning is not color alone.

### Performance

- Record browser and hardware.
- Measure time until the globe accepts input.
- Observe camera frames.
- Record console and network errors.
- Do not call the result Google Earth–smooth without those measurements.

## Scientific milestone after reconciliation (do not implement now)

Produce the first defensible goliath grouper occurrence estimate for one bounded region and time window.

Prerequisites, all required before any card leaves `NOT_PUBLISHED`:

- Rights-approved source inventory
- Structured detections and non-detections
- Sampling-effort information
- Explicit target, region, depth bands, and time window
- Seasonal and habitat baselines
- Fitted effort-aware occurrence model
- Spatial-block holdout
- Time-forward holdout
- Calibration assessment
- Uncertainty and out-of-domain behavior
- Sensitive-site review
- Named human reviewer and publisher

Do not add a forecast slider, abundance map, movement animation, spawning-site pins, or a current-location heatmap before those gates pass.

## Blockers

Reconciliation is not safe, and this session did not perform it.

1. Changes are not saved as commits or patch files.
2. Untracked `OBSERVATION_PLAN.md` and `UX_AUDIT_NOTES.md` would be lost by a clean.
3. Two servers are still running; other writers cannot be ruled out from process existence alone.
4. No integration branch exists yet.
5. `main.ts` and `mapApp.ts` are incompatible as whole-file replacements.
