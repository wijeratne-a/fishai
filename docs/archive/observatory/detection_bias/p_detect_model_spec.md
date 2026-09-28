# Hierarchical occupancy and \(p(\mathrm{detect})\) model specification

**Date:** 2026-09-18  
**Status:** Design. **Do not fit. Do not train. Do not ingest.**  
**As-of clock:** all features and labels must satisfy `published_at_utc ≤ issued_at_utc` (see `/Users/wijeratne/dev/fishai/artifacts/geospatial_data_engineer/as_of_replay_design.md`).  
**Ceiling:** occupancy is Category **D** (relative use / encounter / occupancy probability). It is **not** abundance \(N\), not a census, not harvest legality.

Literature anchors (cite, do not copy): MacKenzie et al. 2002 *Ecology*; MacKenzie et al. 2018 occupancy book; Kéry & Royle *Applied Hierarchical Modeling*; Guillera-Arroita 2017; Lahoz-Monfort, Guillera-Arroita & Wintle 2014 (separating occupancy and detectability); Barker et al. 2018 and Link et al. 2018 (N-mixture identifiability — **do not** treat N-mixture as a stealth census).

Companion: `../ocean_model_comparison.md` §2.3–2.4.

---

## 1. Scientific object

For site (or cell) \(i\) in time window \(t\), method-visit \(j\):

\[
\begin{aligned}
z_{it} &\sim \mathrm{Bernoulli}(\psi_{it}) \\
y_{ijt} \mid z_{it} &\sim \mathrm{Bernoulli}(z_{it}\, p_{ijt})
\end{aligned}
\]

- \(z_{it} \in \{0,1\}\) is **latent occupancy** (used / present at the grain).  
- \(y_{ijt} \in \{0,1\}\) is the **detection trial** (`PRESENT_OBSERVED` vs `NOT_DETECTED` only).  
- \(\psi_{it} = \Pr(z_{it}=1)\) occupancy / use.  
- \(p_{ijt} = \Pr(y_{ijt}=1 \mid z_{it}=1)\) detection given presence.

**Required functional form (conceptual):**

\[
p_{ijt} = f(\underbrace{\text{method},\ \text{effort},\ \text{species},\ \text{life stage},\ \text{depth},\ \text{water clarity},\ \text{weather},\ \text{sensor quality},\ \text{observer skill},\ \text{habitat},\ \text{time of day},\ \text{season},\ \text{behavior}}_{W_{ijt}})
\]

Default link (when a model is ever fitted): \(\mathrm{logit}(p_{ijt}) = W_{ijt}\alpha\), \(\mathrm{logit}(\psi_{it}) = X_{it}\beta\), with hierarchical intercepts for **platform**, **crew/farm**, and **survey program**. Alternatives (complementary log-log for rare detections; Royle–Nichols if counts exist) must be **pre-registered** and still do not emit \(N\) without a designed census.

**W1 special case.** On an active lease, \(\psi\) for **planted** Pacific oysters is **operationally 1** until harvest/fallow is logged. The interesting process is **not** wild occupancy. It is detectability of **mortality / stress signs** and workability. Do not run a wild SDM on farm bags.

---

## 2. What is knowable today (2026-09-18)

| Item | Status |
| --- | --- |
| Algebra of \(\psi\) vs \(p\) | **Known.** Textbook. |
| Which methods have published detection functions | **Partially known** (marine-mammal line transect; some BRUV; some eDNA LOD; fisheries acoustic TS). See `method_bias_cards.md`. |
| FishAI-calibrated \(\alpha, \beta\) | **Unknown. Not fitted.** |
| Global \(p\) surface | **Impossible** at claimed grain (`../physics_feasibility_reports/physical_limits.md`). |
| Whether GBIF/OBIS support \(\psi\) | **No**, not without an effort / detection process. |
| Numeric GO thresholds for occupancy skill | **Hypotheses only** (`../validation_protocol.md`). |

Print \(p\) only as **qualitative** (`very low / low / medium / high / unknown`) until a human accepts a **prospective** reliability diagram. Three-decimal biological probabilities are out of contract (`../user_output_contract.md` §4).

---

## 3. Observation-state → likelihood

Reuse `observation_state_enum.md` §4. Short form:

- Include in \(y\): `PRESENT_OBSERVED` (\(y=1\)), `NOT_DETECTED` (\(y=0\)).  
- Exclude from \(y\): `NO_OBSERVATION`, `DATA_UNAVAILABLE`, `PRESENT_INFERRED`.  
- `TRUE_ABSENCE_SUPPORTED` is a **derived** \(\hat{z}\approx 0\), produced after fitting \(p\) on repeated visits — never a raw downloaded zero.

If effort is missing, the row **cannot** enter \(p\). Store as `effort_unknown` and drop from the likelihood (or use an explicit missing-effort submodel — **not** v0).

---

## 4. Hierarchical structure (when fitting is ever allowed)

**v0 (not this iteration):** do not fit. Expert qualitative \(p\) ranks by method only.

**v1 (after Gate 1–4 + designed repeats):**

```text
p_detect ~ method family
         + log(effort)
         + species / guild intercept
         + life_stage
         + depth_band
         + water_clarity (Kd, turbidity, or class)
         + sea_state / wind / rain_noise
         + sensor_quality (cal age, fouling, SNR)
         + observer_or_crew_id (partial pool)
         + habitat_class
         + hour_of_day + season
         + behavior_availability (if measured)
         + (1 | survey_program) + (1 | platform)
```

```text
logit(ψ) ~ habitat / env **at the animal’s depth**
         + effort_null (distance-to-port, depth-of-station, ship-days)  # RT-OBS-03
         + management mask (open/closed) as a **constraint**, not biology
         + (1 | basin) + (1 | year)
```

**Partial pooling is mandatory** across farms/vessels so one high-liner or one tidy grower does not become “the ocean.”

**Forbidden in \(\psi\) as if they were occupancy:** SST-as-abundance, AIS density, chlorophyll-as-fish, DOH growing-area class, vessel heatmaps.

**Allowed in \(\psi\) as habitat covariates** (labeled as such): temperature **at depth**, oxygen, substrate, salinity — with mismatch flags (SST ≠ bottom T ≠ intertidal body T).

**Allowed in \(p\) as detectability covariates:** the \(W\) list above. Temperature may enter \(p\) when it changes **catchability** (lobster; McLeese & Wilder 1958 and ASMFC 2025 catchability blocks). Then the output is **catchability-aware occupancy or CPUE**, never \(N\).

---

## 5. Feature dictionary

Every feature carries: `role` ∈ {`occupancy`, `detection`, `constraint`, `forbidden_as_y`, `effort_null`}, `as_of_field`, `depth_validity`, `known_today`.

### 5.1 Detection design matrix \(W\) (required arguments of \(f\))

| Feature | Role in \(p\) | Knowable today | Leakage / mismatch traps |
| --- | --- | --- | --- |
| **method** | Family intercept (visual, camera, active acoustic, PAM, eDNA, tag, catch, citizen, satellite, farm walk) | Family ranks: qualitative **High** | Mixing methods without intercepts |
| **effort** | Duration, area, volume filtered, angler-hours, trap-hauls, number of bags walked, ping-km | Must be in the protocol; often missing in occurrence DBs | Missing effort → drop row; do not impute 1 |
| **species** | Size, crypsis, TS, vocalization, shedding, coloration | Guild-level literature | Transfer across taxa forbidden without test |
| **life stage** | Larva vs adult vs seed vs legal-size | Required partition (`species_model_factory.md` Step 1) | Juvenile chl papers ≠ adult Chinook \(p\) |
| **depth** | Optical path, acoustic dead zone, camera range, trap on bottom | Bins from architecture agent; SST is skin | Surface \(p\) ≠ midwater occupancy |
| **water clarity** | \(K_d(490)\), turbidity, CDOM, bubbles | VIIRS/OLCI **optics** products exist; coastal Case-2 error | Using chl as if it were fish; using Kd as occupancy |
| **weather** | Sea state, glare, wind, rain (PAM mask), small-craft go/no-go | Forecasts exist; as-of NWP | Weather that **cancels the trip** removes the trial (→ `NO_OBSERVATION`), it does not create \(y=0\) |
| **sensor quality** | Cal date, fouling, gain, primer/LOD, bit depth, biofouling | Often **UNKNOWN** | Fouled DO as oyster death; uncalibrated EK as \(N\) |
| **observer skill** | Crew, ID expert, charter captain, grower protocol | Partner metadata; not public | Captain skill ≠ biomass |
| **habitat** | Complexity, rugosity, canopy, gear type, culture method | Static maps + farm metadata | Habitat suitability ≠ \(p\) and ≠ current \(z\) |
| **time of day** | Light, diel vertical migration, calling, farm tide clock | Clock is free | Night satellite optical = `NO_OBSERVATION` for imagery |
| **season** | Calling, molt, spawn, tourism (citizen effort), survey windows | Calendar + program docs | Seasonal **availability** vs seasonal **occupancy** |
| **behavior** | Avoidance, bait response, surfacing, emersion, feeding | Rarely measured | BRUV \(p\) inflated by bait; vessel avoidance lowers acoustic \(p\) |

### 5.2 Occupancy design matrix \(X\) (not \(p\))

Habitat and use drivers with a **stated mechanism** (factory Step 3). Always include an **effort-null** path (distance-to-port, coast distance, station depth, program funding era) so the model can fail RT-OBS-03: if removing biology does not hurt skill, stop occupancy maps.

### 5.3 Constraints (not biology)

Open/closed salmon water, NSSP harvest status, ALWTRP gear rules, private/NEVER_PUBLISH masks. These **zero the user-facing score** or hide the cell. They do **not** enter as \(y\).

---

## 6. Leakage rules (BLOCKER if violated)

Aligned with `observatory_red_team_01.md` RT-OBS-01…07 and FishAI validation protocol.

| ID | Rule |
| --- | --- |
| L1 | **As-of.** Every column in \(X\) and \(W\) has `published_at_utc ≤ issued_at_utc`. Delayed-mode SST/chl, revised landings, post-pop-up PSAT decode, eDNA batches returned weeks later **cannot** be used as if they were live. Research lane `retrospective_corrected` is not a product metric. |
| L2 | **No future surveys in train.** Year-block. Do not random-split adjacent H3 cells. Spatial blocking at residual SAC scale. |
| L3 | **No using \(y\) to build \(X\).** Habitat rasters must not be scored against themselves. Occupancy labels from cameras cannot include the same frames used as “habitat texture” without a held-out set. |
| L4 | **No occurrence-only zeros.** Querying GBIF/OBIS for “no record in cell” is **not** \(y=0\). State = `NO_OBSERVATION`. |
| L5 | **No unvisited = absent.** Unfished Chinook cells, un-hauled lobster TMS, un-walked farm-days are `NO_OBSERVATION`. |
| L6 | **No AIS / VMS / GFW as \(y\) or as \(N\).** Optional effort diagnostic only, labeled traffic, and **illegal** for typical inshore lobster (carriage). |
| L7 | **No DOH/NSSP closure as oyster \(y\).** Constraint layer. |
| L8 | **No circular sensors.** W1: in situ T/DO may be \(X\); mortality/workability logs are \(y\). Do not threshold the sensor and call it the label (Quality RT circularity). |
| L9 | **No test-year management indices** published after the fact (PFMC preseason as if known in April of a past year without checking publication time). |
| L10 | **No N-mixture census** on unstructured citizen data (Barker 2018). |
| L11 | **Coordinates + month dummies** must lose to, or be reported vs, a B12 seasonal-spatial baseline. Memorizing ports is not occupancy. |
| L12 | **Presence-inferred rows are not labels.** |

---

## 7. Identifiability and design requirements

Occupancy \(p\) and \(\psi\) are **not identifiable** from single-visit presence-only data (MacKenzie 2002; Lahoz-Monfort et al. 2014).

**Minimum design to estimate \(p\):**

- Repeated visits within a closure window, **or**  
- Multiple independent methods on the same visit (camera + eDNA; walk + count), **or**  
- Distance / time-to-detection / count structure with **stated** parametric assumptions (and a red-team of those assumptions).

**If the design is single-visit occurrence-only:** do **not** claim occupancy. Emit T1 historical occurrence or T2 suitability. State remaining `PRESENT_OBSERVED` / `NO_OBSERVATION` only.

**Pseudo-absence** is not a substitute for repeats. Rules in `training_policy.md`.

---

## 8. Evaluation (when a fit exists)

Reuse observatory validation V1–V9 and FishAI blocked CV.

Occupancy-specific tests:

| Test | Pass idea (hypothesis) | Fail |
| --- | --- | --- |
| Effort-null | Biology covariates improve skill vs distance-to-port only | RT-OBS-03: sampling model |
| Independent method | Camera occupancy predicts eDNA or vice versa on held-out stations | Same-sensor circularity |
| Non-detect calibration | Predicted \(p\) matches repeat-visit detection frequencies | Overconfident zeros |
| Extreme year | 2021 AHW (oyster) / closed salmon year held out | Climate theater |
| Baseline | Beat month × place occurrence climatology (B12-class) | NOT READY FOR USE |

**Do not** use AUC on GBIF with random background as a GO metric.

---

## 9. As-of snapshot contents (occupancy issuance)

When (later) an occupancy or \(p\) layer is issued, persist:

- `issued_at_utc`, `source_data_cutoff_utc`, `training_data_cutoff_utc`  
- Feature parquet with per-source `published_at`  
- `known_missing_inputs` (clarity, cal, effort, …)  
- Observation-state counts per cell (`n_present_observed`, `n_not_detected`, `n_no_observation`, …)  
- `unknown_flag` if \(n\) trials = 0  
- `model_or_baseline_version` or `none — qualitative method card`  
- Privacy tier after coarsening  

**Never UPDATE** an issuance; supersede (`as_of_replay_design.md` §2).

---

## 10. Relationship to commercial wedges

| Wedge | \(\psi\) | \(p\) | Honest product object |
| --- | --- | --- | --- |
| W1 oyster | ≈ 1 on planted gear; 0 if logged fallow (`TRUE_ABSENCE_SUPPORTED` possible) | Detect **gaper / gap / heat-kill / workability**, not wild set | Category D **ops-stress**, not occupancy map |
| W2 Chinook | Use of open water at depth band | Charter encounter given trip + gear + skill + weather | Category D encounter; evaluate C on **visited** cells |
| W3 lobster | Benthic use at depth/substrate | Trap catchability (T, molt, bait, soak, saturation) | Category C CPUE; **not** \(\psi\) as \(N\) |

---

## 11. Implementation freeze

Until founder lock + rights + designed labels:

- No Stan/TMB/unmarked/ubms/Maxent/SDM run.  
- No downloading occurrence tables “to try occupancy.”  
- Qualitative method cards and fixtures only.

This spec is **APPROVED_AS_DESIGN**, not **APPROVED_FOR_TRAINING**.
