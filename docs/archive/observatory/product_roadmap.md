# Product roadmap — Global Saltwater Life Observatory

**Agent:** product roadmap owner (COST + UI/EXPLAINABILITY)  
**Date:** 2026-09-18  
**Status:** Scientific/technical product path. **Not** a commitment to ship a global consumer map.

---

## 0. Two products, one firewall

| | **Commercial FishAI** | **Observatory** |
| --- | --- | --- |
| Job | One paid decision | Honest living digital-twin *blueprint* and one validated cell |
| Scope until traction | **ONE species × ONE geography × ONE customer × ONE decision** | Research globally; **build** only the smallest cell that could later serve that wedge |
| v0 surface | Email + PDF brief | Same brief + evidence UI for scientists/operators; **no fish-count theater** |
| Success | Behavior change + WTP | Skill vs baseline + calibrated UNKNOWN + no claim inflation |
| Failure mode | Another NANOOS tab | A planetary heatmap of interpolated animals |

**Rule:** Observatory research **must not** expand the commercial SKU. A Chinook layer in the observatory catalog is not a Chinook product.

**Recommended commercial wedge (RECOMMENDED, not DECIDED):** Pacific oyster (*Magallana gigas*) × Willapa Bay WA DOH growing areas × farm operator × 24–72h operational stress / work-window. See `/Users/wijeratne/dev/fishai/artifacts/requirements_and_wedge/recommended_initial_wedge.md`.

**Recommended observatory P0:** the same cell, as a **digital twin of environmental + operational-stress state** — because the animals are sessile on the lease, the decision exists year-round, and public covariates already exist. This is the smallest *honest* twin that can later feed the commercial brief.

---

## 1. Product principles (UI + claims)

Every user-facing view, including internal demos:

1. **Exactly one evidence class** on every layer: DIRECTLY OBSERVED | REMOTELY DETECTED | SURVEY-DERIVED | TAG/TELEMETRY-DERIVED | OPERATIONALLY OBSERVED | MODEL-INFERRED | FORECAST | HYPOTHETICAL/RESEARCH MODE | UNKNOWN/INSUFFICIENT DATA.  
2. **UNKNOWN is first-class** — a hatched cell is a successful render, not a missing texture.  
3. **No fish-count theater** — no fake integers, no 3-decimal probabilities, no SST painted as biomass.  
4. **Depth + time + uncertainty** are always visible (emersion vs water column for oysters; depth band for pelagics).  
5. **Provenance** (source, as-of, license class, model version).  
6. **What it does not mean** (food-safety, harvest legality, abundance, navigation, catch guarantee).  
7. **14-field output contract** inherited from the commercial product (`artifacts/product_and_monetization/product_thesis.md` §7) plus observatory evidence class and support tier T0–T6.

Copy may shorten layout. It may **not** strengthen meaning. Red-team contract: `fishai/artifacts/scientific_red_team/prediction_contract.md`.

---

## 2. Traction gates (commercial) vs scientific gates (observatory)

Observatory P0 may proceed as **research** with public catalog-only work while the founder wedge is UNRESOLVED. **Issuing operator-facing briefs** and **partner collection** wait on founder lock + rights.

| Gate | Commercial | Observatory P0 |
| --- | --- | --- |
| G0 Wedge lock | Founder chooses W1/W2/W3 | P0 follows W1 unless founder locks another ONE×ONE×ONE×ONE |
| G1 Rights | No ingest until APPROVED | Same |
| G2 Partner labels | 3 farms (W1) log outcomes | Same labels are the twin’s ground truth |
| G3 Beat ritual | Brief changes a crew call vs NANOOS+tides+weather | Twin beats simple physical baseline (heat×tide, persistence) |
| G4 Calibration | High ≠ always-on | Confidence categories informative |
| G5 WTP | Paid 90-day signal | Not required to *learn*; required to *scale staff* |
| G6 No claim inflation | Food-safety firewall | Evidence class never silently upgraded |

If G3 or G5 fail: **narrow or stop**. Do not add taxa, maps, or hardware.

---

## 3. Roadmap phases

### P0 — Framework + one prototype cell (Year 1)

**Ship:** taxonomy/support-tier framework (sibling); modality catalog (sibling); rights/unknown policy; **Willapa *M. gigas* OSI-72 twin**; evidence-typed email/PDF + outcome form; as-of replay for that cell only.

**Do not ship:** global map, species picker, foundation model, DAS, AUV, public farm performance, harvest authorization.

**Support tier target for P0 taxon in-cell:** T3–T4 *attempt* (current condition + 72h forecast of **stress conditions**, not mortality %). Likely landing: **T2–T3 with honest UNKNOWN** until prospective skill exists. T6 is **not** a Year-1 claim.

### P1 — Operational-ish first cell (Year 1–2, only if G3–G5)

Daily briefs in stress season; calibrated confidence; partner loop ≥60% complete; automation of source pull before farm 8.

### P2 — Few taxa, still bounded (Year 2–3)

**At most 2–4 additional operational-ish slices**, each still ONE×ONE×ONE×ONE, chosen for *validatability*:

| Candidate slice | Why it might be next | Why it might never be next |
| --- | --- | --- |
| Same oyster, **one other WA basin** (e.g. named South Sound) | Transfer test of culture-method stratification | Different hypoxia physics; easy to fake “Washington-wide” |
| American lobster **private** CPUE, one statistical area | Strong surveys; bottom-T catchability science | Confidentiality; AIS temptation; CPUE≠abundance |
| A **surface-visible** scientific cell (HAB/bloom extent, or permissioned mammal detections coarsened) | Honest DIRECTLY/REMOTELY DETECTED layer | NEVER_PUBLISH tracks; not a commercial FishAI SKU |
| Chinook 24–48h encounter | Only if season stays open **and** captains log effort | Worst public-product science; closure can zero the decision |

Default P2 if oyster WTP fails: **do not automatically switch to Chinook maps.** Write a pivot memo.

### P3 — Regional observatory fabric (Year 4–6)

Shared **architecture** (layers 0–10, replay, privacy tiers) reused across cells. Most of the WoRMS tree remains **T0–T2**. Public surfaces are **coverage/unknown maps** and attributed survey indices — not a video game ocean.

### P4 — Planetary observation vision (Year 7–10)

See `10_year_plan.md`. Vision = **infrastructure + honesty + a few dense cells**, not omniscience.

---

## 4. Surface roadmap (what humans touch)

| When | Surface | Forbidden twin |
| --- | --- | --- |
| P0 | Email + 1-page PDF + 30s form + scientist “evidence drawer” | Multi-tab terminal |
| P0 | Internal cell dashboard: drivers, missingness, station distance, depth/emersion | Choropleth of “oysters” |
| P1 | Same + weekly private calibration email | Push spam on Typical days |
| P2 | Per-taxon cards with support tier; API for **evidence-typed** JSON | Species arcade |
| P3 | Partner GIS/API feeds (Esri/BlueTrace class) | Replacing farm ERP |
| P4 | Public **unknown/coverage** globe; restricted biological layers | Public abundance globe |

Wireframe language for the brief: `fishai/artifacts/product_and_monetization/wireframe_spec.md`. Observatory extensions: `artifacts/product_cost/sample_evidence_ui_spec.md`.

---

## 5. Model / ML roadmap (deliberately boring)

| Stage | Allowed | Blocked |
| --- | --- | --- |
| P0 weeks 1–8 | Manual brief; documented rules (tide × air, wave threshold) | Neural nets, foundation models |
| P0 after labels | Simple baselines (persistence, climatology, GLM/GAM **if** n allows) | Training on DOH closures, SST-as-y, AIS-as-y |
| P1 | Only if beats baseline on time-forward + spatial holdout | Claiming T6 |
| P2+ | Cell-specific models; transfer **as hypothesis** | One weights file for all taxa |
| Anytime | Suppression when Low + missing critical inputs | Opaque 0–100 scores |

Quality gates: `fishai/artifacts/quality_and_validation/go_no_go_scorecard.md`. Observatory validation sibling owns the global protocol.

---

## 6. Monetization (commercial only; observatory is not a SKU)

Hypothesis prices for the oyster brief: design-partner $0–$500; paid 90-day **$750–$1,500**; recurring **$400–$900 / farm / month** — **untested**. Source: `fishai/artifacts/product_and_monetization/pricing_hypothesis.md`.

Observatory funding is **research / public-good / partnership**, not “sell the globe.” A planetary marketplace (hypothesis 4.13) is out of Year-1 scope.

---

## 7. Explicit non-goals (until named gates)

- Tracking every saltwater organism.  
- Real-time individual tracking without tags/sensors.  
- Abundance from satellites or vessel density.  
- Food-safety or legal-harvest products.  
- Public fishing-spot or farm-performance maps.  
- Hardware as a substitute for labels.  
- Unconstrained LLM chat over ocean layers.

---

## 8. Decision log (start)

| Date | Decision | Status |
| --- | --- | --- |
| 2026-09-18 | P0 cell = Willapa Pacific oyster OSI-72 twin | **RECOMMENDED**, not founder-locked |
| 2026-09-18 | Hardware last after public→partner export→existing sensors→manual→mobile→integrations | **LOCKED by this roadmap** |
| 2026-09-18 | No public global biological heatmap in v1 | **LOCKED** |
| 2026-09-18 | Commercial 1×1×1×1 until traction | **LOCKED** (inherits commercial run) |
