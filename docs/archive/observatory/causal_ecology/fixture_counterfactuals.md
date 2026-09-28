# W1 fixture counterfactuals

**Date:** 2026-09-18  
**Graph:** `W1-M-GIGAS-2026-09-18`  
**Trained causal model:** none. These are **worked examples of the contract**, not results.

Every fixture is:

# SCENARIO ESTIMATE — NOT OBSERVED FACT

Output class: `HYPOTHETICAL/RESEARCH MODE`. Privacy: do not attach to a public lease. Five scenarios (templates 3.1, 3.2, 3.3, 3.7, 3.8). Current-direction, prey-drop, and MPA templates remain in `counterfactual_contract.md` and are **not** expanded here because they are hard-forbidden as 72 h mortality stories (`UNKNOWN` edges W1-E21, W1-E22, W1-E53).

---

## Fixture A — `CF-W1-WATER-PLUS-2C`

**SCENARIO ESTIMATE — NOT OBSERVED FACT**

| Field | Content |
|---|---|
| Intervention \(X\) | In situ **water** temperature +2 °C vs a named lease baseline for 72 h. **Air T, tide, solar held constant.** Not a satellite SST nudge unless separately declared (that would be a different, weaker path). |
| \(Y\) | `PHYS.metabolic_spawn_condition` and relative `ops_disruption_72h` **indicator** — **not** bag % dead |
| Assumed path | W1-E10 (water T → metabolism/spawn). **Does not** include W1-E03, E05, E06, E08 |
| Path status | `ECOLOGICALLY_SUPPORTED_ASSOCIATION` for metabolism; **if** the user wanted “mass kill like 2021” the path is `UNKNOWN` / `OBSERVED_CORRELATION` (E08 kill-law) |
| Identification | `NONE` on farm. Lab contrast: George et al. 2023 water-heat **alone** vs water-heat **then** 44 °C aerial emersion https://doi.org/10.1111/gcb.16880 |
| Assumptions | Ceteris paribus air/tide/solar; culture method unchanged; no SCM; delayed death ignored if \(Y\) is 72 h |
| Limitations | +2 °C water is **not** the 2021 Salish mechanism (that was **air × midday emersion × solar**, not SST as body T). Microclimate unobserved. Spawn phenology is seasonal. |
| Uncertainty | `uncalibrated`; no percent mortality |
| Causal-evidence tier | Path: `ECOLOGICALLY_SUPPORTED_ASSOCIATION`. Context data: Tier 3 if only SST, Tier 1 if lease logger |
| Data support | `sparse` (NANOOS/NERRS exist; not this lease) https://nvs.nanoos.org/ShellfishGrowers |
| Confounders | season, geography, depth, culture, ploidy, data availability |
| Anti-claims | **SST ≥ 19 °C is not a kill law.** This fixture is not a 2021 replay. |
| Review gate | `forbidden_user_facing` if kill/2021 language; `internal_research_ok_after_review` as metabolism co-factor |

---

## Fixture B — `CF-W1-DO-BELOW-THRESHOLD`

**SCENARIO ESTIMATE — NOT OBSERVED FACT**

| Field | Content |
|---|---|
| Intervention \(X\) | DO < **3 mg L⁻¹** (example threshold, **not** a calibrated no-effect level) for ≥12 h at **culture depth** in a **named stratified basin** (Hood Canal analogue). FAO >2 mg L⁻¹ is a culture **floor**, not a 72 h kill law. |
| \(Y\) | `PHYS.hypoxic_stress` rank; optional workability if crews cannot handle stock |
| Assumed path | W1-E13 → E11 → (E12 if heat×neap co-occur) · tradeoff E17 if intertidal |
| Path status | `ECOLOGICALLY_SUPPORTED_ASSOCIATION` **only** with named basin + depth. WA-wide: `UNKNOWN` (E56) |
| Identification | `NATURAL_EXPERIMENT` / Ecology time series **if** later used; **not run here**. Distinguish from aerial-heat days (Willapa). |
| Assumptions | Sensor represents culture depth; no fusion with NSSP; no trained model |
| Limitations | Cheney et al. 2000 is Puget Sound multi-stressor observation, not Willapa identification https://www.pacshell.org/publications.asp . Satellite DO does not exist. |
| Uncertainty | `uncalibrated`; Low/None without local DO |
| Causal-evidence tier | `ECOLOGICALLY_SUPPORTED_ASSOCIATION`; labels would need Tier 1/2 farm outcomes |
| Data support | `program_exists` in some basins (ORCA/Ecology); `none` on most leases |
| Confounders | geography, depth, neap (`CF.season` via tides), observation method, sampling effort |
| Anti-claims | Not a harvest closure. Not interchangeable with 2021 air heat. Not a statewide layer. |
| Review gate | `internal_research_ok_after_review` in named basin; `forbidden_user_facing` as WA-wide product |

---

## Fixture C — `CF-W1-30D-MHW`

**SCENARIO ESTIMATE — NOT OBSERVED FACT**

| Field | Content |
|---|---|
| Intervention \(X\) | Water-column marine heatwave lasting **30 days** (Hobday-style: named climatology, named percentile). **Not** an atmospheric heat dome. |
| \(Y\) | Seasonal condition / spawn; **not** 72 h bag death; **not** “2021 again” |
| Assumed path | E10, E49; delayed-death E28 / E04 as **horizon warning** |
| Path status | `UNKNOWN` as 72 h bag headline; `OBSERVED_CORRELATION` / `ECOLOGICALLY_SUPPORTED_ASSOCIATION` as seasonal water heat |
| Identification | `NONE`. 2021 contrast is **AHW × midday emersion**, Miner et al. 2025 https://doi.org/10.3389/fmars.2025.1503019 · Raymond et al. 2022 https://doi.org/10.1002/ecy.3798 |
| Assumptions | MHW definition held; air/tide **not** set to June 2021; no SCM |
| Limitations | George scores mortality at **~30 days after a short multi-stressor**, which is not the same as 30 days of SST anomaly. Ops product window is **72 h**. SST ≠ tissue T (E06). |
| Uncertainty | `uncalibrated` |
| Causal-evidence tier | Path `UNKNOWN` for declared 72 h mortality \(Y\) |
| Data support | `none` for this scenario as a product |
| Confounders | climate modes, season, geography, delayed death, observation method |
| Anti-claims | Do not call 2021 a 30-day MHW kill. Do not issue a 72 h death forecast from a 30-day SST blob. |
| Review gate | **`forbidden_user_facing`** |

---

## Fixture D — `CF-W1-HAB-IN-REGION`

**SCENARIO ESTIMATE — NOT OBSERVED FACT**

| Field | Content |
|---|---|
| Intervention \(X\) | A **named** taxon is present in a named sub-basin (SoundToxins-class cell counts as **context**, not loaded). Two forks **must not be merged.** **Fork 1:** animal-stress taxon. **Fork 2:** human-toxin taxon feeding NSSP. |
| \(Y\) fork 1 | Feeding shutdown / hypothesized animal toxicity (`EXPERT_HYPOTHESIS`, W1-E35) |
| \(Y\) fork 2 | `OUT.doh_harvest_status` (`POLICY_MAPPING`, W1-E43) — **not** farm mortality |
| Path status | Fork 1 `EXPERT_HYPOTHESIS`; fork 2 `OBSERVED_CORRELATION` policy; **causal mortality via DOH = `UNKNOWN` (E42)** |
| Identification | Split lists a priori. Tissue tests (authority) vs farm gaping. *Heterosigma* ≠ PSP. |
| Assumptions | No toxin nowcast; SoundToxins ≠ NSSP reopening; no mixed green/red score |
| Limitations | WDFW 2019 is narrative https://wdfw.medium.com/whats-been-causing-mass-shellfish-die-offs-around-puget-sound-1ada7071a242 · SoundToxins https://soundtoxins.org/about.html · weekly, not 72 h continuous |
| Uncertainty | `uncalibrated`; confidence **None** for toxins |
| Causal-evidence tier | `EXPERT_HYPOTHESIS` (animal) / policy mapping (human) |
| Data support | `program_exists` (SoundToxins, DOH) as **catalog**; not ingested |
| Confounders | observation method, regulation, season, sampling effort, geography |
| Anti-claims | **WA DOH closure is regulatory, not causal mortality in the ops model.** Never “safe to eat,” “toxin-free,” or harvest authorization. |
| Review gate | **`forbidden_user_facing`** if readable as food safety or as ops+sanitation blend |

---

## Fixture E — `CF-W1-PREFERRED-DEPTH-HYPOXIC`

**SCENARIO ESTIMATE — NOT OBSERVED FACT**

| Field | Content |
|---|---|
| Intervention \(X\) | Hypoxia at the **culture elevation / depth the animals occupy** (not a surface pixel; not “the preferred depth of wild mobile fish”). |
| \(Y\) | `PHYS.hypoxic_stress` for **subtidal/raft**; aerial-heat vs hypoxia **tradeoff** for intertidal (E17) |
| Assumed path | E11, E13, E17, E25; **not** E56 (WA-wide law) |
| Path status | `ECOLOGICALLY_SUPPORTED_ASSOCIATION` in a named stratified basin with depth; `UNKNOWN` as statewide law |
| Identification | Culture-method split: intertidal bags can emersion-escape water hypoxia and **gain** 2021-type aerial risk; rafts cannot. |
| Assumptions | Elevation known to centimetres; no public lease map |
| Limitations | No satellite DO; Hood Canal instrumentation is not Willapa GT |
| Uncertainty | `uncalibrated` |
| Causal-evidence tier | `ECOLOGICALLY_SUPPORTED_ASSOCIATION` (named) / `UNKNOWN` (generic) |
| Data support | `sparse` |
| Confounders | depth, geography, culture method, vessel access, privacy |
| Anti-claims | Not Chinook 8–12 °C depth refuge. Not a public heatmap (farm failure inversion). |
| Review gate | `forbidden_user_facing` at lease grain; named-basin mechanism note only after review |

---

## What these fixtures are not

They are not hindcasts of 26–28 June 2021, not DOH closures, not OsHV-1 WA outbreaks, not OA bag kills, not MPA benefits, not current-reversal mortality, not chlorophyll-as-oysters.

Templates **not** fixtured (still contracted, still bannered, **forbidden user-facing** as 72 h mortality): `CF.CURRENT.DIRECTION`, `CF.PREY.DROP`, `CF.MPA.REDUCE_FISHING`.
