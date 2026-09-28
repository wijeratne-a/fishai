# W1 causal ecology graph — *Magallana gigas* (Pacific oyster)

**Graph ID:** `W1-M-GIGAS-2026-09-18`  
**Date / URL access date:** 2026-09-18  
**Taxon:** *Magallana gigas* (Thunberg, 1793), WoRMS AphiaID [836033](https://www.marinespecies.org/aphia.php?p=taxdetails&id=836033). Synonym *Crassostrea gigas* AphiaID 140656 (unaccepted combination) for joins only.  
**Scope:** Washington farmed stock, spat through market, 24–72 h **operational stress/disruption** (Category D). Not harvest legality. Not abundance.  
**Trained causal model:** **none.**  
**Output class:** `HYPOTHETICAL/RESEARCH MODE`

This graph **must** be read with:

- 2021 Salish / heat-dome mechanism = **air temperature × midday emersion × solar**, **not** satellite SST as body temperature.  
- **SST ≥ 19 °C is not a kill law.**  
- **OsHV-1 is not an established 72 h Washington driver.**  
- **OA / Ω is hatchery-larva, not a 72 h bag headline.**  
- **WA DOH closure is regulatory, not causal mortality in the ops model.**

Statuses are exactly one of: `OBSERVED_CORRELATION` | `ECOLOGICALLY_SUPPORTED_ASSOCIATION` | `CAUSALLY_TESTED_RELATIONSHIP` | `EXPERT_HYPOTHESIS` | `UNKNOWN`.

---

## 0. Pathway (W1 instantiation)

```text
L1 environmental variables
    → L2 habitat (emersion, microclimate, DO, S, waves, culture elevation)
        → L3 food / HAB / pathogen
            → L4 physiology (tissue T ≠ SST; spawn; hypoxia; delayed death; larval calcification is a side branch)
                → L5 sessile / planted inventory / ops workability / mortality
                   ↛ DOH harvest class as physiology
```

Movement at 72 h ≈ 0 after settlement. Abundance on the lease is **planted**. Do not predict “where the oysters are.”

---

## 1.0 EMIV registry bindings (`v0.1-draft`)

Graph `node_id` values are unchanged. Bind to [`../emiv/emiv_registry.csv`](../emiv/emiv_registry.csv) where a row exists. **DOH = `EMIV-HUM-HARV-001` constraint, not ops mortality. SST = `EMIV-PHY-SST-001` PROXY.** Solar = `EMIV-PHY-SOLAR-001`. Tissue/bag T = `EMIV-PHY-TISST-001`. Full table: [`../emiv/engine_id_crosswalk.md`](../emiv/engine_id_crosswalk.md).

| node_id | emiv_id |
|---|---|
| `ENV.air_temperature` | `EMIV-PHY-ATEMP-001` |
| `ENV.water_temperature_in_situ` | `EMIV-PHY-WTEMP-001` |
| `ENV.satellite_sst` | `EMIV-PHY-SST-001` |
| `ENV.solar_irradiance` | `EMIV-PHY-SOLAR-001` |
| `ENV.solar_geometry_timing` | `EMIV-PHY-SOLAR-001` |
| `ENV.precipitation_discharge` | `EMIV-BGC-RUNOFF-001` |
| `ENV.wind_waves` | `EMIV-PHY-WIND-001` \| `EMIV-PHY-WAVE-001` |
| `ENV.astronomical_tide` | `EMIV-PHY-TIDE-001` |
| `ENV.pH_omega` | `EMIV-BGC-OMEGA-001` (Ω; related `EMIV-BGC-PH-001`) |
| `ENV.nutrients` | `EMIV-BGC-NUTR-001` |
| `ENV.climate_modes` | `EMIV-HUM-CLIM-001` |
| `HAB.emersion_duration` | `EMIV-PHY-EMERS-001` |
| `HAB.water_column_heat` | `EMIV-PHY-WTEMP-001` |
| `HAB.dissolved_oxygen` | `EMIV-BGC-DOXY-001` |
| `HAB.salinity` | `EMIV-PHY-SALIN-001` |
| `HAB.turbidity` | `EMIV-BGC-TURB-001` |
| `HAB.wave_loading` | `EMIV-PHY-WAVE-001` |
| `HAB.stratification_flushing` | `EMIV-PHY-STRAT-001` |
| `HAB.culture_method_elevation` | `EMIV-HUM-CULT-001` |
| `HAB.residence_time_currents` | `EMIV-PHY-CURR-001` |
| `BIO.phytoplankton_food` | `EMIV-BGC-CHL-001` (pigment proxy, not abundance) |
| `BIO.hab_animal_stress` | `EMIV-ECO-HAB-001` |
| `BIO.oshv1` | `EMIV-ECO-DIS-001` |
| `BIO.vibrio` | `EMIV-ECO-DIS-001` |
| `BIO.predators_fouling` | `EMIV-ECO-PRED-001` |
| `PHYS.handling_stress` | `EMIV-HUM-HAND-001` |
| `PHYS.tissue_temperature` | `EMIV-PHY-TISST-001` |
| `OUT.lease_inventory` | `EMIV-BIO-ABUND-001` (farm count; PRIVATE) |
| `OUT.ops_workability` | `EMIV-ECO-OPSOUT-001` |
| `OUT.ops_gear_disruption` | `EMIV-ECO-OPSOUT-001` |
| `OUT.farm_mortality_72h` | `EMIV-ECO-OPSOUT-001` |
| `OUT.farm_mortality_delayed` | `EMIV-ECO-OPSOUT-001` |
| `OUT.doh_harvest_status` | `EMIV-HUM-HARV-001` |

Unresolved (leave `node_id` only): `HAB.intertidal_microclimate`, `BIO.hab_human_toxin`, `PHYS.metabolic_spawn_condition`, `PHYS.hypoxic_stress`, `PHYS.osmotic_stress`, `PHYS.larval_calcification`, `PHYS.delayed_mortality`, `OUT.sessile_no_72h_movement`, `OUT.planted_distribution`, `CF.*`.

---

## 1. Nodes

### L1 — environmental variables

| node_id | Quantity | forbidden_as |
|---|---|---|
| `ENV.air_temperature` | Shelter / 2 m air T; still not bag microclimate | body T alone |
| `ENV.solar_irradiance` | Insolation during emersion | optional decoration |
| `ENV.solar_geometry_timing` | Whether low tide overlaps midday | moon-as-toxin |
| `ENV.water_temperature_in_situ` | Water T at culture depth | SST; kill law at 19 °C |
| `ENV.satellite_sst` | Skin / foundation SST pixel | **body T, abundance, legality** |
| `ENV.precipitation_discharge` | Rain + gauged rivers | fecal legality |
| `ENV.wind_waves` | Wind, waves, fetch | weather-safety advice |
| `ENV.astronomical_tide` | Predicted water level | toxin |
| `ENV.pH_omega` | pH / Ω_aragonite | 72 h adult headline |
| `ENV.nutrients` | DIN/DIP | 72 h mortality |
| `ENV.climate_modes` | ENSO/PDO/MHW indices | 2021 AHW analogue |

### L2 — habitat conditions

| node_id | Quantity |
|---|---|
| `HAB.emersion_duration` | Hours aerial at this bed height |
| `HAB.intertidal_microclimate` | Bag color, mud T, shade, aspect |
| `HAB.water_column_heat` | In-water heat at culture depth |
| `HAB.dissolved_oxygen` | DO at culture depth |
| `HAB.salinity` | S |
| `HAB.turbidity` | TSS / turbidity |
| `HAB.wave_loading` | Gear/burial force |
| `HAB.stratification_flushing` | Neap / basin stratification |
| `HAB.culture_method_elevation` | Intertidal bag / bottom / raft / FLUPSY + cm height |
| `HAB.residence_time_currents` | Residual circulation / residence |

### L3 — prey / predator / pathogen / food-web

| node_id | Quantity | note |
|---|---|---|
| `BIO.phytoplankton_food` | Food for growth | not abundance |
| `BIO.hab_animal_stress` | Named taxa that stress **the oyster** | split from NSSP |
| `BIO.hab_human_toxin` | PSP/DSP/ASP producers | food safety only |
| `BIO.oshv1` | Ostreid herpesvirus µVar | CA ≠ WA |
| `BIO.vibrio` | Opportunistic *Vibrio* spp. (animal) | ≠ Vp harvest control |
| `BIO.predators_fouling` | Drills, crabs, fouling | not 72 h headline |

### L4 — life-stage physiology

| node_id | Quantity |
|---|---|
| `PHYS.tissue_temperature` | Body / biomimetic T **during emersion** |
| `PHYS.metabolic_spawn_condition` | Metabolism, gametogenesis, ripe/spent |
| `PHYS.hypoxic_stress` | Oxyregulation / shutdown |
| `PHYS.osmotic_stress` | Acute low S |
| `PHYS.larval_calcification` | **Hatchery larvae only** |
| `PHYS.handling_stress` | Crowding, tumbling, time out of water |
| `PHYS.delayed_mortality` | Death accruing days–weeks after exposure |

### L5 — movement / distribution / abundance / ops

| node_id | Quantity | privacy |
|---|---|---|
| `OUT.sessile_no_72h_movement` | No relocation off lease | PUBLIC fact |
| `OUT.planted_distribution` | Where bags/cultch were placed | PRIVATE GPS |
| `OUT.lease_inventory` | Count/biomass planted | PRIVATE |
| `OUT.ops_workability` | Could crew work the tide? | PRIVATE |
| `OUT.ops_gear_disruption` | Gear loss / burial | PRIVATE |
| `OUT.farm_mortality_72h` | Deaths inside 72 h window | PRIVATE |
| `OUT.farm_mortality_delayed` | Deaths to ~30 d | PRIVATE |
| `OUT.doh_harvest_status` | NSSP / biotoxin / Vp **legal** status | PUBLIC official **link** |

### Confounder nodes

`CF.sampling_effort`, `CF.vessel_access`, `CF.season`, `CF.geography_basin`, `CF.depth`, `CF.observation_method`, `CF.regulation`, `CF.fishing_behavior`, `CF.climate_modes`, `CF.data_availability` — definitions in `confounder_catalog.md`.

---

## 2. Edges

Citations are **cited, not copied**. Access date 2026-09-18. `causal_use` default for all: `research_only` or `mechanism_note_only`; never a customer causal score.

### 2.1 Heating physics and the 2021 field path

**W1-E01** `ENV.astronomical_tide` → `HAB.emersion_duration`  
**Status:** `CAUSALLY_TESTED_RELATIONSHIP` · **ID class:** `PHYSICAL_IDENTITY`  
Given bed elevation, predicted tide determines aerial hours.  
**Citations:** NOAA CO-OPS https://tidesandcurrents.noaa.gov/  
**Horizon:** hourly · **Stage:** farm spat–market · **Culture:** intertidal / shallow  
**Confounders:** `CF.depth`, datums, local hydrodynamics  
**Data support:** `program_exists` (predictions)  
**Anti-claim:** Tide is not a toxin; moon independent of tide is not this edge.

**W1-E02** `HAB.culture_method_elevation` → `HAB.emersion_duration`  
**Status:** `CAUSALLY_TESTED_RELATIONSHIP` · **ID class:** `OPERATOR_INTERVENTION` / geometry  
**Citations:** NOAA Fisheries Pacific oyster https://www.fisheries.noaa.gov/species/pacific-oyster  
**Anti-claim:** Same estuary ≠ same exposure.

**W1-E03** `ENV.air_temperature` × `HAB.emersion_duration` × `ENV.solar_irradiance` → `PHYS.tissue_temperature`  
**Status:** `CAUSALLY_TESTED_RELATIONSHIP` · **ID class:** `LAB_EXPERIMENT` / biomimetic + shade manipulations  
Intertidal body temperature is a heat-budget problem (air + radiation + wave splash + morphology), **not** SST.  
**Citations:** Helmuth 1998 *Ecol. Monogr.* https://doi.org/10.1890/0012-9615(1998)068[0051:IMMPTB]2.0.CO;2 · Hesketh & Harley 2022/23 *Glob. Change Biol.* (topography / solar irradiance / shading during 2021 AHW; barnacles, same heat-budget class) https://doi.org/10.1111/gcb.16390  
**Confounders:** `CF.microhabitat`, `CF.depth`, wind  
**Data support:** `lab_only` + published biomimetics; lease loggers generally `none`  
**Anti-claim:** **Satellite SST is not body temperature.**

**W1-E04** lab protocol (≈30 °C water then ≈4 h aerial 44 °C) → `PHYS.delayed_mortality` (and ploidy modifier in-protocol)  
**Status:** `CAUSALLY_TESTED_RELATIONSHIP` · **ID class:** `LAB_EXPERIMENT`  
George et al.: sequential **water heat then aerial emersion** raised mortality vs control; triploids 36.4% vs diploids 14.8% at 30 days in the multi-stressor arm. **Water-heat alone is not that protocol.** Mortality scored to **day 30**, not hour 72.  
**Citations:** George et al. 2023 *Glob. Change Biol.* https://doi.org/10.1111/gcb.16880 · NOAA IR https://repository.library.noaa.gov/view/noaa/63100  
**Geography:** hatchery protocol inspired by 2021, **not** a WA lease identification  
**Anti-claim:** Not a bag-level % for Willapa; not an SST≥19 law.

**W1-E05** 26–28 Jun 2021 air heat dome × lowest daytime tides × solar → Salish intertidal shellfish mortality (Pacific oysters worse than Olympia; some deaths delayed)  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION` · **ID class:** `NATURAL_EXPERIMENT`  
Expert post-event ratings and community contrasts: Salish **afternoon** lows hit harder than Olympic Coast **morning** lows. This is the **template 72 h event**, still not Pearl identification at bag grain, still not SST.  
**Citations:** Raymond et al. 2022 *Ecology* https://doi.org/10.1002/ecy.3798 · Miner et al. 2025 *Front. Mar. Sci.* https://doi.org/10.3389/fmars.2025.1503019 · WA Sea Grant Rapid Response https://waseagrant.uw.edu/our-programs/seafood-fisheries-aquaculture/aquaculture/rapid-response-network/  
**Confounders:** culture method, species (*M. gigas* vs *O. lurida*), `CF.sampling_effort`, delayed death, microhabitat  
**Anti-claim:** Do not describe 2021 as a marine heatwave / SST kill. Do not treat expert PHWR maps as farm KPIs.

**W1-E06** `ENV.satellite_sst` → `PHYS.tissue_temperature` **during emersion**  
**Status:** `UNKNOWN` · **ID class:** `NONE`  
Mechanism fails: SST can be near-normal while tissue is lethal.  
**Citations:** Raymond et al. 2022 https://doi.org/10.1002/ecy.3798 · red-team RT-OYS-02  
**Anti-claim:** Any sentence that SST “caused the 2021 die-off.”

**W1-E07** `ENV.satellite_sst` → `HAB.water_column_heat` in **well-mixed shallows**  
**Status:** `OBSERVED_CORRELATION` · **ID class:** `OBSERVATIONAL_ADJUSTMENT` (proxy, not identity)  
**Citations:** NANOOS NVS Shellfish Growers https://nvs.nanoos.org/ShellfishGrowers  
**Predictive:** `proxy_only` · **Causal:** `not_identified`  
**Anti-claim:** SST is not DO, not air T, not abundance.

**W1-E08** water T or SST **≥ ~19 °C** → `OUT.farm_mortality_72h` **as a kill law**  
**Status:** `OBSERVED_CORRELATION` · **ID class:** `NONE`  
~19–20 °C appears in culture/spawn envelopes and as a **co-stressor** band (Cheney; NANOOS >64 °F / ~17.8 °C concern). FAO survival envelope is far wider. **This is not a kill law.**  
**Citations:** Cheney et al. 2000 *J. Shellfish Res.* 19:353–359 https://www.pacshell.org/publications.asp · FAO cultured species sheet https://www.fao.org/fishery/docs/CDrom/aquaculture/I1129m/file/en/en_pacificcuppedoyster.htm · NANOOS https://nvs.nanoos.org/ShellfishGrowers  
**Anti-claim:** “SST ≥ 19 °C (for 12 h) kills WA bags.” Binding correction vs quality B4 (`prediction_contract.md` §8).

**W1-E09** `ENV.satellite_sst` ↔ 2021 mortality geography  
**Status:** `OBSERVED_CORRELATION` · **ID class:** `NONE`  
Any spatial match is confounded by summer calendar and is the **wrong variable**. If SST-only “wins” a 2021 holdout against air×tide, **labels are wrong** (likely closures or water T).  
**Citations:** Raymond https://doi.org/10.1002/ecy.3798 · Miner https://doi.org/10.3389/fmars.2025.1503019

---

### 2.2 Water-column habitat, oxygen, salinity, turbidity

**W1-E10** `ENV.water_temperature_in_situ` → `PHYS.metabolic_spawn_condition`  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
Gametogenesis ~10 °C; spawning often cited ~18–22 °C. Metabolism rises with T. **Not 72 h death.**  
**Citations:** NOAA species page https://www.fisheries.noaa.gov/species/pacific-oyster · FAO fact sheet (URL above)

**W1-E11** low `HAB.dissolved_oxygen` → `PHYS.hypoxic_stress`  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION` · **ID class:** established bivalve physiology; **not** a WA 72 h SCM  
FAO culture minimum >2 mg L⁻¹ is a **floor**, not no-effect.  
**Citations:** FAO fact sheet · Cheney et al. 2000 https://www.pacshell.org/publications.asp

**W1-E12** elevated T × neap tides × oxygen-depleted water → Puget Sound **field** summer mortality  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION` · **ID class:** `NATURAL_EXPERIMENT` / observational multi-stressor  
**Citations:** Cheney, Macdonald & Elston 2000 *J. Shellfish Res.* 19:353–359 https://www.pacshell.org/publications.asp  
**Anti-claim:** One-variable heat map; Hood Canal copied onto Willapa.

**W1-E13** `HAB.stratification_flushing` (neap / basin) → `HAB.dissolved_oxygen`  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
**Citations:** Cheney 2000; WA Ecology marine WQ (Hood Canal hypoxia context, catalog only)

**W1-E14** `ENV.precipitation_discharge` → `HAB.salinity`  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
**Citations:** FAO euryhaline envelope; WA DOH growing-area hydrology is **not** the label https://doh.wa.gov/community-and-environment/shellfish/growing-areas

**W1-E15** acute low S + TSS + DO (flood pulse) → mortality **as multi-stressor**  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
**Anti-claim:** Salinity alone as the 72 h killer.

**W1-E16** `HAB.turbidity` → feeding interference / physiological strain  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
**Citations:** NANOOS turbidity sensors https://nvs.nanoos.org/ShellfishGrowers  
**Data support:** `sparse`

**W1-E17** emersion at culture elevation ↔ water-column hypoxia **tradeoff** (leave hypoxic water, take aerial heat)  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
This is the honest reading of `CF.DEPTH.PREFERRED_HYPOXIC` for oysters.

---

### 2.3 Food, currents, storms, culture, life history

**W1-E18** `BIO.phytoplankton_food` / `HAB.residence_time_currents` → growth / condition (**seasonal**, Willapa fattening-line contrast)  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
**Citations:** Lowe / Ruesink Willapa growth–food work PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC7809371/ (Banas et al. 2007 residence-time contrast therein)  
**Horizon:** weeks–season · **Anti-claim:** 72 h mortality engine.

**W1-E19** satellite chlorophyll-a → `OUT.lease_inventory` / abundance  
**Status:** `UNKNOWN`  
Stock is planted. Category E if sold as oysters.

**W1-E20** satellite chlorophyll-a ↔ growth/condition  
**Status:** `OBSERVED_CORRELATION`  
Pigment ≠ food quality; CDOM/turbidity contamination in estuaries.

**W1-E21** current **direction change** → `OUT.farm_mortality_72h`  
**Status:** `UNKNOWN`  
See E18 for seasonal growth. Sessile 72 h.

**W1-E22** prey / food **drop** → `OUT.farm_mortality_72h` (absent named HAB crash)  
**Status:** `UNKNOWN`

**W1-E23** `ENV.wind_waves` → `HAB.wave_loading` → `OUT.ops_gear_disruption`  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
Disruption, not physiology.  
**Citations:** WSG Rapid Response (storm/gear as grower concern) https://waseagrant.uw.edu/our-programs/seafood-fisheries-aquaculture/aquaculture/rapid-response-network/

**W1-E24** storms / wind → `OUT.ops_workability`  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
**Confounders:** `CF.vessel_access` (observation of workability). **Anti-claim:** weather-safety advice.

**W1-E25** `HAB.culture_method_elevation` → which stressor class dominates (aerial heat vs hypoxia vs HAB vs handling)  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
Pooled “WA oyster” model is a category error (RT-OYS-05).

**W1-E26** settlement → `OUT.sessile_no_72h_movement`  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
**Citations:** NOAA species page https://www.fisheries.noaa.gov/species/pacific-oyster

**W1-E27** ripe / post-spawn `PHYS.metabolic_spawn_condition` → elevated summer-mortality **vulnerability**  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
Degree-day / seasonal; not a 48 h spawn clock.  
**Citations:** NOAA/FAO; Wendling & Wegner 2013 (spawn state in lab) https://doi.org/10.1016/j.aquaculture.2013.07.009

**W1-E28** `PHYS.delayed_mortality` → mismatch with `OUT.farm_mortality_72h` labels  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
**Citations:** Raymond 2022 (deaths days–weeks later) https://doi.org/10.1002/ecy.3798 · George 2023 (day-30 scores) https://doi.org/10.1111/gcb.16880

**W1-E29** `CF.geography_basin` → which of heat vs DO vs runoff dominates  
**Status:** `ECOLOGICALLY_SUPPORTED_ASSOCIATION`  
Willapa (ocean-influenced, heat/food) ≠ Hood Canal (stratified hypoxia) ≠ South Sound.

**W1-E30** operator planting / culling → `OUT.lease_inventory`  
**Status:** `CAUSALLY_TESTED_RELATIONSHIP` · **ID class:** `OPERATOR_INTERVENTION`  
The farmer places the animals. This is why Category A “find the oysters” is the wrong product.

---

### 2.4 OA, disease, HABs

**W1-E31** `ENV.pH_omega` → `PHYS.larval_calcification`  
**Status:** `CAUSALLY_TESTED_RELATIONSHIP` · **ID class:** `LAB_EXPERIMENT` (saturation-state manipulations) with hatchery **correlative** context  
**Citations:** Waldbusser et al. 2015 *Nat. Clim. Change* https://doi.org/10.1038/nclimate2479 · Barton et al. 2012 *Limnol. Oceanogr.* (hatchery **correlation** with Ω; not a 72 h bag study) https://doi.org/10.4319/lo.2012.57.3.0698 · NOAA OAP https://oceanacidification.noaa.gov/  
**Stage:** **hatchery larvae** · **Anti-claim:** **OA is not a 72 h market-bag headline.**

**W1-E32** `ENV.pH_omega` → `OUT.farm_mortality_72h` (adult bags)  
**Status:** `UNKNOWN`  
Adult shells already formed. Featuring Ω as the farm headline repeats 2009 on the wrong stage.

**W1-E33** `BIO.oshv1` **when present** → mass farm mortality  
**Status:** `CAUSALLY_TESTED_RELATIONSHIP` · **ID class:** `LAB_EXPERIMENT` / epidemic documentation **in infected regions**  
**Geography:** CA / EU / Aus **≠ Washington 72 h**  
**Citations:** USDA-ARS PSBC / OSU MBP context https://marineresearch.oregonstate.edu/comes/molluscan-broodstock-programusda-ars-pacific-shellfish-breeding-center

**W1-E34** OsHV-1 as **established 72 h WA driver**  
**Status:** `UNKNOWN`  
Not detected at tested OR/WA sentinel sites in 2020.  
**Citations:** Dumbauld et al. 2023 *Dis. Aquat. Org.* https://doi.org/10.3354/dao03868  
**Anti-claim:** Import Mediterranean/Australian herpes timing into Willapa.

**W1-E35** `BIO.hab_animal_stress` (e.g. *Heterosigma*; *Protoceratium*/yessotoxins) → WA 72 h bag mortality  
**Status:** `EXPERT_HYPOTHESIS`  
WDFW 2019 compiled grower reports; disease not confirmed as the 2018 driver; mixed heat/DO/nutrition/HAB hypotheses. *Heterosigma* is more a **finfish** killer.  
**Citations:** WDFW 2019 note https://wdfw.medium.com/whats-been-causing-mass-shellfish-die-offs-around-puget-sound-1ada7071a242 · SoundToxins https://soundtoxins.org/about.html  
**Anti-claim:** HAB in region = harvest closure = dead oysters.

**W1-E36** `ENV.nutrients` → HAB at **72 h**  
**Status:** `EXPERT_HYPOTHESIS`  
Usually days–seasonal; indirect.

**W1-E37** *Vibrio* infection × thermal stress × reproductive state (lab) → mortality  
**Status:** `CAUSALLY_TESTED_RELATIONSHIP` · **ID class:** `LAB_EXPERIMENT`  
**Citations:** Wendling & Wegner 2013 *Aquaculture* https://doi.org/10.1016/j.aquaculture.2013.07.009  
**Geography:** experimental; **not** WA 72 h identification. Distinct from WAC 246-282-006 *V. parahaemolyticus* **harvest** controls.

**W1-E38** *Vibrio* as WA 72 h **field** driver  
**Status:** `EXPERT_HYPOTHESIS`

---

### 2.5 Handling, microhabitat, ploidy (field)

**W1-E39** handling / crowding after heat → extra mortality  
**Status:** `EXPERT_HYPOTHESIS`  
**Citations:** WDFW 2019 (ordinary handling failed during die-offs) https://wdfw.medium.com/whats-been-causing-mass-shellfish-die-offs-around-puget-sound-1ada7071a242  
**Confounders:** `CF.fishing_behavior` (the advice is the treatment).

**W1-E40** `HAB.intertidal_microclimate` residuals → `PHYS.tissue_temperature`  
**Status:** `EXPERT_HYPOTHESIS` at **lease grain** (principle sits in E03; unmapped per bag)

**W1-E41** triploid vs diploid → differential mortality **on WA farms in 72 h ops**  
**Status:** `EXPERT_HYPOTHESIS`  
Lab contrast is in **E04**; field WA not identified.

---

### 2.6 Regulation, labels, required confounder paths, anti-edges

**W1-E42** `OUT.doh_harvest_status` → `OUT.farm_mortality_72h` (closure as **causal mortality**)  
**Status:** `UNKNOWN` · **ID class:** `NONE`  
**WA DOH / NSSP / biotoxin / Vp control status is regulatory, not causal mortality in the ops model.** Public closures miss heat-kill when harvest stays legally open.  
**Citations:** WA DOH growing areas https://doh.wa.gov/community-and-environment/shellfish/growing-areas · `ground_truth_relabel_W1.md` · WAC 246-282-006 · RT-OYS-01/04  
**Observation method:** fecal coliform and tissue toxin tests ≠ gaping counts.

**W1-E43** `BIO.hab_human_toxin` / fecal indicators → `OUT.doh_harvest_status`  
**Status:** `OBSERVED_CORRELATION` · **ID class:** `POLICY_MAPPING`  
Designed administrative mapping with sampling lag. **Not physiology.**

**W1-E44** summer `CF.season` ↔ both heat-stress risk and DOH actions  
**Status:** `OBSERVED_CORRELATION`  
Confounding: calendar opens a back-door from closures to “stress.”

**W1-E45** `CF.sampling_effort` → recorded mortality / disruption  
**Status:** `OBSERVED_CORRELATION`

**W1-E46** `CF.vessel_access` → whether `OUT.ops_workability` is observed  
**Status:** `OBSERVED_CORRELATION`

**W1-E47** `CF.season` (month dummy) → observed stress/mortality **as climatology**  
**Status:** `OBSERVED_CORRELATION`  
Must be beaten by a mechanism, not shipped as AI.

**W1-E48** `CF.observation_method` → which \(Y\) is seen (visual vs logger vs DOH sample vs SST)  
**Status:** `OBSERVED_CORRELATION`

**W1-E49** `CF.climate_modes` → seasonal T/DO anomalies  
**Status:** `OBSERVED_CORRELATION` at 72 h (too slow to be the 2021 AHW mechanism)

**W1-E50** `CF.fishing_behavior` (harvest / handling) → observed inventory and apparent mortality (censoring)  
**Status:** `OBSERVED_CORRELATION`

**W1-E51** operator following an indicator (treatment) → later observed outcome  
**Status:** `OBSERVED_CORRELATION`  
Confounder for any future skill test.

**W1-E52** `CF.data_availability` (lease sensors vs SST-only) → whether E03 is **estimable**  
**Status:** `UNKNOWN` as biology (identification constraint, not a cause of death)

**W1-E53** MPA reduces fishing → 72 h bag survival / abundance  
**Status:** `UNKNOWN`  
Wrong system for planted sessile stock.

**W1-E54** AIS / vessel density → oyster abundance or stress  
**Status:** `UNKNOWN`  
Category error. Privacy.

**W1-E55** moon phase **independent of tide** → mortality  
**Status:** `UNKNOWN`  
Tide tables already capture the useful part.

**W1-E56** “preferred depth hypoxic” as a **WA-wide law** → mortality  
**Status:** `UNKNOWN`  
Use E11–E13 + E17 in a **named basin** instead.

---

## 3. Edge counts by causal status

| Status | Count | Edge IDs |
|---|---:|---|
| `CAUSALLY_TESTED_RELATIONSHIP` | **8** | E01, E02, E03, E04, E30, E31, E33, E37 |
| `ECOLOGICALLY_SUPPORTED_ASSOCIATION` | **17** | E05, E10, E11, E12, E13, E14, E15, E16, E17, E18, E23, E24, E25, E26, E27, E28, E29 |
| `OBSERVED_CORRELATION` | **13** | E07, E08, E09, E20, E43, E44, E45, E46, E47, E48, E49, E50, E51 |
| `EXPERT_HYPOTHESIS` | **6** | E35, E36, E38, E39, E40, E41 |
| `UNKNOWN` | **12** | E06, E19, E21, E22, E32, E34, E42, E52, E53, E54, E55, E56 |
| **Total** | **56** | E01–E56 |

**None** of the eight `CAUSALLY_TESTED_RELATIONSHIP` edges is a FishAI-fitted effect. Three of them are **off-scope for the 72 h WA bag headline** if misused: E31 (larvae/OA), E33 (OsHV-1 where present), E37 (lab *Vibrio*). E04 is lab delayed mortality, not a 72 h lease %.

---

## 4. Paths that are in-bounds vs forbidden to chain

**In-bounds mechanism note (still not a product causal score):**  
E01+E02+E03 → tissue T; E05 as field association for 2021-type days; E23/E24 for gear/workability; E11–E13+E17 for named-basin hypoxia.

**Forbidden chains:**

- E07/E08/E09 → death (SST kill law / 2021 as MHW)  
- E31 → E32 (larval OA to adult 72 h bags)  
- E33 → E34 (CA virus to WA 72 h)  
- E42/E43 as physiology  
- E19, E53, E54 as abundance  

Weakest-link rule: any path that includes E06 has path status `UNKNOWN`.
