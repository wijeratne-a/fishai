# First-model decision memo

**Date:** 2026-09-23  
**Audit:** `audit/actionable-data-to-prediction-audit-2026-09-23.md`

## FIRST_MODEL_RECOMMENDATION

Fit, only after a written yes, a **survey-season probability of detection of one common reef fish during a standardized Reef Visual Census dive** on the Florida Keys portion of **NCEI Accession 0282183** (1 June–28 November 2022).

The species is not chosen today. It is the common species in that approved table with enough detections to meet a reviewer-set minimum and with low sensitive-site risk. Atlantic goliath grouper is not the default.

| Item | Decision |
|---|---|
| Target species or group | One common Florida Keys reef fish, named only after the approved table is counted. Not goliath grouper. |
| Region | Florida Keys stratum of the 2022 RVC domain. Dry Tortugas and southeast Florida stay out of the first fit. |
| Radius or spatial support | The survey’s 200 m primary sample unit and 15 m second-stage plot (Smith et al. 2011). A 50-mile circle is a user window over those units, not a finer biological grid. |
| Target variable | Probability that the species code is recorded on a completed diver survey, given the protocol, depth, and effort on that survey. |
| Observation method | Two-stage stratified stationary point count, 7.5 m radius, as stated for this program family. |
| Required source | NCEI Accession 0282183. |
| Source-access status | `CONDITIONAL_REVIEW_REQUIRED`. Not downloaded. |
| Model family | Binomial or single-season occupancy on the diver survey, only if it beats the baselines below. Not a forecast model. |
| Baseline models | Season-only detection rate; habitat or stratum only; effort and visibility and depth only; spatial rate with the test block held out. |
| Required covariates | Fields on the dive: depth, stratum or habitat code, visibility, region, date. Ocean-model fields are optional and are not the first fit. |
| Validation design | Spatial-block holdout inside the Keys. Time-forward only if a second year with the same protocol is cleared. 0306184 is not that year until the single-stage change is reconciled. |
| Safety and display | Coarse probabilities only. No sample coordinates. No goliath layer in this first publication. |
| Key dependency | Written training and coarsened-display permission, then a hash and a zero rule. |
| Fallback | If 0282183 is declined or has no constructible zeros, switch to CalCOFI CUFES egg or encounter presence for Pacific sardine or northern anchovy, still only after that program’s own written yes. |

Goliath grouper remains a later question on the same frame. Fit it only if `EPIITAJ` detections meet `THRESHOLD_TO_BE_DEFINED_WITH_REVIEWER` and a sensitive-site review allows a coarse layer. Until then the goliath card stays `NOT_PUBLISHED`.

No nowcast or forecast is issued by this memo.
