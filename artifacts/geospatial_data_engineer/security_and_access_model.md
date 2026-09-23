# Security and access model

**Agent:** GEOSPATIAL_DATA_ENGINEER_AGENT  
**Date:** 2026-09-18  
**Audience:** engineers implementing L0–L5 and the first partner DUA. Not a substitute for human legal review.

This model is **privacy-tiered access on one canonical store**, not three products and not a multi-tenant SaaS. HiveClaw Rewind’s “trusted local SQLite” lesson applies: do not add login theater that does not change the data model. When a second operator or first partner arrives, switch the warehouse to Postgres + RLS.

---

## 1. Privacy tiers (every row, every derived file)

| Tier | Who can read | Spatial rule | Typical contents |
|---|---|---|---|
| `PUBLIC` | Anyone receiving a product | Official unit or H3 parent at `public_h3_res`; **no lat/lon** | Coarsened ranks, public SST context, attribution |
| `COARSENED` | Authenticated pilots / published maps | Aggregate, delayed, or parent cell | Fleet- or bay-level benchmarks if DUA allows |
| `RESTRICTED` | Named role + purpose | May include finer cells, not GPS | Agency datasets with use limits |
| `PRIVATE` | Data owner + explicitly authorized operators | Exact geometry allowed in this tier only | Farm outcomes, trap/set GPS, logbooks |
| `NEVER_PUBLISH` | Break-glass operator pair; not in models that ship public explanations | Stored for legal/safety hold if required, else do not collect | Protected-species dens, tribal data without consent, secrets |

Stricter of (source default, DUA, `SensitiveLocationRule`) wins.

---

## 2. Default rules (non-negotiable)

1. Exact user catch locations, trap GPS, and lease corners are `PRIVATE`.
2. Public fish products use H3 res 6 or parent res 5 (or an official PFMC/NEFSC unit) — never a GPS spot map.
3. Farm performance is `PRIVATE`. No public leaderboard.
4. Official closure polygons may be `PUBLIC` or `RESTRICTED` **as the agency publishes them**, with attribution and `last_verified_at`. They are not a FishAI food-safety stamp.
5. Do not expose precise locations via heatmaps, tooltips, APIs, embeddings, SHAP/feature dumps, screenshots, CSV downloads, or “top 10 holes” lists.
6. Do not train a **public** model on PRIVATE partner rows unless the DUA `training_allowed` and `commercial_derivatives_allowed` are true. Private per-partner models stay in the PRIVATE prefix.
7. `user_visible_explanation` may name official units, public env variables, and coarsened cells. It may not echo lat/lon, lease ids, vessel ids, or neighbor farms.
8. Missing closure data is displayed as missing, never as “open.”

---

## 3. Principals and roles (v1)

| Principal | Local SQLite | Pilot Postgres |
|---|---|---|
| `operator_local` | Full file access (OS user) | Superuser-equivalent on the instance; use a dedicated role |
| `ingest_job` | RW on L0/L1 prefixes it owns | DML on catalog + INSERT L1 pointers; no SELECT on `outcomes_private` except its writer schema |
| `model_job` | Read L1/L2 per wedge + privacy policy file | SELECT on views `features_asof_public` / `features_asof_partner` |
| `brief_job` | Read L3 + L5 write | SELECT `forecast_public_view`; cannot SELECT `catch_effort_private` |
| `partner_owner` | n/a until app exists | RLS: `partner_id = current_setting('fishai.partner_id')` |
| `redteam_ro` | n/a | SELECT on PUBLIC/COARSENED + synthetic fixtures; no PRIVATE |

There is **no** anonymous public S3 listing.

---

## 4. Enforcement: write-time over query-time

Query-time coarsening will leak (a forgotten `SELECT *`, a notebook, a SHAP plot). v1 materializes separate files:

```text
normalized/PRIVATE/...    exact cells, optional lat/lon
normalized/COARSENED/...  parent H3, official_unit only
normalized/PUBLIC/...     same plus stripped identifiers
```

Jobs that produce briefs **only mount PUBLIC or COARSENED prefixes**. PRIVATE prefixes are not in the brief job’s IAM role.

Postgres RLS is defense in depth, not the first control.

Sketch (pilot):

```sql
ALTER TABLE catch_effort_observation ENABLE ROW LEVEL SECURITY;
CREATE POLICY catch_owner ON catch_effort_observation
  USING (privacy_tier IN ('PUBLIC','COARSENED')
     OR partner_id = current_setting('fishai.partner_id', true));
```

Do not ship a user-facing app until this is tested with two partner_ids.

---

## 5. Path-by-path controls

| Path | Control |
|---|---|
| Object IAM | Separate keys: `ingest`, `brief`, `backup`. PRIVATE prefix deny for `brief`. |
| Encryption at rest | Disk encryption locally; bucket default encryption in cloud; optional SSE-C for PRIVATE |
| Encryption in transit | HTTPS to APIs; `sslmode=require` for Postgres |
| Secrets | Not in git, not in parquet. Partner CSV lives in PRIVATE L0 |
| PII | Partner contact emails in `partner_metadata` only, not on observation rows |
| Vessel ids | Opaque `vessel_id_internal`; real names in partner table |
| Embeddings / vector search | **Forbidden in v1.** If added later, embed coarsened text without coordinates |
| Exports | `export` job checks tier + DUA `public_release_allowed` |
| Logs | Redact query strings with lat/lon; do not log raw partner CSV lines |
| Notebooks | Fixtures only on laptops that also have PRIVATE data; or use a stripped warehouse replica |

---

## 6. SensitiveLocationRule application order

1. Load rules whose geometry intersects the row or whose taxon matches.
2. Apply `forced_privacy_tier` if stricter.
3. Raise public H3 to `min_public_h3_res` (numerically **lower** res = coarser).
4. Apply `min_delay_hours` before any COARSENED/PUBLIC materialization (`published_at + delay ≤ now`).
5. If reason is `tribal_sovereignty` or `protected_species` and no DUA: do not ingest (`NEVER_PUBLISH` / reject).

---

## 7. Partner program alignment

Charter / farm / fleet defaults from the platform spec:

- Exact productive locations private.
- Shared data spatially coarsened, aggregated, delayed, opt-in.
- Contributor data never becomes a public spot map.
- Aggregation/benchmarks require `aggregation_benchmark_allowed`.
- Revocation: see storage retention. Forecasts already sent are not rewritten; future jobs drop the partner’s PRIVATE rows.

`DataUseAgreement` version is stored on every partner `event_id`.

---

## 8. Threat notes (practical)

| Threat | v1 mitigation |
|---|---|
| Notebook leaks GPS | Separate PRIVATE bucket + role; fixtures for day-to-day |
| Model explanation leak | Allowlist of explanation features; test that lat/lon strings are absent |
| Reverse-geocode from fine H3 | Public res ≥ 5 (fish) or official growing area (farms); k-anonymity: do not publish a cell with n < 3 partners |
| Operator laptop theft | Disk encryption; PRIVATE data not in iCloud |
| Over-broad IAM | Two keys minimum at pilot |
| “Just this CSV on email” | Ingest via L0 only; treat email attachments as PRIVATE raw |
| Scraped forums as labels | Evidence tier T4; cannot enter production labels |

Multi-tenant SaaS, customer-by-customer encryption keys, and SOC2 are **out of scope** until revenue exists. If untrusted internet clients appear, stop and redesign authn/z (same warning as HiveClaw Rewind threat model).

---

## 9. Human legal review flags

Flag `HUMAN LEGAL REVIEW` before ingest when: tribal/Indigenous knowledge, ESA-listed species precise locations, VMS, paywalled data, unclear commercial use, personal data of crew, or any `CONDITIONAL_REVIEW_REQUIRED` source. This document does not authorize those collections.
