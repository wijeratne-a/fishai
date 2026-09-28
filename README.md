# FishAI

> **Current scientific/product context (2026-09-27):** [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md).  
> This README is the **2026-09-18 paused commercial-wedge track**. It is not the operator runbook for the survey-detection program.

Working name for an Ocean Intelligence Builder research project. Long-term vision: a **trusted intelligence layer** for biological, environmental, operational, regulatory, and commercial ocean conditions.

This is **not** a world map, generic dashboard, generic AI agent, or a dump of public ocean datasets.

**Research problem (canonical):** [`RESEARCH_PROBLEM.md`](RESEARCH_PROBLEM.md) — given a species, location, depth, and time, estimate presence and (where evidence permits) concentration, then how that may change, with uncertainty and evidence. Do not mistake habitat or Copernicus ocean state for an observed animal. The six research programs are not claimed as built. Publication is earned.

The first commercial product, when a founder locks it, must still be:

**ONE SPECIES × ONE GEOGRAPHY × ONE CUSTOMER TYPE × ONE RECURRING DECISION**

## Status (2026-09-18)

**Paused for founder decision.** Configuration was not supplied. All Section 2 fields are `UNRESOLVED` except the working project name and default autonomous-work budget.

Read, in order:

1. [`decision_required.md`](decision_required.md) — exact questions the founder must answer
2. [`artifacts/requirements_and_wedge/recommended_initial_wedge.md`](artifacts/requirements_and_wedge/recommended_initial_wedge.md) — recommendation, labeled **RECOMMENDED not DECIDED**
3. [`artifacts/requirements_and_wedge/wedge_options.md`](artifacts/requirements_and_wedge/wedge_options.md) — three viable narrow wedges
4. [`config/project_config.json`](config/project_config.json) and [`project_state.json`](project_state.json)

Current state machine value: `STATE_10_PAUSED_FOR_HUMAN_DECISION`.

## Canonical first prototype (not decided)

Independent tracks recommend the same first cell: **`P0-WILLAPA-MGIGAS-OSI72`** — Pacific oyster × Willapa Bay DOH growing areas × farm operator × 24–72h Category D ops-stress / work-window. This is **RECOMMENDED, not DECIDED**; it does not lock W1/W2/W3. Alignment note: [`P0_WILLAPA_MGIGAS_OSI72.md`](P0_WILLAPA_MGIGAS_OSI72.md). Next human action remains [`decision_required.md`](decision_required.md). State stays paused.

## Non-negotiables

- No ingestion until a data-rights review approves a source.
- No ML until wedge, label, ground truth, baseline, validation, rights, and red-team gates are met.
- No food-safety, navigation, weather-safety, or legal-harvest authorization claims.
- No exact private fishing locations, farm performance, Indigenous knowledge, or protected-species locations.
- Catalog and cite official sources only; do not scrape paywalls or bypass licenses.

## Layout

```
artifacts/          specialist agent outputs (one folder per agent)
config/             project_config.json
data_dictionary/    reserved
ingestion_pipeline/ reserved (do not ingest yet)
model_registry/     reserved (no models)
evaluation_reports/ reserved
iteration_reports/  iteration cards
checkpoints/        pause / score checkpoints
```

Founder organization is **UNRESOLVED**. Related repos under `~/dev` (HiveClaw, Atlas, NeuroClaw) do not define a FishAI operating company or marine-product choice.
