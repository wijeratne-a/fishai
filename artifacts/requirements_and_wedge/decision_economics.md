# Decision economics

**Status:** Framework + documented industry magnitudes. **No willingness-to-pay observations.** Do not treat census sales or disaster aid as FishAI revenue.  
**Date:** 2026-09-18  
**Access date for sources:** 2026-09-18  
**Agent:** REQUIREMENTS_AND_WEDGE_AGENT

Master-prompt identity:

```
Expected Decision Value =
    P(event) × Value of True Alert
  − P(false alert) × Cost of False Alert
  − Cost of Action
```

P(event), P(false alert), and per-farm/per-trip dollars are **UNRESOLVED** until partners log outcomes. This file only bounds the terms with official evidence.

---

## Rules of interpretation

- USDA and DMR figures are **industry scale**, not ARPU.
- Disaster determinations are **season-scale revenue loss**, not the value of a 48h area ranker.
- Mortality percentages from PSI/WDFW are **event reports**, not a probability for a typical day.
- Never convert these numbers into a guaranteed ROI slide.

---

## W1 — Oyster 24–72h work / stress

### Action the brief can change

Mobilize or stand down a crew for a tide; reduce handling; add monitoring; postpone planting/moves.

### Cost of action (UNRESOLVED numerically)

Labor + vessel time for one tide window. Not published as a statewide average in sources reviewed. Interview question (see `interview_script.md`).

### Value of true alert (bounded by public evidence, not averaged)

| Evidence | What it is | What it is not |
| --- | --- | --- |
| PSI: 20–80% losses in multiple WA commercial growing areas in recent summers | Upper-bound **event** severity for summer mortality | Mean annual farm loss |
| WDFW 2018: 80–90%/bag vs 5–10% typical (Discovery Bay / Whidbey) | Shows handling-during-stress can coincide with extreme bag loss **in those basins** | A Willapa parameter |
| 2021 heat dome + extreme lows (Raymond et al. 2022; WSG: “one estimate” >1 billion animals region-wide) | Mechanism: air heat × exposure tide | A farm invoice |
| USDA 2023: 114 WA Pacific oyster farms; $106.801 million sales | If a 20% mortality event hits a farm’s near-market inventory, dollars at risk are material relative to farm sales | Per-farm sales (many (D) cells in NASS) |
| Pacific County 2022 Ag Census (press): 29 farms, $43.25 million oysters+clams | Concentrated local industry | FishAI TAM |

**True-alert value (qualitative):** avoiding one handling event during a heat-low-tide or hypoxia pulse, or catching a die-off early, can be a **five-figure to high-five-figure** inventory event on a commercial farm — **hypothesis**, to be replaced with partner inventory × observed mortality.

### Cost of false alert

Wasted crew day; missed good tide; alarm fatigue → ignored briefs. **Must be measured** as unused alerts / month.

### Cost of missed event

Mortality and quality loss that a stand-down or reduced handling might have lessened. Causality is **not** proven: 2018 WDFW listed temperature, hypoxia, phytoplankton, handling, possible disease. A temperature-only alert can be wrong.

### Lead time that matters

Hours to two days (next daylight low tide). Seasonal averages do not change tomorrow’s crew call.

### Pricing hypothesis (UNTESTED)

Seasonal SMS/email brief to 3–10 Willapa farms at a **small-business** subscription, **or** a paid 90-day pilot against a documented crew-day cost. Not a Bloomberg-terminal price. **No founder pricing was supplied.**

### EDV status

**Cannot be computed.** Next measurement: 14-day manual brief, log true/false stand-downs, and one inventory-at-risk number per partner.

---

## W2 — Chinook 24–48h relative encounter

### Action

Run vs not (only after NWS/captain safety). If run: choose coarsened sub-area / duration.

### Value of true alert

Incremental anglers retained + fuel not burned on a poor cell, **conditional on an open season**.

Documented **season** loss, not 48h lift:

- 2023 CA CPFV: 127 eligible vessels; **$4.79 million** NOAA allocation to that sector (draft spend plan).
- Implied mean aid ~$38k/vessel if divided equally — **not** stated as equal in the plan (proportional to historical salmon anglers).
- Per-angler prices used in the plan: **$225** standard, **$265** six-pack.
- 2024 CA ocean+inland salmon disaster: **$36.35 million**, **100%** vs 5-year average excluding 2023.

A 48h ranker **cannot** recover a closed season. EDV is **zero** on closed days. Addressable days = open recreational Chinook days in the locked polygon.

### Cost of false alert

Steam to the wrong coarsened cell; extra fuel; disappointed repeat bookers. Fuel cost UNRESOLVED (interview).

### Cost of missed event

Fishing a poor cell when a better coarsened cell was available — **only** if the model is better than the captain’s status quo. Captains may already outperform a public-data model.

### Pricing hypothesis (UNTESTED)

Per-boat seasonal pass for open months only. Disaster aid ≠ subscription.

### EDV status

**Cannot be computed** without trip-level CPUE vs baseline (last year’s same week / inshore vs offshore rule). RecFIN is too lagged to score tomorrow.

---

## W3 — Lobster next-trip CPUE

### Action

Allocate next trip’s hauls among coarsened sub-areas; optionally skip a trip (captain’s call).

### Value of true alert

Better legal catch per trap-haul × price, minus extra steam.

- 2025 preliminary boat price **$5.85/lb** (DMR).
- Statewide 2025: 78.8 million lb, $461.4 million, 5,060 licenses — **mean** ~$91k landed value/license **if** divided equally, which licenses are **not**. Do not use as ARPU.
- 2025 vs 2024: −8 million lb, −$75 million, −21,000 trips. Mixed causes (inflation, tariffs, late molt). Not model lift.

### Cost of false alert

Steam and bait on a weak cell; pulling gear from a better one. Social cost: if the product leaked locations, **negative** EDV from lost trust (uncountable; treat as a hard constraint, not a term to optimize).

### Cost of missed event

Fishing a declining inshore cell while a coarsened neighbor is better — possible given ASMFC note that inshore harvest is highly recruit-dependent and inshore surveys show stronger declines. Still **not** a local 24h forecast.

### Pricing hypothesis (UNTESTED)

Private co-op tool. Public consumer map is incompatible with EDV (destroys the data).

### EDV status

**Cannot be computed** without permissioned haul CPUE.

---

## Cross-wedge comparison (decision economics only)

| | W1 | W2 | W3 |
| --- | --- | --- | --- |
| Event frequency in a 90-day autonomous run | High in summer | Only open days | High |
| Public $ at industry scale | $107M WA Pacific oyster sales (2023) | Disaster $ at CPFV/state scale | $461M ME lobster (2025 prelim.) |
| Unit of action | Crew-tide | Trip | Trip / haul set |
| Measurable in 14 days? | Yes, if 1 farm logs | Yes, if 5 boats log open days | Yes, if 8 boats log |
| EDV computable now? | No | No | No |
| Lethal EDV failure mode | Food-safety impersonation | Season closure + spot map | Location leak + whale-rule impersonation |

**Ranking for *ability to measure EDV inside the 48h budget after founder lock*:** W1 > W2 (if season open) > W3 (more boats needed).

---

## What not to monetize in v0

- Insurance or “mortality guarantee”
- Quota/lease speculation
- Public paid hotspot maps
- Food-safety API
- Hardware sensors (prompt: exhaust public → partner export → existing sensors first)

---

## Sources

| Claim | Source | URL | Tier | Confidence |
| --- | --- | --- | --- | --- |
| WA Pacific oyster 114 farms, $106.801M (2023) | USDA NASS Census of Aquaculture Table 19 | https://www.nass.usda.gov/Publications/AgCensus/2022/Online_Resources/Aquaculture/AQUA.txt | 2 | High |
| PSI 20–80% summer losses | Pacific Shellfish Institute | https://www.pacshell.org/triploid-oyster-health.asp | 2/4 | Medium (research page, not a census) |
| 2021 heat-dome shellfish impacts | Raymond et al. 2022 *Ecology*; UW News; WSG RRN | https://doi.org/10.1002/ecy.3798 ; https://www.washington.edu/news/2022/06/21/2021-heat-wave-perfect-storm-shellfish-die-off/ ; https://waseagrant.uw.edu/our-programs/seafood-fisheries-aquaculture/aquaculture/rapid-response-network/ | 1/2 | High on mechanism; medium on “1 billion” (WSG says “one estimate”) |
| CA 2023 CPFV disaster allocation | CDFW draft spend plan | https://ncgasa.org/wp-content/uploads/2024/04/2023-California-Salmon-Disaster-Spend-Plan-Draft_040324.pdf | 2 | Medium (draft hosted by NCGASA) |
| CA 2024 100% / $36.35M | NOAA disaster determination | https://www.fisheries.noaa.gov/s3/2024-12/CA-Salmon-Determination-2024.pdf | 1/2 | High |
| ME lobster 2025 prelim. | DMR table + news | https://www.maine.gov/dmr/sites/maine.gov.dmr/files/inline-files/lobster_table.pdf ; https://www1.maine.gov/dmr/news/fri-03062026-1200-2025-maine-commercial-fisheries-value-again-tops-600-million | 2 | High (preliminary) |
| GOM/GBK overfishing 2025 | ASMFC | https://asmfc.org/species/american-lobster/ | 2 | High |
