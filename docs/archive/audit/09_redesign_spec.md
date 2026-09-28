# Redesign spec — human-usable FishAI (do not implement in this audit)

**Constraint:** Stay scientifically honest. No live tuna heatmap. 2D MapLibre default. Expert Mode for 16 fields / EMIV / Category D / cell IDs.

**Success:** A normal person searches **yellowfin tuna** and in **30s** understands where / measured-vs-forecast / confidence / depth / why / limits — even when the honest answer is “we don’t know.”

---

## 1. Navigation (≤4 modes)

Persistent top nav, text not numbers:

| Nav | Job | Today’s pieces |
|---|---|---|
| **Find Species** | Search + species answer | **New** (home) |
| **Explore Globe** | 2D map, place, layers, gaps | Mode 1 map + unknown toggle + overlays |
| **Evidence** | Why this pixel/species | Right panel; Mode 8 sensors |
| **Learn** | Teach encodings + this demo vs tuna | New; oyster OPS-RISK lives here |

No Mode 2–7, 10 on this bar. No “Globe mode” fieldset.

**Expert Mode** is a **toggle** (header, last), not a fifth nav. When on: cell IDs, Category D, 16 fields, JSON, model version, EMIV IDs, H3 grain, publish class, later research modes as disabled list.

---

## 2. Design tokens

Use the existing paper/ink palette; stop using it to look like a 19th-century instrument manual.

| Token | Value | Use |
|---|---|---|
| `--paper` | `#F7F1E4` | Page |
| `--ink` | `#1C1710` | Text |
| `--muted` | `#5C5346` | Secondary; **not** for primary answers |
| `--panel` | `#FFFAF0` | Panels |
| `--banner` | `#24180C` | Thin status bar only |
| `--signal` | `#FFD166` | Sample-data chip, not 4px screaming border everywhere |
| `--focus` | `#005F73` | **Actual** `:focus-visible` rings (3px) |
| `--warn` | `#9B2226` | Rare; harvest/food-safety “not this” |
| `--measured` | `#0072B2` | Measured |
| `--guessed` | `#E69F00` | Guessed / model |
| `--future` | `#56B4E9` | Forecast |
| `--habitat` | `#009E73` | Habitat only |
| `--unknown` | hatch grey | Don’t know |
| `--font-ui` | system-ui / Segoe UI | **Default UI** (drop Palatino for chrome) |
| `--font-size` | 16px body; 14px meta; **no 10px timebar** | |
| `--space` | 8px grid | Answer strip padding 16px |
| `--radius` | 8px chips | |
| `--target` | 44px min tap | Search, nav, primary buttons |

**Legend default (4):** Measured (solid) · Guessed (dotted) · Future (dashed) · Don’t know (hatch).  
Gap vs restricted vs habitat stay in Expert or Learn.

---

## 3. Home — Find Species

**First 5 seconds:** search is the only primary control. Map may sit dimmed behind or to the side showing **world/basin hatch**, not Willapa C17.

```
[ FishAI ]  Find Species | Explore | Evidence | Learn     [ Expert: off ]

Find a saltwater species
[ Search: yellowfin tuna                    ] [Find]

This product does not track animals live.
It says what was measured, what was guessed, what is forecast, and what is unknown.
```

Placeholder examples: yellowfin tuna · Pacific oyster · (species we truly have).  
No AOI lecture. No Mode 8.

**If the user does nothing:** do **not** auto-open OPS-RISK. Optional quiet link: “See the Willapa oyster working-conditions demo” → Learn.

---

## 4. Species detail (yellowfin and any taxon)

Always the same skeleton. Quantity class is named; never “life.”

### Answer strip (always above the fold; also `aria-live` composed sentence)

| Field | Yellowfin in *this* build (honest) | Future if a real model exists |
|---|---|---|
| **Species** | Yellowfin tuna | same |
| **Where now** | No issued location | Named coarsened cells / basins with truth state |
| **Soon** | No forecast issued | Dashed cells + valid window |
| **How sure** | None | High/Medium/Low/None + one reason |
| **Depth** | Unknown | Named band or unknown |
| **Why** | No observations or evaluated model for yellowfin in this product | One sentence drivers as **inputs** |
| **This is not** | Live tracking, a fishing map, a count of tuna | same + not AIS-as-abundance |

Map for yellowfin now: **global or Pacific hatch** labeled “No yellowfin estimate,” **or** a static locator “This demo map is Willapa Bay, Washington (oysters), not tuna habitat.” **Forbidden:** purple occupancy, SST-as-tuna, AIS density, swimming sprites, climatology fill without a climatology label.

If later a T3 habitat layer exists: teal **habitat only**, caption “conditions that often suit yellowfin — not where they are.” Pattern = guessed or habitat, never solid observation.

### Species page layout (desktop)

Left: answer strip + short limits.  
Center: 2D map.  
Right: Evidence (short). Expert opens 16 fields.

### Species page (oyster, if user chose Learn demo)

Where now: planted animals **not counted**.  
Soon: **farm working conditions** next 72h (plain words), confidence Low.  
Depth: tide-flat in air vs water.  
Why: hot air at low tide + wind/waves (demo rule).  
This is not: food-safety, harvest OK, animal GPS.  
Category D / W1 / Aphia / WAC: Expert only.

---

## 5. Map spec (Explore Globe)

- **Engine:** MapLibre 2D (already). `showCompass: false` for v1 AOI.
- **Default zoom:** named place, not hex IDs.
- **Labels:** place names at low zoom; cell IDs only Expert + high zoom.
- **Click:** selects a place; if no species chosen, prompt “This place is Willapa public water. Choose a species to ask where/when.”
- **Bounds:** if still Willapa-only, chrome must say “This map is Willapa Bay only.”
- **Unknown toggle:** “Highlight where we have no estimate” — default **on** for species with no data.
- **Overlays:** collapsed “Water temperature / Habitat type / Sample counts” with persistent caption; never replace truth outlines.
- **Legend:** on the map card, 4 items, always visible.
- **Stamp:** `SAMPLE DATA · not a boat chart · not live tracking` (one).

Do not add Cesium, volume clouds, or time-lapse of animals.

---

## 6. Evidence panel (default vs Expert)

### Default (≤6 lines + links)

1. What this number **is** (one phrase)  
2. Measured / guessed / future / don’t know  
3. How sure + **because** (one clause)  
4. What’s missing (three bullets max)  
5. Official pages if harvest/legal (oyster)  
6. “See full details” → Expert  

### Expert (today’s panel, renamed)

- 16 fields (`evidence_explorer.md`)  
- Category A–E, tiers, EMIV IDs, model version, JSON copy  
- C17 OPS options A–D  
- Publish class, H3 grain  

Honesty questions stay **above** the 16 fields even in Expert (fix the C17 fold bug).

---

## 7. No-data state (first-class product)

Trigger: search taxon with no issued estimate (yellowfin today).

Copy:

> **Yellowfin tuna** — we cannot say where they are.  
> **Now:** no location. **Soon:** no forecast. **Sure:** none. **Depth:** unknown.  
> **Why:** this build has no yellowfin measurements and no tested yellowfin model.  
> The map is striped on purpose. Stripes are not empty ocean.  
> We will not draw a smooth tuna map to look finished.

CTA: Learn why unknown is the answer · See Willapa oyster demo · Expert: cell JSON none.

Do **not** reuse `#evidence-empty` “16 provenance fields.”

---

## 8. Low-confidence state

When an estimate **is** issued at Low (C17-like):

- Chip **Low confidence** next to the answer, not only in a footer.  
- Reasons as words: “No on-site sensors. Never tested against real outcomes.”  
- Hide `FRESH:ok` codes unless Expert.  
- Options (oyster) labeled consider-only.  
- Do not thicken the hex as if it were the hero fish cell.

---

## 9. Forecast UI

- Default: **Now | Next 24h | Next 72h** segmented control if a forecast exists.  
- If none: control disabled, “No forecast issued.”  
- Clock: **one** local time (“As of 4:00 pm Pacific, 18 Sep 2026”). UTC in Expert.  
- Forecast cells: dashed + chip **Future** on the answer strip.  
- No playback. No eased mid-frames.  
- Footer does not show a forecast clock on a Don’t-know species.

---

## 10. Mobile

1. Sticky search or sticky answer strip (does-not-mean one line).  
2. Map 40–50% viewport.  
3. Drawer: layers, depth, expert.  
4. Nav: 4 icons + labels.  
5. 16 fields: accordion in Expert only.  
6. Breakpoint: one column **before** the rail dumps Mode 10 on top of the map (fix `1100px` stack order).

---

## 11. Expert Mode (explicit)

**Off (default):** Find Species home, 4-legend, plain clocks, no cell IDs, no Category D letter, no EMIV, no JSON, no later-modes list.

**On:** today’s scientific instrument: 16 fields, `WILLAPA-C17`, Category D, model `GLOBE-PROTO-…`, publish class, station IDs, copy JSON, optional Mode 8 sensors, unknown vs data-gap split.

The current GUI is Expert Mode with the toggle removed. **Ship the toggle.**

---

## 12. Copy principles (binding)

1. One positive sentence of what this **is**, then one of what it is **not**.  
2. Category D → “This is a risk estimate, not a count of animals.”  
3. OPS-RISK → “Farm working conditions.”  
4. WILLAPA-C17 → place name; id in Expert.  
5. Emersion → “in the air at low tide.”  
6. Fixture → “sample / demo data” once per view, not every sentence.  
7. Never lead with OBIS/GBIF/AIS.

Full string table: `04_language_and_jargon_audit.csv`.

---

## 13. What we refuse (still)

- Red/yellow “hotspot” tuna  
- AIS as abundance  
- Filling hatch with climatology to look global  
- Green = harvest OK  
- Autoplay schools of fish  
- Shipping all 10 globe modes  
- Putting EMIV catalog on Find Species
