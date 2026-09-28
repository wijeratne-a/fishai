# Ecological network view

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/ecological_network_view.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Mode 10 — **later**. Not in MVP or fixture prototype.

An optional graph + spatial join for **relationships**. It must not imply causality without evidence and must not become a second heatmap of “life.”

---

## 1. Purpose

For a selected taxon × AOI × season (when dossiers exist), show:

| Node / edge theme | Display only if |
|---|---|
| Prey | Cited or observed diet; lag noted (e.g. *Calanus* → lobster **years**) |
| Predators | Same; listed predators **not** mapped finely |
| Competitors | Literature or data |
| Nursery habitat | **Withhold GPS** by default; may show “uses structured habitat (type)” |
| Spawning habitat | **Withhold** active sites |
| Migration routes | Corridors coarsened; see `movement_visualization.md` |
| Thermal habitat | Envelope **as habitat**, teal legend |
| Oxygen boundaries | Habitat edge, not counts |
| Currents | Physical layer, passive |
| Fisheries pressure | Official effort/landings grain; not AIS hunting |
| Disease / HAB risk | Named, not NSSP legality |
| Climate anomalies | Scenario/anomaly state, research banner |

W1: **do not ship this mode.** Chlorophyll is not a 72h oyster-mortality food-web story.

---

## 2. Relationship classes (exactly one per edge)

| Class | Meaning | Visual |
|---|---|---|
| `OBSERVED` | Measured in this system (diet study, camera, tag) | Solid edge |
| `LITERATURE` | Peer-reviewed or official dossier, possibly other basins | Dashed edge + citation |
| `MODEL_INFERRED` | From a named model | Dotted edge |
| `SPECULATIVE` | Hypothesis / lore / unverified | Faint edge + **SPECULATIVE** label |

**Causality:** an edge is **association or directed hypothesis**, never “A caused B” unless the dossier says so with a study design. UI copy: `relationship, not proven cause` unless tagged `causal_evidence=experimental_or_strong`.

Do not auto-layout a pretty food-web that invents missing edges.

---

## 3. Time and lag

Food-web lags are first-class:

- Oyster 72 h ≠ phytoplankton carbon problem.  
- Lobster legal CPUE ≠ same-week *Calanus*.  
- Chinook 48 h ≠ NWFSC stoplight / JSOES juvenile product.

Edges show `lag: hours | days | months | years | unknown`. Year-lag edges **cannot** drive a 72h operator layer.

---

## 4. Spatial join rules

Clicking a node may highlight **habitat** or **coverage**, not a predator GPS.

Forbidden spatializations: fine predator maps of mammals, spawning choruses, remnant invertebrate beds, private fishing.

---

## 5. Prototype UI

Mode 10 in the switcher: visible, disabled, caption `Later — no fake causality`.
