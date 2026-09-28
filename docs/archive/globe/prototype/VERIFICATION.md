# Browser verification — globe + UX integration (2026-09-23)

Checked on branch `integrate/globe-ux-2026-09-23`. The integration commit is `478983b9c69a0628c8ca135b2627f48b45097671`. Stabilization edits after that commit were checked on the same Vite server, `http://127.0.0.1:5174/` and `http://[::1]:5174/`, which served identical HTML (sha256 `ea0588d06615459bc438c5d2fad600041a5fc6994c2640199de34a2eb8ed042a`).

`npm run build` (`tsc --noEmit && vite build`) exited 0 after the CSS edit and again after the place-view edit. There is no test or lint script. `generate-fixtures` was not run.

Camera rows in the controls table were verified during integration and were not repeated after the stabilization edit. Truth-state rows, the 390px layout, the skip link, and the place view were checked again after that edit.

## Cold load

| Check | Status | What was observed |
|---|---|---|
| Globe and purpose line | VERIFIED | Canvas present. Purpose sentence under the search box. |
| No estimate or forecast on an empty search | VERIFIED | Answer: “No forecast issued.” Depth: “Depth unknown / not modeled.” “This is not” includes “Live tracking, a fishing map, or a count of animals.” |
| Oyster demo inactive | VERIFIED | Learn content hidden until Learn is opened. Willapa cells not drawn on cold load. |
| Default camera | VERIFIED | Projection `globe`, center `[0, 15]`, zoom `1.6`, pitch `28`. |
| Legend | VERIFIED | “Empty globe. Imagery is Earth, not a species map. Unknown is the default.” |
| Imagery | VERIFIED | Chip: “NASA Blue Marble · ~500 m · not live · bathymetry is shading, not a 3D seafloor.” GIBS attribution link present. |

## Species and places

| Check | Status | What was observed |
|---|---|---|
| Goliath search | VERIFIED | “goliath” → Atlantic goliath grouper, *Epinephelus itajara*. Where now “No issued location.” Soon “No forecast issued.” How sure “Not assessed.” Depth is an ecology note, not a live depth. Evidence states historical reports and that no current estimate or forecast is issued. 332,628 compiled records, 1935–2026, 7 coarse cells, partial-extract wording. Stamp: “Past reports 1935–2026 · not where they are now.” No wreck, spawning, or nursery layer. |
| Yellowfin tuna | VERIFIED | *Thunnus albacares*. “No issued location.” “No forecast issued.” How sure “None.” Depth unknown / not modeled. 246,964 past reports, 1788–2026, 17 drawn cells, “not where the animals are now.” `cells-fill` visibility `none`. No wreck, spawning, or nursery layer. |
| White shark | VERIFIED | *Carcharodon carcharias*. “No issued location.” “No forecast issued.” How sure “None.” “Past reports exist but locations are withheld.” Past-report feature count 0. |
| Willapa demo | VERIFIED | Opened only from “Open the oyster working-conditions demo” on Learn. Copy: planted oysters are not counted; 72-hour demo rule; not a species location; not oyster GPS; fixture/synthetic; not food-safety or harvest. Stamp: “Willapa working-conditions demo · not harvest advice.” |
| Fly to a named place | VERIFIED | After the Willapa demo was open, “Pacific Ocean” flew to about `[-160, 5]`, zoom `2.05`. Answer: “geographic view only” and “No forecast issued.” Stamp: “Geographic view · not a species location.” Evidence no longer described the Willapa cell. Legend returned to the empty-globe Unknown text. `cells-fill` stayed `none`. |
| Ten Thousand Islands | NOT_TESTED | Not selected in this session. |

## Globe controls

| Check | Status | What was observed |
|---|---|---|
| Zoom in / zoom out buttons | VERIFIED | Fresh page: zoom `1.6` → `2.6` on Zoom in, back to `1.6` on Zoom out. Center stayed `[0, 15]`. |
| Home | VERIFIED | Home returned center `[0, 15]`, zoom `1.6`, pitch `28`, globe. |
| Reset North | VERIFIED | Bearing set to `35`, then Reset North returned bearing `0`. |
| Reset tilt | VERIFIED | At zoom `5.2`, pitch `46` returned to `0`. |
| 2D / 3D | VERIFIED | Toggle to mercator kept center `[0, 15]` and zoom `5.2`, set pitch `0`, button label “2D flat map”, `aria-pressed` true. On the Willapa view, the same toggle kept center about `[-123.935, 46.552]` and zoom `9.9` and left the oyster answer in place. |
| Fly-to | VERIFIED | Pacific Ocean, above. |
| Wheel zoom | VERIFIED | A `wheel` event on the canvas changed zoom `5.2` → `5.495`. |
| Double-click zoom | VERIFIED | A `dblclick` on the canvas increased zoom by 1 (`5.495` → `6.495`). |
| Reduced motion | VERIFIED | Emulated `prefers-reduced-motion: reduce`. Zoom in changed zoom by 1 within 30 ms and the map was not in a camera animation. |
| Drag, pinch, right-drag tilt | NOT_TESTED | A drag on the compass control completed and left bearing at `0`. No pinch and no right-drag tilt were performed. |
| Drag versus click on a cell | NOT_TESTED | No pointer drag across a past-report cell was performed. |

The long-session stall is logged in `audit/bugs/2026-09-23-map-moving-stall.md`. Status this stabilization session: NOT_REPRODUCED_THIS_SESSION. Ten overlapping fly, projection, tilt, and zoom actions still left Zoom in and Reset tilt able to change the camera, and `isMoving()` returned to false.

## Accessibility

| Check | Status | What was observed |
|---|---|---|
| Keyboard search | VERIFIED | Typing `Gulf` one character at a time listed “Place — Gulf of Maine”. |
| Skip link | VERIFIED | Activating “Skip to species search” moved focus to `#species-search`. |
| Visible focus ring | NOT_TESTED | CSS sets `:focus-visible` to a 3px solid `#005f73` outline (2px on the map tool buttons). In this automation, Tab moved focus and `focus({ focusVisible: true })` was called, but `:focus-visible` did not match and the computed outline style stayed `none`. The painted ring was not confirmed. |
| Legend patterns | VERIFIED | At 390px the legend included Past reports (horizontal stripe) and Unknown (45° stripe) as separate `repeating-linear-gradient` swatches. |
| 390px viewport | VERIFIED | After the results list was placed in normal flow below 1100px, `innerWidth` 390 and `scrollWidth` 390. “Find Species”, “Explore Ocean”, “Evidence & Data”, and “Learn & Methods” were fully visible and did not overlap the open “Place — Gulf of Maine” result. Purpose line and sample-data banner wrapped. Map and zoom controls were visible. |

## Browser health

| Check | Status | What was observed |
|---|---|---|
| Boot error | VERIFIED | No fixture alert and no Vite error overlay on the fresh page. |
| Failed HTTP responses | VERIFIED | `performance` resource entries with status ≥ 400: none during the fresh-page session. |
| Basemap requests | VERIFIED | 140 NASA/GIBS resource entries and 12 EOX/Sentinel-2 entries completed. GIBS link visible at world zoom. Sentinel-2 cloudless link visible when zoomed to Willapa. |
| Console exceptions | NOT_TESTED | An error listener installed after load recorded none during yellowfin, Pacific, and Gulf checks. Exceptions from the initial script evaluation were not captured. |

## Publication gates

| Check | Status |
|---|---|
| `model-cards.json` has one card, Magallana gigas, `NOT_PUBLISHED` | VERIFIED by file read |
| Goliath publication decision remains `NOT_PUBLISHED` | VERIFIED by file read |
| A published current-location or species-forecast layer | NOT present. The Willapa “forecast” wording is the Learn fixture demo, labeled synthetic and not a species location. |
