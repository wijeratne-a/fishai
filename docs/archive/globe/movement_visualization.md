# Movement visualization

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/movement_visualization.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Later-mode spec. **Not MVP.** W1 oysters are sessile on gear; do not draw swimming oysters.

Never imply every individual follows one predicted route. Never reveal sensitive migration or spawning at harmful precision.

---

## 1. Object types (do not share a line style)

| Object | Truth state | Geometry | Motion |
|---|---|---|---|
| Observed tag / telemetry track | `TAGGED_INDIVIDUAL` | **Solid** polyline + time-stamped points | Cursor along **stored** vertices only |
| Survey / camera / acoustic fix sequence | Matching detection state | Solid stamps | None unless a documented track |
| Inferred migration corridor | `MODEL_INFERENCE` | **Translucent band** + probability contours | None or slow pulse labeled inferred |
| Forecast probability plume | `FORECAST` | **Dashed** particle cloud or dashed contour | Optional playback of **issued** fields |
| Passive advection (currents, larvae, eDNA, HAB cells) | `MODEL_INFERENCE` / `FORECAST` | Streamlines / particles | Labeled **passive / hydrodynamic** |
| Active animal movement | `MODEL_INFERENCE` | Oriented envelope | Labeled **active (behavior model)** |
| Seasonal distribution shift | `HISTORICAL_RANGE` or inferred | Muted polygons by month | Stepped months, not smooth morph |
| Climate-driven range shift | `SCENARIO` | Research banner | Never operator 72h |
| Connectivity (source–sink) | Literature or model | Arrows with relationship class | See food-web rules |
| Spawning / feeding / nursery **transitions** | Mixed | Default **withhold** sites | Phenology as **time**, not GPS |

---

## 2. Passive vs active (mandatory caption)

| Kind | Physics | Caption |
|---|---|---|
| Passive | Water moves the tracer | `Passive transport (currents / tides) · not swimming` |
| Active | Behavior, swimming, walking, vertical migration | `Active movement model · individuals may not follow this` |
| Mixed | e.g. larvae with ontogenetic swimming | Split encoding or refuse a single arrow |

Current **streamlines** are physical ocean layers, not fish. They may sit under a movement layer but keep the physical legend.

---

## 3. Uncertainty envelopes

| Confidence | Visual |
|---|---|
| High (rare for movement) | Narrow band; still not a single “the route” unless it is a **single tagged animal** |
| Medium | Wide translucent corridor |
| Low | Diffuse envelope + `HIGH UNCERTAINTY` label |
| None | Do not draw a corridor; show coverage hatch |

**Forbidden:** one centerline that looks like a GPS path when the object is a population corridor.

For a **single tagged animal**, a solid line is allowed **in PRIVATE/RESTRICTED PI views**. Public: coarsen, delay, or withhold (`sensitive_display_rules.md`). Strip public names (“watch Turtle X”).

---

## 4. Parent brief support list — status

| # | Feature | Status |
|---|---|---|
| 1 | Ocean current streamlines | Later physical layer |
| 2 | Particle advection paths | Later research (larvae/eDNA/HAB) |
| 3 | Species probability movement vectors | Later; arrows on **issued** fields only |
| 4 | Migration corridors | Later; coarsened; no listed-ESU mouths |
| 5 | Larval dispersal trajectories | Later research; not W1 72h |
| 6 | Tag tracks | Partner/PI; public delayed/coarse or never |
| 7 | Individual-based simulation tracks | `HYPOTHETICAL_RESEARCH`; banner |
| 8 | Forecasted probability plume | Later; dashed |
| 9 | Seasonal distribution shift | T1 historical ok if coarsened |
| 10 | Climate-driven range shift | Scenario only |
| 11 | Source-to-destination connectivity | Relationship class required |
| 12 | Predicted spawning/feeding/nursery transitions | **No harmful site precision**; often time-only |

---

## 5. Sensitive movement (hard)

Do **not** draw at native grain, even if a paper published a figure:

- Nesting beaches, internesting, hatchling nights  
- Spawning aggregations (GPS, depth, moon timing, fish choruses)  
- Natal-stream holding pools, listed salmon mouths as hotspots  
- Haul-outs, calving, pupping  
- Raw ARGOS/GPS/PSAT of turtles, mammals, sawfish, aggregation sharks  
- Anything that back-solves a nest from a “corridor” animation  

Public, if ever: basin / EEZ / 0.1°–1° **delayed** seasonal presence after harm review — not a fly-along.

**Reverse-engineering test:** time-slider + corridor must not let a user wait on a whale or find a grouper aggregation. Fail → withhold.

---

## 6. W1 / sessile rule

Pacific oyster grow-out: **no movement layer**. Gear may shift in storms (operational), which is a **workability / gear-inspect option**, not a migration plume.

If larval set is ever studied, it is a **different target**, not the 72h ops-stress product, and not a public settlement heatmap.
