# Species Model Cards

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/observatory/model_cards/`  
**Owner:** Species Model Cards and Scientific Model Governance  
**Date:** 2026-09-18  
**Training:** none  
**Ingest:** none  
**Default card status:** `NOT_PUBLISHED`  
**Default operational status:** `NOT_OPERATIONAL`

This directory is the **only** place species-model scientific identity is recorded for observatory and (later) globe outputs. It is not a model zoo. Nothing here is a live score.

---

## Globe linking rule (binding)

**No globe cell, tile, API biological field, or customer brief may ship without a `card_id` that resolves to a Species Model Card in this directory.**

| Condition | Result |
|---|---|
| Output has no `card_id` | **Cannot publish the layer.** Do not draw the cell. |
| `card_id` missing from `cards/` | **Cannot publish the layer.** |
| Card exists but `card_status = NOT_PUBLISHED` | **Cannot publish the layer.** Research fixture / hatch `UNKNOWN` only. |
| Card `operational_status = NOT_OPERATIONAL` | **Cannot issue a score.** May show identity + insufficient-data copy. |
| Card `PUBLISHED` but globe payload lacks `model_version` or `claim_pack` | **Cannot publish the layer.** Trio is mandatory: `card_id` + `model_version` + `claim_pack`. |

A screenshot, demo, or “prototype heatmap” is a published layer if a user can read it as animals or ops-risk. Missing card ⇒ do not ship.

Contract for implementers: [`globe_link_contract.md`](globe_link_contract.md). This owner does **not** write `globe/**` while other agents fill that tree.

---

## Why nothing is publishable today

1. Commercial wedge is **UNRESOLVED** (`B-ALL-08`).
2. **0** observations ingested; **0** operator interviews completed.
3. **No model trained.** W1 is specified as expert-rule + climatology only; those baselines are **not fitted**.
4. Validation is vacuously failed (`B-ALL-01`, RT-XCUT-01): no as-of store, no time-forward/spatial holdout, no prospective log.
5. Rights: ingest is **not** authorized; partner DUAs unsigned; many families `UNKNOWN` / `CONDITIONAL_REVIEW_REQUIRED`.
6. Reviewer status: `REQUIRED_HUMAN_REVIEW`; **no human named**.
7. Red-team **NO-GO** for all three wedges. Open BLOCKERs include food-safety/harvest wall (oyster), 24–48h habitat identifiability (Chinook), AIS-as-abundance and public CPUE maps (lobster).
8. Factory step 7 (publish) has not been reached for any taxon. Emitted observatory class remains `UNKNOWN/INSUFFICIENT DATA`.

Until those gates clear, cards stay `NOT_PUBLISHED` / `NOT_OPERATIONAL`. That is a successful honest result.

---

## Registry (2026-09-18)

| card_id | File | Taxon | Target | Cat | Status | Operational | Reviewer |
|---|---|---|---|---|---|---|---|
| `SMC-W1-OYSTER-OPS-RISK-v0-DRAFT` | [`cards/W1_oyster_ops_risk_v0_DRAFT.md`](cards/W1_oyster_ops_risk_v0_DRAFT.md) | *Magallana gigas* | 72h ops-stress indicator | D | **NOT_PUBLISHED** | **NOT_OPERATIONAL** | REQUIRED_HUMAN_REVIEW (none named) |
| `SMC-W2-CHINOOK-ENCOUNTER-v0-DRAFT` | [`cards/W2_chinook_encounter_v0_DRAFT.md`](cards/W2_chinook_encounter_v0_DRAFT.md) | *Oncorhynchus tshawytscha* | 24–48h relative encounter rank | C (preferred) / D | **NOT_PUBLISHED** | **NOT_OPERATIONAL** | REQUIRED_HUMAN_REVIEW (none named) |
| `SMC-W3-LOBSTER-CPUE-v0-DRAFT` | [`cards/W3_lobster_cpue_v0_DRAFT.md`](cards/W3_lobster_cpue_v0_DRAFT.md) | *Homarus americanus* | next-trip legal CPUE rank | C | **NOT_PUBLISHED** | **NOT_OPERATIONAL** | REQUIRED_HUMAN_REVIEW (none named) |

No other species models exist. Observatory CSV eligibility tiers (T0–T2) in `../species_support_tiers.csv` are **not** published models and have no globe layer.

---

## Files in this directory

| File | Role |
|---|---|
| [`model_card_schema.json`](model_card_schema.json) | Machine schema. **31** scientific contract fields + **14** governance/link fields = **45** required top-level properties (**50** defined). |
| [`model_card_template.md`](model_card_template.md) | Human fill template for all 31 + governance. |
| [`governance.md`](governance.md) | Who can publish; red-team + domain reviewer; as-of replay; never overwrite past cards; versioning. |
| [`permitted_vs_prohibited_claims.md`](permitted_vs_prohibited_claims.md) | Oyster / Chinook / lobster claim packs from the red team. |
| [`globe_link_contract.md`](globe_link_contract.md) | API trio: `card_id`, `model_version`, `claim_pack`. |
| [`agent_handoff.md`](agent_handoff.md) | Recipients and today’s verdict. |
| `cards/` | Immutable-after-publish card files. |

---

## Schema field count

| Count | What |
|---|---|
| **31** | Scientific contract fields that **every** published species model (and every globe organism/ops output) must fill. |
| **14** | Governance and globe-link fields (`card_id`, statuses, `claim_pack`, factory/wedge, interviews, ingest counts, output class, capability, evidence tier). |
| **45** | Required top-level properties (`model_card_schema.json` `required` array). |
| **50** | Defined top-level properties (45 + 5 optional: supersedes pointers, red-team ids, extrapolation flag, notes). |

The 31 scientific fields are: Species identity; Taxonomic authority; Geographic scope; Depth scope; Life stage; Prediction target; Output category (A–E / visual truth state); Support tier T0–T6; Training data sources; Data rights status; Observation count; Observation methods; Environmental variables; Feature availability/latency; Model architecture; Baseline comparison; Validation approach; Performance metrics; Calibration results; Known biases; Known failure modes; Uncertainty method; Geographic/seasonal/depth gaps; Sensitive-location rules; Last retrained date; Current model version; Reviewer status; Permitted user claims; Prohibited user claims; Recommended use cases; Not-recommended use cases.

---

## How this relates to other programs

| Program | Relationship |
|---|---|
| Commercial 1×1×1×1 wedge | Paused / UNRESOLVED. These cards describe **SPEC** baselines for the three candidates. They do not lock a wedge and do not widen SKU. |
| Observatory factory | Cards are the Step 7 artifact. Step 7 has not run. |
| Globe | Must consume the link contract. This owner prefers **not** to write `globe/**`. |

Shared non-negotiables: a model is not an observation; SST/AIS/chlorophyll are not abundance; habitat is not presence or legality; CPUE is not abundance; food-safety and harvest authorization stay with authorities.
