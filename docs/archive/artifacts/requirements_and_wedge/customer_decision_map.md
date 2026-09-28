# Customer decision map

**Status:** Hypothesis map from official industry evidence. **No operator interviews completed.** Treat workflow detail as UNTESTED except where a public source describes it.  
**Date:** 2026-09-18  
**Agent:** REQUIREMENTS_AND_WEDGE_AGENT

The map is written for all three viable wedges so the founder can see the decision object before choosing. After a wedge is locked, delete the other two sections from the working copy (do not expand scope).

---

## Shared product contract (every wedge)

Customer-facing output must answer, in under 60 seconds:

1. What changed?
2. What may happen in the horizon?
3. Why (drivers), with evidence tier?
4. How confident?
5. What options exist (not commands)?
6. What official safety/regulatory boundary applies, with URL and timestamp?
7. How does the user report what actually happened?

Never: licence, navigation, weather-safety, food-safety authorization, catch/harvest/revenue guarantee, exact private coordinates, Indigenous knowledge, protected-species dens.

---

## W1 — Pacific oyster farm operator (recommended wedge)

### Who

Commercial farm manager or crew lead on a Pacific oyster plot in a named WA DOH growing area (recommended: Willapa Bay system). Pays labor, fuel, barge/skiff time, seed, and bears mortality.

### Recurring decision

**Next 24–72 hours:** Is this a **stress, disruption, or workable tide window**? Specifically:

- Work the next low tide (handle, sort, move, harvest-prep, plant) **versus** stand down.
- Add shading/immersion/handling limits if heat coincides with daylight lows.
- Increase mortality checks / reduce handling after a heat, hypoxia, or bloom-stress signal.
- **Not:** “Are these oysters legal/safe to sell?” That is WA DOH / NSSP.

### Current workflow (hypothesis — untested with named farms)

| Step | Likely current tool | Pain |
| --- | --- | --- |
| Check tide | CO-OPS / local tide book / phone app | Tide is necessary but not sufficient (heat × low tide × wind) |
| Check weather | NWS, local knowledge | Not framed as “crew call + oyster stress” |
| Check water | NANOOS Shellfish Growers, farm gauges, “look at the bay” | Portal exists; **decision packaging** may not |
| Check harvest legality | DOH growing-area map / biotoxin bulletins / WAHH reporting | Must remain the authority |
| Decide crew | Phone tree, experience | Cost of a wasted tide vs cost of missing a rare work window |
| Observe outcome | Walk bags/beds; maybe PSI mortality form (research-only) | Not structured as a forecast label |

NANOOS states growers need temperature, chlorophyll, salinity, turbidity, and DO to manage mariculture ([NVS Shellfish Growers](https://nvs.nanoos.org/ShellfishGrowers)). That is **evidence of a data-packaging and forecasting problem**, not proof they will pay FishAI.

### Cost of being wrong (directional, not a WTP number)

| Error | Documented analog | Operational cost (qualitative) |
| --- | --- | --- |
| Miss heat-at-low-tide | 2021 heat dome + lowest tides; Pacific oysters hit harder inland/south (Raymond et al. 2022; WSG RRN) | Mass mortality; handling during stress worsens outcomes (2018 WDFW grower reports: animals intolerant of handling/crowding) |
| False alarm (stand down a good tide) | None quantified in public sources | Wasted labor schedule; missed planting/harvest-prep; **alarm fatigue** |
| Treat HAB/sanitation as FishAI call | DOH emergency closures (e.g. Possession Sound flood closure 10–20 Dec 2025 in 2025 annual review) | Legal/safety violation; product-killing claim |

PSI: **20–80%** losses in multiple WA growing areas in recent summers ([pacshell.org](https://www.pacshell.org/triploid-oyster-health.asp)). That is **event magnitude**, not expected annual loss for a typical Willapa farm.

### Alternatives (not FishAI)

- NANOOS NVS Shellfish Growers / Data Explorer (free viewer)
- NOAA CO-OPS and NWS (free)
- Farm sensors / hatchery dashboards
- Innovasea / aquaManager / Manolin-class **fish/shrimp** FMS (poor fit for intertidal oysters)
- PCSGA / WSG / PSI extension and mortality diagnostics
- Consultant / tribal co-manager advice
- “Do what we did last year”

**Gap hypothesis:** none of the free viewers output a **single farm-specific work/stress decision** with a locked forecast time, uncertainty, and a 30-second outcome loop.

### Ground truth the customer can provide

Permissioned, PRIVATE:

- Tide worked Y/N and why
- Handling events
- Counted mortality or “unusual die-off” flag by bag/bed (coarse)
- Optional sensor exports they already own

PUBLIC must never show farm performance. WAHH production reports are disclosure-exempt per WDFW user manual.

### Why they might contribute outcomes

- Private historical stress calendar
- Brief tuned to **their** growing area, not Hood Canal ORCA by default
- Diagnostic funding already exists at PSI for some health screening — FishAI should complement, not scrape that research-only form into a commercial model without a new agreement

**Untested.**

### Cadence

Daily brief at T-12h before the relevant low tide in May–September; silent or weekly off-season unless a storm/heat/flood watch.

---

## W2 — Chinook charter captain

### Who

CPFV captain in one open ocean salmon area (recommended: Cape Falcon–Humbug Mountain, OR). Revenue = booked anglers × price minus fuel, crew, maintenance. 2023 CA disaster math used **$225–$265 per angler**.

### Recurring decision

**Next 24–48h, if legally open:** Run vs cancel (weather is NWS, not FishAI). If run: **which coarsened sub-area** has higher **relative Chinook encounter** given fuel range. Not “how many kings are in the ocean.”

### Current workflow (hypothesis)

| Step | Tool | Pain |
| --- | --- | --- |
| Is the season open? | PFMC/NMFS in-season, ODFW/CDFW | Closures can be total (2023–24 CA) |
| Weather/safety | NWS, USCG, judgment | FishAI must only **link** official weather |
| Where to go | Personal history, radio, forums (Tier 4) | Forums are not labels; spots are private |
| Log the trip | CA CPFV log required; RecFIN/CRFS sample | Logs are not a product |

### Cost of being wrong

- Burn fuel and reputation on a zero-encounter day vs staying nearer / not running.
- 2023–24 disasters show **season-scale** loss (CA CPFV allocation $4.79M across 127 boats) — that is **stock/season risk**, only partly a 24h area-choice problem. Do not sell W2 as disaster insurance.

### Alternatives

- State regs and in-season hotlines
- RecFIN public estimates (too lagged for tomorrow)
- Consumer apps (Fishbrain/Fishidy) — spot-map culture; wrong privacy posture
- Captain networks

**Gap hypothesis:** no rights-safe, coarsened, uncertainty-aware **relative encounter brief** tied to a captain logbook flywheel.

### Ground truth

Trip: coarsened cell, angler-hours or lines, Chinook catch/zero, date. Exact lat/lon PRIVATE / NEVER_PUBLISH.

### Cadence

Evening-before + dawn update on **open days only**. Product sleeps when closed.

---

## W3 — Commercial lobster operator (SA 513)

### Who

Maine commercial lobster license holder, day-trip inshore, trap/pot. 2025: 5,060 trap-capable licenses statewide; SA 513 is a subset.

### Recurring decision

**Next trip:** where to allocate limited haul time among coarsened sub-areas for **expected legal CPUE**, given bait, fuel, soak, and **official** whale-gear constraints. Not “how many lobsters are in the Gulf of Maine” (ASMFC already publishes stock status).

### Current workflow (hypothesis)

| Step | Tool | Pain |
| --- | --- | --- |
| Where the gear is | Private knowledge | Will not share GPS with a public app |
| Temp / molt timing | Experience, NERACOOS, dock talk | 2025 DMR: late molt limited summer new-shell access |
| Rules | NOAA ALWTRP, DMR zone rules | Must remain official |
| Report | Mandatory dealer/harvester reporting | Confidential; not a FishAI feed without agreement |

### Cost of being wrong

- Extra steam / bait for weak CPUE; opportunity cost of not hauling a better coarsened cell.
- 2025: 21,000 fewer trips, −8 million lb, −$75 million vs 2024 (DMR) — mix of price, molt, tariffs, behavior. **Not** proof a 24h model would have changed that.

### Alternatives

- DMR landings dashboards (coarse, delayed)
- ASMFC assessments (annual)
- Co-op / dealer intel
- Personal logbooks

**Gap hypothesis:** private next-trip CPUE ranking with official constraint links. Public hotspot map would destroy trust.

### Ground truth

Haul: coarsened cell, trap-hauls, legal count. NEVER_PUBLISH coordinates. Right-whale and ESA layers NEVER_PUBLISH at fine scale.

### Cadence

Pre-trip brief on days they will haul; not a consumer map.

---

## Decision-type diagnosis (all wedges)

| Question | W1 | W2 | W3 |
| --- | --- | --- | --- |
| Data quality problem? | Partly (Willapa in-situ sparse) | Ocean in-situ sparse for fish | Haul data hidden |
| Data access problem? | Farm outcomes private | Captain outcomes private | Haul outcomes private |
| Packaging problem? | **Likely** (NANOOS exists) | Regs exist; forecast does not | Assessments exist; trip forecast does not |
| Forecasting problem? | Yes (72h stress/work) | Yes (48h relative encounter) | Yes (next-trip CPUE) |
| Workflow problem? | Crew call | Trip planning | Effort allocation |
| Trust problem? | Food-safety impersonation risk | Spot-map / ESA risk | Spot-map / whale risk |

v0 should attack **packaging + measurable forecast + outcome loop**, not a new global database.

---

## Traction gates (from master prompt; none met)

30-day targets after wedge lock: 15 interviews, 3 design partners, 1 paid/LOI, 1 historical outcome dataset or DUA, 1 domain reviewer, 1 manual brief delivered, documented workflow. **Current: 0.**
