# Agent handoff — observatory validation, physics, and scientific red team

**Date:** 2026-09-18  
**From:** MODEL_VALIDATION_AND_UNCERTAINTY_AGENT + PHYSICS_AND_FEASIBILITY_RED_TEAM_AGENT + SCIENTIFIC_PEER_REVIEW_RED_TEAM_AGENT  
**To:** Orchestrator, founder, REQUIREMENTS_AND_WEDGE, MARINE_DOMAIN, QUALITY_AND_VALIDATION, SCIENTIFIC_RED_TEAM (FishAI folder), PRODUCT, DATA_RIGHTS, GEOSPATIAL, DATA_DISCOVERY  
**Write scope:** `/Users/wijeratne/dev/fishai/observatory/` only  
**Did not overwrite:** `artifacts/scientific_red_team/**`, `artifacts/quality_and_validation/**`, or other sibling folders.

**Project context read:** FishAI `STATE_10_PAUSED_FOR_HUMAN_DECISION`; wedge UNRESOLVED; no ingest; no models; prediction contract Category C/D default; AIS ≠ abundance; UNKNOWN must be sayable.

---

## 1. Executive finding

A **global saltwater life observatory that tracks everything** is **not physically identified** and **not scientifically deployable**. Satellites observe an optical skin, not fish. Acoustics cannot have basin-scale range and fish-body identity on one frequency. eDNA is a decaying, moving tracer. Tags are delayed and few. DAS measures cable strain at gauge lengths of meters, mostly at low frequency. Bioluminescence from space is not a taxon. Underwater comms are kbps-class acoustics or short-range optics. Unattended sensors foul.

**No model is accepted because it looks plausible.** If it does not beat a frozen simple baseline on honest time-forward **and** spatial tests, it is **NOT READY FOR USE**.

**Observatory biological emissions today: support T0–T1 catalog only. T3–T6 assigned count = 0. T6 operational grade: not met.**  
**FishAI 1×1×1×1 briefs must not inherit observatory slogans.** Cost/UI P0 Willapa OSI-72 is the smallest honest twin candidate — still not T6.

This trio of agents is **not** a human fisheries scientist, acoustician, or molecular ecologist. HIGH/BLOCKER items stay open until named humans sign.

### Return block (requested)

#### A. Physical hard stops

| Stop | One-line physics |
|---|---|
| Satellites do not see most fish | Water-leaving radiance from the **first optical depth** (often meters; **~1 m or less** in turbid coastal water). SST is skin, not body or bottom T. |
| Acoustics range ≠ resolution ≠ species | Absorption \(\alpha(f)\) and wavelength \(\lambda=c/f\). Uncalibrated NASC ≠ biomass; \(\alpha\) error alone moved long-range 38 kHz biomass **17–45%** in Doonan et al. 2003. |
| eDNA ≠ live GPS / abundance | Marine fish eDNA half-lives often **hours to ~2 days**; transport **meters to tens of km**. |
| Tags ≠ real-time population tracks | Duty cycle; PSAT pop-up + Argos; surface drift errors **O(10–50 km)**; tagged n ≪ N. |
| DAS ≠ fish-body map | Gauge **~4–30 m**; long-cable bandwidth often **≲300 Hz**; strain, not target strength. |
| Space bioluminescence ≠ species | VIIRS DNB **~0.74 km** pixels; milky seas are bacterial, not fish ID. |
| No RF mesh of fish | Seawater kills GHz RF; acoustic modems **~10²–10³ bps** class, high latency. |
| No set-and-forget in situ truth | Biofouling on week–month scales. |
| Fusion ≠ census | Cannot create photons, SNR, or samples. Unsampled ocean is **UNKNOWN**. |
| AIS ≠ fish | Vessels; project non-negotiable. |

Full register: `physics_feasibility_reports/physical_limits.md` PX-01…PX-20.

#### B. Most dangerous false claims (this product class)

1. **“We track all marine life in real time.”**  
2. **Public hotspot / biomass heatmap** (effort + spot-burn + ESA/whale harm).  
3. **AIS / vessel density as fish.**  
4. **Satellite sees the fish** (and SST as oyster/lobster/Chinook truth).  
5. **eDNA pin = live animal / abundance.**  
6. **Uncalibrated acoustics or DAS = stock size.**  
7. **Catch guarantee, harvest authorization, food-safe, navigation-safe.**  
8. **Tag tracks as the population; pop-up as nowcast.**  
9. **Cross-ocean / cross-species foundation model “already works here.”**  
10. **Smooth global completeness** (coverage theater; confidence in sparse cells).

#### C. Minimum validation to call **anything** operational (**support T6**)

Species support T6 is defined in `global_species_registry/support_tier_framework.md`. Bind it with `validation_protocol.md` §7 (tests **V1–V9**).

- Locked taxon (or explicit community), geography, target, horizon, grain, universe.  
- Physics not `IMPOSSIBLE`; claim ≤ evidence (Category C/D public biology; A/B only as attributed survey).  
- Rights approved; as-of timestamps; privacy reverse-engineering pass.  
- **V1** time-forward + out-of-year holdout (honest as-of lane).  
- **V2** spatial blocked CV / SAC.  
- **V3** independent source.  
- **V4** **beats frozen simple baseline** (B12/B3/B4) **prospectively** — else **NOT READY FOR USE** (or ship the baseline **labeled as climatology/persistence/rule**, not as AI observatory).  
- **V5** literature at matching scale/stage/depth.  
- **V6** ecological plausibility (catchability ≠ density; unsampled ≠ absent).  
- **V7** calibration: High actually better than Low; no fake intervals.  
- **V8** adversarial review of leakage, effort-vs-biology, habitat-vs-presence, anomalies, coverage hiding, false transfer, sensitive locations, claims>evidence.  
- **V9** physics / modality catalog not `IMPOSSIBLE` for the claimed detection.  
- Coverage/`UNKNOWN/INSUFFICIENT DATA` published; drift monitor; named human reviewers (fisheries + acoustician if sound + molecular if eDNA).  
- 14-field product contract; stop-ship for abundance/legal/safety language.  
- Privacy: `sensitive_location_policy.md` (DAS/PAM mammal localizations `NEVER_PUBLISH`; global public life map **rejected** as v1).

**T6 is claim-scoped.** Operational water level ≠ operational fish. Operational Willapa ops-stress ≠ operational global life layer. T5 tags ≠ T6 census.

---

## 2. Evidence table

| Question | Finding | Evidence | Confidence |
|---|---|---|---|
| Do ocean-color satellites image fish? | No | First optical depth (Gordon & McCluney 1975; Organelli 2017); Shi & Wang 2010 Kd occupancy; Case-2 coastal Kd often >0.3 m⁻¹ | High |
| Can one acoustic freq do range + cm ID globally? | No | Francois–Garrison; Macaulay et al. 2020; ICES survey practice | High |
| Is eDNA a synoptic GPS? | No | Sassoubre 2016; Collins 2018; Lagrangian 5–30 h / 0.3–39 km | High on *not GPS*; medium on exact km |
| Are PSATs live tracks? | No | MiniPAT duty cycle; Horning 2019; Nielsen 2024 drift | High |
| Is DAS a fish census? | No | Bouffaut/Landrø 8.16 m gauge, ~320 Hz on 120 km cable | High |
| Does FishAI have labels/models? | No | `project_state.json`; Quality Gate 3 fail | High |
| Will random CV lie? | Yes | Roberts spatial CV; FishAI RT-XCUT-03 | High |
| Which private MVP is least insane? | Oyster 72 h ops-stress, still blocked | Sibling scientific red team | High as ranking, not a lock |

---

## 3. Source / license table

This pass **did not ingest** data and **does not approve** licenses. Citations are counter-evidence. DATA_RIGHTS owns class.

| Source | Use here | License note |
|---|---|---|
| Organelli et al. 2017; Shi & Wang 2010 | Optical depth / Kd | Cite; not a training corpus |
| Francois & Garrison 1982; Doonan 2003; Macaulay 2020 | Absorption / biomass sensitivity | Cite |
| Sassoubre 2016; Collins 2018; Archimer eDNA Lagrangian | Decay/transport | Cite |
| Wildlife Computers / Argos docs; Horning 2019; Nielsen 2024 | Tag latency | Vendor + papers; not independent census |
| Bouffaut 2022; Landrø 2022; HAL fish-DAS | DAS limits | Cite |
| Miller et al. 2021 VIIRS milky seas | Bioluminescence ≠ fish | Cite |
| WHOI Micromodem; Sanchez 2012 | Comms envelope | Cite |
| FishAI sibling artifacts 2026-09-18 | Claim ceiling, baselines, privacy | Internal; do not overwrite |

**Do not train on** AIS/VMS/Addendum XXIX tracks, farm yields, exact catch GPS, listed-species fine tracks, or CC BY-NC aggregators.

---

## 4. Confidence / limitations of this review

| Item | Confidence | Limitation |
|---|---|---|
| Hard physical stops | **High** | Exact Kd/eDNA-km in unnamed cells must be measured |
| Dangerous-claim ranking | **High** | Harm mix is judgment; ESA/public-health blast radius is site-specific |
| Numeric FishAI GO thresholds | **Low** | Quality marked them HYPOTHESIS; we **did not** adopt them as observatory facts |
| Sibling wedge ranking | **n/a** | Founder lock still required |
| Human peer review | **Invalid as sign-off** | Simulated reviewer *arguments* only |
| Legal | **Not legal advice** | Counsel for DAS waveforms, eDNA sequences, tags |

---

## 5. Recommended decision

1. **Founder / product:** Do not ship observatory, digital-twin-of-life, or satellite-fish-finder language. Keep MVP at one locked wedge (still UNRESOLVED).  
2. **Validation:** Adopt `observatory/validation_protocol.md` as the ceiling for any multi-modal or global claim; FishAI `artifacts/quality_and_validation/` remains the wedge protocol. **Stricter gate wins.** Do not assign T3–T6 without V1–V9.  
3. **Physics:** Treat `PHYSICALLY_UNLIKELY` rows as **tier 0** until a measurement plan exists. Hardware is out of FishAI v0.  
4. **Red team:** Bind `observatory_red_team_01.md` + existing FishAI risk register. Re-review on first product sentence that says “life layer.”  
5. **All agents:** Unsampled cells = **UNKNOWN**. No confidence in sparse cells. No training.  
6. **Humans before any biological user output:** fisheries scientist; add acoustician and/or molecular ecologist if those modalities appear.

---

## 6. Rejected alternatives

| Alternative | Why rejected |
|---|---|
| Global occupancy inpaint from SST/chl | PX-01/02/15; RT-OBS-05/09/15 |
| AIS foundation model for abundance | RT-OBS-04; rights; Harley 2001 |
| eDNA dashboard as nowcast GPS | PX-05/06 |
| DAS EEZ fish map | PX-09/10 |
| Pop-up tag “live tracks” | PX-07 |
| Random-split leaderboard as validation | RT-OBS-07 |
| Disclaimer under a complete heatmap | Does not bound the claim |
| “We’ll fuse it later” | Fusion inflation |
| Using this handoff as domain sign-off | Explicitly not |

---

## 7. Follow-ups

- Diff new product/marine/geo copy against RT-OBS-01…15 and PX-01…20.  
- If wedge locks: run FishAI Gates 1–8 **and** observatory V1–V9 on **that target only**. Do not promote CSV example rows to T3+.  
- Founder names human reviewer seats.  
- Do not stand up an observatory data lake.  
- Quality agent: hypothesized numeric GOs remain hypotheses.  
- Re-open if anyone proposes a foundation ocean-life model.

---

## 8. Artifacts produced

All under `/Users/wijeratne/dev/fishai/observatory/`:

| File | Role |
|---|---|
| `validation_protocol.md` | Evidence contract; UNKNOWN; T0–T6 mapped to V1–V9; T6 bar |
| `scientific_red_team_reports/observatory_red_team_01.md` | Hunt list; dangerous claims; three-reviewer reject list |
| `physics_feasibility_reports/physical_limits.md` | Modality physics; PHYSICALLY_UNLIKELY register |
| `artifacts/validation_redteam/agent_handoff.md` | This file |

---

## 9. Residual reviewer questions

- Is a public biological map ever worth the leakage?  
- Public-health: oyster stress vs Vp?  
- DAS: can detectors run without localizable listed-species waveforms?  
- Minimum n for blocked CV — still a human/data question.  
- After interviews: does any buyer **want** observatory, or only a 72 h brief?

---

## 10. Next experiment (smallest falsifier)

**Do not train.**

1. Coverage honesty on one AOI: fraction of cells with same-day valid ocean-color/SST.  
2. Effort null on public occurrences: port-distance vs SST/chl.  
3. B12 vs any proposed nowcast on a held-out year.  
4. If oyster path: air×tide vs SST-only on 2021-type days (marine-domain E1).

**Stop if** the experiment needs public hotspots, AIS labels, closure labels, or painted UNKNOWN cells.

---

**Handoff complete.** Parent payload: physical hard stops (§1.A); most dangerous false claims (§1.B); minimum validation for **T6** (§1.C). Observatory biology is **not operational**. Beating a pretty map is not validation. **UNKNOWN: not enough evidence** is a first-class output.
