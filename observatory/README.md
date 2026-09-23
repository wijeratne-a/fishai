# Global Saltwater Life Observatory

**Program:** scientific blueprint for a living digital twin of saltwater marine life  
**Parent project:** FishAI (`/Users/wijeratne/dev/fishai`)  
**This directory:** `/Users/wijeratne/dev/fishai/observatory/`  
**Date:** 2026-09-18  
**Current observatory state:** `STATE_1_FRAMEWORK`  
**Current commercial-wedge state (do not modify):** `STATE_10_PAUSED_FOR_HUMAN_DECISION` in `/Users/wijeratne/dev/fishai/project_state.json`

This is **research, architecture, feasibility, and hypotheses**. It is **not** a claim that global operational tracking of marine life exists, and it is **not** a widening of the commercial product.

No datasets were ingested in this program. UNKNOWN is a valid, high-quality output.

---

## How this relates to the commercial wedge

Two programs share a repo and honesty rules. They do **not** share product scope.

| | Commercial Ocean Intelligence wedge | This observatory |
|---|---|---|
| Goal | One sellable decision aid | Scientific blueprint for a global saltwater-life digital twin |
| Scope lock | **ONE species × ONE geography × ONE customer type × ONE recurring decision** | Eventually every saltwater taxonomic group, with honest support tiers |
| Candidates (not decided) | Pacific oyster / WA farms; Chinook / CA–OR charter; American lobster / Gulf of Maine | Those three taxa are **example registry rows only**. They do not become a global product. |
| Status 2026-09-18 | Paused for founder decision. Recommended W1 (Pacific oyster, Willapa) is **RECOMMENDED, not DECIDED**. | Framework iteration 1: taxonomy authority, support tiers, species-model factory, output contract |
| What may be sold | Nothing yet. No model, no pilot, no ingest. | Nothing. Research artifacts only. |
| Ingest | Forbidden until rights + wedge + label gates | Forbidden. Catalog and cite only. |
| Success | A narrow operator brief that beats a simple baseline under prospective tests | An evidence-typed roadmap from sparse observation to broader coverage, without pretending coverage exists |

**Do not copy observatory breadth into `config/project_config.json` or `artifacts/`.** Those paths belong to the commercial run. Observatory writes stay under `observatory/`.

**Do not upgrade** oyster, Chinook, or lobster to TIER 3–6 because a product team is researching them. A wedge research dossier is not a validated current-condition model, not a forecast, and not operational grade.

Shared non-negotiables (both programs):

- A model is not an observation.
- Vessel density is not abundance.
- Satellite surface imagery is not a census of animals below the surface.
- Habitat suitability is not current presence, harvest legality, or food safety.
- Exact locations of endangered taxa, spawning/nursery/nesting sites, private fishing spots, farm performance, and Indigenous knowledge are not public outputs.
- Licenses are `UNKNOWN` until verified on the official page for the intended use.

---

## What “living digital twin” means here

A **probabilistic, uncertainty-aware, depth-and-time-aware estimate** of where saltwater organisms have been observed, where habitat could support them, and—only where evidence allows—current relative condition or short-horizon change.

It does **not** mean:

- exact locations of all individuals;
- exact regional census;
- real-time tracking without a contemporaneous observation;
- a single global heatmap of “the fish.”

Every capability is classified:

1. observable today  
2. inferable today  
3. forecastable today  
4. requires new data infrastructure  
5. scientifically plausible but unproven  
6. technically speculative  
7. physically impossible or not currently measurable  

Every output is classified as exactly one of: `DIRECTLY OBSERVED` | `REMOTELY DETECTED` | `SURVEY-DERIVED` | `TAG/TELEMETRY-DERIVED` | `OPERATIONALLY OBSERVED` | `MODEL-INFERRED` | `FORECAST` | `HYPOTHETICAL/RESEARCH MODE` | `UNKNOWN/INSUFFICIENT DATA`.

Contract: [`user_output_contract.md`](user_output_contract.md).

---

## Species support tiers (summary)

Defined in [`global_species_registry/support_tier_framework.md`](global_species_registry/support_tier_framework.md). Example rows: [`species_support_tiers.csv`](species_support_tiers.csv).

| Tier | Name | Honest meaning |
|------|------|----------------|
| T0 | Taxonomy only | Known taxon; insufficient data to estimate distribution |
| T1 | Historical occurrence | Compiled records support coarse range/seasonality, not current presence |
| T2 | Habitat suitability | Occurrence + environment can support a suitability model. **Not** current presence or abundance |
| T3 | Current condition estimate | Time-aware validated estimate of current occurrence/encounter or relative condition |
| T4 | Short-horizon forecast | Prospectively tested 24 h / 72 h / 7-day forecast |
| T5 | Direct observation / telemetry | Recent observation or tagged-animal track. **Individual ≠ population** |
| T6 | Operational grade | Prospective validation, source resilience, rights, and outcome feedback |

No taxon is upgraded without cited evidence. Example rows in iteration 1 are **T0–T2 only**. T3–T6 remain empty because this observatory has not published, ingested, or prospectively validated any current-condition, forecast, telemetry, or operational product.

---

## Directory skeleton

Specialist agents fill catalogs inside these folders. Empty folders are intentional at iteration 1.

```
observatory/
  README.md                          this file
  project_state.json                 observatory state machine (not the commercial one)
  user_output_contract.md
  species_model_factory.md
  species_support_tiers.csv
  global_species_registry/
  taxonomy_graph/
  species_model_registry/
  species_ecology_profiles/
  observation_coverage_maps/
  depth_coverage_maps/
  uncertainty_maps/
  direct_observation_registry/
  telemetry_registry/
  eDNA_registry/
  acoustic_registry/
  sensor_network_catalog/
  hypothesis_experiment_cards/
  scientific_red_team_reports/
  physics_feasibility_reports/
  cost_and_deployment_models/
  checkpoints/
  iteration_reports/
```

Taxonomy authority: WoRMS / Aphia ([`taxonomy_graph/taxonomy_standard.md`](taxonomy_graph/taxonomy_standard.md)).

---

## Budget (iteration 1)

Recorded in `project_state.json`:

- `MAX_AUTONOMOUS_WORK_HOURS` = 72  
- `MAX_PARALLEL_AGENTS` = 16  
- `CHECKPOINT_INTERVAL_HOURS` = 4  
- `MAX_HYPOTHESIS_ITERATIONS` = 12  
- `MAX_DATA_SOURCE_DISCOVERY_PASSES` = 5  
- `MAX_PROTOTYPE_DESIGNS` = 10  
- `start_time` = 2026-09-18T22:35:00-07:00  

---

## Read next

1. [`project_state.json`](project_state.json)  
2. [`taxonomy_graph/taxonomy_standard.md`](taxonomy_graph/taxonomy_standard.md)  
3. [`global_species_registry/support_tier_framework.md`](global_species_registry/support_tier_framework.md)  
4. [`species_support_tiers.csv`](species_support_tiers.csv)  
5. [`species_model_factory.md`](species_model_factory.md)  
6. [`user_output_contract.md`](user_output_contract.md)  
7. [`checkpoints/CHECKPOINT_2026-09-18T2235.md`](checkpoints/CHECKPOINT_2026-09-18T2235.md)  
8. [`iteration_reports/ITERATION_01.md`](iteration_reports/ITERATION_01.md)  

Commercial (do not edit from this program): `/Users/wijeratne/dev/fishai/decision_required.md`, `/Users/wijeratne/dev/fishai/artifacts/requirements_and_wedge/recommended_initial_wedge.md`.
