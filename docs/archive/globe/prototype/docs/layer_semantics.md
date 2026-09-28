# Layer semantics

Canonical problem: [`../../../RESEARCH_PROBLEM.md`](../../../RESEARCH_PROBLEM.md).

Every drawn biological or demo object has exactly one **scientific status**. Encodings must not be mixed. The six **prediction targets** are named in answer copy and must not collapse into “where the fish are.”

## Scientific status (what a pixel may claim)

| Status | When it may draw | Visual | User sentence |
|---|---|---|---|
| Confirmed observation | Direct measured value on a Learn demo cell | Solid measured color | Measured — not a sighting of animals if it is water temperature |
| Historical pattern | Official OBIS occurrence grid after coarsening | Hatched brown cells labeled Past reports | Old detections, not where they are now |
| Current estimate | `publishStatus === PUBLISHED` and `hasCurrentEstimate` | Highlighted likelihood zones | Only if a card is actually published |
| Forecast | `publishStatus === PUBLISHED` and `hasForecast` | Distinct future pattern | Only if a forecast card is actually published |
| Favorable habitat | Overlay checkbox, Learn demo only | Separate brown palette | Favorable conditions — not confirmed species presence |
| Unknown | Default empty ocean; gap toggle; demo unknown cells | Neutral hatch | Don’t know. Not absence. |
| Coarsened / withheld | Sensitive taxa or n < 3 | Not drawn, or withheld copy | Locations withheld |

## Prediction targets (never one “fish map”)

| Target | Issued in this build? |
|---|---|
| Observed presence | No present-day presence product. Past reports are **historical pattern** only. |
| Occurrence probability | No. Requires a `PUBLISHED` current-estimate card. |
| Relative abundance | No. `hasRelativeAbundance` is false on every card. |
| Movement | No. `hasMovement` is false on every card. |
| Habitat suitability | Overlay on Learn demo only, labeled **not confirmed presence**. |
| Unknown | **Yes — default.** Cold load is empty. |

## Gates in code

[`../src/layers.ts`](../src/layers.ts) `mayDrawCurrentEstimate` / `mayDrawForecast` / `mayDrawOccurrenceProbability` / `mayDrawRelativeAbundance` / `mayDrawMovement`.  
[`../public/fixtures/model-cards.json`](../public/fixtures/model-cards.json) has zero `PUBLISHED` cards.

Therefore this build draws **no** current-estimate layer, **no** occurrence-probability layer, **no** abundance layer, **no** movement layer, and **no** forecast species layer.

Willapa fixture cells (including cells tagged `FORECAST` or `MODEL_INFERENCE` in the fixture) appear **only** when the user opens the Learn oyster working-conditions demo.

## Honesty copy

- Cold load: “Empty globe. No species layer. Unknown is the scientific status.”
- Species without a published card: “No issued location.” / “No forecast issued.”
- Habitat: “Favorable conditions — not confirmed presence.”
- Do not say a published estimate “exists (none in this build).” That sentence is gone.
