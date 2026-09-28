# Camera and input controls

**Engine:** MapLibre GL JS 6.10 native handlers. No per-frame DOM camera math.  
**Reduced motion:** `prefers-reduced-motion: reduce` sets flight duration to 0 (`jumpTo`).

## Mouse

| Gesture | Action |
|---|---|
| Left drag | Pan / globe spin (native `dragPan`, tuned inertia) |
| Wheel | Zoom toward the cursor (`scrollZoom`; wheel rate 1/520) |
| Double-click | Zoom toward the click (`doubleClickZoom`) |
| Right drag | Rotate and tilt (`dragRotate` + `pitchWithRotate`) |
| Control / Command + drag | Same rotate/tilt family (MapLibre modifier) |
| Click | Select a Willapa demo cell only if the pointer moved less than 7 px |

## Trackpad

| Gesture | Action |
|---|---|
| Pinch | Zoom (`touchZoomRotate` / scroll zoom) |
| Two-finger pan | Pan |
| Two-finger rotate / pitch | Rotate and tilt where the OS reports it |

## Touch

| Gesture | Action |
|---|---|
| One-finger drag | Pan / spin |
| Two-finger pinch | Zoom |
| Two-finger rotate / tilt | Where the browser reports it |
| Tap | Select only if it was not a drag |

## Keyboard

MapLibre default when the map canvas is focused: arrow keys pan, `+` / `-` zoom.

App extras (ignored while typing in an input):

| Key | Action |
|---|---|
| Escape | Close search results and the first-run hint |
| H | Home / whole-Earth view |
| N | North up |
| 0 | Reset tilt |
| [ | Previous geographic view |

Visible buttons: Home, North up, Reset tilt, Back.

## Camera actions

| Action | Implementation |
|---|---|
| Place search | `flyTo` / `fitBounds` via `globe.flyToPlace` |
| Learn oyster demo | `fitBounds` to Willapa DOH-scale fixture |
| Home | `flyTo` world center zoom 1.35, pitch 42 on globe |
| 2D / 3D | `setProjection` keeps center, zoom, bearing, species, and selected cell |
| User grab during flight | `map.stop()` on drag, rotate, pitch, and wheel |

## Limits

- `minZoom` 0.55 so the planet stays in frame
- `maxZoom` 12 (EOX meaningful ceiling in this build; NASA Blue Marble is meaningful to zoom 8)
- `maxPitch` 70; `minPitch` 0

Do not describe these controls as “Google Earth smooth” from unit tests. Judge them by hand with a mouse and trackpad.
