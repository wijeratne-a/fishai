# Region screening — first goliath grouper detection model

**Date:** 2026-09-23  
**Branch context:** `integrate/globe-ux-2026-09-23`  
**Species:** Atlantic goliath grouper, *Epinephelus itajara*, WoRMS AphiaID 159353

This screen asks which region could support a first **detection-given-effort** model. It does not choose a place to draw animals, wrecks, nurseries, or fishing spots.

Scores:

| Score | Meaning |
|---|---|
| HIGH | Public evidence supports the item |
| PARTIAL | A program exists, but the extract, zeros, or rights were not confirmed |
| LOW | Public evidence argues against using this as the first frame |
| UNKNOWN | Not established in this pass |
| HIGH RISK | Sensitive sites are a reason to withhold geometry |

No region is cleared for fitting.

---

## Florida Keys and southeast Florida reef tract (RVC domain)

This is the Florida reef-tract visual-survey footprint: Florida Keys, Dry Tortugas, and southeast Florida, as separate region codes in the NOAA Reef Visual Census. It is one design family, not a claim that density is the same in each code.

| Criterion | Score | Evidence |
|---|---|---|
| Structured goliath records | PARTIAL | The survey records species counts. The portal species-code scheme can represent *Epinephelus itajara* as `EPIITAJ`. This pass did not count how many samples contain that code. |
| Non-detections | UNKNOWN | Sample units exist. Whether the public CSV stores zeros, or only positive species rows, was not verified. |
| Effort metadata | HIGH | Published fields include sample unit, stratum, region, year, day, visibility, and diver samples. |
| Habitat covariates | PARTIAL | A habitat code is a published field. An external habitat map was not licensed. |
| Depth coverage | PARTIAL | Average depth of the secondary unit is a published field, in meters. The numeric range of goliath-positive samples was not computed. |
| Temporal continuity | PARTIAL | Portal: files from 1999. FWC: Keys visual work with RVC methods from 2008, then biennial even years after 2014, generally April–September. Not a monthly census. |
| Environmental covariates | UNKNOWN | None matched to sample dates in this repo. |
| Validation feasibility | PARTIAL | Multiple years and separate region codes could support a spatial block and a time-forward split, after an approved extract exists. |
| Sensitive-location risk | HIGH RISK | Adult structure and any aggregation inside a sample must stay off the public map. The model target is a sample-unit probability, not a site guide. |
| Governance / rights | UNKNOWN | Files are posted. Training and display rights are not `APPROVED_*`. |
| Human scientific reviewer | UNKNOWN | None named. |

**Screen result:** least-blocked candidate. Still not a cleared region.

---

## Ten Thousand Islands and southwest Florida estuaries

| Criterion | Score | Evidence |
|---|---|---|
| Structured goliath records | PARTIAL | NOAA prose, already filed in `ECOLOGY_PROFILE.md`, describes juvenile mark-recapture in the Ten Thousand Islands. FWC inshore monitoring covers estuarine strata. Neither table was opened. |
| Non-detections | UNKNOWN | Not demonstrated. |
| Effort metadata | PARTIAL | FWC describes stratified-random monthly sampling and gear. The open map service may be a thinned point layer. |
| Habitat covariates | PARTIAL | Mangrove and estuary classes are the ecological context. No layer was licensed. |
| Depth coverage | UNKNOWN | Juvenile habitat is shallow. Survey depth fields were not read. |
| Temporal continuity | UNKNOWN | Program is long-term. An analysis-ready goliath extract was not found. |
| Environmental covariates | UNKNOWN | Not matched. |
| Validation feasibility | UNKNOWN | Cannot design a holdout without the sample frame. |
| Sensitive-location risk | HIGH RISK | Juvenile mangrove and creek habitat is nursery-adjacent. No creek names or coordinates belong in this product. |
| Governance / rights | UNKNOWN | Open-data pages exist. Rights are not approved. |
| Human scientific reviewer | UNKNOWN | None named. |

**Screen result:** a possible later juvenile target. It is a different animal stage and a different gear than the reef visual census. It is not the first model region.

---

## Gulf of Mexico as one region

| Criterion | Score | Evidence |
|---|---|---|
| Structured goliath records | LOW | RVC includes Flower Garden Banks as its own region code. That does not make the whole Gulf one survey. SEAMAP was not fetched. |
| Non-detections | UNKNOWN | Not fetched. |
| Effort metadata | LOW | Mixed historical gears in the OBIS compiler. No single Gulf effort frame is in hand. |
| Habitat covariates | UNKNOWN | Not selected. |
| Depth coverage | UNKNOWN | Not selected. |
| Temporal continuity | LOW | Compiler years are not a Gulf survey calendar. |
| Environmental covariates | PARTIAL | Ocean fields exist as products. None are ingested, and none are sightings. |
| Validation feasibility | LOW | A Gulf-wide grid would hide gear changes and overstate resolution. |
| Sensitive-location risk | HIGH RISK | Structure, wrecks, and any aggregation sites. |
| Governance / rights | UNKNOWN | Not reviewed. |
| Human scientific reviewer | UNKNOWN | None named. |

**Screen result:** too broad for a first model. Do not average the Keys design across the Gulf.

---

## Caribbean regional programs

| Criterion | Score | Evidence |
|---|---|---|
| Structured goliath records | PARTIAL | The same RVC portal lists Puerto Rico, St. Thomas/St. John, and St. Croix as region codes. Other Caribbean states were not inventoried. |
| Non-detections | UNKNOWN | Same file-layout question as Florida. |
| Effort metadata | PARTIAL | Same RVC design where those region codes were surveyed. |
| Habitat covariates | UNKNOWN | Not licensed. |
| Depth coverage | PARTIAL | Same depth field, uncounted. |
| Temporal continuity | UNKNOWN | Not counted per region code. |
| Environmental covariates | UNKNOWN | Not matched. |
| Validation feasibility | UNKNOWN | A US Caribbean block could be a later transfer test. It is not the first fit. |
| Sensitive-location risk | HIGH RISK | Same structure-site rule. |
| Governance / rights | UNKNOWN | NOAA portal rights still unconfirmed. Other countries were not reviewed. |
| Human scientific reviewer | UNKNOWN | None named. |

**Screen result:** keep as a possible later spatial holdout inside the same US visual-survey design. Not the first region.

---

## Brazil

| Criterion | Score | Evidence |
|---|---|---|
| Structured goliath records | LOW | Giglio and colleagues (doi:10.1590/1982-0224-20130166) analyzed diver reports from 2005–2011 and state that sampling effort could not be obtained. |
| Non-detections | LOW | The same paper treats the data as sporadic presence reports. |
| Effort metadata | LOW | Authors say effort was unavailable. |
| Habitat covariates | PARTIAL | The protocol asked divers about natural versus artificial habitat. That is not a survey grid. |
| Depth coverage | PARTIAL | Divers reported depth. It is not a designed depth frame. |
| Temporal continuity | PARTIAL | Projeto Meros do Brasil describes work since 2002. An open analysis-ready table was not found. |
| Environmental covariates | UNKNOWN | Not matched. |
| Validation feasibility | LOW | Presence-only reports cannot support a detection probability. |
| Sensitive-location risk | HIGH RISK | Project pages describe aggregation monitoring, telemetry, and juvenile estuary work. |
| Governance / rights | UNKNOWN | No open extract terms were confirmed. A harvest moratorium is a legal fact and is not fishing advice. |
| Human scientific reviewer | UNKNOWN | None named. A Brazilian partner would be required before any Brazil model. |

**Screen result:** not a first-model region. Presence reports and telemetry stay out of the product.

---

## Screen conclusion

No region is implementation-ready.

The only design that is public, spatially bounded, and built around sample units rather than sighting pins is the **Florida reef-tract Reef Visual Census** (Florida Keys, with Dry Tortugas and southeast Florida as separate codes in the same program). That is a conditional candidate, not a winner.

Ten Thousand Islands, the Gulf as a whole, the wider Caribbean, and Brazil do not meet the observation-design bar on the evidence in hand.
