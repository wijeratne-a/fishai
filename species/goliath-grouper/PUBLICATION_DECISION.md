# Publication decision — Atlantic goliath grouper

**Date:** 2026-09-22  
**Taxon:** *Epinephelus itajara* (AphiaID 159353)  
**Candidate products:** current occurrence probability; 24–72h forecast; seasonal aggregation presence; relative abundance index  
**Decision:** **`NOT_PUBLISHED`**

Publication is earned. No card was marked `PUBLISHED` to make the globe look complete. A beautiful Earth with **unknown** as the answer is the correct state.

**Stop condition:** this system does **not** know exactly where Atlantic goliath grouper are at every moment. Do not imply that it does.

---

## What may appear on the globe

- Empty / unknown ocean (default).
- Optional **historical pattern**: official OBIS 1° cells after coarsening (`n ≥ 3`, max 80), labeled **past reports — not where they are now**.
- Ecology copy: juvenile mangrove vs adult ~0–50 m structure; Jul–Sep spawning **season** (no site list).

## What must not appear

- Current-estimate layer
- Forecast layer
- Habitat painted as presence
- Relative-abundance heat
- Spawning-aggregation pins, wrecks, or nursery GPS
- Invented confidence scores

**Spawning-site layer: BLOCKED.**

---

## Missing gates ([`observatory/model_cards/governance.md`](../../observatory/model_cards/governance.md))

| Gate | Status |
|---|---|
| Rights-approved ingest (`APPROVED_*`) | Missing — nothing ingested |
| Effort-aware non-detections | Missing |
| Spatial-block holdout | Not run |
| Temporal / time-forward holdout | Not run |
| Baseline beat on those holdouts | None |
| Calibration of a probability | None |
| As-of replay | Specified elsewhere; not built for this taxon |
| Sensitive-site review of a published grain | Aggregation/nursery layer blocked; 1° past reports only if coarsener applies |
| Named human domain reviewer | None |
| Named human publisher | None |
| Wedge / commercial lock | Unrelated; commercial project still paused |
| Globe link `card_id` + `model_version` + `claim_pack` | No published card |

Zero `PUBLISHED` cards remain in `globe/prototype/public/fixtures/model-cards.json`.
