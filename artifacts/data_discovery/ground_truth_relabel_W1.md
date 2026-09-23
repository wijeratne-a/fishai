# W1 ground-truth relabel (DOH closures are not ops GT)

**Date:** 2026-09-18 (follow-up)  
**Scope:** `artifacts/data_discovery/` only. No ingest. No training.

## What was wrong

DATA_DISCOVERY_AGENT originally ranked **WA DOH commercial growing-area closures** as the #1 source (SPS 0.885) and described them as **public 24–72h disruption labels / ground truth** for W1 farm operational stress. That mixed a **food-safety harvest-authority product** with the **ops-stress model target**.

Sibling agents contradict that mix. This file records the correction.

## Corrected W1 GT definition

| Item | Correct definition |
|------|-------------------|
| Model target | `ops_disruption_72h` |
| Label source | Partner farm logs: **mortality**, **workability** (can crew work the tide/gear), **intervention** (early harvest, re-submerge, shade, move) |
| Not the label | WA DOH / NSSP growing-area class, commercial closures, fecal coliform, biotoxin tissue results, WAHH harvest volume |
| DOH closures role | Official **harvest legally open?** **CONSTRAINT** and **user-facing authority link**. Must show. Must not impersonate. |
| Legal blocker | Using closures as the ops-stress target, or ops-stress copy as harvest legality, is a **BLOCKER** (WAC 246-282-006). Never impersonate NSSP/WA DOH harvest or food-safety authority. |

Public closures **miss heat-kill and gear damage when harvest stays legally open**. Hood Canal ORCA (Twanoh, Hoodsport, Dabob) is **not** Willapa instrumentation and is **not** a substitute for Willapa farm labels.

## Sibling-agent conflict table

| Agent | Finding | Discovery catalog (before) | Discovery catalog (after) |
|-------|---------|----------------------------|---------------------------|
| Marine domain | DOH growing-area class is the **wrong label** for farm operational stress | Closures treated as public GT / disruption outcome | Closures = harvest-open constraint only |
| Validation | Official DOH/NSSP closure is **CONTEXT**, not the food-safety or ops-stress label. Label is `ops_disruption_72h` from partner farm mortality/workability/intervention | Closures as 24–72h labels; partner logs “needed” as extra | Partner logs = sole ops GT; DOH = context/constraint |
| Red team | Using closures as the model target / ops-stress copy as harvest legality is a **BLOCKER** (WAC 246-282-006) | “Never as NSSP authorization” in copy, but still trained-on-closures implied | Explicit: do not train `ops_disruption_72h` on DOH; do not output harvest authorization |
| Data rights | Never impersonate NSSP/WA DOH harvest or food-safety authority | Constraint language mixed with “outcome” | Authority link + UNKNOWN license; no impersonation |
| This agent (original) | Public official outcome exists at event timescale; therefore W1 has the best lawful GT path | Rank #1 SPS 0.885 as GT | **Withdrawn.** W1 remains the best lawful **constraint + covariate** path, not because DOH is GT |

## Score change (0–1 scale unchanged)

| source_id | Role | Old SPS | New SPS | P0? |
|-----------|------|--------:|--------:|-----|
| WDOH-GROWING-AREA-CLOSURES | Must-show harvest-open constraint; not ops GT | 0.885 (DR 1.00, EPL 0.85) | 0.745 (DR 0.90, EPL 0.30) | Yes (constraint) |
| PARTNER-FARM-OPS-LOGS | `ops_disruption_72h` GT | 0.780 already P0 | 0.780; fallback `none` (no public ops label) | Yes (label) |

`expected_predictive_lift` dropped because closures do not lift an **ops-stress** model; they overlay **is harvest legally open**. Decision relevance stays high because the product **must display** the official status.

## W2 / W3 recheck (no factual error found)

| Claim | Status |
|-------|--------|
| RecFIN CTE001 **excludes salmon**; use the salmon report | **Kept.** CTE001 report text still the evidence. |
| W2 24–48h encounter GT = partner charter logs; RecFIN/ODFW are lagged | **Kept.** |
| Maine LEEDS harvester microdata `commercial_use_allowed = NO` | **Kept.** |
| NOAA VTR confidential (NAO 216-100 / 50 CFR 600); public rule-of-3 only | **Kept.** |
| Public DMR landings lack effort and are not next-trip CPUE | **Kept.** |

Do not analogize W1’s DOH mistake onto W2/W3: PFMC/CDFW season status and ALWTRP are already cataloged as **constraints**, not encounter/CPUE labels.

## Files touched

- `data_catalog.csv` (regenerated from `_build_catalog.py`)
- `source_gap_analysis.md`
- `data_source_priority_queue.md`
- `data_acquisition_plan.md`
- `agent_handoff.md`
- `scoring_and_verification.md`
- this file
