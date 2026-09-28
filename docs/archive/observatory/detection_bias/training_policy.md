# Training policy — detection, absence, and occurrence data

**Date:** 2026-09-18  
**Status:** Binding on any future occupancy / SDM / encounter / CPUE model.  
**This iteration:** **no training.** The policy exists so nobody “just fits Maxent on OBIS” in a later sprint.

Gates before any fit: FishAI quality Gates 1–8 and observatory validation protocol. Today Gate 1 (wedge) fails; advanced ML is blocked.

---

## 1. Top banned practices (copy these)

These are **BLOCKERS**. Do not “try them to learn the stack.”

| ID | Banned practice | Correct treatment |
| --- | --- | --- |
| **BAN-1** | Naive presence/absence from occurrence-only databases | Presence-only: `PRESENT_OBSERVED` vs `NO_OBSERVATION` |
| **BAN-2** | Treating **GBIF / OBIS / Ocean Biodiversity Information System** “no record in cell” as absence | GBIF/OBIS = **presence**, never absence |
| **BAN-3** | Filling unsampled cells with 0 so a classifier has negatives | `NO_OBSERVATION`; `DATA_GAP` hatch |
| **BAN-4** | Unfished / unvisited cells as true negatives (Chinook EEZ occupancy) | Evaluate only **visited** cells; Quality validation_protocol effort rule |
| **BAN-5** | Cancelled charter / no trip as zero catch | `NO_OBSERVATION`, not `NOT_DETECTED` |
| **BAN-6** | Dealer landings without effort as CPUE or non-detect | Reject as Category C; `DATA_UNAVAILABLE` if logs exist but lack soak |
| **BAN-7** | AIS / VMS / GFW as abundance, occupancy labels, or inshore lobster effort | Traffic diagnostic only; inshore lobster AIS **not** effort |
| **BAN-8** | WA DOH / NSSP closures as oyster mortality, occupancy, or ops-stress \(y\) | Constraint + authority context; farm logs are \(y\) |
| **BAN-9** | SST / chlorophyll as \(y\) or as proof of presence | Habitat covariates at most; SST ≠ body T ≠ bottom T |
| **BAN-10** | Single-visit Maxent/SDM emitted as current occupancy / T3 | T1–T2 suitability only; `PRESENT_INFERRED` |
| **BAN-11** | Pseudo-absences drawn uniformly in geographic space without an access model | See §4; still **background**, not absence |
| **BAN-12** | Random 80/20 split of nearby marine cells | Blocked spatial/temporal CV |
| **BAN-13** | Using `PRESENT_INFERRED` or habitat rasters as labels | Labels are observed trials only |
| **BAN-14** | N-mixture / “AI census” on iNaturalist | Barker et al. 2018; forbidden Category A |
| **BAN-15** | Training through the as-of clock (delayed-mode, revised landings, future eDNA) | `published_at ≤ issued_at` |
| **BAN-16** | Mixing closed salmon water into encounter likelihood as zeros | Closed = constraint; no trial |
| **BAN-17** | Trap CPUE as \(N\) or as \(\psi\) | Category C + catchability text; hyperstability |
| **BAN-18** | eDNA non-detect as animal absence without kernel + repeats | `NOT_DETECTED` of DNA only |
| **BAN-19** | Tag-empty cells as stock absence | Tagged subset ≠ population |
| **BAN-20** | Sensor-threshold labels (e.g. SST ≥ 19 °C → oyster dead) | Circularity; red-team RT-SIB-01 |

---

## 2. GBIF / OBIS contract

OBIS metadata (page access 2026-09-18): on the order of **224M observations / 207K marine species / 7,363 datasets** — still biased to coastal, shallow, well-known taxa; ~half of WoRMS species have any OBIS record; 56% of OBIS species have &lt;10 records (Webb et al. 2010; OBIS 2019 review cited in modality catalog).

**Allowed**

- Compile **presence** points as `PRESENT_OBSERVED` / `SURVEY-DERIVED` **if** rights later allow, with `as_of` and dataset citation.  
- T1 historical occurrence coverage, explicitly effort-biased.  
- Covariate exploration in research lane **without** emitting maps.

**Forbidden**

- \(y=0\) for cells without points.  
- “Occupancy of the species is 0 outside the convex hull of OBIS.”  
- Bulk ingest this iteration.  
- Fine public maps of listed / harvest-sensitive taxa.

**License:** `UNKNOWN` until DATA_RIGHTS verifies the **intended use**. Visual access ≠ license (`../observation_modality_catalog.md`).

Same rule for GBIF, iNaturalist (unless a **complete checklist** protocol exists), OBIS DNA-derived records (still presence of **sequences**, with contamination caveats), and museum dumps.

---

## 3. When occupancy models are allowed

An occupancy (\(\psi, p\)) model may be **fitted** only if **all** hold:

1. Founder/wedge or observatory protocol names the taxon × grain × window.  
2. Rights class approved for train/eval.  
3. Detection **trials** exist: repeated visits **or** dual methods **or** a documented distance/count structure — not occurrence-only.  
4. Effort is known for those trials.  
5. As-of snapshots exist.  
6. An effort-null baseline is pre-registered (RT-OBS-03).  
7. Output class will remain `MODEL-INFERRED` occupancy / Category D until independent validation.  
8. Public grain passes `sensitive_location_policy.md`.  
9. The fit is **not** this 2026-09-18 iteration.

**Allowed occupancy settings (examples, still future)**

- eDNA occupancy on a **fixed station grid** with blanks, LOD, and a hydrodynamic kernel.  
- Camera grid with soak + visibility.  
- Intertidal quadrats with repeat tides.  
- eBird-like complete checklists (rare at sea).

**Not occupancy**

- W1 planted oysters ( \(\psi \approx 1\) by husbandry). Use a **mortality/workability** detection model instead.  
- W2 24–48 h Chinook EEZ maps.  
- W3 next-trip lobster as \(\psi\). Use soak-adjusted CPUE with catchability.

If repeats do not exist, stop at **presence-background suitability (T2)** or **presence-only reporting (T1)**. Say so.

---

## 4. Pseudo-absence and background rules

**Vocabulary:** a **background** sample is a location used to characterize the environment **available** to a presence-background SDM. It is **not** an absence. A **pseudo-absence** is a modeler’s synthetic \(y=0\). FishAI allows background. It allows pseudo-absence only under the narrow rules below, and the stored observation state must **not** be `TRUE_ABSENCE_SUPPORTED` unless §1.4 of the enum is met.

### 4.1 Allowed background (presence-background SDM, T2 only)

| Design | Label in store | Notes |
| --- | --- | --- |
| Target-group background (Phillips et al. 2009): sites surveyed for a comparable guild | `NO_OBSERVATION` of **focal taxon** if the protocol did not look for it; `NOT_DETECTED` if it did | Prefer the latter |
| Random background **inside the sampled access envelope** (depth, distance-to-port quantile of presences) | `BACKGROUND_SAMPLE` metadata; observation_state stays `NO_OBSERVATION` | Must include access covariates in \(\psi\) |
| Kernel density of effort (ship-days, checklists) as weights | weights, not zeros | |

Output: habitat suitability `PRESENT_INFERRED`. **Not** current presence. **Not** T3.

### 4.2 Allowed justified pseudo-absence (enters likelihood as \(y=0\))

All of:

1. A **real observation process** ran (`effort > 0`).  
2. Protocol looked for the taxon (or a defined guild including it).  
3. Result was non-detect → store `NOT_DETECTED`.  
4. Optionally, after repeats + \(p\) model + corroboration, promote to `TRUE_ABSENCE_SUPPORTED`.

Examples that **qualify:** charter trip with angler-hours and zero Chinook; trap-haul with soak and zero legal lobster; farm walk of named bags with zero gapers; eDNA filter with negatives and passing blanks.

### 4.3 Forbidden pseudo-absence

- Uniform random points in the EEZ.  
- “All H3 cells without OBIS hits.”  
- Cells beyond the survey polygon.  
- Clouded satellite pixels as biological zeros.  
- Weather-cancelled trips.  
- Closed management areas as biological zeros (they are **constraints**).  
- Deep cells for a surface-only method.  
- Another species’ absences without a target-group justification.

### 4.4 W2-specific

Quality agent: *“Do not treat unfished cells as true negatives unless a documented presence-absence survey exists (it does not).”* Ranking among **visited** cells is the honest metric. Occupancy maps of the whole EEZ are **out of scope**.

---

## 5. Positive-only and presence-only models

If only presences exist:

- Allowed research: envelope, Maxent/Blight-style suitability, with access bias covariates, year-block, and **explicit** `PRESENT_INFERRED` / T2.  
- Required failure text: “This is not occupancy, not current condition, not abundance.”  
- Forbidden: converting the complementary raster to absence.

---

## 6. Leakage and splits (training-time)

Reuse `p_detect_model_spec.md` §6. Additional training bans:

- No pre-training a foundation model on global OBIS then “fine-tuning” Willapa mortality (RT-OBS-10).  
- No using the same farm’s sensor both as \(X\) and as a thresholded \(y\).  
- No evaluating occupancy with the habitat raster that trained it.  
- No splicing lobster CPUE across the 10% → 100% reporting break (Hodgdon 2025) without an era flag.

---

## 7. What may be stored before training exists

Fixtures in `fixture_records.csv` are **synthetic**. Production stores, when they exist, must persist `observation_state` as a **required** column. ETL that writes 0/1 without the enum is a contract break.

---

## 8. Stop rules

Stop model complexity (Quality: two major iterations without beating the relevant baseline). Additional detection-engine stops:

- Effort-null wins → stop occupancy maps.  
- Users interpret Unknown hatch as absence → fail UI, do not “fix” by filling zeros.  
- Any PR that adds `absent=True` for null OBIS joins → reject.
