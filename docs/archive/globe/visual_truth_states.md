# Visual truth states — mandatory encodings

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/visual_truth_states.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Binding. If a pixel cannot be classified, it is not drawn.

Every visual object — point, line, cell, plume, trajectory, curtain, volume, sparkline, or “heatmap” — carries **exactly one** visual-truth state. A stack of satellite SST does **not** promote a cell to `DIRECT_OBSERVATION` of animals.

This file is the visual language. Claim language remains `../artifacts/scientific_red_team/prediction_contract.md`. Observatory evidence classes in `../observatory/artifacts/product_cost/sample_evidence_ui_spec.md` are a **subset**; this globe adds habitat, historical range, survey index, and restricted encodings that must never share a legend with occurrence or abundance.

---

## 1. Law: never one red scale

**Forbidden:** a single sequential red (or red–yellow–green) field titled “fish,” “life,” “hotspot,” “abundance,” or “where they are,” regardless of slider labels.

A viewer must be able to answer, **from the encoding itself** (color **and** texture **and** chrome), all of:

| Question | If missing, do not ship the layer |
|---|---|
| Observed or inferred or forecast or unknown? | Truth-state texture + chip |
| Valid time range? | Time readout |
| Depth band, or depth unknown, or depth-integrated? | Depth chip |
| Confidence? | Hatch / opacity rule + High/Medium/Low/None |
| Spatial grain? | Cell size / “coarsened” badge |
| Freshness? | `inputs_through` / last obs |
| Units / target class? | Legend title (never a naked color bar) |

**Never:** red = fish-here. Red-outline is reserved for **operational stress rank** (W1) and for **alert chrome**, not for biological presence.

---

## 2. State catalog (use these strings)

Map to observatory output class in the last column. Do not invent stronger synonyms in the UI (`detected` ≠ `observed`; `likely` ≠ `present`).

| Visual-truth state | Operator phrase | Observatory class (approx.) | Prediction-contract ceiling |
|---|---|---|---|
| `DIRECT_OBSERVATION` | Measured / seen here | `DIRECTLY_OBSERVED` | A/B only if protocol + units match |
| `REMOTE_DETECTION` | Detected by remote sensor | `REMOTELY_DETECTED` | Skin / first optical depth unless stated |
| `SURVEY_INDEX` | From a survey protocol | `SURVEY_DERIVED` | B (index), not A (census) |
| `TAGGED_INDIVIDUAL` | Tagged animal(s) | `TAG_TELEMETRY_DERIVED` | Individual ≠ population |
| `EDNA_DETECTION` | DNA at the filter | `REMOTELY_DETECTED` / survey-derived | Occupancy of molecules, not GPS of animals |
| `ACOUSTIC_DETECTION` | Sound / PAM detection | `REMOTELY_DETECTED` | Vocal / scatterer, not Linnaean census |
| `SONAR_BIOMASS_ESTIMATE` | Acoustic biomass **index** | `SURVEY_DERIVED` or `MODEL_INFERRED` | B; never unlabeled “biomass” |
| `OPERATIONAL_CATCH_OR_EFFORT` | Catch or effort log | `OPERATIONALLY_OBSERVED` | C if effort-normalized; **PRIVATE** default |
| `MODEL_INFERENCE` | Inferred by a model | `MODEL_INFERRED` | D/E typical; cannot exceed label tier |
| `FORECAST` | Forecast | `FORECAST` | Same category as the target; clock required |
| `HISTORICAL_RANGE` | Historical compiled range | `SURVEY_DERIVED` (compiled) | Not current presence (support tier ≤ T1) |
| `HABITAT_SUITABILITY` | Habitat favorability | `MODEL_INFERRED` | **D**; not presence, not abundance (≤ T2) |
| `UNKNOWN` | Not enough evidence to estimate | `UNKNOWN_INSUFFICIENT` | Confidence **None**; no score |
| `DATA_GAP` | No samples in this cell/depth/window | (coverage layer) | Not absence |
| `RESTRICTED_OR_COARSENED` | Shown coarser / delayed / withheld | (publish-class overlay) | Native geometry not drawn |

**`UNKNOWN` vs `DATA_GAP`:** a data gap is a **sampling emptiness**. UNKNOWN is a **belief emptiness** (gap, missing drivers, out-of-domain, rights block, or “we refuse to invent”). A cell can be both. Draw **DATA_GAP** on the coverage map; draw **UNKNOWN** on any estimate layer that would otherwise fill.

**`RESTRICTED_OR_COARSENED` may stack as a badge** on another state (e.g. historical range shown at 0.1°). The **geometry** follows the restricted grain; the **truth state of the content** stays the underlying class.

---

## 3. Encoding table (implement this)

Palettes are **Okabe–Ito** plus texture. Hex is the fill/stroke; texture is mandatory so colorblind users do not collapse states.

| State | Fill / stroke | Texture | Motion | Legend title pattern | Never |
|---|---|---|---|---|---|
| `DIRECT_OBSERVATION` | Stroke `#000000`, fill none or 20% black | **Solid** point/track; no glow | None (static stamp) | `{method} · observed {timestamp}` | Heatmap of points into a density sold as abundance |
| `REMOTE_DETECTION` | Stroke `#56B4E9` | Solid + **“remote / skin-or-beam”** chip | None | `{sensor} · {vertical validity}` | SST/chl titled as animals |
| `SURVEY_INDEX` | `#009E73` | **Light hatch** (survey grid) | None | `{survey name} index · {units} · {cruise/dates}` | “Biomass” without protocol |
| `TAGGED_INDIVIDUAL` | `#CC79A7` | Solid dots on a **solid** track | Optional time-scrub of **that** animal | `n tagged individuals · not a population` | Live listed-taxon pins; nest back-solve |
| `EDNA_DETECTION` | `#F0E442` stroke on black | **Dot stipple** (molecule) | None | `eDNA {detected/not detected} · station · not GPS` | Station maps of rare/listed taxa |
| `ACOUSTIC_DETECTION` | `#0072B2` | **Wave hatch** | None | `PAM/acoustic detection · {duty cycle}` | DIY localization of mammals |
| `SONAR_BIOMASS_ESTIMATE` | `#E69F00` | **Cross-hatch** + “index” | None | `Acoustic index (NASC or equivalent) · not a census` | Unlabeled biomass cloud |
| `OPERATIONAL_CATCH_OR_EFFORT` | `#8B6914` (olive-brown) | Solid in **PRIVATE** UI only | None | `CPUE or effort · {unit} · {comparison set}` | Public choropleth; AIS as catch |
| `MODEL_INFERENCE` | `#56B4E9` at 25–40% | **Dotted outline**; confidence grain | None | `{target} inferred · Category {A–E} · not an observation` | Opaque filled “truth” |
| `FORECAST` | `#E69F00` at 25–40% | **Dashed** outline + **horizon clock** | Playback **optional later**; MVP = static + clock | `{target} forecast · issued {t} · valid {window}` | Animation that looks like swimming fish |
| `HISTORICAL_RANGE` | `#0072B2` at 15%, muted | Soft fill, **date-range** label | None | `Historical compiled range · {start}–{end} · not current` | “They are here now” |
| `HABITAT_SUITABILITY` | Sequential **teal** `#009E73`→`#004D40` | Smooth **only inside observed env domain**; hatch outside | None | `Habitat suitability (not presence, not abundance)` | Same scale as occurrence or CPUE |
| `UNKNOWN` | None / paper | **Diagonal hatch** `#000000` on `#FFFFFF` | None | `Insufficient evidence to estimate` | Zero, grey-as-low-p, climatology fill |
| `DATA_GAP` | None | **Wider** diagonal hatch, slightly sparser | None | `No observations in this cell / depth / window` | “Empty ocean” |
| `RESTRICTED_OR_COARSENED` | Parent-cell fill of underlying state | **Large pixels** + lock / delay badge | None | `{publish class} · native geometry withheld` | Jittered fake precision |

**W1 ops-stress (Category D) is not in the biological presence table.** Use a **separate ordinal encoding** (see §6). Do not reuse habitat teal or occurrence purple.

### Occurrence probability (when a T3+ model exists — not MVP)

| Quantity | Palette | Texture |
|---|---|---|
| Occurrence *p* / occupancy | Sequential **purple** `#CC79A7`→`#5A2A4A` | Dotted if `MODEL_INFERENCE`; dashed if `FORECAST` |
| Units | `occurrence probability (not a count)` | No 3-decimal display until prospective calibration is accepted |

Purple is **never** used for habitat suitability or for W1 stress.

---

## 4. Confidence, staleness, extrapolation (modifiers, not new states)

These **modify** a state. They do not replace it.

| Modifier | Visual | Rule |
|---|---|---|
| Confidence **High** | Full opacity of the state’s fill (still textured) | Only if uncertainty policy allows; never if density low |
| **Medium** | 60% fill opacity | Default research look |
| **Low** | 35% + extra micro-hatch | Suppress action options if costly |
| **None** | No estimate fill; UNKNOWN hatch | Successful issuance of “cannot issue” |
| **Stale** | Clock-with-slash chip | Freshness SLA breached |
| **Extrapolated** | Magenta tick marks on cell edge (`#CC79A7` ticks, not fill) | Out of training envelope / new basin / new era |
| **Disputed** | Two-state split fill + “sources disagree” | Do not average secretly |
| **Data-sparse** | Same as Low + observation-count in panel | Coverage map, not a guess |

Labels allowed in chrome: **High / Medium / Low / None** only for issued scores (`prediction_contract.md` §2). Do not print calibrated-looking percentages until a human reviewer accepts a prospective calibration plot.

---

## 5. Quantity classes — different legends, always

These are **not** truth states; they are **what the number means**. Mixing them on one color bar is a ship-block.

| Quantity | Encoding family | Example legend |
|---|---|---|
| Habitat suitability | Teal sequential | Suitability index · reference {env domain} |
| Historical occurrence of **records** | Muted blue, effort-biased caption | Compiled records (sampling, not absence) |
| Occurrence / occupancy *p* | Purple sequential | P(present) · not abundance |
| Relative abundance rank | Olive sequential **or** tercile chips | Lower / middle / upper tercile of {comparison set} |
| Survey index | Green hatch | {survey} · {units} · {stratum} |
| Biomass (validated) | Orange cross-hatch | t/km² or kg · protocol {id} |
| Direct count | Black integers on a **defined** plot | N in {area} at {time} · method |
| CPUE | Olive-brown | Catch per {effort unit} · not stock |
| Forecast of any of the above | Dashed + clock on **that** quantity’s palette | Same units + issued/valid |
| Unknown | Black/white hatch | No quantity |

Full rules: `abundance_encoding.md`.

---

## 6. W1 Willapa — operational stress (not a life layer)

| Chip | Visual | Means | Does not mean |
|---|---|---|---|
| **Typical** | Gray fill `#999999`, solid | Mid tercile of **this lease’s** comparable tide/season work-stress | Safe, legal, healthy stock |
| **Elevated** | Amber `#E69F00`, solid | Upper tercile ops-stress indicator | Harvest OK / not OK |
| **High** | **Red outline** `#D55E00` on white, not a red flood | Extreme of comparison set | Mortality %; food-safety |
| **Cannot issue** | Black/white hatch | UNKNOWN / confidence None | Broken app |

**Always-visible strip:** `NOT FOOD-SAFETY · NOT HARVEST AUTHORIZATION · verify WA DOH`.

**Primary drivers encoding (inputs, not “caused by SST”):**

- Air × daytime emersion: **solid** time-series (forecast dashed).
- Wind/wave workability: **separate** series.
- Station water T/DO/S: **supporting**, labeled lag + km offset; **not** oyster body temperature.

DOH growing-area polygons: **context outline only**, caption *harvest geography, not biology*. Never model-color open/closed.

---

## 7. Anti-patterns (design-review fail)

| Anti-pattern | Why it fails |
|---|---|
| One RdYlGn choropleth named “life” | Collapses habitat, effort, and animals |
| Kriging across UNKNOWN | Manufactured confidence |
| Green cell next to a DOH “Approved” layer | Food-safety contamination |
| Glow / bloom / school-of-fish sprites | Count theater |
| Default missing cells to climatology without banner | Hides UNKNOWN |
| Same teal for suitability and occurrence | Category error |
| AIS density in biological palette | Effort ≠ abundance |
| 0.73 printed on a cell | Forbidden precision |
| Animation of a forecast plume that looks like swimming | Deceptive motion |

---

## 8. Accessibility cross-check

Every state in §3 has a **non-color** channel (solid / dotted / dashed / diagonal hatch / stipple / wave / lock). See `accessibility_and_trust.md`. If two states differ only by hue, the layer fails review.

---

## 9. API sketch (visual client)

Sibling `api_for_globe.md` owns transport. The visual client **rejects** a feature that lacks:

```json
{
  "truth_state": "FORECAST",
  "quantity_class": "operational_stress_indicator",
  "prediction_category": "D",
  "confidence_category": "low",
  "depth_band": "INTERTIDAL_AIR",
  "depth_status": "known | unknown | integrated",
  "time": { "issued_at": "", "valid_from": "", "valid_to": "", "inputs_through": "", "last_direct_obs": null },
  "spatial_grain_m": 10000,
  "publish_class": "COARSENED",
  "units": "tercile_rank",
  "legend_id": "osi72-ordinal-v0"
}
```

Reject `quantity_class=abundance` without Category A or B **and** a survey protocol id. Reject any payload with `fish_count` on an unsurveyed cell.
