# UI functional audit (scientific display)

**Scope:** Read-only audit of `globe/prototype/index.html` and `globe/prototype/src/layers.ts` (plus enough call-site context to confirm gates).  
**Out of scope:** Aesthetics, restyling, and live globe code changes. This directory does not modify the prototype.

**As of:** 2026-09-25

## Already true in the live prototype

| Behavior | Where | Status |
|---|---|---|
| Current estimate draw gated on `publishStatus === "PUBLISHED"` **and** `hasCurrentEstimate` | `layers.ts` → `mayDrawCurrentEstimate` | **IMPLEMENTED** |
| Forecast draw gated on `publishStatus === "PUBLISHED"` **and** `hasForecast` | `layers.ts` → `mayDrawForecast` | **IMPLEMENTED** |
| Occurrence probability / relative abundance / movement similarly require `PUBLISHED` | `layers.ts` | **IMPLEMENTED** |
| Model card fixture has zero `PUBLISHED` cards (Pacific oyster is `NOT_PUBLISHED`) | `public/fixtures/model-cards.json` | **IMPLEMENTED** |
| Atlantic goliath grouper (`aphiaId` 159353) is `no_estimate` | `taxa.json`; answer path in `main.ts` | **IMPLEMENTED** |
| Unknown is the default scientific status when no published now/soon and no past-report claim | `layers.ts` → `scientificStatusCopy`; Learn copy in `index.html` | **IMPLEMENTED** |
| First-run and Learn copy: Measured / Estimate / Forecast / Past reports / Unknown; not live GPS | `index.html` | **IMPLEMENTED** |
| Banner: sample data; not live tracking; not harvest/food-safety advice | `index.html` | **IMPLEMENTED** |
| Timebar footer shows “Soon: No forecast issued” by default | `index.html` (`#t-soon`) | **IMPLEMENTED** |

## Functional gaps (live UI)

These scientific display fields are **not** implemented as first-class, species-model honesty surfaces on the live globe. Fixture “As of” / expert model strings on the Willapa demo do not satisfy them.

| Gap | Live UI status | Notes |
|---|---|---|
| Valid time (phenomenon / prediction valid interval, not “as of” fixture text) | **NOT_IMPLEMENTED** | No dedicated valid-time field for published or internal model layers. |
| Model version (stable id for the scientific estimate in use) | **NOT_IMPLEMENTED** | Expert timebar `#t-model` is Willapa fixture metadata only; not a gated scientific version chip for species outputs. |
| Extrapolation flag (outside training support) | **NOT_IMPLEMENTED** | No UI signal when a covariate or cell is outside model support. |
| Sensitivity withheld (explicit “locations withheld for sensitivity”) as a structured status | **NOT_IMPLEMENTED** | Sensitive taxa can withhold past reports in copy paths, but there is no dedicated sensitivity-withheld evidence field or badge. |
| Environmental latency (how stale environmental inputs are relative to valid time) | **NOT_IMPLEMENTED** | No latency duration or staleness badge tied to environmental joins. |

## What this audit does not claim

- It does **not** claim the live globe was fixed or restyled.
- Deliverables under `ui-functional/` are audit/spec only (plus the evidence-inspector mock spec).
- No published current estimate or forecast is issued in this build; gates correctly block drawing until `PUBLISHED`.
