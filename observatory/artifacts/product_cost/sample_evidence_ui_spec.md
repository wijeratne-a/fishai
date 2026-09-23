# Sample evidence UI specification — Observatory P0

**Date:** 2026-09-18  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Surfaces:** (1) operator brief (email/PDF/form) (2) scientist/operator evidence drawer (3) coverage/unknown panel  
**Not a surface:** global multi-taxon arcade, unconstrained chat, public hotspot map.

This spec **extends** the commercial 14-field contract and ASCII wireframes in `fishai/artifacts/product_and_monetization/wireframe_spec.md`. It does not replace them. Observatory views add **evidence class**, **support tier**, **depth**, and **UNKNOWN-as-layer**.

---

## 1. Binding UI laws

1. **Every view classifies evidence type.** If a pixel, sentence, sparkline, or API field cannot be classified, it is not shown.  
2. **UNKNOWN is first-class.** Hatched / “insufficient data” is a complete screen, not a spinner that “finishes” into a guess.  
3. **No fish-count theater.** No integers of wild animals in unsurveyed water, no 3-decimal probabilities, no 0–100 “AI scores,” no SST choropleth titled as oysters/fish.  
4. **Depth + time + uncertainty** are visible without a secondary click on the primary surface (brief: emersion vs water; drawer: full).  
5. **Provenance** is one tap/scroll away: source, as-of, license class, model/rule version, brief id.  
6. **What it does not mean** is on the **first screen** of any operator-facing artifact (commercial copy: always “NOT FOOD-SAFETY”).  
7. **Suggested actions are OPTIONS**, never commands.  
8. **T5 tracks ≠ T3 population.** If both exist someday, they do not share a color scale.  
9. **Publish class** badge: PUBLIC | COARSENED | DELAYED | RESTRICTED | PRIVATE | NEVER_PUBLISH.  
10. **Support tier** T0–T6 is visible on any taxon card; T2 must say “not current presence.”

---

## 2. Evidence classes (exactly one per output object)

Use these strings in UI and API. Do not invent synonyms that sound stronger.

| Code | Operator phrase | Color / pattern (accessible) |
| --- | --- | --- |
| `DIRECTLY_OBSERVED` | Measured here | Solid, no glow |
| `REMOTELY_DETECTED` | Detected by remote sensor | Solid + “remote” chip |
| `SURVEY_DERIVED` | From a survey protocol | Hatch-light |
| `TAG_TELEMETRY_DERIVED` | From tagged animals | Distinct hue; caption “individuals” |
| `OPERATIONALLY_OBSERVED` | From operations (farm/trip log) | Solid; **PRIVATE** by default |
| `MODEL_INFERRED` | Inferred by a model | Dotted outline |
| `FORECAST` | Forecast | Dotted + horizon clock |
| `HYPOTHETICAL_RESEARCH` | Research / not operational | Purple banner **RESEARCH MODE** |
| `UNKNOWN_INSUFFICIENT` | Not enough evidence | Hatch + explicit sentence |

**Ceiling rule (display):** a stack of `REMOTELY_DETECTED` SST does not promote a layer to `DIRECTLY_OBSERVED` oysters.

**Badge line (required on briefs):**

`Evidence: FORECAST · Category D · Tier 3 env + Tier 2 labels · Confidence MEDIUM · Support tier T3 (not T6)`

Align with red-team evidence tiers 1–4 and prediction categories A–E (`fishai/artifacts/scientific_red_team/prediction_contract.md`).

---

## 3. Primary operator surface — email (P0 oyster)

Keep the commercial above-the-fold layout. Add four observatory chips that fit on a phone without scroll:

```
┌─────────────────────────────────────────────────────────────┐
│ OBSERVATORY CELL  P0-WILLAPA-MGIGAS-OSI72                   │
│ Evidence: FORECAST (drivers DIRECTLY_OBSERVED / REMOTE)     │
│ Depth: intertidal EMRSION window + water @ station 3.2 km   │
│ Time: valid 2026-09-18 16:00 PDT → 2026-09-21 16:00 PDT     │
│ UNKNOWN: on-lease T/DO · bag microclimate · last 14d mort.  │
│ NOT: food-safety · harvest OK · % dead · abundance          │
└─────────────────────────────────────────────────────────────┘
```

Full 14 fields remain in the PDF. WhatsApp ping **must** include NOT food-safety + link to PDF (SMS cannot hold the contract).

**Status vocabulary (only):** Typical | Elevated | High | **Cannot issue (UNKNOWN)**  
Cannot-issue is a **successful product state**. Visual: black/white, not a broken image.

---

## 4. Coverage / unknown panel (scientist + eventually operator weekly)

Purpose: show **where the twin is blind**, not a prettier estuary.

```
WILLAPA CELL — observation support (not oyster counts)
Depth axis:  [emersion] [0–1 m] [1–5 m] [>5 m] [bottom]
Time axis:   last 72h hourly

Legend:
  ██  DIRECTLY_OBSERVED (named station)
  ░░  REMOTELY_DETECTED (SST pixel — WATER SURFACE ONLY)
  ▒▒  MODEL_INFERRED / FORECAST (OSI-72)
  ▢▢  UNKNOWN_INSUFFICIENT

Map rules:
  - Official DOH growing-area outline: CONTEXT, labeled “harvest geography, not biology”
  - Lease Zone B: PRIVATE outline to the farm; public maps coarsened
  - No interpolation across UNKNOWN. Do not krige animals.
  - Station shown as a point with distance-to-lease in km
  - Color scale never labeled “oysters” or “fish”
```

**Empty-state copy (required):**

> UNKNOWN: not enough evidence to estimate on-lease tissue temperature or dissolved oxygen. Nearest station is 3.2 km. OSI-72 is a **relative environmental/workability indicator**, not a count of animals and not a harvest decision.

---

## 5. Depth × time curtain (P0)

Oysters: the scientifically load-bearing vertical distinction is **emersion vs immersion**, not a 50-layer z-grid.

```
Hour →
Tide  ████░░░░████░░░░   (DIRECTLY_OBSERVED prediction: harmonic)
AirT  ·····FORECAST····
WtrT  ░station░░░░UNKNOWN on lease
OSI   ···FORECAST rank···
Mort  □□□ UNKNOWN (no protocol count this window)

Y-axis labels: “emersion (air exposure)” / “water (station, not bed)”
```

For a future pelagic cell, the same widget becomes depth bins (m positive down) with hatch on unobserved bins. **Do not** draw a full water column of implied fish.

---

## 6. Provenance drawer

Every brief_id opens:

| Field | Example |
| --- | --- |
| `brief_id` | OY-WA-SAMPLE-2026-09-18-A |
| `issued_at` / `valid_from` / `valid_to` | UTC + local |
| `source_cutoff` | last observation time per input |
| `inputs[]` | CO-OPS 9440910; NWS coastal; NANOOS station_id; CMEMS product_id+DOI |
| `license_class` | pending DATA_RIGHTS; show UNKNOWN if unverified |
| `rule_or_model_version` | OSI72-RULE-2026-09-18-v0 |
| `prediction_category` | D |
| `evidence_class` | FORECAST |
| `support_tier` | T3 attempt / actual T2 until prospective |
| `publish_class` | PRIVATE (this farm) |
| `replay_pointer` | as-of snapshot id |
| `limitations[]` | station offset; no bag color; delayed mortality possible |

**As-of replay:** changing a past brief is forbidden without an amendment record. UI shows “issued view” vs “revised view.”

---

## 7. Uncertainty display (no fake ±)

Follow `fishai/artifacts/quality_and_validation/uncertainty_policy.md`:

- Category **High / Medium / Low / None** with **reasons**, not vibes.  
- Interval only if a declared method produced it; else `uncertainty_rationale` prose.  
- Low + expensive action → **suppress recommendation**, still show context + official links.

Operator sentence patterns (approved):

- High: “Conditions look like cases we have scored before. This is not a guarantee of survival or legal harvest.”  
- Medium: “Treat as a watch, not a sure bet.”  
- Low: “Insufficient to change a high-cost action.”  
- None: “Cannot issue OSI-72. Official weather/tides/DOH links only.”

---

## 8. What-it-does-not-mean library (always nearby)

P0 oyster (required paragraph, may typeset as bullets):

> This is not a food-safety determination and not harvest authorization. It is not NSSP classification, not a toxin test, not percent mortality, not navigation, not weather-safety advice. Satellite temperature is not oyster tissue temperature. Verify WA DOH growing-area and closure pages; those pages win.

Chinook / lobster copy exists in the prediction contract — **do not** put those taxa in the P0 UI.

---

## 9. Taxon card (framework UI, not P0 operator product)

For observatory browsers (internal):

```
Taxon: Magallana gigas  Aphia 836033
Support tier: T2 globally / T3-in-cell P0 (if earned)
What can be shown: historical culture range; local OSI-72 FORECAST
What cannot: wild abundance; larval set 72h; food-safety
Evidence available: [list classes]
Default publish: PRIVATE outcomes; NEVER_PUBLISH other farms
```

Most cards in Year 1: **T0–T2** + UNKNOWN map. That is the product.

---

## 10. API sketch (research, not public)

Sibling architecture owns the full API. UI requires at least:

```json
{
  "output_id": "…",
  "evidence_class": "FORECAST",
  "prediction_category": "D",
  "support_tier": "T3",
  "confidence_category": "medium",
  "confidence_reasons": ["FRESH:ok", "DENSITY:low", "IN_DOMAIN:mild"],
  "time": {"issued_at": "…", "valid_from": "…", "valid_to": "…", "source_cutoff": "…"},
  "space": {"cell_id": "WILLAPA-GA-NAHCOTTA", "depth_band": "emersion+surface", "precision_m": null},
  "does_not_mean": ["food_safety", "harvest_authorization", "abundance"],
  "provenance": [{"source_id": "COOPS-9440910", "observed_at": "…"}],
  "unknown": ["on_lease_temperature", "bag_microclimate"],
  "publish_class": "PRIVATE"
}
```

Reject payloads that include `fish_count` or `abundance` without `prediction_category: A|B` **and** a survey protocol id.

---

## 11. Anti-patterns (design review fail)

| Anti-pattern | Why it fails |
| --- | --- |
| Smooth heatmap named “life” | Interpolation theater |
| Green/red mixing OSI with DOH open/closed | Food-safety contamination |
| 3D school of generic fish | Count theater |
| Defaulting missing cells to climatology without banner | Hides UNKNOWN |
| Chatbot that will “just estimate” | Unconstrained claims |
| Public lease performance | Privacy |
| Layer named “AIS biomass” | Category error |

---

## 12. P0 implementation order

1. Email/PDF/form (commercial wireframe) with evidence chips.  
2. Cannot-issue state.  
3. Provenance footer + replay id.  
4. Unknown/coverage panel for one estuary.  
5. Depth-time curtain.  
6. **Stop.** No map product, no app store, no species switcher.
