# Forecast Scorecard Template — Ocean Intelligence Builder / FishAI

**Agent:** QUALITY_AND_VALIDATION_AGENT  
**Date:** 2026-09-18  
**Version:** `SCORECARD-TMPL-2026-09-18-v1`  
**Status:** Empty template. No models scored. All numeric targets are **HYPOTHESES**.

Fill one copy per `iteration_id` × `candidate_id` × `eval_kind`  
(`time_forward` | `out_of_year` | `spatial_holdout` | `geographic_transfer` | `prospective_pilot`).

Mark every evaluation that used post-issuance revisions as `eval_data = retrospective_corrected` and **exclude** it from go/no-go.

---

## 0. Header (required)

| Field | Value |
| --- | --- |
| scorecard_id | |
| iteration_id | |
| date_filled | |
| candidate | A_oyster / B_chinook / C_lobster |
| wedge_locked | NO (2026-09-18) |
| label_id | |
| prediction_contract_category | C / D (A/B/E forbidden as product claim) |
| model_or_baseline_ids | |
| relevant_baseline_id | |
| eval_kind | |
| issued_at_range | |
| n_rows_raw | |
| n_independent_units | |
| n_positive_events | |
| prevalence | |
| spatial_block_rule | |
| SAC_range_estimate | |
| as_of_compliant | YES / NO |
| red_team_status | |
| evaluator | |
| claim_allowed | none / internal_only / customer_facing |

**Independent units:** farm-weeks (A), vessel-days (B), vessel-trips (C) unless a documented alternative.

---

## 1. Slice keys (always compute; never hide)

Fill metrics **overall** and for each slice level present in the data.

| Slice | Levels (adapt to wedge) |
| --- | --- |
| season | month or management season |
| subregion | growing area / CRFS district / lobster zone |
| habitat | depth band, estuary vs open coast, substrate if known |
| observation_density | low / medium / high terciles of local n |
| freshness | fresh / stale / missing-critical at issuance |
| platform | farm type, vessel class, gear |
| extreme | heatwave, hypoxia, storm, in-season closure, gauge-change era |
| skill_segment | high-liner vs others (C); targeting vs incidental (B) |

If a slice has < **10** independent units or < **5** positives, report `NA — underpowered` (hypothesis cutoffs). Do not average away NA slices.

---

## 2. Product-type metric blocks

Use **only the block that matches the product**. Other blocks may be filled as diagnostics but cannot be the go metric.

### 2.1 Occurrence / encounter (Chinook primary; oyster only if a binary diagnostic is used)

| Metric | Model | Relevant baseline | Δ | Slice | n | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| AUROC | | | | overall | | Secondary for imbalanced labels |
| PR-AUC | | | | overall | | **Chinook co-primary** |
| PR-AUC lift vs baseline | | 0 (ref) | | | | Hypothesis GO: ≥ +0.08 prospective |
| Brier | | | | | | Lower is better |
| Brier skill score (BSS) | | 0 (vs B12) | | | | Hypothesis GO: ≥ 0.05 Chinook; ≥ 0.10 oyster |
| ECE (10-bin, hypothesis) | | | | | | Hypothesis: ≤ 0.08 prospective |
| Reliability diagram | (attach) | | | | | Required |
| Precision @ locked T | | | | | | |
| Recall @ locked T | | | | | | |
| F1 @ locked T | | | | | | Do not optimize F1 after looking at test |
| Log loss | | | | | | Optional |

**Calibration plot required.** If probabilities are not issued, this block is incomplete for a Category D product.

**Chinook extra ranking (visited cells only):**

| Metric | Model | Baseline | Δ | n_visited_cells |
| --- | --- | --- | --- | --- |
| Top-20% lift (realized encounter rate ratio) | | | | |
| Top-20% lift (realized CPUE ratio) | | | | |
| NDCG@5 | | | | |
| Spearman (predicted score vs CPUE) | | | | |
| Hit rate: ≥1 encounter in top-k recommended cells | | | | |

**Hypothesis GO (Chinook prospective):** PR-AUC ≥ B12 + 0.08; AUROC ≥ 0.65; BSS ≥ 0.05; top-20% visited-cell lift ≥ 1.30; ECE ≤ 0.08.

**Hypothesis NO-GO:** AUROC < 0.55 or no PR-AUC/Brier lift vs B12 after two major iterations.

---

### 2.2 Continuous / CPUE (Lobster primary; Chinook secondary CPUE)

| Metric | Model | B3 persistence | B12 climatology | Best simple | Slice | n |
| --- | --- | --- | --- | --- | --- | --- |
| MAE (raw CPUE) | | | | | | Sensitive to outliers |
| MAE log1p(CPUE) | | | | | | **Lobster co-primary** |
| RMSE log1p | | | | | | |
| Spearman ρ | | | | | | **Lobster co-primary** |
| Pearson r (optional) | | | | | | |
| Pinball τ=0.5 | | | | | | |
| Pinball τ=0.8 | | | | | | |
| 50% PI coverage | | | | | | Target ~0.50 |
| 80% PI coverage | | | | | | Hypothesis band 0.70–0.90 |
| 80% PI median width | | | | | | Decision-useful? |
| Top-quartile lift | | | | | | Mean y in predicted Q4 / mean y elsewhere; **≥1.20 hypothesis** |
| NDCG@k TMS | | | | | | |
| Bias (mean ŷ − y) overall | | | | | | |
| Bias high-liner slice | | | | | | Must not reverse lift |
| Bias new-vessel holdout | | | | | | |

**Hypothesis GO (lobster prospective):** Spearman ≥ 0.35 **and** top-quartile lift ≥ 1.20 **and** MAE_log1p ≤ 0.85 × B3 **and** ≤ B12; 80% PI coverage 0.70–0.90.

**Hypothesis NO-GO:** neither MAE nor rank beats **both** B3 and B12 after two major iterations.

---

### 2.3 Risk-alert (Oyster primary)

Operating point **T locked before evaluation**. Do not sweep T on the test set. A ROC/PR curve may be shown as diagnostic with the locked T marked.

| Metric | Model | B4 expert-rule | B12 climatology | B3 persistence | Slice | n |
| --- | --- | --- | --- | --- | --- | --- |
| Recall @ locked T | | | | | | **Primary** |
| Precision @ locked T | | | | | | Floor hypothesis ≥ 0.40 |
| False alerts per farm-month | | | | | | **Primary constraint**; GO ≤ 3; NO-GO > 6 |
| Missed-event rate (1 − recall) | | | | | | |
| Median lead time (h), onset-only | | | | | | GO ≥ 12 h hypothesis |
| Mean lead time (h) | | | | | | |
| PR-AUC | | | | | | |
| Brier / BSS vs B12 | | | | | | BSS ≥ 0.10 hypothesis |
| Action rate (user did something) | | | | | | Prospective only |
| Value of action (currency or hours) | | | | | | If collected |
| Alerts during official closure days (context) | | | | | | **Not** a label; diagnostic leakage check |

**Onset vs continuation:** duplicate the recall/lead-time rows for **event onsets only** (no event in prior 7 days). Persistence will dominate continuation; go/no-go should emphasize **onsets**.

**Hypothesis GO (oyster prospective):** recall ≥ 0.60 at precision ≥ 0.40; false alerts ≤ 3/farm-month; onset median lead time ≥ 12 h; BSS vs B12 ≥ 0.10; beat B4 on recall-at-precision **or** on false-alert-adjusted decision value.

**Hypothesis NO-GO:** recall < 0.40 at that precision floor, or false alerts > 6/farm-month, or no beat of B4 on BSS and recall, after two major iterations.

---

## 3. Decision-value block (all products; required for customer-facing GO)

| Item | Value | Source |
| --- | --- | --- |
| Action considered | | PRODUCT |
| Cost of action | | interview / log |
| Cost of missed event | | interview |
| Cost of false alert | | interview |
| Value of true alert | | interview |
| P(event) in eval window | | scorecard |
| P(false alert) @ T | | scorecard |
| Expected decision value (model) | | formula in validation protocol §3.6 |
| EDV (relevant baseline) | | |
| Δ EDV | | |
| Behavior change rate | | % issued briefs where user changed plan |
| Outcome-form completion | | |

**Hypothesis:** customer-facing “better forecast” needs Δ EDV > 0 **or** measured behavior change ≥ 20% of completed briefs **or** paid pilot — not skill-in-sample alone.

---

## 4. Uncertainty performance block (all products)

See `uncertainty_policy.md`. If this block is empty, the scorecard **cannot** support a GO.

| Check | Result | Pass hypothesis |
| --- | --- | --- |
| High vs low confidence: Brier or MAE_log1p | | High strictly better than low |
| High vs low: actual coverage of stated interval | | Monotone |
| % issuances High / Medium / Low | | Not 100% High |
| Extrapolation flag rate | | Flagged cases have worse skill or are suppressed |
| Freshness-stale skill drop | | Stale ⇒ lower confidence issued |
| Suppression / “insufficient data” rate | | Documented; not silent |
| Opaque single score shipped? | YES/NO | Must be NO |

---

## 5. Leakage & protocol integrity (binary; any YES is a red-team hold)

| Test | Result (YES/NO) |
| --- | --- |
| Random row split used | |
| Future vintage used at issuance | |
| AIS used as abundance or label | |
| Official shellfish closure used as food-safety label | |
| Unfished cells treated as true negatives | |
| Test-set threshold fishing | |
| Partner overlap without partner-holdout when claiming transfer | |
| Same sensor as both label and feature (oyster circularity) | |
| Dealer landings without effort used as CPUE | |
| Overwritten historical forecasts | |

---

## 6. Narrative (required, ≤12 lines)

- What beat what, on which slice?  
- Where did it fail (failure taxonomy codes)?  
- Is lift large enough vs false-alert cost?  
- Is GT n above the minimum?  
- Allowed claim: none / internal / customer.

```
[narrative]
```

---

## 7. Unified candidate comparison (use while wedge UNRESOLVED)

This is **validation feasibility**, not a founder product pick.

| Item | A Oyster 72h risk | B Chinook 24–48h encounter | C Lobster next-trip CPUE |
| --- | --- | --- | --- |
| Contract | D risk | D claim, C evaluation | C CPUE |
| Recommended label | `ops_disruption_72h` | `encounter_48h` | soak-adj legal CPUE |
| Public GT sufficient for product grain? | NO | NO (monthly only) | PARTIAL (monthly TMS; lag) |
| Partner GT required? | YES | YES | YES for next-trip |
| Primary metric | Recall@P≥0.40 + false alerts/mo + lead time | PR-AUC lift + visited-cell top-20% lift | Spearman + Q4 lift + MAE_log1p vs B3/B12 |
| Relevant baseline to beat | B4 expert-rule and B12 | B12 spatial-month; B3 persistence | B3 persistence **and** B12 |
| Biggest validity threat | Event rarity; sensor-label circularity; closure leakage | Interannual run size; zeros; AIS temptation; coarse public CPUE | Reporting lag/bias; one TMS/trip; high-liner; gauge-era |
| Advanced ML allowed 2026-09-18 | NO | NO | NO |

---

## 8. Filing

Save filled scorecards to (future):  
`/Users/wijeratne/dev/fishai/evaluation_reports/SCORECARD_<candidate>_<eval_kind>_<date>_<iteration>.md`

Do not fill with synthetic metrics. Empty cells > fake lift.
