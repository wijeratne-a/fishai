# Observation-state enum

**Date:** 2026-09-18  
**Status:** Binding on observatory biological records, APIs, fixtures, and (later) globe encodings.  
**No training. No ingest.**  
**Every biological record carries exactly one of the six codes below.**

This enum is **orthogonal** to the user-output contract classes (`DIRECTLY OBSERVED` … `UNKNOWN/INSUFFICIENT DATA`) and to species support tiers T0–T6. A record can be `PRESENT_OBSERVED` + `DIRECTLY OBSERVED` + T5, or `NO_OBSERVATION` + `UNKNOWN/INSUFFICIENT DATA` + T0. Mixing those ladders into one color is a contract break.

Related: `../user_output_contract.md`, `../validation_protocol.md` §1.3 UNKNOWN policy, `globe/README.md` (Unknown map is first-class; **do not edit globe from this folder**).

---

## 0. Non-negotiable sentence

**Missing data are not absences.**  
`NO_OBSERVATION` and `DATA_UNAVAILABLE` must never be stored, trained, plotted, or spoken as “absent,” “zero occupancy,” “not present,” or “species not found.”

The only states that may appear in a detection-history likelihood as a Bernoulli trial are `PRESENT_OBSERVED` (success) and `NOT_DETECTED` (failure **conditional on a known effort process**). `TRUE_ABSENCE_SUPPORTED` is a **derived occupancy conclusion**, not a raw trial.

---

## 1. The six states

### 1.1 `PRESENT_OBSERVED`

**Definition.** A contemporaneous record that the **organism, or a direct tracer of that organism**, was registered by a named method in a named spatiotemporal grain.

Direct tracers allowed: image of the organism; expert-validated catch in gear; calibrated acoustic backscatter **with an independent ID prior**; a DNA assay hit **at the filter** (molecules, not a GPS pin); a tag/telemetry fix of **that individual**; a farm count of live or dead oysters on inspected gear.

**Required fields.** `method`, `observed_at_utc`, `published_at_utc`, `effort` (or explicit `effort_unknown`), `taxon` + life stage, `depth_precision`, `evidence_class`, `legal_privacy_tier`.

**Output class (typical).** `DIRECTLY OBSERVED` | `REMOTELY DETECTED` | `SURVEY-DERIVED` | `TAG/TELEMETRY-DERIVED` | `OPERATIONALLY OBSERVED`.

**Is not.** Abundance; a census; proof the rest of the cell is occupied; a license to map listed-species coordinates publicly.

**UI copy (allowed).** “Observed [taxon] by [method] at [grain], [time]. This is not a count of all animals.”  
**UI copy (forbidden).** “The stock is here.” “Abundance high.” “Safe to harvest.”

---

### 1.2 `PRESENT_INFERRED`

**Definition.** Occupancy, habitat use, or relative encounter is **estimated** from a named model or mechanistic assumption. No contemporaneous observation of the organism is claimed.

**Required fields.** `model_or_baseline_version`, `assumptions[]`, `training_data_cutoff_utc` (or `none — expert rule`), `extrapolation_flag`, `uncertainty_rationale`, capability class `Inferable today` or weaker.

**Output class.** `MODEL-INFERRED` or `FORECAST` or `HYPOTHETICAL/RESEARCH MODE`. **Never** `DIRECTLY OBSERVED`.

**Is not.** A detection. A label for occupancy training unless a human-signed protocol says the inference is being used as a **prior**, not as \(y\).

**UI copy (allowed).** “Model-inferred occupancy / habitat / encounter. Not an observation.”  
**UI copy (forbidden).** “Detected.” “Confirmed present.” “Seen on satellite.” (unless the satellite actually imaged the organism — that is `PRESENT_OBSERVED` / `REMOTELY DETECTED`.)

**W1 note.** SST-based “oysters stressed” is at best `PRESENT_INFERRED` **stress**, and is usually **Low/None** because SST ≠ intertidal body temperature. It is **never** oyster occupancy (the farm already knows the animals are planted).

---

### 1.3 `NOT_DETECTED`

**Definition.** A **designed or documented observation process ran** (survey station, camera soak, eDNA filter, charter trip with angler-hours, trap-haul with soak, farm walk of named bags). The target taxon was **not recorded**. Occupancy remains unidentified: \(z\) may be 1 with probability \(1-p\), or 0.

**Required fields.** `method`, `effort` **known and > 0**, `protocol_id` or equivalent, `observed_at_utc`, detection covariates used or listed as missing.

**Is not.** True absence. Unfished water. A cancelled trip. A cell with no OBIS points. A growing-area “closed.”

**UI copy (allowed).** “Not detected on this [survey/trip/walk] given [effort]. Absence is not established.”  
**UI copy (forbidden).** “Absent.” “None in this area.” “Zero fish in the cell.” “Oysters gone.”

**Globe.** A surveyed-negative mark (e.g. open symbol, hatched **only inside the sampled footprint**). Must not use the global `DATA_GAP` hatch — that hatch is reserved for `NO_OBSERVATION`.

---

### 1.4 `TRUE_ABSENCE_SUPPORTED`

**Definition.** Occupancy at the stated grain is supported as ≈ 0. This is a **conclusion from a detection model plus corroboration**, not a single zero.

**Minimum support (all of):**

1. **Repeated visits or spatially exhaustive design** in a closed (or immigration-negligible) window.  
2. A **documented detection process** with estimated or bounded \(p\), such that cumulative detection probability \(1-(1-p)^K\) meets a **pre-registered** threshold (hypothesis: ≥ 0.95; lock after first protocol — **not** a FishAI-calibrated number today).  
3. **Independent corroboration** appropriate to the taxon (examples: lease harvested and fallow; intertidal mosaic photographed with no live oysters on inspected cultch; repeated qPCR non-detects **and** hydrodynamic kernel implying local source should have been hit; structured survey with availability-bias correction for diving taxa).  
4. Written **limitations**: grain, window, life stage, method. Global or EEZ-scale “absent” is **out of contract**.

**Output class.** `SURVEY-DERIVED` or `MODEL-INFERRED` with Category D language (“supported unused / unoccupied at grain”), **never** Category A census of zeros.

**Is not.** Default for empty database queries. Not the complement of GBIF.

**UI copy (allowed).** “Supported unoccupied at [grain] given [K visits, method, p bound, corroboration]. Not a regional extirpation claim.”  
**UI copy (forbidden).** “Proven absent from the ocean.” “No oysters in Washington.” Bare word **“absent”** without the support clause.

**Globe.** Distinct from `NOT_DETECTED`. If the encoding is too similar, users will collapse the two. Caption **must** travel with the fill.

**Rarity.** Expect this state to be **uncommon** in a global observatory. Farm fallow beds and post-harvest empty gear are the honest W1 cases. Wild mobile fish at 10 km × 48 h almost never qualify.

---

### 1.5 `NO_OBSERVATION`

**Definition.** No observation process of the claimed method occurred in this cell × depth band × time window. The database is silent because **nobody looked** (or the look is outside the claimed grain).

**Includes.** Unsurveyed H3 cells; charter cells with **no trip**; days a farm was **not walked**; depths below the optical/acoustic instrument; nights with no PAM duty cycle; taxa never in the primer set; years before a program started.

**Output class.** `UNKNOWN/INSUFFICIENT DATA`.

**Is not.** Evidence of absence. A training zero. A “background point” unless explicitly sampled as **background** (see `training_policy.md`) and still **not** labeled absence.

**UI copy (allowed).**  
- “No observation in this cell at this time.”  
- “Not sampled.”  
- “Unknown — insufficient data.”  
- “Data gap.”

**UI copy (forbidden — hard ban).**  
- “Absent”  
- “Not present”  
- “None found”  
- “Zero occupancy”  
- “Species not recorded here” (this last sentence is true of the **database** and is routinely misread as biology; do not use it in UI. Use “No observation.”)

**Globe.** **`DATA_GAP` / UNKNOWN texture (Mode 9 hatch).** This is a successful product state (`globe/README.md` law 2; observatory red team RT-OBS-09). Filling, interpolating, or GANning this hatch into occupancy is a BLOCKER.

---

### 1.6 `DATA_UNAVAILABLE`

**Definition.** An observation or product **may exist**, but FishAI cannot lawfully or technically use it **as of** the issuance clock.

**Includes.** Rights `UNKNOWN` / noncommercial / confidential VMS; embargoed sea-sampling; fouled or failed sensor; missing calibration; delayed-mode file not yet published; partner declined DUA; PAM on a navy range; listed-species coordinates `NEVER_PUBLISH`; AIS switch-off; Maine harvester microdata not licensed; RecFIN salmon microdata not in hand.

**Output class.** `UNKNOWN/INSUFFICIENT DATA` plus a **reason code**.

**Reason codes (closed list, extend only by spec revision):**

| Code | Meaning |
| --- | --- |
| `RIGHTS` | License / DUA / confidentiality |
| `EMBARGO` | Exists but not yet public at `issued_at` |
| `SENSOR_FAIL` | Instrument down, fouled, out of cal |
| `WITHHELD_SENSITIVE` | Ecological / privacy withhold |
| `LATENCY` | Sample taken; result not available yet (e.g. metabarcoding batch) |
| `FORMAT_UNUSABLE` | Corrupt, undocumented, no time/depth |
| `NOT_INGESTED_BY_POLICY` | Identified, deliberately not pulled (this iteration: all bulk sources) |

**UI copy (allowed).** “Data unavailable ([reason]). Not the same as unsampled; not absence.”  
**UI copy (forbidden).** “Absent.” Hiding the reason so it looks like `NO_OBSERVATION`.

**Globe.** Gap **with reason chip**. Different from the unmarked Unknown hatch. A rights hole is not an ecological desert.

---

## 2. Mapping to output class and visual truth

| Observation state | Typical output class | Globe / visual-truth (contract for `globe/` implementers) |
| --- | --- | --- |
| `PRESENT_OBSERVED` | Direct / remote / survey / tag / operational | Observation glyph; coarsen if sensitive |
| `PRESENT_INFERRED` | `MODEL-INFERRED` / `FORECAST` / research | Inferred texture; **never** same as observed |
| `NOT_DETECTED` | `SURVEY-DERIVED` or `OPERATIONALLY OBSERVED` (a zero **trial**) | Surveyed-negative encoding |
| `TRUE_ABSENCE_SUPPORTED` | `SURVEY-DERIVED` or `MODEL-INFERRED` | Supported-absence encoding, caption-mandatory |
| `NO_OBSERVATION` | `UNKNOWN/INSUFFICIENT DATA` | **`DATA_GAP` / UNKNOWN hatch** |
| `DATA_UNAVAILABLE` | `UNKNOWN/INSUFFICIENT DATA` | Gap + reason; not hatch-as-biology |

**Never share a colormap** between `NOT_DETECTED` and `TRUE_ABSENCE_SUPPORTED`, or between either and `NO_OBSERVATION`.

---

## 3. Allowed transitions

States are **time-stamped**. History is append-only. A cell’s **current** state may change; past records do not.

```text
                    ┌──────────────────────┐
                    │   DATA_UNAVAILABLE   │
                    └──────────┬───────────┘
                               │ access restored / fail diagnosed
                               ▼
┌─────────────┐  sample taken   ┌──────────────┐
│NO_OBSERVATION│ ─────────────► │ NOT_DETECTED │
└──────┬──────┘                  └──────┬───────┘
       │ observation                    │ later detect
       ▼                                ▼
┌─────────────────┐              ┌─────────────────┐
│PRESENT_OBSERVED │◄─────────────│  (same cell)    │
└────────┬────────┘              └─────────────────┘
         │
         │ model-only path (never upgrades observed)
         ▼
┌──────────────────┐     high-bar protocol
│ PRESENT_INFERRED │ ─ ─ ─ (does not create TRUE_ABSENCE)
└──────────────────┘

NOT_DETECTED ──[K repeats + p model + corroboration]──► TRUE_ABSENCE_SUPPORTED
TRUE_ABSENCE_SUPPORTED ──[new detection]──► PRESENT_OBSERVED
PRESENT_INFERRED ──[real observation]──► PRESENT_OBSERVED
```

### 3.1 Allowed

| From | To | Condition |
| --- | --- | --- |
| `NO_OBSERVATION` | `PRESENT_OBSERVED` | A qualifying observation arrives |
| `NO_OBSERVATION` | `NOT_DETECTED` | A documented effort > 0 ran and recorded a non-detect |
| `NO_OBSERVATION` | `DATA_UNAVAILABLE` | We learn a sample exists but cannot use it |
| `NO_OBSERVATION` | `PRESENT_INFERRED` | A **named** model is issued for that grain (research); still not an observation |
| `DATA_UNAVAILABLE` | any of the four “looked or modeled” states | Reason cleared; as-of clock respected |
| `DATA_UNAVAILABLE` | `NO_OBSERVATION` | We learn **no** sample existed (rights hole was hypothetical) |
| `NOT_DETECTED` | `PRESENT_OBSERVED` | Subsequent detection in window, or QA reversal of a false negative |
| `NOT_DETECTED` | `TRUE_ABSENCE_SUPPORTED` | §1.4 bar met; versioned protocol |
| `TRUE_ABSENCE_SUPPORTED` | `PRESENT_OBSERVED` | Recolonization / new detection |
| `TRUE_ABSENCE_SUPPORTED` | `NOT_DETECTED` | Protocol invalidated (p overestimated); demote, do not hide |
| `PRESENT_INFERRED` | `PRESENT_OBSERVED` | Independent observation |
| `PRESENT_INFERRED` | `NOT_DETECTED` | A real survey ran; inference is no longer the current state (keep inference as a **layer**, not the record state) |
| `PRESENT_OBSERVED` | `NOT_DETECTED` | **Only** as a **new** time slice after the observation window (e.g. next survey). Do not rewrite history. |

### 3.2 Forbidden

| Transition | Why |
| --- | --- |
| `NO_OBSERVATION` → `TRUE_ABSENCE_SUPPORTED` in one step | No effort, no \(p\), no corroboration |
| `NO_OBSERVATION` → `NOT_DETECTED` without effort > 0 | Empty query ≠ survey |
| `PRESENT_INFERRED` → `PRESENT_OBSERVED` by relabel | Models are not observations |
| `PRESENT_OBSERVED` → `TRUE_ABSENCE_SUPPORTED` without a later designed survey | You cannot absent-out a detection in the same window |
| GBIF miss → any negative state | Presence-only database |
| `DATA_UNAVAILABLE` → `NOT_DETECTED` | Unusable data are not a clean non-detect (contamination of \(p\)) |
| Any state → `PRESENT_OBSERVED` from SST, AIS, chlorophyll, or DOH closure | Category E / wrong process |

---

## 4. What may enter a likelihood

| State | Occupancy \(z\) | Detection trial \(y\) | Training use |
| --- | --- | --- | --- |
| `PRESENT_OBSERVED` | 1 | 1 | Yes, as detection success (with effort) |
| `NOT_DETECTED` | unknown | 0 **if** effort known | Yes, as detection failure |
| `TRUE_ABSENCE_SUPPORTED` | ≈ 0 (derived) | used to **fit** \(p\) then infer \(z\) | Yes, as occupancy conclusion, versioned |
| `PRESENT_INFERRED` | prior / covariate | **no** | Prior or feature only; **not** \(y\) |
| `NO_OBSERVATION` | unknown | **no trial** | **Banned** as 0/1 |
| `DATA_UNAVAILABLE` | unknown | **no trial** | **Banned** as 0/1 |

---

## 5. QA phrases for product/globe copy decks

Pass this checklist before any string ships:

1. Does the sentence use **absent / absence / not present / none found** for a cell that was not surveyed? → **Fail.** Rewrite to “No observation” / “Unknown.”  
2. Does a non-detect from one pass say the species is gone? → **Fail.** Use `NOT_DETECTED` copy.  
3. Is a model colored like a camera hit? → **Fail.**  
4. Is the Unknown hatch explained as “no fish”? → **Fail.**  
5. Is a DOH closure described as oysters dead or gone? → **Fail.**  
6. Is a cancelled charter described as a zero? → **Fail.**

---

## 6. Fixture keys

Synthetic rows for each state: `fixture_records.csv`. Fixtures are **not** real observations and must keep `legal_privacy_tier=FIXTURE_SYNTHETIC`.
