# Life-stage model rules (WS42)

**Ontology:** `labels/LIFE_STAGE_ONTOLOGY.yaml`  
**Mappings:** `labels/LIFE_STAGE_MAPPING.csv`

## Why stage matters

Distribution and movement can differ by life stage. Egg, larva, juvenile, and adult processes must not be pooled into one distribution model without testing whether their spatial processes differ.

## Normalized stages

`egg` · `larva` · `juvenile` · `subadult` · `adult` · `spawning_adult` · `unknown` · `mixed` · `source_specific`

Always preserve the source’s original stage string in `life_stage_source_label` when present.

## Length and stage

Length **may** support a **probabilistic** life-stage classification only when all of the following hold:

1. Species is resolved.
2. Applicable population or region is known.
3. Length metric is known (e.g. FL, TL, SL) and documented.
4. Source relationship (length → stage) is documented for that population.
5. Uncertainty is preserved on the label (no silent hard assignment).

**Do not** assign a definitive life stage from length alone. Atlantic RVC `length_fish` bins therefore default to `unknown` unless an approved species-region mapping exists and uncertainty is recorded.

## Source-specific notes

| Source | Rule |
|---|---|
| CalCOFI CUFES | Counts are **eggs** (`life_stage=egg`). Not adult occurrence. |
| Atlantic RVC | Length bins support size structure research; default model stage remains `unknown` until a documented length–stage map exists. |
| Pacific NCRMP COUNT | Stage usually unstated → `unknown`. |
| OBIS | Map only when the publisher’s lifeStage field is present; otherwise `unknown`. |

## Modeling constraints

- Do not train one detection model on mixed egg + adult rows without an explicit multi-stage design.
- Larval connectivity / particle tracking is a separate question from adult reef detection (see `science/MODEL_QUESTION_ROUTER.yaml`).
- Spawning-adult labels are sensitive in some taxa; coarsen or withhold per security policy — this file does not authorize publishing spawning sites.
