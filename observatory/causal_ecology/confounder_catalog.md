# Confounder catalog — causal ecology

**Date:** 2026-09-18  
**Status:** Required adjustment / bias list for every driver query and counterfactual.  
**Not a feature store.** Listing a confounder does not authorize ingest.

If a query cannot say how these would bias \(Y\) or the observed label, the query is incomplete and the honest answer is `UNKNOWN`.

---

## 1. Universal confounders (all taxa, all geographies)

These ten **must** be considered. “Does not apply” is allowed only with a one-line reason (example: AIS is irrelevant to sessile planted stock **as abundance**, but vessel access still confounds **whether a mortality walk happened**).

| ID | Confounder | What it actually is | Typical bias if ignored | W1 oyster (72 h ops) | Never treat as |
|---|---|---|---|---|---|
| `CF.sampling_effort` | Sampling effort | Hours on the tide, number of bags checked, survey design, who walked which elevation | Apparent mortality tracks **inspection**, not death; missing zeros | Farm checks cluster after heat rumors and spring tides | Abundance of oysters |
| `CF.vessel_access` | Vessel / site access | Weather, ramp, mud, staffing, small-craft conditions | Workability labels exist only on days people could go; blown-out days look like “no disruption” | Storms prevent the observation of storms | Weather-safety advice; biology |
| `CF.season` | Season / calendar | Degree-days, spawn phenology, legal harvest season, month dummies | Models secretly become climatology (RT-XCUT-07) | Summer mortality literature is seasonal; 72 h product must not be a month lookup | A 72 h ocean mechanism |
| `CF.geography` | Geography / basin | Willapa ≠ Hood Canal ≠ South Sound ≠ Discovery Bay | Pooled “WA oyster” model is misspecified | Heat-emersion vs hypoxia vs runoff split by basin | Transferable kill law |
| `CF.depth` | Depth / tidal elevation | Centimetres of bed height; intertidal vs subtidal vs raft | Same weather, opposite exposure (air heat vs water-column DO) | First-class stratum; culture method | Satellite SST as depth |
| `CF.observation_method` | Observation method | Visual gaping, protocol counts, logger, satellite, DOH water sample, tissue toxin test | Each method measures a **different quantity** | DOH fecal/toxin ≠ farm mortality; SST ≠ tissue T | One fused “stress score” |
| `CF.regulation` | Regulation | NSSP class, biotoxin, Vp control plan, seasons, MPAs, size limits | Legal status masquerades as biology | **WA DOH closure is regulatory, not causal mortality in the ops model** | Harvest authorization from ops-stress |
| `CF.fishing_behavior` | Fishing / farm behavior | Effort, soak, bait, handling, crowding, early harvest, who follows the model | Treatment contaminates the outcome; CPUE ≠ \(N\) | Handling after heat; harvest censors bags that would have died later | Proof of abundance or of model skill |
| `CF.climate_modes` | Climate modes | ENSO, PDO, NE Pacific marine heatwave indices, “the Blob” | Seasonal-to-multi-year; leaks into 72 h fits as spurious skill | 2021 was an **atmospheric** heat dome, not a marine SST mode analogue | 72 h cause; 2021 replay |
| `CF.data_availability` | Data availability | Sensors on **this** lease vs km-scale SST; delayed-mode composites; partner DUA | Availability-at-\(t\) leakage; SST-only products look complete | SST-only ⇒ confidence **Low/None** (`prediction_contract.md`) | Proof that a cause was absent |

---

## 2. How confounders enter the DAG

Draw confounders as nodes that affect **treatment assignment, selection into the dataset, or the measurement of \(Y\)**, not as extra “AI features.”

```text
CF.season, CF.geography, CF.climate_modes  →  L1_ENV and L2_HAB
CF.depth, culture method                   →  emersion vs DO exposure
CF.sampling_effort, CF.vessel_access,
CF.observation_method, CF.data_availability →  observed labels only
CF.regulation                               →  DOH status (policy); also selection if harvest censors bags
CF.fishing_behavior                         →  handling / inventory / whether a 72 h death is observed
```

**Collider warning:** analyzing only farms that submitted mortality logs, or only growing areas that closed, opens a back-door. Do not condition on the reporter without a selection model.

**Mediator vs confounder:** tide is a **mediator/modulator** of aerial heat, not a toxin. Month is usually a **confounder** (spawn, effort, regulation), not a mechanism.

---

## 3. W1 additional confounders (oyster-specific)

| ID | Why it is not optional |
|---|---|
| `CF.culture_method` | Intertidal bag vs bottom vs raft vs FLUPSY changes the 2021-type pathway entirely |
| `CF.ploidy_pedigree` | Lab: triploids took ~2.5× mortality after 30 °C water **then** 44 °C aerial emersion (George et al. 2023). Field WA not identified. |
| `CF.microhabitat` | Bag color, shade, mud vs gravel, cm elevation, solar aspect — tissue T residuals |
| `CF.delayed_death` | Deaths accrue days–weeks; a 72 h window can miss the label when the cause was inside the window |
| `CF.label_doh_contamination` | Training ops-stress on closures builds a shadow food-safety model (RT-OYS-04, `ground_truth_relabel_W1.md`) |
| `CF.prior_stress` | Handling or prior heat primes later mortality |
| `CF.co_occurring_taxa` | Burrowing shrimp, eelgrass, fouling; not 72 h headline |

---

## 4. Cross-wedge reminders (do not import blindly into W1)

| Confounder | Chinook 24–48 h | Lobster next trip |
|---|---|---|
| Sampling effort | Bag-limit truncation; weekend trips | Soak, trap density |
| Vessel access | Go/no-go looks like “no fish” | Haulability |
| Regulation | Closed area must not be scored | Legal size / v-notch ≠ density |
| Fishing behavior | Skipper skill, secret holes | Bait, competition |
| Depth | 8–12 °C band may be **deeper** when SST warms | Bottom T ≠ SST |
| AIS | Effort/crowding, **not** Chinook | Most inshore boats have no AIS duty |

---

## 5. Completeness test (gate for any query)

A driver or counterfactual record is incomplete unless it answers, in prose:

1. Which of the ten universal confounders could produce the same observed association **without** the proposed mechanism?  
2. What observation would **break** that alternative (negative control, contrast geography, culture-method split, sensor vs SST)?  
3. Is the label `ops_disruption_72h` / CPUE / encounter, or a **wrong** official closure / landings series?

Fail the gate → return `UNKNOWN` and do not emit a scenario to users.
