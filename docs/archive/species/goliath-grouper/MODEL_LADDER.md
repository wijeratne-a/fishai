# Model ladder — Atlantic goliath grouper

**No model is fitted in this pass** except a transparent **historical occurrence-density summary** from the official OBIS count API. That summary is **not** current presence and has **no skill score**.

Advanced names (VAST, ISDM, state-space) are **rungs**, not trophies. Do not claim a fitted VAST model.

---

## Rungs

| Step | What it is | Status |
|---|---|---|
| **0. Range envelope** | Published geographic range as text (NOAA / FishBase / WoRMS). Not a probability. | **IMPLEMENTED** as prose in `ECOLOGY_PROFILE.md`. Not a globe layer. |
| **1. Seasonal frequency** | Jul–Sep spawning window vs rest of year, from fetched ecology pages | **IMPLEMENTED** as text only. Not a calendar heatmap. |
| **2. Habitat-only suitability** | Mangrove vs 0–50 m structure as covariates | **NOT STARTED.** Must stay labeled **not presence** if ever drawn. |
| **3. Historical occurrence density** | Coarse compiled OBIS counts | **IMPLEMENTED (summary only).** See below. Globe may show a **1° past-report grid** at runtime, labeled historical. |
| **4. Occupancy / SDM with effort** | Detection vs non-detection given survey effort. This is the next milestone: **Prediction MVP — Florida Keys Goliath Grouper Detection Nowcast**. | **BLOCKED** — no rights-cleared extract and no effort-aware non-detections ingested. |
| **5. Dynamic SDM / ISDM** | Time-varying occupancy; integrated sources | **NOT STARTED.** |
| **6. VAST-like spatiotemporal index** | Relative abundance index with spatial correlation | **NOT STARTED.** Do not claim a fitted VAST model. |
| **7. Movement / aggregation state-space** | Home range + seasonal aggregation state | **BLOCKED** on telemetry rights and sensitive-site policy. |
| **8. Advanced / foundation models** | Allowed only if they **beat baselines** on spatial and temporal holdout | **NOT STARTED.** Must not drive globe layers until they do. |

---

## Historical occurrence density (not current presence)

**Query (official, modest, 2026-09-22):**

- `GET https://api.obis.org/v3/occurrence?scientificname=Epinephelus%20itajara&size=0` → `total` **332,628**
- `GET https://api.obis.org/v3/statistics/years?scientificname=Epinephelus%20itajara` → years **1935–2026**

**Label:** **HISTORICAL OCCURRENCE DENSITY** (compiled rows in OBIS).  

**This is not:**
- a population count
- a current-location product
- a forecast
- a validated occupancy model

**Composition warning:** most compiled rows fall in **2010–2016** (e.g. 121,869 in 2011 on the years endpoint). That pattern is **ingest/effort**, not an inferred boom-and-bust of animals. No CPUE was computed.

**Skill scores:** **none.** None were invented.

**Globe use:** if the existing coarsener allows (`n ≥ 3`, max 80 cells, ~1°), draw as **past reports / historical pattern**. Zooming in does not sharpen biology. No wreck pins.

---

## What would be required to climb the ladder

Effort-aware surveys, rights-approved ingest, spatial-block and time-forward holdout, a beaten baseline, calibration, sensitive-site review, and a named human publisher. See [`VALIDATION.md`](VALIDATION.md) and [`PUBLICATION_DECISION.md`](PUBLICATION_DECISION.md).
