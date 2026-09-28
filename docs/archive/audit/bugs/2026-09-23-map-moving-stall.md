# Map camera stall after projection and tilt activity

## Status

NOT_REPRODUCED_THIS_SESSION

Severity: **P2**. The original observation recovered after a full page load. A fresh page in the integration session did not show the stall, and a follow-up burst on 2026-09-23 also left zoom and reset-tilt working.

This bug affects interaction reliability, not scientific truth-state.

## Where it was seen

| Item | Value |
|---|---|
| Branch | `integrate/globe-ux-2026-09-23` |
| Commit containing the camera code | `478983b9c69a0628c8ca135b2627f48b45097671` |
| Environment | macOS Darwin 25.6.0, Cursor embedded browser, Vite 6.4.3, MapLibre GL JS 6.10.0 |
| Server | `http://127.0.0.1:5174/` and `http://[::1]:5174/`, one Vite process from `globe/prototype` |

The observation happened on a long-lived page during integration verification, before that commit was created. The camera code under test is the code in that commit.

## Observed symptom

After several projection and tilt actions on that page:

- `map.isMoving()` stayed true while zoom, pitch, and center were not changing.
- Zoom in and Reset tilt then did not change zoom or pitch.
- `map.jumpTo` still changed zoom and pitch.
- `map.stop()` cleared `isMoving()`.
- A following `easeTo` of zoom left `isMoving()` true again and did not change zoom.
- Loading the same app in a new page did not reproduce the stall. On that page, zoom, home, reset north, reset tilt, and the 2D toggle changed the camera.

Reproducible or intermittent: intermittent. Recoverable by reload. Not reproduced in the stabilization session.

## Stabilization attempt (2026-09-23)

On a fresh load of the same server, a script overlapped `flyTo` with the 3D/2D button, Reset tilt, and Zoom in for 10 cycles. After the burst settled, `isMoving()` was false, Zoom in increased zoom by 1, and Reset tilt moved pitch from about 26.6 to 0.

During an earlier overlapping flight, `pitchstart` fired without `originalEvent`, and `map.stop()` ran. That shows the flight-interrupt listener can run for a programmatic pitch. It did not leave the map stuck in this attempt, so it is not established as the cause.

## Suspected areas

Not a root cause. Places worth inspecting if the stall returns:

- motion-state cleanup after `map.stop()`
- transition completion (`easeTo` / `flyTo` left in progress)
- camera event listeners, including `bindFlightInterrupt` on `pitchstart`, `rotatestart`, `dragstart`, and `wheel`
- projection-toggle `easeTo` overlapping another flight
- reduced-motion path (`motionMs` returns 0 and uses `jumpTo`)
- control handlers do not disable the buttons while `isMoving()` is true; the failure was that `easeTo` stopped taking effect

## Out of scope

No scientific copy, publication gate, species layer, or forecast behavior changed with this record.
