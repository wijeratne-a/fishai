# Local 50-mile prediction MVP (proposal)

**Date:** 2026-09-23  
**Status:** PROPOSAL ONLY  
**Issued product:** None. No nowcast, forecast, or abundance model is fitted or published.

**Related infrastructure map:** see `planning/nowcast-infrastructure/INFRASTRUCTURE_FRAMEWORK.md`.
Candidate source rows for that map are in `planning/nowcast-infrastructure/SOURCE_FAMILIES.csv`.
Those files summarize a multi-species briefing as a proposed infrastructure map only—nothing ingested or operational.
The infrastructure brief does **not** clear this MVP, does not authorize CalCOFI/WCOFS ingest, and does not issue a 50-mile nowcast or forecast.
Goliath RVC rights, card `NOT_PUBLISHED`, and feasibility `CONDITIONAL GO` are unchanged by that note.

This file records a recommended first *dynamic* 50-mile MVP from an external strategy brief, grounded against verified FishAI state. It does not replace the Florida Keys goliath path, clear rights, or authorize ingest.

---

## Proposed first dynamic MVP (from strategy brief)

| Item | Proposal (not built) |
|---|---|
| Geography | California Current coastal window on the order of **about 50 miles** (user-local radius or equivalent coarsened cells)—exact polygon not locked in this repo |
| Species | Pacific sardine (*Sardinops sagax*) and northern anchovy (*Engraulis mordax*), as named in the brief |
| Biological target | Encounter rate or egg-density style response from **CalCOFI CUFES** (or documented CalCOFI egg/encounter products), not adult reef visual detection |
| Environment | **WCOFS** surface (and related) fields as candidate covariates |
| Model family | **sdmTMB** delta / spatiotemporal model family as a candidate engine |
| Update cadence | Daily update proposed in the brief (requires an operational environmental pull that does not exist here) |
| Display | Research prototype probabilities or indices, coarsened; labeled nowcast only if a card is later `PUBLISHED` |

**Brief operational claims (not independently verified in this pass):** the strategy brief cites figures such as WCOFS ~4 km horizontal scale, on the order of 40 vertical levels, ~72 h forecast guidance, ERDDAP rate-limit practice, and validation shorthand (e.g. “Rule of Three,” Boyce Index targets). Restate them only as brief claims until a human confirms them from provider pages during an approved ingest design.

**Timeline in the brief:** **6–8 weeks** is the brief’s estimate for standing up a prototype after data access. It is **not** a FishAI commitment, schedule, or staffing plan.

---

## What this proposal is for

- A **pelagic, survey-linked** first dynamic path where egg or encounter products and West Coast ocean fields might eventually support a calibrated local index.
- A separation of **direct observation**, **historical pattern**, **nowcast**, **forecast**, and **unknown** (`local-50-mile-coverage-framework.md`).
- A reminder that unknown remains valid when CUFES coverage, rights, or covariate match fail inside the 50-mile window.

## What this proposal is not

- Not a system that finds every fish within 50 miles.
- Not live tracking or vessel guidance to animals.
- Not harvest, spear, or “where to fish” advice.
- Not an implication that CalCOFI, WCOFS, or sdmTMB are already ingested or operational in this repository. They are **candidates**.
- Not permission to scrape, store credentials, or query VMS.

---

## Validation plan (proposed)

Only after written rights approval and a frozen biological extract:

1. Define the estimand in one sentence (egg density vs encounter probability) and lock method fields.
2. Baselines before complexity: seasonal climatology; effort-only; spatial smoother labeled historical.
3. Holdouts: time-forward cruise or year blocks; spatial blocks along the coast so the smoother cannot see the test segment.
4. Metrics: log-loss / continuous ranked skill appropriate to the response; calibration plots; explicit out-of-domain → **Unknown**.
5. Prospective check: score a held-out recent period against the daily environmental fields actually available at decision time (no peeking at future analyses).
6. Display-safety review before any public layer.

None of these tests have been run for this MVP. No fitted object exists.

---

## Display-safety note

Pelagic egg or encounter surfaces are **not** wreck maps, spawning-aggregation pins, nursery guides, or telemetry tracks. Coarsen to a support that cannot be reverse-engineered into a site list. Withhold any cell a sensitivity reviewer flags. Do not place fishing guidance on the layer.

---

## Exact blockers (current repo)

| Blocker | State |
|---|---|
| Approved ingest | Absent. No written yes for CalCOFI CUFES or WCOFS training/display package in this planning folder; rights templates are drafts only |
| Local environmental lake | Absent. WCOFS (and related) fields are not stored or joined here |
| Fitted model | Absent. No sdmTMB (or other) fit; no nowcast issued |
| Published model card | Not applicable until a fit exists; default remains no predictive layer |

Source inventory rows for CalCOFI/CUFES and WCOFS remain candidates with `CONDITIONAL_REVIEW_REQUIRED` until a human records approval (`local-50-mile-source-inventory.csv`).

---

## Florida Keys goliath path (separate, still blocked)

The Prediction MVP — Florida Keys Goliath Grouper Detection Nowcast remains the named reef-fish milestone in `species/goliath-grouper/`. It is **not** replaced by this California Current proposal.

Verified blockers that still apply there (`TRAINING_DATA_HURDLE.md`, `RVC_RIGHTS_RECORD.md`, `FIRST_MODEL_FEASIBILITY.md`):

- Feasibility: **CONDITIONAL GO**; training **not started**; card **`NOT_PUBLISHED`**
- Rights: **`CONDITIONAL_REVIEW_REQUIRED`**; no `APPROVED_*` without written approval (none in repo)
- NCEI **0208321** (2018, published Jan 2020) set aside as too old for the first training extract
- **0282183** and **0306184** screened only; not downloaded; zeros and `EPIITAJ` unverified
- OBIS compiled rows = historical context only
- Smith et al. 2011 = design citation (200 m primary; 15 m second-stage); not a data grant; does not mention goliath

A sardine/anchovy CUFES prototype, if ever built, does not clear RVC rights, does not verify RVC zeros, and does not publish the goliath card.

---

PROPOSAL ONLY — no 50-mile nowcast or forecast is issued
