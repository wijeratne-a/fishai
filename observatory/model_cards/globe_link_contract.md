# Globe link contract

**Owner:** Species Model Cards and Scientific Model Governance  
**Date:** 2026-09-18  
**Status:** Binding on any globe, tile, research API, or evidence panel that draws organisms or ops-as-biology.  
**Globe tree:** this owner does **not** write `globe/**` (other agents own that directory). Implementers must satisfy this contract. Optional one-line pointer at `globe/MODEL_CARD_LINK.md` is **not** required if that tree already cites this file.

---

## 1. Mandatory trio on every output

Every globe cell, feature, layer legend row, evidence-explorer record, and `/state` or `/forecasts` payload that is about life or farm/fishery **operations-as-biology** MUST include:

| Field | Card field | Meaning |
|---|---|---|
| `card_id` | `card_id` | Resolves to a file under `observatory/model_cards/cards/` |
| `model_version` | `current_model_version` | Exact string match |
| `claim_pack` | `claim_pack` | Exact string match; UI copy ⊆ that pack |

**Missing `card_id` ⇒ cannot publish the layer.** Do not draw the cell. Do not substitute a prettier class. Unclassifiable visual-truth state ⇒ do not draw (`globe/visual_truth_states.md`).

```json
{
  "card_id": "SMC-W1-OYSTER-OPS-RISK-v0-DRAFT",
  "model_version": "W1_oyster_ops_risk_v0_SPEC",
  "claim_pack": "claim_pack_W1_oyster_ops_D_v0"
}
```

The example above is a **draft** trio. It is valid as a fixture **only** if the globe also badges `NOT_PUBLISHED` / `NOT_OPERATIONAL` and does not issue a biological score. Shipping that trio as a live layer **fails** the README rule because the card is not `PUBLISHED`.

---

## 2. Resolve-and-refuse algorithm

```text
if payload has no card_id:
    REFUSE layer  # cannot publish
lookup card by card_id
if not found:
    REFUSE layer
if card.current_model_version != payload.model_version:
    REFUSE layer  # silent mix of versions forbidden
if card.claim_pack != payload.claim_pack:
    REFUSE layer
if card.card_status != PUBLISHED:
    REFUSE score; optional UNKNOWN hatch + identity only
if card.operational_status != OPERATIONAL:
    REFUSE score
if user-visible sentence not in card permitted_user_claims / claim_pack:
    REFUSE copy
draw using card.output_category.visual_truth_state
never upgrade visual-truth state because SST/chl/AIS are stacked
```

Globe may show **environmental context** (bathymetry-not-for-nav, air/water fields labeled as physics) **without** a species card **only if** the legend does not name a taxon, ops-stress, CPUE, encounter, abundance, or “life.” The moment a taxon or W1/W2/W3 target is named, the trio is required.

---

## 3. Fields the globe must echo (not all 31 on-chrome)

Chrome / evidence panel (no secondary click for the primary readout) must surface at least:

- Taxon common + accepted name + AphiaID  
- Prediction target + horizon  
- Category A–E and visual-truth state  
- Support tier **emitted** (not merely eligibility)  
- Confidence High/Medium/Low/None or None-because-unpublished  
- Freshness / `inputs_through`  
- `model_version` + `card_id`  
- Publish class (`PRIVATE` / `COARSENED` / `NEVER_PUBLISH` / …)  
- One “does not mean” line from the claim pack  

The other scientific fields live on the card. A link or panel “Open Species Model Card” is required on any issued layer.

---

## 4. Visual-truth state vs A–E

`output_category` is one schema field with two members:

- `prediction_contract_category`: A–E or `NONE`  
- `visual_truth_state`: exactly one state from the globe catalog  

They must not contradict. Examples that are in contract:

| Product | A–E | Visual-truth (when live) | Today (draft) |
|---|---|---|---|
| W1 ops-stress rank | D | `FORECAST` or `MODEL_INFERENCE` (ops encoding, **not** presence teal) | `UNKNOWN` |
| W2 encounter rank | C | `OPERATIONAL_CATCH_OR_EFFORT` (PRIVATE) or `FORECAST` of that rank | `UNKNOWN` |
| W3 CPUE rank | C | `OPERATIONAL_CATCH_OR_EFFORT` (PRIVATE) | `UNKNOWN` |
| SST skin | not a species prediction | `REMOTE_DETECTION` of **temperature** | physics layer, no species `card_id` |

**Never** one red scale titled “fish.” W1 stress uses a **separate** ordinal encoding from biological presence.

---

## 5. Historical cells

If a globe later replays a past issuance, the cell keeps the **original** `(card_id, model_version, claim_pack)`. Do not restyle old cells with a newer card. That is the visual half of as-of replay (`governance.md` §4).

---

## 6. What this contract does not do

- Does not implement tiles, WebGL, or `globe/prototype/`.  
- Does not authorize drawing W1/W2/W3 scores on 2026-09-18.  
- Does not replace `artifacts/scientific_red_team/prediction_contract.md` for sentence-level copy.
