# Information architecture audit

The live IA is a **fixture laboratory**: Area of Interest → numbered globe modes → cell → 16 provenance fields.  
The required IA is a **question answering product**: Species → place/time → confidence/depth/why → limits.

Those are different products. The GUI implements the first and is titled as the second.

---

## 1. There are no routes

| Expected IA | Actual |
|---|---|
| `/` home + search | Single `index.html` |
| `/species/yellowfin-tuna` | Missing |
| `/map?aoi=willapa` | Missing; AOI hardcoded |
| `/learn/observed-vs-forecast` | Missing; seven “later modes” listed instead |
| `/expert/cell/WILLAPA-C17` | The **default homepage** |

`globe_modes.md` even ranks shipping all ten modes as v1 as a **product failure**. The rail still **advertises** modes 2–7 and 10 as a list the user cannot use. Dead IA is still cognitive IA.

---

## 2. Hierarchy the user sees (left → center → right → footer)

```
FishAI Ocean Life Globe
└─ NOT a live fish map (acronym banner)
   ├─ AOI (Willapa, H3)
   ├─ Globe mode (1, 8, 9 + later 2–7, 10)
   ├─ Unknown map (ignorance as the feature)
   ├─ Depth (stub)
   ├─ Layer stubs (SST / habitat / n)
   ├─ Jump to cell (WILLAPA-Cxx · ENUM)     ← below fold
   ├─ Legend                                 ← below fold
   ├─ [Map of hex IDs]
   ├─ Evidence explorer
   │  ├─ OPS-RISK Category D (default, huge)
   │  ├─ Honesty questions                   ← below fold on C17
   │  └─ Fields 1–16
   └─ Timebar (7 expert clocks)
```

**Missing top nodes:** Find Species, species name, Now/Soon toggle, human confidence, human depth, Learn.

**Primary action** in this tree is “pick a coarsened cell.” That is an internal object, not a user goal.

---

## 3. Object model mismatch

| User object | App object | File |
|---|---|---|
| Species | Not a first-class object. Oyster appears only inside C17 `opsRisk` | `evidence-by-cell.json` |
| Place (named water / basin) | `cellId` `WILLAPA-C17`; labels exist in geojson but are not the select labels | `willapa-cells.geojson` vs `main.ts` option text |
| Now vs soon | `visualTruthState` enum + AOI timebar | `types.ts`, `meta.json` |
| Confidence | `high\|medium\|low\|none` plus `low (category, not a %)` | `fillTimebar`, evidence field 3 |
| Depth of animal | Depth **band of the view** (surface skin / emersion / 0–10 / unknown) | `index.html` fieldset |
| Why | 4 honesty sentences + 16 fields + ops headline | `evidence.ts` |
| Evidence pack | Always-on 16 fields, including “Copy cell JSON” | `evidence_explorer.md` MVP |

The 16-field panel is specified as mandatory for **every map click** (`evidence_explorer.md`). That forces **expert IA onto the only screen**. There is no progressive disclosure.

---

## 4. Mode model vs user jobs

Implemented modes (`types.ts` `GlobeMode`):

| ID | Label in UI | User-facing meaning | Overlap |
|---|---|---|---|
| Mode 1 | Earth / surface (2D map) | The map | Default |
| Mode 8 | Evidence / provenance | Same map, more transparent fill + station dots | Evidence is **already** the right panel |
| Mode 9 | Uncertainty / data-gap | Forces unknown-map paint + density `n=` | Duplicate of Unknown checkbox |

So “modes” are **paint recipes**, not destinations. Mode 8 does not open a different IA; the Evidence explorer is always mounted.

Recommended user nav (≤4), mapping to current:

| User mode | Replaces |
|---|---|
| **Find Species** | Does not exist — must be new home |
| **Explore Globe** | Mode 1 map, 2D default |
| **Evidence** | Right panel + today’s Mode 8 (expert) |
| **Learn** | Glossary + oyster demo + “why hatches aren’t empty ocean” |

Unknown map becomes a **layer/toggle inside Explore**, not a peer of “Earth.” Depth becomes part of the species answer, not a stub fieldset beside unused modes.

---

## 5. Default information is the wrong demo

Boot = C17 OPS-RISK (`main.ts`, `meta.json`).

IA consequence: every session **teaches** Category D farm stress, WA DOH, emersion, AphiaID. It does **not** teach “search a species” or “this hatch means we don’t know.”

C05 UNKNOWN is a better teaching cell for the observatory story and is **not** the default. The jump control that would open it is below the fold.

---

## 6. Labels that are coordinates, not names

| Control | Label | Should be |
|---|---|---|
| Select | `WILLAPA-C17 · FORECAST · W1 OPS-RISK` | “Nahcotta-area public water — forecast of farm working conditions (demo)” |
| Map text | `WILLAPA-C17` | Place name or no label until zoom |
| Banner mark | Ocean Life Globe | Matches the **wrong** mental model |
| Rail h2 | AOI, Globe mode, Layer stubs, Depth (stub) | Place, Map, Layers, Depth of this estimate |
| Evidence h2 | Evidence explorer | “What’s going on here” / species answer |

`label` in geojson is already more human (“Northern entrance (Shoalwater / Toke Point reach)”) and is **not** used in the dropdown. IA waste: the good string is hidden in the panel lede only after selection.

---

## 7. Time IA

Seven equal columns in the footer compete. User needs:

1. **As of** (one local time)
2. **About the next N hours** (one range)
3. Everything else in Expert

AOI-level “last direct observation” stays visible even when the selected cell is UNKNOWN with `lastDirectObservation: none` (C05). That is an IA lie: the footer talks about a bay-wide fixture clock, the panel talks about this cell. Two times, one chrome.

`time_and_forecast_ui.md`: if the view is not a forecast, show `n/a — no forecast issued`. **Not done.** Footer always looks like a live forecast product.

---

## 8. Spec IA vs commercial IA vs founder IA

| Source | Intended top object |
|---|---|
| Founder / 30s goal | Species location |
| `globe/README.md` | Visual language + Willapa fixture; “not the commercial MVP” |
| `globe_modes.md` | Honest local instrument, Willapa only |
| Commercial `wireframe_spec.md` | One farm, one email, no map |
| Live GUI | Cell + visualTruthState + OPS-RISK |

Shipping the globe **named** as Ocean Life Globe without Find Species is an IA bait-and-switch. The specs even warn against a “planetary arcade,” then the **product title** promises a globe of life. Users believe titles.

---

## 9. Required IA rewrite (see `09_redesign_spec.md`)

1. **Species** is the root. Cells are an expert spatial grain.
2. **Four nav items**, not ten modes.
3. **Answer strip** is a peer of the map, not field 8 of 16.
4. **Oyster OPS-RISK** is a Learn/Expert scenario, not `/`.
5. **No-data species** is a real destination, equal to a filled map.
6. Keep 2D map. Keep truth-state encodings. **Hide** EMIV, Category D, H3, cell IDs, 16 fields behind Expert Mode.
