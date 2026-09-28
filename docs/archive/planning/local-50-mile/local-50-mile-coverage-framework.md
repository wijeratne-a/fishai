# Local 50-mile coverage framework

**Date:** 2026-09-23  
**Status:** Planning only  
**Product claim:** None. No 50-mile nowcast, forecast, or abundance surface is issued.

This note turns a proposed data-acquisition strategy into a coverage vocabulary for FishAI. It does not fit a model, ingest survey files, or change publication status. Existing species decisions for Atlantic goliath grouper remain in force: card `NOT_PUBLISHED`, feasibility `CONDITIONAL GO`, training blocked (`species/goliath-grouper/TRAINING_DATA_HURDLE.md`, `FIRST_MODEL_FEASIBILITY.md`).

---

## Five ecological states

Every coarsened cell inside a user’s local 50-mile radius must resolve to exactly one of these states. Mixing them on one layer without labels is a product error.

| State | Meaning | What supports it |
|---|---|---|
| **Direct observation** | A protocol-matched detection or non-detection at a known event time, with documented effort | Structured survey sample (or an approved equivalent event) whose rights allow storage and display |
| **Historical pattern** | Past occurrence rate or report density over a stated window; not current presence | Effort-aware history if available; otherwise coarsened past reports labeled historical (e.g. OBIS-style compiled rows as context only) |
| **Current nowcast** | Calibrated probability for “now” (or the latest environmental analysis time), conditional on effort and covariates | Approved training extract + matched environmental fields + validated model card `PUBLISHED` |
| **Forecast** | Same family of probability at a stated lead time, using forecast environmental inputs | Stable nowcast first; skill by lead time on the card |
| **Unknown** | No supported claim | Default when rights, effort, zeros, or covariate match fail |

**Unknown is a first-class output.** Absence of a public pin is not local absence. Presence-only history is not current presence. SST or habitat alone is not a sighting.

The product does not claim to find every animal within 50 miles, and it does not do live tracking.

---

## The 50-mile problem

A 50-mile radius around a user (port, lease, or vessel) is a local decision window. Presence-only compilations cannot fill that window:

1. **Presence-only is not local absence.** A cell with no compiled row may be unsampled, poorly reported, or outside the contributor’s effort. It is not a verified zero.
2. **Historical pattern is not current presence.** Multi-decade OBIS/GBIF mixes are historical context (`research/FINDINGS.md` and `TRAINING_DATA_HURDLE.md` already treat the compiled OBIS total this way for goliath).
3. **Protocol non-detection is not proof the species was absent from the reef or water mass.** It is absence from the search unit under that method (see `FIRST_MODEL_FEASIBILITY.md`).
4. **Gear and design are not interchangeable.** A 15 m visual plot (Smith et al. 2011 primary/secondary frame) is not a trawl tow, CUFES transect, eDNA sample, or acoustic detection. Pooling them as one “detection” without method fields invents a likelihood.
5. **Public download is not training or display permission.** RVC/NCEI accessions remain `CONDITIONAL_REVIEW_REQUIRED` with zeros and `EPIITAJ` unverified (`RVC_RIGHTS_RECORD.md`, `RVC_MULTIYEAR_READINESS.csv`).

Until a cell has rights-cleared, effort-aware events and a matched covariate path, its honest state is **Unknown** or at best **Historical pattern** with a forced downgrade (below).

---

## Coverage metrics

For each species × 50-mile window × time slice, score coverage on these axes before assigning a readiness class.

| Metric | Question |
|---|---|
| **Effort density** | How many protocol-matched sample events fall inside the window in the training and evaluation windows? |
| **Non-detection support** | Are zeros derived from a complete sample frame, or only positive rows? |
| **Temporal freshness** | Is the latest usable biological event near the claimed “now,” or only historical? |
| **Environmental match** | Do covariates align to the event’s time, depth, and spatial support without overstating model resolution? |
| **Method consistency** | Is one survey design modeled, or are mixed gears forced into one likelihood? |
| **Rights and sensitivity** | Is there written training and coarsened-display approval? Are native coordinates withheld? |
| **Validation path** | Spatial-block and time-forward holdouts defined and feasible? |

A cell may look dense on a pin map and still fail every nowcast metric.

---

## Readiness classes

| Class | Use |
|---|---|
| **HIGH** | Rights-cleared structured detections and non-detections; effort and method fields; matched environment; validation path ready; sensitive-site rules approved. Eligible to *propose* a nowcast engineering ticket. Does not itself issue a nowcast. |
| **MODERATE** | Structured survey exists and is documented, but one or more gates are open (rights, zeros unverified, protocol mismatch across years, thin local density, or covariates not yet matched). |
| **LIMITED** | Sparse structured effort, mixed methods, or only coarse environmental candidates. Research context only. |

### Forced downgrades

Apply these regardless of how attractive the candidate looks:

| Forced label | When |
|---|---|
| **HISTORICAL_CONTEXT_ONLY** | Presence-only compilations (GBIF/OBIS-style), unverified zeros, or seasons too old for the stated training extract (e.g. NCEI 0208321 set aside as too old for the first goliath training extract). |
| **UNKNOWN** | No approved ingest, no effort frame, no covariate match, or rights still `CONDITIONAL_REVIEW_REQUIRED` with no written yes. Also the correct public output when the model card is not `PUBLISHED`. |

**Current product state:** no 50-mile cell is **HIGH** coverage for any species in this product. Candidate sources in `local-50-mile-source-inventory.csv` are proposed families. CalCOFI, WCOFS, SEAMAP, NEFSC, G-FISHER, sdmTMB, and related stacks are **not** ingested or operational here. RVC/NCRMP Florida extracts are screened only; not downloaded; zeros unverified.

Florida Keys goliath detection remains a separate, blocked path (`TRAINING_DATA_HURDLE.md`). A California Current pelagic proposal does not clear that path and does not raise any Keys cell to HIGH.

---

## Display rule (planning)

Observation, historical pattern, nowcast, forecast, and unknown stay separate layers or explicitly labeled modes. A map that merely looks predictive is not success (`FIRST_MODEL_FEASIBILITY.md`). No wreck, spawning-site, nursery, telemetry-track, or fishing-guidance coordinates are added by this framework.
