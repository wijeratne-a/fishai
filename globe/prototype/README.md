# FishAI — Find a saltwater species

**Path:** `/Users/wijeratne/dev/fishai/globe/prototype/`  
**Stack:** Vite 6.4.3 + TypeScript 5.9.3 + MapLibre GL JS 6.10.0 (2D map; no Cesium).

Search a fish or crustacean name. Most species return **no current location** and **no forecast**. Some names show coarse **past reports** from OBIS. The Willapa oyster screen is a **working-conditions demo** opened from Learn — not harvest advice and not animal GPS.

This is **not** live tracking.

---

## How to run

```bash
cd /Users/wijeratne/dev/fishai/globe/prototype
npm install
npm run dev
```

Open the URL Vite prints (default `http://localhost:5173`).

| Script | What it does |
|---|---|
| `npm run dev` | Local Vite server |
| `npm run build` | Typecheck + production bundle in `dist/` |
| `npm run preview` | Serve the production bundle |
| `npm run generate-fixtures` | Recreate synthetic GeoJSON/JSON under `public/fixtures/` |

No backend. No API keys. No `.env`. Willapa cells are static fixtures. Species names use a local catalog plus modest WoRMS lookups. Past-report cells use the official OBIS API, coarsened.

---

## What the first screen does

- One-line banner: sample data, not live tracking, not harvest or food-safety advice.
- Four destinations: Find Species, Explore Globe, Evidence, Learn. Expert is a toggle.
- Cold load: “Search a species or pick a place.” No Category D cell, no AphiaID wall, no later-modes list.
- Answer strip always above the fold: Where now, Soon, How sure, Depth, Why, This is not.
- Map legend: Measured, Guessed, Future, Don’t know.

Typing **yellowfin tuna** should say there is no issued location and no forecast. Stripes mean we do not know, not that the ocean is empty. If OBIS returns records, they draw as coarse past reports with a year span and license note.

The **Pacific oyster** working-conditions demo opens from **Learn** only.

---

## Honesty rules in this build

- Current location and forecasts appear only when a model card is `PUBLISHED` and a baseline was beaten. That count is **zero**.
- The oyster demo is air, tide, sun, and waves — not sea-surface temperature as body temperature, not harvest legality.
- Satellites, chlorophyll, and vessel traffic are never painted as animal positions.
- Empty water stays “not enough data,” not absence.
- Sensitive taxa (for example white shark) are withheld from the public past-report grid.
- Cells with fewer than 3 records are hidden. At most 80 coarse cells are drawn.

---

## What is fixture vs live lookup

| Item | Status |
|---|---|
| Willapa cell colors, ranks, SST, habitat class, observation `n` | Synthetic fixtures generated 2026-09-18 |
| In-water stations | Fictional sensors, not animals |
| Species catalog | Local WoRMS-verified names; unknown spellings resolve via the official WoRMS REST service |
| Past-report grid | Official OBIS occurrence + 1° grid, rate-limited |
| Model cards | Only Magallana gigas draft, `NOT_PUBLISHED` |

---

## Files

```
prototype/
  package.json
  index.html
  src/                 UI + MapLibre + WoRMS/OBIS clients
  public/fixtures/     Willapa GeoJSON + taxa + model-card gate
  scripts/generate-fixtures.mjs
```
