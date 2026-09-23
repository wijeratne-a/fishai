# Go / No-Go Scorecard — Ocean Intelligence Builder / FishAI

**Agent:** QUALITY_AND_VALIDATION_AGENT  
**Date:** 2026-09-18  
**Version:** `GONOGO-2026-09-18-v1`  
**Wedge:** UNRESOLVED  
**Models trained:** none  
**Bulk ingest:** none  

All numeric thresholds are **HYPOTHESES** to be revised after the first honest retrospective and the first prospective window. They are not performance claims.

---

## 1. How to use this card

Fill **Section 3 (ML gates)** on every iteration.  
Fill **Section 4** only for the **locked** wedge.  
Fill **Section 2** until a wedge is locked (feasibility comparison).  
Fill **Section 5** for stop / diminishing returns.

**Decision vocabulary:**

| Verdict | Meaning |
| --- | --- |
| GO | Evidence supports the stated claim at the stated scope |
| CONDITIONAL | Continue narrowly; do not expand species/region/model class |
| NO-GO | Do not deploy that claim |
| STOP | Hit a project stop condition; founder decision required |
| PAUSE | Waiting on partner, rights, season open, or human input |
| DESIGN_ONLY | Protocol exists; no empirical score yet |

**Today’s overall verdict:** `PAUSE` + `DESIGN_ONLY`. Gate 1 (wedge) is open. Advanced ML is **blocked**.

---

## 2. Unified candidate panel (validation path, not a product ranking)

Quality’s job is whether a forecast can be *shown* to be better, not whether it will sell.

| Criterion (0–5, hypothesis rubric) | A Oyster WA 72h ops risk | B Chinook CA/OR 24–48h encounter | C Lobster GOM next-trip CPUE |
| --- | --- | --- | --- |
| Target label specifiable | 5 — binary ops disruption defined | 5 — trip encounter defined | 5 — soak-adj CPUE defined |
| Public GT at product grain | 1 — no farm mortality series | 2 — RecFIN/CRFS monthly/district; CPFV logs lagged | 3 — 100% ME trip reports since 2023 but monthly lag + 1 TMS/trip |
| Partner GT path | 4 — if 3 farms log daily | 4 — if ≥3 charters log zeros+effort | 4 — if ≥8 vessels log trip CPUE |
| Rights likely (pending rights agent) | 2 — partner DUA + official closure display review | 2 — public estimates vs log microdata | 2 — harvester microdata is not open commercial |
| Baseline feasibility | 3 — expert air×emersion×wave rules (SST/DO supporting only; 19 °C SST kill-law dropped; gates HYPOTHESIS) | 4 — spatial-month CPUA | 5 — persistence + TMS-month |
| Honest validation feasible | 3 — rare events; basin SAC | 3 — strong year effects; visited-cell only | 4 — dense trips if data licensed |
| Leakage / proxy risk | 4 high — closure-as-label; sensor circularity | 5 high — AIS; unfished-as-absent; run-size memorization | 4 high — effort confounding; reporting bias |
| Calibration / uncertainty tractable | 3 — sparse positives | 3 — prevalence swings by year | 4 — continuous y |
| Prospective seasonality / downtime | 3 — need summer | 2 — need open Chinook season | 4 — year-round in much of GOM |
| Outcome-linkage potential | 5 — daily farm ops | 4 — post-trip form | 4 — trip ticket |
| **Min GT ready now?** | **NO** | **NO** | **NO** (not in this repo; not ingested) |
| **Advanced ML** | BLOCKED | BLOCKED | BLOCKED |

**Quality recommendation on *validatability* (not commercialization):**

- If **partner farms** can be signed: Candidate A has the cleanest action-labeled risk product, provided closures stay context-only.
- If **only public fisheries data** is available in 30 days: none of the three supports a 24–72h claim; the least-wrong *research* backtest is **lobster climatology vs persistence** at TMS-month (still not “next-trip”).
- Candidate B’s public CPUA is the most tempting **false** 24–48h GT and should be treated as B12 only.

Founder pick should combine this card with PRODUCT (willingness to pay) and RIGHTS (what can actually be used). Quality does **not** lock the wedge.

---

## 3. Eight gates before advanced ML

| # | Gate | Pass rule | Status 2026-09-18 | Evidence |
| --- | --- | --- | --- | --- |
| 1 | Wedge defined | One species × geography × customer × decision in `project_state.json` | **FAIL** | UNRESOLVED by design |
| 2 | Target label defined | Single primary label + exclusions | **CONDITIONAL** | Proposed in validation_protocol §4; not locked |
| 3 | Ground truth available | Min dataset in hand, approved rights | **FAIL** | No partner logs ingested; none in repo |
| 4 | Rights approved | All train/eval/feature sources APPROVED_* | **FAIL** | Pending DATA_RIGHTS; no ingest |
| 5 | Baseline defined | Five families specified | **PASS (spec)** | baseline_model_spec.md; none fitted |
| 6 | Validation protocol approved | Temporal + spatial honesty + prospective | **PASS (design)** | validation_protocol.md; not yet generating splits |
| 7 | Red-team no unresolved blocker | High-severity closed or bounded | **UNKNOWN** | Sibling agent; assume open until report exists |
| 8 | Prediction contract defined | 14 fields; C or D; disclaimers | **CONDITIONAL** | Outlines in protocol; PRODUCT owns UX copy |

**Aggregate ML gate:** **CLOSED.** Do not train advanced models.

Checkboxes for later:

- [ ] Gate 1 pass date: ____  
- [ ] Gate 2 pass date: ____  
- [ ] Gate 3 pass date: ____  
- [ ] Gate 4 pass date: ____  
- [ ] Gate 5 fitted baselines date: ____  
- [ ] Gate 6 splits generated date: ____  
- [ ] Gate 7 red-team sign-off: ____  
- [ ] Gate 8 contract URL: ____  
- [ ] Advanced ML allowed: NO

---

## 4. Locked-wedge empirical card (fill after Gates 1–3)

Copy this table into each iteration report.

### 4.1 Header

| Field | Value |
| --- | --- |
| Locked wedge | |
| Label | |
| Primary metric | |
| Relevant baseline | |
| Eval windows | retro time-forward / spatial / prospective |
| n independent | |
| Completeness of outcomes | |

### 4.2 Hypothesized numeric thresholds by candidate

Use the row matching the locked wedge. Do not mix.

#### A — Oyster 72h risk (hypotheses)

| Decision | Recall @ P≥0.40 | False alerts / farm-month | Onset median lead time | BSS vs B12 | vs B4 | Outcomes |
| --- | --- | --- | --- | --- | --- | --- |
| GO (customer superiority) | ≥ 0.60 | ≤ 3 | ≥ 12 h | ≥ 0.10 | beat recall@P or EDV | ≥70% days logged; ≥15 independent events in pilot **or** pre-registered rarity plan |
| CONDITIONAL | 0.45–0.60 | ≤ 3 | ≥ 6 h | > 0 | mixed | skill in one basin only |
| NO-GO deploy | < 0.45 | — | — | — | — | |
| STOP model complexity | < 0.40 after **2 major iterations** | > 6 | — | no beat | no beat | or no logging |

Min GT to **start** B4/B12 fitting: 3 farms, 2 seasons, 1,500 farm-days, **30** independent events. Below that: collect, do not boost.

#### B — Chinook 24–48h encounter (hypotheses)

| Decision | AUROC | PR-AUC vs B12 | BSS | Top-20% visited-cell lift | ECE | Other |
| --- | --- | --- | --- | --- | --- | --- |
| GO | ≥ 0.65 | ≥ +0.08 | ≥ 0.05 | ≥ 1.30 | ≤ 0.08 | zeros logged; no AIS-as-abundance; open-season only |
| CONDITIONAL | ≥ 0.60 | +0.03–0.08 | > 0 | ≥ 1.15 | ≤ 0.12 | one year/district only |
| NO-GO deploy | < 0.60 | ≤ 0 | ≤ 0 | < 1.10 | — | catch-guarantee language |
| STOP model complexity | < 0.55 after 2 major iterations | no lift | no lift | — | — | or captains will not log zeros |

Min GT to start advanced ML: **≥600** labeled partner trips / **≥400** to fit B12+B3 only (hypothesis). Public monthly CPUA never starts a 24–48h GO.

#### C — Lobster next-trip CPUE (hypotheses)

| Decision | Spearman ρ | Top-quartile lift | MAE_log1p vs B3 | vs B12 | 80% PI coverage | Bias slices |
| --- | --- | --- | --- | --- | --- | --- |
| GO | ≥ 0.35 | ≥ 1.20 | ≤ 0.85 × B3 | ≤ B12 MAE | 0.70–0.90 | lift not only high-liners |
| CONDITIONAL | ≥ 0.25 | ≥ 1.10 | < B3 or < B12 (not both) | mixed | 0.60–0.95 | one zone; or rank-only |
| NO-GO deploy | < 0.25 | < 1.05 | worse than both | worse than both | — | dealer-only pounds |
| STOP model complexity | no beat of **both** B3 and B12 after 2 major iterations | | | | | or no effort fields |

Min GT: **2,000** trips retrospective (post-2023 era if using ME reports); prospective **400** issued+realized. Partner same-day logs required to claim next-trip rather than next-month.

### 4.3 Non-ML GO (product still allowed)

A **baseline-packaged brief** may GO to a **paid or design pilot** if:

- Gates 1, 2, 4, 8 pass (label + rights + contract)
- B4 or B12 is issued with uncertainty policy
- Outcome capture is live
- No advanced-ML superiority language is used

This is the preferred path when GT n is below advanced-ML minima.

---

## 5. Stop conditions (quality-owned subset)

Trigger STOP or PAUSE and write `STOP_DECISION_MEMO.md` (orchestrator) if:

1. No viable ground truth at product grain after a good-faith partner attempt (hypothesis: 30 days post-wedge-lock).  
2. Advanced model fails to beat relevant baseline after **two major iterations**.  
3. Customer will not share minimum outcomes (completion < 50% for 14 days after onboarding).  
4. Data quality cannot support the claim (dashboard hard fail on legal, privacy, or label resolution).  
5. Confidence is Low on >80% of issuances for 28 days (hypothesis) — product not actionable.  
6. Red-team high-severity leakage (AIS-as-abundance; closure-as-food-safety; exact-spot heatmap) unresolved.  
7. Claim would exceed evidence (Category A/B abundance, catch guarantee, harvest legality).  
8. Three consecutive iterations with no improvement in GT n, rights, baseline skill, or outcome completion (project-level diminishing returns).

**Diminishing returns (model):** stop complexity after two failed major iterations even if the broader project continues packaging baselines.

---

## 6. Traction / decision-value overlay (do not fake)

From project founder gates — quality only **records**, does not generate customers:

| 30-day evidence | Status |
| --- | --- |
| Interviews | not this agent |
| Design partners | 0 |
| Historical outcome dataset or DUA | 0 |
| Manual brief delivered | 0 |
| 90-day paid pilot / measured lift / behavior change | 0 |

A ML GO without any of the 90-day evidence is **internal-only**, never marketing.

---

## 7. Current recommended actions (quality)

1. **Do not train.**  
2. Lock wedge **or** keep three-track partner conversations, but do not ingest.  
3. For whichever wedge is chosen, execute the **minimum GT checklist** in Section 4.2 before features.  
4. Fit **only** B12/B3/B4 on the first lawful dataset.  
5. Red-team the first scorecard before any customer sentence that implies skill.

**Quality verdict for this pass:** protocols are ready; **no-go on modeling and on any forecast-quality claim.**
