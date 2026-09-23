# W2 Chinook and W3 lobster — detection notes

**Date:** 2026-09-18  
**Status:** Design notes for the detection engine. **Not** a wedge lock. **No training.**  
**Taxa:** *Oncorhynchus tshawytscha* (AphiaID 158075); *Homarus americanus* (AphiaID 156134).

These notes exist so later models do not treat **missing trips as zeros**, **trap CPUE as biomass**, or **AIS as inshore effort**.

---

## W2 — Chinook × CA/OR charter encounter

Honest object: Category **D** relative encounter in **open** PFMC recreational water; evaluate with Category **C** CPUE. Never a catch guarantee. Never AIS-as-abundance. Public RecFIN/CRFS monthly = **B12**, not 24–48 h \(y\) (Quality agent).

### Charter zeros vs no trip

| Field situation | Observation state | Enters encounter likelihood? |
| --- | --- | --- |
| Trip ran; angler-hours &gt; 0; Chinook kept or released ≥ 1 | `PRESENT_OBSERVED` (encounter) | \(y=1\) |
| Trip ran; effort known; **zero** Chinook | `NOT_DETECTED` | \(y=0\) (**keep zeros** — Quality min GT) |
| Trip cancelled (weather, mechanical, no booking) | `NO_OBSERVATION` | **No trial** |
| Cell never visited that day | `NO_OBSERVATION` | **No trial** — not a true negative |
| Area **closed** (in-season / season / river-mouth special closure) | **Constraint**; do not score encounter | Not biology; not \(y=0\) occupancy |
| Captain intended grounds pre-logged (B5) but steamed elsewhere | Effort is where they **fished** | Do not assign zeros to unfished intended cells |
| Monthly CPFV log / RecFIN estimate only | Too coarse / lagged → `DATA_UNAVAILABLE` for 48 h trials | B12 baseline only if licensed |
| AIS of other boats in the cell | Traffic / crowding | **Forbidden** as \(y\) or \(N\) |

**Why cancelled trips are not zeros.** A small-craft warning can yield **zero encounters because nobody fished**, while fish remain in the water. Coding that day \(y=0\) trains the model to equate **weather** with **absence** (and to punish good habitat on unwindy days incorrectly). Weather belongs in \(p\) (catchability / go-no-go) **conditional on a trip**, and in a **trip-generation** model if one exists — not as occupancy of Chinook.

**Why unfished cells are not zeros.** Charters sample a tiny, skill-biased subset of the EEZ. Completing the raster with zeros is BAN-4. Honest metrics: PR-AUC and top-k **among visited cells**.

**Vertical refuge.** Adults occupy ~8–12 °C **by changing depth** when SST warms (Hinke et al. 2005 *MEPS*). A surface non-detect / surface-empty troll is `NOT_DETECTED` **in the fished depth band**, not `TRUE_ABSENCE_SUPPORTED` in the cell.

**Stock mix.** One “Chinook” encounter mixes hatchery and ESA-listed ESUs. No ESU-resolved occupancy maps. Fine public spots forbidden.

**Stage error.** JSOES / NWFSC stoplight / juvenile chl-habitat papers are the **wrong stage and timescale** for adult charter \(p\).

### W2 \(p(\mathrm{detect})\) sketch (not fitted)

\(p\) rises with angler-hours, competent local skill, legal gear, fishable sea state, and thermal habitat **at fishing depth**. \(p\) is unidentified at 24–48 h from SST/chl alone (Shelton et al. 2021 seasonal SST; Satterthwaite contact-rate = area/month/effort — red team). Bag limits **truncate** retained CPUE.

---

## W3 — American lobster × GOM CPUE

Honest object: Category **C** next-trip **legal** CPUE (pounds or count per trap-haul), soak-adjusted. **Catch ≠ abundance.** Universe = trips with hauls &gt; 0.

### Trap CPUE hyperstability

Harley, Myers & Dunn (2001) *CJFAS*: CPUE can remain high while abundance falls when animals aggregate and fishers find aggregations. ASMFC **2025** lobster assessment / peer review treats hyperstability and **temperature-dependent catchability** as first-order. Watson et al. 2019 *Fish. Bull.*: trap **saturation**. Zhang et al. 2025 (Ocean State Report): bottom T catchability. McLeese & Wilder 1958: warmer water → more trap encounters.

**Engine implications:**

| Tempting interpretation | Honest state / claim |
| --- | --- |
| High CPUE → high \(\psi\) or high \(N\) | **Forbidden.** High \(q\) (activity, bait, molt, T) can dominate |
| Low CPUE → absence | `NOT_DETECTED` of **legal catch on that haul**, not unoccupied bottom |
| No haul this TMS this week | `NO_OBSERVATION` |
| VTS summer zero at a station | `NOT_DETECTED` in **that survey protocol**; not January occupancy |
| Dealer pounds, no trap-hauls | Not a detection process; reject Category C |
| Gauge / v-notch / vent era change | Reporting-process break; Hodgdon et al. 2025 2008–2023 protocols; do not splice as one \(p\) |

Soak and bait are **detection/catchability** covariates. If missing, the row cannot enter a CPUE likelihood (Quality: dealer pounds without effort rejected).

**Hyperstability and maps.** A public CPUE heatmap is both scientifically false as abundance **and** a privacy BLOCKER (secret strings). Observatory: coarsen or `NEVER_PUBLISH`. Detection engine: do not convert high CPUE cells to `PRESENT_OBSERVED` **stock** layers.

### AIS is not effort for inshore lobster

| Fact | Consequence |
| --- | --- |
| U.S. AIS carriage for many commercial vessels is **≥65 ft** (33 CFR 164.46), with exceptions | Typical **inshore** lobster boats are often **below** carriage size |
| Addendum XXIX / ME DMR tracker programs: **confidential** subsets | `DATA_UNAVAILABLE` / `RIGHTS` / `WITHHELD_SENSITIVE` — not public effort |
| VMS confidential (NMFS 06-101) | Authority-to-authority only |
| AIS switch-off, garbling, class-B gaps | Even where AIS exists, it is a **selected** transmitting subset |
| GFW | Vessel-activity product; project rights: treat as noncommercial / not abundance |

**Therefore:** AIS density **cannot** stand in for trap-hauls, soak, or \(E\) in GOM inshore lobster. Using AIS as effort manufactures \(p\) where large AIS-equipped vessels steam and **misses** the actual fishery. Red team: BLOCKER.

**Valid effort (when lawfully available):** partner haul logs; licensed ME e-reports (lagged, **one 10-minute square per trip** — not next-haul GPS); CFRF research-fleet protocols; sea-sampling (confidential). Public DMR landings **lack effort**.

Empty AIS in a nearshore cell = `NO_OBSERVATION` of **Class-A traffic**, **not** `NOT_DETECTED` of lobster.

### SST ≠ bottom T

Bottom temperature is the catchability covariate. Satellite SST is the wrong depth (ASMFC 2025 peer review; eMOLT-class sensors are the relevant **source class**, not ingested here). A warm SST pixel is not `PRESENT_OBSERVED` lobster.

---

## Shared bans (W2/W3)

1. No trip / no haul ≠ biological zero.  
2. No AIS-as-\(N\) or AIS-as-inshore-\(E\).  
3. No EEZ occupancy inpaint.  
4. Zeros **with documented effort** are precious — keep them as `NOT_DETECTED`.  
5. Management masks (salmon closures, ALWTRP, gauges) are constraints, not detection trials.
