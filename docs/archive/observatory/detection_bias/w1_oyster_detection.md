# W1 — Pacific oyster detection (farm walk vs sensor vs SST vs HAB scope)

**Date:** 2026-09-18  
**Taxon:** *Magallana gigas* (Thunberg, 1793), AphiaID 836033; synonym *Crassostrea gigas* 140656. Dual-label in UI.  
**Geography (illustration):** Washington growing areas; Willapa recommended as AOI — **not a founder lock**.  
**Product object (if ever locked):** Category **D** 24–72 h **operational stress / disruption**, **not** occupancy of wild oysters, **not** NSSP harvest legality.  
**No training. No ingest.**

Planted oysters on an active lease are **already counted by the farmer**. The occupancy question \(\psi\) is the wrong v0 object. The detection question is: **would this method, today, have recorded mortality, gapers, workability failure, or gear damage?**

---

## 1. Four observing channels (do not fuse into one “oyster layer”)

| Channel | What it actually measures | Observation state for **oysters** | Observation state for **the measured thing** |
| --- | --- | --- | --- |
| **Farm walk / bag inspect / mortality log** | Live/dead/gaper counts, workability, intervention on **named gear** | `PRESENT_OBSERVED` (dead or live counted); `NOT_DETECTED` (walked, no mortality/disruption); `NO_OBSERVATION` (not walked) | Same (the oysters are the target) |
| **Farm / NANOOS-class sensor** (T, S, DO, pH) | Water or air **environment** at a point | **Never** oyster `PRESENT_OBSERVED`. May support `PRESENT_INFERRED` **stress** if a pre-registered rule uses air×tide, not SST-only | Sensor scalar: `DIRECTLY OBSERVED` environment |
| **Satellite SST / ocean color** | Skin temperature / pigment in a **coarse pixel** | **Never** oyster presence, mortality, or body temperature | `REMOTELY DETECTED` **skin SST / chl**, not animals |
| **HAB microscope / SoundToxins / IFCB** | Named phytoplankton cells or toxin **proxies** in a sample | **Never** oyster death. At most `PRESENT_INFERRED` feeding/toxin **stress** after a **named** mechanism | `PRESENT_OBSERVED` of the **alga** (or `NOT_DETECTED` of that alga) |

**WA DOH growing-area / biotoxin / Vp closures** are a **fifth channel** that is **not a detection method for oysters**. They measure **harvest legality / sanitation**. See §5.

---

## 2. Farm walk — the only honest ops-stress label path

Quality + data-discovery relabel: partner logs of **mortality, workability, intervention** = `ops_disruption_72h`. Public DOH closures **miss heat-kill and gear damage when harvest stays legally open**.

### Detectability on the walk

| Condition | \(p\) of recording heat-kill / gapers | State if zero found |
| --- | --- | --- |
| Daytime low tide, intertidal bags **emersed**, walker on the lease, protocol count | **High** for **already-dead or gaping** animals on inspected gear | `NOT_DETECTED` of the **event**, not “oysters absent” |
| Night / high tide / bags still submerged | **Low** visual \(p\); walk often **not done** | If no walk: `NO_OBSERVATION` |
| Subtidal / raft / deep water | Visual \(p\) **low** without dive/ROV/lift | Do not treat “no report” as zero mortality |
| Seed vs market, crowded vs thinned, bag color, mud T, cm elevation | First-order **microclimate**; same estuary, opposite outcomes | Missing culture metadata → do not claim High \(p\) |
| Delayed mortality (below) | Walk at hour 48 can be a **clean non-detect** while animals die through **day 30** | Keep `NOT_DETECTED` at 48 h; do not rewrite as absence of the heat event |

**Live planted stock** on an active lease: occupancy \(\psi \approx 1\) as **husbandry**. A walk that counts live oysters is `PRESENT_OBSERVED` of stock **presence** (trivial) and separately logs mortality/workability as the **decision label**. Do not train a wild SDM on farm presence.

**Fallow / harvested empty gear** with a documented clear-off + inspect can meet `TRUE_ABSENCE_SUPPORTED` at **gear grain**.

---

## 3. Intertidal emersion detectability

The 26–28 June 2021 atmospheric heatwave coincided with the year’s **lowest tides**. Mass intertidal mortality; Pacific oysters worse than lower-intertidal Olympia oysters (Raymond et al. 2022 *Ecology* https://doi.org/10.1002/ecy.3798; WA Sea Grant Rapid Response). Mechanism: **air × midday emersion × solar**, not a 1-km SST blob (Hesketh & Harley 2023: air ≠ body T; Miner et al. 2025; red-team RT-OYS-02). Quality B4 must **not** be “SST ≥ 19 °C.”

**Implications for \(p\):**

1. **Emersion is a visibility window** (walkers can see gapers) **and** an **exposure window** (heat kill). Those are different roles: exposure belongs in \(\psi_{\mathrm{stress}}\) / the ops indicator; visibility belongs in \(p_{\mathrm{walk}}\).  
2. A satellite SST pixel can be mild while bag-and-mud temperature is lethal — **low** validity of SST as a detection **or** stress sensor.  
3. Subtidal culture: emersion \(p\) and emersion heat **do not apply**. DO/hypoxia/HAB channels dominate; Hood Canal ORCA is **not** Willapa.  
4. Night-time lows: heat stress may be lower; visual \(p\) also lower. Do not score a skipped night tide as a biological zero.

---

## 4. Heat-kill visible vs delayed mortality to day 30

George et al. (lab; NOAA repo / https://doi.org/10.1101/2023.03.02.530828): mortality can accrue to **day 30**; triploid > diploid in that work. 2021 field narrative: some deaths **days to weeks later** (Raymond et al. 2022; marine-domain lifecycle note).

| Horizon | What a walk can detect | Risk if used as 72 h \(y\) |
| --- | --- | --- |
| Hours (same tide) | Acute gapers, cooked tissue, opened shells | True acute kills — **high** \(p\) if emersed and inspected |
| 24–72 h ops window | Some acute; **misses** delayed | False `NOT_DETECTED` / false negative ops label |
| ~day 7–30 | Additional mortality from the **same** heat event | Label lag; do not treat late deaths as a new independent event without a gap rule (≥7 d in Quality min-GT) |

**Engine rule:** store **two clocks** on W1 mortality records:

- `stressor_window_utc` (tide × air event)  
- `detected_at_utc` (walk when death was recorded)

A day-21 death with a day-0 heat event is `PRESENT_OBSERVED` **mortality** with `detection_lag_hours≈504`, **not** proof that 72 h models are useless — it is proof that **72 h ≠ % dead**. The product remains an **ops-stress indicator** (Category D), not a bag-level death forecast (marine-domain: cannot predict bag-level % dead without loggers).

Ploidy, handling, and crowding are **detection and process** covariates; they are usually `DATA_UNAVAILABLE` unless the partner logs them.

---

## 5. Farm logs vs DOH closures (binding)

| | Partner farm log | WA DOH / NSSP growing-area closure |
| --- | --- | --- |
| **Question** | Did animals die, could crew work, was there an emergency intervention? | Is **harvest legally open** / sanitary / biotoxin status? |
| **Authority** | Grower protocol (PSI / WSG rapid-response style) | WA DOH, NSSP, WAC 246-282-006 (*Vp* control) |
| **As model \(y\) for ops-stress** | **Yes** (only path) | **BLOCKER** — wrong process |
| **As occupancy of oysters** | Presence is planted; mortality is the event | Irrelevant |
| **As food safety** | Never | **Display as official context**, never impersonate |
| **Heat-kill while area stays OPEN** | Log can show `PRESENT_OBSERVED` mortality | Closure table shows **open** — if used as \(y\), the model learns **no event** |
| **Closure while animals healthy** | Log may show `NOT_DETECTED` disruption | Closure = 1 — model learns fecal rain as oyster death |
| **Observation state** | Walked: observed / not detected; unwalked: `NO_OBSERVATION` | **Not an observation_state of oysters.** Overlay `constraint: harvest_open=true/false` with `last_verified`. If the GIS cannot be used: `DATA_UNAVAILABLE` / `RIGHTS` |

Data-discovery file `ground_truth_relabel_W1.md` withdrew closures as GT. Red team: combined ops+sanitation score = shadow food-safety model.

**UI:** two modules. Never one color. Copy must not say oysters are “absent” or “safe” because a growing area is closed or open.

---

## 6. Sensors and satellite — environment, not detectability of death

- **In situ T/DO/S:** covariates \(X\). Fouled/unserviced → `DATA_UNAVAILABLE` / `SENSOR_FAIL`, not a mortality zero.  
- **Air T + tide prediction:** highest-leverage **stress** inputs for intertidal; still not an observation of death until a log exists.  
- **Satellite SST:** Low/None as oyster body T; **never** `PRESENT_OBSERVED`. Clouds → `NO_OBSERVATION` of **skin SST**, which is **not** `NOT_DETECTED` of oysters.  
- **Ocean color / HAB satellite indices:** pigment proxies, **not** toxin, **not** oyster \(y\) (SoundToxins warn; reopen needs tissue tests).

Circularity ban: do not threshold DO or SST and call it `ops_disruption_72h`.

---

## 7. HAB microscope

A counted *Alexandrium* / *Dinophysis* / *Heterosigma* (etc.) cell is `PRESENT_OBSERVED` of **that phytoplankter**. Toxin in tissue is a **different** lab process (DOH). Oyster **mortality** from a HAB is `PRESENT_INFERRED` only with a named mechanism and still needs the farm log as \(y\). Cheney et al. 2000: multi-stressor (heat, neap, low oxygen), not a single diagnosed pathogen.

Do not merge SoundToxins maps into oyster occupancy.

---

## 8. Recommended W1 state machine (lease-day)

```text
if no partner log and no walk:
    oyster_event_state = NO_OBSERVATION
elif walk/log exists and mortality|workability|intervention:
    oyster_event_state = PRESENT_OBSERVED   # of the *event*
elif walk/log exists and protocol complete and none of the above:
    oyster_event_state = NOT_DETECTED       # of the *event* at that clock
    # delayed mortality may later add PRESENT_OBSERVED with detection_lag
elif lease documented fallow and cleared:
    occupancy_state = TRUE_ABSENCE_SUPPORTED  # gear grain only

DOH overlay = constraint, never oyster_event_state
SST/sensor = environment layers
HAB scope = phytoplankton states, split from oysters
```

Globe (when implemented elsewhere): unwalked leases = **UNKNOWN hatch**, not grey “no oysters.”
