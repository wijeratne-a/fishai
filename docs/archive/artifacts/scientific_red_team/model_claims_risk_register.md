# Model Claims Risk Register

**Agent:** SCIENTIFIC_RED_TEAM_AGENT  
**Date:** 2026-09-18  
**Scope:** Planned product-class claims for three UNRESOLVED wedges. No model trained.  
**How to use:** Every user-facing sentence, map, and sales claim must map to a row. New sibling-agent claims get new IDs. HIGH/BLOCKER rows block customer-facing pilots until resolved, visibly bounded, or accepted in writing by a **qualified human domain reviewer** (this agent is not that reviewer).

**Severity:** `BLOCKER` > `HIGH` > `MEDIUM` > `LOW`  
**Status:** `OPEN` unless a human signs a later addendum.

**Evidence ceiling:** user-facing claim ≤ strongest evidence tier. Default public product Category C or D only.

---

## Cross-cutting

| ID | Implicit / planned claim | Evidence tier of inputs | Category if published | Failure mode | Sev | Falsification / test | Status |
|---|---|---|---|---|---|---|---|
| RT-XCUT-01 | We can ship a defensible forecast after internal fit looks good | None | n/a | Insufficient validation | BLOCKER | No labels, no as-of store, no baseline, no blocked CV, no prospective log | OPEN |
| RT-XCUT-02 | “Current” SST/chl/reanalysis was available at issuance | 3 | D inflated to C/A | Temporal leakage | HIGH | Feature `availability_at_prediction_time`; delayed-mode vs NRT; 8-day chl includes future days | OPEN |
| RT-XCUT-03 | Random split / neighboring cells are independent tests | 3 | any | Spatial leakage; autocorrelation misuse | HIGH | Year-block + spatial-block CV; persistence baseline must be beaten prospectively | OPEN |
| RT-XCUT-04 | SST, chlorophyll, AIS, social posts measure animals or stress | 3–4 | E/D sold as A/B | Proxy misuse | HIGH | Mechanism table: SST≠body T≠bottom T; chl≠prey; AIS≠biomass; social=Tier 4 | OPEN |
| RT-XCUT-05 | High catch or high vessel density = high abundance | 2–3 | C sold as B/A | Effort confounding; hyperstability | HIGH | Harley et al. 2001; bag-limit truncation; trap saturation; targeting | OPEN |
| RT-XCUT-06 | Partner/public logs are an unbiased sample | 2 | C | Reporting, selection, survivorship bias | HIGH | Missing zeros; protocol breaks; failed operations drop out | OPEN |
| RT-XCUT-07 | Model skill is biological, not month×place | 2–3 | D | Overfit season/location | HIGH | Ablate calendar/region dummies; compare to seasonal spatial average | OPEN |
| RT-XCUT-08 | Significant coefficient ⇒ “driven by / caused by” | 3 | D | Unsupported causal language | HIGH | Ban causal verbs unless intervention evidence exists | OPEN |
| RT-XCUT-09 | Smooth heatmap + 0.73 probability is the truth | 3 | D | Misleading maps; false precision | HIGH | Rank bands only; coarse cells; no red/green go-fish palette | OPEN |
| RT-XCUT-10 | Score implies “do X now” | n/a | n/a | Ungrounded recommendation | HIGH | Options not commands; no legal/safety authorization | OPEN |
| RT-XCUT-11 | Fine public maps are scientifically useful | 2 | C/D | Sensitive-location leakage | BLOCKER | Exact spots NEVER_PUBLISH; coarsen; partner private default | OPEN |
| RT-XCUT-12 | “Closure-risk” or “relative abundance percentile” is a valid public target | 2–3 | B/legal | Claim > evidence; legality shadow model | HIGH | Reject as public targets; closures are context feed only | OPEN |
| RT-XCUT-13 | HiveClaw / “AI” compensates for weak ocean labels | n/a | n/a | AI-washing | HIGH | Master prompt rule 8; HiveClaw is unrelated local inference | OPEN |

---

## Wedge 1 — Pacific oyster × WA × 72h ops stress

| ID | Implicit / planned claim | Evidence | Cat | Failure mode | Sev | Falsification / test | Status |
|---|---|---|---|---|---|---|---|
| RT-OYS-01 | Ops-stress brief will not be used as food-safety or harvest legality | Mixed 1–3 | D sold as legal | Product/causal contamination | BLOCKER | WAC 246-282-006 already maps harvest temperature → 24h prohibition; any combined score fails the wall | OPEN |
| RT-OYS-02 | Satellite/model SST predicts 72h oyster stress/mortality | 3 | D | Proxy misuse (wrong thermal variable) | HIGH | 2021 AHW: aerial + solar + midday tide, not MHW/SST (Raymond et al. 2022) | OPEN |
| RT-OYS-03 | 72h output is a mortality forecast | 1 lab / 2 farm | D sold as A | Horizon mismatch; delayed mortality | HIGH | George et al.: mortality to day 30 after 4h aerial heat; triploids worse | OPEN |
| RT-OYS-04 | Official closures are ground truth for ops stress | 2 regulatory | D→legal | Wrong label; temporal lag | BLOCKER | Closures = tissue tests + admin process; SoundToxins ≠ toxin result | OPEN |
| RT-OYS-05 | Growing-area or SST grid = lease outcome | 3 | D | Spatial leakage; farm privacy | HIGH | Culture method, ploidy, density differ; lease performance PRIVATE | OPEN |
| RT-OYS-06 | One “stress score” captures heat, hypoxia, HAB, disease, waves | 3 | D | False causal aggregation | HIGH | Separate mechanisms; Hood Canal DO ≠ Willapa heat ≠ PSP | OPEN |
| RT-OYS-07 | Chlorophyll indicates oyster food or HAB toxin | 3 | E | Proxy misuse | HIGH | CDOM/turbidity; pigment ≠ toxin; 8-day composite ≠ 72h | OPEN |
| RT-OYS-08 | Harvest-window suitability is an allowed ops target | 3 | legal | Claim > evidence | BLOCKER | Master prompt 15.1 lists it; red team forbids as public/legal language | OPEN |
| RT-OYS-09 | Intertidal and subtidal culture share a model | 1–2 | D | Selection / mechanism mix | MEDIUM | Stratify culture type or do not pool | OPEN |
| RT-OYS-10 | Partner farms with sensors represent WA industry | 2 | D | Selection / survivorship | MEDIUM | Sensor farms are better capitalized; failed farms vanish | OPEN |

**Allowed claim (if walls hold):** Category D, private lease, 72h **operational disruption / environmental-stress indicator**, sensors+tide+air+wave, DOH box separate, no harvest advice.

---

## Wedge 2 — Chinook × CA/OR × 24–48h relative encounter

| ID | Implicit / planned claim | Evidence | Cat | Failure mode | Sev | Falsification / test | Status |
|---|---|---|---|---|---|---|---|
| RT-CHK-01 | Env fields identify 24–48h encounter | 3 | D sold as forecast | Identifiability failure; proxy misuse | BLOCKER | Published SST links are seasonal/stock-scale (Shelton et al. 2021), not 48h | OPEN |
| RT-CHK-02 | Encounter score ≈ abundance or catch guarantee | 2 | C sold as A/B | Effort confounding; false precision | BLOCKER | Bag-limit truncation; missing weather zeros; language contract | OPEN |
| RT-CHK-03 | “Chinook” is one stock in a hotspot map | 2 | D | Stock mix; ESA leakage | BLOCKER | SRWC, CA Coastal, KRFC/KRSC mix; GSI limits; concentrating effort | OPEN |
| RT-CHK-04 | Public RecFIN/CRFS/CPFV data label 24–48h cells | 2 lagged | C | Temporal leakage; resolution mismatch | HIGH | CRFS ~20–25% of days; logs monthly; RecFIN CTE001 excludes salmon | OPEN |
| RT-CHK-05 | Model is biological not weather-workability | 3 | D | Mislabel; forbidden weather-safety product | HIGH | If waves/wind dominate, do not call it encounter | OPEN |
| RT-CHK-06 | Fine map helps captains without leaking spots | 2 | C | Sensitive-location leakage | HIGH | Charter holes are the business; coarsen ≥ PFMC subarea / ≥10 km | OPEN |
| RT-CHK-07 | Social “limits” posts calibrate the model | 4 | E | Reporting bias; illegal labels | HIGH | Tier 4 cannot be labels | OPEN |
| RT-CHK-08 | AIS of CPFVs = fish location | 3 | E | Proxy misuse | HIGH | Traffic ≠ Chinook; privacy | OPEN |
| RT-CHK-09 | Closed-area cells can still be scored | 2 | D | Ungrounded / illegal invitation | BLOCKER | Hard mask: closed ⇒ no score | OPEN |
| RT-CHK-10 | Month×port climatology marketed as 48h AI | 2 | C | Overfit season/location | HIGH | Must beat seasonal spatial average *and* be labeled climatology if it cannot | OPEN |
| RT-CHK-11 | Chlorophyll = forage = adult bite tomorrow | 3 | D | Proxy misuse | HIGH | Hassrick et al. is juvenile survey scale, not adult 48h | OPEN |

**Allowed claim (narrow):** private Category C rank vs comparable **open-season** days in the same management area from partner logs; not abundance; not guarantee; regulations win.

---

## Wedge 3 — Lobster × GOM × next-trip CPUE

| ID | Implicit / planned claim | Evidence | Cat | Failure mode | Sev | Falsification / test | Status |
|---|---|---|---|---|---|---|---|
| RT-LOB-01 | AIS / GFW / vessel density = lobster abundance or fleet effort | 3 | B/A | Proxy misuse; selection; privacy | BLOCKER | 33 CFR 164.46 ≥65 ft; most inshore boats absent; Addendum XXIX is confidential federal-permit subset | OPEN |
| RT-LOB-02 | CPUE up = more lobsters in the cell | 2 | C sold as B | Hyperstability; catchability | HIGH | ASMFC 2025 peer review; Harley 2001; bottom T catchability (Zhang 2025); trap saturation (Watson 2019) | OPEN |
| RT-LOB-03 | Historical CPUE is a continuous index | 2 | C | Reporting-protocol break | HIGH | 10% → optimized active → 100% in 2023; VTR/tribal gaps (Hodgdon 2025) | OPEN |
| RT-LOB-04 | Public high-CPUE heatmap is a product | 2 | C | Sensitive-location leakage | BLOCKER | Exact sets NEVER_PUBLISH; competitive harm; gear conflict | OPEN |
| RT-LOB-05 | Model can recommend new ground (unfished cells) | 2 presence-only | D | Selection; no true zeros | HIGH | Condition on operator’s existing footprint | OPEN |
| RT-LOB-06 | SST = lobster habitat now | 3 | D | Proxy misuse | HIGH | Need bottom temperature; SST skin ≠ bottom | OPEN |
| RT-LOB-07 | Soak-unnormalized landings are CPUE | 2 | C invalid | Effort confounding | HIGH | Define trap-haul / soak; saturation after ~24h | OPEN |
| RT-LOB-08 | Restricted-area CPUE drop = animals left | 2 | C | Regulatory confounding | MEDIUM | Whale/gear closures ≠ biology | OPEN |
| RT-LOB-09 | Partner logbooks represent the GOM stock | 2 | C | Selection / survivorship | MEDIUM | Highliners; latent permits; zone license structure | OPEN |
| RT-LOB-10 | 1-minute tracker pings are a lawful commercial feature | 2 restricted | n/a | Rights + privacy | BLOCKER | HUMAN LEGAL REVIEW; default REJECTED for training/maps | OPEN |

**Allowed claim (narrow):** private Category C rank of **legal catch per defined effort** for that operator’s strings; confounders listed; not abundance; not AIS.

---

## Claim-strength vs evidence (quick ceiling)

| If strongest label is… | Strongest public category | Typical forbidden upgrade |
|---|---|---|
| Partner farm mortality/workability + in situ sensors | D (ops stress) | Food-safe, legal harvest, % mortality to 2 decimals |
| Partner charter log CPUE | C (rank) | Abundance, 48h habitat certainty, “you will catch” |
| Partner lobster log CPUE | C (rank) | Stock map, AIS hotspot, public strings |
| Official survey index (if ever used) | B inside survey design | Cell-level census |
| SST/chl/AIS only | D context or **no biological claim** | Any presence/abundance/safety claim |
| Social / forums | E queue only | Any prediction |

---

## Sibling-artifact claims (second pass)

| ID | Implicit / planned claim | Source artifact | Sev | Status |
|---|---|---|---|---|
| RT-SIB-01 | Alert if SST ≥ 19 °C for 12 h; Hobday MHW flag | `quality_and_validation/baseline_model_spec.md` B4 | HIGH | OPEN — wrong thermal variable; 19 °C is growth-band; MHW ≠ AHW |
| RT-SIB-02 | Sample brief: top 20%, water temp +1.8 °C first, Totten analog | `product_and_monetization/wireframe_spec.md`, `product_thesis.md` | HIGH | OPEN — false precision; Vp Category 3 contamination |
| RT-SIB-03 | “Safely work the tide”; B5 “changed harvest plans” | `requirements_and_wedge/recommended_initial_wedge.md`; baseline B5 | HIGH | OPEN — weather-safety / harvest-legality language |
| RT-SIB-04 | 24–48h Chinook thermal habitat 8–12 °C with depth; SST/chl v0; ~10 km / H3-6 product cell | marine_domain + product + validation_protocol + geo | HIGH | OPEN — not identified at horizon; cell too fine for public |
| RT-SIB-05 | Label specifiable = 5; public ME reports as GT = 3 | `go_no_go_scorecard.md` | MEDIUM | OPEN — spec ≠ identifiability; lag/confidentiality |
| RT-SIB-06 | H3 res 8 oyster feature grid as if product grain | geo handoff / canonical_data_model | MEDIUM | OPEN if mapped; OK if private raster sample only |
| RT-SIB-07 | AIS as Chinook effort-coverage diagnostic | `validation_protocol.md` | MEDIUM | OPEN — default deny ingest |

---

## Register maintenance

- New product copy → new row or explicit map to an existing allowed claim.
- Sibling artifacts, when they exist, must be diffed against this register.
- Closing a BLOCKER/HIGH row requires: evidence of fix **or** visible limitation language **and** named human reviewer, date, and scope.
