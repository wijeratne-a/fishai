# Globe-quality marine interface — implementation brief

**Status:** Binding for the `globe/prototype` pass that follows.  
**Research problem:** [`../RESEARCH_PROBLEM.md`](../RESEARCH_PROBLEM.md) — canonical. This globe must answer that problem honestly, not invent a published species model.  
**Honesty rules remain in** [`../GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md`](../GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md). This file does not replace that prompt or the research-problem document.

## Mission

Two workstreams:

- **A.** Globe, basemap, camera, controls, visual design, and UX. This can ship alone.
- **B.** Scientific data, models, validation, publication, and species layers.

Do not clone Google’s branded interface, imagery, or tiles.  
Do not declare a model `PUBLISHED` to make the globe look complete.  
A polished globe with “we don’t know yet” is the success state if publication gates stay closed.

Render **scientific status** (confirmed observation, current estimate, forecast, historical pattern, favorable habitat, unknown). Do not collapse the six **prediction targets** (observed presence, occurrence probability, relative abundance, movement, habitat suitability, unknown) into “where the fish are.” Current estimate and forecast stay off until a card is actually `PUBLISHED` (today: zero).

## Non-negotiable

- Empty, understandable cold load. No fictional marine-life heatmap.
- “No issued location” / “No forecast issued” unless a card is actually `PUBLISHED`.
- Past reports ≠ present animals. Habitat ≠ confirmed presence.
- Temperature, chlorophyll, currents, and vessels ≠ abundance.
- Willapa oyster working-conditions fixture is Learn/demo only.
- Publication requires the evidence package in `observatory/model_cards/governance.md`. If any gate fails, leave `NOT_PUBLISHED`.

## Phases

0. Baseline the existing MapLibre prototype.  
1. Camera and input (native MapLibre; interruptible flights; reduced motion).  
2. Authorized basemap + source registry; no fake high-resolution ocean.  
3. Full-viewport globe UI with collapsible panels.  
4. Typed layer contracts and rendering gates.  
5. First-species path without a fake publish (historical OBIS density only).  
6. Integrated verification and an honest status report.

## Engine

Stay on **MapLibre GL JS 6.10** unless a documented terrain spike proves globe projection cannot show labeled bathymetry at all. Do not migrate to Cesium in this pass.
