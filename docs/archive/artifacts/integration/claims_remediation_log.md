# Claims remediation log — FishAI

**Date:** 2026-09-18  
**Agent:** COMMERCIAL_LAYER_INTEGRATOR  
**Why this log exists:** Scientific red team found that the product “SAFE brief” and the quality expert-rule baseline would be copy-pasted into a live email as harvest/Vp advice and as an SST≥19°C mortality law. Those artifacts were patched **in place**. Unsafe copy is not left as the SAFE brief. This does **not** close HIGH/BLOCKER scientific items (no human reviewer, no labels, no validation run).

**Not done:** wedge lock; ingest; training; writes under `observatory/`; full dossier rewrites.

---

## Binding rule applied

`artifacts/scientific_red_team/prediction_contract.md` is the only approved claim language. Default public category C or D. Ceiling = strongest evidence tier. Two or more agents already agree → **halt customer-facing model claims**; later pilot may be a **manual** decision brief after founder lock.

---

## Changes

### 1. Product sample brief (RT-SIB-02 / B-SIB-02) — HIGH copy, patched

**Problem:** Sample email/PDF used **Totten Inlet analog** (2026 WA DOH Vp Category 3 harvest-control area), rank **“top ~20%”**, driver 1 **water temp +1.8 °C**, harvest-adjacent options, SST-first thermal story, medium confidence without sensors.

**Fix:** Rewrote the customer-facing mocks to **Category D operational stress / work-window only**, **Willapa DOH growing areas**, **14 contract fields**, **hard WA DOH Module B** (attributed, timestamped, not combined with ops score), drivers **air × daytime emersion × solar** then **wind/wave workability**, water T/DO/S **supporting with lag/mismatch**, **terciles** not top 20%, **no commands**, **no one-decimal fake anomalies**, confidence **Low** when forecast-only, visible limitations on every mock.

| File | What changed |
|---|---|
| `artifacts/product_and_monetization/product_thesis.md` | Claims-halt banner; Chinook v0 SST/chl **halted**; contract-aligned safe language; full sample brief replaced (`OY-WA-SAMPLE-2026-09-18-B`); Candidate A geography/v0 data aligned to Willapa + air×tide |
| `artifacts/product_and_monetization/MVP_workflow.md` | Claims halt; subject line Totten → Willapa; Low conf; air×emersion drivers first |
| `artifacts/product_and_monetization/product_MVP_workflow.md` | Snapshot: Willapa; forbid Totten/top-20%/SST-as-body-T |
| `artifacts/product_and_monetization/wireframe_spec.md` | Email + PDF + WhatsApp + Chinook/lobster mocks + outcome-form limitation line |
| `artifacts/product_and_monetization/pilot_offer.md` | Not a model score; SST ≠ body temperature; no combined ops+sanitation score |

### 2. Validation expert-rule baseline (RT-SIB-01 / B-SIB-01) — HIGH copy, patched

**Problem:** B4 alerted on **SST ≥ 19 °C for ≥12 h** (growth/clearance band, not a WA intertidal mortality law) plus Hobday **marine** heatwave as a 72h oyster rule. Quality handoff repeated “expert-rule (SST/DO/wave/heatwave).”

**Fix:** B4 primary = **air × low-tide emersion × solar** and **wind/wave workability**. SST/DO/salinity = **supporting covariates** with documented lag/mismatch. **Forbidden default:** SST ≥ 19 °C. Hobday MHW **dropped** as a default 72h oyster rule (wrong event class vs atmospheric heatwave × midday emersion). **All numeric gates labeled HYPOTHESIS.** Closures still excluded from B4.

| File | What changed |
|---|---|
| `artifacts/quality_and_validation/baseline_model_spec.md` | B4 rewritten; intro SST-threshold language removed; B5 “harvest plans” → husbandry/gear/crew-timing; Chinook B4 marked not customer-facing |
| `artifacts/quality_and_validation/agent_handoff.md` | B4 description aligned (air×emersion×wave; SST/DO/S supporting) |
| `artifacts/quality_and_validation/go_no_go_scorecard.md` | Baseline feasibility no longer scores a 19 °C SST kill-law as “4” |
| `artifacts/quality_and_validation/uncertainty_policy.md` | Chinook rank band = terciles, not “top 20%” |

### 3. “Safely work” / harvest-plan leak (RT-SIB-03) — HIGH copy, patched surgically

| File | What changed |
|---|---|
| `artifacts/requirements_and_wedge/recommended_initial_wedge.md` | Metric B: workably/productively, **not safety-certified**, not weather-safety advice |
| `artifacts/quality_and_validation/baseline_model_spec.md` | B5 prompt never says “harvest plans” |

### 4. Limitation language on customer-facing examples

Visible limitations added on: product thesis sample, wireframe email/PDF/WhatsApp/form, MVP subject path, pilot-offer disclaimers. Pattern: Category D; not food-safety; not harvest; air×tide×solar ≠ body temperature; tercile ≠ probability; DOH module separate; format mock / no model.

---

## Explicitly not treated as cleared

- B-ALL-01…08, B-OYS-01…05, Chinook and lobster blockers
- RT-SIB-04 (Chinook thermal-habitat-with-depth as v1) — **halted in product/quality copy**, marine-domain dossier **not** rewritten
- RT-SIB-05…07 — scorecard identifiability, H3 product grain, AIS diagnostic; noted in synthesis only
- Any live send of a brief
- Red-team register rows remain **OPEN** until a **named human** signs (this agent is not that reviewer)

---

## What we refused to do

- Lock W1/W2/W3 in `config/project_config.json`
- Change `current_state` off `STATE_10_PAUSED_FOR_HUMAN_DECISION`
- Ingest data, train models, or write under `observatory/`
- Invent elapsed hours
- Leave Totten / top-20% / +1.8 °C / SST≥19°C-as-kill as the “SAFE” sample
- Soften never-claims with a disclaimer under a fake heatmap
