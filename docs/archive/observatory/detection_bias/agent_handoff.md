# Agent handoff — Detection Probability, Absence, and Observation-Bias Engine

**Agent:** DETECTION_PROBABILITY_ABSENCE_AND_OBSERVATION_BIAS_ENGINE  
**Date:** 2026-09-18  
**Project:** Global Saltwater Life Observatory / FishAI  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/detection_bias/` **only**  
**Did not write:** `globe/**`, commercial `artifacts/**`, ingest, weights.

**Read:** `quality_and_validation`, `marine_domain`, `scientific_red_team`, `observatory/observation_modality_catalog.md`, plus observatory output contract, validation protocol, ocean_model_comparison §2.3, W1 GT relabel.

**State:** Design only. No training. Missing records are not absences.

---

## 1. Executive finding

Every biological record must carry **exactly one** of:

`PRESENT_OBSERVED` | `PRESENT_INFERRED` | `NOT_DETECTED` | `TRUE_ABSENCE_SUPPORTED` | `NO_OBSERVATION` | `DATA_UNAVAILABLE`

Unsampled cells, cancelled charters, un-walked farm-days, clouded satellite pixels, and empty OBIS queries are **`NO_OBSERVATION`** (globe: **`DATA_GAP` / UNKNOWN hatch**). Copy must never say “absent.”

`NOT_DETECTED` requires documented effort &gt; 0. `TRUE_ABSENCE_SUPPORTED` is rare and high-bar (repeats + \(p\) + corroboration). GBIF/OBIS are **presence-only**. Occupancy models are **not allowed** on occurrence-only dumps.

**W1:** farm logs are the ops-stress detection process. **WA DOH closures are not oyster occupancy, mortality, or absence.** They are harvest-legality constraints. Sensors and SST do not observe oyster death. Heat-kill can be visually obvious on emersion while **delayed mortality runs to day 30**, so a 72 h clean walk is `NOT_DETECTED`, not proof of no event.

**W2:** completed-trip zeros are `NOT_DETECTED`; **no trip is `NO_OBSERVATION`**.  
**W3:** trap CPUE is hyperstable and catchability-confounded; **AIS is not inshore lobster effort**.

\(p(\mathrm{detect})=f(\mathrm{method},\ \mathrm{effort},\ \mathrm{species},\ \mathrm{life\ stage},\ \mathrm{depth},\ \mathrm{clarity},\ \mathrm{weather},\ \mathrm{sensor\ quality},\ \mathrm{observer\ skill},\ \mathrm{habitat},\ \mathrm{time\ of\ day},\ \mathrm{season},\ \mathrm{behavior})\) is specified, **not fitted**.

---

## 2. Evidence table

| Finding | Why it matters | Evidence | Confidence |
| --- | --- | --- | --- |
| Occupancy \(\neq\) detection; single-visit presence-only cannot identify both | Forbids OBIS zeros | MacKenzie et al. 2002; Lahoz-Monfort et al. 2014; `ocean_model_comparison.md` §2.3 | High |
| OBIS/GBIF are effort-biased presence | Empty cell ≠ unused habitat | Webb et al. 2010; modality catalog OBIS notes; RT-OBS-03 | High |
| Unfished cells ≠ Chinook negatives | Honest metric = visited cells | Quality `validation_protocol.md` effort rule | High |
| DOH ≠ oyster ops GT | Wrong process; BLOCKER if used as \(y\) | `ground_truth_relabel_W1.md`; WAC 246-282-006; red team | High |
| 2021 kill is air×emersion; delayed deaths to ~d30 | Walk \(p\) vs label lag | Raymond et al. 2022; George et al. preprint/NOAA; marine_domain | High (mech.); no FishAI \(p\) |
| CPUE hyperstability | High catch ≠ high \(N\) | Harley et al. 2001; ASMFC 2025 | High |
| Inshore AIS ≠ lobster \(E\) | Carriage ≥65 ft; confidential trackers | 33 CFR 164.46; Addendum XXIX; red team | High |
| eDNA hit = molecules at filter | Transport/decay; contamination | Harrison 2019; Andruszkiewicz 2019; Darling et al. 2021 | High |
| Tags = selected subset | Empty tag map ≠ stock absence | Sequeira et al. 2021 | High |
| Satellite optical \(p\)=0 below first optical depth / under cloud | Cloud ≠ biological zero | Modality catalog hard limits; Gordon & McCluney | High |
| No FishAI \(p\) surface exists | Do not print calibrated probabilities | Empty training; Gate 1 fail | Certain |

---

## 3. Source / license table

No datasets ingested. Citations only. Rights remain `UNKNOWN` until DATA_RIGHTS.

| Source | Use | Note |
| --- | --- | --- |
| MacKenzie et al. 2002 *Ecology* | Occupancy algebra | Cite only |
| Harley et al. 2001 *CJFAS* | Hyperstability | Cite only |
| Raymond et al. 2022 *Ecology* | W1 emersion heat | Cite only |
| George et al. delayed mortality | Day-30 lag | Cite only |
| Sequeira et al. 2021 *MEE* | Tag bias | Cite only |
| Harrison / Andruszkiewicz eDNA | Decay/transport | Cite only |
| ICES CRR 344; Korneliussen | Acoustic ID limits | Cite only |
| Phillips et al. 2009 | Target-group background | Background ≠ absence |
| 33 CFR 164.46; NMFS 06-101 | AIS/VMS | Law / policy |
| WA DOH growing areas | Constraint overlay | Never \(y\) |
| Sibling FishAI artifacts | Alignment | Read-only |

---

## 4. Confidence and limitations

| Area | Confidence | Limitation |
| --- | --- | --- |
| Six-state contract | High as design | Not implemented in API/globe yet |
| Banned training list | High scientifically | Cannot stop a future agent except by this spec |
| Numeric cumulative-\(p\) ≥ 0.95 for true absence | **Low** — hypothesis | Not calibrated |
| Method-card \(p\) ranks | Medium (literature) | No local estimates |
| Globe texture names | Medium | Specified as contract; `globe/` not edited |
| Wedge lock | N/A | UNRESOLVED |

---

## 5. Recommended decision

1. Adopt the six-state enum as **mandatory** on biological records (fixtures already demonstrate it).  
2. Treat this folder as **APPROVED_AS_DESIGN**, not **APPROVED_FOR_TRAINING**.  
3. Globe implementers: Unknown hatch = `NO_OBSERVATION`; **separate** encodings for `NOT_DETECTED` vs `TRUE_ABSENCE_SUPPORTED`.  
4. W1 product path (if locked): farm logs = detection trials; DOH = constraint module.  
5. Do not open occupancy fitting on GBIF/OBIS.

### Return values (requested)

#### Six-state contract

| State | Contract |
| --- | --- |
| `PRESENT_OBSERVED` | Contemporaneous organism/tracer record. Not \(N\). |
| `PRESENT_INFERRED` | Named model. Never stored as observed. |
| `NOT_DETECTED` | Effort &gt; 0 ran; target not recorded; absence **not** proven. |
| `TRUE_ABSENCE_SUPPORTED` | Repeats + detection model + corroboration at stated grain. Rare. |
| `NO_OBSERVATION` | Nobody looked. **Unknown, not zero.** UI: never “absent.” Globe: `DATA_GAP` hatch. |
| `DATA_UNAVAILABLE` | Exists or might exist but unusable (rights, fail, embargo, latency, withhold). Gap + reason. |

Transitions: `observation_state_enum.md` §3. Likelihood: only observed and not-detected are Bernoulli trials.

#### Top banned training practices

1. Naive presence/absence from occurrence-only DBs.  
2. GBIF/OBIS empty cells as absences.  
3. Unsampled / unfished / no-trip / un-walked / cloudy cells as \(y=0\).  
4. DOH/NSSP closures as oyster mortality or occupancy labels.  
5. AIS/VMS as abundance, occupancy, or inshore lobster effort.  
6. SST/chl as \(y\) or as proof of presence.  
7. Uniform geographic pseudo-absences; N-mixture census on citizen data.  
8. Sensor-threshold circular labels (SST ≥ 19 °C ⇒ dead).  
9. As-of leakage (delayed-mode, pending eDNA as live non-detects).  
10. Trap CPUE or charter zeros-without-a-trip as \(N=0\).

Full list: `training_policy.md` BAN-1…BAN-20.

#### W1 implication — farm logs vs DOH closures

**Farm logs** (walk/inspect: mortality, workability, intervention) are the **only** ops-stress detection process. Walked + event = `PRESENT_OBSERVED`; walked + none = `NOT_DETECTED` (delayed mortality may still appear through day 30); not walked = `NO_OBSERVATION`.

**DOH closures** answer **harvest legally open?** They must be shown as official context and **must not** be `observation_state` or \(y\). Open+heat-kill and closed+healthy animals are both possible. Combining them into one color is a food-safety impersonation BLOCKER.

Sensors = environment. Satellite SST = skin temperature, not body T, not death. HAB microscope = phytoplankton, not oyster occupancy.

---

## 6. Rejected alternatives

| Alternative | Why |
| --- | --- |
| Binary present/absent | Drops unknown vs non-detect vs supported unoccupied |
| Default absent when DB empty | Manufactures range edges |
| One globe color for all negatives | Users read hatch as “no fish” |
| Occupancy-on-OBIS v0 | Unidentifiable \(p\); RT-OBS-03 |
| W1 SST mortality label | Mechanism false; circularity |
| W2 EEZ occupancy from charters | Sampling ≠ stock |
| W3 AIS effort surface | Wrong fleet |

---

## 7. Follow-ups

1. Globe agent: implement hatch vs surveyed-negative vs supported-absence (this agent did not touch `globe/`).  
2. API: add `observation_state` to the observation kernel.  
3. Founder/wedge: if W1 locks, DUA farm-log schema with walk yes/no, bag n, detection_lag.  
4. Human shellfish + NSSP reviewer still required before any oyster brief.  
5. Do not train.

---

## 8. Artifacts generated

All under `/Users/wijeratne/dev/fishai/observatory/detection_bias/`:

| File | Role |
| --- | --- |
| `README.md` | Index + binding rules |
| `observation_state_enum.md` | Definitions, transitions, UI copy |
| `p_detect_model_spec.md` | Hierarchical \(\psi,p\); features; leakage; as-of |
| `method_bias_cards.md` | Ten method cards |
| `training_policy.md` | Bans; GBIF/OBIS; occupancy gates; pseudo-absence |
| `w1_oyster_detection.md` | Walk vs sensor vs SST vs HAB; emersion; day-30 lag; DOH split |
| `w2_chinook_and_w3_lobster_notes.md` | Zeros vs no trip; hyperstability; AIS |
| `fixture_records.csv` | Synthetic examples of all six states |
| `agent_handoff.md` | This file |

---

## 9. Red-team?

**Yes.** Highest remaining attacks: (i) UI still says “absent” on hatch; (ii) later agent joins OBIS with `fillna(0)`; (iii) DOH merged back into W1 \(y\); (iv) AIS effort for lobster; (v) promoting `PRESENT_INFERRED` to observed in a globe shader.

This agent is **not** a qualified human domain reviewer.

---

## 10. Suggested next experiment (no ingest, no training)

Paper protocol: take three fixture rows (`FIX-NO-05` OBIS empty, `FIX-ND-02` charter zero, `FIX-NO-02` cancelled trip) and confirm any proposed schema/UI treats them as **three different** states. If a mock map colors the first two the same, fail the mock.

W1: on a consenting lease (later), log walk yes/no separately from DOH open/closed for 30 days including one spring-tide heat window; score how often they disagree. Predicted: disagreement is common — that is the point.

**Stop:** any experiment that needs public hotspots, AIS labels, or closure labels as biology.

---

**Handoff complete.** Parent return: six-state contract (table §5); top bans (list §5); W1 farm logs vs DOH (paragraph §5).
