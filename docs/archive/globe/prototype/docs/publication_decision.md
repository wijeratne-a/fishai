# First-species publication decision

**Date:** 2026-09-22  
**Candidate target:** Historical observation density (not current occurrence, not habitat, not forecast).  
**Taxon / region:** Any catalog species that OBIS will coarsen (example: yellowfin tuna, *Thunnus albacares*, global 1° grid).  
**Decision:** `NOT_PUBLISHED`

This is not a current-location product and not a forecast. The globe may show **past reports** with that label (scientific status: **historical pattern**). It may not show a current-estimate, occurrence-probability, relative-abundance, movement, or forecast layer.

Publication is earned. No `PUBLISHED` card was created to make the globe look complete.

## What was built

- Live, rate-limited lookup of the official OBIS occurrence API.
- Coarse 1° cells, hide n < 3, cap 80 cells.
- Sensitive AphiaIDs withheld before the grid is requested (white shark, AphiaID 105838).
- Answer copy: “No issued location.” “No forecast issued.” “Past reports … not where the animals are now.”
- Six prediction targets named in the answer strip; unknown is first-class.

## What was not built

- No training pipeline.
- No habitat suitability model sold as presence.
- No forecast grid.
- No occurrence-probability or relative-abundance score.
- No movement model.
- No invented metrics, confidence scores, or model card marked `PUBLISHED`.

## Governance gates ([`observatory/model_cards/governance.md`](../../../observatory/model_cards/governance.md))

| Gate | Status |
|---|---|
| Wedge lock in `project_state.json` | Missing — commercial wedge still paused |
| Factory steps + validation artifacts | Missing |
| Prediction contract 14 fields as a live score | Not issued |
| Rights-approved ingest (`APPROVED_*`) | No source approved for ingest |
| Labels in hand / partner_label_n | None |
| Spatial holdout | Not run — no fitted model |
| Temporal / time-forward holdout | Not run — no fitted model |
| Baseline beat on those holdouts | None |
| As-of replay | Specified, not built |
| Named human domain reviewer | None |
| Named human publisher | None |
| Red-team blockers closed | Open (`HIGH_BLOCKERS_OPEN`) |
| Sensitive-location review of a published grain | Past-report coarsening only |
| Globe link `card_id` + `model_version` + `claim_pack` | No published card |

A beautiful globe with an honest unknown state is the correct outcome of this pass.
