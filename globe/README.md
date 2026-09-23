# Ocean Life Globe — visual contract

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Binding visual specification. No live ocean data. No ingest. No public animal heatmap.

This directory is the **long-term scientifically honest visual system** for a 4D, evidence-typed ocean interface. It is **not** the commercial MVP and **not** a claim that the project tracks marine life.

---

## 1. Three surfaces, one honesty rule

| Surface | Job | What a user sees | What it is not |
|---|---|---|---|
| **Commercial FishAI (paused)** | ONE species × ONE geography × ONE customer × ONE recurring decision | Daily **email + 1-page PDF** (optional WhatsApp ping). Recommended: Willapa Pacific oyster **72h Category D operational-stress / work-window** brief. | A globe. A harvest map. Food-safety. A public “fish are here” product. |
| **Observatory** | Scientific blueprint for a saltwater-life digital twin | Catalogs, support tiers T0–T6, physics limits, evidence classes. Research only. | A shipped map of all taxa. A census. |
| **This globe** | Visual language + later local, coarsened, evidence-typed view | Earth + bathymetry + **Unknown map** + **Evidence explorer** + time readout, starting at **one AOI (Willapa)** with **fixture-quality placeholders**. | Live tracking. Volumetric life cloud. Food-web arcade. Climate scenario theater. |

**Firewall:** Observatory research and this globe **must not** expand the commercial SKU. A Chinook layer in a globe mode catalog is not a Chinook product. Commercial v1 remains **email/PDF** until a founder lock and paid pull exist. See `../artifacts/requirements_and_wedge/recommended_initial_wedge.md` (RECOMMENDED, not DECIDED) and `../artifacts/scientific_red_team/prediction_contract.md`.

**First operational visual (later, after rights + wedge lock):** the same globe chrome clipped to Willapa, serving W1 as a **local, coarsened, evidence-typed** view of **ops-stress / coverage / drivers** — not oyster counts, not DOH open/closed as a model color.

---

## 2. Binding laws (every pixel)

1. Every visual object has **exactly one** visual-truth state (`visual_truth_states.md`). Unclassifiable → do not draw.
2. **UNKNOWN is first-class.** A hatch is a successful product state, not a missing texture.
3. **Never red = fish are here.** Habitat, occurrence, abundance, CPUE, forecast, and unknown use **different encodings**.
4. Depth, time, confidence, freshness, grain, and evidence type are visible **without a secondary click** on the primary chrome.
5. Suggested actions are **OPTIONS**, never waypoints or commands.
6. Publish class is always badged: `PUBLIC | COARSENED | DELAYED | RESTRICTED | PRIVATE | NEVER_PUBLISH`.
7. No live tracking of all marine life. No silent interpolation. No deceptive animation.

---

## 3. MVP visual (must ship this, not all 10 modes)

**Recommended MVP modes (only these are in-scope for a fixture prototype):**

| Mode | Name | MVP? |
|---|---|---|
| 1 | Earth surface (land, named water body, **bathymetry / not-for-navigation**) | **Yes** |
| 8 | Evidence / provenance | **Yes** |
| 9 | Uncertainty / data-gap (Unknown map) | **Yes** |
| — | Persistent **time readout** (issued / valid / inputs through / last obs / confidence / model version / coverage) | **Yes** (chrome, not a separate mode) |
| 2 | Semi-transparent ocean / subsurface | Later |
| 3 | Vertical depth slice / curtain | Later (W1 may stub an **emersion vs water** curtain, not a 50-layer fish curtain) |
| 4 | Horizontal depth slice | Later |
| 5 | Seafloor / habitat view | Later (bathymetry already in Mode 1) |
| 6 | Time-lapse forecast playback | Later |
| 7 | Side-by-side comparison | Later |
| 10 | Ecosystem / food-web | Later |
| — | Story mode, volumetric cloud, climate scenarios | Later |

**MVP AOI:** Willapa Bay, Washington — **public water-body geography**, coarsened cells. Fixture / synthetic placeholders only. No real farm KPIs, no real lease corners, no OBIS/GBIF/AIS ingest.

**MVP layers (stubs allowed):** bathymetry; observation-density / data-gap; one **environmental driver** labeled as water-surface or air (never “oysters”); W1 **ops-stress indicator** on a named coarsened cell with Category D copy.

---

## 4. What this globe estimates (and does not)

Long-term biological object (when evidence exists):

```text
P(present | lon, lat, depth, time, env)
```

…shown only as an **evidence-typed field** with a named target, units, and ceiling no stronger than the strongest evidence (`prediction_contract.md` categories A–E). Most of the ocean, most taxa, most depths: **UNKNOWN**.

**W1 / P0 object is not that probability.** Pacific oysters on a farm are **planted**. The first operational visual estimates a **72h operational disruption / environmental-stress indicator** (Category **D**): air × daytime emersion × wind/wave workability, with supporting in-situ water T/DO/S if present. It does **not** estimate abundance, presence of wild set, food safety, or harvest legality.

---

## 5. File map (this agent)

| File | Section | Role |
|---|---|---|
| [`visual_truth_states.md`](visual_truth_states.md) | B | Mandatory states + visual language |
| [`globe_modes.md`](globe_modes.md) | A | Ten modes; MVP vs later |
| [`volume_4d_spec.md`](volume_4d_spec.md) | C | Surface, curtain, slice, volume, depth curve, DVM; depth unknown vs integrated |
| [`time_and_forecast_ui.md`](time_and_forecast_ui.md) | D | Timeline states + issuance clocks |
| [`layer_stack.md`](layer_stack.md) | E | Physical, BGC, habitat, biological, operational |
| [`movement_visualization.md`](movement_visualization.md) | F | Tags vs corridors vs plumes; no spawning GPS |
| [`abundance_encoding.md`](abundance_encoding.md) | G | Count / index / biomass / CPUE / p / suitability |
| [`evidence_explorer.md`](evidence_explorer.md) | H | 16 fields; why / trust / missing / class |
| [`unknown_map.md`](unknown_map.md) | I | Ignorance as a feature |
| [`ecological_network_view.md`](ecological_network_view.md) | J | Observed vs literature vs inferred vs speculative |
| [`story_mode.md`](story_mode.md) | K | Optional explainer; later |
| [`accessibility_and_trust.md`](accessibility_and_trust.md) | N | Colorblind, texture, SR, tables, no deceptive smoothing |
| [`sensitive_display_rules.md`](sensitive_display_rules.md) | A.18 | Publish classes; no harmful precision |
| [`biological_variables_visual.md`](biological_variables_visual.md) | Bio vars | DVM, stages, phenology, bias; absent vs not detected vs no obs |
| [`user_output_contract_visual.md`](user_output_contract_visual.md) | Contract | 14 fields on globe + panel |
| [`wireframes.md`](wireframes.md) | — | ASCII chrome, evidence panel, unknown map, W1 oyster view |
| [`agent_handoff.md`](agent_handoff.md) | — | Recipients, MVP list, never-ship |

**Sibling (do not overwrite; other globe agents):** `visual_performance_architecture.md`, `technology_evaluation.md`, `stack_recommendation.md`, `tile_and_lod_design.md`, `api_for_globe.md`, `prototype/` (fixture app). Sections **L–M** (performance architecture, stack evaluation) are **owned by the stack agent**. This contract states **what** must be visible; they state **how** it is rendered.

**Do not write:** `../artifacts/integration/**`, `../project_state.json`, `../observatory/**`.

---

## 6. How to read with commercial and observatory docs

| If you need… | Read |
|---|---|
| Allowed claim language | `../artifacts/scientific_red_team/prediction_contract.md` |
| Commercial email/PDF layout | `../artifacts/product_and_monetization/wireframe_spec.md` |
| Observatory evidence-class chips | `../observatory/artifacts/product_cost/sample_evidence_ui_spec.md` |
| Support tiers T0–T6 | `../observatory/global_species_registry/support_tier_framework.md` |
| Privacy / NEVER_PUBLISH | `../observatory/sensitive_location_policy.md` |
| Depth bins / as-of clocks | `../observatory/global_digital_twin_architecture.md` §§4–5 |
| Uncertainty categories | `../artifacts/quality_and_validation/uncertainty_policy.md` |

Copy may shorten layout. It **may not strengthen meaning**.

---

## 7. Never-ship (preview; full list in `agent_handoff.md`)

- Public global “fish are here” / “life” heatmap as commercial or observatory v1.
- Red-green traffic light mixing ops-stress with WA DOH harvest open/closed.
- Smooth interpolation across UNKNOWN cells.
- Live tags of listed taxa, spawning GPS, farm KPIs, trap strings, AIS-as-abundance.
- Three-decimal biological probabilities; 100 m hotspot maps as truth.
- Unconstrained chat that “just estimates.”
- Story/food-web/volume cloud as if they were the MVP.

---

## 8. Status of data

**None ingested.** Prototype cells, if any, are **fixtures**. Licenses are UNKNOWN until a rights review. A screenshot of this globe is not a scientific result.
