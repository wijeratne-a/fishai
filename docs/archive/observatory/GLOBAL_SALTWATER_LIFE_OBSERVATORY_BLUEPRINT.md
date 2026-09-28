# GLOBAL SALTWATER LIFE OBSERVATORY — BLUEPRINT

**Program:** Global Saltwater Life Observatory (scientific / technical)  
**Parent:** FishAI commercial wedge (separate, narrower)  
**Date started:** 2026-09-18  
**Status:** **STARTED, not complete.** Sections **1–6** and **19–24** are sketched by COST_AND_DEPLOYMENT_ECONOMICS_AGENT + USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT + product roadmap owner. Sections **7–18** are **placeholders** pointing at sibling-owned files. **Do not overwrite sibling catalogs, architecture, hypotheses, rights, or validation** if those files already contain substance — merge summaries into the placeholder, do not replace their canonical documents.

**No ingest. No trained models. No operational global tracking claim.**

**Commercial firewall:** FishAI remains **ONE species × ONE geography × ONE customer × ONE decision** until traction gates are met. This observatory is the long-horizon blueprint. The first **build** is one honest cell, not a map of all taxa.

Canonical companions written by this agent:

- [`cost_and_deployment_models/cost_model.md`](cost_and_deployment_models/cost_model.md)  
- [`product_roadmap.md`](product_roadmap.md)  
- [`global_coverage_roadmap.md`](global_coverage_roadmap.md)  
- [`1_year_plan.md`](1_year_plan.md) · [`3_year_plan.md`](3_year_plan.md) · [`10_year_plan.md`](10_year_plan.md)  
- [`artifacts/product_cost/sample_evidence_ui_spec.md`](artifacts/product_cost/sample_evidence_ui_spec.md)  

Program framing: [`README.md`](README.md).

---

## 1. Executive Vision

Build the most comprehensive **lawful, scientifically defensible, uncertainty-aware, globally extensible** marine-life intelligence **system design** possible — a living digital twin in the strict sense:

> ecology prior + historical observations + current environmental state + new observations + ocean physics + movement/physiology + an observation model  
> → a **posterior that is allowed to be UNKNOWN**.

The twin estimates, **only where evidence allows**, historical distribution, current occurrence probability, relative abundance/biomass *indices*, depth distribution, movement, habitat suitability, life-stage structure, drivers, and direct observations — each labeled with evidence class, depth, time, provenance, and limitations.

**Vision is not omniscience.** A successful observatory is one that:

1. Shows **empty-of-evidence** ocean as empty.  
2. Operates a **few** bounded cells at decision grade.  
3. Reuses public observing systems (IOOS, Copernicus, surveys) rather than pretending to replace them.  
4. Never sells SST, chlorophyll, or vessel density as animals.  
5. Protects listed species, spawning/nursery/nesting sites, private fishing grounds, farm performance, and Indigenous knowledge.

**Year-1 embodiment of the vision:** framework + **one prototype cell** (`P0-WILLAPA-MGIGAS-OSI72`) — Pacific oyster operational-stress twin in Willapa Bay growing areas — the smallest slice that could later serve the commercial wedge. Architecture siblings independently reached the same v0 recommendation (`global_digital_twin_architecture.md` §8).

**Year-10 embodiment:** a planetary **unknown/coverage fabric** plus operational twins in tens of cells — still not a census. See §21.

---

## 2. What Can Be Tracked Today

“Tracked” here means **observed with an instrument or protocol**, not modeled. Classification: **observable today**.

| What | How (today, in the world — not ingested here) | Output class | Limits |
| --- | --- | --- | --- |
| Sea-surface temperature, ocean color, altimetry, scatterometer winds | Operational satellites (NOAA, Copernicus, NASA) | `REMOTELY DETECTED` | Optical **skin / first optical depth**; not fish; coastal Case-2 water is meters or less (`physics_feasibility_reports/physical_limits.md`) |
| Surface blooms, *Sargassum*, some HAB **proxies** | Ocean color | `REMOTELY DETECTED` | Not toxin; not species of most fish |
| Some whales/pinnipeds/seabird colonies | VHR imagery, aerial surveys, PAM | `REMOTELY DETECTED` / `SURVEY-DERIVED` | Conditional sea state; **not** global census; publish class often NEVER_PUBLISH / COARSENED |
| Shallow benthos / reefs / seagrass / kelp | Clear-water optics, some lidar | `REMOTELY DETECTED` | Turbid estuaries fail |
| Water-column backscatter on survey lines / equipped vessels | Scientific and fisheries echosounders | `REMOTELY DETECTED` | Species ID not unique; effort-biased if opportunistic |
| Vocal marine mammals (and some fish choruses) | Hydrophones; research DAS on some cables | `DIRECTLY OBSERVED` / `REMOTELY DETECTED` | Silent taxa absent; DAS ≠ fish-finder |
| Tagged individuals | Acoustic/satellite/archival tags | `TAG/TELEMETRY-DERIVED` | Biased subset; individual ≠ population |
| eDNA / metabarcoding at sample points | Lab or autonomous samplers | `SURVEY-DERIVED` | Tracer, not GPS; hours–days, 10s of m to 10s of km smear |
| Catch/effort, farm mortality, workability | Logs, landings, observers | `OPERATIONALLY OBSERVED` | Catch ≠ abundance; PRIVATE |
| Physics profiles | Argo, gliders, moorings, NANOOS-class | `DIRECTLY OBSERVED` | Spatially sparse; not biology |
| Tides, NWS marine forecasts | Operational agencies | `FORECAST` (physics) / predictions | Not navigation advice from *this* project |
| Official harvest/season status | DOH, PFMC, DMR, etc. | Context (`DIRECTLY OBSERVED` *regulation*) | **Not** a biological measurement |

**P0 cell (Willapa oyster):** what can actually be tracked *for the decision* is **tides, weather, some in-situ T/S/DO, waves, and partner operational outcomes** — not oyster GPS (they are planted) and not a bay-wide census.

---

## 3. What Can Be Inferred Today

Classification: **inferable today** with explicit models and stated bias. Output class typically `MODEL-INFERRED`. Must not be displayed as observations.

| Inference | When honest | When dishonest |
| --- | --- | --- |
| Habitat suitability (T2) | Occurrence + env envelope, bias covariates, **not presence** | Smooth “the fish are here” |
| Relative heat×emersion stress rank on an intertidal lease | Tide + air + local water; culture method known | SST pixel as tissue temperature or mortality % |
| Relative thermal habitat volume for adult Chinook | 8–12°C with **depth**; season open | Surface SST hotspot = catch |
| Trap CPUE rank vs an operator’s own history | Soak, bait, **bottom T**, legal selectivity | CPUE = stock; AIS = lobsters |
| Larval/plankton transport corridors | Circulation + behavior; wide uncertainty | Adult fish tomorrow |
| Occupancy from eDNA | With transport/decay observation operator | Reads = biomass at the filter GPS |
| Survey indices (Category B) | Design-based / VAST-class on strata | 24–72h operator bite map |
| Soundscape “ecosystem change” | Index of sound, not N animals | Fish count from snaps |

**P0 inference:** Category **D** OSI-72 — relative operational-stress / workability vs comparable tide/season windows at that lease. Residual error is **microclimate and culture metadata** (bag color, elevation cm, ploidy). Delayed mortality after heat (Raymond et al. 2022) can fall **outside** a 72h label window.

---

## 4. What Can Be Forecast Today

Classification: **forecastable today**. Output class `FORECAST`. Skill must beat a simple baseline or the forecast is **NOT READY FOR USE**.

| Forecast | Horizon that is real | What is not a biological forecast |
| --- | --- | --- |
| Weather, waves, air temperature | Hours–days (NWS-class) | “Safe to go” (we refuse) |
| Tides / emersion timing | Days (harmonics) | Oyster body temperature |
| Ocean physics (SST, currents) | Days (CMEMS-class) | Fish abundance |
| OSI-72-type **condition rank** | 24–72h **if** labels exist and rules are calibrated | Mortality guarantee |
| Next-trip CPUE rank | Hours–days **if** private logs + bottom T | Stock status |
| Seasonal phenology (e.g. lobster landings timing literature) | Weeks | Tomorrow’s haul |
| Juvenile marine survival stoplights | Years → adult returns | 48h charter encounter |

**P0 forecast target:** 24–72h **environmental/workability stress indicator**, issued daily. Not food-safety. Not % dead. Confidence **cannot be High** on SST-only (prediction contract).

Most taxa globally: **no** honest short-horizon biological forecast. The correct forecast is **UNKNOWN**.

---

## 5. What Cannot Be Known Today

Honesty ladder items **5–7**: unproven, speculative, physically impossible / not measurable.

**Cannot be known (now, and many not in 10 years either):**

1. Exact location of all (or most) individuals of any wildly mobile taxon.  
2. Exact census / biomass in unsurveyed cells.  
3. Real-time tracking of untagged populations.  
4. Animals below the optical skin from ocean-color/SST satellites (`physical_limits.md`).  
5. Species identity of all acoustic backscatter.  
6. Abundance from AIS/VMS/GFW.  
7. eDNA as a live GPS fix.  
8. DAS as a nekton census (whale-class vocalizations ≠ fish).  
9. On-lease oyster microclimate from a 1 km SST pixel.  
10. 24–48h Chinook **abundance** or catch guarantee (identifiability + ESA mix + vertical refuge).  
11. Lobster **density** from CPUE without catchability model (temperature, molt, soak, competition).  
12. Food-safety / harvest legality from habitat or ops-stress.  
13. Fine public maps of listed taxa, spawning aggregations, nests, private spots, farm performance.  
14. A foundation model that is *correctly confident* in empty cells.

**UNKNOWN / INSUFFICIENT DATA is a high-quality output.** Hiding it is a product defect.

---

## 6. Taxa-by-Taxa Observation Feasibility

**Canonical matrix (sibling):** [`observation_modality_catalog.md`](observation_modality_catalog.md) and `observation_coverage_maps/taxa_modality_feasibility.csv` when present. **Support tiers:** [`species_support_tiers.csv`](species_support_tiers.csv) — iteration-1 examples are **T0–T2 only**; do not upgrade because a wedge is being researched (`README.md`).

Sketch for product/cost planning (not a substitute for the modality catalog):

| Taxon class | Direct today | Infer today | Forecast today (honest) | P0 relevance |
| --- | --- | --- | --- | --- |
| Farmed Pacific oyster | Planted stock known; env sensors; partner mortality | Heat×emersion stress rank | 24–72h OSI-72 **if** labeled | **P0 target** |
| Other shellfish | Similar, different traits | Do not mix Olympia vs Pacific | Separate models | Out of P0 |
| Assessed finfish | Surveys, catch | Seasonal indices | Rarely 24–48h encounter | Chinook is a **worse** first twin |
| Sharks/rays | Some tags; rare VHR | Habitat envelopes | Weak short-horizon | Not P0 |
| Crustaceans (lobster) | Traps, VTS, sea sampling | CPUE with catchability | Next-trip rank **private** | Year 2–3 candidate |
| Cephalopods | Sparse | T0–T2 | Generally no | — |
| Marine mammals | PAM, tags, some VHR, DAS research | Occupancy | Coarse, delayed | NEVER_PUBLISH fine tracks |
| Sea turtles | Nesting programs, some tags | — | — | NEVER_PUBLISH nests |
| Seabirds (marine) | Colonies, some tracking | — | — | — |
| Plankton / HAB | Satellites, nets, imaging | Transport | Bloom *presence* ≠ toxin | Keep off oyster food-safety wall |
| Jellyfish | Campaigns | — | — | — |
| Corals / benthos | Imagery, photogrammetry | Heat-stress **proxies** | DHW ≠ live counts | — |
| Plants / algae | Improving remote maps | — | — | — |
| Microbes | Molecular campaigns | — | — | — |
| Larvae | Sparse samples + particles | Transport | Days–weeks, high uncertainty | Not 72h farm adults |

**Feasibility ≠ permission to productize.** Public layers need ecological-harm review (`sensitive_location_policy.md`).

---

## 7. Observation Modality Matrix

**SIBLING-OWNED.** Canonical: [`observation_modality_catalog.md`](observation_modality_catalog.md), [`satellite_capability_matrix.md`](satellite_capability_matrix.md) (if present), `sensor_network_catalog/`, registries under `direct_observation_registry/`, `telemetry_registry/`, `eDNA_registry/`, `acoustic_registry/`.

Owner: OBSERVATION MODALITY cluster. Cost/UI agents: do not overwrite. When merging, paste a short executive table here and keep numbers in the catalog.

---

## 8. Global Data Source Catalog

**SIBLING-OWNED.** Canonical: [`global_data_catalog.csv`](global_data_catalog.csv), [`global_ocean_variable_catalog.csv`](global_ocean_variable_catalog.csv), `data_catalog_notes.md` (when present).

No bulk ingest. Licenses UNKNOWN until verified. Best P0 starting sources (cost view, not rights approval): CO-OPS tides, NWS, NANOOS (per-stream review), CMEMS SST **as covariate**, WA DOH polygons **as context**, partner outcomes.

---

## 9. Universal Data Architecture

**SIBLING-OWNED.** Canonical: [`global_digital_twin_architecture.md`](global_digital_twin_architecture.md), [`data_assimilation_design.md`](data_assimilation_design.md), [`ocean_model_comparison.md`](ocean_model_comparison.md), `API_specification.md` (when present).

P0 constraint from this agent: **tiny cell store**, as-of replay, H3+official polygons, depth = `INTERTIDAL_AIR` + `SURFACE_0_5`, **no global lake**, **no sequential DA** required for oyster OSI-72. Architecture §8 already specifies this.

UI contract for outputs: [`artifacts/product_cost/sample_evidence_ui_spec.md`](artifacts/product_cost/sample_evidence_ui_spec.md); also `user_output_contract.md` when present.

---

## 10. Species Support Tier Framework

**SIBLING-OWNED.** Canonical: [`global_species_registry/support_tier_framework.md`](global_species_registry/support_tier_framework.md), [`species_support_tiers.csv`](species_support_tiers.csv), [`species_model_factory.md`](species_model_factory.md), [`taxonomy_graph/taxonomy_standard.md`](taxonomy_graph/taxonomy_standard.md).

T0 taxonomy → T1 historical → T2 suitability (not presence) → T3 current condition → T4 short-horizon forecast → T5 direct/telemetry (individual ≠ population) → T6 operational. **No silent upgrades.** P0 may *attempt* T3–T4 **in-cell** only after prospective evidence.

---

## 11. Digital Twin and Data Assimilation Architecture

**SIBLING-OWNED.** See §9 files. v0 assimilation: **none sequential**; expert rules + climatology baselines. Later cells (eDNA+currents, tags, EnKF) are **not** Year-1 oyster work.

---

## 12. Current-State Product Prototype

See **§24** (canonical recommendation from this agent). Architecture §8 agrees. Commercial wireframes: `fishai/artifacts/product_and_monetization/wireframe_spec.md`. Observatory UI: `artifacts/product_cost/sample_evidence_ui_spec.md`.

---

## 13. Sensor and Observation Network Roadmap

**Split ownership.** Cost/deployment path: [`cost_and_deployment_models/cost_model.md`](cost_and_deployment_models/cost_model.md) (hardware last). Coverage rollout: [`global_coverage_roadmap.md`](global_coverage_roadmap.md). Partner incentives: [`partner_network_design.md`](partner_network_design.md). Sensor inventory: `sensor_network_catalog/` (sibling).

**Year-1 network:** public IOOS/federal + 3 farms’ existing logs/sensors + a mobile form. Nothing else.

---

## 14. Hypothetical Technology Portfolio

**SIBLING-OWNED.** Canonical: `hypothesis_registry.md`, `hypothesis_experiment_cards/`, `technology_readiness_matrix.csv`.

Cost ranking for Year-1: **kill** global eDNA mesh, DAS, AUV fleets, VHR tasking, and foundation models as P0. Keep as later experiments with kill criteria. Highest information-per-dollar remains **partner operational labels**.

---

## 15. Ranked Research Experiments

**SIBLING-OWNED** for the full scored list. This agent’s **build sequence** is §23 (next 25 actions). First experiment after founder lock: **14-day manual 72h brief**, no ML, no new sensors.

---

## 16. Scientific Validation Requirements

**SIBLING-OWNED.** Canonical: [`validation_protocol.md`](validation_protocol.md), [`scientific_red_team_reports/observatory_red_team_01.md`](scientific_red_team_reports/observatory_red_team_01.md). Commercial gates: `fishai/artifacts/quality_and_validation/`.

Non-negotiable from this agent’s product view: time-forward + spatial holdout; beat heat×tide / persistence baseline; never score oyster ops-stress against DOH closures; UNKNOWN in empty cells; **NOT READY FOR USE** if not better than baseline.

---

## 17. Privacy, Safety, and Ecological Protections

**SIBLING-OWNED.** Canonical: [`data_rights_register.md`](data_rights_register.md), [`sensitive_location_policy.md`](sensitive_location_policy.md), [`partner_network_design.md`](partner_network_design.md).

Publish classes: PUBLIC | COARSENED | DELAYED | RESTRICTED | PRIVATE | NEVER_PUBLISH. **No public global biological heatmap in v1.** Farm outcomes PRIVATE. Listed-species fine locations NEVER_PUBLISH.

---

## 18. Cost and Deployment Path

**OWNED BY THIS AGENT.** Canonical detail: [`cost_and_deployment_models/cost_model.md`](cost_and_deployment_models/cost_model.md).

**Year-1 budget band: $0.4–1.2 million USD (ESTIMATE)** for framework + one software twin cell (lean $0.25–0.5M). CMEMS/NOAA public physics **$0** licence class (CITED; attribution; NANOOS per-stream review still required). Hardware stacks (sonar, eDNA mesh, PAM/DAS, AUV, VHR tasking) are **later / other taxa** and cost **orders of magnitude more** for less P0 information.

Procurement order: **public → partner export → existing sensors → manual obs → mobile → integrations → (only then) new hardware.**

---

## 19. One-Year Build Plan

Canonical: [`1_year_plan.md`](1_year_plan.md).

**Object:** framework artifacts + **P0-WILLAPA-MGIGAS-OSI72**.  
**Spend:** **$0.4–1.2M ESTIMATE**.  
**Staff:** 2–3 FTE equivalent; **zero** hardware engineers.  
**Ship:** evidence-typed email/PDF/form; as-of cell store; baseline rules; unknown panel.  
**Do not ship:** global map, second species, DAS, AUVs, foundation model.

Success/fail: §24 and `1_year_plan.md` §1.

---

## 20. Three-Year Build Plan

Canonical: [`3_year_plan.md`](3_year_plan.md).

**If Year-1 gates pass:** 1–4 operational-ish **cells**, 2–5 taxa at T3–T4 in those cells, **0–2** at T6, rest of life still T0–T2. Cumulative spend **$1.5–4.5M ESTIMATE** if all years are “go.”

**If Year-1 fails:** this section is void; do not buy sensors to rescue a unused brief.

“Operational-ish” ≠ global. Chinook public encounter maps remain scientifically hostile. Lobster only as **private CPUE**. HAB only as **presence**, never toxin/food-safety mixed into oyster OSI.

---

## 21. Ten-Year Planetary Observation Vision

Canonical: [`10_year_plan.md`](10_year_plan.md) and [`global_coverage_roadmap.md`](global_coverage_roadmap.md).

**Vision:** planetary **unknown/coverage fabric** + operational twins in **tens of cells** + opportunistic partner networks + consortium sensing (cables, IOOS, molecular nodes) **if others fund infrastructure**.

### What global coverage still cannot mean in 10 years

Even with a successful decade of software, partners, and public-good observing:

1. A census of individuals of all or most saltwater species.  
2. Real-time tracking of untagged populations.  
3. Exact counts in unsurveyed cells.  
4. Abundance from SST, chlorophyll, or vessel density.  
5. Uniform depth-resolved global biomass.  
6. Operational T6 forecasts for more than a small minority of taxa×places.  
7. Food-safety, harvest legality, or navigation as twin outputs.  
8. Public fine-scale ESA/MMPA, spawning, nesting, private-spot, or farm-performance maps.  
9. Species-ID of all acoustic targets.  
10. eDNA as a GPS fix; DAS as a fish-finder.  
11. A foundation model that is rightly confident in empty cells.  
12. Deep / polar / turbid oceans known like a well-instrumented temperate estuary.  
13. **The end of UNKNOWN** — unknown maps should get sharper, not vanish.

That list is load-bearing. Marketing that contradicts it is a Sev-1.

---

## 22. Major Risks and Unknowns

| Risk | Why it kills | Mitigation |
| --- | --- | --- |
| **Category inflation** (habitat sold as life) | Core red-team finding | Evidence-class UI; UNKNOWN hatch; no interpolation theater |
| **Food-safety contamination** of oyster P0 | Legal + trust | Firewall copy; DOH links win; never train on closures as y |
| **Scope bleed** into 1×1×1×1 commercial SKU | Unsellable terminal | Firewall in README + this blueprint |
| **No WTP / no behavior change** | Product is a worse NANOOS | 14-day test; kill hardware; pivot memo |
| **No partner labels** | Cannot validate | 3-farm gate; stop ML |
| **NANOOS license exceptions** | Illegal ingest | Per-stream rights; catalog-only until APPROVED |
| **Sensitive location leak** | Harm + partner flight | PRIVATE/NEVER_PUBLISH; coarsen |
| **Chinook season closure** | Zero decision days | Do not make Chinook P0 |
| **CPUE≠N / AIS temptation** | False lobster maps | No public CPUE globe |
| **Physics ignored** (optical skin, eDNA smear) | Impossible claims | `physical_limits.md` is binding |
| **Budget theater** (buy AUVs) | Burns Year-1 band | Hardware-last gate |
| **Founder UNRESOLVED** | Cannot issue operator briefs | Research catalogs OK; collection blocked |
| **WTP unknown** | $0 interviews as of 2026-09-18 | Interview script already exists commercially |

---

## 23. Exact Next 25 Actions

Date zero: **2026-09-18**. Order is load-bearing. Do not skip to 15–25 to look busy.

1. **Founder locks** the commercial wedge (W1/W2/W3 or a still-narrow replacement) and PRIMARY_OUTCOME_METRIC in `fishai/config/project_config.json`. Recommended: **W1 Willapa Pacific oyster 24–72h ops-stress**.  
2. **Keep the firewall:** observatory writes stay under `observatory/`; do not expand `INITIAL_*` to many taxa.  
3. **DATA_RIGHTS review** (no ingest) of CMEMS, CO-OPS, NWS, NANOOS-per-stream, DOH **context-only**.  
4. **Authorize interviews**; run 8–15 operator interviews with the existing script (no GPS in notes).  
5. **Recruit 3 farms** (Willapa or the locked named growing areas) and sign DUAs (PRIVATE outcomes, coarsened public, food-safety firewall).  
6. **Name a human domain reviewer** (shellfish physiologist / extension). Freeze prediction-contract copy.  
7. **Lock the P0 label:** workability **or** stress-event — not mortality % as the v0 claim, not NSSP.  
8. Run the **14-day manual brief** (attributed official tide + NWS + grower-visible NANOOS; 30-second outcome form). **No ML. No new sensors.**  
9. Implement **as-of replay** for **this cell only** (tiny store; clip AOI; no global lake).  
10. Ship **evidence-typed** email/PDF/form (14 fields + evidence class + UNKNOWN + what-it-is-not) per `sample_evidence_ui_spec.md`.  
11. Turn on the **outcome form**; require **≥60%** completeness of work days for continued design-partner briefs.  
12. Code **baseline rules** (heat×daylight-emersion; wave/workability threshold; station T/DO if present). Document version.  
13. **Prospective issuance** ≥60 days (daily in stress season; workability may continue off-peak). Log every cannot-issue.  
14. **Go/no-go** vs baseline and vs the grower’s NANOOS+tide ritual. Stop ML if not beating baseline.  
15. **Paid-signal test** ($750–$1,500 / 90 days hypothesis) only after the free window. If 0/3 would pay *and* would not change a crew call → **fail closed**.  
16. Finish sibling **catalogs** (modalities, sources, hypotheses) without ingesting. Keep non-P0 taxa at T0–T2.  
17. **Kill** any global public biological heatmap designs in review.  
18. Draft **partner sonar edge-feature DUA** (no raw sonar, no public biomass) — **do not deploy** unless a later cell needs it.  
19. Build the **coverage/unknown panel** for the estuary (station distance, missing on-lease T/DO, no kriging animals).  
20. If residual error is dominated by **station offset**, export **existing** on-lease thermistors (hardware-last step 3) before buying anything.  
21. Optional **<$25k** eDNA/HAB micro-test **only** if it reduces a named confusion with food-safety — otherwise skip.  
22. **Automate source pull** before adding an 8th farm; do not scale headcount into copy-paste briefs.  
23. Write **P0 validation report** (skill, calibration, completeness, claim-audit). Upgrade *M. gigas* **in-cell** tier only with evidence.  
24. **Decide Year-2:** stay one cell; add at most one adjacent cell; or archive. No second species because the budget exists.  
25. **Checkpoint** observatory state (`checkpoints/`) including: taxa coverage still honest, cost envelope unused for hardware, next experiments from sibling hypothesis ranking **filtered through hardware-last**.

---

## 24. Recommended First Prototype

### ID

`P0-WILLAPA-MGIGAS-OSI72`

### One sentence

A **public-data-first software digital twin** of **Pacific oyster (*Magallana gigas*, WoRMS AphiaID 836033) 24–72 hour operational stress / work-window** on **named Washington DOH commercial growing areas in the Willapa Bay system (Pacific County)**, for a **commercial farm operator**, estimating a **Category D** relative environmental/operational indicator with **UNKNOWN first-class** — the smallest honest slice that can later serve the commercial FishAI wedge, **not** a global map of all taxa.

### State vector (what is estimated)

1. Predicted **emersion** timing (tide) — `DIRECTLY OBSERVED` harmonics.  
2. **Air-heat × emersion** coincidence — `FORECAST` meteorology × tides.  
3. Nearby **water T / optional DO / S** — `DIRECTLY OBSERVED` if a station exists, else `UNKNOWN`.  
4. **Wave/wind workability** vs a stated rule — `FORECAST` (not navigation safety advice).  
5. **OSI-72 rank** vs comparable windows — `FORECAST` / `MODEL_INFERRED` (rules, not a neural net).  
6. **Missingness / station distance / confidence** — first-class.  
7. Partner **workability / stress noticed** — `OPERATIONALLY_OBSERVED`, `PRIVATE`.

### Explicitly not estimated

Abundance, biomass, wild set, larval tracking, food-safety, NSSP, Vibrio/biotoxin, harvest authorization, navigation, weather-safety commands, other taxa, global 3-D posteriors.

### Why this slice (not a mammal, not Chinook, not a bloom globe)

- Animals are **sessile** on the lease at the decision horizon — no movement DA required.  
- Decision **exists when fisheries are closed**.  
- Official polygons exist; secret-spot blast radius is smaller than capture fisheries.  
- Public covariates already sit in the grower ritual; the product is **synthesis + contract + loop**.  
- Scientifically safest bounded pilot (commercial red team + architecture §8).  
- Directly reusable by the commercial SKU **if** the founder locks W1.

**If the founder locks W2 or W3 instead:** the *commercial* product follows that lock; this observatory still recommends **keeping P0 as the oyster cell for the twin** unless partners for the locked wedge are already in hand — Chinook 24–48h is a poor digital-twin first slice (identifiability, ESA, season kill-switch).

### Build order (hardware last)

Public covariates → partner export → existing sensors → manual observations → mobile form → email/PDF integration. **No** EK80, eDNA mesh, hydrophone, DAS, AUV, or VHR tasking in P0.

### Surfaces

Daily **email + 1-page PDF** + 30-second form. Scientist unknown/coverage panel. No arcade map.

### Year-1 budget

**$0.4–1.2M USD ESTIMATE** (see cost model).

### Success criteria (all required)

| # | Criterion |
| --- | --- |
| S1 | Rights-approved as-of snapshots for the cell (no global lake). |
| S2 | 3 permissioned farms **or** a written recruit-failure after a real attempt. |
| S3 | 14 consecutive days of human-QA briefs, then ≥60 prospective issuance days. |
| S4 | Outcome completeness ≥60% of work days among active partners. |
| S5 | Every brief: evidence class, 14 contract fields, NOT food-safety, provenance, depth (emersion vs station), time, uncertainty, what-it-is-not. |
| S6 | Baseline documented; any ML ships only if it beats that baseline on time-forward evaluation. |
| S7 | No public biological heatmap; no hardware fleet; no second species in the operator UI. |
| S8 | At least some partners **change a crew/handling call** vs NANOOS+tides+weather **or** a documented honest NO-GO (also a success of process). |

### Fail criteria (any one)

| # | Criterion |
| --- | --- |
| F1 | 0/3 design partners would change a crew call after the 14-day + interview window. |
| F2 | Demand is only harvest-legal / Vibrio / HAB toxin (wrong product). |
| F3 | Partners will not log outcomes. |
| F4 | A food-safety, abundance, or navigation claim ships. |
| F5 | Scope expands to a global UI or second taxon to “use the budget.” |
| F6 | Hardware purchased without a written residual-uncertainty experiment and kill criteria. |
| F7 | Model/rule loses to the simple baseline after two honest iterations **and** is still shipped as superior. |

### Kill / continue

**Fail closed** on F1–F7: archive the cell, keep the framework, do not buy the ocean.  
**Continue** only through S1–S8: automate, then consider at most one adjacent cell in Year 2.

---

## Document control

| Field | Value |
| --- | --- |
| Blueprint version | 2026-09-18-start-cost-ui-roadmap |
| Completeness | §§1–6, 19–24 sketched; §§7–18 pointers |
| Next merge | Sibling agents paste summaries into 7–18 **without deleting** this agent’s 1–6 / 19–24 |
| Access date | 2026-09-18 |
