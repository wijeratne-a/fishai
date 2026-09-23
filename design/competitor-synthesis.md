# Competitor-informed design synthesis

**Project:** FishAI / Global Marine Life Intelligence  
**Path:** `/Users/wijeratne/dev/fishai/design/competitor-synthesis.md`  
**Date:** 2026-09-22  
**Scope:** Design audit and incorporation plan only. No product features, models, IDW surfaces, shapefile upload, or fake likelihood heatmaps were implemented in this pass.

**Sources inspected (local):** `globe/prototype/src/*`, `globe/prototype/index.html`, `globe/prototype/README.md`, `globe/prototype/public/fixtures/{taxa,model-cards}.json`, `GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` §32, `observatory/` (model cards, support tiers, EMIV, knowledge graph, data catalog handoff, sensitive-location policy), `audit/` (prior UX audit — partly stale relative to the current search/globe/OBIS build).

**Competitor capabilities:** Taken from the specified feature list in the task brief (OBIS / OBIS Mapper, MarLIN, OBIS-SEAMAP, MiCO, NOAA DisMAP). Official competitor sites were **not** opened for this audit.

---

## 1. Framing

This project aims past any single occurrence portal: plain-language “where now / soon / how sure / depth / why,” visual truth states, model-card gates, and ecological privacy. It must still not fake DisMAP-style biomass density or MiCO-style tracks until the underlying survey/telemetry data and a **PUBLISHED** model card that beats a baseline exist.

Honesty that ships today:

- Empty water is **don’t know**, not absence.
- Past OBIS cells are **old detections**, not current location.
- SST / chlorophyll / AIS must never be painted as animal positions.
- No food-safety, harvest, or navigation claims.
- No public GPS pin maps of rare or nesting sites.
- Current estimates and forecasts appear only behind a published model card — count in this build: **zero**.

---

## 2. Competitor strengths (borrow vs do not copy blindly)

| Source | Borrow | Do not copy blindly |
|---|---|---|
| **OBIS / OBIS Mapper** | Official occurrence API; taxon identity; coarse grids; year span; clear compiler attribution; “records ≠ animals now.” Dataset/time/region filters as **evidence tools**, not as “where they are.” | Full Darwin Core field store and native-grain pins; treating mapper filters as a live distribution product. |
| **MarLIN** | Simple global gridded presence-of-records (~5°) that updates from OBIS; Leaflet/GeoJSON tiling pattern; low cognitive load for “where has this name been reported.” | Implying the grid is current abundance or habitat quality. |
| **OBIS-SEAMAP** | Modality labels (survey, telemetry, acoustics, photo-ID, citizen science); licence discipline; thematic node into OBIS/GBIF; specialized apps for marine megafauna. | Shipping SEAMAP density models or tracks as FishAI “now” without cards; exposing sensitive elasmobranch/turtle sites. |
| **MiCO** | Multi-species toggles; each point → original study; biologically important sites; download with provenance; migratory connectivity as **study evidence**, not live GPS. | Public pin maps of nesting/stopovers; inventing connectivity without study rights. |
| **NOAA DisMAP** | Center-of-gravity and range-limit **metrics** from real trawl time series; area overlap tools; persistence / shift modules; climate-shift **narratives** tied to survey truth; clear “this is survey biomass, not tracking.” | Painting IDW biomass for taxa/regions without trawl (or equivalent) data; implying DisMAP grain (~2 km / 500 m) from SST; shapefile tools before rights + coarsening policy. |

---

## 3. Feature-by-feature table (UI spec §32 A + B)

Classifications are relative to the **current** prototype under `globe/prototype/` (Vite + MapLibre GL JS **6.10.0**, globe projection + flat toggle). Status values are exactly one of: `ALREADY_IMPLEMENTED` | `PARTIALLY_IMPLEMENTED` | `NOT_IMPLEMENTED` | `NOT_APPLICABLE`.

### A. Global layout and primary panels

| Capability | Status | Evidence |
|---|---|---|
| Left: species search | ALREADY_IMPLEMENTED | `index.html` `#species-search`; `search.ts` + `worms.ts` |
| Left: location controls | PARTIALLY_IMPLEMENTED | Willapa `#cell-select` only; no free region/place search (`index.html`, `main.ts`) |
| Left: time controls | PARTIALLY_IMPLEMENTED | Footer as-of / soon text (`index.html` `.timebar`); no time slider or horizon picker |
| Left: favorites / saved views | NOT_IMPLEMENTED | not in repo |
| Left: layer toggles (species / environment / observations / forecasts) | PARTIALLY_IMPLEMENTED | SST / habitat / sample-count overlays (`index.html`, `mapApp.ts`); no species/forecast layers as products |
| Left: simple filters (group, life stage, depth band) | PARTIALLY_IMPLEMENTED | Depth radios only; no group/life-stage filters (`index.html`) |
| Left: quick presets (surface fish, deep, spawning, nursery) | NOT_IMPLEMENTED | not in repo |
| Center: interactive globe / map | ALREADY_IMPLEMENTED | `mapApp.ts` `setProjection({ type: "globe" })`, drag/zoom/tilt, North-up |
| Center: current species distribution | NOT_IMPLEMENTED | Gate requires PUBLISHED + `hasCurrentEstimate`; fixtures show zero (`model-cards.json`, `main.ts` `speciesAnswer`) |
| Center: forecast animation | NOT_IMPLEMENTED | “No forecast issued”; oyster demo is working conditions, not animal forecast (`main.ts`, `model-cards.json`) |
| Center: depth slices / vertical transects | PARTIALLY_IMPLEMENTED | Depth band filter on Willapa cells; no column / transect viz (`mapApp.ts`, `index.html`) |
| Center: environmental overlays (when toggled) | PARTIALLY_IMPLEMENTED | Fixture SST + habitat dots only; not global ocean layers (`mapApp.ts`) |
| Center: 2D map fallback | ALREADY_IMPLEMENTED | Flat/mercator toggle + session preference (`mapApp.ts`, `#flat-map`) |
| Right: plain-English answer | ALREADY_IMPLEMENTED | Answer strip Where now / Soon / How sure / Depth / Why / This is not (`answer.ts`) |
| Right: confidence indicator | PARTIALLY_IMPLEMENTED | “How sure” field exists; usually “None” outside Willapa demo (`answer.ts`, `main.ts`) |
| Right: “Why here?” explanation | PARTIALLY_IMPLEMENTED | Why line + cell honesty answers; not ocean-driver top-N for published models (`answer.ts`, `evidence.ts`) |
| Right: evidence panel | PARTIALLY_IMPLEMENTED | Past-report text + Willapa cell evidence; no modality filters/export (`evidence.ts`, `main.ts`) |
| Right: model card link | PARTIALLY_IMPLEMENTED | Gate JSON exists; no user-facing card page/link (`model-cards.json`; Learn is FAQ-style only) |
| Right: Expert Mode advanced details | ALREADY_IMPLEMENTED | Expert toggle → 16 provenance fields (`evidence.ts` `FIELD_TITLES`) |
| Top: tool description / brand | PARTIALLY_IMPLEMENTED | “FishAI” + banner; not labeled “Marine Life Globe” as primary product name (`index.html`) |
| Top: global search (species, place, coordinates) | PARTIALLY_IMPLEMENTED | Species only; no place/coordinate search (`search.ts`, `index.html`) |
| Top: mode selector (Find / Explore / Evidence / Learn) | ALREADY_IMPLEMENTED | Four nav buttons (`index.html`, `main.ts` `setNav`) |
| Top: Settings and Help | NOT_IMPLEMENTED | Expert toggle only; no Settings/Help (`index.html`) |
| Bottom: coordinates | NOT_IMPLEMENTED | not in repo |
| Bottom: depth band readout | PARTIALLY_IMPLEMENTED | Depth in answer strip + depth radios; not a dedicated status-bar depth chip |
| Bottom: time / forecast horizon | PARTIALLY_IMPLEMENTED | Footer As of / Soon (`index.html`); Soon usually “No forecast issued” |
| Bottom: data freshness | PARTIALLY_IMPLEMENTED | As-of from `meta.json` for Willapa; OBIS year span in past-report copy |
| Bottom: imagery / model loading status | PARTIALLY_IMPLEMENTED | Live region + stamps (`#map-status`, `#map-stamp`); no progressive tile-loading chrome |
| Plain-language primary labels | ALREADY_IMPLEMENTED | Measured / Guessed / Future / Don’t know (`legend.ts`, Learn copy) |

### B. First-run experience and core flow

| Capability | Status | Evidence |
|---|---|---|
| 1. Search for a species | ALREADY_IMPLEMENTED | Local catalog + WoRMS; unknown → “No matching name.” (`search.ts`, `main.ts`) |
| 2. Choose rough region or default | PARTIALLY_IMPLEMENTED | Default world view; Willapa only via Learn oyster demo; no region picker (`mapApp.ts`, `main.ts`) |
| 3. See where likely now | NOT_IMPLEMENTED | Always “No issued location” for non-demo taxa (`main.ts` `speciesAnswer`) |
| 4. See simple near-future forecast | NOT_IMPLEMENTED | “No forecast issued”; oyster soon-line is farm working conditions (`main.ts`) |
| 5. Understand confidence and depth | PARTIALLY_IMPLEMENTED | Fields present; depth is fixture filter / “unknown”; confidence usually None |
| 6. Understand why the system thinks this | PARTIALLY_IMPLEMENTED | Honest “no model / past reports only” copy; not model drivers for live estimates |
| 7. Optionally explore detailed evidence | PARTIALLY_IMPLEMENTED | Evidence panel + Expert 16 fields; OBIS past-report summary only |
| First screen: featured species in featured region | NOT_IMPLEMENTED | Cold load empty answer + world globe; no featured species (`main.ts` boot) |
| First screen: “Today, [Species] is most likely…” | NOT_IMPLEMENTED | Would require published current estimate (zero) |
| First screen: legend More / Less likely / Unknown / Observed | PARTIALLY_IMPLEMENTED | Measured / Guessed / Future / Don’t know (+ Past reports); not likelihood scale (`legend.ts`) |
| Time slider: Now / Tomorrow / Next 7 days | NOT_IMPLEMENTED | not in repo |
| Depth selector with few meaningful options | ALREADY_IMPLEMENTED | Surface / Tide flat / 0–10 m / Depth unknown (`index.html`) |
| Guided tour overlay (5 steps) | NOT_IMPLEMENTED | not in repo |
| Advanced controls deferred until after basic answer | PARTIALLY_IMPLEMENTED | Expert + Explore rail hidden patterns; Find is default but Explore overlays exist once opened |

### Competitor-facing capabilities (for gap planning; not §32 A/B)

| Capability | Status | Evidence |
|---|---|---|
| OBIS occurrence count + year span | ALREADY_IMPLEMENTED | `obis.ts` |
| OBIS coarsened ~1° grid, max 80, hide n&lt;3 | ALREADY_IMPLEMENTED | `obis.ts` |
| Withhold listed/sensitive taxa (e.g. white shark 105838) | ALREADY_IMPLEMENTED | `WITHHOLD_APHIA` in `obis.ts` |
| Past reports labeled as old detections | ALREADY_IMPLEMENTED | `evidence.ts` `renderPastReportsHtml`; stamps in `main.ts` |
| OBIS compiler license note | ALREADY_IMPLEMENTED | `obis.ts` `licenseNote` |
| OBIS Mapper-style taxon/time/dataset/region filters | NOT_IMPLEMENTED | not in repo |
| Darwin Core field store | NOT_IMPLEMENTED | not in repo |
| MarLIN-style ~5° auto-updating OBIS tiles | NOT_IMPLEMENTED | Client fetches 1° GeoJSON per search only (`obis.ts`) |
| Multi-species overlay | NOT_IMPLEMENTED | Single selected taxon (`AppState`) |
| Telemetry tracks | NOT_IMPLEMENTED | not in repo (`observatory/telemetry_registry/` is design-only) |
| Study / paper links per point (MiCO-style) | NOT_IMPLEMENTED | Source is OBIS compiler string only |
| Biologically important sites layer | NOT_IMPLEMENTED | not in repo |
| SEAMAP modality filters / thematic node | NOT_IMPLEMENTED | not in repo |
| DisMAP IDW biomass surfaces | NOT_IMPLEMENTED | not in repo (and must not fake from SST) |
| Center of gravity / range limits / richness / area overlap | NOT_IMPLEMENTED | not in repo |
| Draw area / predefined areas / shapefile upload | NOT_IMPLEMENTED | not in repo |
| Species Persistence / shift modules / climate narrative | NOT_IMPLEMENTED | not in repo |
| Published current estimates count | NOT_IMPLEMENTED | `model-cards.json`: Magallana gigas `NOT_PUBLISHED`; zero published |
| Willapa visual truth states (measured / guessed / future / don’t know) | ALREADY_IMPLEMENTED | fixtures + `mapApp.ts` + `legend.ts` |
| Oyster working-conditions demo from Learn only | ALREADY_IMPLEMENTED | `#learn-oyster` → `openOysterDemo` (`main.ts`) |

---

## 4. Gap analysis by competitor

### OBIS / OBIS Mapper

**Have:** Live official API past-report path with coarsening, rate limit, withhold list, and honest copy.  
**Missing:** Dataset / time / region filters; download of filtered Darwin Core; multi-layer mapper UX; dataset-level licence display beyond the compiler note.  
**Risk if copied naively:** Users read filtered occurrences as “where the fish are now.” Keep the existing stamp language and never promote native grain for withheld taxa.

### MarLIN

**Have:** Coarse global presence-of-records idea (1° cells after search).  
**Missing:** Persistent tiled ~5° (or similar) layer that refreshes with OBIS without a one-shot GeoJSON cap; shared tile cache; MarLIN-like simplicity for “global name footprint.”  
**Risk:** A prettier global grid still must say “past reports,” not “range” or “abundance.”

### OBIS-SEAMAP

**Have:** Observatory docs for modalities and sensitive locations; withhold pattern for white shark.  
**Missing:** UI for survey / telemetry / acoustics / photo-ID / citizen science; density-model projects; specialized megafauna apps; thematic node packaging into OBIS/GBIF.  
**Risk:** Telemetry and photo-ID without delay/coarsen can become harassment maps. Bind to `observatory/sensitive_location_policy.md`.

### MiCO

**Have:** Provenance mindset (16 expert fields; OBIS source note).  
**Missing:** Multi-species toggles; study-linked points; biologically important sites; download packages with per-study provenance.  
**Risk:** Important-site pins for nesting/stopovers are ecology-sensitive — coarsen, delay, or omit publicly.

### NOAA DisMAP

**Have:** Model-card / support-tier culture that forbids abundance from SST; honesty language for survey-derived vs observed.  
**Missing:** Trawl-based IDW surfaces; lat/depth COG; range limits; richness; area overlap (draw / predefined / shapefile); Persistence / Single Species Shift / Regional Shift Summary; climate-shift narratives.  
**Risk:** Building DisMAP-looking heatmaps without DisMAP-class inputs. Do not recommend temperature-painted “biomass.” Metrics and narratives only where survey time series + published cards exist.

### Prior UX audit (`audit/`)

The Sep 2026 audit correctly demanded Find Species first and a honest yellowfin no-data path. Much of that **chrome** is now in the prototype. The audit’s claim that the app is “Willapa-only with no search” is **stale**. Remaining P0 product gap is unchanged scientifically: **no published where-now / soon maps.**

---

## 5. Incorporation plan (beneficial NOT / PARTIAL features)

Phases are incremental and honesty-first. **Do not** recommend painting current/forecast animal positions from temperature. **Do not** recommend public pin maps of rare or nesting sites.

### Phase 0 — Evidence honesty upgrades (prototype UI + thin API)

| Feature | Host | Data / models | UI change | Privacy / ecology |
|---|---|---|---|---|
| OBIS Mapper-lite filters (year range, optional region bbox) | `globe/prototype` (`obis.ts`, Evidence mode) | Official OBIS query params only; still coarsen ≥1°, n≥3, max cells | Filter strip on Evidence; stamp “past reports” | Keep `WITHHOLD_APHIA`; no native pins |
| MarLIN-style coarser overview grid (e.g. 5°) | Prototype + later tile cache | OBIS grid endpoints or pre-agg tiles | Zoom-dependent past-report layer | Same withhold + license note |
| Per-cell / panel link to OBIS taxon page + year span | Prototype | Existing summary fields | “Open compiled records” link | Attribution; no re-host of restricted sets |
| Model card stub page (NOT_PUBLISHED chrome) | Prototype Learn + `model-cards.json` | Existing gate JSON + `observatory/model_cards/` | Link from answer / Learn | Never show live scores until PUBLISHED |

### Phase 1 — Observatory evidence enrichment (pipeline first)

| Feature | Host | Data / models | UI change | Privacy / ecology |
|---|---|---|---|---|
| Study / dataset provenance edges | `observatory/knowledge_graph` + catalog | Licence-filtered OBIS/GBIF metadata; paper DOIs where open | Evidence list: “from study X” | PUBLIC projection only |
| SEAMAP modality tags on records | Observatory modality catalog → fixture/API | Partner/public modality fields | Filter chips: survey / acoustic / … | Telemetry delayed/coarsened; NEVER_PUBLISH sites |
| Biologically important sites (MiCO-like) | Observatory + later UI | Curated polygons with rights review | Toggle “important areas (literature)” | No nesting GPS; official/coarse units only |
| Multi-species compare (max 2–3) | Prototype later | Same past-report path per taxon | Toggle list; shared legend “past reports” | Cap overlays; withhold list per taxon |

### Phase 2 — DisMAP-class analytics only where surveys exist

| Feature | Host | Data / models | UI change | Privacy / ecology |
|---|---|---|---|---|
| Center of gravity / range limits | Observatory metrics service | Bottom-trawl (or equivalent) time series with rights | Expert charts + map markers labeled “survey metric” | Not live tracking; not harvest advice |
| Persistence / shift modules | Observatory + Learn narrative | Same survey stack + published card | Persistence legend + decade comparison | Narrative must cite survey, not SST alone |
| Area overlap (draw / predefined) | Prototype map tools | User polygon client-side vs survey COG/range | Draw tools; predefined EEZ/stat areas | Shapefile upload **later**, after malware/rights review |
| Climate-shift story module | Learn mode | Peer-reviewed / agency narrative + survey metrics | Story panel (e.g. black sea bass pattern) | No fake forecast animation from climate alone |

### Phase 3 — Product likelihood / forecast (only after cards)

| Feature | Host | Data / models | UI change | Privacy / ecology |
|---|---|---|---|---|
| Current likelihood map | Prototype Find mode | PUBLISHED card beating baseline; support tier ≥ T3 | Legend becomes More/Less likely + Unknown + Observed | Coarsen sensitive taxa; unknown ≠ empty |
| Short-horizon forecast + time slider | Prototype | PUBLISHED forecast card | Now / +1d / +7d slider | No animal GPS; ops demos stay Category D language |
| Guided tour | Prototype | None | 5-step overlay after first search | Tour must not promise live tracking |

### Explicit non-goals for next builds

- IDW biomass from SST/chlorophyll/AIS.
- Public rare-species or nesting pin maps.
- Shapefile upload before security + licence review.
- Claiming DisMAP density or MiCO tracks without those data and cards.

---

## 6. Top 20 incorporation actions

Ordered by user value under honesty constraints (safer order preferred over “looks like DisMAP”).

| # | What | Where | Needs | Must not claim |
|---|---|---|---|---|
| 1 | Year + optional bbox filters on past reports | `globe/prototype/src/obis.ts`, Evidence UI | OBIS official query params | Current location or abundance |
| 2 | Zoom-dependent coarser MarLIN-like overview grid | `obis.ts` + `mapApp.ts` | OBIS grid or pre-agg tiles | Live distribution |
| 3 | Click past-report cell → count, years, compiler, open OBIS | `evidence.ts`, `mapApp.ts` | Existing grid properties | “Animals are here now” |
| 4 | Public model-card page with NOT_PUBLISHED chrome | Learn + `model-cards.json` | Card template/schema in `observatory/model_cards/` | Issued scores before PUBLISHED |
| 5 | Dataset / licence rollup for drawn cells | Observatory catalog → Evidence | OBIS dataset metadata (licence-safe) | Homogeneous open licence for all cells |
| 6 | Place / coordinate / named-region search | `search.ts`, map fly-to | Geocoder or curated regions | That the region has a species estimate |
| 7 | Guided 5-step tour after first successful search | `index.html` + small tour module | Copy only | That forecasts exist |
| 8 | Multi-species past-report toggles (≤3) | `AppState`, `mapApp.ts` | Per-taxon OBIS grids | Overlaid “hotspot competition” as ecology truth |
| 9 | Modality filter chips (survey / opportunistic / …) | Evidence mode | Modality fields from catalog / SEAMAP-like tags | Completeness of global modalities |
| 10 | Study / DOI links on evidence rows (MiCO pattern) | Evidence + knowledge graph | Open citations + rights | Proprietary track replay |
| 11 | Important-sites layer (coarse, literature) | Observatory → Explore overlay | Curated polygons post-review | Nesting/trap GPS |
| 12 | Status bar: cursor lon/lat + depth band + freshness | `index.html` footer / map events | Map move events | Navigation safety |
| 13 | Favorites / saved views (species + camera) | Prototype localStorage | None initially | Server sync of private AOIs |
| 14 | Persistence legend for taxa with survey time series | Learn + Expert | Trawl (or equiv.) + published metrics | Persistence from temperature alone |
| 15 | Center-of-gravity + range-limit readout | Expert panel | DisMAP-class or partner survey series | Live animal centroid |
| 16 | Draw / predefined area overlap vs survey metrics | Map tools later | Survey metrics polygons | Harvest authorization inside polygon |
| 17 | Climate-shift narrative module (survey-backed stories) | Learn mode | Agency/peer-reviewed narratives + metrics | Forecast playback from climate essay alone |
| 18 | SEAMAP-informed megafauna evidence mode | Evidence + withhold rules | SEAMAP-class public products + licences | Public shark/turtle pins at native grain |
| 19 | First published current-estimate map (one taxon × region) | Find mode + observatory factory | PUBLISHED card beating baseline | Habitat or SST as presence |
| 20 | Forecast time slider only behind that published card | Find mode | PUBLISHED forecast + validation | Ops demo language for wild GPS |

---

## 7. What a non-expert can do today vs success criteria

### Already possible today

- Search a saltwater name (local catalog or modest WoRMS lookup); see “No matching name.” when unknown.
- Read a plain answer strip: Where now / Soon / How sure / Depth / Why / This is not.
- Spin a MapLibre 6.10 **3D globe**, toggle flat map, tilt, North-up.
- For many taxa: see coarse OBIS **past reports** with counts, year span, and “not where they are now.”
- For white shark and similar: see locations **withheld**.
- Open Learn → Pacific oyster **working-conditions** demo (air/tide/waves — not harvest or oyster GPS).
- Toggle Expert for 16 provenance fields on Willapa cells.
- Understand Measured / Guessed / Future / Don’t know on the Willapa fixture.

### Success criteria still unmet (§32 + honesty gates)

- “Today, [species] is most likely in these areas” from a **published** current estimate — **0** such products.
- Near-term forecast animation / time slider — **0** published forecasts.
- Featured first-run species+region with likelihood legend (More / Less likely).
- Region picker, favorites, Settings/Help, guided tour.
- OBIS Mapper-depth filters, Darwin Core store, multi-species ecology overlays, telemetry, study-linked points, DisMAP metrics/surfaces, shapefile tools, persistence/climate modules, SEAMAP thematic node.
- Model card UX that non-experts can open and understand for a live estimate.

**Bottom line:** The prototype now passes an honest “search → no fake map” path. It does not yet pass “Google Earth for where marine life is likely now and soon,” and must not close that gap by painting temperature or inventing tracks.

---

## Appendix — Verified product facts (2026-09-22)

| Fact | Verification |
|---|---|
| Vite + MapLibre 6.10 globe + flat toggle | `package.json` 6.10.0; `mapApp.ts` projection globe/mercator |
| Search: local + WoRMS; miss → “No matching name.” | `search.ts`, `worms.ts`, `main.ts` |
| Answer strip fields | `answer.ts` |
| OBIS: count, years, ~1° grid, max 80, n&lt;3 hide, withhold 105838 | `obis.ts` |
| Magallana gigas card NOT_PUBLISHED; demo from Learn | `model-cards.json`, `#learn-oyster` |
| Published current + forecast count | zero (`model-cards.json` note) |
| Expert 16 fields | `evidence.ts` `FIELD_TITLES` |
| Prior `audit/` Willapa-only diagnosis | Stale vs current search/OBIS/globe build |
