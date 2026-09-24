# Post-integration stabilization — 2026-09-23

## Branch

`integrate/globe-ux-2026-09-23`

Parent integration commit: `478983b9c69a0628c8ca135b2627f48b45097671`

This file is part of the stabilization commit on that branch. The commit SHA is the commit that contains this file.

## Classification

FUNCTIONAL_HISTORICAL_ATLAS

## Stall bug

Logged in `audit/bugs/2026-09-23-map-moving-stall.md`.

Reproduced this session: no. Status: NOT_REPRODUCED_THIS_SESSION.

Severity recorded as P2. The original case recovered on reload. A burst of ten overlapping fly, projection, tilt, and zoom actions left `isMoving()` false, and Zoom in and Reset tilt still changed the camera. No root cause is claimed. No camera-code change was made for it.

This bug affects interaction reliability, not scientific truth-state.

## Fixes

1. At viewports up to 1100px, the search results list is in normal flow and the mode row takes a full line. At 390px, “Find Species”, “Explore Ocean”, “Evidence & Data”, and “Learn & Methods” were fully visible beside an open result. `scrollWidth` stayed 390.
2. Choosing a named place now clears the selected species, past-report layer, and Willapa demo, then writes a geographic-only evidence note. After the demo was open, Pacific Ocean showed “Geographic view · not a species location”, the empty-globe Unknown legend, and `cells-fill` hidden. The camera moved to about `[-160, 5]` at zoom `2.05`.

## Files changed

- `globe/prototype/src/styles.css`
- `globe/prototype/src/main.ts`
- `globe/prototype/VERIFICATION.md`
- `globe/prototype/README.md`
- `audit/bugs/2026-09-23-map-moving-stall.md`
- `audit/globe-ux-integration-2026-09-23.md` (place-panel limitation pointed at this note)
- `audit/post-integration-stabilization-2026-09-23.md`

## Build

`npm run build` (`tsc --noEmit && vite build`) is the only validation script. No lint script. `generate-fixtures` was not run. Dependencies were not added.

Both `npm run build` runs exited 0: once after the CSS edit, and again after the place-view edit. The second build is the one for this commit. Vite reported only the existing large-chunk warning.

## Browser health

One Vite server from `globe/prototype` on port 5174. `http://127.0.0.1:5174/` and `http://[::1]:5174/` returned the same HTML (sha256 `ea0588d06615459bc438c5d2fad600041a5fc6994c2640199de34a2eb8ed042a`) after the CSS edit. `index.html` was not changed by the place-view edit.

No Vite error overlay on the reloaded page. Resource entries with HTTP status ≥ 400: none on the truth-state pass. GIBS and Sentinel-2 cloudless attribution links were present. An error listener installed after load recorded no exceptions during goliath, white shark, yellowfin, the oyster demo, and the Pacific place view. Exceptions thrown before that listener was installed were not captured.

## Accessibility

| Check | Result |
|---|---|
| Skip link | VERIFIED. Focus moved to `#species-search`. |
| Keyboard search | VERIFIED. Typed queries listed goliath, white shark, yellowfin, and places. |
| Focus ring | CSS sets a 3px `#005f73` outline on `:focus-visible` (2px on map tool buttons). Automation did not activate `:focus-visible`, so the painted ring was not confirmed. |
| Legend | VERIFIED. Past reports use a horizontal stripe and Unknown uses a 45° stripe. |
| 390px | VERIFIED after the layout fix. No horizontal overflow. Mode labels were not clipped. |

## Truth states rerun

No truth-state regression.

- Cold load: globe, purpose line, “No forecast issued”, oyster demo inactive, Unknown legend, center `[0, 15]`, zoom `1.6`, pitch `28`.
- Goliath: *Epinephelus itajara*, AphiaID 159353 in `taxa.json`, “No issued location.”, “No forecast issued.”, ecology depth, 332,628 past reports (1935–2026), 7 cells, partial-extract wording, no wreck, spawning, or nursery layer.
- White shark: locations withheld, 0 past-report features.
- Yellowfin: “No issued location.”, “No forecast issued.”, 246,964 past reports labeled as not where the animals are now, 17 cells, `cells-fill` hidden.
- Willapa: opened from Learn only, fixture/synthetic, not a species location, not harvest advice.
- Place: geographic only, demo cleared.

## Unresolved

- Camera stall: NOT_REPRODUCED_THIS_SESSION. Still P2 if it returns.
- Pointer drag, pinch, right-drag tilt, and drag-versus-click: NOT_TESTED.
- Painted focus ring: not confirmed in this browser automation.
- Ten Thousand Islands: NOT_TESTED.
- Initial-script console exceptions: not captured.
- Camera button, wheel, double-click, and reduced-motion checks from the integration session were not repeated after these edits.

Truth-state regressions found: no.

Final classification: FUNCTIONAL_HISTORICAL_ATLAS

This build is a functional historical atlas with a globe interface. It does not issue a current location estimate or forecast for goliath grouper or other species.
