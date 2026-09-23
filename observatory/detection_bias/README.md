# Detection Probability, Absence, and Observation-Bias Engine

**Program:** Global Saltwater Life Observatory (FishAI scientific blueprint)  
**Agent:** DETECTION_PROBABILITY_ABSENCE_AND_OBSERVATION_BIAS_ENGINE  
**Date / access date for cited URLs:** 2026-09-18  
**Write path:** `/Users/wijeratne/dev/fishai/observatory/detection_bias/`  
**Status:** Design only. **No model training. No ingest.**  
**Observatory state:** `STATE_1_FRAMEWORK`  
**Commercial wedge:** UNRESOLVED / paused. This folder does **not** expand the 1×1×1×1 product.

A missing record is **not** an absence. Unsampled ocean is **not** empty ocean. GBIF/OBIS points are **presence**, not presence/absence.

---

## Why this engine exists

Every biological cell the observatory might later color is the product of **occupancy** (was the organism there?) and **detectability** (would this method, with this effort, have recorded it?). Conflating those two processes manufactures false zeros, fake range edges, and “AI abundance” maps.

This engine is the contract that:

1. Types every biological record into **exactly one of six observation states**.  
2. Specifies a hierarchical occupancy / \(p(\mathrm{detect})\) design that **may not be fitted** until rights, labels, and as-of snapshots exist.  
3. Documents method-specific bias for the ten required observing families.  
4. Bans naive presence/absence training.  
5. Applies the contract to W1 (Pacific oyster), W2 (Chinook charter), and W3 (GOM lobster) as **illustrative rows**, not product locks.

**Companion reads (do not overwrite):**  
`../observation_modality_catalog.md` · `../user_output_contract.md` · `../validation_protocol.md` · `../scientific_red_team_reports/observatory_red_team_01.md` · `../ocean_model_comparison.md` §2.3 · `/Users/wijeratne/dev/fishai/artifacts/quality_and_validation/` · `/Users/wijeratne/dev/fishai/artifacts/marine_domain/` · `/Users/wijeratne/dev/fishai/artifacts/scientific_red_team/`

**Do not write:** `globe/**`, commercial `artifacts/**`, ingest pipelines, trained weights.

---

## The six-state contract (normative)

| Code | Meaning in one line | Globe / UI implication |
| --- | --- | --- |
| `PRESENT_OBSERVED` | A contemporaneous observation of the organism (or its image, sound, DNA, calibrated backscatter, or catch in gear) exists. | Observation glyph. Never a filled “abundance” choropleth. |
| `PRESENT_INFERRED` | A named model/assumption estimates occupancy or habitat use. **Not** an observation. | `MODEL-INFERRED` texture, distinct from observed. |
| `NOT_DETECTED` | A **documented sample/survey** was taken; the target was not recorded; **absence is not proven**. | Surveyed-negative mark. **Not** the Unknown hatch. **Not** “absent.” |
| `TRUE_ABSENCE_SUPPORTED` | Designed repeated effort + a detection model + independent corroboration support occupancy ≈ 0 at the stated grain. Rare. | Distinct supported-absence encoding. High bar. |
| `NO_OBSERVATION` | No sample exists in this cell × depth × time × method. **Unknown, not zero.** | **`DATA_GAP` / UNKNOWN hatch.** Copy must never say “absent.” |
| `DATA_UNAVAILABLE` | A sample or product may exist, but it is not usable (rights, embargo, sensor fail, latency, withheld). | Gap badge **with reason**, not the same as never sampled. |

Definitions, transitions, and forbidden copy: [`observation_state_enum.md`](observation_state_enum.md).

**Default for unsampled ocean, unvisited charter cells, and farms not walked:** `NO_OBSERVATION`.

---

## Detection probability (not fitted)

\[
p(\mathrm{detect}) = f(\mathrm{method},\ \mathrm{effort},\ \mathrm{species},\ \mathrm{life\ stage},\ \mathrm{depth},\ \mathrm{water\ clarity},\ \mathrm{weather},\ \mathrm{sensor\ quality},\ \mathrm{observer\ skill},\ \mathrm{habitat},\ \mathrm{time\ of\ day},\ \mathrm{season},\ \mathrm{behavior})
\]

Hierarchical occupancy (\(\psi\), \(p\)) design, features, leakage, and as-of rules: [`p_detect_model_spec.md`](p_detect_model_spec.md).

**Knowable today (2026-09-18):** the **form** of \(f\), literature ranges, and which covariates are missing. **Not knowable:** a calibrated FishAI \(p\) surface. Do not print three-decimal detection probabilities.

---

## Files in this folder

| File | Role |
| --- | --- |
| `README.md` | This index and the six-state summary |
| `observation_state_enum.md` | Definitions, transitions, UI copy, globe encoding |
| `p_detect_model_spec.md` | Occupancy / \(p(\mathrm{detect})\) design; features; leakage; as-of |
| `method_bias_cards.md` | One card per required method family |
| `training_policy.md` | Banned practices; GBIF/OBIS; occupancy gates; pseudo-absence |
| `w1_oyster_detection.md` | Farm walk vs sensor vs SST vs HAB scope; emersion; delayed mortality |
| `w2_chinook_and_w3_lobster_notes.md` | Charter zeros vs no trip; trap hyperstability; AIS ≠ inshore effort |
| `fixture_records.csv` | Synthetic examples of all six states |
| `agent_handoff.md` | Return payload for the parent orchestrator |

---

## Binding rules (copy onto every downstream agent)

1. **Never treat missing records as absences** unless a justified pseudo-absence **or** a detection model on designed effort is used — and then label the row `NOT_DETECTED` or `TRUE_ABSENCE_SUPPORTED`, never `NO_OBSERVATION`.  
2. **GBIF / OBIS / iNaturalist / unstructured occurrence DBs = presence-only.** They do not generate zeros.  
3. **A model is not an observation.** `PRESENT_INFERRED` cannot be stored as `PRESENT_OBSERVED`.  
4. **Catch ≠ abundance.** CPUE, AIS, and vessel density are not \(N\) and are not \(p(\mathrm{present})\).  
5. **WA DOH / NSSP closures are not oyster occupancy or mortality.** They are harvest-legality **constraints**.  
6. **Charter no-trip ≠ zero Chinook.** Trap CPUE can stay high while biomass falls (hyperstability). Inshore lobster AIS is not effort.  
7. **As-of honesty:** `published_at_utc ≤ issued_at_utc` on every covariate used in \(\psi\) or \(p\).  
8. **No training in this iteration.** Spec only.

---

## Globe / UI implication (owned here as a contract; files live under `globe/` when that agent implements)

Do **not** implement globe files from this agent.

| Observation state | Required visual-truth mapping |
| --- | --- |
| `NO_OBSERVATION` | `DATA_GAP` / **UNKNOWN hatch**. Successful product state. |
| `DATA_UNAVAILABLE` | Gap + **reason chip** (rights / fail / embargo / stale). |
| `NOT_DETECTED` | Surveyed-negative. Different from hatch. Must not read as “species absent.” |
| `TRUE_ABSENCE_SUPPORTED` | Separate encoding from `NOT_DETECTED`. Caption must include the support (repeats, \(p\), corroboration). |
| `PRESENT_OBSERVED` | Evidence-class glyph (`DIRECTLY OBSERVED` / `REMOTELY DETECTED` / `SURVEY-DERIVED` / `TAG/TELEMETRY-DERIVED` / `OPERATIONALLY OBSERVED`). |
| `PRESENT_INFERRED` | `MODEL-INFERRED` texture. Never the same hue/fill as observed. |

Never: red = fish are here; blank = none; interpolating hatch into a smooth occupancy field.

---

## Wedge illustrations (not locks)

| Wedge | Detection lesson |
| --- | --- |
| **W1** Pacific oyster × WA farm | Farmed animals are **planted**. Occupancy of the lease is operational knowledge. Detectability of **heat-kill** is high on an emerged walk, **low** for delayed mortality to ~day 30, **zero** from SST pixels or DOH closures. |
| **W2** Chinook × CA/OR charter | Zeros on **completed trips with effort** are `NOT_DETECTED` (encounter), not stock absence. Cancelled / unfished cells are `NO_OBSERVATION`. |
| **W3** American lobster × GOM | Trap CPUE is catchability-confounded and **hyperstable**. AIS carriage does not cover typical inshore boats. Dealer pounds without soak are not a detection process. |

---

## What this cluster did not do

No bulk download, no GBIF/OBIS cache, no occupancy fit, no \(p\) calibration, no globe textures, no commercial brief copy, no claim that a global detection surface exists.
