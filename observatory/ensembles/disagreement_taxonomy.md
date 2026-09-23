# Disagreement taxonomy

**Date:** 2026-09-18  
**Status:** Controlled vocabulary for contestability panels, planner tickets, and (later) globe `Disputed` modifiers.  
**Rule:** every disagreeing issuance carries **at least one why-code**. “Models differ” is not a why-code.

Disagreement is **scientific**. It is not a UI error, not a failed load, and not a reason to average until the colors match.

---

## 1. Top-level state

| State | When | User phrase |
|---|---|---|
| `AGREE` | \(D = 0\), all required eligible members same band, no incomparable overlay | “Baselines agree on this band.” |
| `DISAGREE` | \(D \ge 0.5\) among eligible members | “Baselines disagree. Both views are shown.” |
| `DATA_GAP` | Required member `cannot_issue` **or** `MC-HUM` expected but missing **or** partner outcome density low | “Not enough observations / logs to compare.” |
| `INCOMPARABLE_QUANTITY` | Same-object test failed (habitat vs CPUE, OSI vs DOH, …) | “These are different quantities. They are not averaged.” |
| `WITHHELD` | Privacy / rights / red-team suppression | “Not shown.” |

`DATA_GAP` may coexist with `DISAGREE` (example: B4 High vs B12 Typical **and** no farm logs). Store both codes.

`AGREE` + `ood_flag` is allowed: “Agree, extrapolated.” Do not upgrade to High confidence.

---

## 2. Why-codes (disagreement / gap)

Use these strings. Multiple allowed. Order by mechanism, not by which member “won.”

| Code | Meaning | Typical W1 pattern | What would resolve it |
|---|---|---|---|
| `DISAGREE_SPARSE_DATA` | Thin local history; climatology shrinks hard to parent; rule uses env now | New lease; B12 pulled to basin-month; B4 uses today’s tide×air | More farm-days in **this** unit (still PRIVATE) |
| `DISAGREE_DATA_GAP` | A required input or label stream is missing | No partner mortality/workability log; no farm wave threshold; no emersion geometry | Permissioned logs, partner threshold, culture metadata |
| `DISAGREE_UNUSUAL_OCEAN` | Env state is rare vs the climatology table | Heat×midday emersion analog; storm workability; hypoxia in a heat-climatology cell | Event-class features (AHW not MHW); holdout scoring of 2021-type days |
| `DISAGREE_ECOLOGICAL_ASSUMPTIONS` | Members encode different mechanisms | B4 air×emersion vs B12 month-rate; or someone proposes SST kill-law (rejected member) | Keep both **honest** members; do not average mechanisms into one cause |
| `DISAGREE_CONFLICTING_OBS` | Two observations of the **same** quantity disagree | Grower `MC-HUM` “already watching” vs B4 Typical; two stations offset | Provenance panel; distance-to-lease; do not pick a winner in the map color |
| `DISAGREE_EXTRAPOLATION` | At least one member is outside training / envelope | New basin, new culture method, new gauge-era analogue, novel AHW | OOD flag; suppress costly action options |
| `DISAGREE_UNRESOLVED_BIOLOGY` | Missing process that would change the label | Ploidy unknown; delayed mortality vs 72h; disease/HAB not in OSI | Stratify; do not pretend OSI-72 is % dead |
| `DISAGREE_QUANTITY_MISMATCH` | Alias of `INCOMPARABLE_QUANTITY` when a candidate class is **displayed as blocked** | Habitat “suitable” chip next to OSI High | Remove from mean; separate legend |

User-requested buckets map 1:1:

| Plain language | Code |
|---|---|
| Sparse data | `DISAGREE_SPARSE_DATA` |
| Unusual ocean | `DISAGREE_UNUSUAL_OCEAN` |
| Different ecological assumptions | `DISAGREE_ECOLOGICAL_ASSUMPTIONS` |
| Conflicting observations | `DISAGREE_CONFLICTING_OBS` |
| Extrapolation | `DISAGREE_EXTRAPOLATION` |
| Unresolved biology | `DISAGREE_UNRESOLVED_BIOLOGY` |

`DISAGREE_DATA_GAP` is the extra code for **missing farm logs / missing clauses**, which is the W1 fixture motif.

---

## 3. What disagreement is not

| Not a why-code | Handle as |
|---|---|
| Source outage | `missing_data_state` + confidence Low/None; may also `DISAGREE_DATA_GAP` |
| Official DOH closed vs OSI Typical | **Not disagreement.** Separate modules. Never a why-code that invites a blended harvest score |
| Two depths (air vs water) | Different drivers, same OSI product — show as **inputs**, not two biological fields |
| Neighbor farm died | PRIVATE; do not import as this cell’s observation |
| Candidate SDM “present” vs OSI | `INCOMPARABLE_QUANTITY` |

---

## 4. Severity for copy (not a color of fish)

| Severity | Rule of thumb | Copy |
|---|---|---|
| `info` | \(D=0\), in-domain | Members agree. Still not food-safety. |
| `watch` | \(D=0.5\) or DATA_GAP with Typical/Elevated | Treat as a watch. Both views shown. |
| `action_relevant` | \(D=1\) or High member vs Typical climatology | Do not hide the High member. Planner eligible. |
| `blocked` | Incomparable or withheld | No mean. No combined chip. |

Severity is **not** confidence. A High-vs-Typical split can still have Low confidence if sensors are stale.

---

## 5. Contestability log (required internally)

When state ≠ `AGREE` (or when `AGREE` + OOD):

```text
contest_id
forecast_id / fixture_id
codes[]
members_involved[]
quantity_class
who_can_see          partner | internal | coarsened_public
resolution_hypothesis
planner_ticket_id    or none
```

Public coarsened cells may show **environmental** disagreement (B4 vs B12) **without** farm outcomes. They may **not** show which lease’s logs are missing in a way that isolates a producer.
