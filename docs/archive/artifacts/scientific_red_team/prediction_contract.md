# Prediction Contract

**Agent:** SCIENTIFIC_RED_TEAM_AGENT  
**Date:** 2026-09-18  
**Status:** Binding for any customer-facing or partner-facing output. No model is approved.  
**Default public category:** C (effort-normalized catch) or D (relative habitat / encounter / risk).  
**Ceiling:** no claim stronger than the strongest evidence tier on that output.

This document is the only approved claim language for the three candidates. Product, sales, and other agents may shorten layout but **may not strengthen meaning**.

---

## 0. Claims that MUST NEVER appear

### Universal (all wedges, all channels including decks)

- Exact counts of wild animals in an unsurveyed cell (“N Chinook in this 10 km square”).
- “AI abundance,” “biomass,” “the stock is up/down/healthy here.”
- AIS, VMS, GFW, vessel density, or tracker pings as fish/lobster abundance.
- SST or chlorophyll as proof of presence, abundance, safety, or legality.
- Social media, forums, or unverified photos as confirmed presence.
- Guarantee of catch, harvest, survival, yield, or revenue.
- Legal fishing authorization; remaining quota as if official.
- Navigation or weather-safety advice (“it is safe to go”).
- Medical, regulatory, or environmental certification.
- Commands: “fish here,” “harvest now,” “set gear on this waypoint,” “eat these oysters.”
- Three-decimal biological probabilities; 100 m “hotspot” maps as truth.
- Silent edits to past forecasts; evaluation that uses data not available at issuance.

### Oyster never-claims

- “Safe to eat / safe to harvest / legal to harvest.”
- “Open” or “closed” as a **model** output.
- “Meets NSSP, FDA, WA DOH, or ISSC requirements.”
- “No Vibrio / no PSP / no DSP / no ASP / toxin-free / below action level.”
- Combined green/red score mixing ops stress with sanitation.
- Another farm’s mortality, yield, or lease polygon without permission.

### Chinook never-claims

- “You will catch fish,” “limits tomorrow,” “the bite is on at this lat/lon.”
- “Abundance is high in this cell.”
- A score on a **closed** area.
- Fine-scale public spot maps; listed-stock targeting language.
- Recreational retained catch described as a scientific abundance survey.

### Lobster never-claims

- “This AIS hotspot is where the lobsters are.”
- “CPUE up means the stock is up” / cell-level abundance.
- Public maps of strings, high-CPUE cells, or tracker paths.
- Guaranteed landings, price, or haul.
- Advice to set on another operator’s gear.

---

## 1. Required fields on every output (14)

Copied from the master product-output contract; all 14 are mandatory.

1. Species and geography scope  
2. Target definition  
3. Forecast horizon  
4. What the prediction means  
5. What it does **not** mean  
6. Data freshness  
7. Confidence and uncertainty  
8. Relevant inputs/drivers  
9. Known missing inputs  
10. Source attribution / provenance  
11. Regulatory / safety disclaimer  
12. Suggested action **options**, not commands  
13. Outcome-reporting mechanism  
14. Error / feedback mechanism  

**Plus red-team fields:** evidence tier of the strongest label; prediction category (A–E); extrapolation flag; official-status last-verified time (oyster and salmon regulation mask).

---

## 2. Confidence labels (only these)

| Label | Meaning |
|---|---|
| **High** | Recent local **verified** outcomes (Tier 1/2), stable inputs, inside trained conditions, official status fresh |
| **Medium** | Adequate environment but sparse recent biological/operational outcomes |
| **Low** | Missing key data, novel conditions, source outage, or extrapolation |
| **None** | Do not issue a biological/operational score (still may show official context + “insufficient data”) |

Do not print calibrated-looking percentages until a human reviewer accepts a calibration plot from **prospective** data.

**Ranks, not fake counts:** lower / middle / upper tercile of the **stated comparison set**, or “elevated / typical / reduced **indicator**.”

---

## 3. Candidate 1 — Pacific oyster × WA × 72h ops stress

| Field | Contract |
|---|---|
| Species / geography | Pacific oyster (*Magallana gigas* / *Crassostrea gigas*), **named growing area and permissioned lease only**, Washington. |
| Target | Category **D**: 72h **operational disruption / environmental-stress indicator** (workability, emersion-heat exposure, wave/gear). |
| Horizon | 24–72 hours from issuance time (UTC + local tide clock). |
| Means | Rank of **physical/operational stress conditions** relative to this lease’s comparable tides/season. |
| Does not mean | Food safety; harvest legality; NSSP classification; toxin absence; guaranteed survival or yield; other farms. |
| Freshness | Env forecast age; in situ sensor age; **DOH status last-verified** separately. |
| Confidence | High only if lease sensors + tide-timed air/emersion; SST-only ⇒ **Low** or **None**. |
| Drivers | Inputs (air, tide/emersion, wind/wave, in situ T/S/DO). Phrase as inputs, not “caused by SST.” |
| Missing | Ploidy, culture type, handling, disease, HAB toxin (always missing from this model). |
| Provenance | Sensor IDs; NWP source; tide source; model/rule version. |
| Disclaimer | **Required paragraph below.** |
| Options | “Consider shifting labor off the hottest emersion; inspect gear after wave event; increase monitoring.” Never “harvest now.” |
| Outcome | Worked tide? Y/N; observed mortality protocol count; gear loss Y/N. |
| Feedback | Wrong tide timing / wrong lease / stale DOH. |

### Official context module (not a model)

Show WA DOH commercial growing-area / biotoxin / Vp control status with: authority, timestamp, jurisdiction, source URL, geographic boundary, last verified time. If stale, banner: “Official status not verified — do not harvest on the basis of this brief.”

### Approved oyster paragraph

> Elevated **operational stress indicator** for Lease [ID] over the next 72 hours, associated with forecast air temperature overlapping daytime emersion and [wave/wind] exposure. Comparison set: this lease, similar tides, [season]. Confidence: [Low/Medium/High]. Category D. Strongest evidence: [Tier 1 sensors / Tier 2 farm log / Tier 3 forecast only]. **This is not a food-safety determination and not harvest authorization.** Verify official growing-area and biotoxin status with the Washington State Department of Health (and tribal or FDA authorities where applicable). Satellite temperature is not oyster body temperature and is not a tissue toxin test. It does not replace the *Vibrio parahaemolyticus* control plan (WAC 246-282-006).

### Forbidden oyster substitutes

Any sentence that a reasonable operator could read as “you can sell these oysters.”

---

## 4. Candidate 2 — Chinook × CA/OR × 24–48h relative encounter

| Field | Contract |
|---|---|
| Species / geography | Ocean Chinook salmon (*Oncorhynchus tshawytscha*), **named PFMC/CDFW/ODFW management area**. Mixed stocks; not a single population. |
| Target | Category **C** (preferred) or **D**: relative **effort-normalized encounter rank**, not occurrence, not abundance. |
| Horizon | 24–48 hours, **only if the area is open**. |
| Means | Rank of expected CPUE vs comparable **open-season** days in this area (same month / weather-workability bin if used). |
| Does not mean | Abundance; biomass; catch guarantee; “limits”; legal authorization; weather safety; navigation; a 48h habitat census. |
| Freshness | Log lag; env lag; **regulation last-verified**. |
| Confidence | Partner logs with effort ⇒ at most Medium in v1. SST/chl-only ⇒ **None** (do not issue). |
| Drivers | Calendar, area, partner history; weather as **trip feasibility confounder**, not “fish are here.” |
| Missing | Stock composition, subsurface habitat, skipper skill, crowding, bait, in-season remaining quota (official). |
| Provenance | Partner trip IDs (private); regulation URL; model/climatology version. |
| Disclaimer | **Required paragraph below.** |
| Options | “Consider trip timing consistent with your usual grounds.” Never waypoints. |
| Outcome | Anglers, hours, retained, released, area coarsened. |
| Feedback | Wrong area / actually closed / weather prevented trip. |

**Hard mask:** if regulation status is closed or unknown, output is **None**: “No encounter score. Fishery closed or status unverified. See NMFS/CDFW/ODFW.”

### Approved Chinook paragraph

> **Relative CPUE rank** for ocean Chinook in [management area] over the next 24–48 hours: [lower/middle/upper] third of comparable **open** days in our partner-log comparison set. Confidence: [Low/Medium]. Category C. Strongest evidence: Tier 2 charter logs (not a survey). **Not an abundance estimate and not a catch guarantee.** Not legal advice, not a license, not navigation, not weather-safety advice. Check NMFS, CDFW, and/or ODFW in-season regulations before leaving the dock. Closed areas are not scored. Chinook in this area are a mix of stocks, including units with conservation limits.

### Forbidden Chinook substitutes

Heatmaps titled “where the fish are”; “72% chance of limits”; scoring a closed cell.

---

## 5. Candidate 3 — Lobster × GOM × next-trip CPUE

| Field | Contract |
|---|---|
| Species / geography | American lobster (*Homarus americanus*), **named statistical area / zone**, **operator’s own effort footprint**. |
| Target | Category **C**: expected **legal catch per defined effort** (default: per trap-haul) for the next planned haul window. |
| Horizon | Next trip / next soak haul, as specified (not a 10-year stock outlook). |
| Means | Rank vs **this operator’s** comparable trips (season, soak band, zone). |
| Does not mean | Abundance; recruitment; stock status; AIS hotspot; public fishing map; others’ gear. |
| Freshness | Last haul in training/comparison; bottom-T forecast age. |
| Confidence | High never in v1 without prospective calibration. Missing soak/bottom T ⇒ Low. |
| Drivers | Soak, bait, zone, bottom temperature **as catchability inputs**; not “more lobsters.” |
| Missing | Molt, trap saturation, neighbor gear, whale-area rules if not ingested. |
| Provenance | Operator log version; env source; **no AIS**. |
| Disclaimer | **Required paragraph below.** |
| Options | “Consider which of *your* strings to haul given soak.” Never “set 2 nm east.” |
| Outcome | Legal count, trap-hauls, soak hours, discards as agreed. |
| Feedback | Wrong soak recorded / rule change / missing haul. |

### Approved lobster paragraph

> **Effort-normalized catch rank** for legal American lobster on **your** gear in [zone], next haul window: [lower/middle/upper] tercile of your comparable trips with similar soak. Confidence: [Low/Medium]. Category C. Strongest evidence: Tier 2 logbook. **This is not abundance.** Catch rates move with temperature-dependent catchability, soak, bait, molt, and regulations even when local density is unchanged. AIS and vessel traffic are not lobster density and are not used here. Exact locations stay private. Not legal, navigational, or entanglement advice. Check Maine DMR / ASMFC / NOAA rules.

### Forbidden lobster substitutes

Public choropleth of “hot cells”; GFW screenshot in the app; “stock booming in this square.”

---

## 6. Map and number rules

| Allowed | Not allowed |
|---|---|
| Coarse rank choropleth for a **data owner** | Public 100 m–1 km biological heatmaps |
| Official closure polygons with attribution | Model-colored “open/closed” |
| Uncertainty / missing-data hatch | Smooth interpolation over empty cells |
| Terciles, “elevated indicator” | 0.73, 37% mortality, “+18.4% abundance” |
| Comparison set named in words | Unspecified “AI score 82” |

---

## 7. Evidence-tier badge (required)

Every brief shows one line:

`Evidence: Tier [1–4] label · Category [A–E] output · [High/Medium/Low/None] confidence`

If label tier ≤ 3 and output is C/D, confidence cannot be High.  
If only Tier 3 inputs exist with no Tier 1/2 labels, **do not issue Category C**. Issue **None** or a non-predictive environmental context note.  
Tier 4 never appears as a prediction.

---

## 8. Binding corrections to sibling drafts

Until rewritten, these sibling sentences are **not** approved product language:

- Quality B4: “SST ≥ 19 °C for ≥12 h” as an oyster alert (growth band, wrong variable).
- Product sample: “Rank ~top 20%” and “Water temp +1.8 °C” as driver 1 (false precision; SST-first).
- Product sample geography: Totten analog (Vp Category 3 harvest-control area).
- Requirements: “crew can **safely** work the tide” (forbidden weather-safety).
- Quality B5: “changed **harvest** … plans” (legality leak).
- Chinook v0: SST/chlorophyll/currents as encounter features; “~10 km cell” as a public product grain.

Use §3–5 paragraphs instead.

---

## 9. Amendment

Only a **named human domain reviewer** may authorize additional sentences. Software agents may only tighten, not loosen, this contract.
