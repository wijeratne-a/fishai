# Research problem — FishAI / saltwater life intelligence

**Status:** Canonical. Persist this wording. Do not treat a globe screenshot, a habitat layer, or Copernicus ocean state as proof that a species is there.  
**Does not replace:** [`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md`](GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md) (honesty / UX contract) or [`decision_required.md`](decision_required.md) (commercial wedge still paused).  
**Globe binding:** [`globe/IMPLEMENTATION_BRIEF.md`](globe/IMPLEMENTATION_BRIEF.md) and [`globe/prototype/docs/layer_semantics.md`](globe/prototype/docs/layer_semantics.md).

---

## The problem

Given a marine species, a location, a depth, and a time, estimate whether that species is present there—and, where evidence permits, how concentrated it is. Then predict how that distribution will change, while showing how uncertain the answer is and what evidence supports it.

**Practical question:** “Where is this species most likely to be now, where might it be next, at what depth, and why?”

The system cannot directly observe all marine life. **Do not mistake plausible habitat for an observed animal.**

---

## Six research programs

These are programs to build. **Do not claim they are built.** Today they are catalogs, fixtures, protocols, and an honest globe — not a published species–region model.

1. **Observations** — a provenance-preserving biological observation database.
2. **Ocean state** — historical and forecast ocean-data cubes. Copernicus (and any other physical cube) is an **input**, not proof of presence.
3. **Species biology** — evidence-graded species profiles.
4. **Inference** — validated species–region distribution models.
5. **Forecasting** — forecasts evaluated against later observations.
6. **Observation planning** — a ranked, testable sampling plan.

---

## Six prediction targets

Never collapse these into “where the fish are.” A pixel, a sentence, and a model card must name **which** target they are talking about.

| Target | Meaning | Ceiling today |
|---|---|---|
| **Observed presence** | Direct evidence that the taxon was recorded at a place, depth, and time | Past OBIS reports may be shown as **historical pattern**, not “here now.” Learn demo measured cells are water-temperature (or other measured values), not animal GPS. |
| **Occurrence probability** | Model estimate that the taxon is present now | **No issued location** unless a card is actually `PUBLISHED` with this target. Count of published cards: **zero**. |
| **Relative abundance** | How concentrated, relative to a defined comparison set — not a census | None issued. |
| **Movement** | Change of location / transport, with a named method | None issued. |
| **Habitat suitability** | Favorable environmental conditions | **Not a presence claim.** Overlay copy: “favorable conditions — not confirmed presence.” |
| **Unknown** | Insufficient evidence to issue any of the above | **First-class default.** Empty ocean is unknown, not absence. |

A **forecast** is a time-forward statement of one of those targets. It is not a seventh collapsed “fish map.” Forecast layers stay off unless a card is actually `PUBLISHED` with a forecast. Count: **zero**.

---

## What the globe must render (scientific status)

The interface may draw only one scientific status per object:

1. Confirmed observation  
2. Current estimate  
3. Forecast  
4. Historical pattern  
5. Favorable habitat  
6. Unknown  

**Publication is earned.** Do not create a `PUBLISHED` model card to make the globe look complete. A polished Earth with unknown as the answer is the correct product state while gates stay closed.

---

## Honesty that this problem forbids

- Plausible habitat ≠ observed animal.  
- Ocean state (SST, chlorophyll, currents) ≠ abundance or presence.  
- Vessel traffic ≠ animals.  
- Past reports ≠ present animals.  
- “Not detected” ≠ absent.  
- A current estimate ≠ a forecast.  
- A forecast ≠ live tracking.  
- Empty water ≠ a survey of zero fish.

See also [`GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md`](GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md) and [`observatory/model_cards/governance.md`](observatory/model_cards/governance.md).

---

## First species slice

**Atlantic goliath grouper** (*Epinephelus itajara*, WoRMS AphiaID **159353**).

Given this species, a location, a depth, and a time, estimate how likely it is that goliath grouper are present there, and how that likelihood will change over hours, days, and seasons—without confusing plausible habitat with observed animals, and while honestly representing uncertainty and data gaps.

Working papers: [`species/goliath-grouper/`](species/goliath-grouper/). **No model is published.** The globe must not imply the system knows exactly where goliath grouper are at every moment. Spawning-aggregation coordinates stay coarsened or withheld.
