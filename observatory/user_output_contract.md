# User output contract — Global Saltwater Life Observatory

**Date:** 2026-09-18  
**Status:** Binding on every observatory-facing output (cards, APIs, maps, prototypes, papers, slides).  
**Default live output this iteration:** `UNKNOWN/INSUFFICIENT DATA`  
**Not a customer product contract.** The commercial 14-field brief in `artifacts/scientific_red_team/prediction_contract.md` remains the product contract for the 1×1×1×1 wedge. This document is stricter on global taxa, depth, and “model ≠ observation.”

If a sentence could be read as “we know where all the animals are,” it is out of contract.

---

## 1. Mandatory classification

Every output about organisms or their environment-as-biology must carry **both**:

### 1.1 Capability class (exactly the primary claim; others allowed as notes)

1. Observable today  
2. Inferable today  
3. Forecastable today  
4. Requires new data infrastructure  
5. Scientifically plausible but unproven  
6. Technically speculative  
7. Physically impossible or not currently measurable  

### 1.2 Output class (exactly one)

`DIRECTLY OBSERVED`  
`REMOTELY DETECTED`  
`SURVEY-DERIVED`  
`TAG/TELEMETRY-DERIVED`  
`OPERATIONALLY OBSERVED`  
`MODEL-INFERRED`  
`FORECAST`  
`HYPOTHETICAL/RESEARCH MODE`  
`UNKNOWN/INSUFFICIENT DATA`

**UNKNOWN/INSUFFICIENT DATA is a complete, high-quality output.** It must still include taxon, geography, what was asked, why evidence fails, and what measurement would help.

A **model may never be labeled** `DIRECTLY OBSERVED`, `REMOTELY DETECTED`, `SURVEY-DERIVED`, `TAG/TELEMETRY-DERIVED`, or `OPERATIONALLY OBSERVED`.

---

## 2. Claims that must never appear

- Exact location of every individual of a taxon.  
- Exact number of all animals in a region (census) without a designed census.  
- Real-time tracking of a species without contemporaneous direct observation or a live telemetry feed that is actually connected.  
- Direct abundance from a satellite **surface** image (SST, ocean color, SAR vessel detections).  
- Biological abundance from vessel density (AIS, VMS, “fishing effort heatmaps”).  
- Safe / legal harvest, food safety, navigation safety, or ESA take authorization from habitat suitability.  
- Certainty where coverage is sparse.  
- “The digital twin shows” as a synonym for “we measured.”  
- Public coordinates of endangered taxa, spawning aggregations, nurseries, nesting beaches, haulouts, private fishing spots, farm performance, or Indigenous knowledge.  
- Up-tier language (“operational global tracking,” “AI abundance”) for T0–T2 rows.

Satellite detection of **surface-visible** features (some large whales in imagery research, floating *Sargassum* mats, giant-kelp canopy, coccolithophore blooms) is `REMOTELY DETECTED` of **that signal**, not a census, and not automatically a species-level T3.

---

## 3. Required fields on every organism-related output

### 3.1 Observatory scientific fields (spec §1)

| # | Field | Notes |
|---|--------|--------|
| S1 | Observation / issue time | UTC |
| S2 | Data latency | Per critical input + overall fresh/stale/missing |
| S3 | Geographic precision | Cell, polygon, or coarsened public grain |
| S4 | Depth precision | Depth band or `depth_unknown` |
| S5 | Evidence / output class | §1.2 |
| S6 | Source provenance | Official URLs, versions, access or cutoff dates |
| S7 | Model version | or `none` |
| S8 | Uncertainty | Interval **or** rationale; no fake ± |
| S9 | Legal / privacy restriction | `PUBLIC` `COARSENED` `DELAYED` `RESTRICTED` `PRIVATE` `NEVER_PUBLISH` |
| S10 | Ecological sensitivity | including listed / spawning / nursery flags |
| S11 | Known limitations | required even when confident |

### 3.2 Shared decision-card fields (adapted from commercial 14)

Use these whenever the output could be mistaken for advice. Research cards still fill them; “suggested action” may be “do not act; evidence insufficient.”

| # | Field | Observatory use |
|---|--------|-----------------|
| 1 | Species and geography scope | Accepted WoRMS name + AphiaID + life stage + population unit + domain |
| 2 | Target definition | What quantity (suitability, historical occurrence, etc.) |
| 3 | Time horizon | Historical window, nowcast latency, or forecast valid-from/to |
| 4 | What it means | One paragraph, class-labeled |
| 5 | What it does **not** mean | Explicit negatives |
| 6 | Data freshness | |
| 7 | Confidence and uncertainty | `none` / `low` / `medium` / `high` only if rules in the commercial uncertainty policy can be applied; else qualitative + `uncalibrated` |
| 8 | Relevant inputs/drivers | Named as inputs, not as proof of presence |
| 9 | Known missing inputs | |
| 10 | Source attribution | |
| 11 | Regulatory / safety disclaimer | Not harvest, not navigation, not food safety, not take |
| 12 | Suggested options, not commands | Research: next measurement; never “fish here” |
| 13 | Outcome-reporting mechanism | or `not_applicable_research_mode` |
| 14 | Error / feedback mechanism | |

Plus: capability class; support tier; extrapolation flag; `as_of` / source cutoff.

---

## 4. Language that is in contract vs out

| In contract | Out of contract |
|-------------|-----------------|
| “OBIS metadata show N compiled occurrence records for AphiaID … as of 2026-09-18. This is not a census.” | “There are N fish in this box.” |
| “Habitat suitability is `MODEL-INFERRED` and is not current presence.” | “Species X is here now.” |
| “Tagged-animal track, `TAG/TELEMETRY-DERIVED`, individual ≠ population.” | “The population migrated along this line.” |
| “UNKNOWN: not enough evidence exists.” | “Assume uniform density.” |
| “Forecast `FORECAST`, not validated, `NOT READY FOR USE`.” | “Operational global twin.” |
| “Official harvest status is the authority’s, last verified …” | “Legal to harvest.” |

Confidence labels, if used: **High / Medium / Low / None** with reasons. No three-decimal biological probabilities until a human accepts a calibration plot from prospective data.

---

## 5. Support-tier → allowed emitted products

| Tier | Allowed emission | Default class |
|------|------------------|---------------|
| T0 | Identity + insufficient-data statement | `UNKNOWN/INSUFFICIENT DATA` |
| T1 | Historical occurrence coverage, biased by effort | `SURVEY-DERIVED` |
| T2 | Suitability + uncertainty; no presence claim | `MODEL-INFERRED` |
| T3 | Current relative condition / encounter **if validated** | `MODEL-INFERRED` or `SURVEY-DERIVED` |
| T4 | Short-horizon forecast **if validated** | `FORECAST` |
| T5 | Observation or track overlay | `DIRECTLY OBSERVED` / `REMOTELY DETECTED` / `TAG/TELEMETRY-DERIVED` / `OPERATIONALLY OBSERVED` |
| T6 | Operational brief with performance | as validated, still never census-from-space |

Iteration 1 public emission for all example taxa: **T0 statement or registry metadata only.** CSV tiers are eligibility, not live maps.

---

## 6. Privacy and ecological safety at the output boundary

Every record inherits a restriction from the observatory rights work (`sensitive_location_policy.md`, `data_rights_register.md` when present):

`PUBLIC` | `COARSENED` | `DELAYED` | `RESTRICTED` | `PRIVATE` | `NEVER_PUBLISH`

Public layers require ecological-harm review. Default when unsure: one tier stricter.

The commercial coarsening rules for the three wedge taxa still apply if those taxa appear in observatory demos. A global scientific mandate does not relax them.

---

## 7. Relationship to the commercial product contract

- Commercial outputs must satisfy **this** contract **and** the wedge prediction contract (categories A–E, never-claims for oyster food safety, Chinook ESA, lobster CPUE≠abundance).  
- Observatory research outputs must satisfy **this** contract even when there is no customer.  
- The observatory must not ship a world animal heatmap as a “prototype” that the wedge paused for being unsafe.  
- Shared vocabulary: habitat ≠ presence; CPUE ≠ abundance; official status ≠ model.

---

## 8. Prototype and API rule

Any research API (see architecture agents) returns the fields in §3 or it is non-compliant. A missing class label defaults to `UNKNOWN/INSUFFICIENT DATA` and **must not** be filled by the model server with a prettier synonym.

Version this contract as `OUTPUT-CONTRACT-OBS-2026-09-18-v1`.
