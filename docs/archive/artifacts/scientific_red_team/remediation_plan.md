# Remediation Plan

**Agent:** SCIENTIFIC_RED_TEAM_AGENT  
**Date:** 2026-09-18  
**Purpose:** Smallest set of actions that could make a *bounded* scientific pilot possible. This is not approval to train or to sell.

**Order of operations:** do not skip to modeling. Founder locks a wedge → rights → labels → as-of features → baselines → blocked validation → prediction contract in the UI → human review → private prospective pilot.

---

## Phase 0 — Immediate (before any training or customer text)

| Action | Owner (suggested) | Clears |
|---|---|---|
| Treat all three wedges as **research candidates**, not products | Requirements | B-ALL-08 until founder lock |
| Adopt this folder as the claims ceiling | Product + all agents | XCUT-08–10 |
| Ban the never-claims list in `prediction_contract.md` from UI copy, sales, and README | Product | All NEVER claims |
| Do not ingest AIS/VMS/Addendum XXIX tracks, bulk ocean rasters, or farm/catch microdata | Data discovery / geo | B-ALL-07, B-LOB-01 |
| Rewrite Quality B4 (air×emersion, not SST ≥ 19 °C) and replace Totten/top-20% sample brief | Quality + Product | RT-SIB-01, RT-SIB-02 |
| When sibling artifacts appear, **re-run red team** on their claims | This agent / parent | Process |
| Name human reviewer seats (do not fill with models) | Founder | B-ALL-05 |

---

## Phase 1 — If oyster is selected (recommended scientific pilot)

1. **Lock target:** 72h Category **D** *operational disruption / environmental-stress indicator* for a named lease. Not mortality %, not closure probability, not harvest window.
2. **Hard-split product modules**
   - Module A: ops indicator (model-optional; rule-based tide×air×wave v0 is preferred).
   - Module B: official WA DOH growing-area / biotoxin / Vp status, attributed, timestamped, linked, never averaged into A.
3. **Label dictionary:** workability (could not work the tide), gear/wave loss, protocol mortality counts, in situ T/S/DO/air. **Forbidden labels:** DOH open/closed, Vp prohibition, toxin result as a predicted output.
4. **Features:** air forecast, tide/emersion duration overlapping daylight, solar, wind/wave; *in situ* sensors if present. SST/chl only as labeled Tier 3 context. Stratify **culture type** and **ploidy**.
5. **Privacy:** farm outcomes PRIVATE; no public lease heatmap.
6. **Validation:** time-forward across seasons; hold out 2021-type AHW days as a stress test; spatial block by bay; persistence and seasonal baselines; delayed-mortality window documented (do not score 30-day death as a 72h hit).
7. **Human review:** shellfish aquaculture extension + NSSP/public-health literate reviewer.
8. **v0 that may beat ML:** a transparent rule (“if emersion overlaps forecast air > X°C for Y hours, flag”) plus DOH context. If the rule is the product, **call it a rule**.

---

## Phase 2 — If lobster is selected (conditional second)

1. **Lock target:** next-trip Category **C** expected **legal catch per trap-haul** (or documented effort unit) **for the partner’s existing strings**.
2. **Never:** AIS abundance maps; public high-CPUE cells; tracker pings in the feature store without legal memo.
3. **Effort dictionary:** trap-hauls, soak hours, bait class, vented vs ventless, gauge. Drop trips with unknown effort.
4. **Catchability covariates:** bottom temperature (not SST), month, zone, molt phenology if available. State them as catchability, not density.
5. **Reporting regimes:** do not splice 10% / optimized / 100% harvester programs into one index without a break indicator.
6. **Validation:** operator-blocked and year-blocked CV; persistence of *that operator’s* last comparable soak as baseline; no random cell split.
7. **Privacy:** output is the operator’s; coarsen if any third party sees it.
8. **Human review:** GOM lobster scientist + confidentiality reviewer.

---

## Phase 3 — If Chinook is selected (last; research only)

1. **Abandon** 24–48h habitat SDMs as a customer product.
2. **Lock target:** Category **C** rank of partner-charter CPUE vs **same PFMC/state area, same month, open-season, similar weather-workability bin**.
3. **Hard mask:** closed or unknown regulation status ⇒ no score.
4. **Labels:** trip-level anglers, hours, retained, released; not RecFIN monthly aggregates as 48h labels; not social; not AIS.
5. **Features:** calendar, area, weather-workability **as confounders**, not as “fish presence.” Do not market weather as encounter.
6. **No public map** in v1. If a map appears later: ≥10 km or PFMC subarea, ESA review first.
7. **Validation:** year-block; port-block; must beat month×area climatology **prospectively**. If it cannot, ship climatology under that name or stop.
8. **Human review:** ocean salmon biologist + ESA/effort-concentration reviewer.

---

## Phase 4 — Validation engineering (all wedges)

| Practice | Remediation |
|---|---|
| Random CV | Replace with time-forward + spatial blocks + out-of-year |
| Future chlorophyll/SST delayed-mode | NRT as-of only; drop 8-day windows that include post-issuance days |
| Adjacent cells as independent | Block by growing area / PFMC area / lobster zone / farm ID |
| One metric | Risk products: precision, false alerts/month, missed events, lead time. CPUE: MAE/RMSE, rank correlation, interval coverage, top-k only if k is coarse. Encounter: PR-AUC, Brier, calibration — **plus** slices by season, subregion, effort density |
| “We beat last week” | Require beat of seasonal spatial average **and** persistence |
| Silent forecast overwrite | Immutable issuance log: time, model version, input snapshot hash, output |

---

## Phase 5 — Product language (all wedges)

1. Implement the 14-field output contract (`prediction_contract.md`).
2. Rank bands: lower / middle / upper tercile (or similar). No 0.00–1.00 “catch probability” in v1.
3. Drivers listed as **associations / inputs**, not causes, unless mechanism is in the domain dossier and reviewer-approved.
4. Suggested actions are **options** (“consider delaying work on this tide”) never commands.
5. Outcome form: 30-second structured result (worked the tide? catch per effort? ) to close the label loop.
6. Stale-data banner when official status or env inputs exceed latency budget.

---

## Phase 6 — What we will not “fix” by modeling

These are not hyperparameter problems:

- SST cannot become intertidal body temperature.
- AIS cannot become lobster abundance.
- Chlorophyll cannot become PSP toxin or Chinook forage at 24h.
- Closures cannot become biological mortality labels.
- Disclaimers cannot neutralize a go-fish heatmap.
- HiveClaw-style “AI” cannot substitute for labels.

If a proposed experiment is “add more satellite variables,” **reject** unless a mechanism and an as-of time are written first.

---

## Phase 7 — Re-review triggers

Re-open this red team when any of the following happens:

- A sibling agent asserts skill, a source “is sufficient,” or a public map.
- Founder locks a wedge.
- A partner DUA exists.
- A baseline is computed.
- Product copy is drafted.
- Anyone asks to train.

**Success criterion for remediation:** a human domain reviewer can sign: “this output cannot reasonably be mistaken for food-safety, legality, abundance, or a catch guarantee, and the validation design can falsify the remaining claim.”
