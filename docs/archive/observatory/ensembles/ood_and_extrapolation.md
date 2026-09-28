# Out-of-domain and extrapolation flags

**Date:** 2026-09-18  
**Status:** Flag dictionary for `ENS-W1-OSI72-v0`. **No envelope fitted.**  
**Companion:** `artifacts/quality_and_validation/uncertainty_policy.md` (`IN_DOMAIN`, `extrapolation_flag`).

OOD is **not** disagreement. Members may agree and still be outside the world they were specified for. Members may disagree **because** one of them is in-domain (B4 on today’s tide×air) and the other is a thin climatology (B12).

---

## 1. Flag

```text
ood_flag                boolean
ood_dimensions[]        controlled strings
ood_severity            mild | hard
in_domain_category      high | medium | low     # from uncertainty policy; do not average
```

**Hard OOD** ⇒ member confidence cannot be High; ensemble mean suppressed; planner R3 if impact medium/high.

**Mild OOD** ⇒ Medium confidence ceiling unless other rules are worse.

v0 has **no training envelope percentiles** (nothing trained). Until a climatology table is fitted, treat OOD as **rule-based / expert** flags below, not as Mahalanobis distance.

---

## 2. Dimensions

| Dimension | W1 hard examples | W1 mild examples | Not OOD |
|---|---|---|---|
| `space` | Issuing Willapa climatology in Hood Canal or a new estuary | Adjacent growing area with shared basin parent | Another cell in the same growing area |
| `season` | Winter rule applied to a summer-only event table (or the reverse) | Shoulder month | July vs August inside a Jun–Sep table that includes both |
| `climate` | Atmospheric heatwave + midday emersion analog (2021-type AHW); documented novel hypoxia for **this** bay | Seasonal marine heatwave **SST** anomaly **without** emersion overlap (wrong event class — log as supporting, do not promote) | Ordinary warm week inside training months **once a table exists** |
| `management_era` | n/a for OSI-72 harvest rules (those are DOH, not this model) | Change in farm gear that alters emersion | DOH classification change (context module, not OOD of OSI) |
| `culture_or_farm` | Subtidal float scored with intertidal B4; unknown ploidy pooled; new farm with no local B12 | Sparse shrinkage \(n/(n+k)\) toward parent | Second zone of the **same** permissioned farm in the same bay (still not independent for CV) |
| `missing_envelope` | No B12 table at all; B4 thresholds unlocked (HYPOTHESIS only) | One supporting sensor missing | Dropped SST kill-law (that law must not exist) |
| `horizon` | Using 30-day delayed mortality as if it were 72h OSI | Scoring onset vs continuation without the split | 24h vs 72h inside the declared window |
| `platform` | (W2/W3) new vessel class — not W1 | — | — |

**Chinook/lobster (registry only):** add `management_era` (gauge, salmon opener) and `platform` (vessel). Do not copy those into W1 OSI.

---

## 3. Joint-failure pattern (must display)

| Pattern | `D` | `ood_flag` | Product |
|---|---|---|---|
| B4 High, B12 Typical, AHW-like air×emersion | 1 | often `climate` | **Canonical useful disagreement.** Do not average to Elevated. Planner P0 if logs missing. |
| B4 Typical, B12 Typical, AHW-like conditions **and** B4 still SST-based | 0 | `climate` **hard** | **Illegal member spec.** SST kill-law is not in the ensemble. Rebuild B4. |
| Both High, ordinary July climatology | 0 | false | Agree; still not food-safety. Outcome capture for validation, not a disagreement ticket unless logs missing. |
| B4 `cannot_issue` (no emersion clause, no wave threshold), B12 Typical | null | `culture_or_farm` or `missing_envelope` | DATA_GAP; not a quiet Typical. |
| Habitat suitability “high” vs OSI High | incomparable | n/a | Do not compute \(D\). |

Uncertainty policy: **High** confidence requires `IN_DOMAIN=high`. OOD hard ⇒ Low or None.

---

## 4. What must not be used as the OOD test

- Distance to the nearest OBIS point (effort, not ops-risk).  
- SST percentile (Hobday MHW) as a proxy for aerial heatwave.  
- “This cell is red on a global SDM.”  
- AIS density.  
- Neighbor-farm mortality (PRIVATE, and not this cell’s envelope).

---

## 5. Fixture flags

See [`fixture_cells.csv`](fixture_cells.csv) column `ood_flag` / `ood_dimensions`. All envelopes are **synthetic**. No percentile was computed on real Willapa series (no ingest).
