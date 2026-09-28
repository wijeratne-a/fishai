# Data assimilation design — Global Saltwater Life Observatory

**Agents:** DATA_ASSIMILATION_AND_DIGITAL_TWIN_AGENT · OCEAN_DATA_ARCHITECTURE_AGENT · SPATIOTEMPORAL_MODELING_AGENT · ECOSYSTEM_AND_FOOD_WEB_MODELING_AGENT  
**Date:** 2026-09-18  
**Status:** Design only. No DA code. No training. No bulk ingest.  
**Companion:** `global_digital_twin_architecture.md`, `ocean_model_comparison.md`.

Assimilation here means: **update a declared state with new observations under an explicit observation operator, without rewriting history, and without pretending sparse data are a dense posterior.**

It does **not** mean running a global ocean GCM, nor converting eDNA, tags, acoustics, or CPUE into abundance by default.

---

## 1. Twin equation (operational)

At issuance time \(t_i\), with cutoff \(t_c \le t_i\):

\[
x_{t_i} \mid y_{\le t_c},\, m,\, \pi \;=\; \mathrm{DA}\big(\pi,\; y^{\mathrm{hist}}_{\le t_c},\; e_{t_c},\; y^{\mathrm{new}}_{\le t_c},\; \Phi,\; \beta,\; H,\; Q,\; R\big)
\]

| Symbol | Meaning | v0 |
|---|---|---|
| \(x\) | Declared state (Category A–E named) | Oyster 72 h stress + workability + env |
| \(\pi\) | Ecology prior (Layer 4) | Dossier: heat×emersion, DO, culture method |
| \(y^{\mathrm{hist}}\) | Historical obs with `published_at ≤ t_c` | Partner outcomes if DUA; else empty |
| \(e_{t_c}\) | Env/habitat state | Tide, air, water T, waves (licensed) |
| \(y^{\mathrm{new}}\) | New obs | Same as-of rule |
| \(\Phi\) | Ocean physics | **Not a GCM.** Tide tables + NWP + optional in-situ |
| \(\beta\) | Movement / physiology | Sessile adults; culture metadata |
| \(H\) | Observation operator | Expert-rule thresholds; later GLM |
| \(Q,R\) | Process / observation noise | Not estimated in v0; confidence is a **rule** |
| \(m\) | Model version + code hash | B4/B12 identifiers |

**As-of invariant:** only rows with `published_at_utc ≤ source_data_cutoff_utc` and `ingested_at_utc ≤ cutoff` (v1 strict) enter DA. Issued \(x\) is append-only. See geospatial `as_of_replay_design.md`.

**Privacy invariant:** PRIVATE GPS never enters \(H(x)\) explanations or PUBLIC API bodies.

---

## 2. Observation operators (the actual science)

DA quality is dominated by \(H\), not by the Kalman gain fashion.

### 2.1 Surveys (fishery-independent)

- **Design-based index:** \(y = H(x) + \varepsilon\), \(H\) = stratum mean of catchability-adjusted counts. Category **B**.  
- **Spatiotemporal index (VAST / sdmTMB):** \(y(s,t)\) with spatial random fields (Thorson 2019 *J. Fish Biol.* https://doi.org/10.1111/jfb.13948; Anderson et al. sdmTMB). Still an **index**, not N.  
- **Horizon:** seasonal to annual. **Not** a 24–72 h operator product.

Lobster VTS / NEFSC trawl / CalCOFI belong here as **later survey context**. They do not mint observatory T3 (current spatial condition) until a factory run is validated at the claimed grain. Not v0.

### 2.2 Catch and effort (fishery-dependent)

\[
\mathbb{E}[\mathrm{CPUE}] = q(T_{\mathrm{bottom}}, \mathrm{molt}, \mathrm{soak}, \mathrm{bait}, \mathrm{gear}) \cdot N_{\mathrm{legal}} \cdot s(\mathrm{regs})
\]

\(q\) and \(N\) are not separately identified from CPUE alone (Harley, Myers & Dunn 2001 *CJFAS* https://doi.org/10.1139/f01-137; lobster hyperstability — ASMFC 2025 peer review).  

**Honest DA:** estimate **CPUE** (Category C) or a rank, with \(q\)-drivers as covariates. **Dishonest DA:** treat AIS density or SST as \(N\).

### 2.3 Tags vs population

- State-space movement models estimate **an individual’s** path (Jonsen, Flemming & Myers 2005 *Ecology* 86:2874–2880; Johnson et al. 2008 CTCRW).  
- \(n_{\mathrm{tags}} \not\Rightarrow N\). Scaling requires a design (mark–recapture, telemetry + survey).  
- Archival tags can update **habitat envelopes** (Chinook 8–12 °C, Hinke et al. 2005) as Layer 4/5 priors. They must not emit listed-ESU public tracks.

**v0:** no tag DA. **Later:** published tag papers may update **T2 habitat kernels**; ingested tracks would be observatory **T5 observations** (individual ≠ population). Never public fine mammal tracks.

### 2.4 Acoustics

- **Active fisheries acoustics:** NASC → biomass needs \(TS(L)\), species mix, and survey design (Simmonds & MacLennan). Category B index if those are documented; Category E if a pretty echogram is sold as fish.  
- **PAM:** detection ≠ count; real-time whale positions are `NEVER_PUBLISH`.

**v0:** no acoustic DA.

### 2.5 eDNA + currents

Forward problem (relatively mature):

\[
\frac{\partial C}{\partial t} + \mathbf{u}\cdot\nabla C = \nabla\cdot(K\nabla C) - \lambda C + S(x_{\mathrm{animals}})
\]

Lagrangian equivalent: particles with decay \(\lambda\) (Andruszkiewicz et al. 2019 *Sci. Rep.* https://doi.org/10.1038/s41598-019-40788-z; Harrison, Sunday & Rogers 2019 *Proc. R. Soc. B* https://doi.org/10.1098/rspb.2019.1409). Tools: OceanParcels (Delandmeter & van Sebille 2019 *Geosci. Model Dev.*).

Inverse problem (what the twin would need): \(S \rightarrow x_{\mathrm{animals}}\) is **severely underdetermined** (shedding, decay \(\lambda(T)\), dilution, non-unique source locations, PCR detection). eDNA is evidence of **DNA transport**, Category D/E unless a local calibration of shedding and \(\lambda\) exists.

**v0:** do not assimilate eDNA. **Later:** particle filter on \(C\) in **one estuary**, emitting a **tracer posterior** and a presence-risk, not N. Never a harvest-toxin product.

### 2.6 Farm sensors and outcomes (v0-relevant)

- Sensors: \(H\) is near-identity for water T, DO, S at the sonde — **not** for bag microclimate or aerial tissue T.  
- Outcomes: binary disruption / workability; delayed mortality can fall **outside** the 72 h window (George et al. delayed oyster mortality after heat). \(H\) must allow lag or the label is misspecified.

### 2.7 Occupancy and N-mixture

Occupancy: \(y \sim \mathrm{Bernoulli}(p \cdot \psi)\) (MacKenzie et al. 2002 *Ecology*). Useful for detection-nondetection grids as T2 research or T3 **if** current-condition validation exists.  
N-mixture (Royle 2004 *Biometrics*): counts with imperfect detection; **identifiability is fragile** (Barker et al. 2018 *J. Appl. Ecol.*; Kéry 2018). Do not use as a stealth census on unstructured OBIS counts.

---

## 3. Assimilation methods — when each is honest

Detailed literature comparison lives in `ocean_model_comparison.md`. Operational assignment:

| Method | Honest use in this observatory | v0 | Later |
|---|---|---|---|
| **None / open-loop expert rule** | Physics thresholds + climatology | **Yes — default** | Always remain as baseline |
| **Hierarchical Bayes (static intercepts)** | Farm/vessel partial pooling (Gelman; Thorson mixed-effects) | Optional when n≥3 partners | Supports T3/T4 **after** validation; not a tier by itself |
| **INLA / sdmTMB / VAST** | Survey-index fields, seasonal | No | Candidate engine for T3 indices |
| **EnKF** (Evensen 1994) | Near-Gaussian physics or BGC tracers on a **named regional model** we do not currently run | No | Physics/BGC **covariates** (H-4.4); animals not the state. Observatory T6 only if operational gates pass |
| **4D-Var / VI** | Operational ocean DA (NEMOVAR, NCODA) — **consume products**, do not reimplement | Consume licensed analysis as \(e_t\) | Same |
| **Particle filter / SMC** | Non-Gaussian tracers (eDNA, HAB cells), individual movement | No | Tracer nowcast/forecast research; eDNA **hits** are T5 of DNA, not of N |
| **Occupancy / IPM** | Detection grids; integrated demography at year scale (Schaub & Abadi 2011) | No | T3 only at validated grain; IPMs are year-scale, not 72 h |
| **ABM/IBM** | Mechanism exploration (larvae) | No | Research, not issuance engine |
| **Food-web (EwE, Atlantis)** | Strategic what-if, not DA | No | Layer 4 |
| **ML residual on mechanism** | Only after B4/B12 beaten prospectively | No | Gate 5 in quality spec |

**Do not implement EnKF, PF, or 4D-Var in v0.** There is no running ocean model, no observation-error covariance we can estimate, and no right to global fields.

---

## 4. v0 assimilation procedure (oyster stress twin)

### 4.1 State vector

For each `official_unit_id` (DOH growing area) and, if DUA allows, each `lease_id_internal`:

```text
x = {
  stress_indicator,          # Category D rank or P(event) if calibrated later
  workability_indicator,     # tide × wind/wave
  env: {air_T, emersion_h, water_T, DO?, S?, Hs, wind},
  observation_density,
  known_missing_inputs[],
  confidence_category
}
```

Dimension: O(10) per site, not O(H3_global × z).

### 4.2 Algorithm (open-loop + rules)

1. Lock `source_data_cutoff_utc`.  
2. Assemble env from as-of tides (CO-OPS), air/water/wave forecasts **if rights-approved**, else in-situ + `SOURCE_OUTAGE_FALLBACK`.  
3. Compute B4 expert-rule (`baseline_model_spec.md` §4) — **hypothesis thresholds**, not WA law.  
4. Compute B12 seasonal-spatial event rate if any historical **farm** labels exist; else omit (do not borrow DOH closures as labels).  
5. Combine with **worse-wins** confidence rule (`uncertainty_policy.md`). SST-only → Low/None.  
6. Attach official DOH status as a **separate non-model module**.  
7. Issue L7; store L2 snapshot. **No Kalman update.** Observatory `support_tier` for this issuance: **T2** / `HYPOTHETICAL/RESEARCH MODE` until time-forward tests exist (then T4 for this AOI×target only).

If n≥3 farms with comparable culture method: a **hierarchical intercept** (farm random effect, Gaussian prior, fitted **offline** on as-of labels, not sequentially) may shrink B12. That is Bayes as **partial pooling**, not sequential DA.

### 4.3 What would count as “assimilation” later on this slice

- Bayesian updating of farm intercepts on a weekly batch using L10 forms (`published_at ≤ cutoff`).  
- Optional: simple Beta-Binomial on event rate.  
- Still not EnKF.

---

## 5. Later slices — DA playbooks (not scheduled)

### 5.1 Lobster next-trip CPUE (commercial Category C; observatory T4 only after tests)

- State: legal CPUE (or tercile) on operator’s own footprint × depth band.  
- \(H\): log CPUE ~ bottom T + molt prior + soak + vessel intercept.  
- DA: hierarchical GAM or sdmTMB on **partner + lawful** effort data; temperature-dependent \(q\) as a **named assumption**.  
- Physics: do **not** run FVCOM; consume eMOLT-class or licensed bottom-T analysis (ASMFC 2025: satellite SST inadequate).  
- Filter: none sequential at trip scale unless a residual AR(1) is validated against persistence baseline B3.

### 5.2 Chinook encounter (Category D; open areas only; T2 habitat until validated T4)

- State: relative encounter rank, not N.  
- Hard mask: closed → `confidence=none`.  
- Physics: 3D T to place 8–12 °C band; if only SST, do not issue.  
- Tags: literature kernels as priors, not live tracks.  
- DA: shrinkage of cell-month CPUE (B12) + weather as catchability/effort confounder. No EnKF.

### 5.3 HAB / eDNA tracer (research; separate from oyster food-safety)

- State: \(C(s,z,t)\) or particle weights; optional occupancy of a **named** phyto taxon.  
- Forward: licensed regional current subset + decay.  
- DA: **particle filter** (positivity, multimodality). EnKF only if log-transform + inflation is documented.  
- Output: Category D transport/presence risk. eDNA positives are observatory **T5 of DNA**, not of cell counts. **Never** toxin or harvest authorization.  
- Do not mix this state into the oyster stress brief.

### 5.4 Acoustics + survey (Category B index; T3 only if current-condition validation exists)

- State: acoustic biomass index on survey domain.  
- DA: design-based or VAST; species-mix prior from trawls.  
- Not a 72 h product.

### 5.5 Coupled physical–biological / food-web

- Consume CMEMS-class BGC **as habitat covariates** if licensed and skill-checked against chlorophyll **as chlorophyll**.  
- Do not invert NPZD into fish.  
- EwE/Atlantis: scenario tools for management-scale questions; no sequential DA into v0.

### 5.6 Causal identification

Where possible, draw a DAG: e.g. bottom T → catchability → CPUE ← N; effort → CPUE; SST ↛ N. DA that conditions on colliders or treats \(q\)-drivers as N is rejected (see `ocean_model_comparison.md` causal row). This is **assumption documentation**, not a claim we can run Pearl-style identification on the ocean.

---

## 6. Sequential vs batch vs climatology

| Mode | Clock | Use |
|---|---|---|
| Climatology (B12) | Month × place | Always on; relevant baseline |
| Batch Bayesian | After a season / week of L10 | v0+ pooling |
| Sequential DA | Every new obs | Only when a real \(\Phi\) and \(H\) exist; still cannot exceed the taxon’s support tier |
| Smoother | Retrospective using future y | `retrospective_corrected` lane **only** |

Issuing a smoother as if it were a nowcast is a red-team blocker (temporal leakage).

---

## 7. Uncertainty during DA

- Process noise \(Q\) and observation noise \(R\) are **not** free knobs to make maps look sharp. If they are not estimated from residuals or a published instrument model, do not print a numeric interval (`uncertainty_rationale` instead).  
- Particle degeneracy, EnKF underdispersion, and VI mode-seeking **all manufacture confidence**. Mitigation: coverage tests on the honest eval lane; if an “80%” interval misses the 0.70–0.90 band, drop to Low and stop printing it (`uncertainty_policy.md` §3).  
- **Empty cell rule:** no posterior mean. Return `data_support=none`. Spatial smoother length-scales, if ever used, must be estimated inside training years and must not fill across official-unit or privacy boundaries.

---

## 8. Computational posture

v0: Python on a laptop; cron; DuckDB; no DA library required.  
Later PF/EnKF: only inside one AOI, one tracer, one licensed current product, offline jobs. Not a 24×7 ocean forecast center.

Do not wrap an unlicensed global reanalysis in an EnKF and call it the observatory.

---

## 9. What not to assimilate

- AIS/VMS/GFW as \(y\) for abundance  
- Social reports as \(y\) (evidence T4_unverified)  
- DOH closures as oyster-stress \(y\)  
- Juvenile survey indices as adult Chinook 48 h \(y\)  
- Satellite SST as lobster bottom T or oyster tissue T  
- Protected-species precise locations  
- Any series without `published_at` (cannot replay)

---

## 10. Decision record

| Decision | Choice |
|---|---|
| v0 DA method | **Open-loop expert rule + climatology**; optional hierarchical intercepts after n≥3 farms |
| v0 physics | Tide + NWP/in-situ; **no GCM** |
| First sequential DA (if ever) | Particle filter on a **named** tracer (HAB/eDNA) in one basin, research-only |
| Ocean-model DA | **Consume** licensed analyses; do not reimplement 4D-Var |
| Depth in DA | `INTERTIDAL_AIR` + `SURFACE_0_5` for v0; `BOTTOM_CONTACT` for later lobster |
| Global EnKF | **Out of scope** |

No code in this pass implements these filters. No data pulled.
