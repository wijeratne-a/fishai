# Agent handoff — observatory architecture / DA / spatiotemporal / food-web

**Date:** 2026-09-18  
**Agents:** OCEAN_DATA_ARCHITECTURE_AGENT · DATA_ASSIMILATION_AND_DIGITAL_TWIN_AGENT · SPATIOTEMPORAL_MODELING_AGENT · ECOSYSTEM_AND_FOOD_WEB_MODELING_AGENT  
**Project:** Global Saltwater Life Observatory (long-term design) + FishAI commercial wedge (local small-stack)  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/` only  
**State:** Design only. No training. No bulk ingest. Wedge UNRESOLVED. `DATA_STORAGE_REGION` UNRESOLVED.

Extended (did not contradict): `/Users/wijeratne/dev/fishai/artifacts/geospatial_data_engineer/**` — observation kernel, H3 + official polygons, privacy tiers, as-of replay, no global lake.

---

## 1. Executive finding

Build **one** evidence-typed, depth-aware twin **schema** (layers 0–10) that the commercial wedge can bind by AOI — and implement **none** of the global cube.

**Recommended v0 twin (RECOMMENDED, not DECIDED):** Pacific oyster (*Magallana gigas*, AphiaID 836033) **24–72 h operational-stress / work-window state** on named WA DOH growing areas in **one** estuary (Willapa recommended). Category **D**. State estimated: stress indicator + workability + local env (air, emersion, surface water, optional DO/S, waves) + density/confidence — **not** abundance, **not** harvest legality, **not** a 3D global posterior.

**v0 assimilation:** **open-loop** expert-rule (B4) + climatology (B12) + uncertainty **rules**. No EnKF, no particle filter, no GCM. Optional hierarchical farm intercepts only after n≥3 permissioned farms.

**Later sequential DA:** particle filter on a **named** eDNA/HAB tracer in one basin (research; eDNA hits = T5 of DNA, not of N), kept off the oyster food-safety brief. Ocean 4D-Var/EnKF: **consume** licensed analyses (H-4.4), do not reimplement. Observatory **T6** is operational-grade validation, not a filter type.

**Depth representation:** discrete **habitat-aware bins** on `(H3 cell, depth_bin_id, time)`, not a global unstructured 3D mesh. v0 uses `INTERTIDAL_AIR` + `SURFACE_0_5` only. Persist `cell_area_km2` (H3 is not equal-area). Lagrangian particles only when the state is a transported tracer.

**Do not build:** global lake, all-taxa maps, neural operators/PINNs/transformers as species engines, public heatmaps, AIS-as-N, real-time listed-species locations, food-web-as-a-service, bulk ingest, training.

Commercial stack stays the geospatial MVP (local SQLite/parquet, ~$30–80/month at pilot). Observatory is the long-term **contract**, not a second platform.

---

## 2. Evidence table

| Finding | Evidence | Confidence | Relevance |
|---|---|---|---|
| Kernel + replay + privacy already specify L0–L5 storage | `canonical_data_model.md`, `as_of_replay_design.md`, `security_and_access_model.md` | High | Observatory layers 0–10 wrap these, do not fork |
| H3 res 6 ≈ 36 km²; res 8 ≈ 0.74 km²; not equal-area | [H3 restable](https://h3geo.org/docs/core-library/restable/) accessed 2026-09-18 | High | Grid + `cell_area_km2` |
| Oyster 72 h mechanism is air × emersion, not SST census | Raymond et al. 2022 *Ecology* https://doi.org/10.1002/ecy.3798; marine_domain dossiers | High | v0 state + depth bins |
| Chinook 48 h SDM from SST not identified | Shelton et al. 2021 https://doi.org/10.1111/faf.12530; Hinke et al. 2005 depth refuge | High | Not v0 twin |
| CPUE ≠ N; lobster needs bottom T | Harley et al. 2001; ASMFC 2025 peer review | High | Later Category C research; T4 only after tests |
| eDNA inverse is underdetermined; forward transport exists | Andruszkiewicz et al. 2019 https://doi.org/10.1038/s41598-019-40788-z; Harrison et al. 2019 | High | Tracer research, not v0 |
| N-mixture/occupancy ≠ stealth census | Barker et al. 2018; MacKenzie et al. 2002 | High | Factory caps |
| Neural operators/PINNs need PDEs + dense sims | Li et al. 2021; Raissi et al. 2019 | High | Reject as species-N |
| Food-web models are year-scale | Christensen & Walters 2004; Fulton Atlantis | High | Layer 4 only |
| W1 scientifically safest commercial slice | marine_domain handoff; red-team; requirements recommended_initial_wedge | Medium (science high, WTP low) | v0 bind |
| No founder lock / no rights / no ingest | `project_state.json` STATE_10 | High | Design-only |

---

## 3. Source / license table

This pass **did not ingest**. Citations for architecture only. DATA_RIGHTS owns production class.

| Source | URL / ID | Use | Note |
|---|---|---|---|
| Geospatial engineer artifacts | `/Users/wijeratne/dev/fishai/artifacts/geospatial_data_engineer/` | Kernel, H3, replay, privacy | Binding |
| WoRMS | https://marinespecies.org doi:10.14284/170 | Taxonomy Layer 0 | Cache used AphiaIDs; no full DB |
| H3 restable | https://h3geo.org/docs/core-library/restable/ | Areas | Apache-2.0 library |
| Prediction contract / uncertainty / baselines | `artifacts/scientific_red_team/`, `quality_and_validation/` | Output contract | Do not loosen |
| Raymond et al. 2022 | https://doi.org/10.1002/ecy.3798 | Oyster v0 mechanism | Cite only |
| Hinke et al. 2005 | https://doi.org/10.3354/meps304207 | Depth-aware Chinook habitat | Cite only |
| Andruszkiewicz et al. 2019 | https://doi.org/10.1038/s41598-019-40788-z | eDNA transport | Cite only |
| Thorson 2019 VAST | https://doi.org/10.1111/jfb.13948 | Later index engine | Cite only |
| Evensen 1994/2003 EnKF | JGR / Ocean Dyn. | Later physics DA | Consume products |
| van Sebille et al. 2018 | https://doi.org/10.1016/j.ocemod.2017.11.008 | Lagrangian | Later tracers |
| CMEMS / NDBC / CO-OPS / NANOOS | landing pages in geospatial resilience plan | Planned env | **UNKNOWN rights until rights agent** |

---

## 4. Confidence and limitations

| Item | Confidence | Limitation |
|---|---|---|
| Two-stack rule (wedge local, observatory schema global) | High | Founder may still demand a world map |
| v0 = oyster stress twin | High scientifically | UNRESOLVED commercially; W2/W3 relationship-gated |
| Discrete depth bins vs 3D mesh | High for v0 | Animals follow isotherms/bottom; derived layers needed later |
| T0–T6 factory | High that we follow `support_tier_framework.md` | Must not be confused with observation evidence T1–T4 |
| Time-to-observatory T6 (operational grade) | Low | No prospective skill, no rights, no outcome loop |
| API as research-only | High | Product agents own briefs |
| No code/DA implemented | Certain | Fixture JSON only in API spec |

---

## 5. Recommended decision

1. **Accept layers 0–10 + H3/bins/polygons/particles + as-of clocks** as the observatory contract.  
2. **Bind v0** to the oyster 72 h Category D slice **if/when** the founder locks W1; if they lock W2/W3, reuse the contract but **do not** upgrade those wedges to abundance twins.  
3. **Ship B4/B12 as the twin engine** until Gate 5 says otherwise.  
4. **Keep commercial infra small**; do not provision a lake “for the observatory.”  
5. **Refuse** public grid fills, mammal-now, harvest-safe, and neural species-N.  
6. Quality/red-team agents: treat observatory `/state` the same as product briefs (14 fields + evidence badge).

---

## 6. Rejected alternatives

| Alternative | Why rejected |
|---|---|
| Global 3D species cube now | No lake, no ingest, manufactured confidence |
| S2 / custom equal-area as v0 index | Weaker privacy parent/child; H3 already chosen |
| Full ROMS/FVCOM mesh as observatory state | We do not run it; rights/cost |
| v0 EnKF / PF / 4D-Var | No \(\Phi\), no \(R\), no coverage tests |
| PINN / FNO / transformer / GNN as abundance | Literature mismatch; empty-cell hallucination |
| EwE/Atlantis as 72 h engine | Wrong horizon |
| Marine mammal real-time occupancy twin | NEVER_PUBLISH / ESA / MMPA |
| HAB toxin twin mixed into oyster brief | Food-safety wall |
| AIS DA | Forbidden as N; privacy |
| Three schema families per wedge | Same kernel; bind by AOI |
| Implementing the research API now | No wedge, no rights, no need |

---

## 7. Follow-up questions

1. Does the founder lock W1 (oyster) or another wedge? Observatory v0 bind follows.  
2. Willapa vs named South Puget Sound polygons?  
3. `DATA_STORAGE_REGION` and PRIVATE residency?  
4. Rights class for CO-OPS / NWS / NANOOS / DOH GIS commercial use?  
5. Are ≥3 design-partner farms plausible (needed before hierarchical intercepts)?  
6. Is a **separate** HAB/eDNA research slice desired later, explicitly firewalled from NSSP language?  
7. Who is human domain reviewer (shellfish + NSSP) before any `/state` leaves localhost?

---

## 8. Artifacts generated

All under `/Users/wijeratne/dev/fishai/observatory/`:

| File | Role |
|---|---|
| `global_digital_twin_architecture.md` | Layers 0–10, space/time, factory T0–T6, v0 state, depth bins, non-goals |
| `data_assimilation_design.md` | Operators (survey, CPUE, tags, acoustics, eDNA), v0 vs later DA |
| `ocean_model_comparison.md` | Honest comparison of requested model families with literature |
| `API_specification.md` | Research API for evidence-typed outputs |
| `artifacts/architecture/agent_handoff.md` | This document |

Did not write outside `observatory/`. Did not ingest. Did not train. Did not modify geospatial schemas.

---

## 9. Should this work be red-teamed?

**Yes — targeted.** Highest leak/claim risks:

- `/state` or `/habitat` used as a public heatmap  
- Empty-cell interpolation  
- Mixing DOH closures into stress labels  
- eDNA/particle clouds reconstructing PRIVATE leases  
- Calling a B4 oyster brief observatory T4/T6 without time-forward tests  
- Chinook thermal-band maps as ESU locations  
- Confusion of observation evidence T1–T4 with registry T0–T6

Re-review required once product wireframes or any live route exists. This agent is not the human NSSP/ESA reviewer.

---

## 10. Suggested next experiment

**Do not download global cubes.** After founder lock (or with fixtures if still paused):

1. Emit one **synthetic** `TwinState` JSON for a Willapa growing-area fixture matching `API_specification.md` §4 and geospatial `ModelPrediction` schema.  
2. Unit-test: PUBLIC serialization drops lat/lon; Low density forbids High confidence; explain reads snapshot ids not live tables.  
3. If W1 locks: 14-day **manual** B4 brief (requirements agent experiment) — still no ML, no DA.

If founder remains UNRESOLVED: freeze this observatory contract; do not specialize connectors or “start the twin” on all taxa.

---

## Return block (for parent agent)

| Question | Answer |
|---|---|
| **Recommended v0 twin / state estimated** | *M. gigas* 24–72 h **operational stress + workability + local env** on named DOH growing areas (one estuary). Category D. Not N, not legality, not global 3D. |
| **Assimilation v0 vs later** | v0: **no sequential DA** — B4 + B12 + confidence rules; optional hierarchical intercepts after n≥3 farms. Later: consume ocean analyses (H-4.4); PF for one-basin tracer; EnKF only inside a named regional physics/BGC twin, never as fish N. Observatory T4/T6 require validation gates, not a Kalman gain. |
| **What NOT to build** | Global lake; all-taxa cube; K8s/Spark/Feast; PINN/FNO/transformer/GNN species engines; public tiles; AIS-as-N; mammal-now; harvest-safe; EwE-as-forecast; bulk ingest; training. |
| **Depth representation** | **Discrete habitat-aware bins** on H3 + official polygons; Lagrangian only for tracers. v0: `INTERTIDAL_AIR` + `SURFACE_0_5`. Not a global 3D mesh. |
