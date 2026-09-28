# Abundance and density encoding

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/abundance_encoding.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Binding. One color bar for “how much life” is a ship-block.

Do **not** display abundance as a universal heatmap. Each quantity class has its **own** legend, units, palette family, and explanation. Probability and abundance **never** share a legend.

**Commercial / P0:** do not ship any of the count-like classes for Willapa oysters. Planted stock is known to the farmer; the product is Category **D** ops-stress **ranks**, not N.

---

## 1. Quantity classes

| Code | Meaning | Typical contract category | Units (display) |
|---|---|---|---|
| `DIRECT_COUNT` | Count in a **defined** area and time with a method | A | individuals (per plot/transect), **not** per unsurveyed km² |
| `SURVEY_INDEX` | Design-based or model-based **index** | B | index units as published (e.g. n/tow, kg/tow, NASC) |
| `BIOMASS` | Mass in a defined frame, method named | A/B | t km⁻², kg, mt — **only** with protocol id |
| `CPUE` | Effort-normalized catch | C | catch per {haul, hour, trap-haul, angler-day} |
| `RELATIVE_ABUNDANCE` | Rank vs a **named** comparison set | B/C/D | lower / middle / upper tercile (or elevated / typical / reduced **indicator**) |
| `OCCURRENCE_P` | Chance of presence, not a count | D | probability or occupancy — **not** N |
| `HABITAT_SUITABILITY` | Ecological favorability | D | suitability index · **not confirmed presence** |
| `OPS_STRESS` | Operational / environmental stress rank (W1) | D | tercile of comparison set · **not** mortality % |
| `UNKNOWN` | No justified quantity | — | `unknown` |

**Forbidden units on public cells:** “AI score,” “fish/km²” without a survey, three-decimal *p*, “+18.4% abundance.”

---

## 2. Separate legends (implement as distinct `legend_id`s)

| Class | Palette family | Texture | Caption must include |
|---|---|---|---|
| `DIRECT_COUNT` | Black integers / graduated **symbols** (not a smooth field) | Solid | Method, plot area, time, detectability notes |
| `SURVEY_INDEX` | Bluish green `#009E73` | Light hatch | Survey name, stratum, cruise dates, “index ≠ census” |
| `BIOMASS` | Orange `#E69F00` | **Cross-hatch** | Protocol, wet/dry, species, “acoustic biomass is an index unless validated” |
| `CPUE` | Olive-brown `#8B6914` | Solid **PRIVATE**; public only coarsened rank | Effort definition, legal selectivity, “CPUE ≠ stock” |
| `RELATIVE_ABUNDANCE` | Olive sequential **or** tercile chips | Quantile bins | **Reference period and set** |
| `OCCURRENCE_P` | Purple sequential | Dotted (inferred) / dashed (forecast) | “Not a count”; no 0.xxx until calibrated |
| `HABITAT_SUITABILITY` | Teal sequential | Smooth only in-domain | “Not presence, not abundance” |
| `OPS_STRESS` | Gray / amber / red-**outline** | Solid chips | “Not food-safety, not harvest, not % dead” |
| `UNKNOWN` | Black/white | Diagonal hatch | Why |

**Quantile encoding:** when absolute values are not justified, use terciles or percentiles **of the stated comparison set**. The set is written in words (e.g. “this lease, similar tides, Jun–Sep 2018–2025 climatology — fixture”). Unspecified “top 20%” is forbidden.

**Uncertainty:** halo, extra hatch, or opacity per `visual_truth_states.md` §4. No fake ±.

---

## 3. Reference period

Every anomaly or percentile legend includes:

```text
Reference: {dataset} · {start}–{end} · {spatial grain} · {season filter}
```

Missing reference → do not draw the anomaly/percentile layer.

---

## 4. Hyperstability and effort (display warnings)

When `CPUE` or `RELATIVE_ABUNDANCE` from catch is shown (partner UI):

> Catch rates move with catchability, effort, gear, rules, and behavior even when local density is unchanged. This is not abundance.

AIS/VMS/GFW **cannot** be a `BIOMASS` or `DIRECT_COUNT` layer. If vessel activity is ever shown, it is **operational coverage / effort confounder**, different legend, different group.

---

## 5. Acoustic and eDNA special cases

| Source | Allowed class | Forbidden class |
|---|---|---|
| EK80 NASC + validated TS + biological samples | `SURVEY_INDEX` or carefully qualified `BIOMASS` | Unlabeled biomass cloud; species name without validation |
| PAM detections | Detection count / presence of **sound** | Animal census |
| eDNA reads / occupancy | Occupancy / detection | Biomass, GPS of shedder |
| Satellite chl | Phytoplankton pigment | Fish or oyster abundance |

---

## 6. W1: what not to encode as abundance

| Tempting layer | Correct class |
|---|---|
| Bags on a lease | Operator’s private count — **not a globe layer** |
| Chlorophyll | BGC / food for **growth at weeks–months**, off for 72h mortality |
| SST | Physical skin T |
| DOH classification | Official **legal** context module — not a model |
| OSI-72 | `OPS_STRESS` tercile |

---

## 7. Ship-block tests

A layer fails if:

1. Legend title is “life,” “hotspot,” or “abundance” but `quantity_class` is suitability, occurrence, CPUE, or env.  
2. Two classes share one color bar.  
3. Empty cells are colored as low abundance.  
4. Public CPUE/biomass at < policy grain.  
5. Integers of wild animals in unsurveyed water.
