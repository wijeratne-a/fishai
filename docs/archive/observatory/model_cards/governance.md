# Species Model Card governance

**Owner:** Species Model Cards and Scientific Model Governance  
**Date:** 2026-09-18  
**Status:** Binding. No species model is published. No model is operational.  
**Schema:** `SMC-SCHEMA-2026-09-18-v1`

This file is who may publish, what must be true before publish, and how cards are versioned. It does not authorize training, ingest, or a globe layer.

---

## 1. What a card is

A Species Model Card is the **scientific identity document** of one model version for one taxon × life-stage × geography × prediction target.

- Every **published** species model must have a card with all **31** scientific contract fields plus the **14** governance/link fields in `model_card_schema.json`.
- Every **globe output** about organisms or ops-as-biology, when a globe exists, must carry `card_id`, `model_version`, and `claim_pack` that resolve to a **PUBLISHED** card. See `globe_link_contract.md`.
- A missing card, a `NOT_PUBLISHED` card, or a card with `operational_status: NOT_OPERATIONAL` **cannot** authorize a public or customer-facing layer.

Cards are **not** observations. A card in `HYPOTHETICAL/RESEARCH MODE` is an honest factory product.

---

## 2. Who can publish

| Role | May draft / tighten | May **publish** (`card_status → PUBLISHED`) | May mark `OPERATIONAL` |
|---|---|---|---|
| Software agents (this program) | Yes (tighten only) | **No** | **No** |
| Scientific red-team agent | Record blockers; refuse overclaim | **No** (not a human reviewer) | **No** |
| Named human **domain reviewer** | Yes | **Required co-sign** | **Required co-sign** |
| Named human **publisher** (founder or delegate recorded in writing) | Yes | **Yes, only after both co-signs** | **Yes, only after both co-signs + gates below** |
| Sales / product / globe UI agents | Shorten layout; **must not** strengthen meaning | **No** | **No** |

**Publishers today:** none named.  
**Domain reviewers today:** none named.  
**Reviewer status on all drafts:** `REQUIRED_HUMAN_REVIEW`.

Closing a BLOCKER or HIGH from `artifacts/scientific_red_team/` requires a named human, date, and scope. Agents cannot accept residual HIGH risk.

---

## 3. Publish gates (all must pass)

A card may move to `PUBLISHED` only when **all** of the following are true. As of 2026-09-18, **none** of the three wedge drafts pass.

1. **Wedge lock.** One species × geography × customer × decision in `project_state.json`, **or** the card is observatory-taxon-only at T0/T1 with `UNKNOWN/INSUFFICIENT DATA` and no score.
2. **Factory step 7.** `species_model_factory.md` steps 1–6 complete for that taxon × stage × geography; validation artifacts exist; status is not `NOT READY FOR USE` if a score is claimed.
3. **Prediction contract.** All 14 product-output fields plus red-team extras (evidence tier, A–E category, extrapolation flag, official-status last-verified where applicable).
4. **Rights.** Every training, eval, and feature source is an `APPROVED_*` class for the intended use. Ingest actually happened under that class. `UNKNOWN` / `REJECTED` / `NONCOMMERCIAL_ONLY` / `RESTRICTED` without a DUA **block**.
5. **Labels in hand.** `observations_ingested` and `partner_label_n` meet the validation protocol minimum for the claimed horizon — not catalog metadata, not “the dataset exists somewhere.”
6. **As-of replay.** `availability_at_prediction_time` is implemented. Issuance snapshots freeze `source_data_cutoff_utc`. Evaluation that uses data not available at issuance is forbidden for go/no-go.
7. **Baselines.** Five families specified **and** the relevant baseline fitted. An advanced model is `NOT READY FOR USE` unless it beats that baseline on honest time-forward **and** spatial holdout. A packaged climatology/expert-rule product must be labeled as such — never “AI forecast.”
8. **Red-team.** No open BLOCKER. Every HIGH is resolved, visibly bounded in the card, or accepted in writing by the named domain reviewer.
9. **Human review.** Named domain reviewer **and** named publisher. Empty `human_reviewer_names` ⇒ cannot publish.
10. **Claim pack.** `permitted_user_claims` / `prohibited_user_claims` match `permitted_vs_prohibited_claims.md` and `artifacts/scientific_red_team/prediction_contract.md`. Agents may only tighten.
11. **Sensitive locations.** Public grain passes ecological-harm review (`sensitive_location_policy.md`). `NEVER_PUBLISH` items are not in the layer.
12. **Globe link.** If any globe cell would draw this model, the cell schema includes `card_id` + `model_version` + `claim_pack`. Missing `card_id` ⇒ **cannot publish the layer** (README rule).

`OPERATIONAL` is a **second** flag. It requires a live issuance path that prints the contract, collects outcomes, and can replay any past brief. A published SPEC with no issuance path stays `NOT_OPERATIONAL`.

---

## 4. As-of replay (never silent edits)

The platform is a time machine. “Why was forecast X issued on date Y?” must be answerable from stored snapshots.

Binding rules (aligned with `artifacts/geospatial_data_engineer/as_of_replay_design.md`):

- Every issued score stores `issued_at_utc`, `source_data_cutoff_utc`, `training_data_cutoff_utc`, `model_version`, `card_id`, feature snapshot hash, and the **user-visible text as delivered**.
- Honest evaluation uses only rows with `published_at_utc ≤ cutoff`. Corrected-data research is a separate lane and **cannot** support go/no-go or customer claims.
- **Never UPDATE** a prediction row. Corrections = new `forecast_id` with `supersedes_forecast_id`.
- **Never UPDATE** a published card. See §5.
- Silent edits to past forecasts, or evaluation that uses future/revised fields, are red-team stop-ship (`B-ALL-02`, RT-XCUT-02).

If as-of replay is not built (`specified_not_built` or `missing` on the card), the model **cannot** be `OPERATIONAL` and **cannot** be `PUBLISHED` as a forecast.

---

## 5. Versioning — never overwrite past cards

| Object | Identity | Mutation rule |
|---|---|---|
| Card file | `card_id` + `as_of_date` | **Create a new file** for any material change. Old file stays. Set `supersedes_card_id` on the new card and `superseded_by_card_id` on the old card **without deleting or rewriting scientific fields of the old card** except that one pointer. |
| Model weights / rules | `current_model_version` | New version ⇒ new card. Do not retcon metrics onto an old version. |
| Claim pack | `claim_pack` | Tightening may ship as a new pack id bound to a new card. Loosening requires a named human. |
| Globe cell | `(card_id, model_version, claim_pack)` | Historical tiles, if any, keep the card_id they were issued with. |

**Forbidden:** editing yesterday’s card so today’s better story appears to have always been true. That is the same class of error as silent forecast edits.

Drafts (`NOT_PUBLISHED`, filename `*_DRAFT.md`) may be revised in place **until first publish**. After `PUBLISHED`, the draft filename is frozen as a snapshot or copied to a dated `cards/archive/` path; subsequent work uses a new `card_id`.

Version string pattern:

```text
{wedge}_{target}_v{n}[_SPEC|_DRAFT|_cal{YYYYMMDD}]
```

`_SPEC` = untrained specification. `_DRAFT` = card not published. No `_SPEC` model may be `OPERATIONAL`.

---

## 6. Factory relationship

| Factory step | Card implication |
|---|---|
| 1 Taxonomy | Identity fields may be filled; no score |
| 2 Data audit | Counts are catalog metadata unless `ingested=true` |
| 3 Ecology | Environmental variables with mechanism status |
| 4 Eligibility tier | `factory_eligibility_tier`; emitted remains T0 until step 7 |
| 5 Model selection | Architecture + baselines specified; **no training required** |
| 6 Validate | Metrics and calibration; `NOT READY FOR USE` is a valid honest result |
| **7 Publish** | Only step that may set `card_status=PUBLISHED` |
| 8 Monitor | Triggers downgrade / new card; never silent overwrite |

Iteration 1 (2026-09-18): example registry rows are T0–T2 **eligibility**. T3–T6 assigned count = 0. Commercial W1/W2/W3 are **not** T6.

---

## 7. Downgrade and withdrawal

Immediately set a **new** card (or `WITHDRAWN` on a successor) if:

- a source is withdrawn or rights class worsens;
- WoRMS splits or the accepted AphiaID changes;
- prospective validation fails or a baseline overtakes the model;
- ecological-harm or ESA/privacy review fails;
- official regulation/sanitation modules are stale and were used as if they were the model.

Downgrade of `support_tier` emitted value is a new card, not a quiet CSV edit.

---

## 8. What this governance does not do

- Does not train models.
- Does not ingest data.
- Does not lock the commercial wedge.
- Does not name a human reviewer (none are named as of 2026-09-18).
- Does not write `globe/**` implementation files.

---

## 9. Related documents

- `README.md` — globe cell rule; missing card = cannot publish layer
- `model_card_schema.json` — 31 scientific + 14 governance fields (45 required)
- `permitted_vs_prohibited_claims.md`
- `globe_link_contract.md`
- `../species_model_factory.md`
- `../global_species_registry/support_tier_framework.md`
- `../../artifacts/scientific_red_team/prediction_contract.md`
- `../../artifacts/scientific_red_team/deployment_blockers.md`
- `../../artifacts/geospatial_data_engineer/as_of_replay_design.md`
