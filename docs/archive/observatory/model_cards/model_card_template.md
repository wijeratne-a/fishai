# Species Model Card — TEMPLATE

**Schema:** `SMC-SCHEMA-2026-09-18-v1` (`model_card_schema.json`)  
**Fill every field.** Empty / `null` / `not_evaluated` is honest. Invented skill is not.  
**Default statuses:** `card_status: NOT_PUBLISHED` · `operational_status: NOT_OPERATIONAL`  
**Copy this file to** `cards/{card_id}.md` **then fill. Do not edit a past published card in place.**

---

## Governance (required; not part of the 31 scientific fields)

| Field | Value |
|---|---|
| `card_id` | `SMC-…` |
| `schema_version` | `SMC-SCHEMA-2026-09-18-v1` |
| `card_status` | `NOT_PUBLISHED` |
| `operational_status` | `NOT_OPERATIONAL` |
| `claim_pack` | `claim_pack_…` |
| `as_of_date` | `YYYY-MM-DD` |
| `wedge_id` | `UNRESOLVED` \| `W1_…` \| `W2_…` \| `W3_…` \| `OBSERVATORY_TAXON_ONLY` |
| `wedge_lock_status` | `UNRESOLVED` \| `LOCKED` |
| `factory_step` | 1–8 (publish = 7; nothing has reached 7 as of 2026-09-18) |
| `observatory_output_class` | default `UNKNOWN/INSUFFICIENT DATA` or `HYPOTHETICAL/RESEARCH MODE` |
| `capability_class` | 1–7 |
| `interviews_completed` | integer (0 if none) |
| `observations_ingested` | integer (0 if none; catalog metadata ≠ ingest) |
| `evidence_tier_strongest_label` | `none` \| `T1_direct` \| `T2_operational` \| `T3_remote_or_modeled` \| `T4_unverified` |
| `supersedes_card_id` | `null` or prior `card_id` |
| `red_team_blocker_ids` | list |

---

## Scientific contract (all 31 required)

### 1. Species identity

- Common name:
- Accepted scientific name:
- WoRMS AphiaID:
- LSID:
- Principal synonyms:
- Common-name collisions:
- Population unit:

### 2. Taxonomic authority

- Authority of record: **WoRMS**
- Taxon URL:
- Access date:
- WoRMS status:
- License status (`UNKNOWN` until verified):

### 3. Geographic scope

- Description:
- Bounding units:
- Public grain:
- Founder-locked? (`false` unless `project_state.json` says otherwise)

### 4. Depth scope

- Depth band (or `depth_unknown`):
- Depth known? (`true`/`false`):
- Notes:

### 5. Life stage

- In scope:
- Out of scope:

### 6. Prediction target

- Name:
- Definition (what the number *is*):
- Horizon:
- Unit:
- `label_id`:

### 7. Output category (A–E / visual truth state)

- Prediction-contract category: `A` \| `B` \| `C` \| `D` \| `E` \| `NONE`
- Visual-truth state (exactly one; unclassifiable → do not draw):

### 8. Support tier T0–T6

- Factory eligibility tier:
- Emitted tier (what the API/globe may actually return):
- Evidence ceiling tier:
- Notes (eligibility ≠ emission):

### 9. Training data sources

| source_id | role | ingested | rights_class | notes |
|---|---|---|---|---|
| | label / feature / context / baseline_only / forbidden / not_used | true/false | | |

### 10. Data rights status

- Overall:
- Human legal review: `REQUIRED` \| `CLEARED` \| `BLOCKED`
- Ingest authorized: `true`/`false`
- Privacy default:

### 11. Observation count

- Ingested n:
- Catalog metadata n (not a census; not ingested):
- Partner label n:

### 12. Observation methods

- List methods that would generate labels. If none ingested, say so.

### 13. Environmental variables

| name | role | mechanism_status | notes |
|---|---|---|---|
| | primary / supporting / context_only / forbidden_as_label / not_used | causal / correlative / proxy / unknown / wrong_variable | |

### 14. Feature availability / latency

- As-of replay implemented?
- `availability_at_prediction_time`: `implemented` \| `specified_not_built` \| `missing`
- Notes:

### 15. Model architecture

- Family: `none` \| `expert_rule` \| `climatology` \| `expert_rule_plus_climatology` \| `persistence` \| `statistical` \| `ml` \| `ensemble`
- Trained? (`false` unless a training run exists)
- Description:

### 16. Baseline comparison

- Baselines specified?
- Baselines fitted?
- Relevant baseline id:
- Beats relevant baseline: `yes` \| `no` \| `not_evaluated`
- Notes:

### 17. Validation approach

- Protocol id:
- Time-forward run?
- Spatial holdout run?
- Prospective pilot run?
- Status: `NOT_RUN` \| `FAILED` \| `PASSED` \| `BOUNDED`

### 18. Performance metrics

- Available?
- Primary metric:
- Value:
- Split:
- Notes:

### 19. Calibration results

- Calibration plot accepted by a named human? (`false` until that happens)
- ECE / interval coverage:
- Notes:

### 20. Known biases

- List.

### 21. Known failure modes

- List.

### 22. Uncertainty method

- Method:
- Confidence labels allowed?
- Numeric probabilities allowed? (No until a human accepts a **prospective** calibration plot.)

### 23. Geographic / seasonal / depth gaps

- List.

### 24. Sensitive-location rules

- Publish class: `PUBLIC` \| `COARSENED` \| `DELAYED` \| `RESTRICTED` \| `PRIVATE` \| `NEVER_PUBLISH`
- Never-publish items:
- Public max grain:

### 25. Last retrained date

- ISO date or `null` (never trained).

### 26. Current model version

- Version string (must match globe `model_version`).

### 27. Reviewer status

- Status: `REQUIRED_HUMAN_REVIEW` \| `APPROVED` \| `REJECTED` \| `BOUNDED`
- Human reviewer names: (empty = none named)
- Red-team signoff (boolean):
- Domain-reviewer signoff (boolean):
- Review date:

### 28. Permitted user claims

- Sentences allowed by the bound `claim_pack` only.

### 29. Prohibited user claims

- Never-claims for this taxon × product.

### 30. Recommended use cases

- List (research / packaging / later pilot). None are customer-facing until PUBLISHED + OPERATIONAL.

### 31. Not-recommended use cases

- List.

---

## Approval block (leave blank until humans sign)

| Role | Name | Date | Scope |
|---|---|---|---|
| Scientific red-team | | | |
| Domain reviewer | | | |
| Publisher (named human) | | | |

Software agents may tighten claims. They may not publish, loosen, or sign this block.
