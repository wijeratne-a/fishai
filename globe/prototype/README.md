# FishAI — Find a saltwater species

**Path:** `/Users/wijeratne/dev/fishai/globe/prototype/`  
**Stack:** Vite 6.4.3 + TypeScript 5.9.3 + MapLibre GL JS **6.10.0** (globe projection; no Cesium; no Google tiles).

**Research problem:** [`../../RESEARCH_PROBLEM.md`](../../RESEARCH_PROBLEM.md)  
**First species slice:** Atlantic goliath grouper — [`../../species/goliath-grouper/`](../../species/goliath-grouper/)

Search a fish or crustacean name. Most species return **no current location** and **no forecast**. Some names show coarse **past reports** from OBIS. Goliath grouper is the first named slice: ecology copy and coarsened history only — **not** a live location. The Willapa oyster screen is a **working-conditions demo** opened from Learn.

This is **not** live tracking. The system does **not** know exactly where goliath grouper (or any species) are at every moment.

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

## Honesty rules in this build

- Current location, occurrence probability, abundance, movement, and forecasts appear only when a model card is `PUBLISHED` and a baseline was beaten. That count is **zero**.
- Habitat is **favorable conditions — not confirmed presence**.
- Past OBIS cells are a **historical pattern**, ~1° / 100 km, `n ≥ 3`, max 80 cells.
- Goliath aggregation wrecks and nursery pins are **not** drawn. A 1° grid may appear with a coarsening note.
- White shark past-report locations stay **withheld**.
- The oyster demo is air, tide, sun, and waves — not oyster GPS.
- Empty water is **unknown**, not absence.

---

## Status

Browser results for the 2026-09-23 integration are in [`VERIFICATION.md`](VERIFICATION.md). That file is the only current pass/fail record.

| Bucket | What |
|---|---|
| **Designed only** | 4D occupancy, occupancy-with-effort, VAST, movement state-space, observation planner execution — see `species/goliath-grouper/` |
| **Blocked on data or licensing** | Rights-approved ingest; ATN/telemetry; survey microdata; GEBCO terrain tiles |
| **Blocked on scientific validation** | Current-estimate and forecast layers; spawning-aggregation layer; any published card |
| **Not started** | Training, skill scores, as-of replay implementation, named reviewer/publisher |

---

## Files

```
prototype/
  package.json
  index.html
  src/                 UI + MapLibre + WoRMS/OBIS clients
  public/fixtures/     Willapa GeoJSON + taxa + model-card gate
  docs/                camera, layers, publication decision
  scripts/generate-fixtures.mjs
```
