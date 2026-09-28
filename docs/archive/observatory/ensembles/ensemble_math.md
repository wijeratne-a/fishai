# Ensemble math (v0)

**Date:** 2026-09-18  
**Ensemble:** `ENS-W1-OSI72-v0`  
**Status:** Equations and issuance rules. **No weights estimated. No mean shipped.**  
**Principle:** weights come from **prospective / time-forward skill**, never from in-sample fit. **Disagreement is a product feature.** A single heatmap that hides member split is a ship block.

Literature pointer (not a FishAI result): averaging structurally different models can help *when they predict the same quantity* (Araújo & New 2007; Dormann et al. 2018). Averaging a bad abundance model with a good CPUE model is a category error (`ocean_model_comparison.md` §2.13).

---

## 1. Same-object test (must pass before any arithmetic)

Members \(i = 1,\ldots,m\) may enter a mean **only if** all of these match the ensemble target \(T\):

| Lock | W1 value |
|---|---|
| Quantity class | `operational_stress_indicator` |
| Prediction-contract category | **D** |
| Label | `ops_disruption_72h` (or the locked ordinal encoding of that label) |
| Horizon | 24–72h from `issued_at` |
| Spatial grain | Same issuance grain (PRIVATE farm-zone **or** the declared COARSENED public parent — never mix grains in one mean) |
| Universe | Stocked farm-days; out-of-universe ⇒ no score |
| Issued-at / as-of cutoff | Shared `issued_at`, `source_data_cutoff` |
| Culture stratum | Intertidal vs subtidal **not pooled** into one mean |

If the test fails: **incomparable**. Output `INCOMPARABLE_QUANTITY`. Do not compute \(\bar{s}\).

`MC-HAB`, `MC-OCC`, `MC-ST`, `MC-MECH`, `MC-FW`, `MC-PART` **fail this test today** because they are not W1 v0 members and/or do not emit OSI-72.

---

## 2. Member state (ordinal v0)

v0 does **not** print calibrated probabilities. Members emit an ordinal on the **same** comparison set (this lease or coarsened unit, similar tides, named season):

| Code \(s_i\) | Numeric map \(z_i\) | User chip |
|---|---|---|
| `typical` | 0 | Typical |
| `elevated` | 1 | Elevated |
| `high` | 2 | High |
| `cannot_issue` | `NA` | Cannot issue |

Optional `MC-HUM`: map pre-brief `{no → typical, already_planned / yes → elevated or high per form}` **only** with a written mapping locked before scoring. If unmapped, store raw form value; do not coerce.

Each member also carries, unchanged from `uncertainty_policy.md`:

`confidence_category`, `confidence_reasons[]`, `missing_data_state[]`, `extrapolation_flag`, `observation_density`, `input_freshness`.

---

## 3. Eligibility at issuance

Member \(i\) is **eligible** (\(e_i = 1\)) iff:

1. Same-object test passes.  
2. Output ≠ `cannot_issue`.  
3. Critical inputs for *that* class are fresh enough for a score (B4: air+tide for emersion culture; B12: training-cutoff climatology table exists).  
4. Rights allow the features used.  
5. Model card id is present (`governance_hooks.md`).

`e_i = 0` members are **shown** in the contestability panel with reason codes. They are **not** dropped quietly so the mean looks certain.

---

## 4. Weights (prospective skill only)

### 4.1 Until the first locked prospective (or honest time-forward) slice exists

\[
w_{i,r,s} = \frac{e_i}{\sum_j e_j}
\]

when \(\sum e_j \ge 1\). These weights are **`UNWEIGHTED_PLACEHOLDER`**. They **must not** be described as skill, importance, or “AI confidence.”

**v0 product default:** do **not** compute a mean at all. Show members. Set `ensemble_mean_status = suppressed_unvalidated`.

### 4.2 After a locked prospective window

Let \(\mathrm{skill}_{i,r,s}\) be the **pre-registered primary metric** for W1 on region \(r\) (growing area or basin) and season \(s\) (month or Jun–Sep), evaluated only on issuances with `available_at ≤ issued_at`:

- Primary: recall @ locked precision floor, false alerts / farm-month, onset lead time (quality protocol).  
- For blending on the ordinal/probability scale: **Brier skill vs the frozen relevant baseline** — but B12 *is* a baseline. Do not award B12 skill-vs-self as if it were a model.

**Rule:** a *candidate* class (when gates pass) gets weight from \(\max(\mathrm{BSS}_{i,r,s}, 0)\) or from decision-value lift vs **frozen** `{B4, B12}`, **never** from training-year AUROC.

\[
w_{i,r,s} \propto e_i \cdot \max(\mathrm{skill}_{i,r,s}, 0)
\]

then renormalize over eligible members. If all skills ≤ 0, **revert to unweighted placeholders** and set `ensemble_mean_status = suppressed_no_skill`.

**Forbidden:**

- In-sample BSS, random-split AUROC, or peeking at the test year to set \(w\).  
- A single global weight that hides a basin where B4 fails.  
- Zeroing B4 because it “disagrees with climatology” during an AHW analog — that disagreement is the point.  
- Using `MC-HUM` logs that were entered **after** the brief as weights (leakage).

Slice rule (quality): if a region×season cell has too few independent events, `skill = NA — underpowered`. Do not borrow a neighbor basin’s weight without an explicit transfer flag.

---

## 5. Ensemble mean (optional, suppressed by default)

If and only if `ensemble_mean_status = issued` (governance + ≥2 eligible members + not a hide-the-split case):

\[
\bar{z} = \sum_i w_i z_i, \quad z_i \in \{0,1,2\}
\]

Map back with **non-hiding** thresholds (hypothesis; lock later):

| \(\bar{z}\) | Band | Condition |
|---|---|---|
| \(\bar{z} < 0.5\) | `typical` | No eligible member is `high` |
| \(0.5 \le \bar{z} < 1.5\) | `elevated` | No eligible member is `high` **or** disagreement index \(D < 0.5\) |
| \(\bar{z} \ge 1.5\) | `high` | — |

**Hard override (non-negotiable):**

If any eligible member is `high` **and** \(D \ge 0.5\), **do not** emit a mean of `typical` or `elevated`. Either:

- suppress the mean and show the split, or  
- emit mean = `high` **and** `disagreement_index` with reasons (still show both members).

Hiding a B4 heat×emersion **High** behind a B12 **Typical** is the failure mode this folder exists to prevent.

If a probability scale is ever approved by a human reviewer from a **prospective** reliability diagram:

\[
\bar{p} = \sum_i w_i p_i
\]

still emit \(\{p_i\}\), \(D\), and OOD. Do not print three-decimal \(\bar{p}\) in v0.

---

## 6. Disagreement index \(D\)

For eligible members with numeric \(z_i\):

\[
D = \frac{\max_i z_i - \min_i z_i}{2} \in \{0,\,0.5,\,1\}
\]

With exactly two required members (B4, B12): \(D = |z_{\mathrm{B4}} - z_{\mathrm{B12}}| / 2\).

| \(D\) | Display |
|---|---|
| `0` | **Agree** |
| `0.5` | **Disagree** (adjacent bands) |
| `1` | **Disagree** (Typical vs High) |
| `null` | A required member `cannot_issue` or incomparable — use taxonomy `DISAGREE_DATA_GAP` / `INCOMPARABLE_QUANTITY`, not a fake \(D=0\) |

If `MC-HUM` is present and eligible, compute pairwise \(D\) against each machine member and store `D_max = max(D_{pairs})`. Human vs machine is **contestability**, not a third vote to wash out B4.

**Do not** replace \(D\) with the standard deviation of a secret list of candidate models that are not members.

---

## 7. Ensemble uncertainty (not the same as \(D\))

Three layers; all visible:

| Layer | v0 source | Must not claim |
|---|---|---|
| Member confidence | Uncertainty-policy rule (FRESH, DENSITY, IN_DOMAIN, …). Worse category wins; do not average High+Low into Medium | That the rule is calibrated |
| Spread | \(D\) and the set \(\{s_i\}\) | That spread is an 80% interval |
| Interval | **None** until a declared Bernoulli/conformal/quantile method is run and coverage scored | A decorative ± |

`ensemble_uncertainty_rationale` (hypothesis copy when unquantified):

> Members are simple baselines, not a calibrated posterior. Spread is scientific disagreement, not a confidence interval. No 80% band is printed because no coverage test has been run.

If later an interval is printed, failed coverage (outside 0.70–0.90 for a nominal 80%) **downgrades confidence to Low** and stops printing the interval (`uncertainty_policy.md` §3).

---

## 8. Validation by region and season

The ensemble is **not** validated as a single number.

For each eval kind (time-forward, out-of-year, spatial holdout, prospective):

1. Score **each member** on slices: basin / growing area × month (or Jun–Sep), culture type, observation density, freshness, extreme-event flag (AHW, hypoxia, storm).  
2. Score **disagreement calibration**: when \(D \ge 0.5\), which member matched the partner label? Rate of “B4 right / B12 right / both wrong / both right.”  
3. Score **mean** (if it was issued) vs members. If the mean is worse than the better member on the primary metric, **stop issuing the mean**.  
4. Never report only a pooled BSS that hides the high-value season.

Empty tables live in quality `forecast_scorecard_template.md`. This folder does not fill them (no ingest).

---

## 9. OOD interaction

`ood_flag` is independent of \(D\). Members can agree inside a novel climate (both `typical` during an AHW analog if B4 were mis-specified as SST-only). That is **joint failure**, not consensus. See [`ood_and_extrapolation.md`](ood_and_extrapolation.md).

If `ood_flag` and \(D = 0\), still show “agree, **extrapolated**” — never High confidence.

---

## 10. Issuance object (conceptual)

```text
ensemble_id            ENS-W1-OSI72-v0
issued_at              UTC
target                 ops_disruption_72h / OSI-72 / Category D
members[]              {member_id, class_id, s_i, z_i, e_i, confidence, missing[], ood, card_id, version}
weights[]              {member_id, w, weight_basis = UNWEIGHTED_PLACEHOLDER | PROSPECTIVE_SLICE_ID}
ensemble_mean          typical|elevated|high|null
ensemble_mean_status   suppressed_unvalidated | suppressed_hide_split | suppressed_no_skill | issued
disagreement_index     0 | 0.5 | 1 | null
disagreement_codes[]   taxonomy
ensemble_uncertainty   rationale (no fake interval)
ood_flag               bool
ood_dimensions[]
planner_score          see planner_handoff.md
publish_class          PRIVATE | COARSENED | ...
does_not_mean[]        food_safety, harvest_authorization, abundance, percent_dead
```

No `latitude`/`longitude` on COARSENED/PUBLIC. No neighbor-farm ids. No lease performance on public payloads.
