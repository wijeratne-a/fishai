# Globe + UX semantic integration — 2026-09-23

## Classification

FUNCTIONAL_HISTORICAL_ATLAS

This is a functional historical atlas. It does not issue a current location estimate or forecast for goliath grouper or other species.

No new verified evidence in this session supports a higher class. OBIS counts observed in the browser are compiler totals and a capped ~1° extract, not a fitted model and not a census.

## Base and worktrees

| Item | Value |
|---|---|
| Integration branch | `integrate/globe-ux-2026-09-23` |
| Base SHA | `20db75e50b3ad48a28aff8edd3528792598b908d` |
| Semantic base | `/Users/wijeratne/dev/fishai` (previously branch `branch`, dirty camera/basemap work kept) |
| UX source, not edited by this merge | `/Users/wijeratne/.cursor/worktrees/fishai-ux-11dc21e2/fishai-4091d9f6d7c3` on `ux/globe-honesty-pass` |
| Remote | none (`CANNOT_VERIFY_REMOTE_STATE`) |

The merge was manual. Neither patch was applied with `git apply` onto the integration tree. No automatic merge, reset, clean, or checkout of the working tree.

## Preserved artifact checksums

From `audit/patches/2026-09-23/SHA256SUMS.txt` (verified before this integration):

| Artifact | SHA-256 |
|---|---|
| `main-globe-camera.patch` | `0f0eeaa00afbc9ac867436c945ba6ccf0999a6ac5ac54a893ebd953a33fe6b79` |
| `ux-honesty.patch` | `7fd76e27b1d5af48159903d6760c859ff4195de04ac38177fa337a17eb1bfe64` |
| `main-untracked/.../OBSERVATION_PLAN.md` | `4d4f4a3f4666c8c8f0905e65eb185438d51273c1b4d42c8443d938ceaaba0052` |
| `ux-untracked/.../UX_AUDIT_NOTES.md` | `db789cf34c36fec2ba32e741674f018bfd6c48aa51159a6d3a0a95b8f03c25af` |
| `audit/current-state-audit-2026-09-23.md` | `e2ab8840e1d80fb07773d336143136194f16d588fdcb149f24cbd7ce673644a1` |
| `audit/parallel-reconciliation-manifest-2026-09-23.md` | `e1b192247854bdc24d54cedea638096961f7245d6bd95d9282869dc77daf7e3c` |

## What came from the main camera pass

Kept as the semantic base:

- `globe/prototype/src/basemap.ts` — NASA GIBS Blue Marble and EOX Sentinel-2 cloudless 2020. GEBCO stays cataloged and unwired.
- `globe/prototype/src/camera.ts` — world center `[0, 15]`, zoom `1.6`, pitch `28`, reduced-motion timing, drag threshold, flight interrupt.
- `globe/prototype/src/places.ts`
- `globe/prototype/src/layers.ts` — `GOLIATH_APHIA_ID` `159353` and the publish gates (`mayDrawCurrentEstimate`, forecast, abundance, movement).
- `globe/prototype/public/fixtures/taxa.json` — goliath alias, AphiaID 159353, status `no_estimate`.
- Goliath answer block in `main.ts`, including `whatCouldBeWrong`.
- `whatCouldBeWrong` on the answer type and renderer.
- `globe/IMPLEMENTATION_BRIEF.md` species-slice pointer.
- `species/goliath-grouper/OBSERVATION_PLAN.md`

## What was ported from the UX pass

Ported by hand onto the main files. The UX copies of `main.ts`, `mapApp.ts`, `layers.ts`, `answer.ts`, `types.ts`, and `taxa.json` were not substituted wholesale.

- Purpose sentence in `index.html` and the standing purpose line.
- Mode labels: Find Species, Explore Ocean, Evidence & Data, Learn & Methods. Internal `data-nav` values stay `find` / `explore` / `evidence` / `learn`.
- Legend and Learn words: Measured, Estimate, Forecast, Past reports, Unknown. Internal enum names were not renamed.
- Grouped evidence (Observations, Model estimates, Environment, Methods and limitations) and the goliath historical-report sentence.
- Progressive disclosure: targets note stays expert-only; cold legend states that Unknown is the default.
- Zoom toolbar buttons, past-report cell click, and projection-button chrome, added beside the existing camera helpers.
- `globe/prototype/UX_AUDIT_NOTES.md` copied in as notes.

## Conflict decisions

| Conflict | Decision |
|---|---|
| UX `taxa.json` dropped the alias “goliath” | Kept the main record so “goliath” still resolves to AphiaID 159353. |
| UX `layers.ts` removed `GOLIATH_APHIA_ID` | Kept the export. `main.ts` still imports it. |
| UX answer types dropped `whatCouldBeWrong` | Kept the field and the goliath wording about wrecks, spawning, and sampling. |
| Both `mapApp.ts` files fly to a place | Kept the main camera/basemap implementation and added `zoomBy` and `onPastReportSelect`. |
| Learn copy said Guessed / Future / Don’t know | Visible words are Estimate, Forecast, and Unknown. |
| Willapa demo uses forecast language | Left behind the Learn button, labeled fixture/synthetic, card remains `NOT_PUBLISHED`. |

## Intentionally excluded

- Applying both patch files onto one tree.
- Publishing a model card, adding a species forecast, abundance layer, or spawning, wreck, or nursery geometry.
- Sensitive goliath coordinates and white-shark occurrence geometry.
- Wiring GEBCO.
- New dependencies.
- Edits to the UX worktree.
- `dist/`, `node_modules`, caches, and screenshots.

## Servers

Stopped only after identity checks:

- PID 69241, Vite, cwd `/Users/wijeratne/dev/fishai/globe/prototype`
- PID 87539, Vite, cwd `/Users/wijeratne/.cursor/worktrees/fishai-ux-11dc21e2/fishai-4091d9f6d7c3/globe/prototype`

Integration server: `npm run dev -- --host --port 5174 --strictPort` from the main prototype. It listened on `*:5174`.

## Build

`cd globe/prototype && npm run build` exited 0 (`tsc --noEmit && vite build`). Vite reported a large JS chunk warning only. No test script and no lint script exist. Dependencies were not installed. `generate-fixtures` was not run.

## Browser verification

Recorded in `globe/prototype/VERIFICATION.md`.

Verified in this session: cold load, goliath, yellowfin, white shark withhold, Learn-only Willapa demo, zoom buttons, home, reset north, reset tilt, 2D/3D center and zoom preservation, Pacific Ocean fly-to, canvas wheel and double-click zoom, emulated reduced motion, keyboard search, skip link, 390px layout, legend stripe patterns, GIBS and EOX requests with no HTTP status ≥ 400 in the resource log.

Not tested: pointer drag, pinch, right-drag tilt, drag-versus-click on a cell, Ten Thousand Islands, and a painted `:focus-visible` ring. One long-lived page later stopped accepting zoom and tilt animations until reload; a fresh page did not reproduce that stall.

At 390px, with search results open, the results list covered part of the “Find Species” label. The page did not scroll horizontally.

## Honesty gates still in force

- Zero `PUBLISHED` cards. The only card is Magallana gigas, `NOT_PUBLISHED`.
- `species/goliath-grouper/PUBLICATION_DECISION.md` remains `NOT_PUBLISHED`.
- White-shark locations stay withheld.
- Goliath wrecks, spawning sites, and nursery pins are not layers.
- GEBCO is unwired.
- Willapa stays a Learn-only synthetic working-conditions demo.

## Remaining limitations

- No species model was fit, validated, or published.
- Past-report grids are a partial OBIS extract (at most 80 cells, API order, cells with n < 3 hidden, about 1°). Missing cells are not biological absence.
- A later stabilization edit clears the Willapa demo and the previous evidence text when a named place is chosen. That behavior is recorded in `audit/post-integration-stabilization-2026-09-23.md`.
- Pointer drag, pinch, and tilt gestures were not confirmed.
- A stuck `isMoving()` state was observed once on a long-lived page.
