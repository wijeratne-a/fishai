# Biological variables — visual encoding

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/biological_variables_visual.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** How to **show** biological structure when scientifically valid. Most variables are **later**. W1 uses a small subset (emersion, extremes as ops-stress, human workability).

All outputs distinguish:

| Phrase | Allowed when | Visual |
|---|---|---|
| **Species absent** | Designed survey + detectability, or physically impossible habitat with a documented envelope | Rare; explicit caption; never default |
| **Species not detected** | Effort + protocol that records nondetection | Open stamp / “ND” · not a zero-abundance fill |
| **No observations available** | Default | `DATA_GAP` hatch |

Mixing these three is a category error equal to painting SST as fish.

---

## 1. Vertical migration (DVM and related)

| Process | Visual | MVP |
|---|---|---|
| Diel vertical migration | Time–depth curtain; **envelope** not a single line; observed stamps solid | Later |
| Seasonal depth changes | Monthly depth-curve small-multiples | Later |
| Thermocline association | Overlay MLD / thermocline as **physical** layer | Later |
| OMZ avoidance | Oxygen habitat edge (teal/habitat), not counts | Later |
| Light response | Kd / PAR as env; behavior as inferred | Later |
| Pressure tolerance | Dossier text, not a globe layer | — |
| Benthic vs pelagic | `BOTTOM_CONTACT` vs pelagic bins; different legends | W1: intertidal vs water |

**Do not** animate a sine-wave fish. If DVM is inferred from a few tags, caption `n tagged individuals ≠ population`.

Oysters: **no DVM layer**.

---

## 2. Life-stage-specific distribution

Stages (eggs, larvae, juveniles, adults, spawning adults, feeding aggregations, nursery, crustacean molt, shellfish settlement) are **different targets**. They do not share a color scale or a search box that silently mixes them.

| Stage | Default publish | W1 |
|---|---|---|
| Farmed grow-out | PRIVATE performance; public env only | **Implied**; chip `grow-out (farmed)` |
| Seed / nursery | Different decision — out of W1 | Off |
| Spawning adults / aggregations | `NEVER_PUBLISH` GPS | Off |
| Larvae / settlement | Research; not 72h OSI | Off |
| Molt (lobster-class) | Seasonal prior, not next-haul map | n/a |

UI: if life-stage selector exists later, default is **explicit** and empty-state is UNKNOWN, not “all stages blended.”

---

## 3. Reproduction and phenology

Show **when**, not **secret where**.

| Signal | Visual | Forbidden |
|---|---|---|
| Spawning season | Calendar / DOY ribbon | Moon-timed GPS |
| Lunar/tidal spawning | Tide/moon as **env** | Aggregation waypoint |
| Temperature threshold | Env line + literature | “Spawn here now” pin |
| Migration trigger | Coarsened corridor later | Listed-ESU mouths |
| Larval dispersal | Particle research | Public settlement heatmap |
| Settlement / recruitment | Index with lag | 72h set forecast as operator product |

W1: ripe summer oysters as a **confounder** in limitations text, not a spatial layer.

---

## 4. Behavioral ecology

Schooling, aggregation, territoriality, hiding/burrowing, reef association, diel behavior, predator avoidance, feeding, sensory ecology — **dossier + later inferred layers**.

Visual risk: aggregation maps are targeting aids. Default coarsen/withhold. Schooling sprites are count theater — forbidden.

---

## 5. Prey / forage fields

| Layer | Class | Caption |
|---|---|---|
| Chlorophyll / productivity | BGC | Not fish, not oyster N |
| Zooplankton / forage fish | Survey index or UNKNOWN | Lag to predators in years–months often |
| Seabirds as indicators | Often sensitive colonies | Do not map nests |
| Food-web lag | Edge attribute | Cannot drive 72h OSI |

W1: chlorophyll **off** for 72h mortality (growth/fattening at longer scale).

---

## 6. Hydrodynamic behavior

Eddy retention, fronts, upwelling, convergence, river plume, larval transport, current shelter, wave exposure, tidal exchange.

These are **physical layers** (Group A) that may **condition** a biological model. They do not inherit a biological legend.

W1 **on:** tides, wave exposure, (optional) freshwater pulse as salinity proxy. **Off:** larval transport.

---

## 7. Extreme-event response

| Event | W1 visual | Notes |
|---|---|---|
| Marine heatwave / aerial heat | Air × emersion OSI | 2021-class mechanism; not body T |
| Hypoxia | DO if sensed; else UNKNOWN | Do not impute from SST |
| Storms | Wind/wave workability | Options: inspect gear — not “safe to go” |
| Freshwater pulses | Discharge / salinity | Flood co-stressor |
| HABs | Not in OSI color | Split animal-stress vs NSSP toxins |
| Disease | Limitations (OsHV-1 not assumed in WA) | No farm disease map |
| Cold snaps | Optional later | |
| Wildfire/runoff | Optional later | |
| Pollution / oil | Not a globe v1 layer | |
| OA events | Off for adult 72h | Larval/hatchery product is different |

Extremes use **anomaly palettes** (diverging, named climatology) separate from occurrence purple and habitat teal.

---

## 8. Human pressure

| Layer | Allowed | Forbidden |
|---|---|---|
| Fishing pressure | Official landings grain, lagged | Public CPUE hotspot, AIS hunt |
| Vessel noise / shipping | Official lanes as context | Identity |
| Habitat destruction | Published change maps | |
| Aquaculture interaction | Partner PRIVATE | Other farms’ KPIs |
| Construction / offshore wind | Official footprints | |
| Bycatch risk | Coarse, delayed, non-targeting | Fine listed-taxon maps |
| MPAs / seasonal closures | Authority polygons + links | Model-colored open/closed |

W1 human pressure that **is** in product: **workability** (can the crew work the tide) as ops-stress — **not** weather-safety certification, not harvest legality.

---

## 9. Population structure

Genetic stock, subpopulation, migratory unit, metapopulation, source–sink, connectivity, local adaptation.

Display as **labels and masks** (e.g. Chinook mixed stocks including conservation units), not as a public stock-health choropleth. “The stock is up/down/healthy here” is a never-claim.

W1: ploidy unknown → listed in missing inputs; do not mix diploid/triploid labels silently.

---

## 10. Detection bias (first-class)

| Bias | Visual / panel |
|---|---|
| p(detect \| present) | Named if a model exists; else “unquantified detectability” |
| Gear bias | Caption on CPUE |
| Depth bias | Empty bins hatch; surface-only remote |
| Observer / citizen bias | Effort of **records**, not abundance |
| Survey-season bias | Seasonal coverage holes |
| Vessel-access bias | Unfished ≠ empty |
| Camera / acoustic / eDNA limits | Modality captions (optical depth, TS overlap, DNA transport) |

**AIS is detection of vessels, not animals.**

Coverage mode is how bias is **shown**. Do not “correct” a map into a fake unbiased abundance field without a validated observation operator — and even then, keep the quantity class honest.

---

## 11. MVP subset (Willapa)

Show or stub:

- Emersion vs water (vertical behavior of **the product**, not of swimming stock)  
- Heat × tide extreme mechanism  
- Wave/wind human workability  
- Detection bias: station offset, no on-lease sensors  
- Absent / not detected / no obs triad in copy  
- Life-stage chip: farmed grow-out  

Hide: DVM, prey field, food-web, spawning, stocks, global pressure atlas.
