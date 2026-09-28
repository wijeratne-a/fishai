# User output contract — globe and panel mapping

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/user_output_contract_visual.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Binding map of the **14-field** commercial contract onto globe chrome + Evidence Explorer. Copy may shorten layout, **not** meaning.

Master fields: `../artifacts/product_and_monetization/product_thesis.md` §7. Allowed sentences: `../artifacts/scientific_red_team/prediction_contract.md`. Observatory extras: evidence class, support tier T0–T6, publish class.

The commercial MVP remains **email + PDF**. The globe, when used, must not drop fields. A WhatsApp ping still deep-links to a 14-field artifact; a map click must open a panel that holds the same payload.

---

## 1. Where each of the 14 fields lives

| # | Contract field | Globe chrome | Evidence panel | W1 notes |
|---|---|---|---|---|
| 1 | Species and geography scope | Header: taxon, AphiaID, **named** AOI | Repeat | *M. gigas* · Willapa DOH areas · coarsened zone — **not Totten / Vp Cat 3 demo** |
| 2 | Target definition | Quantity-class + Category A–E chip | Field 1–2 titles | Category **D** OSI-72 ops-stress / work-window |
| 3 | Forecast horizon | Time readout **Valid for** | Same | 24–72 h; UTC + PDT + next emersion |
| 4 | What the prediction means | Legend title + tercile/chip | Why sentence | Rank vs **this zone**, similar tides/season — not a probability of death |
| 5 | What it does **not** mean | **Always-on strip** (no scroll) | Limitations + class sentence | Food-safety, harvest auth, NSSP, toxins, body T, nav, weather-safety, abundance |
| 6 | Data freshness | **Inputs current through** + last obs | Field 14 | Per source; DOH clock **separate** |
| 7 | Confidence and uncertainty | Confidence chip + Unknown toggle | Fields 3, 11 | High/Med/Low/None + reasons; no fake % |
| 8 | Relevant inputs / drivers | Layer stack (named) | Fields 7–8 | Air × emersion; wind/wave; water supporting |
| 9 | Known missing inputs | Coverage line | Fields 5, 16, missing sentence | Ploidy, on-lease T/DO, handling, HAB toxin (always) |
| 10 | Source attribution / provenance | Mode 8 | Fields 10, 13 | NWS, CO-OPS, WDOH context; licence UNKNOWN until review |
| 11 | Regulatory / safety disclaimer | Strip + Module B link | Disclaimer block | WDOH pages **win**; no combined OSI+DOH score |
| 12 | Suggested action **options** | **Not on the map as waypoints** | Options list 0–N | Shift labor; monitor; inspect gear; keep plan. Never “harvest now” |
| 13 | Outcome-reporting | Link in panel footer | Link | 30s form — workability / mortality noticed — **private** |
| 14 | Error / feedback | Link in panel footer | Link | Wrong zone / stale / sounds like food-safety / unsafe-nav language |

**Red-team extras (also mandatory on globe issuances):**

| Extra | Chrome | Panel |
|---|---|---|
| Strongest evidence tier 1–4 | Badge line | Badge |
| Prediction category A–E | Chip | Chip |
| Extrapolation flag | Magenta ticks + chip | Reasons |
| Official-status last-verified | Module B clock | Field 14 split |

---

## 2. Layout law

**First screen** (map visible, phone or desktop) must include without scrolling the panel:

- Scope (species × geo)  
- Target + category  
- Horizon (valid_for)  
- Does-not-mean strip  
- Confidence  
- Truth state (observed / inferred / forecast / unknown)  
- Publish class  

The remaining 14-field details may live in the scrollable Evidence Explorer, **except** that a map-only screenshot must still not be readable as harvest advice. Hence the strip is **over the map**, not only in the drawer.

---

## 3. W1 approved paragraph (may typeset as bullets)

From the prediction contract — do not strengthen:

> Elevated **operational stress indicator** for {zone} over the next 72 hours, associated with forecast air temperature overlapping daytime emersion and {wave/wind} exposure. Comparison set: this zone, similar tides, {season}. Confidence: {Low/Medium/High}. Category D. Strongest evidence: {tier}. **This is not a food-safety determination and not harvest authorization.** Verify official growing-area and biotoxin status with the Washington State Department of Health (and tribal or FDA authorities where applicable). Satellite temperature is not oyster body temperature and is not a tissue toxin test. It does not replace the *Vibrio parahaemolyticus* control plan (WAC 246-282-006).

Globe legend title must be consistent with this paragraph (ops-stress indicator), never “oyster mortality risk %” or “safe to harvest.”

---

## 4. Options vs commands (field 12)

| Allowed on panel | Forbidden on globe |
|---|---|
| Checkbox-style **options** | Pins that say “work here” |
| “Consider shifting labor off hottest emersion” | “Harvest now” / “it’s safe” |
| “Inspect gear after wave event” | Waypoints on beds |
| “Keep current plan” | Green = go |

If confidence is Low and the action is expensive, **suppress recommendation**; still show context + official links (`uncertainty_policy.md`).

---

## 5. Module B — official context (not a model)

Separate card, separate colors (no OSI palette):

- Authority, timestamp, jurisdiction, source URL  
- Geographic boundary as **theirs**  
- Last verified time  
- If stale: `Official status not verified — do not harvest on the basis of this view`

Never paint growing areas green/red from the model.

---

## 6. JSON parity

The panel is a view of the same object the email renderer uses. Reject globe payloads that omit any of the 14 fields or the extras. Sibling `api_for_globe.md` should require them on any `issued_view`.

Commercial surfaces without a globe (email/PDF) remain valid complete products. The globe **adds** depth/coverage visualization; it does not replace the contract.
