# Evidence Explorer

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/evidence_explorer.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Binding. Every map click that can show an estimate opens this panel. **MVP.**

The panel answers four questions **above the fold**:

1. **Why does the platform believe this?**  
2. **How much should I trust it?**  
3. **What data is missing?**  
4. **Is this observed, inferred, or forecast?**

If those four cannot be answered, show UNKNOWN — not a thinner map.

---

## 1. Sixteen mandatory fields

For the selected **taxon (or W1 target) × cell × depth band × time window**:

| # | Field | UI label | MVP fixture example (Willapa OSI) |
|---|---|---|---|
| 1 | Current estimate | Current estimate | `n/a as abundance · ops-stress Typical→Elevated at issuance` or `Cannot issue` |
| 2 | Forecast estimate | Forecast estimate | `Elevated OSI-72 · upper tercile vs this zone, similar tides/season (fixture)` |
| 3 | Confidence | Confidence | `Low` + reasons (`FRESH:ok`, `DENSITY:low`, `LABEL_SUPPORT:low`) |
| 4 | Last direct observation | Last direct observation | `None on-lease · nearest station fixture 3.2 km · water T only` |
| 5 | Observation count | Observation count in region | `0 protocol mortality counts in 14d · 1 tide gauge (regional) · 0 bag loggers` |
| 6 | Observation types | Observation types present | Checklist: survey / tag / eDNA / acoustic / sonar / camera / catch-effort / citizen / satellite proxy — **W1: tide harmonic, NWS forecast, optional station** |
| 7 | Environmental inputs | Environmental inputs | Air forecast, tide/emersion, wind/wave; water T/DO/S supporting or UNKNOWN |
| 8 | Key model drivers | Key drivers (inputs, not causes) | `1 air × daytime emersion (+ solar)  2 wind/wave workability  3 station water supporting only` |
| 9 | Comparable history | Comparable historical conditions | Named comparison set; “yesterday Typical” |
| 10 | Model version | Model / rule version | `OSI72-RULE-2026-09-18-v0` · `none trained` |
| 11 | Validation | Validation performance (this species/region) | `Not evaluated prospectively · NOT READY FOR OPERATIONAL USE` |
| 12 | Limitations | Known limitations | Body T unknown; no HAB toxin; no ploidy; not food-safety |
| 13 | Sources | Source links and licenses | NWS, CO-OPS, WDOH context; license `UNKNOWN` until rights review |
| 14 | Freshness | Data freshness | Per-source as-of; DOH last-verified **separate** |
| 15 | Privacy | Privacy / coarsening | `COARSENED public water body · no lease corners · PRIVATE if partner KPI` |
| 16 | Reduce uncertainty | What would reduce uncertainty here? | On-lease T/DO; emersion-timed air at bag; 14d mortality protocol; rights-cleared NANOOS stream |

**Observation types (field 6) — show each as present / absent / not applicable, never as a fake count of animals:**

- survey  
- tag  
- eDNA  
- acoustic  
- sonar  
- camera  
- catch/effort  
- citizen science  
- satellite **proxy** (env, not animals)

---

## 2. Above-the-fold template (MVP)

```text
┌─ EVIDENCE EXPLORER ─────────────────────────────────────────┐
│ Cell: WILLAPA-PUBLIC-H3-PARENT  ·  Depth: EMRSION + surface │
│ Time: valid 2026-09-18 16:00–2026-09-21 16:00 PDT           │
│                                                             │
│ THIS IS: FORECAST of Category D ops-stress (not abundance)  │
│ NOT: food-safety · harvest OK · % dead · live tracking      │
│                                                             │
│ Why believe this?                                           │
│   Rule: forecast air overlaps daytime emersion + wind/wave  │
│   Inputs: NWS (forecast) · CO-OPS tide (harmonic)           │
│                                                             │
│ How much to trust?                                          │
│   Confidence LOW · Evidence Tier 3 env only · no on-lease   │
│   sensors · no prospective skill · fixture ranks            │
│                                                             │
│ What is missing?                                            │
│   On-lease T/DO · bag microclimate · ploidy · HAB toxin     │
│   (toxin always missing from this product)                  │
│                                                             │
│ Observed / inferred / forecast?                             │
│   Tide clock: model-supported prediction (harmonic)         │
│   Air, waves: FORECAST                                      │
│   OSI rank: FORECAST (rule, not ML)                         │
│   Oysters: not estimated                                    │
└─────────────────────────────────────────────────────────────┘
```

Full 16 fields scroll beneath. WhatsApp/email commercial surfaces still carry the 14-field contract; this panel is the **globe** binding of the same honesty.

---

## 3. Why / trust / missing / class — required sentences

Generate from fields; do not free-write stronger language.

**Why**

> This view uses {truth_state} of {quantity_class} from {sources} as of {cutoff}. Drivers listed are **inputs**, not proven causes.

**Trust**

> Confidence {High/Medium/Low/None}: {reason codes in prose}. Strongest evidence {tier}. Support tier {T0–T6}. Validation: {none | pointer}.

**Missing**

> Missing: {list}. Because of that, we {do not issue a score | cap confidence | withhold depth claims}.

**Class**

> This cell is **{OBSERVED | INFERRED | FORECAST | UNKNOWN}** for {target}. It is not {forbidden list}.

W1 forbidden list (always): food-safety, harvest authorization, NSSP, toxin-free, oyster body temperature, navigation, weather-safety certification, abundance.

---

## 4. Evidence badge line (required)

Match red-team + observatory chips:

```text
Evidence: {truth_state} · Category {A–E} · Tier {1–4} labels ·
Confidence {H/M/L/None} · Support {T0–T6} · Publish {class}
```

Rules: if label tier ≤ 3 and output is C/D, confidence cannot be High. Tier 3-only inputs → do not issue Category C. Tier 4 unverified never appears as a prediction.

---

## 5. “What would reduce uncertainty here?” (field 16)

Recommendations are **measurement options**, not “buy our hardware fleet.”

| Gap | Honest next measurement |
|---|---|
| No on-lease T/DO | Permissioned logger at bag height; or declare UNKNOWN |
| Station 3+ km away | Do not krige; report distance |
| No mortality protocol | 30s outcome form; PSI-class counts if partner agrees |
| No depth | Depth-tagged samples; else `depth_status=unknown` |
| Out of domain heat | Say extrapolated; do not pretend High |
| Rights unverified | Do not ingest; keep fixture |

Never: “more AI,” “fuse AIS,” “scrape iNaturalist hidden coords.”

---

## 6. Replay and amendments

- `brief_id` / `forecast_id` + `feature_snapshot_id` in scientist drawer.  
- Issued vs revised toggle if `supersedes_forecast_id` exists.  
- User-visible text **as delivered** is immutable.

---

## 7. Empty click (ocean with no AOI product)

Still open the panel:

> No issued estimate. DATA_GAP for biological targets. Physical bathymetry is context only, not for navigation. This is not a live animal map.

That is a **complete** product state.
