# W1 oyster fixtures — classification drills (not alerts)

**Date:** 2026-09-18  
**Taxon:** *Magallana gigas* (Thunberg, 1793), AphiaID **836033** (synonym *Crassostrea gigas* 140656)  
**Product family:** `W1_OPS_STRESS` — 24–72 h Category **D** operational stress / workability on a **permissioned lease**.  
**These rows are not operational anomaly alerts.** `issued_as_operational_alert=false`, `story_eligible=false`.

Machine table: `fixture_events.csv`. Tree: `bias_vs_biology.md`. Contract: `artifacts/scientific_red_team/prediction_contract.md`.

---

## 0. What W1 is allowed to call an “anomaly”

On a named growing area / lease (PRIVATE KPIs):

| Allowed class | When |
|---|---|
| `POSSIBLE_MORTALITY_EVENT` | Protocol mortality or a **named** lethal pathway with the right variables |
| `POSSIBLE_HAB_EVENT` | Named **animal-stress** phytoplankton hypothesis — never NSSP authorization |
| `POSSIBLE_OBSERVATION_ARTIFACT` | Effort, SST-as-body-T, wrong basin, platform |
| `DATA_GAP` | No ops GT, or instruments in the wrong estuary |
| `NO_SIGNIFICANT_CHANGE` | After the tree, residual in climatology noise |

**Not W1 product classes:** `RANGE_SHIFT` (sessile planted stock at 72 h), public `AGGREGATION_EVENT`, `PHENOLOGY_SHIFT` as a harvest clock, Chinook/lobster research shifts.

**Hard walls:**

- Not food-safety; not “open/closed”; not *Vibrio*/PSP/DSP/ASP clearance.  
- Not a public aggregation or mortality choropleth.  
- Not SST-only.  
- Hood Canal ORCA is not Willapa.

Growing-area polygons frame the farm; they are **not** the label (`ground_truth_relabel_W1.md`).

---

## 1. FIX-CD-2021-001 — heat dome as `POSSIBLE_MORTALITY_EVENT` (air × tide, not SST-only)

**Historical process (literature, not an observatory measurement):** 26–28 June 2021 Pacific Northwest atmospheric heat dome coincided with the **lowest tides of the year**, producing mass intertidal mortality. Pacific oysters were more affected than lower-intertidal Olympia oysters; some deaths were **delayed days to weeks** (Raymond et al. 2022 *Ecology* https://doi.org/10.1002/ecy.3798; Washington Sea Grant Rapid Response Network).

**Tree path:** N1 coverage via published surveys + grower reports (still `observation_coverage=low` for any single lease) → N3 effort not a winter drop → N5 SST-only would **fail** → N6 **E-MORT** because the pathway is **air temperature overlapping daytime emersion**, matching B4 primary clause.

**Why not SST-only:** satellite skin temperature is not oyster tissue temperature and misses aerial exposure on emerged bags. Quality B4 forbids SST ≥ 19 °C for ≥12 h as a WA kill law (19 °C is a growth/clearance band). Hobday marine-heatwave flags (multi-day SST percentile) are the **wrong event class** for an **atmospheric** heatwave during midday emersion.

**Why `POSSIBLE_`:** this engine did not ingest farm counts; delayed mortality can fall **outside** a 72 h label window; microclimate (bag color, elevation cm, shade) is unobserved.

**Magnitude:** `elevated` vs typical June intertidal reports on the **published-event** comparison set — not a bag-level % as a FishAI number.

**Related env anomalies (EMIV):** `EMIV-PHY-ATEMP-001` (extreme air T); `EMIV-PHY-EMERS-001` (spring-tide daytime emersion); `EMIV-PHY-SOLAR-001` (midday insolation / solar geometry; not chlorophyll). Water T (`EMIV-PHY-WTEMP-001`) is supporting, not primary. Tissue/bag T is `EMIV-PHY-TISST-001` (CANDIDATE unless a partner thermistor exists). SST-only is `EMIV-PHY-SST-001` **PROXY**.

**Confidence:** `low` as a **product** score (no partner series in-repo; no calibration). Mechanism confidence in the literature is separate and must not be laundered into “High AI.”

**Privacy:** farm mortality `PRIVATE`. Geography in the CSV is a **fixture growing-area id**, not lease corners. Do not publish a 2021 kill map.

**Human review:** **required** before any user-facing story (`G-MORT`, `G-STORY`, `G-FOOD-WALL`).

**Recommended observation task:** `LEASE_MORTALITY_PROTOCOL_COUNT` + `INTERTIDAL_MICROCLIMATE_LOGGER` + `LEASE_WORKABILITY_LOG` on the **same** lease; `not_for_public_map=true`. Success: protocol counts with effort (bags inspected) and emersion-timed loggers — not a denser SST raster.

**What it does not mean:** harvest legality; food safety; % dead guarantee; other farms; Olympia oyster outcomes; that a 2026 brief is live.

---

## 2. HAB vs ops-stress (two fixtures)

### 2.1 FIX-CD-2019-002 — `POSSIBLE_HAB_EVENT` (animal stress, not a plate stamp)

**Historical process (tier 3 narrative):** WDFW compiled 2018–2019 grower reports of severe bag mortality in parts of Puget Sound (Discovery Bay / northern Whidbey Basin cited in public notes); Willapa bottom culture also reported hits. Hypotheses included heat, low oxygen, nutrition, and *Protoceratium*/yessotoxins; **disease not confirmed** in 2018 sampling (WDFW 2019 communication). SoundToxins exists to track HAB cells; some taxa can reduce feeding or stress animals (`variable_relevance_matrix.csv` `HAB_cells_animal_stress`).

**Tree path:** N6 **E-HAB** only if a **named** stress taxon is the hypothesis **and** NSSP harvest toxins are not used as *y*. Multi-stressor remainder stays in `confounders[]` (Cheney et al. 2000).

**Split (mandatory):**

| Stream | Engine | Authority |
|---|---|---|
| Animal-stress HAB (e.g. *Heterosigma*, high-biomass, yessotoxin producers as **grower-stress** hypotheses) | `POSSIBLE_HAB_EVENT` | Scientific review; still not a diagnosis |
| PSP/DSP/ASP / fecal coliform / Vp control | **Not an ops class** | WA DOH / NSSP — Module A link only |

**Recommended task:** `SOUNDTOXINS_ANIMAL_STRESS_TAXA` at the farm’s basin, plus `LEASE_MORTALITY_PROTOCOL_COUNT`. **Explicitly not:** impersonating a biotoxin tissue test or issuing “safe to harvest.”

**Privacy:** outbreak attributed to a named company is `NEVER_PUBLISH` / `PRIVATE`. Fixture geography is coarsened.

### 2.2 FIX-CD-2019-003 — official biotoxin/harvest status is not ops GT (`DATA_GAP` on ops *y*)

If the only observed “event” is a growing-area commercial closure or biotoxin status, the ops engine **does not** emit `POSSIBLE_HAB_EVENT` or `POSSIBLE_MORTALITY_EVENT`. Exit **E-AUTH**: `event_class=DATA_GAP` (partner mortality/workability unknown) with official status as **constraint text**, not the label.

This is the same correction as `artifacts/data_discovery/ground_truth_relabel_W1.md`.

---

## 3. FIX-CD-2026-004 — Willapa vs Hood Canal ORCA `DATA_GAP`

**Ask people will make:** “ORCA shows hypoxia in Hood Canal (Twanoh, Hoodsport, Dabob); flag Willapa oysters.”

**Engine:** `DATA_GAP` (exit **E-TRANSFER**).

| | Willapa (W1 recommended frame) | Hood Canal ORCA |
|---|---|---|
| Circulation | Ocean-influenced, relatively well mixed; heat/food/residence-time gradients | Stratified fjord; documented hypoxia |
| Instruments | Lease loggers / NANOOS growers **if** rights later allow — **not in-repo** | Ecology ORCA moorings at Hood Canal sites |
| 72 h mechanism mix | Air × emersion, waves, local T/S; DO **only if local** | DO can be first-order **there** |
| Transfer | **Forbidden** as Willapa *y* or as Willapa DO covariate without a documented mismatch budget | Valid for a **Hood Canal** research cell, not this fixture’s Willapa claim |

Marine domain: pooling Willapa and Hood Canal without site ID misspecifies a 72 h model (`model_limitations.md`).

**Recommended task:** `IN_SITU_DO_AT_CULTURE_DEPTH` **in Willapa** (or declare DO `known_missing_inputs` and keep confidence **low/none`). Not “ingest more Hood Canal.” `COVERAGE_STATION_GAP_FILL` if the gap is empty Willapa sensors.

**As-of:** 2026-09-18. Still no bulk ingest. This fixture is a **coverage truth**, not a hypoxia alert.

---

## 4. Other W1 drills in the CSV

| ID | Class | Point |
|---|---|---|
| FIX-CD-FIXT-005 | `POSSIBLE_OBSERVATION_ARTIFACT` | Winter drop in farm-walks / public mentions ≠ planted-stock decline (**E-EFFORT-DROP**) |
| FIX-CD-FIXT-006 | `POSSIBLE_OBSERVATION_ARTIFACT` | SST-only warm pixel without daytime emersion overlap (**E-PROXY**) |
| FIX-CD-FIXT-007 | `NO_SIGNIFICANT_CHANGE` | Typical June tides, B4 quiet, coverage adequate **in the hypothetical**; still fixture, not a green light to harvest |

Research-only rows (`RANGE_SHIFT`, `DEPTH_SHIFT`, `PHENOLOGY_SHIFT`, `AGGREGATION_EVENT`, `DISPERSAL_EVENT`) sit in the same CSV so the closed class set is exercised, with `product_claim_family=OBSERVATORY_RESEARCH_NOT_W1` or `SUPPRESSED_PRIVACY`. They are **not** W1 briefs.

---

## 5. Copy that must never ship from these fixtures

- “Safe to eat / legal to harvest / meets NSSP.”  
- “ORCA confirms Willapa mortality.”  
- “SST shows a kill event.”  
- “Oyster abundance is down.”  
- “New aggregation at [lat, lon] — go see.”  
- Any sentence a reasonable operator could read as a **2026 live alert**.

Approved direction (if a human later promotes a **non-fixture** W1 brief): prediction-contract oyster paragraph — **operational stress indicator**, air × emersion, Category D, **not food-safety**.
