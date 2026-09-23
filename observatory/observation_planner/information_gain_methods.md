# Information-gain methods

**Date:** 2026-09-18  
**Status:** Methods card for the Active Observation Planner. Cite, do not copy papers. No DA code. No ingest.  
**Honesty rule:** classify every method as `IMPLEMENTABLE_NOW` (with the data and models this program actually has) or `REQUIRES_RESEARCH_BREAKTHROUGH` (physics or identifiability, not just “needs a sprint”).

The planner’s objective is **expected reduction in decision-relevant uncertainty**, not entropy of a global animal field we do not have.

---

## 1. Value of information (VOI)

Classical decision analysis: an observation is worth collecting if the expected improvement in the **decision** exceeds its cost and harm (Raiffa & Schlaifer 1961; Howard 1966 *IEEE Trans. Syst. Sci. Cybern.*; Lindley 1956 *Ann. Math. Statist.* on measures of information in experiments).

Let \(a\) be an action in a **named** set (W1: shift handling off the hottest emersion; inspect gear after a wave window; increase monitoring — **options, not commands**). Let \(u(a,x)\) be a utility that is **not** revenue-from-take and **not** harvest legality. Let \(y\) be a future observation.

**Expected value of sample information (EVSI):**

\[
\mathrm{EVSI}(y) = \mathbb{E}_y\big[\max_a \mathbb{E}[u(a,x)\mid y]\big] - \max_a \mathbb{E}[u(a,x)]
\]

**Expected value of perfect information (EVPI)** is the same with \(y=x\). EVPI is an **upper bound**, not a product claim.

**What is IMPLEMENTABLE_NOW**

- Replace \(u\) with a **proxy**: reduction in `confidence_category` error, Brier against `ops_disruption_72h`, or fraction of issuances that move from Low → Medium because a **critical missing input** is filled (`uncertainty_policy.md`).
- Discrete action set of size ≤5, as in the oyster contract options.
- One-step lookahead on **whether labels exist at all** (they do not, in-repo). EVSI of a partner form is approximately EVPI on the label margin.

**What REQUIRES_RESEARCH_BREAKTHROUGH**

- Global EVSI over a saltwater-life twin with unknown \(H\), unknown costs, and mixed `NEVER_PUBLISH` states.
- Computing VOI by inverting eDNA to \(N\) or AIS to abundance (identifiability + policy; not a compute problem).
- Closed-form VOI for non-stationary spatial fields without a fitted observation-error model.

W1 implication: the 30-second outcome form is high EVSI because the **state we issue is unevaluable** without it. A Pacific glider profile of offshore SST has near-zero EVSI for lease emersion heat.

---

## 2. Expected uncertainty reduction (practical EUR)

Full posterior-variance traces need a fitted model. This program has **no fitted model** (wedge UNRESOLVED; Gate 3 labels missing).

**IMPLEMENTABLE_NOW — rule EUR**

1. List critical inputs for the issuance (`uncertainty_policy.md` §2.1: FRESH, DENSITY, LABEL_SUPPORT, …).  
2. Score 1 if the candidate observation is the **named missing critical** (e.g. farm labels; bag T during emersion).  
3. Score partial if it is a supporting covariate with a documented mismatch (water T station vs lease).  
4. Cap SST-only EUR at 0.20 on W1.  
5. Prefer **label** and **metadata for \(H\)** over another environmental raster.

**IMPLEMENTABLE_NOW — ensemble spread as a stand-in**

Where multiple **admissible** forecasts exist (NWS members, CO-OPS vs local tide staff, in-situ vs NWP air):

\[
\widehat{\mathrm{FcstDis}} = \mathrm{clip}_{[0,1]}\big(\mathrm{spread}(\{f_k\}) / \mathrm{operational\_scale}\big)
\]

Spread on **forbidden** quantities (AIS density “as fish”) is discarded.

**REQUIRES_RESEARCH_BREAKTHROUGH**

- Mutual information \(I(x;y)\) on a 3-D global biomass field.
- Gradient-based sensor placement on an unbuilt EnKF (v0 DA is open-loop expert rule; `data_assimilation_design.md`).

Literature for later (cite, do not implement): Chaloner & Verdinelli 1995 Bayesian experimental design; Krause, Singh & Guestrin 2008 submodular sensor placement; Settles 2009 active learning survey — useful **after** a model exists that is allowed to be trained.

---

## 3. Ensemble disagreement

**Honest use:** disagreement among physics ensembles or among **baselines** (B4 vs B12 vs B3 vs B5) flags where a new observation **adjudicates a decision**.

| Ensemble | IMPLEMENTABLE_NOW? | Notes |
|---|---|---|
| NWS / NWP air T members × tide | Yes, after rights | W1 primary physical disagreement is **timing of heat vs emersion**, not SST color |
| B4 expert rule vs B12 climatology | Yes, once labels exist | If they disagree on alert, a farm log has high EUR |
| Satellite SST vs intertidal bag T | Yes, if bag loggers exist | Disagreement is expected; **bag T wins** for the mechanism |
| Multi-model fish SDM | No | No identified 24–48 h Chinook SDM (Shelton et al. 2021 scale mismatch; red team) |
| AIS vs CPUE | Forbidden | Not disagreement to resolve; category error |

**REQUIRES_RESEARCH_BREAKTHROUGH:** treating deep-learning predictive entropy over OBIS points as “where to survey next” without a detection model — that optimizes **sampler bias**, not occupancy.

---

## 4. Occupancy and detection probability

MacKenzie et al. 2002 *Ecology* (https://doi.org/10.1890/0012-9658(2002)083[2248:ESORWD]2.0.CO;2):

\[
\mathbb{P}(y=1)=\psi\, p,\qquad \mathbb{P}(y=0)=(1-\psi)+\psi(1-p)
\]

A zero is **not** \(1-\psi\). Guillera-Arroita, Ridout & Morgan 2010; Tyre et al. 2003: ignoring \(p\) biases occupancy and “range.”

N-mixture (Royle 2004) is **not** a stealth census. Identifiability is fragile (Barker et al. 2018 *J. Appl. Ecol.* https://doi.org/10.1111/1365-2664.13143; Kéry 2018). **Do not** use N-mixture to invent \(N\) from unstructured OBIS.

**IMPLEMENTABLE_NOW**

- Persist the ternary `SPECIES_ABSENT` / `NOT_DETECTED` / `NO_OBSERVATIONS` (`scoring_spec.md` §5).  
- Design repeat visits or dual methods **only** when a detection-nondetection grid is the scientific target (not W1 farmed oysters — stock is planted and counted by the farmer).  
- For W2/W3 later: zeros in logs are catchability-confounded; buy **effort metadata**, not more empty cells.

**REQUIRES_RESEARCH_BREAKTHROUGH**

- Global \(p(s,t,\text{modality})\) for all taxa.  
- Converting eDNA read counts to \(p\) without local calibration.  
- Using occupancy to “fill” `NO_OBSERVATIONS` cells for a public map.

W1: occupancy of *wild* *M. gigas* is the **wrong state**. The animals are on the lease. Information gain is about **stress and workability**, not \(\psi\).

---

## 5. eDNA transport uncertainty

Forward problem (relatively mature): DNA concentration \(C\) as a decaying tracer

\[
\partial_t C + \mathbf{u}\cdot\nabla C = \nabla\cdot(K\nabla C) - \lambda C + S
\]

- Sassoubre, Yamahara, Gardner, Block & Boehm 2016 *Environ. Sci. Technol.* https://doi.org/10.1021/acs.est.6b03114 — shedding/decay order **hours**.  
- Harrison, Sunday & Rogers 2019 *Proc. R. Soc. B* https://doi.org/10.1098/rspb.2019.1409 — fate and transport.  
- Andruszkiewicz et al. 2019 *Sci. Rep.* https://doi.org/10.1038/s41598-019-40788-z — Lagrangian transport; **models can exceed field detections**.  
- Scriver et al. / *Environmental DNA* transport reviews (e.g. https://doi.org/10.1002/edn3.405); 2025 spatial-bound work reporting modeled medians on the order of **~2–14 km**, up to ~10× observed (see observatory modality catalog).  
- Murakami et al. 2019 — empirical detection often **tens of meters** vs km-scale models.

**Inverse problem** \(C \mapsto S \mapsto\) animals is **underdetermined** (shedding, \(\lambda(T)\), dilution, PCR, non-unique sources). Observatory DA design: particle filter on **tracer \(C\)** in one estuary later; emit presence-risk, not \(N\). Rare-taxon native coordinates are `NEVER_PUBLISH`.

**IMPLEMENTABLE_NOW**

- Do **not** recommend eDNA as the W1 next observation (sessile farmed stock already known).  
- If a later basin occupancy study is designed: pair samples with **current/tide** and blanks; treat positives as **plume evidence**; coarsen listed taxa.  
- Score EUR against occupancy/tracer uncertainty, never against biomass.

**REQUIRES_RESEARCH_BREAKTHROUGH**

- Operational inversion to source biomass or to GPS of a rare animal.  
- Global autonomous eDNA mesh as a census (`H-4.1` remains partnership/infra).  
- Using eDNA to reopen NSSP harvest (toxin ≠ DNA of the oyster).

---

## 6. Depth uncertainty versus horizontal uncertainty

Horizontal grids (H3, SST pixels) are cheap. **Vertical mismatch is often the larger error.**

| Setting | Horizontal issue | Vertical issue | Planner consequence |
|---|---|---|---|
| W1 intertidal oyster | 1 km SST ≠ lease | **Air vs water vs tissue**; cm of elevation | Buy **elevation metadata + bag T + air×tide**, not a finer SST grid |
| Chinook 8–12 °C (Hinke et al. 2005 *MEPS* https://doi.org/10.3354/meps304207) | 10 km cell still not a waypoint | Fish **go deeper** when SST warms | Surface hotspot maps can invert encounter; subsurface T has higher EUR than another color pixel |
| Lobster CPUE | Stat area vs string | **Bottom T ≠ SST** (ASMFC 2025 peer review) | eMOLT-class bottom T (coarsened) before satellite SST |
| eDNA | Station vs plume km | Thermocline / depth of filter | Do not integrate across pycnocline naively |
| PAM | Detection range km | Calling depth / waveguide | Localization is `NEVER_PUBLISH` for mammals |

**IMPLEMENTABLE_NOW:** put `depth_bin` on every recommendation (`INTERTIDAL_AIR`, `SURFACE_0_5`, `BOTTOM`, …). Prefer observations that kill the **named vertical error**.

**REQUIRES_RESEARCH_BREAKTHROUGH:** a global 3-D unstructured animal mesh with honest observation operators at every depth.

Literature: Fiedler & Bernard 1987 and later habitat-volume work; ocean-color optical depth (Jerlov / \(K_d\)) — animals below optical depth are **IMPOSSIBLE** to image from air/space (`observation_modality_catalog.md`).

---

## 7. Modality-specific information, FP/FN (qualitative)

False positives/negatives below are **qualitative**. Do not invent rates.

| Modality | Typical false + | Typical false − | IG notes |
|---|---|---|---|
| Partner ops form | Misremembered tide; social-desirability | Non-response bias | Highest W1 IG if completeness holds |
| Bag thermistor | Logger in shade/mud not representing bag | Gap / biofouling | Adjudicates air vs tissue |
| Tide gauge | Datum / staff offset | None for “no tide” | High for emersion **when paired with air** |
| Satellite SST | Skin ≠ bulk ≠ tissue | Cloud | Low W1 IG if already available |
| eDNA metabarcoding | Contamination, rare-taxa inflation (Darling, Jerde, Sepulveda 2021) | Primer dropout, inhibition | Occupancy tracer |
| qPCR target | Lab contamination | Shedding below LOD | Better for *named* occupancy |
| Active acoustics | Siphonophore resonance, mixed TS | Near-surface/bottom dead zones | Biomass only with ID haul |
| PAM | Other sources, detector FP | Silence ≠ absence | Presence of vocalizers |
| Aerial/drone | ID error, glare | Availability bias (submerged) | Disturbance cost in `HarmPen` |
| CPUE | Targeting, hyperstability | Low catchability | Category C only |
| AIS | — | — | **Not an animal observation** |

---

## 8. Summary table

| Method | IMPLEMENTABLE_NOW | REQUIRES_RESEARCH_BREAKTHROUGH |
|---|---|---|
| Rule EUR from missing critical inputs | Yes | — |
| Discrete EVSI on W1 action set once labels exist | Yes (small) | Global VOI twin |
| NWP / baseline disagreement | Yes | Fish-SDM ensemble as 48 h truth |
| Ternary occupancy accounting | Yes | Global \(p\) surface |
| Repeat-visit occupancy in one estuary | Partnership + design | — |
| N-mixture census | No | Identifiability |
| eDNA forward tracer in one basin | Later research T5 | Inverse to \(N\) / rare GPS |
| Depth-aware recs | Yes (bins) | Global 3-D animal mesh |
| Submodular glider paths on EnKF | No | Needs a real DA system we will not pretend to have |
| Active learning on untrained net | No | Would overfit sampler bias |

**Default W1 information-gain engine:** missing-label and missing-\(H\)-metadata first; then vertical/microclimate (air × tide × bag T); then existing in-situ water T/S; never offshore gliders or DOH closure assays as ops IG.
