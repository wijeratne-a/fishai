# Agent handoff — Species Model Cards and Scientific Model Governance

**Date:** 2026-09-18  
**From:** Species Model Cards / Scientific Model Governance owner  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/model_cards/` **only**  
**Did not write:** `globe/**`, `artifacts/integration/**`, commercial SKU files  
**Training:** none  
**Ingest:** none

---

## 1. Executive finding

**Schema field count:** **31** scientific contract fields (mandatory on every published species model and every globe organism/ops output) + **14** governance/link fields = **45 required** top-level properties (**50** defined, including 5 optional). Globe link trio: `card_id`, `model_version`, `claim_pack`.

**Why nothing is publishable today:** wedge **UNRESOLVED**; **0** observations ingested; **0** interviews; **no training**; expert-rule+climatology **specified not fitted**; validation vacuously failed; rights ingest **not** authorized; red-team **NO-GO**; factory step 7 not reached; reviewer status **REQUIRED_HUMAN_REVIEW** with **no human named**. All three cards are `NOT_PUBLISHED` / `NOT_OPERATIONAL`.

**Globe linking rule:** **No globe cell without `card_id`.** Missing card, `NOT_PUBLISHED` card, or missing `model_version`/`claim_pack` ⇒ **cannot publish the layer.** Do not draw. Details: `globe_link_contract.md` and `README.md`.

---

## 2. What was written

| File | Purpose |
|---|---|
| `README.md` | Index; globe cell rule; why unpublished |
| `model_card_schema.json` | Machine schema (`SMC-SCHEMA-2026-09-18-v1`) |
| `model_card_template.md` | Human template for all 31 + governance |
| `governance.md` | Who can publish; red-team + domain reviewer; as-of replay; never overwrite past cards |
| `permitted_vs_prohibited_claims.md` | Oyster / Chinook / lobster packs from the prediction contract |
| `globe_link_contract.md` | API trio; resolve-and-refuse |
| `cards/W1_oyster_ops_risk_v0_DRAFT.md` | UNRESOLVED; 0 obs; 0 interviews; B4+B12 SPEC; prohibited: food-safety, harvest auth, SST=body T, abundance |
| `cards/W2_chinook_encounter_v0_DRAFT.md` | 24–48h env encounter **not identified** (BLOCKER for habitat SDM); horizon allowed only for partner-log C rank; NOT_PUBLISHED |
| `cards/W3_lobster_cpue_v0_DRAFT.md` | catch ≠ abundance; AIS banned; NOT_PUBLISHED |
| `agent_handoff.md` | this file |

Optional `globe/MODEL_CARD_LINK.md` was **not** added (avoid colliding with globe agents). Point at `observatory/model_cards/globe_link_contract.md`.

---

## 3. Card ids (for globe / API stubs)

| card_id | model_version | claim_pack | Draw live layer? |
|---|---|---|---|
| `SMC-W1-OYSTER-OPS-RISK-v0-DRAFT` | `W1_oyster_ops_risk_v0_SPEC` | `claim_pack_W1_oyster_ops_D_v0` | **No** |
| `SMC-W2-CHINOOK-ENCOUNTER-v0-DRAFT` | `W2_chinook_encounter_v0_SPEC` | `claim_pack_W2_chinook_encounter_C_v0` | **No** |
| `SMC-W3-LOBSTER-CPUE-v0-DRAFT` | `W3_lobster_cpue_v0_SPEC` | `claim_pack_W3_lobster_cpue_C_v0` | **No** |

Fixtures may echo the trio **only** with `NOT_PUBLISHED` / `UNKNOWN` hatch and no score.

---

## 4. Recipients

| Recipient | Ask |
|---|---|
| Globe / UI / explainability | Implement `globe_link_contract.md`. Refuse layers without `card_id`. Do not restyle W1 as presence. |
| Observatory factory / registry | Eligibility T2 ≠ emission. CSV rows still have no published card. |
| Quality / validation | Cards record `NOT_RUN` / `not_evaluated`. Do not backfill metrics. |
| Red team | Claim packs copy the prediction contract; they do not close BLOCKERs. |
| Rights / privacy | Cards inherit `ingest_authorized=false`. |
| Product / commercial | Do not treat these drafts as a wedge lock or as approved copy for email/PDF. |
| Founder | No publisher or domain reviewer is named. Publish is impossible until humans exist and gates in `governance.md` §3 pass. |

---

## 5. Honesty checklist (this pass)

- [x] No training claimed  
- [x] 0 observations ingested, 0 interviews  
- [x] Wedge UNRESOLVED on all three cards  
- [x] W1 architecture = expert-rule + climatology only, unfitted  
- [x] W2 24–48h identifiability recorded as BLOCKER for habitat models; allowed C-rank path still unpublished  
- [x] W3 catch ≠ abundance; AIS banned  
- [x] Reviewer: REQUIRED_HUMAN_REVIEW, names empty  
- [x] Status NOT_PUBLISHED / NOT_OPERATIONAL  
- [x] Did not write globe implementation files  

---

## 6. Related authorities (read, not overwritten)

- `artifacts/scientific_red_team/prediction_contract.md`  
- `artifacts/scientific_red_team/deployment_blockers.md`  
- `artifacts/quality_and_validation/` (baselines, validation, uncertainty)  
- `artifacts/marine_domain/`  
- `observatory/species_model_factory.md`  
- `observatory/global_species_registry/support_tier_framework.md`  
- `observatory/data_rights_register.md` + `artifacts/data_rights_and_privacy/data_rights_register.md`  
- `observatory/sensitive_location_policy.md`  
- `globe/visual_truth_states.md` (read for state names; not edited)
