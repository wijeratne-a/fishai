# Before / after wireframes

Desktop ~1440×900. **Before** is the live `globe/prototype` first-run (measured). **After** is the redesign in `09_redesign_spec.md`. Not implemented.

---

## 1. First run / home

### Before (actual)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ FISHAI · OCEAN LIFE GLOBE                                                    │
│ Not a live fish map. Fixtures 2026-09-18. No OBIS, GBIF, AIS, GFW…          │
│ Not harvest authorization. Not food-safety. Not WA DOH open/closed.          │
├──────────────┬─────────────────────────────────────────┬─────────────────────┤
│ AOI          │ FIXTURE · NOT FOR NAVIGATION · NOT LIVE │ Evidence explorer   │
│ Willapa Bay  │                                         │ Nahcotta… (W1       │
│ H3-like ~20  │         [ WILLAPA-C17 ]                 │  OPS-RISK cell)     │
│ km² not lease│     hexes labeled C01…C27               │ WILLAPA-C17         │
│              │                                         │ FORECAST  PUBLIC    │
│ Globe mode   │                                         │                     │
│ • Mode 1 2D  │                                         │ W1 oyster OPS-RISK  │
│   Mode 8     │                                         │ (Category D)        │
│   Mode 9     │                                         │ NOT FOOD-SAFETY …   │
│ Later modes  │                                         │ ELEVATED tercile…   │
│  2 Subsurface│                                         │ [90-word WAC/Vp     │
│  3 Vertical  │                                         │  headline]          │
│  …           │                                         │ AphiaID 836033      │
│  10 Food-web │                                         │ Options A–D         │
│ Unknown map  │                                         │ (why/trust/class    │
│ □ ignorance  │                                         │  are BELOW FOLD)    │
│ as the       │                                         │                     │
│ feature      │                                         │                     │
│ Depth (stub) │                                         │                     │
│ • Surface    │                                         │                     │
│   Intertidal │                                         │                     │
│   /emersion  │                                         │                     │
│ (Jump/Legend │                                         │                     │
│  BELOW FOLD) │                                         │                     │
├──────────────┴─────────────────────────────────────────┴─────────────────────┤
│ ISSUED 2026-09-18T23:00:00Z · Sep 18… | VALID … | INPUTS … | LOW (not a %)  │
│ MODEL GLOBE-PROTO-FIXTURE-2026-09-18-v0 | 27 cells; 5 DATA_GAP; 0 live ingest│
└──────────────────────────────────────────────────────────────────────────────┘
```

Yellowfin: **no control exists.**

### After

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ FishAI    [ Find Species ] Explore Globe  Evidence  Learn     Expert: Off    │
│ Sample data · not live tracking · not a harvest or food-safety notice        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│              Find a saltwater species                                        │
│              ┌─────────────────────────────────────────────┐                 │
│              │ yellowfin tuna                          Find│                 │
│              └─────────────────────────────────────────────┘                 │
│              Examples: yellowfin tuna · Pacific oyster                       │
│                                                                              │
│              The map stays striped until we have an estimate.                │
│              Stripes mean we don't know — not empty ocean.                   │
│                                                                              │
│              [ Willapa oyster working-conditions demo ]  ← Learn, not home   │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ As of — (no species yet)                                                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Yellowfin 30s (after) — no-data, honest

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ FishAI    Find Species  [Explore] Evidence  Learn              Expert: Off   │
│ Sample data · not live tracking                                              │
├──────────────────────────────────────────────┬───────────────────────────────┤
│ YELLOWFIN TUNA                               │ What's going on               │
│ Now:  no issued location                     │ Measured / guessed / future / │
│ Soon: no forecast                            │ don't know:  DON'T KNOW       │
│ Sure: none                                   │                               │
│ Depth: unknown                               │ Why: no yellowfin             │
│                                              │ measurements and no tested    │
│ Why: this product has no yellowfin           │ model in this build.          │
│ observations or tested model.                │                               │
│                                              │ Missing: everything a tuna    │
│ This is not: live tracking · a fishing map · │ forecast would need.          │
│ a count of tuna                              │                               │
│                                              │ We will not paint a smooth    │
│ ┌──────────────────────────────────────────┐ │ tuna map to look finished.    │
│ │  2D map: Pacific / world HATCH           │ │                               │
│ │  caption: No yellowfin estimate          │ │ [Learn: unknown ≠ empty]      │
│ │  legend: Measured Guessed Future Don't   │ │                               │
│ │          know  (Don't know selected)     │ │                               │
│ └──────────────────────────────────────────┘ │                               │
│ Highlight gaps: ON                           │                               │
├──────────────────────────────────────────────┴───────────────────────────────┤
│ As of 18 Sep 2026, 4:00 pm Pacific · No forecast issued                      │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Clicks:** 1 (search) + type + Enter. **≤30s.** No heatmap.

---

## 3. Evidence panel

### Before (C17 fold)

```
┌ Evidence explorer  (390×736 visible of 3802) ─────────────┐
│ Nahcotta-adjacent public water (W1 OPS-RISK example cell) │
│ WILLAPA-C17  FORECAST  PUBLIC                             │
│ W1 oyster OPS-RISK (Category D)                           │
│ NOT FOOD-SAFETY  NOT HARVEST…  AIR × TIDE — NOT SST=…     │
│ Status (fixture): ELEVATED (fixture tercile…)             │
│ [ ~90 words Category D Tier 3 WAC Vp FDA … ]              │
│ Species: Magallana gigas AphiaID 836033 · not Totten…     │
│ Target: Category D 72h operational disruption…            │
│ OPTIONS A B C D  Never harvest now                        │
│ …… viewport ends ……                                       │
│ (below) Why / trust / missing / observed vs forecast      │
│ (below) Copy cell JSON                                    │
│ (below) 1. Current estimate … 16. reduce uncertainty      │
└───────────────────────────────────────────────────────────┘
```

### After (default species or place)

```
┌ What's going on ──────────────────────────────────────────┐
│ Yellowfin tuna · no estimate                              │
│ This is: we don't know          Sure: none                │
│ Now: —   Soon: —   Depth: unknown                         │
│ Why: no measurements, no tested model.                    │
│ Not: tracking · fishing advice · a count                  │
│ [ Full scientific details ]  ← Expert on                  │
└───────────────────────────────────────────────────────────┘
```

### After (Expert on, oyster demo)

```
┌ Evidence (Expert) ────────────────────────────────────────┐
│ Place: public water near Nahcotta                         │
│ This is: forecast of farm working conditions              │
│          (a risk estimate, not a count of animals)        │
│ Sure: Low — no on-farm sensors; never tested              │
│ Depth: tide-flat in air vs water                          │
│ Why: hot air at low tide + wind/waves (demo rule)         │
│ Not: food-safety · harvest allowed · oyster GPS           │
│ Check: Washington Department of Health (link)             │
│ --- 16 fields / Category D / JSON / EMIV below fold OK ---│
└───────────────────────────────────────────────────────────┘
```

---

## 4. Explore Globe (Willapa still allowed as a demo AOI)

### Before — left rail

```
AOI (H3)
Globe mode 1 / 8 / 9
Later: 2 3 4 5 6 7 10
Unknown: Show ignorance as the feature
Depth (stub)
Layer stubs
(Jump) (Legend)   ← off screen
```

### After — Explore

```
Place: Willapa Bay, Washington (this map does not leave the bay)
Species filter: [ none — pick in Find Species ]

[ Highlight where we have no estimate ]

Depth of this estimate:
  ( ) Sea surface  ( ) Tide flats (air at low tide)
  ( ) 0–10 m down  ( ) Depth not identified

Overlays ▸  (collapsed)
Legend on map:  Measured | Guessed | Future | Don't know

Jump to a place: [ Northern entrance — measured water temp ▾ ]
```

---

## 5. Map encodings (same science, fewer words)

### Before (user-facing)

Hex fill + 7 legend items below fold + `WILLAPA-Cxx` + optional SST/habitat/`n=` + stamp + ⌘-scroll.

### After

```
        land
   ▢▢  Don't know (hatch)
   ░░  Guessed (dotted)
   ▒▒  Future (dashed)
   ██  Measured (solid) = water T or a real protocol — chip says which
   caption under map: "Solid is a measurement of [water temperature], not tuna."
```

C01 after: chip **Measured · water temperature 15.7 °C · not an animal.**

---

## 6. Time / forecast

### Before

Seven columns of `2026-09-18T23:00:00Z · Sep 18, 2026, 16:00 PDT` plus `low (category, not a %)` plus `GLOBE-PROTO-FIXTURE-2026-09-18-v0`.

### After (species with no forecast)

```
As of 18 Sep 2026, 4:00 pm Pacific     No forecast issued
```

### After (oyster demo, Expert off)

```
As of 18 Sep 2026, 4:00 pm Pacific     About the next 3 days     Sure: Low
[ Now | Next 3 days ]
```

Expert adds UTC, model id, coverage counts.

---

## 7. Mobile (after)

```
┌─────────────────────┐
│ Find  Explore  …    │
│ [ yellowfin tuna ]  │
│ NONE · no location  │
│ not tracking        │
├─────────────────────┤
│  hatch map  40vh    │
│  Measured Guessed   │
│  Future  Don't know │
├─────────────────────┤
│ Why: no model here  │
│ [ Details ]         │
└─────────────────────┘
```

Before mobile: disclaimer → entire mode catalog → 50vh map → 3800px Category D.

---

## 8. Nav map (after)

```
Find Species ──┬── no-data (yellowfin today)
               └── species with estimate (future)
Explore Globe ──── 2D MapLibre Willapa or basin; gaps toggle
Evidence ───────── short answer; Expert = 16 fields
Learn ──────────── encodings + oyster working-conditions demo
Expert toggle ──── IDs, Category D, EMIV, JSON
```

Commercial email/PDF stays **out of this map** (`artifacts/product_and_monetization/wireframe_spec.md`). Learn may say so.
